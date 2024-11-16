import django_filters
from erp_app.models import CdaAggregationDaywiseMilktype,LocalSaleTxn,LocalSale,Product
import django_filters

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

