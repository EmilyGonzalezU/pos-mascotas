from django.conf import settings
from django.db import models
from apps.core.models import TenantAwareModel


class StaffProfile(TenantAwareModel):
    """Perfil de un empleado asociado a un tenant y opcionalmente a una sucursal."""

    ROLE_CHOICES = [
        ('OWNER', 'Dueño'),
        ('ADMIN', 'Administrador'),
        ('SUPERVISOR', 'Supervisor'),
        ('CASHIER', 'Cajero'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='staff_profile',
    )
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default='CASHIER',
        verbose_name="Rol",
    )
    branch = models.ForeignKey(
        'tenants.Branch',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Sucursal Asignada",
        related_name='staff',
    )
    pin_code = models.CharField(
        max_length=6, blank=True,
        verbose_name="PIN Rápido",
        help_text="PIN de 4-6 dígitos para cambio rápido de cajero",
    )
    is_active_staff = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Personal"
        verbose_name_plural = "Personal"
        unique_together = ('tenant', 'user')

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

    # --- Permission helpers ---

    @property
    def is_owner(self):
        return self.role == 'OWNER'

    @property
    def is_admin(self):
        return self.role in ('OWNER', 'ADMIN')

    @property
    def is_supervisor(self):
        return self.role in ('OWNER', 'ADMIN', 'SUPERVISOR')

    @property
    def can_manage_inventory(self):
        return self.role in ('OWNER', 'ADMIN', 'SUPERVISOR')

    @property
    def can_view_reports(self):
        return self.role in ('OWNER', 'ADMIN', 'SUPERVISOR')

    @property
    def can_manage_staff(self):
        return self.role in ('OWNER', 'ADMIN')

    @property
    def can_void_sales(self):
        return self.role in ('OWNER', 'ADMIN', 'SUPERVISOR')

    @property
    def can_manage_settings(self):
        return self.role == 'OWNER'
