from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from decimal import Decimal

from .models import Order, OrderItem, Payment, CashRegister, Shift
from .services import (
    CheckoutService, ShiftService,
    InsufficientStockError, ShiftClosedError,
    ShiftAlreadyOpenError, NoOpenShiftError,
)
from apps.inventory.models import Product
from apps.core.utils import format_clp


# ──────────────────────── Cart helpers ────────────────────────

def get_cart(request):
    if 'cart' not in request.session:
        request.session['cart'] = {}
    return request.session['cart']


def save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


def calculate_cart_totals(cart):
    items = []
    total_gross = 0

    for product_id, quantity_str in cart.items():
        try:
            product = Product.all_objects.get(id=product_id)
            quantity = Decimal(quantity_str)
            line_total = int(round(product.price_clp * float(quantity)))

            items.append({
                'product': product,
                'quantity': quantity,
                'line_total': line_total,
                'line_total_formatted': format_clp(line_total),
            })
            total_gross += line_total
        except Product.DoesNotExist:
            continue

    total_net = int(total_gross / 1.19) if total_gross else 0
    total_iva = total_gross - total_net

    return {
        'items': items,
        'total_gross': total_gross,
        'total_net': total_net,
        'total_iva': total_iva,
        'total_formatted': format_clp(total_gross),
        'iva_formatted': format_clp(total_iva),
    }


# ──────────────────────── Shift helpers ────────────────────────

def _get_active_shift(request):
    """Get the active shift for the current user, or None."""
    shift_id = request.session.get('active_shift_id')
    if shift_id:
        try:
            return Shift.all_objects.get(id=shift_id, closed_at__isnull=True)
        except Shift.DoesNotExist:
            # Shift was closed externally
            del request.session['active_shift_id']
    return None


# ──────────────────────── POS Views ────────────────────────

@login_required
def pos_dashboard(request):
    """Vista principal de caja."""
    shift = _get_active_shift(request)
    cart_data = calculate_cart_totals(get_cart(request))

    return render(request, 'pos/dashboard.html', {
        'cart': cart_data,
        'active_shift': shift,
    })


@login_required
@require_GET
def search_products(request):
    """Endpoint HTMX para búsqueda de productos."""
    query = request.GET.get('q', '').strip()
    products = []
    if len(query) >= 1:
        products = Product.objects.filter(
            name__icontains=query, stock__gt=0
        ) | Product.objects.filter(
            sku__icontains=query, stock__gt=0
        ) | Product.objects.filter(
            barcode__icontains=query, stock__gt=0
        )
        products = products.distinct()[:12]

    return render(request, 'pos/partials/product_list.html', {'products': products})


@require_POST
def add_to_cart(request, product_id):
    """Endpoint HTMX para agregar al carrito."""
    cart = get_cart(request)
    product = get_object_or_404(Product, id=product_id)

    quantity_to_add = Decimal('1.0')
    if product.is_bulk:
        quantity_to_add = Decimal('0.500')

    current_qty = Decimal(cart.get(str(product_id), '0'))
    new_qty = current_qty + quantity_to_add

    if new_qty <= product.stock:
        cart[str(product_id)] = str(new_qty)
        save_cart(request, cart)

    cart_data = calculate_cart_totals(cart)
    return render(request, 'pos/partials/cart_items.html', {'cart': cart_data})


@require_POST
def remove_from_cart(request, product_id):
    cart = get_cart(request)
    if str(product_id) in cart:
        del cart[str(product_id)]
        save_cart(request, cart)

    cart_data = calculate_cart_totals(cart)
    return render(request, 'pos/partials/cart_items.html', {'cart': cart_data})


