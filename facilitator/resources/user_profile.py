from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from django.contrib.auth.models import User

from ..models.user_profile_model import UserProfile

class UserProfileResource(resources.ModelResource):
    # Include user-related fields
    user__username = fields.Field(
        column_name="Username",
        attribute="user",
        widget=ForeignKeyWidget(User, "username"),
    )
    user__first_name = fields.Field(
        column_name="First Name", attribute="user__first_name"
    )
    user__last_name = fields.Field(column_name="Last Name", attribute="user__last_name")
    user__email = fields.Field(column_name="Email", attribute="user__email")
    user__is_active = fields.Field(column_name="Is Active", attribute="user__is_active")
    user__is_staff = fields.Field(column_name="Is Staff", attribute="user__is_staff")

    # Flattened or derived custom fields
    reports_to__username = fields.Field(
        column_name="Reports To Username", attribute="reports_to__user__username"
    )

    department_display = fields.Field(
        column_name="Department",
    )

    full_contact = fields.Field(
        column_name="Full Contact Info",
    )

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "user__username",
            "user__first_name",
            "user__last_name",
            "user__email",
            "user__is_active",
            "user__is_staff",
            "salutation",
            "designation",
            "department_display",
            "phone_number",
            "address",
            "full_contact",
            "reports_to__username",
            "is_verified",
            "is_email_verified",
            "mpp_code",
        )
        export_order = fields
        # Optional:
        # skip_unchanged = True
        # report_skipped = False

    def dehydrate_department_display(self, obj):
        return obj.get_department_display() or "-"

    def dehydrate_full_contact(self, obj):
        return obj.full_contact_info()
