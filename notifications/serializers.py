from rest_framework import serializers
from .models import AppNotification
from django.contrib.auth import get_user_model

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
