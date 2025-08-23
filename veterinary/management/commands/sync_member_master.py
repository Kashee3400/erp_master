from django.core.management.base import BaseCommand
from django.db import transaction
from erp_app.models import MemberHierarchyView
from veterinary.models.models import MembersMasterCopy
from django.contrib.auth import get_user_model
from ...utils.sync_model_util import sync_model

User = get_user_model()


class Command(BaseCommand):
    help = "Syncs member data from MSSQL (MemberHierarchyView) to PostgreSQL (MembersMasterCopy)"

    def handle(self, *args, **options):
        self.stdout.write("Fetching records from MSSQL...")
        source_members = MemberHierarchyView.objects.using("sarthak_kashee").all()

        self.stdout.write("Indexing users by username (mobile_no)...")
        user_lookup = {
            user.username: user
            for user in User.objects.filter(username__isnull=False).only("id", "username")
        }

        def key_fn(member):
            return member.member_code

        def map_fn(member):
            return MembersMasterCopy(
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
                user=user_lookup.get(member.mobile_no),
            )

        update_fields = [
            'company_code', 'plant_code', 'mcc_code', 'bmc_code', 'mpp_code',
            'member_tr_code', 'member_name', 'member_middle_name', 'member_surname',
            'gender', 'mobile_no', 'member_type', 'caste_category', 'birth_date',
            'age', 'is_active', 'wef_date', 'is_default', 'created_at',
            'folio_no', 'application_date', 'application_no', 'created_by',
            'member_master_relation', 'ex_member_code', 'device_id', 'user'
        ]

        created, updated = sync_model(
            model=MembersMasterCopy,
            source_objects=source_members,
            key_fn=key_fn,
            map_fn=map_fn,
            update_fields=update_fields,
            batch_size=500,
            key_field="member_code",
        )

        self.stdout.write(self.style.SUCCESS(
            f"✅ Sync completed successfully: Created={created}, Updated={updated}"
        ))
