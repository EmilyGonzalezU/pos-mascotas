from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from .models import Order, OrderItem, Payment
from inventory.models import Product
from decimal import Decimal
from core.utils import format_clp

# --- Helpers ---
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
            product = Product.objects.get(id=product_id)
            quantity = Decimal(quantity_str)
            
            # Logic for line total (handle bulk vs unit)
            # If bulk, price might be per KG, quantity is KG.
            line_total = int(round(product.price_clp * float(quantity)))
            
            items.append({
                'product': product,
                'quantity': quantity,
                'line_total': line_total,
                'line_total_formatted': format_clp(line_total)
            })
            total_gross += line_total
        except Product.DoesNotExist:
            continue
            
    # IVA extraction (19%) - included in gross
    total_net = int(total_gross / 1.19)
    total_iva = total_gross - total_net
    
    return {
        'items': items,
        'total_gross': total_gross,
        'total_net': total_net,
        'total_iva': total_iva,
        'total_formatted': format_clp(total_gross),
        'iva_formatted': format_clp(total_iva)
    }

# --- Views ---

@login_required
def pos_dashboard(request):
    """Renderiza la vista principal de la caja."""
    cart_data = calculate_cart_totals(get_cart(request))
    return render(request, 'pos/dashboard.html', {'cart': cart_data})

@require_GET
def search_products(request):
    """Endpoint HTMX para búsqueda de productos."""
    query = request.GET.get('q', '')
    products = []
    if len(query) > 2:
        products = Product.objects.filter(
            name__icontains=query, stock__gt=0
        ) | Product.objects.filter(
            sku__icontains=query, stock__gt=0
        ) | Product.objects.filter(
            barcode__icontains=query, stock__gt=0
        ).distinct()[:10]
        
    return render(request, 'pos/partials/product_list.html', {'products': products})

@require_POST
def add_to_cart(request, product_id):
    """Endpoint HTMX para agregar al carrito."""
    cart = get_cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    # Cantidad: Por defecto 1 (unidad) o 0.1 (100g para granel si no se especifica)
    # En un POS real, para granel se ingresaría el peso. Aquí asumiremos +1 unidad o +0.5kg por click para simpleza UI
    quantity_to_add = Decimal('1.0')
    if product.is_bulk:
        quantity_to_add = Decimal('0.500') # 500 gramos por defecto al clickear granel

    current_qty = Decimal(cart.get(str(product_id), '0'))
    new_qty = current_qty + quantity_to_add
    
    # Validar stock
    if new_qty <= product.stock:
        cart[str(product_id)] = str(new_qty)
        save_cart(request, cart)
    else:
        # Podríamos retornar un error HTMX aquí
        pass 
        
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
@transaction.atomic
def checkout(request):
    cart = get_cart(request)
    if not cart:
        return redirect('pos_dashboard')
        
    # Calcular totales
    total_clp = 0
    items_data = []
    
    # Validar stock antes de crear la orden
    for product_id, quantity_str in cart.items():
        product = Product.objects.get(id=product_id)
        qty = Decimal(quantity_str)
        if product.stock < qty:
            messages.error(request, f"Stock insuficiente para {product.name}")
            return redirect('pos_dashboard')

    # Crear Orden
    with transaction.atomic():
        order = Order.objects.create(customer=None) # Cliente anónimo por ahora
        
        for product_id, quantity_str in cart.items():
            product = Product.objects.get(id=product_id)
            qty = Decimal(quantity_str)
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                unit_price_clp=product.price_clp,
                # line_total se calcula auto en save()
            )
            
            # Descontar Stock
            product.stock -= qty
            product.save()
            
        order.calculate_total()
        
        # Procesar Pago
        method = request.POST.get('payment_method', 'CASH')
        trx_id = request.POST.get('transaction_id', '')
        last_4 = request.POST.get('card_last_4', '')
        
        Payment.objects.create(
            order=order,
            amount_clp=order.total_clp,
            method=method,
            transaction_id=trx_id if method in ['CARD', 'TRANSFER'] else None,
            card_last_4=last_4 if method == 'CARD' else None
        )
        
        order.is_paid = True
        order.save()
    
    # Limpiar carrito
    request.session['cart'] = {}
    
    messages.success(request, f"Venta #{order.id} registrada correctamente")
    return redirect('pos_dashboard')
