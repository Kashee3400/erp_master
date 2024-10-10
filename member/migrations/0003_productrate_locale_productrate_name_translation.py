# Generated by Django 4.2 on 2024-08-29 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0002_sahayakincentives_productrate'),
    ]

    operations = [
        migrations.AddField(
            model_name='productrate',
            name='locale',
            field=models.CharField(choices=[('en', 'English'), ('hi', 'Hindi')], default='en', help_text='Locale of the product data (e.g., en for English, hi for Hindi)', max_length=10, verbose_name='Locale'),
        ),
        migrations.AddField(
            model_name='productrate',
            name='name_translation',
            field=models.CharField(blank=True, help_text='Translated name of the product in the selected locale', max_length=100, null=True, verbose_name='Translated Product Name'),
        ),
    ]