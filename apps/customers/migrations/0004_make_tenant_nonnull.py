"""Make tenant non-nullable on customer models after data population."""
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0003_customer_tenant_pet_tenant_alter_customer_rut_and_more'),
        ('tenants', '0002_default_tenant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
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
            model_name='pet',
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
