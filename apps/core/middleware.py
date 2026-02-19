"""
TenantMiddleware — resolves tenant from subdomain or header and sets thread-local context.
"""
from apps.core.managers import set_current_tenant


class TenantMiddleware:
    """
    Resolves the current tenant from the request and sets it in thread-local storage.
    Resolution order:
      1. Subdomain (e.g. tienda1.nutripet.cl)
      2. X-Tenant-ID header (for API/development)
      3. Default tenant (first active tenant, for single-tenant setups)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from apps.tenants.models import Tenant

        tenant = None

        # 1. Try subdomain resolution
        host = request.get_host().split(':')[0]  # Remove port
        parts = host.split('.')
        if len(parts) > 2:
            subdomain = parts[0]
            tenant = Tenant.objects.filter(
                subdomain=subdomain, is_active=True
            ).first()

        # 2. Fallback: X-Tenant-ID header
        if tenant is None:
            tenant_id = request.headers.get('X-Tenant-ID')
            if tenant_id:
                tenant = Tenant.objects.filter(
                    id=tenant_id, is_active=True
                ).first()

        # 3. Fallback: default tenant (first active)
        if tenant is None:
            tenant = Tenant.objects.filter(is_active=True).first()

        request.tenant = tenant
        set_current_tenant(tenant)

        response = self.get_response(request)

        # Clean up thread-local
        set_current_tenant(None)
        return response
