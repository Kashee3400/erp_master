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
    NotificationMedium,
    NotificationType,
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
        app_route=f"/feedback/{feedback.pk}",
        custom_key=f"feedback_{feedback.pk}",
        is_subroute=True,
        title=rendered.get("title", ""),
        body=rendered.get("body", ""),
        email_subject=rendered.get("email_subject", ""),
        email_body=rendered.get("email_body"),
        content_type=collection_ct,
        object_id=feedback.pk,
        context_data={},
        status=NotificationStatus.PENDING,
    )


@receiver(post_save, sender=Feedback)
def feedback_post_save(sender, instance, created, **kwargs):
    collection_ct = ContentType.objects.get_for_model(Feedback)

    # -------------------------
    # 1. New Feedback Created
    # -------------------------
    if created:
        template = NotificationTemplate.objects.filter(name="feedback_update_hi").last()
        logger.info(f"[Feedback] New feedback created: {instance.feedback_id}")

        render_context = {
            "recipient": instance.sender,
            "feedback": instance,
            "site_name": "Kashee E-Dairy",
        }

        rendered = template.render_content(render_context)

        Notification.objects.create(
            recipient=instance.sender,
            template=template,
            delivery_status={"status": NotificationStatus.PENDING},
            channels=["push"],
            app_route=f"/feedback/{instance.pk}",
            custom_key=f"feedback_{instance.pk}",
            is_subroute=True,
            title=rendered.get("title", ""),
            body=rendered.get("body", ""),
            email_subject=rendered.get("email_subject", ""),
            email_body=rendered.get("email_body"),
            content_type=collection_ct,
            object_id=instance.pk,
            context_data=render_context,
            status=NotificationStatus.PENDING,
        )
        return

    # -------------------------
    # 2. Assignment Changed
    # -------------------------
    if getattr(instance, "_assigned_to_changed", False) and instance.assigned_to:
        logger.info(f"[Feedback] Reassigned to: {instance.assigned_to}")

        template = NotificationTemplate.objects.filter(name="feedback_update_hi").last()
        render_context = {
            "recipient": instance.assigned_to,
            "feedback": instance,
            "assigner": instance.sender,
            "site_name": "Kashee E-Dairy",
        }

        rendered = template.render_content(render_context)

        Notification.objects.create(
            recipient=instance.assigned_to,
            sender=instance.sender,
            template=template,
            delivery_status={"status": NotificationStatus.PENDING},
            channels=["push"],
            app_route=f"/feedback/{instance.pk}",
            custom_key=f"feedback_assigned_{instance.pk}",
            is_subroute=True,
            title=rendered.get("title", f"New Feedback Assigned"),
            body=rendered.get(
                "body",
                f"{instance.sender.get_full_name()} assigned you feedback ({instance.feedback_id}), Priority: {instance.priority}",
            ),
            email_subject=rendered.get("email_subject", ""),
            email_body=rendered.get("email_body", ""),
            content_type=collection_ct,
            object_id=instance.pk,
            context_data=render_context,
            status=NotificationStatus.PENDING,
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

        template = NotificationTemplate.objects.filter(name="feedback_status_change_hi").last()
        render_context = {
            "recipient": instance.sender,
            "feedback": instance,
            "old_status": old_status,
            "new_status": new_status,
            "site_name": "Kashee E-Dairy",
        }

        rendered = template.render_content(render_context)

        Notification.objects.create(
            recipient=instance.sender,
            sender=instance.assigned_to or None,
            template=template,
            delivery_status={"status": NotificationStatus.PENDING},
            channels=["push"],
            app_route=f"/feedback/{instance.pk}",
            custom_key=f"feedback_status_{instance.pk}",
            is_subroute=True,
            title=rendered.get("title", f"Feedback {status_label}"),
            body=rendered.get(
                "body", f"Your feedback ID {instance.feedback_id} is now '{status_label}'."
            ),
            email_subject=rendered.get("email_subject", ""),
            email_body=rendered.get("email_body", ""),
            content_type=collection_ct,
            object_id=instance.pk,
            context_data=render_context,
            status=NotificationStatus.PENDING,
        )
