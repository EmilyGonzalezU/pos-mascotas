from django.conf import settings
from django.db import models
from apps.core.models import TenantAwareModel
from apps.customers.models import Customer
from apps.inventory.models import Product


class CashRegister(TenantAwareModel):
    """Caja registradora física en una sucursal."""
    name = models.CharField(max_length=100, verbose_name="Nombre Caja")
    branch = models.ForeignKey(
        'tenants.Branch', on_delete=models.CASCADE, related_name='registers',
        verbose_name="Sucursal",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activa")

    class Meta:
        verbose_name = "Caja Registradora"
        verbose_name_plural = "Cajas Registradoras"
        unique_together = ('tenant', 'branch', 'name')

    def __str__(self):
        return f"{self.name} — {self.branch.name}"


class Shift(TenantAwareModel):
    """Turno/apertura de caja."""
    register = models.ForeignKey(
        CashRegister, on_delete=models.CASCADE, related_name='shifts',
        verbose_name="Caja",
    )
    cashier = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        verbose_name="Cajero",
    )
    opened_at = models.DateTimeField(auto_now_add=True, verbose_name="Apertura")
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name="Cierre")
    opening_cash = models.IntegerField(default=0, verbose_name="Efectivo Inicial (CLP)")
    closing_cash = models.IntegerField(null=True, blank=True, verbose_name="Efectivo Final (CLP)")
    notes = models.TextField(blank=True, verbose_name="Observaciones")

    class Meta:
        verbose_name = "Turno"
        verbose_name_plural = "Turnos"
        ordering = ['-opened_at']

    def __str__(self):
        status = "Abierto" if self.is_open else "Cerrado"
        return f"Turno {self.register.name} — {status}"

    @property
    def is_open(self):
        return self.closed_at is None


class Order(TenantAwareModel):
    # --- Campos existentes (mantenidos) ---
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='orders',
    )
    total_clp = models.IntegerField(default=0, verbose_name="Total (CLP)")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha Venta")
    is_paid = models.BooleanField(default=False, verbose_name="Pagado")

    # --- Campos NUEVOS v2.0 ---
    shift = models.ForeignKey(
        Shift, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='orders',
        verbose_name="Turno",
    )
    branch = models.ForeignKey(
        'tenants.Branch', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Sucursal",
    )
    cashier = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Cajero",
    )
    order_number = models.CharField(
        max_length=20, blank=True, verbose_name="Nro. Boleta/Ticket",
    )
    is_voided = models.BooleanField(default=False, verbose_name="Anulada")
    voided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='voided_orders',
    )
    void_reason = models.TextField(blank=True, verbose_name="Razón Anulación")

    # Desglose fiscal
    net_amount = models.IntegerField(default=0, verbose_name="Neto")
    iva_amount = models.IntegerField(default=0, verbose_name="IVA")

    def calculate_total(self):
        self.total_clp = sum(item.line_total_clp for item in self.items.all())
        self.net_amount = int(self.total_clp / 1.19)
        self.iva_amount = self.total_clp - self.net_amount
        self.save()

    def __str__(self):
        return f"Orden #{self.id} - ${self.total_clp}"

    class Meta:
        ordering = ['-date']
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Cantidad")
    unit_price_clp = models.IntegerField(verbose_name="Precio Unitario (CLP)")
    cost_at_sale = models.IntegerField(default=0, verbose_name="Costo al momento de venta")
    line_total_clp = models.IntegerField(verbose_name="Total Línea (CLP)")

    def save(self, *args, **kwargs):
        total = float(self.unit_price_clp) * float(self.quantity)
        self.line_total_clp = int(round(total))
        super().save(*args, **kwargs)


class Payment(TenantAwareModel):
    METHOD_CHOICES = [
        ('CASH', 'Efectivo'),
        ('CARD', 'Tarjeta (Redcompra)'),
        ('TRANSFER', 'Transferencia'),
        ('MIXED', 'Pago Mixto'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount_clp = models.IntegerField(verbose_name="Monto")
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    transaction_id = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="ID Transacción / Nro Operación",
    )
    card_last_4 = models.CharField(
        max_length=4, blank=True, null=True, verbose_name="Últimos 4 Dígitos Tarjeta",
    )

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
