"""
Data migration: Create a default tenant for existing data.
"""
from django.db import migrations


def create_default_tenant(apps, schema_editor):
    Tenant = apps.get_model('tenants', 'Tenant')
    Branch = apps.get_model('tenants', 'Branch')
    Subscription = apps.get_model('tenants', 'Subscription')

    tenant, created = Tenant.objects.get_or_create(
        rut_empresa='00.000.000-0',
        defaults={
            'name': 'Mi Tienda de Mascotas',
            'legal_name': 'Mi Tienda de Mascotas SpA',
            'subdomain': 'default',
            'is_active': True,
        }
    )

    if created:
        Branch.objects.create(
            tenant=tenant,
            name='Sucursal Principal',
            is_main=True,
            is_active=True,
        )
        Subscription.objects.create(
            tenant=tenant,
            plan='FREE',
            status='ACTIVE',
        )


def reverse_default_tenant(apps, schema_editor):
    Tenant = apps.get_model('tenants', 'Tenant')
    Tenant.objects.filter(rut_empresa='00.000.000-0').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_tenant, reverse_default_tenant),
    ]
