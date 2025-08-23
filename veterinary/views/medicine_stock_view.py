# views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from django.db.models import Q, Sum, F, Count, Case, When, FloatField
from django.utils import timezone
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models.stock_models import (
    Medicine,
    MedicineCategory,
    MedicineStock,
    UserMedicineStock,
    UserMedicineTransaction,
    MedicineStockAudit,
)
from ..serializers.inventory_serializers import (
    MedicineStockSerializer,
    MedicineStockCreateUpdateSerializer,
    UserMedicineStockSerializer,
    UserMedicineStockCreateSerializer,
    UserMedicineTransactionSerializer,
    MedicineStockAuditSerializer,
    InventoryAlertSerializer,
    DashboardStatsSerializer,
    MedicineBasicSerializer,
)
from ..filters.inventory_filter import MedicineStockFilter, UserMedicineStockFilter
from ..permissions import IsMedicineManagerOrReadOnly
from util.response import (
    custom_response,
    handle_custom_exceptions,
    ExceptionHandlerMixin,
)


class MedicineStockViewSet(ExceptionHandlerMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing global medicine stock.
    Supports CRUD operations with inventory alerts and batch operations.
    """

    queryset = MedicineStock.objects.select_related(
        "medicine", "medicine__category"
    ).prefetch_related("user_allocations")
    permission_classes = [permissions.IsAuthenticated, IsMedicineManagerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MedicineStockFilter
    search_fields = ["medicine__medicine", "batch_number", "medicine__strength"]
    ordering_fields = ["total_quantity", "expiry_date", "last_updated"]
    ordering = ["-last_updated"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return MedicineStockCreateUpdateSerializer
        return MedicineStockSerializer

    def perform_create(self, serializer):
        """Create stock entry and log audit trail"""
        stock = serializer.save()

        # Create audit log
        MedicineStockAudit.objects.create(
            medicine=stock.medicine,
            transaction_type="IN",
            quantity=stock.total_quantity,
            description=f"New stock added - Batch: {stock.batch_number or 'N/A'}",
            created_by=self.request.user,
        )

    def perform_update(self, serializer):
        """Update stock and log changes"""
        old_quantity = serializer.instance.total_quantity
        stock = serializer.save()

        # Log quantity changes
        if old_quantity != stock.total_quantity:
            transaction_type = "IN" if stock.total_quantity > old_quantity else "OUT"
            quantity_change = abs(stock.total_quantity - old_quantity)

            MedicineStockAudit.objects.create(
                medicine=stock.medicine,
                transaction_type=transaction_type,
                quantity=quantity_change,
                description=f"Stock adjusted from {old_quantity} to {stock.total_quantity}",
                created_by=self.request.user,
            )

    @action(detail=False, methods=["get"])
    def low_stock_alerts(self, request):
        """Get medicines with low stock levels"""
        # Define low stock threshold (can be configurable)
        low_stock_threshold = request.query_params.get("threshold", 10)

        low_stocks = (
            self.get_queryset()
            .annotate(
                allocated_quantity=Sum("user_allocations__allocated_quantity"),
                available_quantity=F("total_quantity") - F("allocated_quantity"),
            )
            .filter(
                Q(available_quantity__lte=low_stock_threshold)
                | Q(
                    available_quantity__isnull=True,
                    total_quantity__lte=low_stock_threshold,
                )
            )
        )

        alerts = []
        for stock in low_stocks:
            available = stock.available_quantity or stock.total_quantity
            alerts.append(
                {
                    "type": "global_stock",
                    "severity": "critical" if available <= 5 else "warning",
                    "medicine_name": stock.medicine.medicine,
                    "medicine_strength": stock.medicine.strength or "",
                    "current_quantity": available,
                    "threshold_quantity": float(low_stock_threshold),
                    "unit_of_quantity": stock.medicine.category.unit_of_quantity,
                    "batch_number": stock.batch_number,
                    "message": f"Low stock alert: Only {available} {stock.medicine.category.unit_of_quantity} remaining",
                }
            )

        serializer = InventoryAlertSerializer(alerts, many=True)
        return custom_response(
            status_text="success", data=serializer.data, message="Success"
        )

    @action(detail=False, methods=["get"])
    def expiry_alerts(self, request):
        """Get medicines expiring soon or already expired"""
        days_ahead = int(request.query_params.get("days", 30))
        future_date = timezone.now().date() + timedelta(days=days_ahead)

        expiring_stocks = (
            self.get_queryset()
            .filter(expiry_date__lte=future_date, expiry_date__isnull=False)
            .order_by("expiry_date")
        )

        alerts = []
        for stock in expiring_stocks:
            days_to_expiry = (stock.expiry_date - timezone.now().date()).days
            severity = (
                "expired"
                if days_to_expiry < 0
                else "critical" if days_to_expiry <= 7 else "warning"
            )

            alerts.append(
                {
                    "type": "global_stock",
                    "severity": severity,
                    "medicine_name": stock.medicine.medicine,
                    "medicine_strength": stock.medicine.strength or "",
                    "current_quantity": stock.total_quantity,
                    "unit_of_quantity": stock.medicine.category.unit_of_quantity,
                    "batch_number": stock.batch_number,
                    "expiry_date": stock.expiry_date,
                    "days_to_expiry": days_to_expiry,
                    "message": f"{'Expired' if days_to_expiry < 0 else 'Expiring in'} {abs(days_to_expiry)} days",
                }
            )

        serializer = InventoryAlertSerializer(alerts, many=True)
        return custom_response(
            status_text="success",
            status_code=status.HTTP_200_OK,
            data=serializer.data,
            message="Success",
        )

    @action(detail=False, methods=["post"])
    def bulk_update_stock(self, request):
        """Bulk update stock quantities"""
        updates = request.data.get("updates", [])

        if not updates:
            return custom_response(
                status_text="error",
                errors={"error": "No updates provided"},
                status_code=status.HTTP_400_BAD_REQUEST,
                message="No updates provided",
            )

        updated_stocks = []
        errors = []

        for update in updates:
            try:
                stock_id = update.get("id")
                new_quantity = update.get("quantity")
                reason = update.get("reason", "Bulk update")

                if not stock_id or new_quantity is None:
                    errors.append(f"Missing id or quantity for update")
                    continue

                stock = MedicineStock.objects.get(id=stock_id)
                old_quantity = stock.total_quantity
                stock.total_quantity = new_quantity
                stock.save()

                # Log audit
                transaction_type = "IN" if new_quantity > old_quantity else "OUT"
                quantity_change = abs(new_quantity - old_quantity)

                MedicineStockAudit.objects.create(
                    medicine=stock.medicine,
                    transaction_type=transaction_type,
                    quantity=quantity_change,
                    description=f"{reason} - Changed from {old_quantity} to {new_quantity}",
                    created_by=request.user,
                )

                updated_stocks.append(stock.id)

            except MedicineStock.DoesNotExist:
                errors.append(f"Stock with id {stock_id} not found")
            except Exception as e:
                errors.append(f"Error updating stock {stock_id}: {str(e)}")
        return custom_response(
            status_text="success",
            status_code=status.HTTP_200_OK,
            data={
                "updated_stocks": updated_stocks,
                "success_count": len(updated_stocks),
            },
            errors=errors,
        )

    @action(detail=True, methods=["get"])
    def allocation_history(self, request, pk=None):
        """Get allocation history for a specific stock"""
        stock = self.get_object()
        allocations = UserMedicineStock.objects.filter(
            medicine_stock=stock
        ).select_related("user", "allocated_by")

        serializer = UserMedicineStockSerializer(allocations, many=True)
        return custom_response(
            status_text="success",
            status_code=status.HTTP_200_OK,
            data=serializer.data,
            message="Success",
        )


class UserMedicineStockViewSet(ExceptionHandlerMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing user medicine stock allocations.
    Handles CRUD operations for medicine transfers to users.
    """

    queryset = UserMedicineStock.objects.select_related(
        "user",
        "medicine_stock",
        "medicine_stock__medicine",
        "medicine_stock__medicine__category",
        "allocated_by",
    )
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UserMedicineStockFilter
    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "medicine_stock__medicine__medicine",
    ]
    ordering_fields = ["allocation_date", "allocated_quantity", "used_quantity"]
    ordering = ["-allocation_date"]

    def get_serializer_class(self):
        if self.action == "create":
            return UserMedicineStockCreateSerializer
        return UserMedicineStockSerializer

    def get_queryset(self):
        """Filter based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user

        # If user is not staff/admin, only show their own allocations
        if not user.is_staff:
            queryset = queryset.filter(user=user)

        return queryset

    def perform_create(self, serializer):
        """Create allocation and log transaction"""
        allocation = serializer.save()

        # Create transaction log
        UserMedicineTransaction.objects.create(
            user_medicine_stock=allocation,
            action="ALLOCATED",
            quantity=allocation.allocated_quantity,
            note=f"Initial allocation by {self.request.user.get_full_name()}",
        )

    @action(detail=False, methods=["get"])
    def my_allocations(self, request):
        """Get current user's medicine allocations"""
        allocations = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(allocations, many=True)
        return custom_response(
            status_text="success",
            data=serializer.data,
            message="Success",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def low_stock_users(self, request):
        """Get users with low medicine stock"""
        low_stocks = (
            self.get_queryset()
            .annotate(remaining=F("allocated_quantity") - F("used_quantity"))
            .filter(
                Q(remaining__lte=F("min_threshold"))
                | Q(remaining__lte=F("threshold_quantity"))
            )
        )

        alerts = []
        for stock in low_stocks:
            remaining = stock.remaining_quantity()
            threshold = max(stock.min_threshold, stock.threshold_quantity)

            alerts.append(
                {
                    "type": "user_stock",
                    "severity": (
                        "critical" if remaining <= threshold * 0.5 else "warning"
                    ),
                    "medicine_name": stock.medicine_stock.medicine.medicine,
                    "medicine_strength": stock.medicine_stock.medicine.strength or "",
                    "current_quantity": remaining,
                    "threshold_quantity": threshold,
                    "unit_of_quantity": stock.medicine_stock.medicine.category.unit_of_quantity,
                    "user_name": stock.user.get_full_name(),
                    "message": f"{stock.user.get_full_name()} has low stock: {remaining} {stock.medicine_stock.medicine.category.unit_of_quantity} remaining",
                }
            )

        serializer = InventoryAlertSerializer(alerts, many=True)
        return custom_response(
            status_text="success",
            data=serializer.data,
            message="Success",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def use_medicine(self, request, pk=None):
        """Record medicine usage"""
        allocation = self.get_object()
        quantity = request.data.get("quantity")
        note = request.data.get("note", "")

        # Validate quantity
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return custom_response(
                status_text="error",
                data={},
                message="Valid quantity is required",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if quantity <= 0:
            return custom_response(
                status_text="error",
                data={},
                message="Quantity must be greater than zero",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Check allocation limit
        if allocation.used_quantity + quantity > allocation.allocated_quantity:
            return custom_response(
                status_text="error",
                data={},
                message="Cannot use more than allocated quantity",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Update used quantity
        allocation.used_quantity += quantity
        allocation.save()

        # Log transaction
        UserMedicineTransaction.objects.create(
            user_medicine_stock=allocation,
            action="USED",
            quantity=quantity,
            note=note,
        )

        serializer = self.get_serializer(allocation)

        return custom_response(
            status_text="success",
            data=serializer.data,
            message="Medicine usage recorded successfully",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def return_medicine(self, request, pk=None):
        """Return unused medicine to stock"""
        allocation = self.get_object()
        quantity = request.data.get("quantity")
        note = request.data.get("note", "")

        # ✅ Validate quantity
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return custom_response(
                status_text="error",
                data={},
                message="Valid quantity is required",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if quantity <= 0:
            return custom_response(
                status_text="error",
                data={},
                message="Quantity must be greater than zero",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Check remaining quantity
        remaining = allocation.remaining_quantity()
        if quantity > remaining:
            return custom_response(
                status_text="error",
                data={},
                message=f"Cannot return more than remaining quantity ({remaining})",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Update allocation
        allocation.allocated_quantity -= quantity
        allocation.save()

        # ✅ Return to main stock
        allocation.medicine_stock.total_quantity += quantity
        allocation.medicine_stock.save()

        # ✅ Log user transaction
        UserMedicineTransaction.objects.create(
            user_medicine_stock=allocation,
            action="RETURNED",
            quantity=quantity,
            note=note,
        )

        # ✅ Audit stock movement
        MedicineStockAudit.objects.create(
            medicine=allocation.medicine_stock.medicine,
            transaction_type="IN",
            quantity=quantity,
            description=f"Medicine returned by {allocation.user.get_full_name()}",
            created_by=request.user,
        )

        serializer = self.get_serializer(allocation)
        return custom_response(
            status_text="success",
            data=serializer.data,
            message="Medicine successfully returned to stock",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"])
    def transaction_history(self, request, pk=None):
        """Get transaction history for allocation"""
        allocation = self.get_object()
        transactions = allocation.transactions.all().order_by("-created_at")

        if not transactions.exists():
            return custom_response(
                status_text="success",
                data=[],
                message="No transactions found for this allocation",
                status_code=status.HTTP_200_OK,
            )

        serializer = UserMedicineTransactionSerializer(transactions, many=True)
        return custom_response(
            status_text="success",
            data=serializer.data,
            message="Transaction history fetched successfully",
            status_code=status.HTTP_200_OK,
        )



class DashboardViewSet(ExceptionHandlerMixin, viewsets.ViewSet):
    """
    Dashboard API for inventory overview and alerts
    """

    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Get dashboard statistics"""
        now = timezone.now()

        stats = {
            "total_medicines": Medicine.objects.count(),
            "total_stock_items": MedicineStock.objects.count(),
            "total_user_allocations": UserMedicineStock.objects.count(),
            "expired_stock_count": MedicineStock.objects.filter(
                expiry_date__lt=now.date()
            ).count(),
            "expiring_soon_count": MedicineStock.objects.filter(
                expiry_date__lte=now.date() + timedelta(days=30),
                expiry_date__gte=now.date(),
            ).count(),
            "low_stock_count": MedicineStock.objects.annotate(
                available=F("total_quantity")
                - Sum("user_allocations__allocated_quantity")
            )
            .filter(available__lte=10)
            .count(),
            "critical_user_stock_count": UserMedicineStock.objects.annotate(
                remaining=F("allocated_quantity") - F("used_quantity")
            )
            .filter(
                Q(remaining__lte=F("min_threshold"))
                | Q(remaining__lte=F("threshold_quantity"))
            )
            .count(),
        }

        serializer = DashboardStatsSerializer(stats)
        return custom_response(
            data=serializer.data, status_text="success", status_code=status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"])
    def all_alerts(self, request):
        """Get all inventory alerts in one call"""
        alerts = []

        # Global low stock alerts
        low_stocks = (
            MedicineStock.objects.annotate(
                allocated_quantity=Sum("user_allocations__allocated_quantity"),
                available_quantity=F("total_quantity") - F("allocated_quantity"),
            )
            .filter(
                Q(available_quantity__lte=10)
                | Q(available_quantity__isnull=True, total_quantity__lte=10)
            )
            .select_related("medicine", "medicine__category")
        )

        for stock in low_stocks:
            available = stock.available_quantity or stock.total_quantity
            alerts.append(
                {
                    "type": "global_stock",
                    "severity": "critical" if available <= 5 else "warning",
                    "medicine_name": stock.medicine.medicine,
                    "medicine_strength": stock.medicine.strength or "",
                    "current_quantity": available,
                    "threshold_quantity": 10.0,
                    "unit_of_quantity": stock.medicine.category.unit_of_quantity,
                    "batch_number": stock.batch_number,
                    "message": f"Low global stock: {available} {stock.medicine.category.unit_of_quantity} remaining",
                }
            )

        # Expiry alerts
        future_date = timezone.now().date() + timedelta(days=30)
        expiring_stocks = MedicineStock.objects.filter(
            expiry_date__lte=future_date, expiry_date__isnull=False
        ).select_related("medicine", "medicine__category")

        for stock in expiring_stocks:
            days_to_expiry = (stock.expiry_date - timezone.now().date()).days
            severity = (
                "expired"
                if days_to_expiry < 0
                else "critical" if days_to_expiry <= 7 else "warning"
            )

            alerts.append(
                {
                    "type": "global_stock",
                    "severity": severity,
                    "medicine_name": stock.medicine.medicine,
                    "medicine_strength": stock.medicine.strength or "",
                    "current_quantity": stock.total_quantity,
                    "unit_of_quantity": stock.medicine.category.unit_of_quantity,
                    "batch_number": stock.batch_number,
                    "expiry_date": stock.expiry_date,
                    "days_to_expiry": days_to_expiry,
                    "message": f"{'Expired' if days_to_expiry < 0 else 'Expiring in'} {abs(days_to_expiry)} days",
                }
            )

        # User low stock alerts
        user_low_stocks = (
            UserMedicineStock.objects.annotate(
                remaining=F("allocated_quantity") - F("used_quantity")
            )
            .filter(
                Q(remaining__lte=F("min_threshold"))
                | Q(remaining__lte=F("threshold_quantity"))
            )
            .select_related(
                "user", "medicine_stock__medicine", "medicine_stock__medicine__category"
            )
        )

        for stock in user_low_stocks:
            remaining = stock.remaining_quantity()
            threshold = max(stock.min_threshold, stock.threshold_quantity)

            alerts.append(
                {
                    "type": "user_stock",
                    "severity": (
                        "critical" if remaining <= threshold * 0.5 else "warning"
                    ),
                    "medicine_name": stock.medicine_stock.medicine.medicine,
                    "medicine_strength": stock.medicine_stock.medicine.strength or "",
                    "current_quantity": remaining,
                    "threshold_quantity": threshold,
                    "unit_of_quantity": stock.medicine_stock.medicine.category.unit_of_quantity,
                    "user_name": stock.user.get_full_name(),
                    "message": f"{stock.user.get_full_name()} - Low stock: {remaining} {stock.medicine_stock.medicine.category.unit_of_quantity} remaining",
                }
            )

        # Sort by severity
        severity_order = {"expired": 0, "critical": 1, "warning": 2}
        alerts.sort(key=lambda x: severity_order.get(x["severity"], 3))

        serializer = InventoryAlertSerializer(alerts, many=True)
        return custom_response(
            status_code=status.HTTP_200_OK,
            data=serializer.data,
            status_text="success",
            message="Success",
        )

    @action(detail=False, methods=["get"])
    def medicine_list(self, request):
        """Get simplified medicine list for dropdowns"""
        medicines = Medicine.objects.select_related("category").all()
        serializer = MedicineBasicSerializer(medicines, many=True)
        return custom_response(
            status_code=status.HTTP_200_OK,
            data=serializer.data,
            status_text="success",
            message="Success",
        )

