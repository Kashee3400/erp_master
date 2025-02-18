from rest_framework import generics, status, viewsets, exceptions, decorators
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from ..models import AssignedMppToFacilitator
from ..serializers import *
from erp_app.serializers import MemberHierarchyViewSerializer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from import_export.admin import ImportExportModelAdmin
from import_export.forms import (
    ImportForm,
)
from django_filters import FilterSet, DateFromToRangeFilter, DateTimeFromToRangeFilter
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django_filters import rest_framework as filters
import os
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Avg,Q
from django.conf import settings
from django.utils.timezone import now
from datetime import date
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

class CdaAggregationDaywiseMilktypeViewSet(viewsets.ModelViewSet):
    queryset = CdaAggregation.objects.all()
    serializer_class = CdaAggregationDaywiseMilktypeSerializer
    pagination_class = StandardResultsSetPagination
    authentication_classes = [JWTAuthentication]
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
        collection_date_param = request.query_params.get("created_at", None)
        mpp_ex_code = request.query_params.get("mpp_ex_code", None)
        if collection_date_param and collection_date_param.lower() != "null":
            collection_date = parse_date(collection_date_param)
        else:
            collection_date = now().date()
        mpp = AssignedMppToFacilitator.objects.filter(mpp_ex_code=mpp_ex_code).last()
        if not mpp:
            return Response(
                {
                    "status": "error",
                    "message": f"No MPP found for the provided mppcode: {mpp_ex_code}",
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

from asgiref.sync import sync_to_async

# class CdaAggregationDaywiseMilktypeViewSet(viewsets.ModelViewSet):
#     queryset = CdaAggregation.objects.all()
#     serializer_class = CdaAggregationDaywiseMilktypeSerializer
#     pagination_class = PageNumberPagination
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get_financial_year_dates(self, input_date):
#         """Returns the start and end date of the financial year for a given date."""
#         year = input_date.year
#         start_year, end_year = (year - 1, year) if input_date.month < 4 else (year, year + 1)
#         return date(start_year, 4, 1), date(end_year, 3, 31)

#     def format_aggregates(self, aggregates):
#         """Formats aggregate values to 2 decimal places."""
#         return {key: round(value, 2) if value is not None else None for key, value in aggregates.items()}

#     async def list(self, request, *args, **kwargs):
#         """Asynchronous list method with optimized database queries."""
#         collection_date_param = request.query_params.get("created_at", None)
#         mpp_ex_code = request.query_params.get("mpp_ex_code", None)

#         collection_date = parse_date(collection_date_param) if collection_date_param and collection_date_param.lower() != "null" else now().date()

#         # Fetch MPP asynchronously
#         mpp = await sync_to_async(AssignedMppToFacilitator.objects.filter(mpp_ex_code=mpp_ex_code).last)()
#         if not mpp:
#             return Response({"status": "error", "message": f"No MPP found for the provided mppcode: {mpp_ex_code}"}, status=status.HTTP_404_NOT_FOUND)

#         start_date, end_date = self.get_financial_year_dates(collection_date)

#         # Fetch financial year aggregate data asynchronously
#         fy_data = await sync_to_async(
#             lambda: CdaAggregation.objects.filter(
#                 collection_date__gte=start_date,
#                 collection_date__lte=end_date,
#                 mpp_code=mpp.mpp_code
#             ).aggregate(
#                 total_composite_qty=Sum("composite_qty"),
#                 total_dispatch_qty=Sum("dispatch_qty"),
#                 total_actual_qty=Sum("actual_qty"),
#                 avg_composite_fat=Avg("composite_fat"),
#                 avg_dispatch_fat=Avg("dispatch_fat"),
#                 avg_actual_fat=Avg("actual_fat"),
#                 avg_composite_snf=Avg("composite_snf"),
#                 avg_dispatch_snf=Avg("dispatch_snf"),
#                 avg_actual_snf=Avg("actual_snf"),
#             )
#         )()
        
#         formatted_fy_data = self.format_aggregates(fy_data)

#         # Fetch current date data (morning & evening shifts) asynchronously
#         current_date_data_morning = await sync_to_async(
#             lambda: list(CdaAggregation.objects.filter(collection_date__date=collection_date, mpp_code=mpp.mpp_code, shift="Morning"))
#         )()
#         current_date_data_evening = await sync_to_async(
#             lambda: list(CdaAggregation.objects.filter(collection_date__date=collection_date, mpp_code=mpp.mpp_code, shift="Evening"))
#         )()

#         # Apply pagination
#         page_morning = self.paginate_queryset(current_date_data_morning)
#         page_evening = self.paginate_queryset(current_date_data_evening)

#         if page_morning is not None:
#             serializer_morning = self.get_serializer(page_morning, many=True)
#             serializer_evening = self.get_serializer(page_evening, many=True)
#             return self.get_paginated_response(
#                 {
#                     "status": "success",
#                     "current_date_data": serializer_morning.data,
#                     "current_date_data_evening": serializer_evening.data,
#                     "fy_data": formatted_fy_data,
#                     "message": "Success",
#                 }
#             )

#         # If pagination is not applied, serialize everything
#         serializer_morning = self.get_serializer(current_date_data_morning, many=True)
#         serializer_evening = self.get_serializer(current_date_data_evening, many=True)

#         return Response(
#             {
#                 "status": "success",
#                 "current_date_data": serializer_morning.data,
#                 "current_date_data_evening": serializer_evening.data,
#                 "fy_data": formatted_fy_data,
#                 "message": "Success",
#             },
#             status=status.HTTP_200_OK,
#         )
