from import_export import resources
from .models import SahayakIncentives, UserDevice
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import SahayakIncentives
from django.contrib.auth import get_user_model

User = get_user_model()


class SahayakIncentivesResource(resources.ModelResource):
    # Explicitly map file column → model field
    user = fields.Field(
        column_name="Username",
        attribute="user",
        widget=ForeignKeyWidget(User, "username"),
    )
    mcc_code = fields.Field(column_name="MCC Code", attribute="mcc_code")
    mcc_name = fields.Field(column_name="MCC Name", attribute="mcc_name")
    mpp_code = fields.Field(column_name="MPP Code", attribute="mpp_code")
    mpp_name = fields.Field(column_name="MPP Name", attribute="mpp_name")
    month = fields.Field(column_name="Month", attribute="month")
    year = fields.Field(column_name="Year", attribute="year")
    opening = fields.Field(column_name="Opening", attribute="opening")
    milk_qty = fields.Field(column_name="Milk Qty", attribute="milk_qty")
    tds = fields.Field(column_name="TDS Rate", attribute="tds")
    tds_amt = fields.Field(column_name="TDS Amount", attribute="tds_amt")
    cda_recovery = fields.Field(column_name="CDA Recovery", attribute="cda_recovery")
    transporter_recovery = fields.Field(
        column_name="Transporter Recovery", attribute="transporter_recovery"
    )
    recovery_deposited = fields.Field(
        column_name="Recovery Deposited", attribute="recovery_deposited"
    )
    asset_recovery = fields.Field(
        column_name="Asset Recovery", attribute="asset_recovery"
    )
    milk_incentive = fields.Field(
        column_name=" Incentive Earned", attribute="milk_incentive"
    )
    milk_incentive_payable = fields.Field(
        column_name="Incentive Payable", attribute="milk_incentive_payable"
    )
    cf_incentive = fields.Field(column_name="CF Incentive", attribute="cf_incentive")
    mm_incentive = fields.Field(column_name="MM Incentive", attribute="mm_incentive")
    payable = fields.Field(column_name="Paid", attribute="payable")
    closing = fields.Field(column_name="Closing", attribute="closing")
    additional_data = fields.Field(
        column_name="Additional Data", attribute="additional_data"
    )

    def import_row(self, row, instance_loader, **kwargs):
        # Check for missing 'user' value
        user_value = str(row.get("Username", "")).strip()
        if not user_value:
            raise ValueError(f"Missing 'Username' value for row: {row}")

        # Ensure 'user' matches an existing username in the database
        if not User.objects.filter(username=user_value).exists():
            raise ValueError(
                f"Invalid 'Username' value: {user_value} - No matching User found."
            )

        return super().import_row(row, instance_loader, **kwargs)

    class Meta:
        model = SahayakIncentives
        import_id_fields = ("user", "month", "year")
        exclude = ("id",)


from django.contrib.auth.hashers import make_password


class UserResource(resources.ModelResource):
    # Explicit column mappings
    username = fields.Field(column_name="Username", attribute="username")
    first_name = fields.Field(column_name="First Name", attribute="first_name")
    last_name = fields.Field(column_name="Last Name", attribute="last_name")
    password = fields.Field(column_name="Password", attribute="password")

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "password")
        import_id_fields = ("username",)
        exclude = ("id",)

    def before_import_row(self, row, **kwargs):
        raw_password = row.get("Password")  # match column_name
        if raw_password and not raw_password.startswith("pbkdf2_"):
            row["Password"] = make_password(raw_password)


class UserDeviceResource(resources.ModelResource):
    user = fields.Field(
        column_name="user", attribute="user", widget=ForeignKeyWidget(User, "username")
    )

    class Meta:
        model = UserDevice
        fields = ("user", "mpp_code", "module", "device")
        exclude = ("id",)
        import_id_fields = ("user",)
