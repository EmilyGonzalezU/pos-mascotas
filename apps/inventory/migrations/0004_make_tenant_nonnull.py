"""Make tenant non-nullable on inventory models after data population."""
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_batch_tenant_category_tenant_product_tenant_and_more'),
        ('tenants', '0002_default_tenant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batch',
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
            model_name='category',
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
            model_name='product',
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
