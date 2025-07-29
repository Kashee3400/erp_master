# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models.case_models import CaseEntry, CaseReceiverLog
from django.utils.translation import gettext_lazy as _


@receiver(post_save, sender=CaseEntry)
def create_receiver_log_on_case_entry(sender, instance, created, **kwargs):
    if created and instance.applied_by:
        CaseReceiverLog.objects.create(
            case_entry=instance,
            from_user=None,  # No one previously handled the case
            to_user=instance.applied_by,
            remarks=_("Initial assignment on case creation."),
        )
