from django.contrib import admin
from .models import Brand, Supplier, Category, Product, Batch


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'tenant')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'rut', 'contact_name', 'phone', 'tenant')
    search_fields = ('name', 'rut', 'contact_name')


class BatchInline(admin.TabularInline):
    model = Batch
    extra = 0
    readonly_fields = ('is_expired', 'days_to_expiration')

    def is_expired(self, obj):
        return obj.is_expired if obj.pk else '-'
    is_expired.boolean = True
    is_expired.short_description = '¿Expirado?'

    def days_to_expiration(self, obj):
        return obj.days_to_expiration if obj.pk else '-'
    days_to_expiration.short_description = 'Días p/vencer'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'sku', 'name', 'brand', 'species', 'protein',
        'price_clp', 'cost_clp', 'display_margin',
        'stock', 'is_low_stock', 'tenant',
    )
    list_filter = ('species', 'lifecycle', 'protein', 'brand', 'is_bulk')
    search_fields = ('sku', 'name', 'barcode')
    inlines = [BatchInline]

    fieldsets = (
        ('Identificación', {
            'fields': ('sku', 'barcode', 'name', 'brand', 'brand_name', 'category', 'supplier', 'image')
        }),
        ('Clasificación Pet', {
            'fields': ('species', 'lifecycle', 'protein', 'weight_kg')
        }),
        ('Precios y Costos', {
            'fields': ('price_clp', 'cost_clp', 'min_margin_pct', 'is_bulk', 'bulk_price_per_kg')
        }),
        ('Stock', {
            'fields': ('stock', 'min_stock_alert')
        }),
    )

    @admin.display(description='Margen %', ordering='cost_clp')
    def display_margin(self, obj):
        margin = obj.margin_pct
        if obj.is_margin_below_minimum:
            return f"⚠️ {margin}%"
        return f"{margin}%"

    @admin.display(description='Stock Bajo', boolean=True)
    def is_low_stock(self, obj):
        return obj.is_low_stock


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = (
        'product', 'batch_number', 'expiration_date',
        'current_quantity', 'is_expired_display', 'days_display',
    )
    list_filter = ('expiration_date',)
    search_fields = ('product__name', 'batch_number')

    @admin.display(description='¿Expirado?', boolean=True)
    def is_expired_display(self, obj):
        return obj.is_expired

    @admin.display(description='Días p/vencer')
    def days_display(self, obj):
        days = obj.days_to_expiration
        if days < 0:
            return f"❌ Expirado hace {abs(days)} días"
        if days <= 30:
            return f"⚠️ {days} días"
        return f"✅ {days} días"