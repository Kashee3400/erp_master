# Generated by Django 5.0 on 2024-06-24 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0006_productstockopening'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productstockopening',
            name='bin_location_code',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Bin Location Code'),
        ),
        migrations.AlterField(
            model_name='productstockopening',
            name='warehouse_code',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Warehouse Code'),
        ),
    ]
