from rest_framework import generics, status, viewsets, exceptions, decorators,filters
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
import requests
from .serialzers import *
from erp_app.models import (
    MemberMaster,
    Mpp,
    LocalSaleTxn,
    MemberHierarchyView,
    BillingMemberDetail,
    MppCollection,
    MppCollectionReferences,
    RmrdMilkCollection,
    PriceBook,
    PriceBookDetail,
    Mcc,
)
from erp_app.serializers import (
    MemberHierarchyViewSerializer,
    MccSerializer,
    MppSerializer,
)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from import_export.admin import ImportExportModelAdmin
from import_export.forms import (
    ImportForm,
)
from django_filters import FilterSet, DateFromToRangeFilter, DateTimeFromToRangeFilter
from .resources import SahayakIncentivesResource
import csv
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django_filters import rest_framework as filters
import os
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import *
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Avg,Q
from django.conf import settings
from .filters import SahayakIncentivesFilter,MemberHeirarchyFilter
from facilitator.authentication import ApiKeyAuthentication
from datetime import date
from django.utils.dateparse import parse_date
from .serialzers import NewsSerializer
from django.db.models import Sum, Count, Avg
from django.utils.timezone import make_aware, now
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta

from member.models import UserDevice

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
                {"status": 400, "message": _("Mobile number doest not exists")},
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


class GenerateSahayakOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get("phone_number")
        otp = OTP.objects.filter(phone_number=phone_number)
        if otp:
            otp.delete()
        notp = OTP.objects.create(phone_number=phone_number)
        send_sms_api(mobile=phone_number, otp=notp)
        return Response(
            {"status": 200, "message": _("OTP sent")}, status=status.HTTP_200_OK
        )


class VerifySahayakOTPView(generics.GenericAPIView):
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
        device, created = UserDevice.objects.update_or_create(
            user=user, defaults={"device": device_id}
        )
        refresh = RefreshToken.for_user(user)
        response = {
            "status": status.HTTP_200_OK,
            "phone_number": user.username,
            "message": _("Authentication successful"),
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "device_id": device_id,
            "mpp_code": device.mpp_code,
        }
        return Response(response, status=status.HTTP_200_OK)


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
        user = self.request.user
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

    @decorators.action(detail=False, methods=["get"])
    def user_details(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(
            {"status": 200, "message": "Success", "data": serializer.data},
            status=status.HTTP_200_OK,
        )


def app_ads_txt(request):
    # Specify the path to the app-ads.txt file
    file_path = os.path.join(os.path.dirname(__file__), "static\\app-ads.txt")

    # Read the content of the file
    with open(file_path, "r") as file:
        content = file.read()

    # Return the content as a plain text response
    return HttpResponse(content, content_type="text/plain")


def custom_response(status, data=None, message=None, status_code=200):
    response_data = {"status": status, "message": message or "Success", "data": data}
    return JsonResponse(
        response_data, status=status_code, json_dumps_params={"ensure_ascii": False}
    )


class ProductRateListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend,)
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
            
from .forms import DataFilterForm
class MyHomePage(LoginRequiredMixin, View):
    template_name = "member/pages/dashboards/default.html"
    permission_required = "member_app.can_view_otp"
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    

# class AppInstalledData(APIView):
#     permission_classes = [AllowAny]

#     def get(self, request, *args, **kwargs):
#         mcc_code = request.GET.get("mcc_code")
#         mpp_codes_param = request.GET.get("mpp_codes")  # comma-separated list
#         year = int(request.GET.get("year", now().year))
#         month = int(request.GET.get("month", now().month))

#         # Parse MPP codes if provided
#         mpp_codes = [code.strip() for code in mpp_codes_param.split(",")] if mpp_codes_param else None

#         # Date range for collection
#         start_date = make_aware(datetime(year, month, 1))
#         end_date = (
#             make_aware(datetime(year + 1, 1, 1)) - timedelta(seconds=1)
#             if month == 12
#             else make_aware(datetime(year, month + 1, 1)) - timedelta(seconds=1)
#         )

#         user_device_usernames = set(
#             UserDevice.objects.filter(module=None).values_list("user__username", flat=True)
#         )

#         mcc_queryset = Mcc.objects.filter(mcc_code=mcc_code) if mcc_code else Mcc.objects.all()
#         result = []

#         for mcc in mcc_queryset:
#             members_qs = MemberHierarchyView.objects.filter(
#                 mcc_code=mcc.mcc_code,
#                 is_active=True,
#                 is_default=True,
#             )

#             if mpp_codes:
#                 members_qs = members_qs.filter(mpp_code__in=mpp_codes)
#                 mpp_list = list(Mpp.objects.filter(mpp_code__in=mpp_codes))
#                 serialized_mpps = MppSerializer(mpp_list, many=True).data
#             else:
#                 serialized_mpps = None

