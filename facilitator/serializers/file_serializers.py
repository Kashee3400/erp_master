from rest_framework import serializers
from ..models.file_models import UploadedFile
from taggit.serializers import TagListSerializerField, TaggitSerializer
from django.core.exceptions import ValidationError
import mimetypes
import hashlib

class UploadedFileSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False)
    get_url = serializers.CharField(read_only=True)
    get_thumb_url = serializers.CharField(read_only=True)

    class Meta:
        model = UploadedFile
        fields = [
            'id', 'file', 'original_name', 'uploaded_at', 'uploaded_by',
            'size', 'media_type', 'mime_type', 'file_hash',
            'ip_address', 'geo_location', 'view_count', 'download_count',
            'notes', 'tags', 'get_url', 'get_thumb_url'
        ]
        read_only_fields = [
            'id', 'uploaded_at', 'uploaded_by', 'original_name', 'size',
            'mime_type', 'file_hash', 'ip_address', 'geo_location',
            'view_count', 'download_count', 'get_url', 'get_thumb_url'
        ]

    def validate_file(self, file):
        allowed_extensions = [
            '.jpg', '.jpeg', '.png', '.gif',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx',
            '.mp3', '.wav', '.mp4', '.avi', '.mov'
        ]
        if not any(file.name.lower().endswith(ext) for ext in allowed_extensions):
            raise serializers.ValidationError("Unsupported file extension.")
        return file

    def calculate_file_hash(self, file_field):
        sha256 = hashlib.sha256()
        for chunk in file_field.chunks():
            sha256.update(chunk)
        return sha256.hexdigest()

    def create(self, validated_data):
        file = validated_data['file']

        file_hash = self.calculate_file_hash(file)
        if UploadedFile.objects.filter(file_hash=file_hash).exists():
            raise serializers.ValidationError("Duplicate file: already uploaded.")

        validated_data['original_name'] = file.name
        validated_data['file_hash'] = file_hash
        validated_data['size'] = file.size
        validated_data['mime_type'] = mimetypes.guess_type(file.name)[0] or 'application/octet-stream'

        # ip/geo will be added from view
        return super().create(validated_data)
