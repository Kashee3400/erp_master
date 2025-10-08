# filters.py
import django_filters
from django.db.models import Q, F

from ..models.stock_models import MedicineStock, UserMedicineStock


class MedicineStockFilter(django_filters.FilterSet):
    medicine_name = django_filters.CharFilter(
        field_name="medicine__medicine", lookup_expr="icontains", label="Medicine Name"
    )
    locale = django_filters.CharFilter(field_name='locale',lookup_expr='exact',label="Locale")
    category = django_filters.CharFilter(
        field_name="medicine__category__category",
        lookup_expr="icontains",
        label="Category",
    )

    medicine_form = django_filters.ChoiceFilter(
        field_name="medicine__category__medicine_form", label="Medicine Form"
    )

    expiry_status = django_filters.ChoiceFilter(
        method="filter_by_expiry_status",
        choices=[
            ("expired", "Expired"),
            ("expiring_soon", "Expiring Soon (30 days)"),
            ("expiring_week", "Expiring This Week"),
            ("valid", "Valid"),
            ("no_expiry", "No Expiry"),
        ],
        label="Expiry Status",
    )

    stock_level = django_filters.ChoiceFilter(
        method="filter_by_stock_level",
        choices=[
            ("out_of_stock", "Out of Stock"),
            ("low_stock", "Low Stock (≤10)"),
            ("critical_stock", "Critical Stock (≤5)"),
            ("adequate", "Adequate Stock"),
            ("overstock", "Over Stock"),
        ],
        label="Stock Level",
    )

    batch_number = django_filters.CharFilter(
        lookup_expr="icontains", label="Batch Number"
    )

    total_quantity__gte = django_filters.NumberFilter(
        field_name="total_quantity", lookup_expr="gte", label="Minimum Quantity"
    )

    total_quantity__lte = django_filters.NumberFilter(
        field_name="total_quantity", lookup_expr="lte", label="Maximum Quantity"
    )

    expiry_date__gte = django_filters.DateFilter(
        field_name="expiry_date", lookup_expr="gte", label="Expiry Date From"
    )

    expiry_date__lte = django_filters.DateFilter(
        field_name="expiry_date", lookup_expr="lte", label="Expiry Date To"
    )

    has_allocations = django_filters.BooleanFilter(
        method="filter_has_allocations", label="Has User Allocations"
    )

    class Meta:
        model = MedicineStock
        fields = {
            "medicine": ["exact"],
            "total_quantity": ["exact"],
            "last_updated": ["gte", "lte"],
        }

    def filter_by_expiry_status(self, queryset, name, value):

        if value == "expired":
            return queryset.expired()
        elif value == "expiring_soon":
            return queryset.expiring(day=30)
        elif value == "expiring_week":
            return queryset.expiring_soon(day=7)
        elif value == "valid":
            return queryset.valid_stock()
        
        elif value == "no_expiry":
            return queryset.no_expiry()

        return queryset

    def filter_by_stock_level(self, queryset, name, value):
        
        if value == "out_of_stock":
            return queryset.out_of_stock()
        elif value == "critical_stock":
            return queryset.critical_stock()
        
        elif value == "low_stock":
            return queryset.low_stock(threshold=10)
        
        elif value == "adequate":
            return queryset.healthy_stock(threshold=10)
        
        elif value == "overstock":
            return queryset.overstocked(threshold=1000)
        return queryset
    
    def filter_has_allocations(self, queryset, name, value):
        if value:
            return queryset.filter(user_allocations__isnull=False).distinct()
        else:
            return queryset.filter(user_allocations__isnull=True)


class UserMedicineStockFilter(django_filters.FilterSet):
    user_name = django_filters.CharFilter(
        method="filter_by_user_name", label="User Name"
    )
    is_deleted = django_filters.BooleanFilter(field_name="is_deleted")
    is_active = django_filters.BooleanFilter(field_name="is_active")

    username = django_filters.CharFilter(
        field_name="user__username", lookup_expr="icontains", label="Username"
    )

    medicine_name = django_filters.CharFilter(
        field_name="medicine_stock__medicine__medicine",
        lookup_expr="icontains",
        label="Medicine Name",
    )

    category = django_filters.CharFilter(
        field_name="medicine_stock__medicine__category__category",
        lookup_expr="icontains",
        label="Category",
    )

    batch_number = django_filters.CharFilter(
        field_name="medicine_stock__batch_number",
        lookup_expr="icontains",
        label="Batch Number",
    )

    stock_status = django_filters.ChoiceFilter(
        method="filter_by_stock_status",
        choices=[
            ("below_threshold", "Below Threshold"),
            ("critical", "Critical (≤50% of threshold)"),
            ("adequate", "Adequate"),
            ("fully_used", "Fully Used"),
        ],
        label="Stock Status",
    )

    allocation_date__gte = django_filters.DateFilter(
        field_name="allocation_date", lookup_expr="gte", label="Allocated From"
    )

    allocation_date__lte = django_filters.DateFilter(
        field_name="allocation_date", lookup_expr="lte", label="Allocated To"
    )

    allocated_by = django_filters.ModelChoiceFilter(
        queryset=None, label="Allocated By"  # Will be set in __init__
    )

    sync_status = django_filters.BooleanFilter(field_name="sync", label="Sync Status")

    remaining_quantity__gte = django_filters.NumberFilter(
        method="filter_remaining_quantity_gte", label="Minimum Remaining Quantity"
    )

    remaining_quantity__lte = django_filters.NumberFilter(
        method="filter_remaining_quantity_lte", label="Maximum Remaining Quantity"
    )

    class Meta:
        model = UserMedicineStock
        fields = {
            "user": ["exact"],
            "is_deleted": ["exact"],
            "is_active": ["exact"],
            "medicine_stock": ["exact"],
            "allocated_quantity": ["gte", "lte"],
            "used_quantity": ["gte", "lte"],
            "allocation_date": ["exact"],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set queryset for allocated_by field
        from django.contrib.auth import get_user_model

        User = get_user_model()
        self.filters["allocated_by"].queryset = User.objects.filter(
            stock_allocations_made__isnull=False
        ).distinct()

    def filter_by_user_name(self, queryset, name, value):
        return queryset.filter(
            Q(user__first_name__icontains=value)
            | Q(user__last_name__icontains=value)
            | Q(user__username__icontains=value)
        )

    def filter_by_stock_status(self, queryset, name, value):
        queryset = queryset.annotate(
            remaining_qty=F("allocated_quantity") - F("used_quantity")
        )

        if value == "below_threshold":
            return queryset.filter(
                Q(remaining_qty__lte=F("min_threshold"))
                | Q(remaining_qty__lte=F("threshold_quantity"))
            )
        elif value == "critical":
            return queryset.filter(
                Q(remaining_qty__lte=F("min_threshold") * 0.5)
                | Q(remaining_qty__lte=F("threshold_quantity") * 0.5)
            )
        elif value == "adequate":
            return queryset.filter(
                Q(remaining_qty__gt=F("min_threshold"))
                & Q(remaining_qty__gt=F("threshold_quantity"))
            )
        elif value == "fully_used":
            return queryset.filter(remaining_qty__lte=0)

        return queryset

    def filter_remaining_quantity_gte(self, queryset, name, value):
        return queryset.annotate(
            remaining_qty=F("allocated_quantity") - F("used_quantity")
        ).filter(remaining_qty__gte=value)

    def filter_remaining_quantity_lte(self, queryset, name, value):
        return queryset.annotate(
            remaining_qty=F("allocated_quantity") - F("used_quantity")
        ).filter(remaining_qty__lte=value)