#             total_members = members_qs.count()
#             member_mobiles = members_qs.values_list("mobile_no", flat=True)
#             installed_count = sum(1 for mobile in member_mobiles if mobile in user_device_usernames)
#             installed_percentage = (installed_count / total_members * 100) if total_members else 0

#             member_codes = members_qs.values_list("member_code", flat=True)
#             collections = MppCollection.objects.filter(
#                 collection_date__range=(start_date, end_date),
#                 member_code__in=member_codes,
#             )
#             no_of_pourers = collections.values("member_code").annotate(
#                 days=Count(TruncDate("collection_date"), distinct=True)
#             ).count()

#             result.append({
#                 "mcc": MccSerializer(mcc).data,
#                 "mpp": serialized_mpps,
#                 "total_members": total_members,
#                 "app_installed_by_member": installed_count,
#                 "installed_percentage": round(installed_percentage, 2),
#                 "no_of_pourers": no_of_pourers,
#             })

#         return Response(result, status=status.HTTP_200_OK)

class AppInstalledData(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        mcc_code = request.GET.get("mcc_code")
        mpp_codes_param = request.GET.get("mpp_codes")  # comma-separated list
        year = int(request.GET.get("year", now().year))
        month = int(request.GET.get("month", now().month))

        mpp_codes = [code.strip() for code in mpp_codes_param.split(",")] if mpp_codes_param else None

        start_date = make_aware(datetime(year, month, 1))
        end_date = (
            make_aware(datetime(year + 1, 1, 1)) - timedelta(seconds=1)
            if month == 12
            else make_aware(datetime(year, month + 1, 1)) - timedelta(seconds=1)
        )

        user_device_usernames = set(
            UserDevice.objects.filter(module=None).values_list("user__username", flat=True)
        )

        mcc_queryset = Mcc.objects.filter(mcc_code=mcc_code) if mcc_code else Mcc.objects.all()
        result = []

        # Grand totals
        total_members_all = 0
        installed_count_all = 0
        total_pourers_all = 0

        for mcc in mcc_queryset:
            members_qs = MemberHierarchyView.objects.filter(
                mcc_code=mcc.mcc_code,
                is_active=True,
                is_default=True,
            )

            if mpp_codes:
                members_qs = members_qs.filter(mpp_code__in=mpp_codes)
                mpp_list = list(Mpp.objects.filter(mpp_code__in=mpp_codes))
                serialized_mpps = MppSerializer(mpp_list, many=True).data
            else:
                serialized_mpps = None

            total_members = members_qs.count()
            member_mobiles = members_qs.values_list("mobile_no", flat=True)
            installed_count = sum(1 for mobile in member_mobiles if mobile in user_device_usernames)
            installed_percentage = (installed_count / total_members * 100) if total_members else 0

            member_codes = members_qs.values_list("member_code", flat=True)
            collections = MppCollection.objects.filter(
                collection_date__range=(start_date, end_date),
                member_code__in=member_codes,
            )
            no_of_pourers = collections.values("member_code").annotate(
                days=Count(TruncDate("collection_date"), distinct=True)
            ).count()

            result.append({
                "mcc": MccSerializer(mcc).data,
                "mpp": serialized_mpps,
                "total_members": total_members,
                "app_installed_by_member": installed_count,
                "installed_percentage": round(installed_percentage, 2),
                "no_of_pourers": no_of_pourers,
            })

            # Accumulate totals
            total_members_all += total_members
            installed_count_all += installed_count
            total_pourers_all += no_of_pourers

        # Append grand total row
        grand_total_percentage = (installed_count_all / total_members_all * 100) if total_members_all else 0
        result.append({
            "mcc": {"name": "Grand Total"},
            "mpp": None,
            "total_members": total_members_all,
            "app_installed_by_member": installed_count_all,
            "installed_percentage": round(grand_total_percentage, 2),
            "no_of_pourers": total_pourers_all,
            "is_total": True  # Helps frontend to identify the total row
        })

        return Response(result, status=status.HTTP_200_OK)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class CdaAggregationDaywiseMilktypeViewSet(viewsets.ModelViewSet):
    queryset = CdaAggregation.objects.all()
    serializer_class = CdaAggregationDaywiseMilktypeSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]

    def get_financial_year_dates(self, input_date):
        year = input_date.year
        if input_date.month < 4:
            start_year = year - 1
            end_year = year
        else:
            start_year = year
            end_year = year + 1
        start_date = date(start_year, 4, 1)
        end_date = date(end_year, 3, 31)
        return start_date, end_date

    def format_aggregates(self, aggregates):
        formatted_aggregates = {}
        for key, value in aggregates.items():
            if value is not None:
                formatted_aggregates[key] = round(value, 2)
            else:
                formatted_aggregates[key] = None
        return formatted_aggregates

    def list(self, request, *args, **kwargs):
        device = self.request.user.device
        collection_date_param = request.query_params.get("created_at", None)
        if collection_date_param and collection_date_param.lower() != "null":
            collection_date = parse_date(collection_date_param)
        else:
            collection_date = now().date()
        mpp = Mpp.objects.filter(mpp_ex_code=device.mpp_code).last()
        if not mpp:
            return Response(
                {
                    "status": "error",
                    "message": f"No MPP found for the provided mppcode: {device.mpp_code}",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        start_date, end_date = self.get_financial_year_dates(collection_date)
        current_date_data = CdaAggregation.objects.filter(
            collection_date__date=collection_date, mpp_code=mpp.mpp_code
        )

        fy_data = CdaAggregation.objects.filter(
            collection_date__gte=start_date,
            collection_date__lte=end_date,
            mpp_code=mpp.mpp_code,
        ).aggregate(
            total_composite_qty=Sum("composite_qty"),
            total_dispatch_qty=Sum("dispatch_qty"),
            total_actual_qty=Sum("actual_qty"),
            avg_composite_fat=Avg("composite_fat"),
            avg_dispatch_fat=Avg("dispatch_fat"),
            avg_actual_fat=Avg("actual_fat"),
            avg_composite_snf=Avg("composite_snf"),
            avg_dispatch_snf=Avg("dispatch_snf"),
            avg_actual_snf=Avg("actual_snf"),
        )

        # Format the aggregated data
        formatted_fy_data = self.format_aggregates(fy_data)

        page_morning = self.paginate_queryset(current_date_data.filter(shift="Morning"))
        page_evening = self.paginate_queryset(current_date_data.filter(shift="Evening"))
        if page_morning is not None:
            serializer_morning = self.get_serializer(page_morning, many=True)
            serializer_evening = self.get_serializer(page_evening, many=True)
            return self.get_paginated_response(
                {
                    "status": "success",
                    "current_date_data": serializer_morning.data,
                    "current_date_data_evening": serializer_evening.data,
                    "fy_data": formatted_fy_data,
                    "message": "Success",
                }
            )

        serializer_morning = self.get_serializer(
            current_date_data.filter(shift="Morning"), many=True
        )
        serializer_evening = self.get_serializer(
            current_date_data.filter(shift="Evening"), many=True
        )
        return Response(
            {
                "status": "success",
                "current_date_data": serializer_morning.data,
                "current_date_data_evening": serializer_evening.data,
                "fy_data": formatted_fy_data,
                "message": "Success",
            },
            status=status.HTTP_200_OK,
        )


class SahayakIncentivesAllInOneView(LoginRequiredMixin, View, ImportExportModelAdmin):
    template_name = "member/pages/dashboards/sahayak_incentives_all.html"
    form_class = SahayakIncentivesForm
    excel_form = ImportForm
    resource_class = SahayakIncentivesResource
    import_template_name = "member/form/confirm_excel_import.html"
    success_url = reverse_lazy("sahayak_incentives_list")
    model = SahayakIncentives

    export_template_name = "member/form/export.html"

    def get(self, request, *args, **kwargs):
        query = request.GET.get("q", "")
        filter_class = SahayakIncentivesFilter(
            request.GET, queryset=SahayakIncentives.objects.all().order_by("-id")
        )
        incentives = self.get_filtered_incentives(query, filter_class)
        # Pagination setup
        page_number = request.GET.get("page", 1)
        per_page = (
            settings.PAGINATION_SIZE if hasattr(settings, "PAGINATION_SIZE") else 100
        )
        paginator = Paginator(incentives, per_page)
        paginated_incentives = paginator.get_page(page_number)
        actions = [
            {"value": "bulk_delete", "label": "Delete Selected"},
            {"value": "export_csv", "label": "Export Selected"},
        ]
        import_form = self.create_import_form(request=request)
        total_rows = incentives.count()
        context = {
            "objects": paginated_incentives,
            "form": self.form_class(),
            "filter": filter_class,
            "import_form": import_form,
            "actions": actions,
            "total_rows": total_rows,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        import_excel = request.POST.get("excel_import")
        process_import = request.POST.get("process_import")
        if action:
            handler = getattr(self, f"handle_{action}", None)
            if handler:
                return handler(request)
        elif import_excel and import_excel == "excel_import":
            handler = getattr(self, f"import_action", None)
            return handler(request)
        elif process_import and process_import == "process_import":
            handler = getattr(self, f"process_import", None)
            return handler(request)
        return self.get(request)

    def get_filtered_incentives(self, query, filter_class):
        if query:
            return SahayakIncentives.objects.filter(
                Q(mcc_name__icontains=query)
                | Q(mpp_name__icontains=query)
                | Q(user__username__icontains=query)
            )
        return filter_class.qs

    def import_action(self, request, **kwargs):
        """
        Perform a dry_run of the import to make sure the import will not
        result in errors.  If there are no errors, save the user
        uploaded file to a local temp file that will be used by
        'process_import' for the actual import.
        """
        if not self.has_import_permission(request):
            raise PermissionDenied

        context = self.get_import_context_data()

        import_formats = self.get_import_formats()
        import_form = self.create_import_form(request)
        if request.POST and import_form.is_valid():
            input_format = import_formats[int(import_form.cleaned_data["format"])]()
            if not input_format.is_binary():
                input_format.encoding = self.from_encoding
            import_file = import_form.cleaned_data["import_file"]
            if self.is_skip_import_confirm_enabled():
                data = b""
                for chunk in import_file.chunks():
                    data += chunk
                try:
                    dataset = input_format.create_dataset(data)
                except Exception as e:
                    self.add_data_read_fail_error_to_form(import_form, e)
                if not import_form.errors:
                    result = self.process_dataset(
                        dataset,
                        import_form,
                        request,
                        raise_errors=False,
                        rollback_on_validation_errors=True,
                        **kwargs,
                    )
                    if not result.has_errors() and not result.has_validation_errors():
                        return self.process_result(result, request)
                    else:
                        context["result"] = result
            else:
                tmp_storage = self.write_to_tmp_storage(import_file, input_format)
                import_file.tmp_storage_name = tmp_storage.name
                try:
                    data = tmp_storage.read()
                    dataset = input_format.create_dataset(data)
                except Exception as e:
                    self.add_data_read_fail_error_to_form(import_form, e)
                else:
                    if len(dataset) == 0:
                        import_form.add_error(
                            "import_file",
                            _(
                                "No valid data to import. Ensure your file "
                                "has the correct headers or data for import."
                            ),
                        )
                if not import_form.errors:
                    # prepare kwargs for import data, if needed
                    res_kwargs = self.get_import_resource_kwargs(
                        request, form=import_form, **kwargs
                    )
                    resource = self.choose_import_resource_class(import_form, request)(
                        **res_kwargs
                    )
                    # prepare additional kwargs for import_data, if needed
                    imp_kwargs = self.get_import_data_kwargs(
                        request=request, form=import_form, **kwargs
                    )
                    result = resource.import_data(
                        dataset,
                        dry_run=True,
                        raise_errors=False,
                        file_name=import_file.name,
                        user=request.user,
                        **imp_kwargs,
                    )
                    context["result"] = result

                    if not result.has_errors() and not result.has_validation_errors():
                        context["confirm_form"] = self.create_confirm_form(
                            request, import_form=import_form
                        )
        else:
            res_kwargs = self.get_import_resource_kwargs(
                request=request, form=import_form, **kwargs
            )
        context.update(self.get_context_data())
        context["title"] = _("Import Sahayak Incentive Preview")
        context["form"] = import_form
        context["media"] = self.media + import_form.media
        context["import_error_display"] = self.import_error_display
        request.current_app = "Kashee ERP"
        return TemplateResponse(request, [self.import_template_name], context)

    def process_import(self, request, **kwargs):
        """
        Perform the actual import action (after the user has confirmed the import)
        """
        if not self.has_import_permission(request):
            raise PermissionDenied

        confirm_form = self.create_confirm_form(request)
        if confirm_form.is_valid():
            import_formats = self.get_import_formats()
            input_format = import_formats[int(confirm_form.cleaned_data["format"])](
                encoding=self.from_encoding
            )
            encoding = None if input_format.is_binary() else self.from_encoding
            tmp_storage_cls = self.get_tmp_storage_class()
            tmp_storage = tmp_storage_cls(
                name=confirm_form.cleaned_data["import_file_name"],
                encoding=encoding,
                read_mode=input_format.get_read_mode(),
                **self.get_tmp_storage_class_kwargs(),
            )

            data = tmp_storage.read()
            dataset = input_format.create_dataset(data)
            result = self.process_dataset(dataset, confirm_form, request, **kwargs)

            tmp_storage.remove()

            return self.process_result(result, request)
        else:
            context = self.get_context_data()
            context.update(
                {
                    "title": _("Import"),
                    "confirm_form": confirm_form,
                    "opts": self.model._meta,
                    "errors": confirm_form.errors,
                }
            )
            return TemplateResponse(request, [self.import_template_name], context)

    def process_result(self, result, request):
        self.generate_log_entries(result, request)
        self.add_success_message(result, request)
        # post_import.send(sender=None, model=self.model)

        return redirect(self.success_url)

    def handle_bulk_delete(self, request):
        ids = self.request.POST.getlist("selected_rows")
        if ids:
            SahayakIncentives.objects.filter(id__in=ids).delete()
            messages.success(request, "Selected incentives deleted successfully!")
        else:
            messages.warning(request, "No incentives were selected for deletion.")
        return redirect(self.success_url)

    def handle_export_csv(self, request):
        return self.export_to_csv()

    def save_form(self, form, action):
        if form.is_valid():
            form.save()
            messages.success(self.request, f"Sahayak incentive {action} successfully!")
        else:
            messages.error(self.request, f"Error {action} incentive.")
        return redirect(self.success_url)

    def export_to_csv(self):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="sahayak_incentives.csv"'
        )
        writer = csv.writer(response)
        writer.writerow(
            [
                "User",
                "MCC Code",
                "MCC Name",
                "MPP Code",
                "MPP Name",
                "Month",
                "Opening",
                "Milk Incentive",
                "Other Incentive",
                "Payable",
                "Closing",
            ]
        )

        for incentive in SahayakIncentives.objects.all():
            writer.writerow(
                [
                    incentive.user.username,
                    incentive.mcc_code,
                    incentive.mcc_name,
                    incentive.mpp_code,
                    incentive.mpp_name,
                    incentive.month,
                    incentive.opening,
                    incentive.milk_incentive,
                    incentive.other_incentive,
                    incentive.payable,
                    incentive.closing,
                ]
            )
        return response


class SahayakIncentivesCreateView(CreateView):
    model = SahayakIncentives
    form_class = SahayakIncentivesForm
    template_name = "member/form/creation_form.html"
    success_url = reverse_lazy("sahayak_incentives_list")

    def form_valid(self, form):
        messages.success(self.request, "Sahayak incentive created successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Error creating Sahayak incentive. Please correct the errors below.",
        )
        return super().form_invalid(form)


class SahayakIncentivesUpdateView(UpdateView):
    model = SahayakIncentives
    form_class = SahayakIncentivesForm
    template_name = "member/form/creation_form.html"
    success_url = reverse_lazy("sahayak_incentives_list")

    def get_object(self, queryset=None):
        # Get the object to be updated
        return get_object_or_404(SahayakIncentives, id=self.kwargs["pk"])

    def form_valid(self, form):
        # Custom processing before saving
        return super().form_valid(form)


class SahayakIncentivesViewSet(viewsets.ModelViewSet):
    queryset = SahayakIncentives.objects.all()
    serializer_class = SahayakIncentivesSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "user",
        "mcc_code",
        "mcc_name",
        "mpp_code",
        "mpp_name",
        "month",
        "year",
    ]
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SahayakIncentives.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(
                    {
                        "status": "success",
                        "message": "Incentives retrieved successfully",
                        "result": serializer.data,
                    }
                )
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "status": "success",
                    "message": "Incentives retrieved successfully",
                    "result": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": "Error retrieving incentives",
                    "result": {},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


from django.utils.translation import gettext as _


class MonthListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        months = [
            _("January"),
            _("February"),
            _("March"),
            _("April"),
            _("May"),
            _("June"),
            _("July"),
            _("August"),
            _("September"),
            _("October"),
            _("November"),
            _("December"),
        ]

        return Response(
            {
                "status": "success",
                "message": _("Months retrieved successfully"),
                "result": months,
            },
            status=status.HTTP_200_OK,
        )


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_saleable", "is_purchase"]
    serializer_class = ERProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        Fetch products based on the latest PriceBook and its PriceBookDetail efficiently.
        """
        latest_price_book = PriceBook.objects.order_by("-created_at").first()
        self.latest_price_book = latest_price_book  # Store it for reuse

        if latest_price_book:
            # Fetch PriceBookDetails efficiently & store for later use
            self.price_book_details = {
                detail.product_code.product_code: detail
                for detail in PriceBookDetail.objects.filter(
                    price_book_code=latest_price_book.price_book_code
                ).select_related("product_code")
            }

            # Get only the filtered products
            product_codes = self.price_book_details.keys()
            return Product.objects.filter(product_code__in=product_codes)

        self.price_book_details = {}  # Empty dictionary if no price book
        return Product.objects.none()

    def list(self, request, *args, **kwargs):
        """
        Custom response format with `status`, `message`, and `results`.
        Pass `price_book` and `price_book_details` to the serializer.
        """
        queryset = self.get_queryset()  # Calls optimized get_queryset()
        serializer = self.get_serializer(
            queryset,
            many=True,
            context={
                "latest_price_book": self.latest_price_book,
                "price_book_details": self.price_book_details,
            },
        )
        response_data = {
            "status": "success",
            "message": "Data fetched successfully",
            "results": serializer.data,
            "latest_price_book": self.latest_price_book.price_book_code,
        }
        return Response(response_data)


class LocalSaleViewSet(viewsets.ModelViewSet):
    queryset = LocalSaleTxn.objects.all()
    serializer_class = LocalSaleTxnSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_serializer_context(self):
        return {"request": self.request}

    def get_queryset(self):
        queryset = super().get_queryset()
        device = self.request.user.device
        mpp = Mpp.objects.filter(mpp_ex_code=device.mpp_code).last()
        return queryset.filter(local_sale_code__mpp_code=mpp.mpp_code)

    def list(self, request, *args, **kwargs):
        product_id = request.query_params.get("product_id", None)
        start_date = request.query_params.get("start_date", None)
        end_date = request.query_params.get("end_date", None)
        queryset = self.get_queryset()
        if product_id:
            queryset = queryset.filter(product_code__product_code=product_id)
        if not start_date == "null" and not end_date == "null":
            queryset = queryset.filter(
                local_sale_code__transaction_date__range=[start_date, end_date]
            )
        aggregated_data = queryset.aggregate(
            total_qty=Sum("qty"),
            total_amount=Sum("amount"),
            avg_rate=Avg("rate"),
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(
                {
                    "status": "success",
                    "message": "Data fetched successfully",
                    "aggregated_data": aggregated_data,
                    "results": serializer.data,
                }
            )

        # Serialize and return response
        serializer = self.get_serializer(queryset, many=True)
        response_data = {
            "status": "success",
            "message": "Data fetched successfully",
            "aggregated_data": aggregated_data,
            "results": serializer.data,
        }
        return Response(response_data)


class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"

    def get_paginated_response(self, data):
        return Response(
            {
                "status": "success",
                "status_code": 200,
                "message": "Data fetched successfully",
                "pagination": {
                    "count": self.page.paginator.count,
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                    "page_size": self.page_size,
                },
                "results": data,
            }
        )


class MemberHierarchyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A ViewSet for viewing MemberHierarchy data with additional last 15 days data.
    """

    queryset = MemberHierarchyView.objects.all()
    serializer_class = MemberHierarchyViewSerializer
    pagination_class = CustomPagination
    permission_classes = [AllowAny]
    filterset_class = MemberHeirarchyFilter
    filter_backends = [DjangoFilterBackend ]
    search_fields = ["member_name", "member_code", "member_tr_code"]
    ordering_fields = ["member_name"]

    def get_queryset(self):
        queryset = super().get_queryset()
        device = self.request.user.device
        mpp = Mpp.objects.filter(mpp_ex_code=device.mpp_code).last()
        mpp = Mpp.objects.filter(mpp_ex_code="1008").last()
        if not mpp:
            return MemberHierarchyView.objects.none()
        return queryset.filter(mpp_code=mpp.mpp_code).order_by("member_name")

    def list(self, request, *args, **kwargs):
        from datetime import timedelta, datetime

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            main_data = self.get_serializer(page, many=True).data
            paginated_response = self.get_paginated_response(main_data)
        else:
            main_data = self.get_serializer(queryset, many=True).data
            paginated_response = {"results": main_data}

        # Calculate the last 15 days
        # fixed_date = datetime(2024, 3, 28, 0, 0, 0)
        # last_15_days_date = fixed_date - timedelta(days=15)
        last_15_days_date = timezone.now() - timedelta(days=15)
        last_15_days_data = queryset.filter(created_at__gte=last_15_days_date)
        last_15_days_serializer = self.get_serializer(last_15_days_data, many=True)

        # Add last 15 days data to the response
        paginated_response.data["last_15_days"] = last_15_days_serializer.data
        return Response(paginated_response.data)


class SahayakFeedbackViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling SahayakFeedback operations with custom responses and pagination.
    """

    queryset = SahayakFeedback.objects.all()
    serializer_class = SahayakFeedbackSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        """
        Restrict to feedbacks created by the authenticated user.
        """
        if not self.request.user.is_superuser:
            return self.queryset.filter(sender=self.request.user)
        return self.queryset

    def perform_create(self, serializer):
        """
        Automatically set the authenticated user as the sender during feedback creation.
        """
        serializer.save(sender=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        Override the list response to include a custom format.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(
            page if page is not None else queryset, many=True
        )

        response_data = {
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "message": "Feedbacks retrieved successfully.",
            "results": serializer.data,
        }

        return (
            self.get_paginated_response(serializer.data)
            if page is not None
            else Response(response_data)
        )

    def create(self, request, *args, **kwargs):
        """
        Override the create response to include a custom format.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "message": "Feedback created successfully.",
                "results": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        """
        Override the update response to include a custom format.
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Feedback updated successfully.",
                "results": serializer.data,
            }
        )

    def destroy(self, request, *args, **kwargs):
        """
        Override the delete response to include a custom format.
        """
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_204_NO_CONTENT,
                "message": "Feedback deleted successfully.",
                "results": None,
            },
            status=status.HTTP_204_NO_CONTENT,
        )


class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["is_published"]
    ordering_fields = ["published_date", "updated_date"]
    pagination_class = CustomPagination

    def get_queryset(self):
        """
        Optionally filter queryset by date range.
        """
        queryset = super().get_queryset()
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        search = self.request.query_params.get("search")
        if start_date and end_date:
            try:
                queryset = queryset.filter(
                    published_date__date__range=[start_date, end_date]
                )
            except Exception as e:
                raise exceptions.ValidationError(
                    {"error": f"Invalid date range provided: {str(e)}"}
                )

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(summary__icontains=search)
                | Q(content__icontains=search)
            )

        return queryset

    def list(self, request, *args, **kwargs):
        """
        Customize the response for list API.
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(data=serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "status": "success",
                    "status_code": 200,
                    "results": len(serializer.data),
                    "message": "News articles retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except exceptions.ValidationError as e:
            return Response(
                {
                    "status": "error",
                    "status_code": 400,
                    "message": "Validation error.",
                    "errors": e.detail,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "status_code": 500,
                    "message": "An unexpected error occurred.",
                    "errors": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def retrieve(self, request, *args, **kwargs):
        """
        Customize the response for retrieve API.
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                {
                    "status": "success",
                    "status_code": 200,
                    "message": "News article retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "status_code": 404,
                    "message": "News article not found.",
                    "errors": str(e),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request, *args, **kwargs):
        """
        Customize the response for create API.
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "status": "success",
                    "status_code": 201,
                    "message": "News article created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except exceptions.ValidationError as e:
            return Response(
                {
                    "status": "error",
                    "status_code": 400,
                    "message": "Validation error.",
                    "errors": e.detail,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "status_code": 500,
                    "message": "An unexpected error occurred.",
                    "errors": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, *args, **kwargs):
        """
        Customize the response for update API.
        """
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(
                {
                    "status": "success",
                    "status_code": 200,
                    "message": "News article updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except exceptions.ValidationError as e:
            return Response(
                {
                    "status": "error",
                    "status_code": 400,
                    "message": "Validation error.",
                    "errors": e.detail,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "status_code": 500,
                    "message": "An unexpected error occurred.",
                    "errors": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request, *args, **kwargs):
        """
        Customize the response for delete API.
        """
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {
                    "status": "success",
                    "status_code": 204,
                    "message": "News article deleted successfully.",
                },
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "status_code": 500,
                    "message": "An unexpected error occurred.",
                    "errors": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class NewsNotReadCountAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        not_read_count = News.objects.filter(is_read=False).count()
        return Response({"not_read_count": not_read_count})


from erp_app.models import BillingMemberMaster


class BillingMemberMasterRowFilter(FilterSet):
    from_date = DateTimeFromToRangeFilter()
    to_date = DateTimeFromToRangeFilter()

    class Meta:
        model = BillingMemberMaster
        fields = ["from_date", "to_date", "mpp_code"]


class MemberMasterViewSet(viewsets.ModelViewSet):
    queryset = MemberMaster.objects.all()
    serializer_class = MemberMasterSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["member_code", "member_name", "is_active"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Member Masters retrieved successfully",
                "results": serializer.data,
            }
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Member Master retrieved successfully",
                "results": serializer.data,
            }
        )


class BankViewSet(viewsets.ModelViewSet):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["bank_name", "is_active", "nationalized_bank"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Banks retrieved successfully",
                "results": serializer.data,
            }
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Bank retrieved successfully",
                "results": serializer.data,
            }
        )


class BillingMemberMasterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BillingMemberMaster.objects.all()
    serializer_class = BillingMemberMasterSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = BillingMemberMasterRowFilter
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Billing Member Master Rows retrieved successfully",
                "results": serializer.data,
            }
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Billing Member Master Row retrieved successfully",
                "results": serializer.data,
            }
        )


class BillingMemberDetailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BillingMemberDetail.objects.all()
    serializer_class = BillingMemberDetailSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["member_code", "billing_member_master_code"]
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return BillingMemberDetail.objects.all()
        billing_master_code = self.request.GET.get("billing_member_master_code")
        return BillingMemberDetail.objects.filter(
            billing_member_master_code=billing_master_code
        )

    def get_serializer_context(self):
        return {"request": self.request}

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            queryset, many=True, context={"request": request}
        )
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Billing Member Details retrieved successfully",
                "results": serializer.data,
            }
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Billing Member Detail retrieved successfully",
                "results": serializer.data,
            }
        )


class MppViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Mpp.objects.all()
    serializer_class = MppSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["mpp_ex_code"]
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Mpp list retrieved successfully",
                "results": serializer.data,
            }
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Mpp retrieved successfully",
                "results": serializer.data,
            }
        )


class LocalSaleTxnFilter(FilterSet):
    installment_start_date = DateFromToRangeFilter(
        field_name="local_sale_code__installment_start_date"
    )

    class Meta:
        model = LocalSaleTxn
        fields = ["installment_start_date", "local_sale_code__module_code"]


class LocalSaleTxnViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LocalSaleTxn.objects.all()
    serializer_class = DeductionTxnSerializer
    filter_backends = [DjangoFilterBackend]
    pagination_class = StandardResultsSetPagination
    filterset_class = LocalSaleTxnFilter
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Local sale transactions retrieved successfully",
                "results": serializer.data,
            }
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Local sale transaction retrieved successfully",
                "results": serializer.data,
            }
        )


from django.db.models import Sum, F, FloatField, DecimalField
from django.db.models.functions import Coalesce, Cast

from django.utils.translation import gettext as _
from django.core.cache import cache


class SahayakDashboardAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        created_date = request.GET.get("date", timezone.now().date())
        mpp_code = request.GET.get("mpp_code")
        shift_code = request.GET.get("shift_code")

        if not mpp_code:
            return Response(
                {"status": "error", "message": "Please provide the MPP code"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Caching: Store and retrieve results from cache
        cache_key = f"sahayak_dashboard_{mpp_code}_{shift_code}_{created_date}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        # Use `.values_list()` to fetch only required field
        mpp_ref_code = (
            MppCollectionReferences.objects.filter(
                collection_date__date=created_date,
                mpp_code=mpp_code,
                shift_code=shift_code,
            )
            .values_list("mpp_collection_references_code", flat=True)
            .first()
        )

        if not mpp_ref_code:
            return Response(
                {"status": "error", "message": "No MPP reference found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Optimize aggregations
        mpp_collection_agg = self.get_aggregates(
            MppCollection, "qty", "fat", "snf", references=mpp_ref_code
        )
        actual_agg_data = self.get_aggregates(
            RmrdMilkCollection,
            "qty",
            "fat",
            "snf",
            collection_date__date=created_date,
            module_code=mpp_code,
            shift_code__shift_code=shift_code,
        )
        dispatches = self.get_aggregates(
            MppDispatchTxn,
            "dispatch_qty",
            "fat",
            "snf",
            mpp_dispatch_code__mpp_code=mpp_code,
            mpp_dispatch_code__from_date__date=created_date,
            mpp_dispatch_code__from_shift=shift_code,
        )

        # Construct response data
        response_data = {
            "status": 200,
            "message": _("Data Retrieved"),
            "data": {
                "composite": self.format_aggregates(mpp_collection_agg),
                "actual": self.format_aggregates(actual_agg_data),
                "dispatch": self.format_aggregates(dispatches),
            },
        }

        # Store in cache for 5 minutes
        cache.set(cache_key, response_data, timeout=300)
        return Response(response_data, status=status.HTTP_200_OK)

    def get_aggregates(self, model, qty_field, fat_field, snf_field, **filters):
        """
        Optimized function to compute aggregations efficiently.
        """
        aggregation = model.objects.filter(**filters).aggregate(
            qty=Sum(qty_field),
            fat=Coalesce(
                Cast(
                    Sum(F(qty_field) * F(fat_field), output_field=FloatField()),
                    FloatField(),
                )
                / Cast(Sum(qty_field), FloatField()),
                0.0,
            ),
            snf=Coalesce(
                Cast(
                    Sum(F(qty_field) * F(snf_field), output_field=FloatField()),
                    FloatField(),
                )
                / Cast(Sum(qty_field), FloatField()),
                0.0,
            ),
        )
        return aggregation

    def format_aggregates(self, aggregates):
        """
        Rounds float values for better readability.
        """
        return {
            key: round(value, 2) if value is not None else 0.0
            for key, value in aggregates.items()
        }


class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = get_object_or_404(self.queryset, pk=kwargs["pk"])
        serializer = self.get_serializer(instance)
        return JsonResponse(serializer.data)
