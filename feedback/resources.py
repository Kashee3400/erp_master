from import_export import resources, fields
from import_export.widgets import DateTimeWidget
from django.utils.timezone import localtime
from .models import Feedback

class FeedbackResource(resources.ModelResource):
    # Convert to naive datetime in desired format
    created_at = fields.Field(
        column_name='Created At',
        attribute='created_at',
        widget=DateTimeWidget(format='%Y-%m-%d %H:%M:%S')
    )

    # Override dehydrate_<field> to remove tzinfo
    def dehydrate_created_at(self, obj):
        if obj.created_at:
            return localtime(obj.created_at).replace(tzinfo=None)
        return ''

    class Meta:
        model = Feedback
        fields = (
            'feedback_id','mpp_code', 'mcc_code', 'member_code', 'member_tr_code',
            'name', 'mobile_no', 'status', 'priority','created_at','message'
        )
        export_order = fields
