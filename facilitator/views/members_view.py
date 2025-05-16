from rest_framework import status, viewsets, exceptions, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from ..serializers.serializers import *
from erp_app.models import (
    MemberHierarchyView,
    MppCollection,
)
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from ..authentication import ApiKeyAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncDate
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from django.utils.dateparse import parse_date
from django.db.models import Sum, F, FloatField, Avg, Q
from django.db.models.functions import Coalesce, Cast, Round

CACHE_TIMEOUT = 600
from django.core.cache import cache


def custom_response(status, data=None, message=None, status_code=200):
    response_data = {"status": status, "message": message or "Success", "data": data}
    return Response(
        response_data,
        status=status_code,
    )


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class MemberHierarchyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for fetching Member Hierarchy with filtering on:
    - `mcc_code`
    - `mpp_code`
    - `bmc_code`
    - `member_code`
    """

    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [AllowAny]
    queryset = MemberHierarchyView.objects.all()
    serializer_class = MemberHierarchySerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = [
        "mcc_code",
        "mpp_code",
        "member_code",
        "bmc_code",
        "is_active",
        "is_default",
    ]
    ordering_fields = ["created_at", "member_name"]
    search_fields = ["member_name", "mobile_no"]
    pagination_class = StandardResultsSetPagination
    lookup_field = "member_code"

    def retrieve(self, request, *args, **kwargs):
        """
        Override retrieve to filter data based on `member_code`
        """
        member_code = self.kwargs.get(self.lookup_field)
        queryset = self.get_queryset().filter(member_code=member_code)

        if not queryset.exists():
            return Response(
                {"status": "error", "message": "Not found.", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(queryset.first())
        return Response(
            {
                "status": "success",
                "message": "Data retrieved successfully.",
                "data": serializer.data,
            }
        )

    def list(self, request, *args, **kwargs):
        """
        Override list to format response with desired structure
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "status": "success",
                "message": "Data retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class MonthlyDataView(APIView):
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        year = int(request.GET.get("year", datetime.now().year))
        month = int(request.GET.get("month", datetime.now().month))
        mpp_code = request.GET.get("mpp_code")
        if not mpp_code:
            return Response(
                {"status": "error", "message": "mpp_code is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        start_date = make_aware(datetime(year, month, 1))
        if month == 12:
            end_date = make_aware(datetime(year + 1, 1, 1)) - timedelta(seconds=1)
        else:
            end_date = make_aware(datetime(year, month + 1, 1)) - timedelta(seconds=1)

        collections = MppCollection.objects.filter(
            collection_date__range=(start_date, end_date),
            member_code__startswith=mpp_code,
        )
        # Total milk collection
        milk_collection = collections.aggregate(total_qty=Sum("qty"))["total_qty"] or 0
        # Unique members
        total_members = MemberHierarchyView.objects.filter(
            mpp_code=mpp_code, is_active=True
        ).count()
        # Total pourers
        pourer_days = collections.values("member_code").annotate(
            days=Count(TruncDate("collection_date"), distinct=True)
        )
        no_of_pourers = pourer_days.count()
        # Pourers breakdown
        pourers_15_days = sum(1 for p in pourer_days if p["days"] >= 15)
        pourers_25_days = sum(1 for p in pourer_days if p["days"] >= 25)
        zero_days_pourers = total_members - no_of_pourers
        top_pourers = (
            collections.values("member_code")
            .annotate(total_qty=Sum("qty"))
            .order_by("-total_qty")[:3]
        )

        top_pourers_list = [
            {"member_code": p["member_code"], "total_qty": round(p["total_qty"], 2)}
            for p in top_pourers
        ]

        # Prepare response data
        response_data = {
            "mpp_code": mpp_code,
            "month": f"{year}-{month:02}",
            "milk_collection": round(milk_collection, 2),
            "total_members": total_members,
            "no_of_pourers": no_of_pourers,
            "pourers_15_days": pourers_15_days,
            "pourers_25_days": pourers_25_days,
            "zero_days_pourers": zero_days_pourers,
            "top_pourers": top_pourers_list,
        }

        serializer = MonthAssignmentSerializer(
            response_data, context={"request": request}
        )
        return Response(
            {
                "status": "success",
                "message": "Data fetched successfully",
                "result": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class LocalSaleViewSet(viewsets.ModelViewSet):
    queryset = LocalSaleTxn.objects.all()
    serializer_class = LocalSaleTxnSerializer
    authentication_classes = [ApiKeyAuthentication]
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_serializer_context(self):
        return {"request": self.request}

    def get_queryset(self):
        queryset = super().get_queryset()
        # Extract query parameters
        product_id = self.request.query_params.get("product_id", None)
        start_date = self.request.query_params.get("start_date", None)
        mpp_code = self.request.query_params.get("mpp_code", None)
        end_date = self.request.query_params.get("end_date", None)
        if mpp_code:
            queryset = queryset.filter(local_sale_code__mpp_code=mpp_code)
        if product_id:
            queryset = queryset.filter(product_code__product_code=product_id)

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

        # Aggregate data
        aggregated_data = queryset.aggregate(
            total_qty=Sum("qty") or 0,
            total_amount=Sum("amount") or 0,
            avg_rate=Avg("rate") or 0,
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


class MemberCDADetailView(APIView):
    """
    API endpoint to retrieve a summary of member collection data.

    This endpoint fetches quantity, amount, fat percentage, and snf percentage
    based on the collection date, member code, and shift.

    Authentication:
        - Uses `ApiKeyAuthentication` to ensure secure access.

    Methods:
        - GET: Retrieves aggregated collection data.

    Parameters:
        - date (str): Collection date in YYYY-MM-DD format.
        - member_code (str): Unique identifier for the member.
        - shift (str): Shift name for collection data filtering.

    Responses:
        - 200: Successful retrieval of member collection data.
        - 400: Missing required query parameters.
        - 500: Internal server error during processing.
    """

    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        collection_date = request.GET.get("date")
        member_code = request.GET.get("member_code")
        shift = request.GET.get("shift")

        if not collection_date or not member_code or not shift:
            return custom_response(
                status="error",
                message="collection_date, member_code, shift these fields are required.",
            )

        # Generate a unique cache key
        cache_key = f"cda_summary:{collection_date}:{member_code}:{shift}"
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return custom_response(
                status="success",
                data=cached_data,
                message="CDA fetched from cache",
                status_code=status.HTTP_200_OK,
            )

        try:
            composite_data = MppCollection.objects.filter(
                references__collection_date__date=collection_date,
                member_code=member_code,
                shift_code__shift_short_name=shift,
            ).aggregate(
                qty=Sum("qty"),
                amount=Sum("amount"),
                fat=Round(
                    Coalesce(
                        Cast(
                            Sum(F("qty") * F("fat"), output_field=FloatField()),
                            FloatField(),
                        )
                        / Cast(Sum("qty"), FloatField()),
                        0.0,
                    ),
                    2,
                ),
                snf=Round(
                    Coalesce(
                        Cast(
                            Sum(F("qty") * F("snf"), output_field=FloatField()),
                            FloatField(),
                        )
                        / Cast(Sum("qty"), FloatField()),
                        0.0,
                    ),
                    2,
                ),
            )

            # Store in cache for 15 minutes (900 seconds)
            cache.set(cache_key, composite_data, timeout=900)

            return custom_response(
                status="success",
                data=composite_data,
                message="CDA fetched successfully",
                status_code=status.HTTP_200_OK,
            )

        except Exception as e:
            return custom_response(
                status="error",
                data={},
                message="Server error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MemberLast10DaysQtyView(APIView):
    """
    API endpoint to retrieve a summary of member collection data.

    This endpoint fetches quantity, amount, fat percentage, and snf percentage
    based on the collection date, member code, and shift.

    Authentication:
        - Uses `ApiKeyAuthentication` to ensure secure access.

    Methods:
        - GET: Retrieves aggregated collection data.

    Parameters:
        - date (str): Collection date in YYYY-MM-DD format.
        - member_code (str): Unique identifier for the member.

    Responses:
        - 200: Successful retrieval of member collection data.
        - 400: Missing required query parameters.
        - 500: Internal server error during processing.
    """
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        from datetime import datetime, timedelta
        member_code = request.GET.get("member_code")
        collection_date_str = request.GET.get("collection_date")
        collection_date = datetime.strptime(collection_date_str, "%Y-%m-%d").date()

        if not collection_date or  not member_code:
            return custom_response(
                status="error",
                message="collection_date, member_code these fields are required.",
            )

        # Generate a unique cache key
        cache_key = f"10_days_qty:{collection_date}:{member_code}"
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return custom_response(
                status="success",
                data=cached_data,
                message="10 Days qty fetched from cache",
                status_code=status.HTTP_200_OK,
            )
        try:            
            
            ten_days_ago = collection_date - timedelta(days=9)
            composite_data = (
                MppCollection.objects
                .filter(
                    references__collection_date__date__range=[ten_days_ago, collection_date],
                    member_code=member_code
                )
                .annotate(date=TruncDate("references__collection_date"))
                .values("date")
                .annotate(total_qty=Sum("qty"))
                .order_by("date")
            )
            cache.set(cache_key, composite_data, timeout=900)
            return custom_response(
                status="success",
                data=composite_data,
                message="10 Days qty fetched successfully",
                status_code=status.HTTP_200_OK,
            )

        except Exception as e:
            return custom_response(
                status="error",
                data={},
                message="Server error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
