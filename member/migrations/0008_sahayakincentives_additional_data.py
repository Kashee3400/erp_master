# Generated by Django 4.2 on 2024-11-16 05:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0007_sahayakincentives_recovery_deposit_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sahayakincentives',
            name='additional_data',
            field=models.JSONField(blank=True, help_text='Add additional data to be shown in sahayak recovery', null=True, verbose_name='Additional Data'),
        ),
    ]
