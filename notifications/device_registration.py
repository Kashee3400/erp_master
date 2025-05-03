from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from member.models import UserDevice
from django.contrib.auth import get_user_model
from .fcm import _send_device_specific_notification

User = get_user_model()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register_device(request):
    device_id = request.data.get("device_id")
    fcm_token = request.data.get("fcm_token")

    if not device_id or not fcm_token:
        return Response({"error": "Missing device_id or fcm_token"}, status=400)
    device, _ = UserDevice.objects.update_or_create(
        device=device_id, defaults={"user": request.user, "fcm_token": fcm_token}
    )

    return Response({"message": "Device registered successfully."})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_user_notification(request):
    user_id = request.data.get("user_id")
    title = request.data.get("title")
    body = request.data.get("body")
    route = request.data.get("route")
    ref_id = request.data.get("id")

    try:
        user = User.objects.get(id=user_id)
        device = UserDevice.objects.filter(user=user).first()
        if not device:
            return Response({"error": "Device not found"}, status=404)

        # data_payload = {
        #     "route": route,
        #     "id": ref_id
        # }
        notification = {
            "title": title,
            "body": body,
        }
        result = _send_device_specific_notification(
            device_token=device.device, notification=notification
        )
        return Response(result)

    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
