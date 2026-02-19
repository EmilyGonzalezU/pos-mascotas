from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import StaffProfile


class StaffProfileInline(admin.StackedInline):
    model = StaffProfile
    can_delete = False
    verbose_name_plural = 'Perfil de Personal'
    fields = ('role', 'branch', 'pin_code', 'is_active_staff')


# Extend the default User admin to show StaffProfile inline
class UserAdmin(BaseUserAdmin):
    inlines = [StaffProfileInline]


# Re-register User with the extended admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'branch', 'tenant', 'is_active_staff')
    list_filter = ('role', 'is_active_staff', 'branch')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user',)
