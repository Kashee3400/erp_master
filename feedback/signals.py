import logging
from django.dispatch import receiver
from .models import Feedback, FeedbackComment
from django.db.models.signals import pre_save, post_save

logger = logging.getLogger(__name__)
from notifications.models import AppNotification, NotificationMedium, NotificationType


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
        return  # Skip if recipient is None or same as sender

    AppNotification.objects.create(
        sender=comment_user,
        recipient=recipient,
        title="New Feedback Message",
        body=instance.comment,
        message=instance.comment,
        model="feedback",
        object_id=feedback.pk,
        route="feedback-details",
        custom_key="feedbackNotification",
        is_subroute=True,
        allowed_email=True,
        notification_type=NotificationType.INFO,
        sent_via=NotificationMedium.SYSTEM,
    )


@receiver(post_save, sender=Feedback)
def feedback_post_save(sender, instance, created, **kwargs):
    # -------------------------
    # 1. New Feedback Created
    # -------------------------
    if created:
        logger.info(f"[Feedback] New feedback created: {instance.feedback_id}")

        AppNotification.objects.create(
            sender=instance.sender,
            recipient=instance.sender,
            title="New Feedback Submitted",
            body=f"Thank you for your feedback (ID: {instance.feedback_id})",
            message=f"Feedback by {instance.sender.get_full_name() or instance.sender.username} has been created with status: {instance.status}.",
            model="feedback",
            object_id=instance.pk,
            route="feedback-details",
            custom_key="feedbackNotification",
            is_subroute=True,
            allowed_email=True,
            notification_type=NotificationType.INFO,
            sent_via=NotificationMedium.SYSTEM,
        )
        return

    # -------------------------
    # 2. Assignment Changed
    # -------------------------
    if getattr(instance, "_assigned_to_changed", False) and instance.assigned_to:
        logger.info(f"[Feedback] Reassigned to: {instance.assigned_to}")

        AppNotification.objects.create(
            sender=instance.sender,
            recipient=instance.assigned_to,
            title="New Feedback Assigned",
            body=f"{instance.sender.get_full_name()} Assigned you a feedback({instance.feedback_id}), Priority: {instance.priority}",
            message=(
                f"You've been assigned a new feedback.\n"
                f"By: {instance.sender.get_full_name()}.\n"
                if instance.sender
                else "" f"Priority: {instance.priority}, Status: {instance.status}."
            ),
            model="feedback",
            object_id=instance.pk,
            route="feedback-details",
            custom_key="feedbackNotification",
            is_subroute=True,
            notification_type=NotificationType.INFO,
            sent_via=NotificationMedium.SYSTEM,
            allowed_email=True,
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

        AppNotification.objects.create(
            sender=instance.assigned_to or None,
            recipient=instance.sender,
            title=f"Feedback {status_label}",
            body=f"Your feedback ID {instance.feedback_id} is now '{status_label}'.",
            message=(
                f"Your feedback has been '{status_label}' "
            ),
            model="feedback",
            object_id=instance.pk,
            route="feedback-details",
            custom_key="feedbackNotification",
            is_subroute=True,
            notification_type=NotificationType.INFO,
            sent_via=NotificationMedium.SYSTEM,
            allowed_email=True,
        )
