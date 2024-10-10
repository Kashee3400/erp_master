from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
import requests
from .serialzers import *
from erp_app.models import MemberMaster,MppCollectionAggregation
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _
from .models import UserDevice
from rest_framework.response import Response
from django.contrib.auth import get_user_model

User = get_user_model()


class GenerateOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get("phone_number")
        if (
            not MemberMaster.objects.using("sarthak_kashee")
            .filter(mobile_no=phone_number)
            .exists()
        ):
            return Response(
                {"status": 400, "message": _("Mobile no doest not exists")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        otp = OTP.objects.filter(phone_number=phone_number)
        if otp:
            otp.delete()
        notp = OTP.objects.create(phone_number=phone_number)
        send_sms_api(mobile=phone_number, otp=notp)
        return Response(
            {"status": 200, "message": _("OTP sent")}, status=status.HTTP_200_OK
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
        try:
            otp = OTP.objects.get(phone_number=phone_number, otp=otp_value)
        except OTP.DoesNotExist:
            return Response(
                {"status": status.HTTP_400_BAD_REQUEST, "message": _("Invalid OTP")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not otp.is_valid():
            otp.delete()
            return Response(
                {"status": status.HTTP_400_BAD_REQUEST, "message": _("OTP expired")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user, created = User.objects.get_or_create(username=phone_number)
        UserDevice.objects.filter(user=user).delete()
        UserDevice.objects.filter(device=device_id).delete()
        UserDevice.objects.create(user=user, device=device_id)
        refresh = RefreshToken.for_user(user)
        response = {
            "status": status.HTTP_200_OK,
            "phone_number": user.username,
            "message": _("Authentication successful"),
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "device_id": device_id,
        }
        return Response(response, status=status.HTTP_200_OK)


def send_sms_api(mobile, otp):
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
        "duplicatecheck": "true",
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return True
    else:
        return False


class VerifySession(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        device_id = request.data.get("device_id")
        if UserDevice.objects.filter(user=user, device=device_id).exists():
            return Response({"is_valid": True}, status=status.HTTP_200_OK)
        else:
            return Response({"is_valid": False}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {
                    "status": status.HTTP_205_RESET_CONTENT,
                    "message": _("Logout successful"),
                },
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception as e:
            return Response(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


from rest_framework import viewsets, status
from rest_framework.decorators import action


class UserAPiView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {"status": 200, "message": "Success", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(
            {"status": 200, "message": "Success", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"status": 201, "message": "Created successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {"status": 200, "message": "Updated successfully", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"status": 204, "message": "Deleted successfully", "data": {}},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(detail=False, methods=["get"])
    def user_details(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(
            {"status": 200, "message": "Success", "data": serializer.data},
            status=status.HTTP_200_OK,
        )


from django.http import HttpResponse
import os


def app_ads_txt(request):
    # Specify the path to the app-ads.txt file
    file_path = os.path.join(os.path.dirname(__file__), "static\\app-ads.txt")

    # Read the content of the file
    with open(file_path, "r") as file:
        content = file.read()

    # Return the content as a plain text response
    return HttpResponse(content, content_type="text/plain")


from django.http import JsonResponse


def custom_response(status, data=None, message=None, status_code=200):
    response_data = {"status": status, "message": message or "Success", "data": data}
    return JsonResponse(
        response_data, status=status_code, json_dumps_params={"ensure_ascii": False}
    )


from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from django_filters import rest_framework as filters


class ProductRateListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ("locale",)

    def get_queryset(self):
        locale = self.request.query_params.get("locale", "en")
        return ProductRate.objects.filter(locale=locale)

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            if queryset.exists():
                return custom_response(status="success", data=serializer.data)
            else:
                return custom_response(
                    status="error",
                    message="No products found",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
        except Exception as e:
            return custom_response(
                status="error",
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


from django.shortcuts import render
from django.http import JsonResponse, HttpResponseForbidden
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import OTP


class MyHomePage(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "member/pages/dashboards/default.html"  # Define the template path
    permission_required = "member_app.can_view_otp"

    # Custom behavior for GET request
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    # Custom behavior for POST request
    def post(self, request, *args, **kwargs):
        data = request.POST
        context = {
            "message": "This is a POST request!",
            "submitted_data": data,
        }
        # Optionally render a different template after POST, or just return JSON response
        return JsonResponse(context)

    def handle_no_permission(self):
        return HttpResponseForbidden(
            "You don't have permission to perform this action."
        )


class MyAppLists(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "member/pages/dashboards/app_list.html"  # Define the template path
    permission_required = "member_app.can_view_otp"

    # Custom behavior for GET request
    def get(self, request, *args, **kwargs):

        users = User.objects.all()
        member_master_list = []
        
        for user in users:
            member_master = MemberMaster.objects.using("sarthak_kashee").filter(
                mobile_no=user.username
            )
            if member_master.exists():
                data = member_master.first()
                mpp_collection_agg = MppCollectionAggregation.objects.filter(member_code = data.member_code).first()
                member_data_dict = {
                    "member_data":data,
                    "user":user,
                    "mpp_collection_agg":mpp_collection_agg,
                    "otp":OTP.objects.filter(phone_number=user.username).first()
                }
                member_master_list.append(member_data_dict)
                context = {"message": "This is a GET request!",'objects':member_master_list,}
        return render(request, self.template_name, context)

    # Custom behavior for POST request
    def post(self, request, *args, **kwargs):
        data = request.POST
        context = {
            "message": "This is a POST request!",
            "submitted_data": data,
        }
        # Optionally render a different template after POST, or just return JSON response
        return JsonResponse(context)

    def handle_no_permission(self):
        return HttpResponseForbidden(
            "You don't have permission to perform this action."
        )
