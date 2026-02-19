"""
Service layer for sales operations.
Encapsulates business logic away from views for testability and reuse.
"""
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from .models import Order, OrderItem, Payment, Shift, CashRegister
from apps.inventory.models import Product


# --- Custom exceptions ---

class SalesError(Exception):
    """Base exception for sales operations."""
    pass


class InsufficientStockError(SalesError):
    pass


class ShiftClosedError(SalesError):
    pass


class ShiftAlreadyOpenError(SalesError):
    pass


class NoOpenShiftError(SalesError):
    pass


# --- CheckoutService ---

class CheckoutService:
    """Encapsula toda la lógica de cobro y cierre de venta."""

    def __init__(self, tenant, shift, cashier):
        self.tenant = tenant
        self.shift = shift
        self.cashier = cashier

    @transaction.atomic
    def process_sale(self, cart_items, customer=None, payment_method='CASH',
                     payment_details=None):
        """
        Crea la orden, descuenta stock, registra pago.

        Args:
            cart_items: dict {product_id: quantity_str}
            customer: Customer instance or None
            payment_method: 'CASH', 'CARD', 'TRANSFER', 'MIXED'
            payment_details: dict with optional transaction_id, card_last_4

        Returns: Order

        Raises:
            ShiftClosedError: si el turno está cerrado
            InsufficientStockError: si no hay stock suficiente
        """
        if not self.shift.is_open:
            raise ShiftClosedError("El turno está cerrado. Abre un nuevo turno.")

        # Create order
        order = Order(
            tenant=self.tenant,
            customer=customer,
            shift=self.shift,
            branch=self.shift.register.branch,
            cashier=self.cashier,
        )
        order.save()

        total = 0
        for product_id, quantity_str in cart_items.items():
            product = Product.all_objects.get(id=product_id)
            qty = Decimal(quantity_str)

            if product.stock < qty:
                raise InsufficientStockError(
                    f"Stock insuficiente para {product.name}: "
                    f"disponible {product.stock}, requerido {qty}"
                )

            line_total = int(round(product.price_clp * float(qty)))
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                unit_price_clp=product.price_clp,
                cost_at_sale=product.cost_clp,
                line_total_clp=line_total,
            )

            product.stock -= qty
            product.save()
            total += line_total

        # Fiscal breakdown
        order.total_clp = total
        order.net_amount = int(total / 1.19)
        order.iva_amount = total - order.net_amount
        order.is_paid = True
        order.save()

        # Payment
        details = payment_details or {}
        Payment(
            tenant=self.tenant,
            order=order,
            amount_clp=total,
            method=payment_method,
            transaction_id=details.get('transaction_id'),
            card_last_4=details.get('card_last_4'),
        ).save()

        return order

    @transaction.atomic
    def void_sale(self, order, voided_by, reason=''):
        """
        Anula una venta y devuelve stock.

        Args:
            order: Order to void
            voided_by: User who authorizes void
            reason: Reason for void
        """
        if order.is_voided:
            raise SalesError("Esta venta ya fue anulada.")

        # Restore stock
        for item in order.items.select_related('product'):
            item.product.stock += item.quantity
            item.product.save()

        order.is_voided = True
        order.voided_by = voided_by
        order.void_reason = reason
        order.save()

        return order


# --- ShiftService ---

class ShiftService:
    """Gestión de turnos/apertura/cierre de caja."""

    def __init__(self, tenant):
        self.tenant = tenant

    def get_open_shift(self, register):
        """Get the currently open shift for a register, or None."""
        return Shift.all_objects.filter(
            tenant=self.tenant,
            register=register,
            closed_at__isnull=True,
        ).first()

    def get_open_shifts_for_user(self, user):
        """Get all open shifts for a specific cashier."""
        return Shift.all_objects.filter(
            tenant=self.tenant,
            cashier=user,
            closed_at__isnull=True,
        )

    @transaction.atomic
    def open_shift(self, register, cashier, opening_cash=0):
        """
        Abrir un nuevo turno en una caja.

        Raises:
            ShiftAlreadyOpenError: si ya hay un turno abierto en esta caja
        """
        existing = self.get_open_shift(register)
        if existing:
            raise ShiftAlreadyOpenError(
                f"Ya hay un turno abierto en {register.name} "
                f"por {existing.cashier.get_full_name() or existing.cashier.username}"
            )

        shift = Shift(
            tenant=self.tenant,
            register=register,
            cashier=cashier,
            opening_cash=opening_cash,
        )
        shift.save()
        return shift

    @transaction.atomic
    def close_shift(self, shift, closing_cash=None, notes=''):
        """
        Cerrar un turno. Calcula diferencias de caja.

        Returns: dict with shift summary
        """
        if not shift.is_open:
            raise ShiftClosedError("Este turno ya fue cerrado.")

        shift.closed_at = timezone.now()
        shift.closing_cash = closing_cash
        shift.notes = notes
        shift.save()

        # Calculate shift summary
        orders = Order.all_objects.filter(shift=shift, is_paid=True, is_voided=False)
        total_sales = sum(o.total_clp for o in orders)
        total_orders = orders.count()

        # Cash payments only
        cash_payments = Payment.all_objects.filter(
            order__shift=shift,
            order__is_paid=True,
            order__is_voided=False,
            method='CASH',
        )
        total_cash = sum(p.amount_clp for p in cash_payments)

        expected_cash = shift.opening_cash + total_cash
        difference = (closing_cash or 0) - expected_cash

        return {
            'shift': shift,
            'total_sales': total_sales,
            'total_orders': total_orders,
            'total_cash_received': total_cash,
            'expected_cash': expected_cash,
            'closing_cash': closing_cash or 0,
            'difference': difference,
        }

    def get_active_registers(self, branch=None):
        """Get all active cash registers, optionally filtered by branch."""
        qs = CashRegister.all_objects.filter(tenant=self.tenant, is_active=True)
        if branch:
            qs = qs.filter(branch=branch)
        return qs
