from rest_framework import generics, status, viewsets, exceptions, decorators, filters
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
import requests
from member.serialzers import VerifyOTPSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.translation import gettext_lazy as _
from member.models import UserDevice, OTP

User = get_user_model()


class GenerateOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get("phone_number")

        if not phone_number:
            return Response(
                {"status": "error", "message": _("Phone number is required.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not User.objects.filter(username=phone_number).exists():
            return Response(
                {
                    "status": "error",
                    "message": _("User does not exist. Please contact support."),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Delete previous OTPs for this number
        OTP.objects.filter(phone_number=phone_number).delete()

        # Create new OTP
        new_otp = OTP.objects.create(phone_number=phone_number)

        sent, info = send_sms_api(mobile=phone_number, otp=new_otp.otp)
        if not sent:
            return Response(
                {
                    "status": "error",
                    "message": _("Failed to send OTP. Please try again later."),
                    "details": info,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"status": "success", "message": _("OTP sent successfully.")},
            status=status.HTTP_200_OK,
        )


class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]
        otp_value = serializer.validated_data["otp"]
        device_id = request.data.get("device_id")

        if not device_id:
            return Response(
                {"status": "error", "message": _("Device ID is required.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            otp = OTP.objects.get(phone_number=phone_number, otp=otp_value)
        except OTP.DoesNotExist:
            return Response(
                {"status": "error", "message": _("Invalid OTP.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not otp.is_valid():
            otp.delete()
            return Response(
                {"status": "error", "message": _("OTP has expired.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user, _ = User.objects.get_or_create(username=phone_number)
        UserDevice.objects.filter(Q(user=user) | Q(device=device_id)).delete()
        UserDevice.objects.create(user=user, device=device_id)
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        otp.delete()
        return Response(
            {
                "status": "success",
                "message": _("Authentication successful."),
                "data": {
                    "phone_number": user.username,
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "device_id": device_id,
                },
            },
            status=status.HTTP_200_OK,
        )


def send_sms_api(mobile, otp):
    url = "https://alerts.cbis.in/SMSApi/send"
    params = {
        "userid": "kashee",
        "output": "json",
        "password": "Kash@12",
        "sendMethod": "quick",
        "mobile": mobile,
        "msg": f"आपका काशी ई-डेयरी लॉगिन ओटीपी कोड {otp} है। किसी के साथ साझा न करें- काशी डेरी",
        "senderid": "KMPCLV",
        "msgType": "unicode",
        "dltEntityId": "1001453540000074525",
        "dltTemplateId": "1007171661975556092",
        "duplicatecheck": "true",
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get("ErrorCode") == "000":
            return True, data
        return False, data
    except requests.RequestException as e:
        return False, str(e)


class VerifySession(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        device_id = request.data.get("device_id")

        if not device_id:
            return Response(
                {"status": "error", "message": "Device ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        is_valid = UserDevice.objects.filter(user=user, device=device_id).exists()

        if is_valid:
            return Response(
                {
                    "status": "success",
                    "is_valid": True,
                    "message": "Session is valid for this device.",
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "status": "unauthorized",
                    "is_valid": False,
                    "message": "Device not recognized or session invalid.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response(
                {"message": _("Refresh token is required")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # Ensure token blacklisting is enabled in settings
            return Response(
                {"message": _("Logout successful")},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception as e:
            return Response(
                {
                    "message": _("Invalid refresh token or already blacklisted"),
                    "error": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
