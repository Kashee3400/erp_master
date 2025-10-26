import logging
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models.user_profile_model import UserProfile
from .models.facilitator_model import AssignedMppToFacilitator
from notifications.model import NotificationMedium, NotificationType
from import_export.signals import post_import
from .utils.import_flag import set_importing, is_importing
from facilitator.models.file_models import UploadedFile, FileActionLog
from .models.member_update_model import (
    UpdateRequestHistory,
    UpdateRequestDocument,
    UpdateRequest,
    ChangeType,
    UpdateRequestData,
)
import json


User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_import)
def clear_import_flag(sender, **kwargs):
    set_importing(False)


# @receiver(post_save, sender=AssignedMppToFacilitator)
# def mpp_post_save(sender, instance, created, **kwargs):
#     if is_importing():
#         return  # Skip during import

#     title = "New MPP Created" if created else "MPP Updated"
#     AppNotification.objects.create(
#         recipient=instance.sahayak,
#         title=title,
#         body=f"{'Assigned' if created else 'Updated'} MPP: {instance.mpp_name} ({instance.mpp_ex_code})",
#         message=f"You have been {'assigned' if created else 'updated with'} a MPP.\n"
#         f"MPP: {instance.mpp_name} ({instance.mpp_ex_code})",
#         model="mpp",
#         object_id=instance.pk,
#         route="mpps-list",
#         custom_key="mppNotification",
#         is_subroute=True,
#         notification_type=NotificationType.INFO,
#         sent_via=NotificationMedium.SYSTEM,
#     )


@receiver(post_save, sender=UploadedFile)
def log_file_upload(sender, instance, created, **kwargs):
    if created:
        FileActionLog.objects.create(
            uploaded_file=instance,
            action="uploaded",
            performed_by=instance.uploaded_by,
            ip_address=instance.ip_address,
        )


@receiver(post_delete, sender=UploadedFile)
def log_file_delete(sender, instance, **kwargs):
    FileActionLog.objects.create(
        uploaded_file=instance,
        action="deleted",
        performed_by=instance.uploaded_by,
        ip_address=instance.ip_address,
    )


@receiver(pre_save, sender=UpdateRequest)
def capture_update_request_changes(sender, instance, **kwargs):
    """Capture changes before saving UpdateRequest"""
    if instance.pk:
        try:
            old_instance = UpdateRequest.objects.get(pk=instance.pk)
            instance._old_instance = old_instance
        except UpdateRequest.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


import json
from django.utils.encoding import force_str


@receiver(post_save, sender=UpdateRequest)
def log_update_request_changes(sender, instance, created, **kwargs):
    """Log changes after saving UpdateRequest"""

    # Get the user from the current context, fallback to updated_by or created_by
    user = getattr(instance, "_current_user", None)
    from django.contrib.auth.models import AnonymousUser
    if not user or isinstance(user, AnonymousUser):
        user = instance.updated_by or instance.created_by

    if created:
        # Log creation
        UpdateRequestHistory.objects.create(
            request=instance,
            change_type=ChangeType.CREATE,
            changed_by=user,
            new_value=json.dumps(
                {
                    "member_code": instance.member_code,
                    "member_name": instance.member_name,
                    "request_type": force_str(instance.request_type),
                    "status": force_str(instance.status),
                }
            ),
            change_reason="Request created",
            metadata={
                "created_by": (
                    instance.created_by.username if instance.created_by else None
                ),
                "request_type": force_str(instance.request_type),
            },
        )
    else:
        # Log updates
        old_instance = getattr(instance, "_old_instance", None)
        if old_instance:
            fields_to_track = [
                "status",
                "ho_comments",
                "rejection_reason",
                "reviewed_by",
                "reviewed_at",
            ]

            for field in fields_to_track:
                old_value = getattr(old_instance, field, None)
                new_value = getattr(instance, field, None)

                if old_value != new_value:
                    # Handle FK values like reviewed_by
                    if field == "reviewed_by":
                        old_value = old_value.username if old_value else None
                        new_value = new_value.username if new_value else None

                    UpdateRequestHistory.objects.create(
                        request=instance,
                        change_type=ChangeType.UPDATE,
                        field_name=field,
                        old_value=str(old_value) if old_value else None,
                        new_value=str(new_value) if new_value else None,
                        changed_by=user,
                        change_reason=f"Field '{field}' updated",
                        metadata={
                            "field_verbose_name": str(
                                instance._meta.get_field(field).verbose_name
                            ),
                        },
                    )

            # Explicit status change log (if status changed)
            if old_instance.status != instance.status:
                UpdateRequestHistory.objects.create(
                    request=instance,
                    change_type=ChangeType.STATUS_CHANGE,
                    field_name="status",
                    old_value=force_str(old_instance.get_status_display()),
                    new_value=force_str(instance.get_status_display()),
                    changed_by=user,
                    change_reason=f"Status changed from {force_str(old_instance.get_status_display())} to {force_str(instance.get_status_display())}",
                    metadata={
                        "old_status_code": old_instance.status,
                        "new_status_code": instance.status,
                        "reviewer": (
                            instance.reviewed_by.username
                            if instance.reviewed_by
                            else None
                        ),
                    },
                )


@receiver(post_save, sender=UpdateRequestData)
def log_request_data_changes(sender, instance, created, **kwargs):
    """Log changes to request data"""
    user = getattr(instance, "_current_user", None) or instance.created_by
    if created:
        UpdateRequestHistory.objects.create(
            request=instance.request,
            change_type=ChangeType.CREATE,
            field_name=f"data_{instance.field_name}",
            new_value=instance.new_value,
            changed_by=user,
            change_reason=f"Added data field: {instance.field_name}",
            metadata={
                "data_type": instance.data_type,
                "field_name": instance.field_name,
            },
        )


@receiver(post_save, sender=UpdateRequestDocument)
def log_document_changes(sender, instance, created, **kwargs):
    """Log document uploads"""
    user = getattr(instance, "_current_user", None) or instance.created_by
    print(f"User: {user}")
    if created:
        UpdateRequestHistory.objects.create(
            request=instance.request,
            change_type=ChangeType.CREATE,
            field_name=f"document_{instance.document_type}",
            new_value=instance.original_filename,
            changed_by=user,
            change_reason=f"Uploaded document: {instance.get_document_type_display()}",
            metadata={
                "document_type": instance.document_type,
                "file_size": instance.file_size,
                "content_type": instance.content_type,
            },
        )
