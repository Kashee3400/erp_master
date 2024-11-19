import django_filters
from erp_app.models import CdaAggregationDaywiseMilktype,LocalSaleTxn,LocalSale,Product,MemberHierarchyView

class BooleanStringFilter(django_filters.BooleanFilter):
    def filter(self, qs, value):
        if value in ['true', 'false']:
            value = value == 'true'
        return super().filter(qs, value)

class MemberHeirarchyFilter(django_filters.FilterSet):
    is_active = BooleanStringFilter(field_name='is_active', label='Is Active')
    mpp_code = django_filters.CharFilter(field_name='mpp_code', lookup_expr='icontains', label='MPP Code')

    class Meta:
        model = MemberHierarchyView
        fields = ['is_active', 'mpp_code']

class CdaAggregationDaywiseMilktypeFilter(django_filters.FilterSet):
    class Meta:
        model = CdaAggregationDaywiseMilktype
        fields = ['created_at', 'mpp_code']

class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = ['is_saleable','is_purchase']

class LocalSaleTxnFilter(django_filters.FilterSet):
    # Filter for exact transaction_date
    transaction_date = django_filters.DateFilter(field_name='transaction_date', lookup_expr='exact', required=False)
    
    # Filter for filtering by month. The value should be an integer (e.g., 5 for May).
    transaction_month = django_filters.NumberFilter(field_name='transaction_date__month', lookup_expr='exact', required=False)
    
    # Filter for filtering by year. The value should be an integer (e.g., 2024).
    transaction_year = django_filters.NumberFilter(field_name='transaction_date__year', lookup_expr='exact', required=False)

    class Meta:
        model = LocalSaleTxn
        fields = ['transaction_date', 'transaction_month', 'transaction_year']

