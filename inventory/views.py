from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product
from .forms import ProductForm

@login_required
def inventory_dashboard(request):
    return render(request, 'inventory/dashboard.html')

@login_required
def product_list(request):
    products = Product.objects.all().order_by('name')
    return render(request, 'inventory/product_list.html', {'products': products})

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/product_form.html', {'form': form, 'title': 'Nuevo Producto'})

@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('inventory_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/product_form.html', {'form': form, 'title': 'Editar Producto'})

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('inventory_list')
    return render(request, 'inventory/product_confirm_delete.html', {'product': product})

# --- Category CRUD ---
from .forms import CategoryForm, BatchForm
from .models import Category, Batch

@login_required
def category_list(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'inventory/category_list.html', {'categories': categories})

@login_required
def category_create(request):
    title = 'Nueva Categoría'
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'inventory/generic_form.html', {'form': form, 'title': title})

@login_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'inventory/generic_form.html', {'form': form, 'title': 'Editar Categoría'})

@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    # Using generic delete template or creating one? Let's genericize.
    return render(request, 'inventory/product_confirm_delete.html', {'product': category}) # Reusing for now

# --- Batch CRUD ---
@login_required
def batch_list(request):
    from datetime import date
    batches = Batch.objects.select_related('product').order_by('expiration_date')
    return render(request, 'inventory/batch_list.html', {'batches': batches, 'today': date.today()})

@login_required
def batch_create(request):
    title = 'Nuevo Lote'
    if request.method == 'POST':
        form = BatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('batch_list')
    else:
        form = BatchForm()
    return render(request, 'inventory/generic_form.html', {'form': form, 'title': title})

@login_required
def batch_update(request, pk):
    batch = get_object_or_404(Batch, pk=pk)
    if request.method == 'POST':
        form = BatchForm(request.POST, instance=batch)
        if form.is_valid():
            form.save()
            return redirect('batch_list')
    else:
        form = BatchForm(instance=batch)
    return render(request, 'inventory/generic_form.html', {'form': form, 'title': 'Editar Lote'})

@login_required
def batch_delete(request, pk):
    batch = get_object_or_404(Batch, pk=pk)
    if request.method == 'POST':
        batch.delete()
        return redirect('batch_list')
    return render(request, 'inventory/product_confirm_delete.html', {'product': batch}) # Reusing

