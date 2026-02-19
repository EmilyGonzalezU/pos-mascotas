from django.db import models
from apps.core.managers import TenantManager, get_current_tenant


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    'created' and 'modified' fields.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")
    modified_at = models.DateTimeField(auto_now=True, verbose_name="Modificado el")

    class Meta:
        abstract = True


class TenantAwareModel(TimeStampedModel):
    """
    Abstract model that isolates data by tenant.
    Auto-filters queries via TenantManager and auto-assigns tenant on save.
    """
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='%(class)s_set',
        editable=False,
        verbose_name="Tienda",
    )

    objects = TenantManager()
    all_objects = models.Manager()  # Escape hatch: unscoped queries

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.tenant_id:
            tenant = get_current_tenant()
            if tenant:
                self.tenant = tenant
        super().save(*args, **kwargs)
