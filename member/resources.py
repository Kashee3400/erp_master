from import_export import resources
from .models import SahayakIncentives, UserDevice
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import SahayakIncentives
from django.contrib.auth import get_user_model

User = get_user_model()


class SahayakIncentivesResource(resources.ModelResource):
    user = fields.Field(
        column_name="user", attribute="user", widget=ForeignKeyWidget(User, "username")
    )

    def import_row(self, row, instance_loader, **kwargs):
        # Check for missing 'user' value
        user_value = str(row.get("user", "")).strip()
        if not user_value:
            raise ValueError(f"Missing 'user' value for row: {row}")

        # Ensure 'user' matches an existing username in the database
        if not User.objects.filter(username=user_value).exists():
            raise ValueError(
                f"Invalid 'user' value: {user_value} - No matching User found."
            )

        return super().import_row(row, instance_loader, **kwargs)

    class Meta:
        model = SahayakIncentives
        fields = (
            "user",
            "mcc_code",
            "mcc_name",
            "mpp_code",
            "mpp_name",
            "month",
            "year",
            "opening",
            "milk_qty",
            "milk_incentive",
            "tds",
            "tds_amt",
            "cf_incentive",
            "mm_incentive",
            "cda_recovery",
            "asset_recovery",
            "milk_incentive_payable",
            "payable",
            "closing",
        )
        exclude = ("id",)
        import_id_fields = ("user", "month")


from django.contrib.auth.hashers import make_password
class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "password")
        import_id_fields = ("username",)
        exclude = ("id",)

    def before_import_row(self, row, **kwargs):
        raw_password = row.get("password")
        if raw_password and not raw_password.startswith("pbkdf2_"):
            row["password"] = make_password(raw_password)


class UserDeviceResource(resources.ModelResource):
    user = fields.Field(
        column_name="user", attribute="user", widget=ForeignKeyWidget(User, "username")
    )

    class Meta:
        model = UserDevice
        fields = ("user", "mpp_code", "module")
        exclude = ("id",)
        import_id_fields = ("user",)
