from rest_framework import serializers
from .models import AppNotification

class RegisterDeviceSerializer(serializers.Serializer):
    device_id = serializers.CharField()
    fcm_token = serializers.CharField()

class SendUserNotificationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    title = serializers.CharField()
    body = serializers.JSONField()
    route = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    id = serializers.IntegerField(required=False, allow_null=True)

class AppNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppNotification
        fields = [
            'id', 'title', 'message', 'model', 'object_id',
            'route', 'custom_key', 'is_subroute',
            'notification_type', 'sent_via',
            'is_read', 'read_at', 'created_at'
        ]
        read_only_fields = ['id', 'read_at', 'created_at', 'recipient']

    def update(self, instance, validated_data):
        # If 'is_read' is being set to True, set the timestamp
        if validated_data.get('is_read') and not instance.is_read:
            instance.mark_as_read()
        return super().update(instance, validated_data)
