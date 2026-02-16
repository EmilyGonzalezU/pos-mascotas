from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['sku', 'barcode', 'name', 'brand', 'category', 'species', 'lifecycle', 'price_clp', 'is_bulk', 'stock']
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'barcode': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'brand': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'category': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
            'species': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
            'lifecycle': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
            'price_clp': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
            'stock': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
            'is_bulk': forms.CheckboxInput(attrs={'class': 'w-5 h-5'}),
        }

from .models import Category, Batch

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Ej. Alimentos, Juguetes'}),
        }

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ['product', 'batch_number', 'expiration_date', 'current_quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
            'batch_number': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'expiration_date': forms.DateInput(attrs={'class': 'w-full p-2 border rounded', 'type': 'date'}),
            'current_quantity': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
        }
