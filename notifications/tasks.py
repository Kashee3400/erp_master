from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging
from django.utils import timezone
import subprocess
import platform
from .choices import NotificationStatus
from django.contrib.auth import get_user_model
import logging
from django.core.management import call_command

CHUNK_SIZE = 500

User = get_user_model()

logger = logging.getLogger(__name__)


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

@shared_task(bind=True, max_retries=3)
def process_mpp_collection_notifications(self):
    """
    Celery task to process MPP collection notifications.
    Runs the management command to create and send notifications.
    """
    try:
        logger.info("Starting MPP collection notification processing...")
        call_command('process_collection_notifications')
        logger.info("MPP collection notification processing completed successfully.")
        return "Success"
    except Exception as exc:
        logger.error(f"Error processing MPP collection notifications: {exc}")
        # Retry after 5 minutes if failed
        raise self.retry(exc=exc, countdown=300)

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
def deliver_notification(self, notification_id: str):
    """Celery task for delivering notifications"""
    logger.info(f"Recieved task with notification id ${notification_id}")
    try:
        from .model import Notification
        from .delivery import NotificationDeliveryService
        notification = Notification.objects.get(uuid=notification_id)
        delivery_service = NotificationDeliveryService()
        delivery_service.deliver(notification)
    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")
    except Exception as exc:
        logger.error(f"Notification delivery failed: {exc}")
        raise self.retry(exc=exc)


@shared_task
def cleanup_expired_notifications():
    """
    Periodic task to remove expired notifications
    Schedule with Celery Beat
    """
    from .notification_service import NotificationServices

    service = NotificationServices()
    count = service.cleanup_expired()

    logger.info(f"Cleanup task removed {count} expired notifications")
    return count


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def process_collections_batch(self, notification_ids: list[int]):
    """
    Main task: splits large batch into smaller Celery subtasks.
    """
    try:
        for start in range(0, len(notification_ids), CHUNK_SIZE): # 0 
            chunk_ids = notification_ids[start : start + CHUNK_SIZE]
            deliver_chunk.delay(chunk_ids)

        return {"scheduled_chunks": len(notification_ids) // CHUNK_SIZE + 1}

    except Exception as exc:
        logger.exception(f"🔥 Fatal error in main batch task: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def deliver_chunk(self, notification_ids: list[int]):
    """
    Delivers a chunk of notifications using parallel channel delivery.
    """
    from .model import Notification, NotificationStatus
    from .delivery import NotificationDeliveryService

    try:
        notifications_qs = (
            Notification.objects.filter(
                id__in=notification_ids,
                status__in=[NotificationStatus.PENDING, NotificationStatus.QUEUED],
            )
            .select_related("recipient")
            .only("id", "uuid", "recipient_id", "delivery_status", "channels", "status")
        )

        if not notifications_qs.exists():
            logger.warning("⚠️ No notifications to process in this chunk.")
            return {"processed": 0, "skipped": len(notification_ids)}

        notifications = list(notifications_qs)
        delivery_service = NotificationDeliveryService()
        processed_count = delivery_service.deliver_batch(notifications)

        logger.info(
            f"✅ Chunk delivered: {processed_count}/{len(notification_ids)} notifications processed."
        )
        return {"processed": processed_count}

    except Exception as exc:
        logger.exception(f"🔥 Error delivering chunk: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))

@shared_task(bind=True, max_retries=5)
def queue_notification_async(self, notification_id):
    """
    Task to handle notification queuing
    Separated from signal to avoid blocking the save operation
    """
    try:
        from .model import Notification

        notification = Notification.objects.get(id=notification_id)

        # Update status to QUEUED
        notification.status = NotificationStatus.QUEUED
        notification.queued_at = timezone.now()
        notification.save(update_fields=["status", "queued_at"])

        logger.info(f"Notification {notification.uuid} status set to QUEUED")

        from .delivery import NotificationDeliveryService

        notification = Notification.objects.get(id=notification_id)
        if notification.status != NotificationStatus.QUEUED:
            logger.warning(f"Notification {notification.uuid} is not in queued state")
            return
        delivery_service = NotificationDeliveryService()
        delivery_service.deliver(notification)
        logger.info(f"Notification {notification.uuid} delivery tasks queued")
        return True

    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")
        return False

    except Exception as exc:
        logger.error(f"Error queueing notification {notification_id}: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))
