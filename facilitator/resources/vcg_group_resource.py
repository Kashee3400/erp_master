from facilitator.models.vcg_model import VCGMeeting,VCGroup,VCGMemberAttendance
from facilitator.models.facilitator_model import AssignedMppToFacilitator
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget


class VCGroupResource(resources.ModelResource):
    mpp = fields.Field(column_name='mpp',attribute='mpp',
        widget=ForeignKeyWidget(AssignedMppToFacilitator, 'mpp_ex_code')
    )
    class Meta:
        model = VCGroup
        fields = ('member_code', 'member_ex_code', 'member_name', 'whatsapp_num', 'mpp')
        import_id_fields = ('member_code',)
        skip_unchanged = True
        report_skipped = True
        exclude = ('id',)