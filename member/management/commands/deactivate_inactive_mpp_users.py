import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from facilitator.models.user_profile_model import UserProfile
from member.models import UserDevice
import pandas as pd
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Deactivate Users, UserProfiles and delete UserDevices based on MPP Ex Codes from Excel"

    def add_arguments(self, parser):
        parser.add_argument("excel_path", type=str, help="Path to Excel file")

    @transaction.atomic
    def handle(self, *args, **options):
        excel_path = options["excel_path"]
        self.stdout.write(self.style.WARNING(f"Reading Excel: {excel_path}"))

        df = pd.read_excel(excel_path)

        if "MPP Ex Code" not in df.columns:
            raise ValueError("Excel must contain 'MPP Ex Code' column")

        # Clean codes
        mpp_codes = df["MPP Ex Code"].astype(str).str.strip().dropna().unique()

        self.stdout.write(self.style.WARNING(f"MPP Codes cleaned: {len(mpp_codes)}"))

        # ===============================
        # FETCH USERS BY PROFILE MPP CODE
        # ===============================
        affected_profiles = UserProfile.objects.filter(mpp_code__in=mpp_codes)
        user_ids = list(affected_profiles.values_list("user_id", flat=True))

        # ===============================
        # UPDATE USER RECORDS
        # ===============================
        user_count = User.objects.filter(id__in=user_ids).update(is_active=False)

        # ===============================
        # UPDATE USER PROFILE
        # ===============================
        profile_count = affected_profiles.update(is_verified=False)

        # ===============================
        # DELETE DEVICES
        # ===============================
        device_count, _ = UserDevice.objects.filter(mpp_code__in=mpp_codes).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Deactivated {user_count} users, "
                f"updated {profile_count} profiles, "
                f"deleted {device_count} devices."
            )
        )


# "C:\Users\Divyanshu\Downloads\mpp inactive list ballia.xlsx"
