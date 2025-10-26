from rest_framework import serializers
from django.contrib.auth import get_user_model
from .model import Notification, NotificationTemplate, NotificationPreferences

User = get_user_model()


class RegisterDeviceSerializer(serializers.Serializer):
    device_id = serializers.CharField()
    fcm_token = serializers.CharField()


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notification instances"""

    template_name = serializers.CharField(source="template.name", read_only=True)
    category = serializers.CharField(source="template.category", read_only=True)
    sender_name = serializers.CharField(source="sender.get_full_name", read_only=True)
    time_since = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "uuid",
            "template_name",
            "category",
            "title",
            "body",
            "notification_type",
            "priority",
            "deep_link_url",
            "app_route",
            'is_subroute',
            "is_read",
            'object_id',
            "read_at",
            "created_at",
            "sender_name",
            "time_since",
            "expires_at",
            "status",
        ]
        read_only_fields = ["uuid", "created_at", "read_at"]

    def get_time_since(self, obj):
        """Get human-readable time since creation"""
        from django.utils.timesince import timesince

        return timesince(obj.created_at)


class NotificationPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for notification preferences"""

    template_name = serializers.CharField(source="template.name", read_only=True)

    class Meta:
        model = NotificationPreferences
        fields = [
            "id",
            "template_name",
            "category",
            "allow_push",
            "allow_email",
            "allow_sms",
            "allow_in_app",
            "quiet_hours_start",
            "quiet_hours_end",
            "timezone",
        ]
