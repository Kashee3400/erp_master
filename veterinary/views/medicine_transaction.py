# views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from ..models.stock_models import UserMedicineTransaction
from util.response import custom_response,StandardResultsSetPagination
from ..permissions import CanManageMedicineTransactions, CanCreateTransactions,UserHierarchyChecker
from ..serializers.medicine_transaction import (
    UserMedicineTransactionSerializer,
    CreateTransactionSerializer
)
from django.contrib.auth import get_user_model


User = get_user_model()


class UserMedicineTransactionViewSet(viewsets.ModelViewSet):
    queryset = UserMedicineTransaction.objects.select_related(
        'user_medicine_stock__user',
        'user_medicine_stock__medicine_stock__medicine',
        'performed_by'
    ).all()
    
    pagination_class = StandardResultsSetPagination
    permission_classes = [CanManageMedicineTransactions, CanCreateTransactions]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action', 'user_medicine_stock__user', 'performed_by']
    search_fields = ['note', 'user_medicine_stock__user__username']
    ordering_fields = ['timestamp', 'quantity', 'running_balance']
    ordering = ['-timestamp']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hierarchy_checker = UserHierarchyChecker()

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateTransactionSerializer
        return UserMedicineTransactionSerializer

    def get_queryset(self):
        """
        Filter queryset based on user hierarchy permissions.
        Uses the reusable UserHierarchyChecker for consistent logic.
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # Superuser sees all transactions
        if user.is_superuser:
            return queryset
        
        # Get all users this user can access using the hierarchy checker
        manageable_user_ids = self._get_manageable_users(user)
        
        return queryset.filter(
            user_medicine_stock__user__id__in=manageable_user_ids
        )

    def _get_manageable_users(self, user):
        """
        Get list of user IDs that this user can manage.
        Uses the centralized UserHierarchyChecker for consistent logic.
        """
        manageable_ids = [user.id]
        
        try:
            # For superusers, return all users
            if user.is_superuser:
                return list(User.objects.values_list('id', flat=True))
            
            # Get all users by checking hierarchy for each user
            all_users = User.objects.select_related('profile').exclude(id=user.id)
            
            for potential_subordinate in all_users:
                if self.hierarchy_checker.is_supervisor_of(user, potential_subordinate):
                    manageable_ids.append(potential_subordinate.id)
        
        except Exception as e:
            # Log the exception if you have logging setup
            # logger.error(f"Error getting manageable users for {user}: {e}")
            pass
        
        return manageable_ids

    def perform_create(self, serializer):
        """
        Override to set performed_by field automatically.
        """
        serializer.save(performed_by=self.request.user)

    def create(self, request, *args, **kwargs):
        """Enhanced create method with better error handling."""
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            try:
                # Use perform_create to ensure performed_by is set
                self.perform_create(serializer)
                transaction_obj = serializer.instance
                
                response_serializer = UserMedicineTransactionSerializer(transaction_obj)
                
                return custom_response(
                    status_text="success",
                    message="Transaction created successfully",
                    data=response_serializer.data,
                    status_code=status.HTTP_201_CREATED
                )
            except Exception as e:
                return custom_response(
                    status_text="error",
                    message="Failed to create transaction",
                    errors={"detail": str(e)},
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        return custom_response(
            status_text="error",
            message="Validation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    def list(self, request, *args, **kwargs):
        """Enhanced list method with better error handling."""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return custom_response(
                status_text="success",
                message="Transactions retrieved successfully",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return custom_response(
                status_text="error",
                message="Failed to fetch transactions",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        """Enhanced retrieve method with better error handling."""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return custom_response(
                status_text="success",
                message="Transaction retrieved successfully",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return custom_response(
                status_text="error",
                message="Transaction not found",
                errors={"detail": str(e)},
                status_code=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def my_transactions(self, request):
        """Get current user's transactions only."""
        try:
            queryset = self.get_queryset().filter(
                user_medicine_stock__user=request.user
            )
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return custom_response(
                status_text="success",
                message="User transactions retrieved successfully",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return custom_response(
                status_text="error",
                message="Failed to fetch user transactions",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def recent_transactions(self, request):
        """Get transactions from last 7 days for manageable users."""
        try:
            last_week = timezone.now() - timedelta(days=7)
            queryset = self.get_queryset().filter(timestamp__gte=last_week)
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return custom_response(
                status_text="success",
                message="Recent transactions retrieved successfully",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return custom_response(
                status_text="error",
                message="Failed to fetch recent transactions",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def transaction_summary(self, request):
        """Get transaction summary statistics for manageable users."""
        try:
            queryset = self.get_queryset()
            
            summary = queryset.aggregate(
                total_transactions=Count('id'),
                total_allocated=Sum('quantity', filter=Q(action=ActionTypeChoices.ALLOCATED)) or 0,
                total_used=Sum('quantity', filter=Q(action=ActionTypeChoices.USED)) or 0,
                total_returned=Sum('quantity', filter=Q(action=ActionTypeChoices.RETURNED)) or 0,
            )
            
            # Add additional summary data
            summary.update({
                'net_consumption': (summary['total_allocated'] or 0) - (summary['total_returned'] or 0),
                'consumption_rate': round((summary['total_used'] or 0) / max(summary['total_allocated'] or 1, 1) * 100, 2),
            })
            
            # Convert None to 0 for cleaner response
            for key, value in summary.items():
                if value is None:
                    summary[key] = 0
            
            return custom_response(
                status_text="success",
                message="Transaction summary retrieved successfully",
                data=summary,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return custom_response(
                status_text="error",
                message="Failed to generate transaction summary",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def manageable_users(self, request):
        """Get list of users this user can manage - useful for frontend dropdowns."""
        try:
            manageable_user_ids = self._get_manageable_users(request.user)
            users = User.objects.filter(
                id__in=manageable_user_ids
            ).select_related('profile').values(
                'id', 'username', 'first_name', 'last_name', 'email',
                'profile__department'
            )
            
            return custom_response(
                status_text="success",
                message="Manageable users retrieved successfully",
                data=list(users),
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return custom_response(
                status_text="error",
                message="Failed to fetch manageable users",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def user_transaction_history(self, request):
        """Get transaction history for a specific user (if manageable)."""
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
                    message="You don't have permission to view this user's transactions",
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            queryset = self.get_queryset().filter(
                user_medicine_stock__user_id=user_id
            )
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return custom_response(
                status_text="success",
                message="User transaction history retrieved successfully",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return custom_response(
                status_text="error",
                message="Failed to fetch user transaction history",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
# Example API Usage:

"""
1. Create a transaction (POST /api/medicine-transactions/):
{
    "user_medicine_stock": 1,
    "action": "USED",
    "quantity": 5.0,
    "note": "Given to patient for fever treatment"
}

2. Get all transactions (GET /api/medicine-transactions/):
- Returns paginated list of transactions

3. Get user's own transactions (GET /api/medicine-transactions/my_transactions/):
- Returns transactions for the authenticated user

4. Get recent transactions (GET /api/medicine-transactions/recent_transactions/):
- Returns transactions from last 7 days

5. Get transaction summary (GET /api/medicine-transactions/transaction_summary/):
- Returns aggregate statistics

6. Filter transactions:
- GET /api/medicine-transactions/?action=USED
- GET /api/medicine-transactions/?user_medicine_stock__user=1
- GET /api/medicine-transactions/?search=fever

7. Get specific transaction (GET /api/medicine-transactions/{id}/):
- Returns single transaction details
"""