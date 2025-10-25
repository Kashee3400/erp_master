from rest_framework import serializers
from .model import AppNotification
from django.contrib.auth import get_user_model
from .model import Notification, NotificationTemplate, NotificationPreferences

User = get_user_model()


class RegisterDeviceSerializer(serializers.Serializer):
    device_id = serializers.CharField()
    fcm_token = serializers.CharField()


class AppNotificationSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = AppNotification
        fields = [
            "id",
            "title",
            "message",
            "model",
            "object_id",
            "route",
            "custom_key",
            "is_subroute",
            "notification_type",
            "sent_via",
            "is_read",
            "read_at",
            "created_at",
            "sender_name",
            "avatar",
        ]
        read_only_fields = ["id", "read_at", "created_at", "recipient"]

    def get_sender_name(self, obj):
        if obj.sender:
            return obj.sender.get_full_name() or obj.sender.username
        return None

    def get_avatar(self, obj):
        if obj.sender and hasattr(obj.sender, "profile") and obj.sender.profile.avatar:
            request = self.context.get("request")
            avatar_url = obj.sender.profile.avatar.url
            if request is not None:
                return request.build_absolute_uri(avatar_url)
            return avatar_url
        return None

    def update(self, instance, validated_data):
        # If 'is_read' is being set to True, set the timestamp
        if validated_data.get("is_read") and not instance.is_read:
            instance.mark_as_read()
        return super().update(instance, validated_data)


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
