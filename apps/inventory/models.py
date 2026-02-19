from django.db import models
from apps.core.models import TenantAwareModel


class Brand(TenantAwareModel):
    """Marca de alimento (Royal Canin, Purina, Champion, etc.)"""
    name = models.CharField(max_length=100, verbose_name="Marca")
    logo = models.ImageField(upload_to='brands/', blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Activa")

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        unique_together = ('tenant', 'name')

    def __str__(self):
        return self.name


class Supplier(TenantAwareModel):
    """Proveedor de productos."""
    name = models.CharField(max_length=200, verbose_name="Nombre Proveedor")
    rut = models.CharField(max_length=12, blank=True, verbose_name="RUT Proveedor")
    contact_name = models.CharField(max_length=100, blank=True, verbose_name="Contacto")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, verbose_name="Email")
    address = models.CharField(max_length=300, blank=True, verbose_name="Dirección")

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        unique_together = ('tenant', 'rut')

    def __str__(self):
        return self.name


class Category(TenantAwareModel):
    name = models.CharField(max_length=100, verbose_name="Nombre Categoría")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        unique_together = ('tenant', 'name')


class Product(TenantAwareModel):
    SPECIES_CHOICES = [
        ('DOG', 'Perro'),
        ('CAT', 'Gato'),
        ('BIRD', 'Ave'),
        ('FISH', 'Pez'),
        ('RODENT', 'Roedor'),
        ('REPTILE', 'Reptil'),
        ('OTHER', 'Exótico/Otro'),
    ]

    LIFECYCLE_CHOICES = [
        ('PUPPY', 'Cachorro/Kitten'),
        ('ADULT', 'Adulto'),
        ('SENIOR', 'Senior'),
        ('ALL', 'Todas las Etapas'),
    ]

    PROTEIN_CHOICES = [
        ('CHICKEN', 'Pollo'),
        ('BEEF', 'Res'),
        ('SALMON', 'Salmón'),
        ('LAMB', 'Cordero'),
        ('DUCK', 'Pato'),
        ('PORK', 'Cerdo'),
        ('MIXED', 'Mix/Varios'),
        ('VEGGIE', 'Vegetariano'),
        ('NONE', 'N/A'),
    ]

    # --- Campos existentes (mantenidos) ---
    sku = models.CharField(max_length=50, verbose_name="SKU")
    barcode = models.CharField(max_length=50, blank=True, null=True, verbose_name="Código de Barras")
    name = models.CharField(max_length=200, verbose_name="Nombre Producto")
    species = models.CharField(max_length=10, choices=SPECIES_CHOICES, default='DOG', verbose_name="Especie")
    lifecycle = models.CharField(max_length=10, choices=LIFECYCLE_CHOICES, default='ALL', verbose_name="Etapa de Vida")
    price_clp = models.IntegerField(verbose_name="Precio Venta (CLP)")  # IVA incluido
    is_bulk = models.BooleanField(default=False, verbose_name="Venta a Granel")
    stock = models.DecimalField(max_digits=10, decimal_places=3, default=0, verbose_name="Stock Disponible")

    # --- Campos NUEVOS v2.0 ---
    brand = models.ForeignKey(
        Brand, on_delete=models.PROTECT, related_name='products',
        verbose_name="Marca", null=True, blank=True,  # nullable para migración
    )
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Proveedor", related_name='products',
    )

    protein = models.CharField(
        max_length=10, choices=PROTEIN_CHOICES, default='NONE',
        verbose_name="Proteína Principal",
    )
    weight_kg = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        verbose_name="Peso Envase (Kg)",
    )

    # Costos y márgenes
    cost_clp = models.IntegerField(default=0, verbose_name="Costo Neto (CLP)")
    min_margin_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=20.00,
        verbose_name="Margen Mínimo (%)",
    )
    min_stock_alert = models.DecimalField(
        max_digits=10, decimal_places=3, default=5,
        verbose_name="Stock Mínimo (alerta)",
    )

    # Granel
    bulk_price_per_kg = models.IntegerField(
        null=True, blank=True, verbose_name="Precio por Kg (granel)",
    )

    # Imagen
    image = models.ImageField(upload_to='products/', blank=True)

    # Legacy — se mantiene para compatibilidad de datos existentes
    brand_name = models.CharField(max_length=100, blank=True, verbose_name="Marca (legacy)")

    def __str__(self):
        brand_display = self.brand.name if self.brand else self.brand_name
        return f"{self.name} ({brand_display})"

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        unique_together = ('tenant', 'sku')

    # --- Propiedades de negocio ---

    @property
    def margin_pct(self):
        """Calcula margen de utilidad actual."""
        if self.cost_clp and self.cost_clp > 0:
            net_price = self.price_clp / 1.19  # Extraer IVA
            return round(((net_price - self.cost_clp) / self.cost_clp) * 100, 2)
        return 0

    @property
    def is_margin_below_minimum(self):
        return self.margin_pct < float(self.min_margin_pct)

    @property
    def is_low_stock(self):
        return self.stock <= self.min_stock_alert


class Batch(TenantAwareModel):
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

    @property
    def is_expired(self):
        from datetime import date
        return self.expiration_date < date.today()

    @property
    def days_to_expiration(self):
        from datetime import date
        return (self.expiration_date - date.today()).days

    @property
    def is_near_expiration(self):
        """Alerta si faltan 30 días o menos."""
        return 0 < self.days_to_expiration <= 30
