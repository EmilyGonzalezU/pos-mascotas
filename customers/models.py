from django.db import models
from core.models import TimeStampedModel
from core.utils import validate_rut
from django.core.exceptions import ValidationError

class Customer(TimeStampedModel):
    rut = models.CharField(max_length=12, unique=True, verbose_name="RUT Cliente")
    first_name = models.CharField(max_length=100, verbose_name="Nombre")
    last_name = models.CharField(max_length=100, verbose_name="Apellido", blank=True)
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")

    def clean(self):
        if self.rut and not validate_rut(self.rut):
            raise ValidationError({'rut': 'RUT inválido (Módulo 11 incorrecto)'})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.rut})"
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

class Pet(TimeStampedModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='pets')
    name = models.CharField(max_length=100, verbose_name="Nombre Mascota")
    species = models.CharField(max_length=50, verbose_name="Especie") # Perro, Gato, Conejo...
    breed = models.CharField(max_length=100, blank=True, verbose_name="Raza")
    age_years = models.PositiveIntegerField(null=True, blank=True, verbose_name="Edad (Años)")
    
    def __str__(self):
        return f"{self.name} ({self.species})"
    
    class Meta:
        verbose_name = "Mascota"
        verbose_name_plural = "Mascotas"
