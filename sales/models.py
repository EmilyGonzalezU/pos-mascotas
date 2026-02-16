from django.db import models
from core.models import TimeStampedModel
from customers.models import Customer
from inventory.models import Product

class Order(TimeStampedModel):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    total_clp = models.IntegerField(default=0, verbose_name="Total (CLP)")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha Venta")
    is_paid = models.BooleanField(default=False, verbose_name="Pagado")

    def calculate_total(self):
        self.total_clp = sum(item.line_total_clp for item in self.items.all())
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
    quantity = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Cantidad") # 1.500 Kg
    unit_price_clp = models.IntegerField(verbose_name="Precio Unitario (CLP)")
    line_total_clp = models.IntegerField(verbose_name="Total Línea (CLP)")

    def save(self, *args, **kwargs):
        # Calcular total de línea: Precio * Cantidad convertida a float para calculo, luego int
        total = float(self.unit_price_clp) * float(self.quantity)
        self.line_total_clp = int(round(total))
        super().save(*args, **kwargs)

class Payment(TimeStampedModel):
    METHOD_CHOICES = [
        ('CASH', 'Efectivo'),
        ('CARD', 'Tarjeta (Redcompra)'),
        ('TRANSFER', 'Transferencia'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount_clp = models.IntegerField(verbose_name="Monto")
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="ID Transacción / Nro Operación")
    card_last_4 = models.CharField(max_length=4, blank=True, null=True, verbose_name="Últimos 4 Dígitos Tarjeta")
    
    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
