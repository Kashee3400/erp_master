from django.db.transaction import on_commit
from ..models.case_models import CaseReceiverLog
from notifications.notification_service import NotificationServices
from facilitator.models.user_profile_model import UserLocation


class CaseEntryService:

    @staticmethod
    def handle_case_creation(case_entry, created_by):
        """
        Handles:
        - CaseReceiverLog creation
        - MCC → notification fanout
        """

        def _after_commit():

            # -----------------------------------------
            # 1) Create CaseReceiverLog
            # -----------------------------------------
            CaseReceiverLog.objects.create(
                case_entry=case_entry,
                assigned_from=None,
                assigned_to=created_by,
                remarks="Initial assignment on case creation.",
            )

            # -----------------------------------------
            # 2) Determine MCC code from cattle or non-member cattle
            # -----------------------------------------
            mcc_code = None

            if case_entry.cattle and case_entry.cattle.owner:
                mcc_code = case_entry.cattle.owner.mcc_code

            elif (
                case_entry.non_member_cattle and case_entry.non_member_cattle.non_member
            ):
                mcc_code = case_entry.non_member_cattle.non_member.mcc_code

            if not mcc_code:
                return

            # -----------------------------------------
            # 3) Find all users in that MCC
            # -----------------------------------------
            users_in_same_mcc = (
                UserLocation.objects.filter(mcc_code=mcc_code)
                .select_related("user")
                .values_list("user", flat=True)
            )

            # -----------------------------------------
            # 4) Send notifications
            # -----------------------------------------
            NotificationServices().create_bulk_notifications(
                template_name="case_entry_update_en",
                recipients=users_in_same_mcc,
                app_host="pes",
                context_factory=lambda recipient, index: {
                    "case": case_entry,
                    "site_name": "Kashee Pasu Sewa",
                    "recipient_id": recipient,
                },
            )

        # Ensure logic runs only after transaction commits
        on_commit(_after_commit)
