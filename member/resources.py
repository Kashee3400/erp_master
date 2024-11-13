from import_export import resources
from .models import SahayakIncentives
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import SahayakIncentives
from django.contrib.auth import get_user_model

User = get_user_model()


class SahayakIncentivesResource(resources.ModelResource):
    user = fields.Field(
        column_name='user',
        attribute='user',
        widget=ForeignKeyWidget(User, 'username')
    )
    class Meta:
        model = SahayakIncentives
        fields = ('user', 'mcc_code', 'mcc_name', 'mpp_code', 'mpp_name', 'month', 'opening', 'milk_incentive', 'other_incentive', 'payable', 'closing')

        # Optional: Customize import/export behavior
        exclude = ('id',)
        import_id_fields = ('user', 'month')
        

class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')

        exclude = ('id',)
        import_id_fields = ('username',)
        