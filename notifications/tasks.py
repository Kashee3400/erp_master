# notifications/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging
from notifications.fcm import _send_device_specific_notification
from typing import Dict, Any
from django.utils import timezone
import subprocess
import platform
from .choices import NotificationStatus, NotificationChannel
from django.contrib.auth import get_user_model
from django.db import transaction
import logging

logger = logging.getLogger(__name__)
CHUNK_SIZE = 500

User = get_user_model()

from .fcm import _send_device_specific_notification

logger = logging.getLogger(__name__)


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
        from .model import Notification, NotificationStatus
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
def create_notification_from_collection(
    self, collection_code, member_code, template_id
):
    """
    Create a notification for a specific collection
    Implements deduplication at task level
    """
    try:
        from .model import Notification, NotificationTemplate
        from erp_app.models import MppCollection
        from django.template import Template, Context

        # Fetch collection and template
        collection = MppCollection.objects.using("mssql").get(
            mpp_collection_code=collection_code
        )
        template = NotificationTemplate.objects.get(id=template_id)
        user = User.objects.get(username=member_code)

        # Double-check deduplication
        existing = Notification.objects.filter(
            template=template,
            recipient=user,
            context_data__collection_code=collection_code,
        ).first()

        if existing:
            logger.info(f"Notification already exists for {collection_code}")
            return True

        # Prepare rendering context
        context = Context(
            {
                "recipient": user,
                "collection": collection,
                "site_name": "Kashee E-Dairy",
            }
        )

        # Render the templates
        title = Template(template.title_template).render(context)
        body = Template(template.body_template).render(context)

        # Create notification
        notification = Notification.objects.create(
            template=template,
            recipient=user,
            title=title.strip(),
            body=body.strip(),
            context_data={
                "collection_code": collection.mpp_collection_code,
                "member_code": collection.member_code,
                "shift": str(collection.shift_code_id),
                "amount": str(collection.amount or 0),
                "qty": str(collection.qty or 0),
                "fat": str(collection.fat or 0),
                "snf": str(collection.snf or 0),
            },
            channels=["in_app", "push"],
            status="PENDING",
        )

        # Mark as processed in MSSQL
        with transaction.atomic(using="mssql"):
            collection.flg_sentbox_entry = "Y"
            collection.save(using="mssql", update_fields=["flg_sentbox_entry"])

        # Queue notification for delivery
        queue_notification_async.delay(notification.id)

        logger.info(f"✅ Notification created for collection {collection_code}")
        return True

    except (
        MppCollection.DoesNotExist,
        NotificationTemplate.DoesNotExist,
        User.DoesNotExist,
    ) as e:
        logger.error(f"Object not found while creating notification: {e}")
        return False

    except Exception as exc:
        logger.error(f"Error creating notification for {collection_code}: {exc}")
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
