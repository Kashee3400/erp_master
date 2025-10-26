import logging
from django.dispatch import receiver

logger = logging.getLogger(__name__)
from django.db.models.signals import post_save, pre_save, m2m_changed
from django.dispatch import receiver
from django.utils import timezone
import logging

from .model import (
    Notification,
    NotificationStatus,
    NotificationGroup,
)
from .tasks import deliver_notification


@receiver(pre_save, sender=Notification)
def notification_pre_save(sender, instance, **kwargs):
    """
    Signal triggered BEFORE notification is saved
    Use for validation and data preprocessing
    """
    try:
        # Set default status if not provided
        if not instance.status:
            instance.status = NotificationStatus.PENDING

        # Set created timestamp if new
        if not instance.id:
            instance.created_at = timezone.now()

        # Validate channels
        if instance.channels and not isinstance(instance.channels, list):
            instance.channels = [instance.channels]

        # Ensure priority is set
        if not instance.priority:
            instance.priority = (
                instance.template.default_priority if instance.template else "normal"
            )

        logger.debug(f"Pre-save validation for notification: {instance.uuid}")

    except Exception as e:
        print(e)
        logger.error(f"Error in notification_pre_save: {e}")


@receiver(post_save, sender=Notification)
def notification_post_save(sender, instance, created, **kwargs):
    """
    Signal triggered AFTER notification is saved
    Use for async tasks and external integrations

    Args:
        created: Boolean indicating if this is a new object
    """
    try:
        if created:
            logger.info(
                f"New notification created: {instance.uuid} for user {instance.recipient.email}"
            )
            deliver_notification.delay(instance.id)
            logger.info(f"Queued notification {instance.uuid} for immediate delivery")

        else:
            logger.debug(f"Notification updated: {instance.uuid}")
            if (
                instance.status == NotificationStatus.FAILED
                # and instance.retry_count
                # and instance.retry_count < 3
            ):
                logger.info(f"Notification {instance.uuid} marked for retry")

    except Exception as e:
        print(e)
        logger.error(f"Error in notification_post_save: {e}")


@receiver(post_save, sender=NotificationGroup)
def notification_group_post_save(sender, instance, created, **kwargs):
    """
    Signal for when a NotificationGroup is created
    Can be used to handle grouped notifications
    """
    try:
        if created:
            logger.info(
                f"New notification group created: {instance.id} - {instance.name}"
            )

            # Could trigger group-specific logic here
            # For example, consolidate similar notifications

    except Exception as e:
        logger.error(f"Error in notification_group_post_save: {e}")
