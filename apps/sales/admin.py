from django.contrib import admin
from .models import CashRegister, Shift, Order, OrderItem, Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('line_total_clp',)


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


@admin.register(CashRegister)
class CashRegisterAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch', 'is_active', 'tenant')
    list_filter = ('is_active', 'branch')


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = (
        'register', 'cashier', 'opened_at', 'closed_at',
        'opening_cash', 'closing_cash', 'is_open_display',
    )
    list_filter = ('register', 'cashier')
    readonly_fields = ('opened_at',)

    @admin.display(description='Abierto', boolean=True)
    def is_open_display(self, obj):
        return obj.is_open


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'date', 'total_display', 'net_display', 'iva_display',
        'is_paid', 'is_voided', 'cashier', 'branch',
    )
    list_filter = ('is_paid', 'is_voided', 'branch', 'date')
    search_fields = ('id', 'order_number', 'customer__first_name')
    inlines = [OrderItemInline, PaymentInline]
    readonly_fields = ('date', 'net_amount', 'iva_amount')

    @admin.display(description='Total CLP')
    def total_display(self, obj):
        return f"${obj.total_clp:,.0f}"

    @admin.display(description='Neto')
    def net_display(self, obj):
        return f"${obj.net_amount:,.0f}"

    @admin.display(description='IVA')
    def iva_display(self, obj):
        return f"${obj.iva_amount:,.0f}"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount_clp', 'method', 'transaction_id')
    list_filter = ('method',)
