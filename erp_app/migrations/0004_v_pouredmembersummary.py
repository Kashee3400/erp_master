# Generated by Django 4.2 on 2025-05-02 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp_app', '0003_delete_accountperiod_delete_accountperiodhistory_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='V_PouredMemberSummary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('collection_date', models.DateField()),
                ('total_qty', models.FloatField()),
                ('avg_fat', models.FloatField()),
                ('avg_snf', models.FloatField()),
            ],
            options={
                'db_table': 'V_PouredMemberSummary',
                'managed': False,
            },
        ),
    ]
