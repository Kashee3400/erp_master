# notifications/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging
from notifications.fcm import _send_device_specific_notification
from typing import Dict, Any
from django.utils import timezone
import logging


logger = logging.getLogger(__name__)

from .fcm import _send_device_specific_notification


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_feedback_email(self, subject, message, recipient_list):
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,  # Let errors raise for retry
        )
        logger.info(f"Sent feedback email to {recipient_list}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}, retrying...")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_fcm_notification_task(self, token, title, body, data=None):

    payload = {
        "to": token,
        "notification": {"title": title, "body": body},
        "data": data or {},
    }

    try:
        sent, info = _send_device_specific_notification(
            device_token=token, notification=payload
        )
        if not sent:
            raise Exception(f"FCM failed: {info}")
        return {"status": "sent", "info": info}
    except Exception as e:
        self.retry(exc=e)


from celery import shared_task
import subprocess
import platform


@shared_task
def scan_file_virus(file_path):
    try:
        if platform.system() == "Windows":
            result = subprocess.run(["clamscan.exe", file_path], stdout=subprocess.PIPE)
        else:
            result = subprocess.run(["clamscan", file_path], stdout=subprocess.PIPE)

        output = result.stdout.decode()
        if "Infected files: 0" in output:
            return "clean"
        return "infected"
    except Exception as e:
        return str(e)


@shared_task
def send_bulk_notifications_task(
    template_name: str, recipient_ids: list, context: Dict[str, Any] = None, **kwargs
):
    """
    Task for sending bulk notifications efficiently
    """
    try:
        # Import here to avoid circular imports
        from django.contrib.auth import get_user_model
        from .notification_service import NotificationServices

        User = get_user_model()
        service = NotificationServices()
        recipients = User.objects.filter(id__in=recipient_ids)
        notifications = []
        for recipient in recipients:
            try:
                notification = service.create_notification(
                    template_name=template_name,
                    recipient=recipient,
                    context=context or {},
                    **kwargs,
                )
                notifications.append(notification)
            except Exception as e:
                logger.error(
                    f"Failed to create notification for user {recipient.id}: {e}"
                )
                continue

        logger.info(f"Created {len(notifications)} bulk notifications")
        return f"Created {len(notifications)} notifications"

    except Exception as exc:
        logger.error(f"Bulk notification task failed: {exc}")
        raise


@shared_task
def schedule_notification_delivery_task(notification_id: int):
    """
    Task to handle scheduled notifications
    """
    try:
        # Import here to avoid circular imports
        from .model import Notification, NotificationStatus
        notification = Notification.objects.get(id=notification_id)
        # Check if it's time to send
        if notification.scheduled_at <= timezone.now():
            if notification.status == NotificationStatus.PENDING:
                notification.status = NotificationStatus.QUEUED
                notification.save(update_fields=["status"])

                # Queue for delivery
                deliver_notification.delay(notification.id)

                return f"Scheduled notification {notification.uuid} queued for delivery"

        return f"Notification {notification.uuid} not yet due for delivery"

    except Exception as exc:
        logger.error(f"Scheduled notification task failed: {exc}")
        raise


@shared_task
def retry_failed_notifications_task(hours_ago: int = 1):
    """
    Task to retry failed notifications
    """
    try:
        from .model import Notification, NotificationStatus

        cutoff_time = timezone.now() - timezone.timedelta(hours=hours_ago)
        failed_notifications = Notification.objects.filter(
            status=NotificationStatus.FAILED, updated_at__gte=cutoff_time
        )
        retry_count = 0
        for notification in failed_notifications:
            # Reset status and retry
            notification.status = NotificationStatus.QUEUED
            notification.save(update_fields=["status"])

            deliver_notification.delay(notification.id)
            retry_count += 1

        logger.info(f"Retrying {retry_count} failed notifications")
        return f"Retrying {retry_count} failed notifications"

    except Exception as exc:
        logger.error(f"Retry failed notifications task failed: {exc}")
        raise


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def deliver_notification(self, notification_id: int):
    """Celery task for delivering notifications"""
    try:
        from .model import Notification, NotificationStatus
        from .delivery import NotificationDeliveryService

        notification = Notification.objects.get(id=notification_id)
        if notification.status != NotificationStatus.QUEUED:
            logger.warning(f"Notification {notification.uuid} is not in queued state")
            return
        delivery_service = NotificationDeliveryService()
        delivery_service.deliver(notification)
    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")
    except Exception as exc:
        logger.error(f"Notification delivery failed: {exc}")
        raise self.retry(exc=exc)


@shared_task
def cleanup_expired_notifications():
    """Celery task for cleaning up expired notifications"""
    from .notification_service import NotificationServices

    service = NotificationServices()
    count = service.cleanup_expired()
    logger.info(f"Cleaned up {count} expired notifications")
