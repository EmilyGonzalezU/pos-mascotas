"""Django management command to set up POS data."""
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Set up POS: creates Branch, CashRegister, and configures admin user'

    def handle(self, *args, **options):
        from apps.tenants.models import Tenant, Branch
        from apps.sales.models import CashRegister
        from apps.accounts.models import StaffProfile
        from django.contrib.auth import get_user_model

        User = get_user_model()

        tenant = Tenant.objects.first()
        if not tenant:
            self.stderr.write("ERROR: No tenant found!")
            return

        self.stdout.write(f"Tenant: {tenant.name}")

        # Branch
        branch, created = Branch.objects.get_or_create(
            tenant=tenant,
            defaults={'name': 'Sucursal Principal', 'address': 'Local 1'}
        )
        self.stdout.write(f"{'CREATED' if created else 'EXISTS'} Branch: {branch.name}")

        # CashRegister
        register, created = CashRegister.objects.get_or_create(
            tenant=tenant,
            branch=branch,
            name='Caja 1',
            defaults={'is_active': True}
        )
        self.stdout.write(f"{'CREATED' if created else 'EXISTS'} Register: {register.name}")

        # User
        user = User.objects.filter(username='admin').first()
        if user:
            user.set_password('admin123')
            user.save()
            self.stdout.write("Password set: admin / admin123")

            profile, _ = StaffProfile.objects.get_or_create(
                user=user, defaults={'tenant': tenant, 'role': 'admin'}
            )
            profile.tenant = tenant
            profile.save()

        self.stdout.write(self.style.SUCCESS("\nPOS setup complete!"))
        self.stdout.write("Login: admin / admin123")
        self.stdout.write("POS: http://127.0.0.1:8000/")
        self.stdout.write("Shift: http://127.0.0.1:8000/shift/")
