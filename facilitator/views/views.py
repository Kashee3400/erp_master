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
)
from django.db.models import Sum, F, FloatField,Avg
from django.db.models.functions import Coalesce, Cast
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from ..authentication import ApiKeyAuthentication


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


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


from django.db.models import Sum, OuterRef, Subquery, FloatField

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
            ).select_related("references")
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

from django.utils.dateparse import parse_date

class LocalSaleViewSet(viewsets.ModelViewSet):
    queryset = LocalSaleTxn.objects.all()
    authentication_classes = [JWTAuthentication]
    serializer_class = [LocalSaleTxnSerializer]
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_serializer_context(self):
        return {"request": self.request}

    def get_queryset(self):
        queryset = super().get_queryset()
        start_date = self.request.query_params.get("start_date", None)
        mpp_codes = self.request.GET.get("mpp_code",None)
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
        # 🟢 Product-wise Summary (Group by product_code)
        product_summary = []
        products = queryset.values("product_code", "product_code__product_name").distinct()

        for product in products:
            product_id = product["product_code"]
            product_name = product["product_code__product_name"]
            product_data = queryset.filter(product_code=product_id)
            
            # Get all MPP data for this product
            mpp_data = product_data.values(
                "local_sale_code__mpp_code", 
                "local_sale_code"
            ).annotate(
                total_qty=Sum("qty"),
                total_amount=Sum("amount"),
                avg_rate=Avg("rate"),
            ).order_by("local_sale_code__mpp_code")
            
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
                        "rate_values": []
                    }
                
                mpp_groups[mpp_code]["local_sale_codes"].append(str(item["local_sale_code"]))
                mpp_groups[mpp_code]["total_qty"] += item["total_qty"]
                mpp_groups[mpp_code]["total_amount"] += item["total_amount"]
                mpp_groups[mpp_code]["rate_values"].append(item["avg_rate"])
            
            # Prepare the final mpp_summary
            mpp_summary = []
            for mpp_code, data in mpp_groups.items():
                # Calculate weighted average rate
                total_amount = data["total_amount"]
                total_qty = data["total_qty"]
                avg_rate = total_amount / total_qty if total_qty != 0 else 0
                
                mpp_summary.append({
                    "local_sale_code__mpp_code": mpp_code,
                    "local_sale_code": ", ".join(data["local_sale_codes"]),  # Comma separated string
                    "total_qty": data["total_qty"],
                    "total_amount": data["total_amount"],
                    "avg_rate": avg_rate
                })
            
            product_summary.append({
                "product_id": product_id,
                "product_name": product_name,
                "from_date": start_date,
                "to_date": end_date,
                "total_qty": product_data.aggregate(Sum("qty"))["qty__sum"] or 0,
                "total_amount": product_data.aggregate(Sum("amount"))["amount__sum"] or 0,
                "avg_rate": product_data.aggregate(Avg("rate"))["rate__avg"] or 0,
                "mpp_summary": mpp_summary,
            })

        return Response({
            "status": "success",
            "message": "Data fetched successfully",
            "product_summary": product_summary,
        })

        # def list(self, request, *args, **kwargs):
        #     queryset = self.get_queryset()
        #     start_date = self.request.query_params.get("start_date", None)
        #     end_date = self.request.query_params.get("end_date", None)
        #     # 🟢 Product-wise Summary (Group by product_code)
        #     product_summary = []
        #     products = queryset.values("product_code", "product_code__product_name").distinct()

        #     for product in products:
        #         product_id = product["product_code"]
        #         product_name = product["product_code__product_name"]
        #         product_data = queryset.filter(product_code=product_id)
        #         mpp_summary = (
        #             product_data.values("local_sale_code__mpp_code", "local_sale_code")  # Include Local Sale Code
        #             .annotate(
        #                 total_qty=Sum("qty"),
        #                 total_amount=Sum("amount"),
        #                 avg_rate=Avg("rate"),  # You can replace this with the latest rate if needed
        #             )
        #             .order_by("local_sale_code__mpp_code")  # Sort by MPP
        #         )
                
        #         product_summary.append({
        #             "product_id": product_id,
        #             "product_name": product_name,
        #             "from_date":start_date,
        #             "to_date":end_date,
        #             "total_qty": product_data.aggregate(Sum("qty"))["qty__sum"] or 0,
        #             "total_amount": product_data.aggregate(Sum("amount"))["amount__sum"] or 0,
        #             "avg_rate": product_data.aggregate(Avg("rate"))["rate__avg"] or 0,
        #             "mpp_summary": list(mpp_summary),
        #         })

        #     return Response({
        #         "status": "success",
        #         "message": "Data fetched successfully",
        #         "product_summary": product_summary,
        #     })


class ShiftViewSet(viewsets.ModelViewSet):
    authentication_classes = [ApiKeyAuthentication, JWTAuthentication]
    permission_classes = [AllowAny]
    queryset = Shift.objects.all().order_by("shift_name")
    serializer_class = ShiftSerializer


from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password


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


import random
from django.core.cache import cache


class RequestOTPPasswordResetView(APIView):
    def post(self, request):
        username = request.data.get("username")  # Or phone number
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
        # TODO: Integrate an SMS/notification service to send OTP to the user
        print(f"Your OTP is: {otp}")  # Debugging (Remove in production)
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
