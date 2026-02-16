from django.contrib import admin
from .models import Category, Product, Batch

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'modified_at')
    search_fields = ('name',)

class BatchInline(admin.TabularInline):
    model = Batch
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'brand', 'category', 'price_clp', 'stock', 'species', 'is_bulk', 'active_status')
    list_filter = ('category', 'brand', 'species', 'lifecycle', 'is_bulk')
    search_fields = ('sku', 'name', 'brand', 'barcode')
    list_editable = ('stock', 'price_clp')
    ordering = ('name',)
    inlines = [BatchInline]
    
    @admin.display(description='Precio', ordering='price_clp')
    def price_clp_fmt(self, obj):
        return f"${obj.price_clp:,}".replace(',', '.')

    @admin.display(description='Estado', boolean=True)
    def active_status(self, obj):
        return obj.stock > 0

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('batch_number', 'product', 'expiration_date', 'current_quantity')
    list_filter = ('expiration_date',)
    search_fields = ('batch_number', 'product__name', 'product__sku')
    date_hierarchy = 'expiration_date'