# views.py
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from ..models import PaymentTransaction
from ..serializers import (
    PaymentTransactionDetailSerializer,
    PaymentStatisticsSerializer,
    PaymentTransactionListSerializer,
)
from ..filters import PaymentTransactionFilter
from util.response import ResponseMixin,StandardResultsSetPagination
from django.contrib.contenttypes.models import ContentType

class PaymentTransactionViewSet(viewsets.ReadOnlyModelViewSet, ResponseMixin):
    """
    ViewSet for Payment Transactions with advanced features

    Endpoints:
    - GET /api/transaction/ - List all transactions (paginated, filtered, sorted)
    - GET /api/transaction/{id}/ - Get transaction details
    - GET /api/transaction/statistics/ - Get overall statistics
    - GET /api/transaction/status_breakdown/ - Get status breakdown
    - GET /api/transaction/daily_stats/ - Get daily statistics
    - GET /api/transaction/by_object/?model=caseentry&object_id=123
    - GET /api/transaction/export/ - Export transactions to CSV
    """
    pagination_class = StandardResultsSetPagination

    queryset = PaymentTransaction.objects.select_related("content_type").all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = PaymentTransactionFilter

    # Search fields
    search_fields = [
        "merchant_order_id",
        "phonepe_transaction_id",
        "user_identifier",
        "object_id",
    ]

    # Ordering fields
    ordering_fields = [
        "created_at",
        "updated_at",
        "amount",
        "status",
        "transaction_type",
    ]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """Use different serializers for list and detail views"""
        if self.action == "retrieve":
            return PaymentTransactionDetailSerializer
        return PaymentTransactionListSerializer

    def get_queryset(self):
        """Optimize queryset based on action"""
        queryset = super().get_queryset()

        # Only active transactions by default
        if self.request.query_params.get("include_deleted") != "true":
            queryset = queryset.filter(is_active=True)

        return queryset

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        stats = queryset.aggregate(
            total_transactions=Count("id"),
            total_amount=Sum("amount", default=Decimal("0.00")),
            successful_transactions=Count("id", filter=Q(status="SUCCESS")),
            successful_amount=Sum(
                "amount", filter=Q(status="SUCCESS"), default=Decimal("0.00")
            ),
            failed_transactions=Count("id", filter=Q(status="FAILED")),
            pending_transactions=Count(
                "id", filter=Q(status__in=["INITIATED", "PENDING"])
            ),
            refunded_transactions=Count("id", filter=Q(refund_amount__gt=0)),
            refunded_amount=Sum("refund_amount", default=Decimal("0.00")),
            average_transaction_amount=Avg("amount", default=Decimal("0.00")),
        )

        stats["success_rate"] = (
            round(
                (stats["successful_transactions"] / stats["total_transactions"]) * 100,
                2,
            )
            if stats["total_transactions"] > 0
            else 0.0
        )

        serializer = PaymentStatisticsSerializer(stats)
        return self.success_response(serializer.data)

    # ----------------------------------------------------------

    @action(detail=False, methods=["get"])
    def status_breakdown(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        breakdown = (
            queryset.values("status")
            .annotate(
                count=Count("id"),
                total_amount=Sum("amount", default=Decimal("0.00")),
            )
            .order_by("-count")
        )

        return self.success_response(list(breakdown))

    # ----------------------------------------------------------

    @action(detail=False, methods=["get"])
    def transaction_type_breakdown(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        breakdown = (
            queryset.values("transaction_type")
            .annotate(
                count=Count("id"),
                total_amount=Sum("amount", default=Decimal("0.00")),
                successful_count=Count("id", filter=Q(status="SUCCESS")),
            )
            .order_by("-count")
        )

        return self.success_response(list(breakdown))

    # ----------------------------------------------------------
    
    @action(detail=False, methods=["get"], url_path="by_object")
    def get_by_object(self, request):
        """
        Get payment transactions for a specific content_type + object_id.

        Example:
        GET /api/transactions/by_object/?model=caseentry&object_id=123
        """

        model_name = request.query_params.get("model")
        object_id = request.query_params.get("object_id")

        if not model_name or not object_id:
            return self.error_response(
                message="Both 'model' and 'object_id' parameters are required.",
                status_code=400
            )

        # Validate model exists
        try:
            content_type = ContentType.objects.get(model=model_name.lower())
        except ContentType.DoesNotExist:
            return self.error_response(
                message=f"Invalid model name: '{model_name}'",
                status_code=400
            )

        # Fetch transactions for that object
        qs = self.get_queryset().filter(
            content_type=content_type,
            object_id=object_id
        ).order_by("-created_at")

        serializer = PaymentTransactionListSerializer(
            qs, many=True, context={"request": request}
        )

        return self.success_response(
            message="Payment transactions fetched successfully.",
            data=serializer.data
        )
    # ----------------------------------------------------------
        
    @action(detail=False, methods=["get"])
    def payment_method_breakdown(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        breakdown = (
            queryset.values("payment_method_type")
            .annotate(
                count=Count("id"),
                total_amount=Sum("amount", default=Decimal("0.00")),
                successful_count=Count("id", filter=Q(status="SUCCESS")),
            )
            .order_by("-count")
        )

        return self.success_response(list(breakdown))

    # ----------------------------------------------------------

    @action(detail=False, methods=["get"])
    def daily_stats(self, request):
        days = int(request.query_params.get("days", 7))
        start_date = timezone.now() - timedelta(days=days)

        queryset = self.filter_queryset(self.get_queryset()).filter(
            created_at__gte=start_date
        )

        daily_stats = (
            queryset.extra(select={"day": "DATE(created_at)"})
            .values("day")
            .annotate(
                count=Count("id"),
                total_amount=Sum("amount", default=Decimal("0.00")),
                successful_count=Count("id", filter=Q(status="SUCCESS")),
                successful_amount=Sum(
                    "amount", filter=Q(status="SUCCESS"), default=Decimal("0.00")
                ),
                failed_count=Count("id", filter=Q(status="FAILED")),
            )
            .order_by("day")
        )

        return self.success_response(list(daily_stats))

    # ----------------------------------------------------------

    @action(detail=False, methods=["get"])
    def recent_transactions(self, request):
        limit = int(request.query_params.get("limit", 10))
        queryset = self.get_queryset().order_by("-created_at")[:limit]
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(serializer.data)


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.paginator.get_paginated_response(serializer.data)

    # ----------------------------------------------------------

    @action(detail=False, methods=["get"])
    def export(self, request):
        import csv
        from django.http import HttpResponse

        queryset = self.filter_queryset(self.get_queryset())

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="transactions_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        )

        writer = csv.writer(response)
        writer.writerow(
            [
                "Merchant Order ID",
                "PhonePe Transaction ID",
                "Transaction Type",
                "User Identifier",
                "Amount",
                "Currency",
                "Status",
                "Payment Method",
                "Created At",
                "Completed At",
            ]
        )

        for tx in queryset:
            writer.writerow(
                [
                    tx.merchant_order_id,
                    tx.phonepe_transaction_id or "",
                    tx.transaction_type,
                    tx.user_identifier,
                    tx.amount,
                    tx.currency,
                    tx.status,
                    tx.payment_method_type or "",
                    tx.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    (
                        tx.completed_at.strftime("%Y-%m-%d %H:%M:%S")
                        if tx.completed_at
                        else ""
                    ),
                ]
            )
        return response 