@require_POST
@login_required
def checkout(request):
    """Procesar venta — funciona con o sin turno abierto."""
    from django.db import transaction

    cart = get_cart(request)
    if not cart:
        messages.warning(request, "El carrito está vacío.")
        return redirect('pos_dashboard')

    tenant = getattr(request, 'tenant', None)
    if not tenant:
        messages.error(request, "No se pudo identificar la tienda.")
        return redirect('pos_dashboard')

    shift = _get_active_shift(request)

    # Try to auto-create shift if we have registers
    if not shift:
        registers = CashRegister.objects.filter(tenant=tenant, is_active=True)
        if registers.exists():
            try:
                shift_service = ShiftService(tenant)
                shift = shift_service.open_shift(registers.first(), request.user, 0)
                request.session['active_shift_id'] = shift.id
            except ShiftAlreadyOpenError:
                pass

    method = request.POST.get('payment_method', 'CASH')
    payment_details = {}
    if method in ('CARD', 'TRANSFER', 'MIXED'):
        payment_details['transaction_id'] = request.POST.get('transaction_id', '')
    if method == 'CARD':
        payment_details['card_last_4'] = request.POST.get('card_last_4', '')

    try:
        if shift:
            # Use CheckoutService with shift
            service = CheckoutService(tenant=tenant, shift=shift, cashier=request.user)
            order = service.process_sale(
                cart_items=cart,
                customer=None,
                payment_method=method,
                payment_details=payment_details,
            )
        else:
            # Direct order creation without shift
            with transaction.atomic():
                order = Order(tenant=tenant, cashier=request.user)
                order.save()

                total = 0
                for product_id, quantity_str in cart.items():
                    product = Product.all_objects.get(id=product_id)
                    qty = Decimal(quantity_str)

                    if product.stock < qty:
                        raise InsufficientStockError(
                            f"Stock insuficiente para {product.name}: "
                            f"disponible {product.stock}, requerido {qty}"
                        )

                    line_total = int(round(product.price_clp * float(qty)))
                    OrderItem.objects.create(
                        order=order, product=product, quantity=qty,
                        unit_price_clp=product.price_clp,
                        cost_at_sale=product.cost_clp,
                        line_total_clp=line_total,
                    )
                    product.stock -= qty
                    product.save()
                    total += line_total

                order.total_clp = total
                order.net_amount = int(total / 1.19)
                order.iva_amount = total - order.net_amount
                order.is_paid = True
                order.save()

                details = payment_details or {}
                Payment(
                    tenant=tenant, order=order, amount_clp=total,
                    method=method,
                    transaction_id=details.get('transaction_id'),
                    card_last_4=details.get('card_last_4'),
                ).save()

        request.session['cart'] = {}
        messages.success(request, f"✅ Venta #{order.id} registrada — ${order.total_clp:,.0f}")
    except InsufficientStockError as e:
        messages.error(request, str(e))
    except ShiftClosedError as e:
        messages.error(request, str(e))

    return redirect('pos_dashboard')


# ──────────────────────── Shift Views ────────────────────────

@login_required
def shift_select(request):
    """Selección de caja para abrir turno."""
    tenant = getattr(request, 'tenant', None)
    if not tenant:
        messages.error(request, "No se pudo identificar la tienda.")
        return redirect('pos_dashboard')

    shift_service = ShiftService(tenant)
    registers = shift_service.get_active_registers()

    # Build register status
    register_data = []
    for reg in registers:
        open_shift = shift_service.get_open_shift(reg)
        register_data.append({
            'register': reg,
            'open_shift': open_shift,
            'can_open': open_shift is None,
        })

    return render(request, 'pos/shift_select.html', {
        'registers': register_data,
        'active_shift': _get_active_shift(request),
    })


@require_POST
@login_required
def shift_open(request, register_id):
    """Abrir turno en una caja."""
    tenant = getattr(request, 'tenant', None)
    register = get_object_or_404(CashRegister, id=register_id)

    opening_cash = int(request.POST.get('opening_cash', 0))

    shift_service = ShiftService(tenant)
    try:
        shift = shift_service.open_shift(register, request.user, opening_cash)
        request.session['active_shift_id'] = shift.id
        messages.success(
            request,
            f"✅ Turno abierto en {register.name} — "
            f"Efectivo inicial: ${opening_cash:,.0f}"
        )
    except ShiftAlreadyOpenError as e:
        messages.error(request, str(e))

    return redirect('pos_dashboard')


@login_required
def shift_close(request):
    """Cerrar turno actual."""
    shift = _get_active_shift(request)
    if not shift:
        messages.warning(request, "No tienes un turno abierto.")
        return redirect('pos_dashboard')

    tenant = getattr(request, 'tenant', None)
    shift_service = ShiftService(tenant)

    if request.method == 'POST':
        closing_cash = int(request.POST.get('closing_cash', 0))
        notes = request.POST.get('notes', '')

        summary = shift_service.close_shift(shift, closing_cash, notes)

        # Clear session
        if 'active_shift_id' in request.session:
            del request.session['active_shift_id']
        # Clear cart
        request.session['cart'] = {}

        return render(request, 'pos/shift_summary.html', {
            'summary': summary,
        })

    # GET — show close form with live summary
    orders = Order.all_objects.filter(shift=shift, is_paid=True, is_voided=False)
    total_sales = sum(o.total_clp for o in orders)
    total_orders = orders.count()

    return render(request, 'pos/shift_close.html', {
        'shift': shift,
        'total_sales': total_sales,
        'total_orders': total_orders,
    })


# ──────────────────────── Void View ────────────────────────

@require_POST
@login_required
def void_sale(request, order_id):
    """Anular una venta (requiere SUPERVISOR+)."""
    tenant = getattr(request, 'tenant', None)
    order = get_object_or_404(Order, id=order_id)

    # Check permission
    profile = getattr(request.user, 'staff_profile', None)
    if not profile or not profile.can_void_sales:
        messages.error(request, "No tienes permiso para anular ventas.")
        return redirect('pos_dashboard')

    shift = _get_active_shift(request)
    if not shift:
        messages.error(request, "No tienes un turno abierto.")
        return redirect('pos_dashboard')

    reason = request.POST.get('reason', '')
    service = CheckoutService(tenant, shift, request.user)

    try:
        service.void_sale(order, voided_by=request.user, reason=reason)
        messages.success(request, f"Venta #{order.id} anulada correctamente.")
    except Exception as e:
        messages.error(request, str(e))

    return redirect('pos_dashboard')
