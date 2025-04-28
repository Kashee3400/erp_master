from import_export import resources
from facilitator.models.vcg_model import VCGMeeting,VCGroup,VCGMemberAttendance

class VCGroupResource(resources.ModelResource):
    class Meta:
        model = VCGroup
        import_id_fields = ['member_code']
        fields = (
            'member_code',
            'member_name',
            'whatsapp_num',
            'member_ex_code',
        )
        export_order = (
            'member_code',
            'member_name',
            'whatsapp_num',
            'member_ex_code',
        )
        skip_unchanged = True   # <<< ADD THIS
        report_skipped = True   # <<< AND THIS
