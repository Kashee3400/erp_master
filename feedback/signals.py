import logging
from django.dispatch import receiver
from django.conf import settings
from .models import Feedback
from django.db.models.signals import pre_save, post_save
from notifications.fcm import _send_device_specific_notification

logger = logging.getLogger(__name__)
from .tasks import send_feedback_email


@receiver(pre_save, sender=Feedback)
def feedback_pre_save(sender, instance, **kwargs):
    if not instance.pk:
        return  # New object

    try:
        previous = Feedback.objects.get(pk=instance.pk)

        instance._assigned_to_changed = previous.assigned_to != instance.assigned_to
        instance._status_changed = previous.status != instance.status
        instance._old_status = previous.status
        instance._new_status = instance.status
    except Feedback.DoesNotExist:
        pass


@receiver(post_save, sender=Feedback)
def feedback_post_save(sender, instance, created, **kwargs):
    # Common FCM payload base
    base_payload = {
        "route": "feedback-details",
        "id": str(instance.pk),
        "customKey": "feedbackNotification",
        "is_subroute": True,
    }
    # -------------------------
    # 1. New Feedback Created
    # -------------------------
    if created:
        logger.info(f"[Feedback] New feedback created: {instance.feedback_id}")

        # Email to support/admin
        send_feedback_email.delay(
            subject=f"New Feedback Submitted: {instance.feedback_id}",
            message=f"Feedback by {instance.sender} has been created with status: {instance.status}.",
            recipient_list=[settings.SUPPORT_TEAM_EMAIL],
        )

        # FCM to sender
        if hasattr(instance.sender, "device") and instance.sender.device:
            payload = base_payload.copy()
            payload["title"] = "New Feedback Submitted"
            payload["body"] = f"Thank you for your feedback (ID: {instance.feedback_id})"

            _send_device_specific_notification(
                instance.sender.device.device,
                data_payload=payload,
            )
        return

    # -------------------------
    # 2. Assignment Changed
    # -------------------------
    if getattr(instance, "_assigned_to_changed", False) and instance.assigned_to:
        logger.info(f"[Feedback] Reassigned to: {instance.assigned_to}")

        # Email to assigned user
        if instance.assigned_to.email:
            send_feedback_email.delay(
                subject=f"You have been assigned Feedback: {instance.feedback_id}",
                message=(
                    f"You've been assigned a new feedback.\n"
                    f"Priority: {instance.priority}, Status: {instance.status}."
                ),
                recipient_list=[instance.assigned_to.email],
            )

        # FCM to assigned user
        if hasattr(instance.assigned_to, "device") and instance.assigned_to.device:
            payload = base_payload.copy()
            payload["title"] = "New Feedback Assigned"
            # payload["route"] = "assigned-feedbacks"
            payload["body"] = f"ID: {instance.feedback_id}, Priority: {instance.priority}"

            _send_device_specific_notification(
                instance.assigned_to.device.device,
                data_payload=payload,
            )

    # -------------------------
    # 3. Status Changed
    # -------------------------
    if getattr(instance, "_status_changed", False):
        old_status = getattr(instance, "_old_status", "unknown")
        new_status = instance.status
        status_label = new_status.replace("_", " ").title()

        logger.info(
            f"[Feedback] Feedback {instance.feedback_id} status changed: {old_status} → {new_status}"
        )

        # Email to sender
        if instance.sender.email:
            send_feedback_email.delay(
                subject=f"Feedback {status_label}: {instance.feedback_id}",
                message=(
                    f"Your feedback has been marked as '{status_label}' "
                    f"by {instance.assigned_to or 'System'}."
                ),
                recipient_list=[instance.sender.email],
            )

        # FCM to sender
        if hasattr(instance.sender, "device") and instance.sender.device:
            payload = base_payload.copy()
            payload["title"] = f"Feedback {status_label}"
            payload["body"] = f"Your feedback ID {instance.feedback_id} is now '{status_label}'."
            _send_device_specific_notification(
                instance.sender.device.device,
                data_payload=payload,
            )
