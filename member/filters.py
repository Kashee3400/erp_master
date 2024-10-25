# filters.py
import django_filters
from erp_app.models import CdaAggregationDaywiseMilktype

class CdaAggregationDaywiseMilktypeFilter(django_filters.FilterSet):
    class Meta:
        model = CdaAggregationDaywiseMilktype
        fields = ['collection_date', 'mpp_code']
