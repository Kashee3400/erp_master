from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from facilitator.models.facilitator_model import AssignedMppToFacilitator, User 

class FacilitatorResource(resources.ModelResource):
    mpp_code = fields.Field(column_name='mpp_code', attribute='mpp_code')
    mpp_short_name = fields.Field(column_name='mpp_short_name', attribute='mpp_short_name')
    mpp_ex_code = fields.Field(column_name='mpp_ex_code', attribute='mpp_ex_code')
    mpp_name = fields.Field(column_name='mpp_name', attribute='mpp_name')
    sahayak = fields.Field(
        column_name='sahayak',
        attribute='sahayak',
        widget=ForeignKeyWidget(User, 'username')
    )

    class Meta:
        model = AssignedMppToFacilitator
        fields = ('mpp_code', 'mpp_short_name', 'mpp_ex_code', 'mpp_name', 'sahayak')
        import_id_fields = ['mpp_code'] 
        skip_unchanged = True
        report_skipped = True

    # def before_import_row(self, row, **kwargs):
    #     # Optional: Validate or manipulate data before importing each row
    #     pass