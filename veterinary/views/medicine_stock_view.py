# views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from django.db.models import Q, Sum, F
from django.utils import timezone
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import IntegrityError, transaction
from rest_framework import serializers
from ..models.stock_models import (
    Medicine,
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
    InventoryAlertSerializer,
    DashboardStatsSerializer,
    MedicineBasicSerializer,
)
from ..filters.inventory_filter import MedicineStockFilter, UserMedicineStockFilter
from ..permissions import IsMedicineManagerOrReadOnly, CanManageUserStock, UserHierarchyChecker
from util.response import (
    custom_response,
    ExceptionHandlerMixin,
    ResponseMixin, StandardResultsSetPagination
)
from ..choices.choices import ActionTypeChoices, TransactionTypeChoices
from ..services.inventory_service import InventoryService, AlertService


class FilterMixin:
    """Mixin for handling common query parameters"""

    def get_base_filters(self):
        """Get base filters from request"""
        return InventoryService.get_base_filters(self.request)


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
    pagination_class = StandardResultsSetPagination
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
            transaction_type = TransactionTypeChoices.IN if stock.total_quantity > old_quantity else TransactionTypeChoices.OUT
            quantity_change = abs(stock.total_quantity - old_quantity)

            MedicineStockAudit.objects.create(
                medicine=stock.medicine,
                transaction_type=transaction_type,
                quantity=quantity_change,
                description=f"Stock adjusted from {old_quantity} to {stock.total_quantity}",
                created_by=self.request.user,
            )

    def create(self, request, *args, **kwargs):
        """
        Custom create method with integrity error handling.
        """
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                self.perform_create(serializer)

        except IntegrityError as e:
            return custom_response(
                status_text="error",
                message="A database integrity error.",
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={"detail": str(e)},
            )

        return custom_response(
            status_text="success",
            message="Medicine Allocated Successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
            errors={},
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return custom_response(
            status_text="success",
            message="User stock success.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=kwargs.get("partial", False),
            context={"request": request},
        )
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return custom_response(
                status_text="success",
                message="Stock Updated Successfully.",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        except serializers.ValidationError as e:
            return custom_response(
                status_text="error",
                message="Validation failed.",
                errors=e.detail,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete()
        return custom_response(
            status_text="success",
            message="Cattle tag deleted successfully.",
            data=None,
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path='low-stock-alerts')
    def low_stock_alerts(self, request):
        """Get medicines with low stock levels"""
        # Define low stock threshold (can be configurable)
        low_stock_threshold = request.query_params.get("threshold", 10)
        low_stocks = MedicineStock.objects.low_stock(threshold=low_stock_threshold)

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

    @action(detail=False, methods=["get"], url_path='expiry-alerts')
    def expiry_alerts(self, request):
        """Get medicines expiring soon or already expired"""
        days_ahead = int(request.query_params.get("days", 30))
        low_stock_threshold = int(request.query_params.get("threshold", 10))
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
                    "threshold_quantity": float(low_stock_threshold),
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

    @action(detail=False, methods=["post"], url_path="bulk-update-stock")
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

    @action(detail=True, methods=["get"], url_path="history")
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
    Handles CRUD operations for medicine transfers to users with hierarchy-based permissions.
    """

    queryset = UserMedicineStock.objects.select_related(
        "user",
        "user__profile",
        "medicine_stock",
        "medicine_stock__medicine",
        "medicine_stock__medicine__category",
        "allocated_by",
    )
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, CanManageUserStock]
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
    lookup_field = 'pk'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hierarchy_checker = UserHierarchyChecker()

    def get_serializer_class(self):
        if self.action in ["create", "update", "retrieve"]:
            return UserMedicineStockCreateSerializer
        return UserMedicineStockSerializer

    def get_queryset(self):
        """
        Filter queryset based on user hierarchy permissions.
        Users see their own stock + any subordinates' stock they can manage.
        """
        queryset = super().get_queryset()
        user = self.request.user

        # Superuser sees everything
        if user.is_superuser:
            return queryset

        # Get manageable user IDs using hierarchy checker
        manageable_user_ids = self._get_manageable_users(user)

        return queryset.filter(user__id__in=manageable_user_ids)

    def _get_manageable_users(self, user):
        """Get list of user IDs that this user can manage (including themselves)."""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        manageable_ids = [user.id]  # Always include self

        try:
            if user.is_superuser:
                return list(User.objects.values_list('id', flat=True))

            # Check hierarchy for all other users
            all_users = User.objects.select_related('profile').exclude(id=user.id)

            for potential_subordinate in all_users:
                if self.hierarchy_checker.is_supervisor_of(user, potential_subordinate):
                    manageable_ids.append(potential_subordinate.id)

        except Exception:
            # Fallback to just the user themselves
            pass

        return manageable_ids

    def perform_create(self, serializer):
        """
        Create allocation and log transaction.
        Set allocated_by to current user.
        """
        allocation = serializer.save(allocated_by=self.request.user)

        # Create transaction log
        UserMedicineTransaction.objects.create(
            user_medicine_stock=allocation,
            action=ActionTypeChoices.ALLOCATED,
            quantity=allocation.allocated_quantity,
            note=f"Initial allocation by {self.request.user.get_full_name()}",
            performed_by=self.request.user,
        )

    def create(self, request, *args, **kwargs):
        """
        Custom create method with integrity error handling.
        """
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                self.perform_create(serializer)

        except IntegrityError as e:
            return custom_response(
                status_text="error",
                message="A database integrity error.",
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={"detail": str(e)},
            )

        return custom_response(
            status_text="success",
            message="Medicine Allocated Successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
            errors={},
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return custom_response(
            status_text="success",
            message="User stock success.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=kwargs.get("partial", False),
            context={"request": request},
        )
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save(updated_by=request.user)
            return custom_response(
                status_text="success",
                message="Stock Updated Successfully.",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        except serializers.ValidationError as e:
            return custom_response(
                status_text="error",
                message="Validation failed.",
                errors=e.detail,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete()
        return custom_response(
            status_text="success",
            message="Cattle tag deleted successfully.",
            data=None,
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def my_allocations(self, request):
        """Get current user's medicine allocations only."""
        try:
            allocations = self.get_queryset().filter(user=request.user)

            page = self.paginate_queryset(allocations)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(allocations, many=True)
            return custom_response(
                status_text="success",
                data=serializer.data,
                message="User allocations retrieved successfully",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return custom_response(
                status_text="error",
                message="Failed to fetch user allocations",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def manageable_allocations(self, request):
        """Get allocations for all users this user can manage."""
        try:
            queryset = self.get_queryset()

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return custom_response(
                status_text="success",
                data=serializer.data,
                message="Manageable allocations retrieved successfully",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return custom_response(
                status_text="error",
                message="Failed to fetch manageable allocations",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def low_stock_users(self, request):
        """Get users with low medicine stock (from manageable users only)."""
        try:
            low_stocks = UserMedicineStock.active.get_low_stock().filter(
                user__id__in=self._get_manageable_users(request.user)
            )

            print(low_stocks)
            alerts = []
            for stock in low_stocks:
                remaining = stock.remaining_quantity()
                threshold = max(stock.min_threshold or 0, stock.threshold_quantity or 0)

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
                        "user_department": getattr(stock.user.profile, 'department', 'N/A') if hasattr(stock.user,
                                                                                                       'profile') else 'N/A',
                        "message": f"{stock.user.get_full_name()} has low stock: {remaining} {stock.medicine_stock.medicine.category.unit_of_quantity} remaining",
                    }
                )

            serializer = InventoryAlertSerializer(alerts, many=True)
            return custom_response(
                status_text="success",
                data=serializer.data,
                message="Low stock alerts retrieved successfully",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return custom_response(
                status_text="error",
                message="Failed to fetch low stock alerts",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def use_medicine(self, request, pk=None):
        """
        Record medicine usage.
        Users can record their own usage, supervisors can record for subordinates.
        """
        try:
            allocation = self.get_object()
            quantity = request.data.get("quantity")
            note = request.data.get("note", "")

            # Validate quantity
            try:
                quantity = int(quantity)
            except (TypeError, ValueError):
                return custom_response(
                    status_text="error",
                    message="Valid quantity is required",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            if quantity <= 0:
                return custom_response(
                    status_text="error",
                    message="Quantity must be greater than zero",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # Check allocation limit
            if allocation.used_quantity + quantity > allocation.allocated_quantity:
                return custom_response(
                    status_text="error",
                    message=(
                        f"Cannot use more than allocated quantity. "
                        f"Available: {allocation.remaining_quantity()}"
                    ),
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # 🔒 Transaction block
            with transaction.atomic():
                # Update used quantity
                allocation.used_quantity += quantity
                allocation.save()

                # Log transaction
                UserMedicineTransaction.objects.create(
                    user_medicine_stock=allocation,
                    action=ActionTypeChoices.USED,
                    quantity=quantity,
                    note=note,
                    performed_by=request.user,
                )

            serializer = self.get_serializer(allocation)

            return custom_response(
                status_text="success",
                data=serializer.data,
                message="Medicine usage recorded successfully",
                status_code=status.HTTP_200_OK,
            )

        except Exception as e:
            return custom_response(
                status_text="error",
                message="Failed to record medicine usage",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def return_medicine(self, request, pk=None):
        """
        Return unused medicine to stock.
        Users can return their own medicine, supervisors can process returns for subordinates.
        """
        try:
            allocation = self.get_object()
            quantity = request.data.get("quantity")
            note = request.data.get("note", "")

            # Validate quantity
            try:
                quantity = int(quantity)
            except (TypeError, ValueError):
                return custom_response(
                    status_text="error",
                    message="Valid quantity is required",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            if quantity <= 0:
                return custom_response(
                    status_text="error",
                    message="Quantity must be greater than zero",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # Check remaining quantity
            remaining = allocation.remaining_quantity()
            if quantity > remaining:
                return custom_response(
                    status_text="error",
                    message=f"Cannot return more than remaining quantity ({remaining})",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # 🔒 Start atomic transaction
            with transaction.atomic():
                # Update allocation
                allocation.allocated_quantity -= quantity
                allocation.save()

                # Return to main stock
                allocation.medicine_stock.total_quantity += quantity
                allocation.medicine_stock.save()

                # Log user transaction
                UserMedicineTransaction.objects.create(
                    user_medicine_stock=allocation,
                    action=ActionTypeChoices.RETURNED,
                    quantity=quantity,
                    note=note,
                    performed_by=request.user,
                )

                # Audit stock movement
                MedicineStockAudit.objects.create(
                    medicine=allocation.medicine_stock.medicine,
                    transaction_type=TransactionTypeChoices.IN,
                    quantity=quantity,
                    description=f"Medicine returned by {allocation.user.get_full_name()} "
                                f"(processed by {request.user.get_full_name()})",
                    created_by=request.user,
                )

            serializer = self.get_serializer(allocation)
            return custom_response(
                status_text="success",
                data=serializer.data,
                message="Medicine successfully returned to stock",
                status_code=status.HTTP_200_OK,
            )

        except Exception as e:
            return custom_response(
                status_text="error",
                message="Failed to return medicine to stock",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["get"])
    def transaction_history(self, request, pk=None):
        """Get transaction history for allocation."""
        try:
            allocation = self.get_object()
            transactions = allocation.transactions.all().order_by("-timestamp")
            print(allocation)
            if not transactions.exists():
                return custom_response(
                    status_text="success",
                    data=[],
                    message="No transactions found for this allocation",
                    status_code=status.HTTP_200_OK,
                )

            page = self.paginate_queryset(transactions)
            if page is not None:
                serializer = UserMedicineTransactionSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = UserMedicineTransactionSerializer(transactions, many=True)
            return custom_response(
                status_text="success",
                data=serializer.data,
                message="Transaction history fetched successfully",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return custom_response(
                status_text="error",
                message="Failed to fetch transaction history",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=['get'])
    def user_stock_summary(self, request):
        """Get stock summary for a specific user (if manageable)."""
        try:
            user_id = request.query_params.get('user_id')
            if not user_id:
                return custom_response(
                    status_text="error",
                    message="user_id parameter is required",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # Check if the requested user is manageable
            manageable_user_ids = self._get_manageable_users(request.user)
            if int(user_id) not in manageable_user_ids:
                return custom_response(
                    status_text="error",
                    message="You don't have permission to view this user's stock",
                    status_code=status.HTTP_403_FORBIDDEN
                )

            queryset = self.get_queryset().filter(user_id=user_id)

            # Calculate summary statistics
            from django.db.models import Sum, Count
            summary = queryset.aggregate(
                total_allocations=Count('id'),
                total_allocated_quantity=Sum('allocated_quantity') or 0,
                total_used_quantity=Sum('used_quantity') or 0,
            )

            summary['total_remaining'] = summary['total_allocated_quantity'] - summary['total_used_quantity']
            summary['usage_percentage'] = round(
                (summary['total_used_quantity'] / max(summary['total_allocated_quantity'], 1)) * 100, 2
            )

            return custom_response(
                status_text="success",
                message="User stock summary retrieved successfully",
                data=summary,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return custom_response(
                status_text="error",
                message="Failed to fetch user stock summary",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InventoryDashboardViewSet(
    ExceptionHandlerMixin,
    FilterMixin,
    ResponseMixin,
    viewsets.ViewSet
):
    """
    Dashboard API for inventory overview and alerts
    Clean, modular implementation following DRY principles
    """

    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Get dashboard statistics"""
        # try:
        # Get filters and querysets
        filters = self.get_base_filters()
        querysets = InventoryService.get_filtered_querysets(filters)

        # Calculate stats using service
        stats = InventoryService.calculate_dashboard_stats(querysets, filters)

        # Serialize and return
        serializer = DashboardStatsSerializer(stats)
        return self.success_response(data=serializer.data)

    # except Exception as e:
    # return self.error_response(f"Failed to retrieve dashboard stats: {str(e)}")

    @action(detail=False, methods=["get"])
    def all_alerts(self, request):
        """Get all inventory alerts in one call"""
        try:
            # Get filters and querysets
            filters = self.get_base_filters()
            querysets = InventoryService.get_filtered_querysets(filters)

            # Generate alerts using service
            alerts = AlertService.generate_all_alerts(querysets, filters)

            # Serialize and return
            serializer = InventoryAlertSerializer(alerts, many=True)
            return self.success_response(data=serializer.data)

        except Exception as e:
            return self.error_response(f"Failed to retrieve alerts: {str(e)}")

    @action(detail=False, methods=["get"])
    def medicine_list(self, request):
        """Get simplified medicine list for dropdowns"""
        try:
            filters = self.get_base_filters()

            medicines = Medicine.objects.select_related("category").filter(
                is_active=filters['is_active'],
                is_deleted=filters['is_deleted'],
                locale=filters['locale']
            ).order_by("medicine")

            serializer = MedicineBasicSerializer(medicines, many=True)
            return self.success_response(data=serializer.data)

        except Exception as e:
            return self.error_response(f"Failed to retrieve medicines: {str(e)}")
