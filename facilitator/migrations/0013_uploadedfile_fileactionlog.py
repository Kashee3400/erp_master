# Generated by Django 4.2 on 2025-06-30 07:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import facilitator.models.file_models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('facilitator', '0012_userprofile_is_email_verified'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='uploads/', validators=[facilitator.models.file_models.validate_file_extension])),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to='thumbnails/')),
                ('original_name', models.CharField(max_length=255)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('size', models.BigIntegerField()),
                ('media_type', models.CharField(choices=[('image', 'Image'), ('video', 'Video'), ('audio', 'Audio'), ('document', 'Document'), ('other', 'Other')], default='other', max_length=20)),
                ('mime_type', models.CharField(blank=True, max_length=50)),
                ('file_hash', models.CharField(max_length=64, unique=True)),
                ('notes', models.TextField(blank=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('geo_location', models.CharField(blank=True, max_length=255)),
                ('view_count', models.PositiveIntegerField(default=0)),
                ('download_count', models.PositiveIntegerField(default=0)),
                ('tags', taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
                ('uploaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FileActionLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('uploaded', 'Uploaded'), ('viewed', 'Viewed'), ('downloaded', 'Downloaded'), ('deleted', 'Deleted')], max_length=20)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('performed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('uploaded_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='action_logs', to='facilitator.uploadedfile')),
            ],
        ),
    ]
