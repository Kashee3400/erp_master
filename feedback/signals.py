import logging
from django.dispatch import receiver
from .models import Feedback, FeedbackComment
from django.db.models.signals import pre_save, post_save
from django.contrib.auth import get_user_model
import logging

from notifications.notification_service import NotificationServices

User = get_user_model()
notification_service = NotificationServices()

logger = logging.getLogger(__name__)


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


@receiver(post_save, sender=FeedbackComment)
def feedback_comment_post_save(sender, instance, created, **kwargs):
    if not created:
        return

    feedback = instance.feedback
    comment_user = instance.user

    recipient = None

    # Determine recipient only if fields are not None
    if feedback.assigned_to and feedback.sender:
        if comment_user == feedback.assigned_to:
            recipient = feedback.sender
        elif comment_user == feedback.sender:
            recipient = feedback.assigned_to

    # Validate recipient
    if not recipient or recipient == comment_user:
        return

    context = {
        "feedback": feedback,
        "pk": feedback.id,
        "site_name": "Kashee E-Dairy",
    }

    notification_service.create_notification(
        template_name="feedback_update_hi",
        recipient=recipient,
        sender=comment_user,
        context=context,
        related_object=feedback,
        channels=["push"],
    )


@receiver(post_save, sender=Feedback)
def feedback_post_save(sender, instance, created, **kwargs):
    """Unified feedback notification handler."""

    # --- 1. New Feedback Created ---
    if created:
        logger.info(f"[Feedback] New feedback created: {instance.feedback_id}")

        context = {
            "feedback": instance,
            "pk": instance.id,
            "site_name": "Kashee E-Dairy",
        }

        notification_service.create_notification(
            template_name="feedback_update_hi",
            recipient=instance.sender,
            context=context,
            related_object=instance,
            channels=["push"],
        )
        return

    # --- 2. Assignment Changed ---
    if getattr(instance, "_assigned_to_changed", False) and instance.assigned_to:
        logger.info(f"[Feedback] Reassigned to: {instance.assigned_to}")

        context = {
            "feedback": instance,
            "pk": instance.id,
            "site_name": "Kashee E-Dairy",
            "assigner_id": instance.sender_id,
            "priority": instance.priority,
        }

        notification_service.create_notification(
            template_name="feedback_update_hi",
            recipient=instance.assigned_to,
            sender=instance.sender,
            context=context,
            related_object=instance,
            channels=["push"],
        )

    # --- 3. Status Changed ---
    if getattr(instance, "_status_changed", False):
        old_status = getattr(instance, "_old_status", "unknown")
        new_status = instance.status
        status_label = new_status.replace("_", " ").title()

        logger.info(
            f"[Feedback] Feedback {instance.feedback_id} status changed: {old_status} → {new_status}"
        )

        context = {
            "feedback": instance,
            "pk": instance.id,
            "site_name": "Kashee E-Dairy",
            "old_status": old_status,
            "new_status": new_status,
            "status_label": status_label,
        }

        notification_service.create_notification(
            template_name="feedback_status_change_hi",
            recipient=instance.sender,
            sender=instance.assigned_to,
            context=context,
            related_object=instance,
            channels=["push"],
        )
