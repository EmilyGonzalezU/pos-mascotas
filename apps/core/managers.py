"""
Thread-local tenant context and custom manager for automatic tenant scoping.
"""
from threading import local
from django.db import models

_thread_locals = local()


def set_current_tenant(tenant):
    """Set the current tenant in thread-local storage."""
    _thread_locals.tenant = tenant


def get_current_tenant():
    """Get the current tenant from thread-local storage."""
    return getattr(_thread_locals, 'tenant', None)


class TenantManager(models.Manager):
    """Custom manager that automatically filters querysets by current tenant."""

    def get_queryset(self):
        qs = super().get_queryset()
        tenant = get_current_tenant()
        if tenant is not None:
            return qs.filter(tenant=tenant)
        return qs

    def unscoped(self):
        """Return unfiltered queryset (bypass tenant scoping)."""
        return super().get_queryset()
