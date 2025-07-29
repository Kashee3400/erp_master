from django.core.management.base import BaseCommand
from django.db import transaction
from erp_app.models import MemberHierarchyView
from veterinary.models.models import MembersMasterCopy
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Syncs member data from MSSQL (MemberHierarchyView) to PostgreSQL (MemberMaster)"

    def handle(self, *args, **options):
        print("Fetching records from MSSQL...")
        # Use the 'sarthak_kashee' DB to read from MSSQL
        source_members = MemberHierarchyView.objects.using('sarthak_kashee').all()
        member_master_list = []
        member_codes = []
        # Step 1: Build a user lookup dictionary
        print("Indexing users by username (mobile_no)...")
        user_lookup = {
            user.username: user
            for user in User.objects.filter(username__isnull=False).only('id', 'username')
        }
        # Step 2: In your member mapping loop
        for member in source_members:
            matched_user = user_lookup.get(member.mobile_no)
            member_master_list.append(MembersMasterCopy(
                member_code=member.member_code,
                company_code=member.company_code,
                plant_code=member.plant_code,
                mcc_code=member.mcc_code,
                bmc_code=member.bmc_code,
                mpp_code=member.mpp_code,
                member_tr_code=member.member_tr_code,
                member_name=member.member_name,
                member_middle_name=member.member_middle_name,
                member_surname=member.member_surname,
                gender=member.gender,
                mobile_no=member.mobile_no,
                member_type=member.member_type,
                caste_category=member.caste_category,
                birth_date=member.birth_date,
                age=member.age,
                is_active=member.is_active,
                wef_date=member.wef_date,
                is_default=member.is_default,
                created_at=member.created_at,
                folio_no=member.folio_no,
                application_date=member.application_date,
                application_no=member.application_no,
                created_by=member.created_by,
                member_master_relation=member.member_master_relation,
                ex_member_code=member.ex_member_code,
                device_id=member.device_id,
                user=matched_user
            ))

        # Fetch existing codes to perform upsert
        existing_members = MembersMasterCopy.objects.filter(member_code__in=member_codes)
        existing_codes = set(existing_members.values_list("member_code", flat=True))

        to_update = []
        to_create = []

        for member in member_master_list:
            if member.member_code in existing_codes:
                to_update.append(member)
            else:
                to_create.append(member)

        print(f"Creating {len(to_create)} new members.")
        print(f"Updating {len(to_update)} existing members.")

        with transaction.atomic(using='default'):
            if to_create:
                MembersMasterCopy.objects.bulk_create(to_create, batch_size=500)

            if to_update:
                # bulk update fields (if Django >= 3.2+)
                fields = [
                    'company_code', 'plant_code', 'mcc_code', 'bmc_code', 'mpp_code',
                    'member_tr_code', 'member_name', 'member_middle_name', 'member_surname',
                    'gender', 'mobile_no', 'member_type', 'caste_category', 'birth_date',
                    'age', 'is_active', 'wef_date', 'is_default', 'created_at',
                    'folio_no', 'application_date', 'application_no', 'created_by',
                    'member_master_relation', 'ex_member_code', 'device_id'
                ]
                MembersMasterCopy.objects.bulk_update(to_update, fields, batch_size=500)

        print("Sync completed successfully.")
