import django_filters
from erp_app.models import (
    CdaAggregationDaywiseMilktype,
    LocalSaleTxn,
    Product,
    MemberHierarchyView,
)
from django.utils import timezone
from datetime import timedelta
from django.contrib import admin
from django.utils.translation import gettext_lazy as _



class BooleanStringFilter(django_filters.BooleanFilter):
    def filter(self, qs, value):
        if value in ["true", "false"]:
            value = value == "true"
        return super().filter(qs, value)


class MemberHeirarchyFilter(django_filters.FilterSet):
    is_active = BooleanStringFilter(field_name="is_active", label="Is Active")
    mpp_code = django_filters.CharFilter(
        field_name="mpp_code", lookup_expr="icontains", label="MPP Code"
    )

    class Meta:
        model = MemberHierarchyView
        fields = ["is_active", "mpp_code"]


class CdaAggregationDaywiseMilktypeFilter(django_filters.FilterSet):
    class Meta:
        model = CdaAggregationDaywiseMilktype
        fields = ["created_at", "mpp_code"]


class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = ["is_saleable", "is_purchase"]


class LocalSaleTxnFilter(django_filters.FilterSet):
    # Filter for exact transaction_date
    transaction_date = django_filters.DateFilter(
        field_name="transaction_date", lookup_expr="exact", required=False
    )

    # Filter for filtering by month. The value should be an integer (e.g., 5 for May).
    transaction_month = django_filters.NumberFilter(
        field_name="transaction_date__month", lookup_expr="exact", required=False
    )

    # Filter for filtering by year. The value should be an integer (e.g., 2024).
    transaction_year = django_filters.NumberFilter(
        field_name="transaction_date__year", lookup_expr="exact", required=False
    )

    class Meta:
        model = LocalSaleTxn
        fields = ["transaction_date", "transaction_month", "transaction_year"]


from django.conf import settings
from django import forms
from .models import SahayakIncentives


class SahayakIncentivesFilter(django_filters.FilterSet):
    mpp_code = django_filters.CharFilter(
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Enter MPP Code"}
        )
    )
    mcc_code = django_filters.CharFilter(
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Enter MCC Code"}
        )
    )
    month = django_filters.ChoiceFilter(
        choices=settings.MONTH_FILTER,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    year = django_filters.NumberFilter(
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Year"})
    )

    class Meta:
        model = SahayakIncentives
        fields = ["mpp_code", "mcc_code", "month", "year"]


class SahayakIncentivesFilter(django_filters.FilterSet):
    mpp_code = django_filters.CharFilter(
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Enter MPP Code"}
        )
    )
    mcc_code = django_filters.CharFilter(
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Enter MCC Code"}
        )
    )
    month = django_filters.ChoiceFilter(
        choices=settings.MONTH_FILTER,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    year = django_filters.NumberFilter(
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Year"})
    )

    class Meta:
        model = SahayakIncentives
        fields = ["mpp_code", "mcc_code", "month", "year"]


class PublishedFilter(admin.SimpleListFilter):
    """Custom filter for published status with more options"""

    title = _("publication status")
    parameter_name = "pub_status"

    def lookups(self, request, model_admin):
        return (
            ("published", _("Published")),
            ("draft", _("Draft")),
            ("featured", _("Featured")),
        )

    def queryset(self, request, queryset):
        if self.value() == "published":
            return queryset.filter(is_published=True)
        elif self.value() == "draft":
            return queryset.filter(is_published=False)
        elif self.value() == "featured":
            return queryset.filter(is_featured=True)
        return queryset


class RecentNewsFilter(admin.SimpleListFilter):
    """Filter for recent news articles"""

    title = _("published timeframe")
    parameter_name = "timeframe"

    def lookups(self, request, model_admin):
        return (
            ("today", _("Today")),
            ("week", _("Past Week")),
            ("month", _("Past Month")),
            ("quarter", _("Past 3 Months")),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == "today":
            return queryset.filter(published_date__date=now.date())
        elif self.value() == "week":
            return queryset.filter(published_date__gte=now - timedelta(days=7))
        elif self.value() == "month":
            return queryset.filter(published_date__gte=now - timedelta(days=30))
        elif self.value() == "quarter":
            return queryset.filter(published_date__gte=now - timedelta(days=90))
        return queryset
