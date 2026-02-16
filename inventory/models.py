from django.db import models
from core.models import TimeStampedModel

class Category(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre Categoría")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

class Product(TimeStampedModel):
    SPECIES_CHOICES = [
        ('DOG', 'Perro'),
        ('CAT', 'Gato'),
        ('OTHER', 'Exótico/Otro'),
    ]
    
    LIFECYCLE_CHOICES = [
        ('PUPPY', 'Cachorro/Kitten'),
        ('ADULT', 'Adulto'),
        ('SENIOR', 'Senior'),
        ('ALL', 'Todas las Etapas'),
    ]

    sku = models.CharField(max_length=50, unique=True, verbose_name="SKU")
    barcode = models.CharField(max_length=50, blank=True, null=True, unique=True, verbose_name="Código de Barras")
    name = models.CharField(max_length=200, verbose_name="Nombre Producto")
    brand = models.CharField(max_length=100, verbose_name="Marca")
    
    species = models.CharField(max_length=10, choices=SPECIES_CHOICES, default='DOG', verbose_name="Especie")
    lifecycle = models.CharField(max_length=10, choices=LIFECYCLE_CHOICES, default='ALL', verbose_name="Etapa de Vida")
    
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    
    price_clp = models.IntegerField(verbose_name="Precio Venta (CLP)") # Precio final IVA incluido
    is_bulk = models.BooleanField(default=False, verbose_name="Venta a Granel")
    stock = models.DecimalField(max_digits=10, decimal_places=3, default=0, verbose_name="Stock Disponible") # Decimales para kilo/gramos

    def __str__(self):
        return f"{self.name} ({self.brand})"

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

class Batch(TimeStampedModel):
    """Control de lotes y vencimientos"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='batches')
    batch_number = models.CharField(max_length=50, verbose_name="N° Lote")
    expiration_date = models.DateField(verbose_name="Fecha Vencimiento")
    quantity = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Cantidad Inicial")
    current_quantity = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Cantidad Actual")

    def __str__(self):
        return f"{self.product.name} - Lote {self.batch_number}"

    class Meta:
        verbose_name = "Lote"
        verbose_name_plural = "Lotes"
