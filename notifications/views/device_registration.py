from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..serializers import RegisterDeviceSerializer
from member.models import UserDevice
from django.contrib.auth import get_user_model

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

