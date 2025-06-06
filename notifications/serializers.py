from rest_framework import serializers

class RegisterDeviceSerializer(serializers.Serializer):
    device_id = serializers.CharField()
    fcm_token = serializers.CharField()

class SendUserNotificationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    title = serializers.CharField()
    body = serializers.JSONField()
    route = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    id = serializers.IntegerField(required=False, allow_null=True)
