from django.db import models
from apps.core.models import TimeStampedModel


class Tenant(TimeStampedModel):
    """Representa una tienda/empresa en la plataforma SaaS."""
    name = models.CharField(max_length=200, verbose_name="Nombre Comercial")
    legal_name = models.CharField(max_length=300, blank=True, verbose_name="Razón Social")
    rut_empresa = models.CharField(max_length=12, unique=True, verbose_name="RUT Empresa")
    subdomain = models.SlugField(max_length=63, unique=True)
    logo = models.ImageField(upload_to='tenants/logos/', blank=True)

    # Datos legales Chile
    giro = models.CharField(max_length=200, blank=True, verbose_name="Giro Comercial")
    direccion_legal = models.CharField(max_length=300, blank=True, verbose_name="Dirección Legal")
    comuna = models.CharField(max_length=100, blank=True, verbose_name="Comuna")
    region = models.CharField(max_length=100, blank=True, verbose_name="Región")

    # Configuración fiscal
    iva_rate = models.DecimalField(
        max_digits=4, decimal_places=2, default=19.00,
        verbose_name="Tasa IVA (%)"
    )
    currency = models.CharField(max_length=3, default='CLP', verbose_name="Moneda")

    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Tienda"
        verbose_name_plural = "Tiendas"
        ordering = ['name']

    def __str__(self):
        return self.name


class Branch(TimeStampedModel):
    """Sucursal de una tienda. Un tenant puede tener múltiples sucursales."""
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name='branches'
    )
    name = models.CharField(max_length=200, verbose_name="Nombre Sucursal")
    address = models.CharField(max_length=300, blank=True, verbose_name="Dirección")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    is_main = models.BooleanField(default=False, verbose_name="Sucursal Principal")
    is_active = models.BooleanField(default=True, verbose_name="Activa")

    class Meta:
        verbose_name = "Sucursal"
        verbose_name_plural = "Sucursales"
        unique_together = ('tenant', 'name')

    def __str__(self):
        return f"{self.name} ({self.tenant.name})"


class Subscription(TimeStampedModel):
    """Plan de suscripción activo del tenant."""
    PLAN_CHOICES = [
        ('FREE', 'Gratuito (1 sucursal, 1 caja)'),
        ('BASIC', 'Básico (2 sucursales, 3 cajas)'),
        ('PRO', 'Profesional (5 sucursales, 10 cajas)'),
        ('ENTERPRISE', 'Empresarial (ilimitado)'),
    ]
    STATUS_CHOICES = [
        ('TRIAL', 'Período de Prueba'),
        ('ACTIVE', 'Activa'),
        ('PAST_DUE', 'Pago Pendiente'),
        ('CANCELLED', 'Cancelada'),
    ]

    tenant = models.OneToOneField(
        Tenant, on_delete=models.CASCADE, related_name='subscription'
    )
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='FREE')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TRIAL')
    trial_ends_at = models.DateTimeField(null=True, blank=True, verbose_name="Fin Período Prueba")
    current_period_end = models.DateTimeField(
        null=True, blank=True, verbose_name="Fin Período Actual"
    )
    max_branches = models.PositiveIntegerField(default=1, verbose_name="Máx. Sucursales")
    max_registers = models.PositiveIntegerField(default=1, verbose_name="Máx. Cajas")
    max_users = models.PositiveIntegerField(default=2, verbose_name="Máx. Usuarios")

    class Meta:
        verbose_name = "Suscripción"
        verbose_name_plural = "Suscripciones"

    def __str__(self):
        return f"{self.tenant.name} — {self.get_plan_display()}"
