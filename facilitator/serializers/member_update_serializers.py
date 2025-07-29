# serializers.py

from rest_framework import serializers
from ..models.member_update_model import UpdateRequest,UpdateRequestDocument
from ..choices import RequestTypeChoices, RequestStatus
from django.utils.translation import gettext_lazy as _

class UpdateRequestListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)

    class Meta:
        model = UpdateRequest
        fields = [
            "id",
            "request_id",
            "mpp_name",
            "mpp_ex_code",
            "member_name",
            "mobile_number",
            "role_type",
            "request_type",
            "status",
            "created_by_name",
        ]


class UpdateRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UpdateRequest
        fields = "__all__"
        read_only_fields = [
            "id",
            "status",
            "request_id",
            "reviewed_by",
            "created_by",
            "created_at",
            "reviewed_at",
            "updated_at",
            "updated_by",
        ]

    def validate(self, data):
        request_type = data.get("request_type")
        if request_type == RequestTypeChoices.MOBILE:
            if not data.get("mobile_number"):
                raise serializers.ValidationError("mobile number is required for mobile update.")
        elif request_type == RequestTypeChoices.BANK:
            required_fields = ["new_account_number", "bank_name", "branch_name", "ifsc"]
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError(f"{field.replace('_', ' ').capitalize()} is required for bank update.")
            if data.get("new_account_holder_name") and data.get("member_name"):
                if data["new_account_holder_name"].strip().lower() != data["member_name"].strip().lower():
                    if not data.get("affidavit_file"):
                        raise serializers.ValidationError("Affidavit file is required if account holder name is changed.")
        
        return data

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["created_by"] = user
        validated_data["updated_by"] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_by"] = self.context["request"].user
        return super().update(instance, validated_data)


class UpdateRequestDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UpdateRequestDocument
        fields = [
            "id",
            "request",
            "document_type",
            "file",
            "original_filename",
            "file_size",
            "content_type",
            "description",
        ]
        read_only_fields = ["id", "original_filename", "file_size", "content_type","created_by","created_at","updated_by"]

    def create(self, validated_data):
        file = validated_data.get("file")

        if not file:
            raise serializers.ValidationError({"file": "File is required."})

        validated_data["original_filename"] = getattr(file, "name", "")
        validated_data["file_size"] = getattr(file, "size", 0)
        validated_data["content_type"] = getattr(file, "content_type", "application/octet-stream")
        user = self.context["request"].user
        validated_data["created_by"] = user
        validated_data["updated_by"] = user

        return super().create(validated_data)
