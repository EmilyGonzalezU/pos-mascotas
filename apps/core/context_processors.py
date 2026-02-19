"""
Context processors that inject tenant and staff info into all templates.
"""


def tenant_context(request):
    """Inject current tenant and staff profile into template context."""
    context = {
        'current_tenant': getattr(request, 'tenant', None),
    }

    if hasattr(request, 'user') and request.user.is_authenticated:
        try:
            profile = request.user.staff_profile
            context['staff_profile'] = profile
            context['user_role'] = profile.get_role_display()
            context['user_role_code'] = profile.role
        except Exception:
            context['staff_profile'] = None
            context['user_role'] = None
            context['user_role_code'] = None

    return context
