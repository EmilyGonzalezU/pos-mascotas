"""
Role-based access control decorators.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def get_staff_profile(user):
    """Get the StaffProfile for a user, or None if not found."""
    try:
        return user.staff_profile
    except Exception:
        return None


def role_required(*allowed_roles):
    """
    Decorator that restricts view access to users with specific roles.

    Usage:
        @role_required('OWNER', 'ADMIN')
        def my_admin_view(request):
            ...

        @role_required('OWNER', 'ADMIN', 'SUPERVISOR', 'CASHIER')
        def my_pos_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            profile = get_staff_profile(request.user)
            if profile is None:
                messages.error(request, "No tienes un perfil de personal asignado.")
                return redirect('pos_dashboard')
            if profile.role not in allowed_roles:
                messages.error(
                    request,
                    f"No tienes permisos para esta acción. Se requiere: "
                    f"{', '.join(allowed_roles)}"
                )
                return redirect('pos_dashboard')
            if not profile.is_active_staff:
                messages.error(request, "Tu cuenta de personal está desactivada.")
                return redirect('pos_dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def tenant_required(view_func):
    """
    Decorator that ensures the request has a valid tenant.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'tenant') or request.tenant is None:
            messages.error(request, "No se pudo identificar tu tienda.")
            return redirect('pos_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# Convenience shortcuts
def owner_required(view_func):
    """Only OWNER can access."""
    return role_required('OWNER')(view_func)


def admin_required(view_func):
    """OWNER or ADMIN can access."""
    return role_required('OWNER', 'ADMIN')(view_func)


def supervisor_required(view_func):
    """OWNER, ADMIN, or SUPERVISOR can access."""
    return role_required('OWNER', 'ADMIN', 'SUPERVISOR')(view_func)


def staff_required(view_func):
    """Any staff role can access (just needs a StaffProfile)."""
    return role_required('OWNER', 'ADMIN', 'SUPERVISOR', 'CASHIER')(view_func)
