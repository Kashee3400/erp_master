# views.py
from django_filters.rest_framework import (
    FilterSet,
    CharFilter,
    DateTimeFilter,
    NumberFilter,
)
from ..models.transaction_model import PaymentTransaction
from django.db.models import Q


class PaymentTransactionFilter(FilterSet):
    """Advanced filtering for payment transactions"""

    # Date range filters
    created_after = DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = DateTimeFilter(field_name="created_at", lookup_expr="lte")

    # Amount range filters
    amount_min = NumberFilter(field_name="amount", lookup_expr="gte")
    amount_max = NumberFilter(field_name="amount", lookup_expr="lte")

    # Search filters
    search = CharFilter(method="search_filter")

    # Status filters
    status = CharFilter(field_name="status", lookup_expr="exact")
    transaction_type = CharFilter(field_name="transaction_type", lookup_expr="exact")
    payment_method_type = CharFilter(
        field_name="payment_method_type", lookup_expr="exact"
    )

    # User filter
    user_identifier = CharFilter(field_name="user_identifier", lookup_expr="icontains")

    # Related object filter
    content_type_model = CharFilter(method="filter_content_type")

    class Meta:
        model = PaymentTransaction
        fields = [
            "status",
            "transaction_type",
            "payment_method_type",
            "currency",
            "is_active",
        ]

    def search_filter(self, queryset, name, value):
        """Search across multiple fields"""
        return queryset.filter(
            Q(merchant_order_id__icontains=value)
            | Q(phonepe_transaction_id__icontains=value)
            | Q(user_identifier__icontains=value)
            | Q(object_id__icontains=value)
        )

    def filter_content_type(self, queryset, name, value):
        """Filter by content type model name"""
        return queryset.filter(content_type__model=value)
