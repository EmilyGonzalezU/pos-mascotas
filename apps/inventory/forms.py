from django import forms
from .models import Product, Category, Batch, Brand, Supplier

WIDGET_BASE = 'w-full p-2 border rounded'


class ProductForm(forms.ModelForm):
    brand_text = forms.CharField(
        max_length=100, required=False,
        label="Marca",
        widget=forms.TextInput(attrs={'class': WIDGET_BASE, 'placeholder': 'Ej. Royal Canin, Purina'}),
    )
    supplier_text = forms.CharField(
        max_length=200, required=False,
        label="Proveedor",
        widget=forms.TextInput(attrs={'class': WIDGET_BASE, 'placeholder': 'Ej. Distribuidora XYZ'}),
    )

    class Meta:
        model = Product
        fields = [
            'sku', 'barcode', 'name', 'category',
            'species', 'lifecycle', 'protein', 'weight_kg',
            'price_clp', 'cost_clp', 'min_margin_pct',
            'is_bulk', 'bulk_price_per_kg', 'stock', 'min_stock_alert',
        ]
        widgets = {
            'sku': forms.TextInput(attrs={'class': WIDGET_BASE}),
            'barcode': forms.TextInput(attrs={'class': WIDGET_BASE}),
            'name': forms.TextInput(attrs={'class': WIDGET_BASE}),
            'category': forms.Select(attrs={'class': WIDGET_BASE}),
            'species': forms.Select(attrs={'class': WIDGET_BASE}),
            'lifecycle': forms.Select(attrs={'class': WIDGET_BASE}),
            'protein': forms.Select(attrs={'class': WIDGET_BASE}),
            'weight_kg': forms.NumberInput(attrs={'class': WIDGET_BASE, 'step': '0.01'}),
            'price_clp': forms.NumberInput(attrs={'class': WIDGET_BASE}),
            'cost_clp': forms.NumberInput(attrs={'class': WIDGET_BASE}),
            'min_margin_pct': forms.NumberInput(attrs={'class': WIDGET_BASE, 'step': '0.01'}),
            'is_bulk': forms.CheckboxInput(attrs={'class': 'w-5 h-5'}),
            'bulk_price_per_kg': forms.NumberInput(attrs={'class': WIDGET_BASE}),
            'stock': forms.NumberInput(attrs={'class': WIDGET_BASE, 'step': '0.001'}),
            'min_stock_alert': forms.NumberInput(attrs={'class': WIDGET_BASE, 'step': '0.001'}),
        }

    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        # Pre-fill brand/supplier text from existing instance
        if self.instance and self.instance.pk:
            if self.instance.brand:
                self.fields['brand_text'].initial = self.instance.brand.name
            elif self.instance.brand_name:
                self.fields['brand_text'].initial = self.instance.brand_name
            if self.instance.supplier:
                self.fields['supplier_text'].initial = self.instance.supplier.name
        # Reorder fields so brand/supplier text appear after name
        field_order = [
            'sku', 'barcode', 'name', 'brand_text', 'supplier_text', 'category',
            'species', 'lifecycle', 'protein', 'weight_kg',
            'price_clp', 'cost_clp', 'min_margin_pct',
            'is_bulk', 'bulk_price_per_kg', 'stock', 'min_stock_alert',
        ]
        self.order_fields(field_order)

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Set tenant
        if self.tenant:
            instance.tenant = self.tenant

        # Handle brand text → Brand FK
        brand_text = self.cleaned_data.get('brand_text', '').strip()
        if brand_text and self.tenant:
            brand_obj, _ = Brand.objects.get_or_create(
                tenant=self.tenant, name__iexact=brand_text,
                defaults={'name': brand_text, 'tenant': self.tenant},
            )
            instance.brand = brand_obj
            instance.brand_name = brand_text
        elif brand_text:
            instance.brand_name = brand_text

        # Handle supplier text → Supplier FK
        supplier_text = self.cleaned_data.get('supplier_text', '').strip()
        if supplier_text and self.tenant:
            supplier_obj, _ = Supplier.objects.get_or_create(
                tenant=self.tenant, name__iexact=supplier_text,
                defaults={'name': supplier_text, 'tenant': self.tenant},
            )
            instance.supplier = supplier_obj

        if commit:
            instance.save()
        return instance


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': WIDGET_BASE, 'placeholder': 'Ej. Alimentos, Juguetes'}),
        }


class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ['product', 'batch_number', 'expiration_date', 'quantity', 'current_quantity']
        widgets = {
            'product': forms.Select(attrs={'class': WIDGET_BASE}),
            'batch_number': forms.TextInput(attrs={'class': WIDGET_BASE}),
            'expiration_date': forms.DateInput(attrs={'class': WIDGET_BASE, 'type': 'date'}),
            'quantity': forms.NumberInput(attrs={'class': WIDGET_BASE, 'step': '0.001'}),
            'current_quantity': forms.NumberInput(attrs={'class': WIDGET_BASE, 'step': '0.001'}),
        }


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': WIDGET_BASE, 'placeholder': 'Ej. Royal Canin, Purina'}),
        }


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'rut', 'contact_name', 'phone', 'email', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': WIDGET_BASE}),
            'rut': forms.TextInput(attrs={'class': WIDGET_BASE, 'placeholder': '12.345.678-9'}),
            'contact_name': forms.TextInput(attrs={'class': WIDGET_BASE}),
            'phone': forms.TextInput(attrs={'class': WIDGET_BASE}),
            'email': forms.EmailInput(attrs={'class': WIDGET_BASE}),
            'address': forms.TextInput(attrs={'class': WIDGET_BASE}),
        }
