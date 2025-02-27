from rest_framework import generics, status, viewsets, exceptions, decorators
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from ..models import AssignedMppToFacilitator
from ..serializers import *
from erp_app.models import (
    MemberMaster,
    Mpp,
    MemberSahayakContactDetail,
    LocalSaleTxn,
    MemberHierarchyView,
    BillingMemberDetail,
    MppCollection,
    MppCollectionReferences,
    RmrdMilkCollection,
)
from member.serialzers import RmrdCollectionSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.utils.dateparse import parse_date

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

from rest_framework.exceptions import ValidationError
from ..authentication import ApiKeyAuthentication


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
                {"message": "Assigned MPP created successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return Response(
                {"message": "Validation error occurred.", "errors": e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"message": "An unexpected error occurred.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(
                {"message": "Assigned MPP updated successfully.", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response(
                {"message": "Validation error occurred.", "errors": e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"message": "An unexpected error occurred.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {"message": "Assigned MPP deleted successfully."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"message": "An unexpected error occurred.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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


class FacilitatorDashboardAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        created_date = request.GET.get("date", timezone.now().date())
        mpp_codes = request.GET.get("mpp_code")
        shift_code = request.GET.get("shift_code")

        if not mpp_codes:
            return Response(
                {"status": "error", "message": "Please provide at least one MPP code"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Convert comma-separated MPP codes into a list
        mpp_code_list = [code.strip() for code in mpp_codes.split(",")]

        # Fetch all MPP references
        mpp_refs = MppCollectionReferences.objects.filter(
            collection_date__date=created_date, 
            mpp_code__in=mpp_code_list, 
            shift_code=shift_code
        )

        if not mpp_refs.exists():
            return Response(
                {"status": "error", "message": "No MPP references found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        from django.db.models import Sum, F, FloatField
        from django.db.models.functions import Coalesce, Cast

        # Fetch all actual milk collection data for given MPPs
        actual_agg_data = RmrdMilkCollection.objects.filter(
            collection_date__date=created_date,
            module_code__in=mpp_code_list,
            shift_code__shift_code=shift_code,
        )
        print(f"actual_agg_data: {actual_agg_data}")
        # Store actual milk collection data in a dictionary {mpp_code: serialized_data}
        actual_data_dict = {
            item.module_code: RmrdCollectionSerializer(item).data for item in actual_agg_data
        }

        response_data = {}
        total_composite = {"qty": 0.0, "fat": 0.0, "snf": 0.0, "fat_weighted": 0.0, "snf_weighted": 0.0}
        total_actual = {"qty": 0.0, "fat": 0.0, "snf": 0.0, "fat_weighted": 0.0, "snf_weighted": 0.0}

        for mpp_ref in mpp_refs:
            mpp_code = mpp_ref.mpp_code

            # Aggregate MPP Collection Data
            mpp_collection_agg = MppCollection.objects.filter(
                mpp_collection_references_code=mpp_ref.mpp_collection_references_code
            ).aggregate(
                qty=Sum("qty", default=0.0),
                fat=Coalesce(
                    Cast(Sum(F("qty") * F("fat"), output_field=FloatField()), FloatField()) /
                    Cast(Sum("qty"), FloatField()), 
                    0.0
                ),
                snf=Coalesce(
                    Cast(Sum(F("qty") * F("snf"), output_field=FloatField()), FloatField()) /
                    Cast(Sum("qty"), FloatField()), 
                    0.0
                ),
            )

            # Fetch actual collection data from dictionary
            actual_data = actual_data_dict.get(mpp_code, {})

            # Extract actual values
            actual_qty = float(actual_data.get("quantity", 0.0))
            actual_fat = float(actual_data.get("fat", 0.0))
            actual_snf = float(actual_data.get("snf", 0.0))
            total_composite["qty"] += float(mpp_collection_agg["qty"] or 0.0)
            total_composite["fat_weighted"] += float(mpp_collection_agg["qty"] or 0.0) * float(mpp_collection_agg["fat"] or 0.0)
            total_composite["snf_weighted"] += float(mpp_collection_agg["qty"] or 0.0) * float(mpp_collection_agg["snf"] or 0.0)

            # Update total actual
            total_actual["qty"] += float(actual_qty)
            total_actual["fat_weighted"] += float(actual_qty) * float(actual_fat)
            total_actual["snf_weighted"] += float(actual_qty) * float(actual_snf)

            # Store results per MPP
            response_data[mpp_code] = {
                "composite": self.format_aggregates(mpp_collection_agg),
                "actual": actual_data,  
                "dispatch": {},
            }

        # Calculate weighted average for total fat & snf
        total_composite["fat"] = (total_composite["fat_weighted"] / total_composite["qty"]) if total_composite["qty"] else 0.0
        total_composite["snf"] = (total_composite["snf_weighted"] / total_composite["qty"]) if total_composite["qty"] else 0.0

        total_actual["fat"] = (total_actual["fat_weighted"] / total_actual["qty"]) if total_actual["qty"] else 0.0
        total_actual["snf"] = (total_actual["snf_weighted"] / total_actual["qty"]) if total_actual["qty"] else 0.0

        # Prepare final response
        final_response = {
            "status": 200,
            "message": _("Data Retrieved"),
            "data": {
                "composite": self.format_aggregates(total_composite),
                "actual": {
                    "qty": round(total_actual["qty"], 2),
                    "fat": round(total_actual["fat"], 2),
                    "snf": round(total_actual["snf"], 2),
                },
                "dispatch": {},
            },
        }

        return Response(final_response, status=status.HTTP_200_OK)

    def format_aggregates(self, aggregates):
        return {
            key: round(value, 2) if value is not None else None
            for key, value in aggregates.items()
            if key in ["qty", "fat", "snf"]
        }
