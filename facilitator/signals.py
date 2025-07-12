import logging
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models.user_profile_model import UserProfile
from .models.facilitator_model import AssignedMppToFacilitator
from notifications.models import AppNotification, NotificationMedium, NotificationType
from import_export.signals import post_import
from .utils.import_flag import set_importing,is_importing
from facilitator.models.file_models import  UploadedFile, FileActionLog


User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_import)
def clear_import_flag(sender, **kwargs):
    set_importing(False)


@receiver(post_save, sender=AssignedMppToFacilitator)
def mpp_post_save(sender, instance, created, **kwargs):
    if is_importing():
        return  # Skip during import

    title = "New MPP Created" if created else "MPP Updated"
    AppNotification.objects.create(
        recipient=instance.sahayak,
        title=title,
        body=f"{'Assigned' if created else 'Updated'} MPP: {instance.mpp_name} ({instance.mpp_ex_code})",
        message=f"You have been {'assigned' if created else 'updated with'} a MPP.\n"
        f"MPP: {instance.mpp_name} ({instance.mpp_ex_code})",
        model="mpp",
        object_id=instance.pk,
        route="mpps-list",
        custom_key="mppNotification",
        is_subroute=True,
        notification_type=NotificationType.INFO,
        sent_via=NotificationMedium.SYSTEM,
    )

@receiver(post_save, sender=UploadedFile)
def log_file_upload(sender, instance, created, **kwargs):
    if created:
        FileActionLog.objects.create(
            uploaded_file=instance,
            action='uploaded',
            performed_by=instance.uploaded_by,
            ip_address=instance.ip_address,
        )

@receiver(post_delete, sender=UploadedFile)
def log_file_delete(sender, instance, **kwargs):
    FileActionLog.objects.create(
        uploaded_file=instance,
        action='deleted',
        performed_by=instance.uploaded_by,
        ip_address=instance.ip_address,
    )
