from rest_framework import status, viewsets, exceptions
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from ..models.facilitator_model import AssignedMppToFacilitator
from ..serializers.serializers import *
from erp_app.models import (
    MppCollection,
    RmrdMilkCollection,
    MppDispatchTxn,
    MppCollectionReferences,
    MemberMasterHistory,
)
from django.db.models import Sum, F, FloatField, Avg
from django.db.models.functions import Coalesce, Cast
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from ..authentication import ApiKeyAuthentication
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
import random
from django.core.cache import cache
from django.db.models import Sum, OuterRef, Subquery, FloatField
from django.utils.dateparse import parse_date
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


CACHE_TIMEOUT = 3600  # 10 minutes


class AssignedMppToFacilitatorViewSet(viewsets.ModelViewSet):
    queryset = AssignedMppToFacilitator.objects.all()
    serializer_class = AssignedMppToFacilitatorSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]
    lookup_field = "mpp_code"

    def get_queryset(self):
        """
        Optionally restricts the returned queryset to the currently authenticated user,
        if the user is not a superuser or staff.
        """
        user = self.request.user
        # if user.is_superuser or user.is_staff:
        #     return AssignedMppToFacilitator.objects.all()
        return AssignedMppToFacilitator.objects.filter(sahayak=user)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "message": "Assigned MPP created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            return Response(
                {"message": "Validation error occurred.", "errors": e.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"message": "An unexpected error occurred.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, *args, **kwargs):
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
                    "message": "Assigned MPP updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response(
                {"message": "Validation error occurred.", "errors": e.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"message": "An unexpected error occurred.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {"message": "Assigned MPP deleted successfully."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": "An unexpected error occurred.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


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
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "status": "success",
                    "message": "Incentive created successfully",
                    "result": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except exceptions.ValidationError as e:
            return Response(
                {"status": "error", "message": str(e), "result": {}},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
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
                    "message": "Incentive updated successfully",
                    "result": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except exceptions.ValidationError as e:
            return Response(
                {"status": "error", "message": str(e), "result": {}},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {
                    "status": "success",
                    "message": "Incentive deleted successfully",
                    "result": {},
                },
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": "Error deleting incentive",
                    "result": {},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                {
                    "status": "success",
                    "message": "Incentive retrieved successfully",
                    "result": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": "Error retrieving incentive",
                    "result": {},
                },
                status=status.HTTP_404_NOT_FOUND,
            )

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

class DashboardSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        created_date = self.request.GET.get("date", timezone.now().date())
        mpp_codes = self.request.GET.get("mpp_code")
        if not mpp_codes:
            mpp_codes = list(
                AssignedMppToFacilitator.objects.filter(
                    sahayak=self.request.user
                ).values_list("mpp_code", flat=True)
            )
        else:
            mpp_codes = mpp_codes.split(",")
        # Subquery for actual amount
        actual_subquery = (
            RmrdMilkCollection.objects.filter(
                collection_date__date=created_date, module_code=OuterRef("mpp_code")
            )
            .values("module_code")
            .annotate(amount=Sum("amount"))
            .values("amount")
        )
        # Subquery for composite amount
        composite_subquery = (
            MppCollection.objects.filter(
                references__collection_date__date=created_date,
                references__mpp_code=OuterRef("mpp_code"),
            )
            .select_related("references")
            .values("references__mpp_code")
            .annotate(amount=Sum("amount"))
            .values("amount")
        )
        # Annotate actual and composite amounts
        return Mpp.objects.filter(mpp_code__in=mpp_codes).annotate(
            actual_amount=Subquery(actual_subquery, output_field=FloatField()),
            composite_amount=Subquery(composite_subquery, output_field=FloatField()),
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        response_data = [
            {
                "mpp_code": mpp.mpp_code,
                "date": self.request.GET.get("date", timezone.now().date()),
                "variation": (
                    round(
                        float(mpp.actual_amount) - float(mpp.composite_amount or 0), 2
                    )
                    if mpp.actual_amount and float(mpp.actual_amount) > 0
                    else round(float(mpp.composite_amount or 0), 2)
                ),
            }
            for mpp in queryset
        ]
        # Sorting by variation
        response_data.sort(key=lambda x: x["variation"])
        # Paginate response
        paginator = self.pagination_class()
        paginated_data = paginator.paginate_queryset(response_data, request)
        return paginator.get_paginated_response(paginated_data)


class DashboardDetailAPI(APIView):
    authentication_classes = [JWTAuthentication]
    # authentication_classes = [ApiKeyAuthentication]
    # permission_classes = [AllowAny]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        created_date = request.GET.get("date", timezone.now().date())
        mpp_code = request.GET.get("mpp_code")
        shift_code = request.GET.get("shift_code")

        if not mpp_code:
            return Response(
                {"message": "mpp_code required", "status": "error"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        actual, dispatch, composite = self.get_bulk_data(
            created_date, mpp_code, shift_code
        )

        response_data = {
            "mpp_code": mpp_code,
            "date": created_date,
            "shift_code": shift_code,
            "data": {
                "actual": actual,
                "dispatch": dispatch,
                "composite": composite,
            },
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def get_bulk_data(self, created_date, mpp_code, shift_codes):
        collections = RmrdMilkCollection.objects.filter(
            collection_date__date=created_date,
            module_code=mpp_code,
            shift_code=shift_codes,
        ).aggregate(
            qty=Sum("qty"),
            amount=Sum("amount"),
            fat=Coalesce(
                Cast(Sum(F("qty") * F("fat"), output_field=FloatField()), FloatField())
                / Cast(Sum("qty"), FloatField()),
                0.0,
            ),
            snf=Coalesce(
                Cast(Sum(F("qty") * F("snf"), output_field=FloatField()), FloatField())
                / Cast(Sum("qty"), FloatField()),
                0.0,
            ),
        )

        dispatches = MppDispatchTxn.objects.filter(
            mpp_dispatch_code__mpp_code=mpp_code,
            mpp_dispatch_code__from_date__date=created_date,
            mpp_dispatch_code__from_shift=shift_codes,
        ).aggregate(
            qty=Sum("dispatch_qty"),
            amount=Sum("amount"),
            fat=Coalesce(
                Cast(
                    Sum(F("dispatch_qty") * F("fat"), output_field=FloatField()),
                    FloatField(),
                )
                / Cast(Sum("dispatch_qty"), FloatField()),
                0.0,
            ),
            snf=Coalesce(
                Cast(
                    Sum(F("dispatch_qty") * F("snf"), output_field=FloatField()),
                    FloatField(),
                )
                / Cast(Sum("dispatch_qty"), FloatField()),
                0.0,
            ),
        )

        aggregated_data = MppCollection.objects.filter(
            references__collection_date__date=created_date,
            references__mpp_code=mpp_code,
            shift_code=shift_codes,
        ).aggregate(
            qty=Sum("qty"),
            amount=Sum("amount"),
            fat=Coalesce(
                Cast(Sum(F("qty") * F("fat"), output_field=FloatField()), FloatField())
                / Cast(Sum("qty"), FloatField()),
                0.0,
            ),
            snf=Coalesce(
                Cast(Sum(F("qty") * F("snf"), output_field=FloatField()), FloatField())
                / Cast(Sum("qty"), FloatField()),
                0.0,
            ),
        )
        return collections, dispatches, aggregated_data

    def format_aggregates(self, aggregates):
        return {
            key: round(value, 2) if value is not None else None
            for key, value in aggregates.items()
        }

    def get_shifts(self):
        shifts = Shift.objects.filter(shift_short_name__in=["M", "E"]).values_list(
            "shift_short_name", "shift_code"
        )
        shift_dict = dict(shifts)
        return shift_dict.get("M"), shift_dict.get("E")


class LocalSaleViewSet(viewsets.ModelViewSet):
    queryset = LocalSaleTxn.objects.all()
    authentication_classes = [JWTAuthentication]
    serializer_class = [LocalSaleTxnSerializer]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_serializer_context(self):
        return {"request": self.request}

    def get_queryset(self):
        queryset = super().get_queryset()
        start_date = self.request.query_params.get("start_date", None)
        mpp_codes = self.request.GET.get("mpp_code", None)
        end_date = self.request.query_params.get("end_date", None)
        if not mpp_codes:
            mpp_codes = list(
                AssignedMppToFacilitator.objects.filter(
                    sahayak=self.request.user
                ).values_list("mpp_code", flat=True)
            )
        else:
            mpp_codes = mpp_codes.split(",")
        if mpp_codes:
            queryset = queryset.filter(local_sale_code__mpp_code__in=mpp_codes)

        if start_date and end_date:
            start_date = parse_date(start_date)
            end_date = parse_date(end_date)

            if start_date and end_date:
                queryset = queryset.filter(
                    local_sale_code__transaction_date__range=[start_date, end_date]
                )
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)
        product_summary = []
        products = queryset.values(
            "product_code", "product_code__product_name"
        ).distinct()

        for product in products:
            product_id = product["product_code"]
            product_name = product["product_code__product_name"]
            product_data = queryset.filter(product_code=product_id)
            
            mpp_data = (
                product_data.values("local_sale_code__mpp_code", "local_sale_code")
                .annotate(
                    total_qty=Sum("qty"),
                    total_amount=Sum("amount"),
                    avg_rate=Avg("rate"),
                )
                .order_by("local_sale_code__mpp_code")
            )

            # Group by mpp_code and aggregate
            mpp_groups = {}
            for item in mpp_data:
                mpp_code = item["local_sale_code__mpp_code"]
                if mpp_code not in mpp_groups:
                    mpp_groups[mpp_code] = {
                        "local_sale_code__mpp_code": mpp_code,
                        "local_sale_codes": [],
                        "total_qty": 0,
                        "total_amount": 0,
                        "rate_values": [],
                    }

                mpp_groups[mpp_code]["local_sale_codes"].append(
                    str(item["local_sale_code"])
                )
                mpp_groups[mpp_code]["total_qty"] += item["total_qty"]
                mpp_groups[mpp_code]["total_amount"] += item["total_amount"]
                mpp_groups[mpp_code]["rate_values"].append(item["avg_rate"])

            mpp_summary = []
            for mpp_code, data in mpp_groups.items():
                total_amount = data["total_amount"]
                total_qty = data["total_qty"]
                avg_rate = total_amount / total_qty if total_qty != 0 else 0
                mpp_summary.append(
                    {
                        "local_sale_code__mpp_code": mpp_code,
                        "local_sale_code": ",".join(data["local_sale_codes"]),
                        "total_qty": total_qty,
                        "total_amount": total_amount,
                        "avg_rate": avg_rate,
                    }
                )

            product_summary.append(
                {
                    "product_id": product_id,
                    "product_name": product_name,
                    "from_date": start_date,
                    "to_date": end_date,
                    "total_qty": product_data.aggregate(Sum("qty"))["qty__sum"] or 0,
                    "total_amount": product_data.aggregate(Sum("amount"))["amount__sum"]
                    or 0,
                    "avg_rate": product_data.aggregate(Avg("rate"))["rate__avg"] or 0,
                    "mpp_summary": mpp_summary,
                }
            )

        return Response(
            {
                "status": "success",
                "message": "Data fetched successfully",
                "product_summary": product_summary,
            }
        )




class SaleToMembersViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LocalSaleTxn.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = LocalSaleTxnSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        local_sale_codes = self.request.GET.get("local_sale_code")
        local_sale_code_list = local_sale_codes.split(",")
        queryset = queryset.filter(local_sale_code__status__in=["Approved"],local_sale_code__local_sale_code__in = local_sale_code_list).distinct()
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Local sale transactions retrieved successfully",
                "data": serializer.data,
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
                "data": serializer.data,
            }
        )



class ShiftViewSet(viewsets.ModelViewSet):
    authentication_classes = [ApiKeyAuthentication, JWTAuthentication]
    permission_classes = [AllowAny]
    queryset = Shift.objects.all().order_by("shift_name")
    serializer_class = ShiftSerializer


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data

        old_password = data.get("old_password")
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")

        if not old_password or not new_password or not confirm_password:
            return Response(
                {"message": _("All fields are required.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_password != confirm_password:
            return Response(
                {"message": _("Passwords do not match.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.check_password(old_password):
            return Response(
                {"message": _("Old password is incorrect.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(new_password, user)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        # Update last login if required
        update_last_login(None, user)

        return Response(
            {"message": _("Password changed successfully.")}, status=status.HTTP_200_OK
        )



class RequestOTPPasswordResetView(APIView):
    def post(self, request):
        username = request.data.get("username")
        if not username:
            return Response(
                {"message": _("Username is required")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"message": _("User not found")}, status=status.HTTP_404_NOT_FOUND
            )
        otp = str(random.randint(100000, 999999))  # Generate 6-digit OTP
        cache.set(f"otp_{username}", otp, timeout=300)  # Store OTP for 5 minutes
        return Response(
            {"message": _("OTP sent successfully.")}, status=status.HTTP_200_OK
        )


class VerifyOTPResetPasswordView(APIView):
    def post(self, request):
        username = request.data.get("username")
        otp = request.data.get("otp")
        new_password = request.data.get("new_password")
        if not username or not otp or not new_password:
            return Response(
                {"message": _("All fields are required")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cached_otp = cache.get(f"otp_{username}")
        if cached_otp is None or cached_otp != otp:
            return Response(
                {"message": _("Invalid or expired OTP")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"message": _("User not found")}, status=status.HTTP_404_NOT_FOUND
            )
        user.set_password(new_password)
        user.save()
        cache.delete(f"otp_{username}")
        return Response(
            {"message": _("Password reset successfully.")}, status=status.HTTP_200_OK
        )

class GetPouredMembersData(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get collection date from query params, default to today
        collection_date_str = request.GET.get("collection_date")
        collection_date = (
            now().date() if collection_date_str is None else collection_date_str
        )

        # Cache key specific to user and date
        cache_key = f"poured_members_{user.id}_{collection_date}"
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response, status=status.HTTP_200_OK)

        # Get mpp codes assigned to user
        mpp_codes = list(self.get_mpps(user))

        # Fetch only active members under those mpps
        all_active_members = MemberHierarchyView.objects.filter(
            mpp_code__in=mpp_codes,
            is_active=True,
            is_default=True
        ).only("member_code")

        # Get their member codes
        member_codes = all_active_members.values_list("member_code", flat=True)

        # Count of poured members (who have collection on given date)
        poured_members = (
            MppCollection.objects.filter(
                references__collection_date__date=collection_date,
                member_code__in=member_codes,
            )
            .values("member_code")
            .distinct()
            .count()
        )

        # Total count of active members
        total_active_member = all_active_members.count()

        # Response payload
        data = {
            "key": "poured_member",
            "title": "Poured Members",
            "data": [
                {
                    "title": "Poured",
                    "value": poured_members,
                    "color": "#7cddf7",
                    "text_color": "#29859e",
                },
                {
                    "title": "Active",
                    "value": total_active_member,
                    "color": "#29859e",
                    "text_color": "#7cddf7",
                },
            ],
        }

        response_data = {
            "message": "success",
            "status": "success",
            "data": data,
        }

        # Set cache
        cache.set(cache_key, response_data, timeout=CACHE_TIMEOUT)

        return Response(response_data, status=status.HTTP_200_OK)

    def get_mpps(self, user):
        if user.is_authenticated:
            return user.mpps.all().values_list("mpp_code", flat=True)
        return []

class GetPouredMppView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"message": "unauthenticated", "status": "fail"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Get collection_date
        collection_date_str = request.GET.get("collection_date")
        collection_date = (
            timezone.now().date() if not collection_date_str else collection_date_str
        )

        # Build a unique cache key
        cache_key = f"poured_mpp_{user.id}_{collection_date}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(
                {"message": "success", "status": "success", "data": cached_data},
                status=status.HTTP_200_OK,
            )

        # Query and aggregate
        mpp_codes = list(user.mpps.values_list("mpp_code", flat=True))
        aggregated_data = (
            MppCollection.objects
            .filter(
                references__mpp_code__in=mpp_codes,
                references__collection_date__date=collection_date,
            )
            .values("references__mpp_code").order_by("references__mpp_code__mpp_name")
            .annotate(total_qty=Sum("qty"))
        )

        final_result = [
            {
                "mpp_code": item["references__mpp_code"],
                "total_qty": item["total_qty"] or 0
            }
            for item in aggregated_data
        ]

        # Store in cache
        cache.set(cache_key, final_result, timeout=CACHE_TIMEOUT)

        return Response(
            {"message": "success", "status": "success", "data": final_result},
            status=status.HTTP_200_OK,
        )


class GetPouredMembersForMppView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        mpp_code = request.GET.get("mpp_code")
        if not mpp_code:
            return Response(
                {"message": "mpp_code query param is required", "status": "error"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        collection_date_str = request.GET.get("collection_date")
        collection_date = (
            timezone.now().date()
            if collection_date_str is None
            else collection_date_str
        )

        # Get all members under the given MPP
        all_members = MemberHierarchyView.objects.filter(mpp_code=mpp_code)

        # Get poured member codes for the given date
        poured_member_codes = set(
            MppCollection.objects.filter(
                references__collection_date__date=collection_date,
                member_code__in=all_members.values_list("member_code", flat=True),
            )
            .values_list("member_code", flat=True)
            .distinct()
        )

        # Filter poured members
        poured_members = all_members.filter(member_code__in=poured_member_codes)

        # Get qty per poured member
        qty_per_member = dict(
            MppCollection.objects.filter(
                references__collection_date__date=collection_date,
                member_code__in=poured_member_codes,
            )
            .values("member_code")
            .annotate(total_qty=Sum("qty"))
            .values_list("member_code", "total_qty")
        )

        # Calculate total qty
        total_qty = sum(qty_per_member.values())

        # Get MPP info
        try:
            mpp = Mpp.objects.get(mpp_code=mpp_code)
            mpp_data = {
                "mpp_code": mpp.mpp_code,
                "mpp_ex_code": mpp.mpp_ex_code,
                "mpp_name": mpp.mpp_name or mpp.mpp_short_name,
            }
        except Mpp.DoesNotExist:
            mpp_data = {"mpp_code": mpp_code}

        members_data = [
            {
                "member_code": member.member_code,
                "member_tr_code": member.member_tr_code,
                "member_name": member.member_name,
                "mobile_no": member.mobile_no,
                "is_active": member.is_active,
                "is_default": member.is_default,
                "qty": qty_per_member.get(member.member_code, 0),
            }
            for member in poured_members
        ]

        return Response(
            data={
                "message": "success",
                "status": "success",
                "data": {
                    "mpp": mpp_data,
                    "poured_members": members_data,
                    "total_qty": total_qty,
                    "collection_date": collection_date,
                },
            },
            status=status.HTTP_200_OK,
        )


class GetTotalMembersData(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Define a unique cache key for this user
        cache_key = f"total_members_data_{user.id}"

        # Check if the data is already cached
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(
                data={
                    "message": "success (cached)",
                    "status": "success",
                    "data": cached_data,
                },
                status=status.HTTP_200_OK,
            )

        # Fetch data if not cached
        mpp_codes = list(self.get_mpps(user))
        all_members = MemberHierarchyView.objects.filter(mpp_code__in=mpp_codes,is_default=True)
        active_member = all_members.filter(is_active=True).count()
        total_members = all_members.count()

        # Prepare the response data
        data = {
            "key": "total_members",
            "title": "Total Members",
            "data": [
                {
                    "title": "Active",
                    "value": active_member,
                    "color": "#baf4ee",
                    "text_color": "#00beac",
                },
                {
                    "title": "Total",
                    "value": total_members,
                    "color": "#00beac",
                    "text_color": "#baf4ee",
                },
            ],
        }

        # Cache the data for 1 hour (3600 seconds)
        cache.set(cache_key, data, timeout=CACHE_TIMEOUT)

        return Response(
            data={"message": "success", "status": "success", "data": data},
            status=status.HTTP_200_OK,
        )

    def get_mpps(self, user):
        if user.is_authenticated:
            return user.mpps.all().values_list("mpp_code", flat=True)

class GetTotalCancelledMembers(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        cache_key = f"cancelled_members_{user.id}"

        # Check cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(data=cached_data, status=status.HTTP_200_OK)

        # Get MPPs
        mpp_codes = list(self.get_mpps(user))
        all_members = MemberHierarchyView.objects.filter(
            mpp_code__in=mpp_codes, is_active=False
        ).values("member_code", "mpp_code")

        members_code = [m["member_code"] for m in all_members]
        member_to_mpp_map = {
            m["member_code"]: m["mpp_code"] for m in all_members
        }

        cancelled_members = MemberMasterHistory.objects.filter(
            member_code__in=members_code,is_active=False
        ).values(
            "history_created_at",
            "operation_type",
            "member_code",
            "member_name",
            "member_ex_code",
            "is_active",
            "mobile_no",
        )

        final_result = []
        for member in cancelled_members:
            member["mpp_code"] = member_to_mpp_map.get(member["member_code"])
            final_result.append(member)

        # ✅ Return dict, not tuple
        response_data = {
            "message": "success",
            "status": "success",
            "data": final_result,
        }

        # Cache the final dict
        cache.set(cache_key, response_data, timeout=CACHE_TIMEOUT)

        return Response(data=response_data, status=status.HTTP_200_OK)

    def get_mpps(self, user):
        if user.is_authenticated:
            return user.mpps.all().values_list("mpp_code", flat=True)
        return []
class GetHighPourerData(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        collection_date_str = request.GET.get("collection_date")
        collection_date = (
            timezone.now().date() if collection_date_str is None else collection_date_str
        )

        # Optional: Enable caching if needed
        cache_key = f"high_pourer_counts_{user.id}_{collection_date}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        # Get assigned MPP codes
        mpp_codes = list(self.get_mpps(user))
        if not mpp_codes:
            return Response(
                {"message": "No MPPs assigned", "status": "error"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get active/default members under user's MPPs
        member_codes = MemberHierarchyView.objects.filter(
            mpp_code__in=mpp_codes,
            is_active=True,
            is_default=True
        ).only("member_code").values_list("member_code", flat=True)

        # Aggregate total quantity per member for the given date
        aggregated = (
            MppCollection.objects.filter(
                references__collection_date__date=collection_date,
                member_code__in=member_codes,
            )
            .values("member_code")
            .annotate(total_qty=Sum("qty"))
        )

        # Count high and low pourers
        high_pourers_count = aggregated.filter(total_qty__gt=49).count()
        low_pourers_count = aggregated.filter(total_qty__lte=49).count()

        # Prepare the response data
        data = {
            "key": "high_pourers",
            "title": "High Pourers",
            "data": [
                {
                    "title": "> 49 L",
                    "value": high_pourers_count,
                    "color": "#27ae60",
                    "text_color": "#0b2d36",
                },
                {
                    "title": "<= 49 L",
                    "value": low_pourers_count,
                    "color": "#f39c12",
                    "text_color": "#ffffff",
                },
            ],
        }

        response_data = {
            "message": "success",
            "status": "success",
            "data": data,
        }

        # Optional: Cache result
        cache.set(cache_key, response_data, timeout=CACHE_TIMEOUT)

        return Response(response_data, status=status.HTTP_200_OK)

    def get_mpps(self, user):
        if user.is_authenticated:
            return user.mpps.only("mpp_code").values_list("mpp_code", flat=True)
        return []

class GetHighPourerMembers(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        collection_date_str = request.GET.get("collection_date")
        collection_date = (
            timezone.now().date()
            if collection_date_str is None
            else collection_date_str
        )

        # Use caching
        cache_key = f"high_pourers_{user.id}_{collection_date}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        # Step 1: Get assigned MPP codes
        mpp_codes = list(self.get_mpps(user))
        if not mpp_codes:
            return Response(
                {"message": "No MPPs assigned", "status": "error"},
                status=status.HTTP_404_NOT_FOUND,
            )

        all_members = MemberHierarchyView.objects.filter(
            mpp_code__in=mpp_codes, is_active=True, is_default=True
        ).values("member_code", "member_tr_code", "member_name", "mobile_no")

        member_codes = all_members.values_list("member_code", flat=True)
        aggregated = (
            MppCollection.objects.filter(
                references__collection_date__date=collection_date,
                member_code__in=member_codes,
            )
            .values("member_code", "references__mpp_code__mpp_code")
            .annotate(total_qty=Sum("qty"))
        )

        mpp_codes_in_result = [m["references__mpp_code__mpp_code"] for m in aggregated]
        mpp_queryset = Mpp.objects.only(
            "mpp_code", "mpp_ex_code", "mpp_name", "mpp_short_name"
        ).filter(mpp_code__in=mpp_codes_in_result)
        mpp_map = {
            mpp.mpp_code: {
                "mpp_code": mpp.mpp_code,
                "mpp_ex_code": mpp.mpp_ex_code,
                "mpp_name": mpp.mpp_name or mpp.mpp_short_name,
            }
            for mpp in mpp_queryset
        }
        high_pourers = aggregated.filter(total_qty__gt=49)
        from collections import defaultdict

        mpp_data = defaultdict(lambda: {"details": {}, "members": []})
        for entry in high_pourers:
            mpp_code = entry["references__mpp_code__mpp_code"]
            member_obj = all_members.filter(member_code=entry["member_code"]).last()
            if member_obj:
                member = {
                    "member": {
                        "member_code": member_obj["member_code"],
                        "member_tr_code": member_obj["member_tr_code"],
                        "member_name": member_obj["member_name"],
                        "mobile_no": member_obj["mobile_no"],
                        "qty": entry["total_qty"],
                    }
                }
                if not mpp_data[mpp_code]["details"]:
                    mpp_data[mpp_code]["details"] = mpp_map.get(mpp_code, {})
                mpp_data[mpp_code]["members"].append(member)
        mpp_data = [
            {**mpp["details"], "members": mpp["members"]}
            for mpp_code, mpp in mpp_data.items()
        ]
        response = {
            "status": "success",
            "message": "Highest pourer fetched successfully",
            "data": mpp_data,
        }
        cache.set(cache_key, response, timeout=CACHE_TIMEOUT)
        return Response(response, status=status.HTTP_200_OK)

    def get_mpps(self, user):
        if user.is_authenticated:
            return user.mpps.only("mpp_code").values_list("mpp_code", flat=True)
        return []


class GetDailyMppCollections(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        collection_date = request.GET.get("collection_date", str(timezone.now().date()))

        # Use cache key based on user and date
        cache_key = f"daily_mpp_collections_{user.id}_{collection_date}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(
                data={"message": "success", "status": "success", "data": cached_data},
                status=status.HTTP_200_OK,
            )

        # Step 1: Get MPPs for this user
        mpp_codes = list(self.get_mpps(user))
        if not mpp_codes:
            return Response(
                data={
                    "message": "No MPPs assigned to user",
                    "status": "error",
                    "data": {},
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Step 2: Aggregate collection quantities
        mpp_collection = (
            MppCollection.objects.filter(
                references__mpp_code__in=mpp_codes,
                references__collection_date__date=collection_date,
            )
            .values("references__mpp_code")
            .annotate(total_qty=Sum("qty"))
        )

        mpp_codes_in_result = [m["references__mpp_code"] for m in mpp_collection]

        # Step 3: Efficient MPP mapping only for required mpps
        mpp_queryset = Mpp.objects.only(
            "mpp_code", "mpp_ex_code", "mpp_name", "mpp_short_name"
        ).filter(mpp_code__in=mpp_codes_in_result)
        mpp_map = {
            mpp.mpp_code: {
                "mpp_code": mpp.mpp_code,
                "mpp_ex_code": mpp.mpp_ex_code,
                "mpp_name": mpp.mpp_name or mpp.mpp_short_name,
            }
            for mpp in mpp_queryset
        }

        # Step 4: Combine data
        formatted_data = {
            "key": "daily_collections",
            "title": "MPP Collection Daily Stats",
            "data": [
                {
                    "mpp": mpp_map.get(item["references__mpp_code"], {}),
                    "qty": float(item["total_qty"]),
                }
                for item in mpp_collection
            ],
        }

        # Step 5: Cache the result
        cache.set(cache_key, formatted_data, CACHE_TIMEOUT)

        return Response(
            data={"message": "success", "status": "success", "data": formatted_data},
            status=status.HTTP_200_OK,
        )

    def get_mpps(self, user):
        if user.is_authenticated:
            return user.mpps.only("mpp_code").values_list("mpp_code", flat=True)
        return []


class GetTotalQtyForToday(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        collection_date = request.GET.get("collection_date", str(timezone.now().date()))

        # Create a unique cache key based on user and date
        cache_key = f"total_qty_{user.id}_{collection_date}"
        cached_total = cache.get(cache_key)
        if cached_total is not None:
            return Response(
                {
                    "message": "success (cached)",
                    "status": "success",
                    "total_qty": float(cached_total),
                },
                status=status.HTTP_200_OK,
            )

        # Get relevant MPP codes
        mpp_codes = list(self.get_mpps(user))
        if not mpp_codes:
            return Response(
                {"message": "No MPPs assigned", "status": "error", "total_qty": 0.0},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Query for total qty
        total_qty = (
            MppCollection.objects.filter(
                references__mpp_code__in=mpp_codes,
                references__collection_date__date=collection_date,
            ).aggregate(total_qty=Sum("qty"))["total_qty"]
            or 0
        )

        # Cache the result
        cache.set(cache_key, total_qty, timeout=CACHE_TIMEOUT)  # 10 minutes cache

        return Response(
            {
                "message": "success",
                "status": "success",
                "total_qty": float(total_qty),
            },
            status=status.HTTP_200_OK,
        )

    def get_mpps(self, user):
        if user.is_authenticated:
            return user.mpps.only("mpp_code").values_list("mpp_code", flat=True)
        return []
