"""
Data migration: Create StaffProfile for existing superusers.
"""
from django.db import migrations


def create_superuser_profiles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    StaffProfile = apps.get_model('accounts', 'StaffProfile')
    Tenant = apps.get_model('tenants', 'Tenant')

    tenant = Tenant.objects.filter(is_active=True).first()
    if not tenant:
        return

    for user in User.objects.filter(is_superuser=True):
        StaffProfile.objects.get_or_create(
            user=user,
            defaults={
                'tenant': tenant,
                'role': 'OWNER',
                'is_active_staff': True,
            }
        )


def reverse(apps, schema_editor):
    StaffProfile = apps.get_model('accounts', 'StaffProfile')
    StaffProfile.objects.filter(role='OWNER').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('tenants', '0002_default_tenant'),
    ]

    operations = [
        migrations.RunPython(create_superuser_profiles, reverse),
    ]
