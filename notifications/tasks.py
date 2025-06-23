# notifications/tasks.py
from celery import shared_task
import requests
from django.core.mail import send_mail
from django.conf import settings
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
