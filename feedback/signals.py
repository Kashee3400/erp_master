import logging
from django.dispatch import receiver
from .models import Feedback, FeedbackComment
from django.db.models.signals import pre_save, post_save
from django.contrib.auth import get_user_model
import logging
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


from notifications.model import (
    Notification,
    NotificationTemplate,
    NotificationStatus,
)

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

    template = NotificationTemplate.objects.filter(name="feedback_update_hi").last()
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
    collection_ct = ContentType.objects.get_for_model(Feedback)

    render_context = {
        "recipient": recipient,
        "feedback": feedback,
        "site_name": "Kashee E-Dairy",
    }

    # Render content using the template model
    rendered = template.render_content(render_context)

    Notification.objects.create(
        sender=comment_user,
        template=template,
        recipient=recipient,
        delivery_status={"status": NotificationStatus.PENDING},
        channels=["push"],
        app_route="feedback-details",
        custom_key=f"feedback_{feedback.pk}",
        is_subroute=True,
        deep_link_url=template.generate_deep_link(context=render_context),
        title=rendered.get("title", ""),
        body=rendered.get("body", ""),
        email_subject=rendered.get("email_subject", ""),
        email_body=rendered.get("email_body"),
        content_type=collection_ct,
        object_id=feedback.pk,
        context_data={},
        status=NotificationStatus.PENDING,
    )


from notifications.tasks import deliver_notification


def create_feedback_notification(
    *,
    recipient,
    sender=None,
    template_name,
    feedback,
    context_extra=None,
    app_route=None,
    custom_key=None,
    title_default="",
    body_default="",
):
    """Common helper to render and create feedback notifications."""
    template = NotificationTemplate.objects.filter(name=template_name).last()
    if not template:
        logger.warning(f"[Feedback] Template '{template_name}' not found.")
        return None

    # safe JSON context
    context_data = {
        "recipient_id": recipient.id if recipient else None,
        "feedback_id": feedback.feedback_id,
        "feedback_status": feedback.status,
        "site_name": "Kashee E-Dairy",
    }
    if context_extra:
        context_data.update(context_extra)
    
    render_context = {
        "recipient": recipient,
        "feedback": feedback,
        "site_name": "Kashee E-Dairy",
    }
    rendered = template.render_content(render_context)

    notification = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        template=template,
        delivery_status={"status": NotificationStatus.PENDING},
        channels=["push"],
        app_route=app_route or f"feedback-details",
        custom_key=custom_key,
        is_subroute=True,
        deep_link_url=template.generate_deep_link(context=render_context),
        title=rendered.get("title", title_default),
        body=rendered.get("body", body_default),
        email_subject=rendered.get("email_subject", ""),
        email_body=rendered.get("email_body", ""),
        content_type=ContentType.objects.get_for_model(feedback),
        object_id=feedback.pk,
        context_data=context_data,
        status=NotificationStatus.PENDING,
    )

    deliver_notification.delay(notification.uuid)
    return notification


@receiver(post_save, sender=Feedback)
def feedback_post_save(sender, instance, created, **kwargs):
    """Unified feedback notification handler."""

    # --- 1. New Feedback Created ---
    if created:
        logger.info(f"[Feedback] New feedback created: {instance.feedback_id}")
        create_feedback_notification(
            recipient=instance.sender,
            template_name="feedback_update_hi",
            feedback=instance,
            custom_key=f"feedback_{instance.pk}",
            app_route="feedback-details",
        )
        return

    # --- 2. Assignment Changed ---
    if getattr(instance, "_assigned_to_changed", False) and instance.assigned_to:
        logger.info(f"[Feedback] Reassigned to: {instance.assigned_to}")
        create_feedback_notification(
            recipient=instance.assigned_to,
            sender=instance.sender,
            template_name="feedback_update_hi",
            feedback=instance,
            custom_key=f"feedback_assigned_{instance.pk}",
            app_route="feedback-details",
            context_extra={
                "assigner_id": instance.sender_id,
                "priority": instance.priority,
            },
            title_default="New Feedback Assigned",
            body_default=f"{instance.sender.get_full_name()} assigned you feedback ({instance.feedback_id}), Priority: {instance.priority}",
        )

    # --- 3. Status Changed ---
    if getattr(instance, "_status_changed", False):
        old_status = getattr(instance, "_old_status", "unknown")
        new_status = instance.status
        status_label = new_status.replace("_", " ").title()

        logger.info(
            f"[Feedback] Feedback {instance.feedback_id} status changed: {old_status} → {new_status}"
        )

        create_feedback_notification(
            recipient=instance.sender,
            sender=instance.assigned_to,
            template_name="feedback_status_change_hi",
            feedback=instance,
            custom_key=f"feedback_status_{instance.pk}",
            app_route="feedback-details",
            context_extra={
                "old_status": old_status,
                "new_status": new_status,
            },
            title_default=f"Feedback {status_label}",
            body_default=f"Your feedback ID {instance.feedback_id} is now '{status_label}'.",
        )
