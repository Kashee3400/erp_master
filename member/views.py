from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
import requests
from .serialzers import *
from erp_app.models import MemberMaster
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _
from .models import UserDevice

class GenerateOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        if not MemberMaster.objects.filter(mobile_no=phone_number).exists():
            return Response({'status': 400, 'message': _('Mobile no doest not exists')}, status=status.HTTP_400_BAD_REQUEST)
        otp = OTP.objects.filter(phone_number=phone_number)
        if otp:
            otp.delete()
        notp = OTP.objects.create(phone_number=phone_number)  
        send_sms_api(mobile=phone_number, otp=notp)
        return Response({'status': 200, 'message': _('OTP sent')}, status=status.HTTP_200_OK)
            
class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']
        otp_value = serializer.validated_data['otp']
        device_id = request.data.get('device_id')
        try:
            otp = OTP.objects.get(phone_number=phone_number, otp=otp_value)
        except OTP.DoesNotExist:
            return Response({'status':status.HTTP_400_BAD_REQUEST,'message': _('Invalid OTP')}, status=status.HTTP_400_BAD_REQUEST)
        
        if not otp.is_valid():
            otp.delete()
            return Response({'status':status.HTTP_400_BAD_REQUEST,'message': _('OTP expired')}, status=status.HTTP_400_BAD_REQUEST)
        user, created = User.objects.get_or_create(username=phone_number)
        UserDevice.objects.filter(user=user).delete()
        UserDevice.objects.filter(device=device_id).delete()
        UserDevice.objects.create(user=user, device=device_id)    
        refresh = RefreshToken.for_user(user)
        response = {
                "status": status.HTTP_200_OK,
                "phone_number": user.username,
                'message': _("Authentication successful"),
                'access_token': str(refresh.access_token),
                'refresh_token':str(refresh),
                'device_id': device_id 
        }
        return Response(response, status=status.HTTP_200_OK)

def send_sms_api(mobile,otp):
    url = "https://alerts.cbis.in/SMSApi/send"
    params = {
        "userid": "kashee",
        "output": "json",
        "password": "Kash@12",
        "sendMethod": "quick",
        "mobile": f"{mobile}",
        "msg": f"आपका काशी ई-डेयरी लॉगिन ओटीपी कोड {otp} है। किसी के साथ साझा न करें- काशी डेरी",
        "senderid": "KMPCLV",
        "msgType": "unicode",
        "dltEntityId": "1001453540000074525",
        "dltTemplateId": "1007171661975556092",
        "duplicatecheck": "true"
    }
    response = requests.get(url, params=params)    
    if response.status_code == 200:
        data = response.json()
        return True
    else:
        return False

class VerifySession(APIView):
    authentication_classes =[JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        device_id = request.data.get('device_id')
        if UserDevice.objects.filter(user=user, device=device_id).exists():
            return Response({'is_valid': True}, status=status.HTTP_200_OK)
        else:
            return Response({'is_valid': False}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({
                "status":status.HTTP_205_RESET_CONTENT,
                "message": _("Logout successful")
                }, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                "message": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
