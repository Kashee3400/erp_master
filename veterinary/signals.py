# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models.case_models import CaseEntry, CaseReceiverLog
from django.utils.translation import gettext_lazy as _
from facilitator.models.user_profile_model import UserLocation
from notifications.notification_service import NotificationServices


@receiver(post_save, sender=CaseEntry)
def create_receiver_log_on_case_entry(sender, instance, created, **kwargs):
    """
    Create an initial CaseReceiverLog when a CaseEntry is created,
    and notify all users linked to the same MCC/MPP location.
    """
    if created and instance.created_by:
        CaseReceiverLog.objects.create(
            case_entry=instance,
            assigned_from=None,
            assigned_to=instance.created_by,
            remarks=_("Initial assignment on case creation."),
        )
        mcc_code = None
        mpp_code = None

        if instance.cattle and instance.cattle.owner:
            mcc_code = instance.cattle.owner.mcc_code
            mpp_code = instance.cattle.owner.mpp_code
        elif instance.non_member_cattle and instance.non_member_cattle.non_member:
            mcc_code = instance.non_member_cattle.non_member.mcc_code
            mpp_code = instance.non_member_cattle.non_member.mpp_code

        if mcc_code:
            users_in_same_mcc = (
                UserLocation.objects.filter(mcc_code=mcc_code)
                .select_related("user")
                .values_list("user", flat=True)
            )
            NotificationServices().create_bulk_notifications(
                template_name="case_entry_update_en",
                recipients=users_in_same_mcc,
                context_factory={
                    "case": instance,
                    "site_name": "Kashee Pasu Sewa",
                },
            )
