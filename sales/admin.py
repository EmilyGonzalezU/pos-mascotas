from django.contrib import admin
from django.db.models import Sum
from .models import Order, OrderItem, Payment

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ('product',)
    extra = 0
    readonly_fields = ('line_total_clp',)

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'customer', 'total_fmt', 'is_paid', 'items_count')
    list_filter = ('date', 'is_paid')
    search_fields = ('id', 'customer__rut', 'customer__first_name')
    date_hierarchy = 'date'
    inlines = [OrderItemInline, PaymentInline]
    readonly_fields = ('date', 'total_clp')

    @admin.display(description='Total', ordering='total_clp')
    def total_fmt(self, obj):
        return f"${obj.total_clp:,}".replace(',', '.')

    @admin.display(description='Items')
    def items_count(self, obj):
        return obj.items.count()

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'line_total_fmt')
    search_fields = ('order__id', 'product__name')
    list_filter = ('product__category',)

    @admin.display(description='Total Línea')
    def line_total_fmt(self, obj):
        return f"${obj.line_total_clp:,}".replace(',', '.')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'method', 'amount_fmt', 'created_at')
    list_filter = ('method', 'created_at')
    
    @admin.display(description='Monto')
    def amount_fmt(self, obj):
        return f"${obj.amount_clp:,}".replace(',', '.')
