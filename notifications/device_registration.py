from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import RegisterDeviceSerializer, SendUserNotificationSerializer
from member.models import UserDevice
from django.contrib.auth import get_user_model
from .fcm import _send_device_specific_notification

User = get_user_model()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register_device(request):
    serializer = RegisterDeviceSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    device, _ = UserDevice.objects.update_or_create(
        device=data["device_id"],
        defaults={"user": request.user, "fcm_token": data["fcm_token"]},
    )
    return Response({"message": "Device registered successfully."})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_user_notification(request):
    serializer = SendUserNotificationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    try:
        user = User.objects.get(id=data["user_id"])
        device = UserDevice.objects.filter(user=user).first()
        if not device:
            return Response({"error": "Device not found"}, status=404)

        notification = {
            "title": data["title"],
            "body": data["body"],
        }

        result = _send_device_specific_notification(
            device_token=device.device, notification=notification
        )
        return Response(result)

    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
