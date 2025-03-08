from rest_framework import generics, status, viewsets, exceptions, decorators
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from ..models.facilitator_model import AssignedMppToFacilitator
from ..serializers.serializers import *
from erp_app.models import (
    MppCollection,
    MppCollectionReferences,
    RmrdMilkCollection,
    MppDispatch,
    MppDispatchTxn,
)
from django.db.models import Sum, F, FloatField
from django.db.models.functions import Coalesce, Cast, NullIf
from member.serialzers import RmrdCollectionSerializer
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

    def get_queryset(self):
        """
        Optionally restricts the returned queryset to the currently authenticated user,
        if the user is not a superuser or staff.
        """
        user = self.request.user

        # If the user is a superuser or staff, return all MPPs
        if user.is_superuser or user.is_staff:
            return AssignedMppToFacilitator.objects.all()

        # Otherwise, return only the MPPs assigned to the authenticated user
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

from django.db.models import DecimalField, FloatField, Value


class DashboardAPI(APIView):
    authentication_classes = [ApiKeyAuthentication, JWTAuthentication]
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination  # Assign pagination

    def get(self, request, *args, **kwargs):
        created_date = request.GET.get("date", timezone.now().date())
        mpp_codes = request.GET.get("mpp_code")
        sort_by = request.GET.get("sort_by", "morning")  # Default sorting by morning

        if not mpp_codes:
            mpp_codes = list(
                AssignedMppToFacilitator.objects.all().values_list(
                    "mpp_code", flat=True
                )
            )
        else:
            mpp_codes = mpp_codes.split(",")
        morning_code, evening_code = self.get_shifts()

        # 🔹 Step 4: Bulk fetch actual data for all mpp_codes
        actual_data = RmrdMilkCollection.objects.filter(
            collection_date__date=created_date, module_code__in=mpp_codes
        ).select_related("shift_code")

        actual_lookup = {
            (data.module_code, data.shift_code.shift_code): data for data in actual_data
        }
        response_data = []
        # 🔹 Step 5: Process each mpp_code
        for mpp_code in mpp_codes:
            # Get morning & evening references
            # Fetch morning and evening dispatch codes
            mor_mpp_dispatch_codes = MppDispatch.objects.filter(
                from_date__date=created_date, mpp_code=mpp_code, from_shift=morning_code
            ).values_list("mpp_dispatch_code", flat=True)

            eve_mpp_dispatch_codes = MppDispatch.objects.filter(
                from_date__date=created_date, mpp_code=mpp_code, from_shift=evening_code
            ).values_list("mpp_dispatch_code", flat=True)

            # Fetch Dispatch Transactions
            mor_dispatch_txn_data = MppDispatchTxn.objects.filter(
                mpp_dispatch_code__in=mor_mpp_dispatch_codes
            ).first()

            eve_dispatch_txn_data = MppDispatchTxn.objects.filter(
                mpp_dispatch_code__in=eve_mpp_dispatch_codes
            ).first()
            # Serialize Dispatch Transactions
            mor_dispatch_data = MppDispatchTxnSerializer(mor_dispatch_txn_data).data
            eve_dispatch_data = MppDispatchTxnSerializer(eve_dispatch_txn_data).data
            
            # 🔹 Step 2: Bulk fetch MppCollectionReferences for all mpp_codes
            mpp_refs = MppCollectionReferences.objects.filter(
                collection_date__date=created_date, mpp_code__in=mpp_codes,shift_code__shift_code=morning_code
            ).values_list("mpp_collection_references_code", flat=True)

            mor_mpp_collections = MppCollection.objects.filter(
                mpp_collection_references_code__in=mpp_refs
            ).aggregate(
                qty=Sum("qty"),
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

            # Get morning & evening actual data
            mor_actual_agg_data = actual_lookup.get((mpp_code, morning_code))
            eve_actual_agg_data = actual_lookup.get((mpp_code, evening_code))

            response_data.append(
                {
                    "mpp_code": mpp_code,
                    "morning": {
                        "composite": self.format_aggregates(mor_mpp_collections),
                        "actual": (
                            RmrdCollectionSerializer(mor_actual_agg_data).data
                            if mor_actual_agg_data
                            else {}
                        ),
                        "dispatch": mor_dispatch_data,
                    },
                    "evening": {
                        "composite": self.format_aggregates(mor_mpp_collections),
                        "actual": (
                            RmrdCollectionSerializer(eve_actual_agg_data).data
                            if eve_actual_agg_data
                            else {}
                        ),
                        "dispatch": eve_dispatch_data,
                    },
                }
            )

        # 🔹 Step 6: Sorting based on query param
        if sort_by == "evening":
            sorted_data = sorted(
                response_data, key=lambda x: x["evening"].get("variation", 0)
            )
        else:
            sorted_data = sorted(
                response_data, key=lambda x: x["morning"].get("variation", 0)
            )

        # 🔹 Step 7: Paginate and return response
        paginator = self.pagination_class()
        paginated_response = paginator.paginate_queryset(sorted_data, request)
        return paginator.get_paginated_response(paginated_response)

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
