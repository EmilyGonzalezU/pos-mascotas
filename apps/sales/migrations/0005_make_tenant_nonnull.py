"""Make tenant non-nullable on sales models after data population."""
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0004_order_tenant_payment_tenant'),
        ('tenants', '0002_default_tenant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='tenant',
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='%(class)s_set',
                to='tenants.tenant',
                verbose_name='Tienda',
            ),
        ),
        migrations.AlterField(
            model_name='payment',
            name='tenant',
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='%(class)s_set',
                to='tenants.tenant',
                verbose_name='Tienda',
            ),
        ),
    ]
