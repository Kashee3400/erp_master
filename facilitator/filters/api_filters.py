import django_filters
from ..models.vcg_model import VCGMeeting,MonthAssignment

class VCGMeetingFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    mpp_code = django_filters.CharFilter(field_name="mpp_code", lookup_expr="icontains")
    started_at = django_filters.DateFilter(field_name="started_at", lookup_expr="gte")
    completed_at = django_filters.DateFilter(field_name="completed_at", lookup_expr="lte")

    class Meta:
        model = VCGMeeting
        fields = ['status', 'mpp_code', 'started_at', 'completed_at']


class MonthAssignmentFilter(django_filters.FilterSet):
    mpp_code = django_filters.CharFilter(field_name="mpp_code", lookup_expr="iexact")  # Exact match
    month = django_filters.CharFilter(field_name="month", lookup_expr="iexact")  # Exact match

    class Meta:
        model = MonthAssignment
        fields = ["mpp_code", "month"]
