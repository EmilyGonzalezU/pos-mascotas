from django.contrib import admin
from .models import Tenant, Branch, Subscription


class BranchInline(admin.TabularInline):
    model = Branch
    extra = 0


class SubscriptionInline(admin.StackedInline):
    model = Subscription
    extra = 0


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'rut_empresa', 'subdomain', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'rut_empresa', 'subdomain')
    inlines = [BranchInline, SubscriptionInline]


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'is_main', 'is_active')
    list_filter = ('tenant', 'is_main', 'is_active')
    search_fields = ('name',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'plan', 'status', 'max_branches', 'max_registers')
    list_filter = ('plan', 'status')
