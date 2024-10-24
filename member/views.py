from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
import requests
from .serialzers import *
from erp_app.models import MemberMaster,MppCollectionAggregation,Mpp,Mcc
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _
from .models import UserDevice
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect, HttpResponse
import pandas as pd
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseForbidden
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import OTP
from django.core.paginator import Paginator
import pandas as pd
import csv
from django.contrib import messages
from django.shortcuts import redirect

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

import openpyxl

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
import openpyxl

class MyAppLists(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "member/pages/dashboards/app_list.html"
    permission_required = "member_app.can_view_otp"

    def get(self, request, *args, **kwargs):
        # Get the search query
        search_query = request.GET.get('search', '')

        # Get the page number from request
        page_number = request.GET.get('page', 1)
        page_size = 100  # or get from settings, e.g., settings.PAGE_SIZE

        # Filter users based on search query
        user_queryset = User.objects.all()
        if search_query:
            user_queryset = user_queryset.filter(username__icontains=search_query)

        # Create a paginator and get the page of users
        paginator = Paginator(user_queryset, page_size)
        page_obj = paginator.get_page(page_number)

        # Fetch mobile numbers for the paginated users
        user_mobile_numbers = list(page_obj.values_list('username', flat=True))

        # Fetch member masters based on the paginated mobile numbers
        member_masters = MemberMaster.objects.using("sarthak_kashee").filter(mobile_no__in=user_mobile_numbers)

        # Prepare a dictionary for fast lookups
        member_master_dict = {member.mobile_no: member for member in member_masters}

        member_master_list = []

        for user in page_obj.object_list:
            mobile_no = user.username
            member_master = member_master_dict.get(mobile_no)

            if member_master:
                mpp_collection_agg = MppCollectionAggregation.objects.filter(member_code=member_master.member_code).first()
                otp = OTP.objects.filter(phone_number=mobile_no).first()

                # Append member data to the list
                member_master_list.append({
                    "member_data": member_master,
                    "user": user,
                    "mpp_collection_agg": mpp_collection_agg,
                    "otp": otp,
                })

        context = {
            "message": "This is a GET request!",
            "objects": page_obj,
            "paginator": paginator,
            "member_master_list": member_master_list,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        selected_members = request.POST.getlist('selected_members')

        if action == "export":
            return self.export_selected(request, selected_members)
        elif action == "delete":
            return self.delete_selected(request, selected_members)

    def export_selected(self, request, selected_members):
        if not selected_members:
            messages.error(request, "No members were selected for export.")
            return redirect('list')

        # Query for existing members
        existing_members = MemberMaster.objects.using("sarthak_kashee").filter(member_code__in=selected_members)

        if not existing_members.exists():
            messages.error(request, "No valid members found for export.")
            return redirect('list')

        # Prepare Excel response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="application_installation_list.xlsx"'

        # Create a workbook and add a worksheet
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = 'Selected Members'

        # Write header row
        headers = ['MCC', 'MCC Code', 'MPP', 'MPP Code', 'Member Name', 'Member Code', 'Mobile No', 'OTP']
        worksheet.append(headers)

        # Pre-fetch related data for optimization
        mpp_collection_aggs = MppCollectionAggregation.objects.filter(member_code__in=existing_members.values_list('member_code', flat=True)).select_related('mpp')
        otps = OTP.objects.filter(phone_number__in=existing_members.values_list('mobile_no', flat=True))

        # Prepare dictionaries for fast lookups
        mpp_collection_dict = {agg.member_code: agg for agg in mpp_collection_aggs}
        otp_dict = {otp.phone_number: otp for otp in otps}

        # Write data to the Excel file
        for member_master in existing_members:
            mpp_collection_agg = mpp_collection_dict.get(member_master.member_code)
            otp = otp_dict.get(member_master.mobile_no)

            worksheet.append([
                mpp_collection_agg.mcc_name if mpp_collection_agg else '',
                mpp_collection_agg.mcc_tr_code if mpp_collection_agg else '',
                mpp_collection_agg.mpp.mpp_name if mpp_collection_agg and mpp_collection_agg.mpp else '',
                mpp_collection_agg.mpp.mpp_ex_code if mpp_collection_agg and mpp_collection_agg.mpp else '',
                member_master.member_name if member_master else '',
                f"'{mpp_collection_agg.member_tr_code}" if mpp_collection_agg else '',
                member_master.mobile_no if member_master else '',
                otp.otp if otp else '',
            ])

        messages.success(request, "Export completed successfully.")
        workbook.save(response)
        return response

    def delete_selected(self, request, selected_members):
        existing_members = MemberMaster.objects.using("sarthak_kashee").filter(member_code__in=selected_members)

        if not existing_members.exists():
            messages.error(request, "No valid members found for deletion.")
            return redirect('list')

        existing_member_codes = existing_members.values_list('member_code', flat=True)
        existing_members.delete()

        non_existent_members = set(selected_members) - set(existing_member_codes)

        messages.success(request, f"Successfully deleted {len(existing_member_codes)} members.")
        if non_existent_members:
            messages.warning(request, f"The following members could not be found: {', '.join(non_existent_members)}.")

        return redirect('list')

    def handle_no_permission(self):
        return HttpResponseForbidden("You don't have permission to perform this action.")
