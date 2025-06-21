from ..models.feedback_model import *
from rest_framework import serializers
from django.utils import timezone
import base64
from django.core.files.base import ContentFile


class FeedbackCommentSerializer(serializers.ModelSerializer):
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = FeedbackComment
        fields = ("id", "user", "comment", "timestamp", "commented_by", "is_mine")
        read_only_fields = ("id", "timestamp", "commented_by", "is_mine")

    def get_is_mine(self, obj):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            return obj.user == request.user
        return False


class FeedbackFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackFile
        fields = "__all__"


class FeedbackSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.SerializerMethodField()
    comments = FeedbackCommentSerializer(many=True, read_only=True)
    new_comments = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
    base64_files = serializers.ListField(
        child=serializers.DictField(), write_only=True, required=False
    )

    class Meta:
        model = Feedback
        fields = [
            "id",
            "feedback_id",
            "sender",
            "assigned_to",
            "assigned_to_name",
            "status",
            "priority",
            "category",
            "message",
            "created_at",
            "updated_at",
            "resolved_at",
            "assigned_at",
            "comments",
            "rating",
            "progress",
            "new_comments",
            "base64_files",
            "mpp_code",
            "mcc_code",
            "member_code",
            "member_tr_code",
            "name",
            "mobile_no",
            "deleted",
        ]
        read_only_fields = (
            "id",
            "feedback_id",
            "created_at",
            "updated_at",
            "resolved_at",
            "assigned_at",
            "sender",
            "deleted",
        )

    def get_assigned_to_name(self, obj):
        return obj.assigned_to.get_full_name() if obj.assigned_to else None

    def validate_status(self, new_status):
        instance = self.instance
        if instance:
            current_status = instance.status
            allowed = ALLOWED_TRANSITIONS.get(current_status, [])
            if new_status not in allowed:
                raise serializers.ValidationError(
                    f"Invalid status transition from '{current_status}' to '{new_status}'."
                )
        return new_status

    def _save_base64_files(self, instance, base64_file_list):
        file_objs = []
        for idx, file_dict in enumerate(base64_file_list):
            file_data = base64.b64decode(file_dict.get("file", ""))
            file_name = f"{instance.feedback_id}_file_{idx}.jpg"
            content = ContentFile(file_data, name=file_name)

            # Save file content manually to disk
            temp_file = FeedbackFile(feedback=instance)
            temp_file.file.save(file_name, content, save=False)  # just store path
            file_objs.append(temp_file)

        FeedbackFile.objects.bulk_create(file_objs)

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        comments = validated_data.pop("new_comments", [])
        base64_files = validated_data.pop("base64_files", [])

        validated_data["sender"] = user
        feedback = super().create(validated_data)

        if base64_files:
            self._save_base64_files(feedback, base64_files)
            feedback.save()

        for comment_text in comments:
            FeedbackComment.objects.create(
                feedback=feedback,
                user=user,
                comment=comment_text,
                commented_by=user.get_full_name() or user.username,
            )

        return feedback

    def update(self, instance, validated_data):
        request = self.context.get("request")
        user = request.user
        comments = validated_data.pop("new_comments", [])
        base64_files = validated_data.pop("base64_files", [])
        print(validated_data.get("assigned_to"))
        # Handle assignment time
        if validated_data.get("assigned_to") and not instance.assigned_at:
            validated_data["assigned_at"] = timezone.now()

        # Handle status change using model's update_status
        new_status = validated_data.get("status")
        if new_status and new_status != instance.status:
            # Remove status from validated_data so .update() doesn't overwrite directly
            validated_data.pop("status")
            instance.update_status(
                new_status, user=user, reason="Status updated via API"
            )
        # Apply remaining updates
        instance = super().update(instance, validated_data)

        # Save base64 files
        if base64_files:
            self._save_base64_files(instance, base64_files)
            instance.save()

        # Save comments
        for comment_text in comments:
            FeedbackComment.objects.create(
                feedback=instance,
                user=user,
                comment=comment_text,
                commented_by=user.get_full_name() or user.username,
            )

        return instance
