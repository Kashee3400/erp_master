from import_export import resources, fields
from ..models.member_update_model import UpdateRequest, DocumentTypeChoice
import logging

logger = logging.getLogger(__name__)


class UpdateRequestResource(resources.ModelResource):
    # Core fields
    request_id = fields.Field(attribute="request_id", column_name="Request ID")
    member_code = fields.Field(attribute="member_code", column_name="Member Code")
    member_name = fields.Field(attribute="member_name", column_name="Member Name")
    mobile_number = fields.Field(attribute="mobile_number", column_name="Mobile Number")
    request_type = fields.Field(attribute="request_type", column_name="Request Type")
    role_type = fields.Field(attribute="role_type", column_name="Role Type")
    status = fields.Field(attribute="status", column_name="Status")

    # Bank fields
    new_account_number = fields.Field(
        attribute="new_account_number", column_name="New Account Number"
    )
    new_account_holder_name = fields.Field(
        attribute="new_account_holder_name", column_name="Account Holder Name"
    )
    bank_name = fields.Field(attribute="bank_name", column_name="Bank Name")
    branch_name = fields.Field(attribute="branch_name", column_name="Branch Name")
    ifsc = fields.Field(attribute="ifsc", column_name="IFSC Code")

    def __init__(self, request=None, **kwargs):
        super().__init__(**kwargs)
        self.request = request
        for choice, label in DocumentTypeChoice.choices:
            field_name = f"file_{choice.lower()}"
            self.fields[field_name] = fields.Field(
                column_name=label,
                attribute=None,
                readonly=True,
            )

            # Dynamically define dehydrate_<field_name>
            setattr(
                self,
                f"dehydrate_{field_name}",
                self.make_dehydrate_method(choice.lower(), field_name),
            )

    def make_dehydrate_method(self, doc_type, field_name):
        def dehydrate_method(obj):
            doc = next(
                (d for d in obj.documents.all() if d.document_type.lower() == doc_type),
                None,
            )
            if doc:
                from django.contrib.sites.models import Site
                from django.conf import settings
                scheme = (
                    "https"
                    if getattr(settings, "SECURE_SSL_REDIRECT", False)
                    else "http"
                )
                domain = Site.objects.get_current().domain
                absolute_url = f"{scheme}://{domain}{doc.file.url}"
                return f'=HYPERLINK("{absolute_url}", "View")'
            return ""

        return dehydrate_method

    class Meta:
        model = UpdateRequest
        fields = (
            "request_id",
            "member_code",
            "member_name",
            "mobile_number",
            "request_type",
            "role_type",
            "status",
            "new_account_number",
            "new_account_holder_name",
            "bank_name",
            "branch_name",
            "ifsc",
        )
        export_order = fields
