# Generated by Django 4.2 on 2025-06-16 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facilitator', '0009_vcgmeeting_is_deleted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vcgmeeting',
            name='status',
            field=models.CharField(choices=[('started', 'Started'), ('completed', 'Completed'), ('completed', 'Deleted')], default='started', help_text='Current status of the meeting.', max_length=20, verbose_name='Meeting Status'),
        ),
    ]
