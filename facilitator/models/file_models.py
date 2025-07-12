import hashlib
import mimetypes
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from taggit.managers import TaggableManager

User = get_user_model()

def validate_file_extension(file):
    valid_extensions = [
        '.jpg', '.jpeg', '.png', '.gif',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx',
        '.mp3', '.wav', '.mp4', '.avi', '.mov'
    ]
    if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
        raise ValidationError(f"Unsupported file extension: {file.name}")

def calculate_file_hash(file_field):
    """Calculates SHA-256 hash of the file content."""
    sha256 = hashlib.sha256()
    for chunk in file_field.chunks():
        sha256.update(chunk)
    return sha256.hexdigest()

class UploadedFile(models.Model):
    MEDIA_TYPE_CHOICES = [
        ("image", "Image"),
        ("video", "Video"),
        ("audio", "Audio"),
        ("document", "Document"),
        ("other", "Other"),
    ]

    file = models.FileField(upload_to='uploads/', validators=[validate_file_extension])
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    original_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    size = models.BigIntegerField()
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES, default="other")
    mime_type = models.CharField(max_length=50, blank=True)
    file_hash = models.CharField(max_length=64, unique=True)
    notes = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    geo_location = models.CharField(max_length=255, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)
    tags = TaggableManager(blank=True)

    def __str__(self):
        return self.original_name

    def get_url(self):
        return self.file.url

    def get_thumb_url(self):
        return self.thumbnail.url if self.thumbnail else None

    def save(self, *args, **kwargs):
        # Auto populate MIME type if empty
        if not self.mime_type:
            self.mime_type = mimetypes.guess_type(self.file.name)[0] or 'application/octet-stream'

        # Set file size
        self.size = self.file.size

        # Compute and store hash
        if not self.file_hash:
            self.file_hash = calculate_file_hash(self.file)

        # Deduplication check (optional: raise error or skip save)
        if not self.pk and UploadedFile.objects.filter(file_hash=self.file_hash).exists():
            raise ValidationError("Duplicate file: already uploaded.")

        super().save(*args, **kwargs)


class FileActionLog(models.Model):
    ACTION_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('viewed', 'Viewed'),
        ('downloaded', 'Downloaded'),
        ('deleted', 'Deleted'),
    ]

    uploaded_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, related_name='action_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    def __str__(self):
        return f"{self.action} - {self.uploaded_file.original_name} @ {self.timestamp}"
