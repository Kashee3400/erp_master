import logging
from django.dispatch import receiver
from .model import AppNotification,Notification
from django.db.models.signals import pre_save, post_save
logger = logging.getLogger(__name__)

from .notification_service import NotificationService,NotificationServices

@receiver(post_save, sender=AppNotification)
def notification_post_save(sender, instance, created, **kwargs):
    if created:
        logger.info(f"[Notification] New notification created: {instance.pk}")
        NotificationService.notify_instance_created(instance)

