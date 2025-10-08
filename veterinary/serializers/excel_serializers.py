# serializers.py - For API responses
from rest_framework import serializers
from ..models.excel_model import ExcelUploadSession


class UserSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for showing who uploaded the file."""

    class Meta:
        model = ExcelUploadSession._meta.get_field("uploaded_by").related_model
        fields = ["id", "username", "email"]


class ExcelUploadSessionListSerializer(serializers.ModelSerializer):
    uploaded_by = UserSummarySerializer(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    uploaded_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    processed_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = ExcelUploadSession
        fields = [
            "id",
            "filename",
            "uploaded_by",
            "uploaded_at",
            "status",
            "status_display",
            "processed_at",
            "processed",
            "total_rows",
            "error_message",
        ]
        read_only_fields = fields


class ExcelUploadSessionDetailSerializer(serializers.ModelSerializer):
    uploaded_by = UserSummarySerializer(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    uploaded_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    processed_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = ExcelUploadSession
        fields = [
            "id",
            "filename",
            "file",  # writable for uploads
            "uploaded_by",
            "uploaded_at",
            "status",
            "status_display",
            "processed_at",
            "processed",
            "total_rows",
            "error_message",
            "sheets_data",  # heavy, keep only in detail
            "metadata",  # heavy, keep only in detail
        ]
        read_only_fields = [
            "id",
            "filename",
            "uploaded_by",
            "uploaded_at",
            "status",
            "status_display",
            "processed_at",
            "processed",
            "total_rows",
            "error_message",
            "sheets_data",
        ]


class ExcelPreviewSerializer(serializers.Serializer):
    """Serializer for Excel preview data"""
    session_id = serializers.UUIDField()
    sheets = serializers.JSONField()
    filename = serializers.CharField()
    total_sheets = serializers.IntegerField()
    total_rows = serializers.IntegerField()


class ExcelImportResultSerializer(serializers.Serializer):
    """Serializer for import results"""
    success = serializers.BooleanField()
    total_created = serializers.IntegerField()
    total_updated = serializers.IntegerField()
    total_processed = serializers.IntegerField()
    errors = serializers.ListField(child=serializers.CharField(), required=False)
