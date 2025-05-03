# notifications/tasks.py
from celery import shared_task
import requests
from django.conf import settings
from  .fcm import _send_device_specific_notification,_send_fcm_message

@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_fcm_notification_task(self, token, title, body, data=None):

    payload = {
        "to": token,
        "notification": {
            "title": title,
            "body": body
        },
        "data": data or {}
    }

    try:
        sent,info = _send_device_specific_notification(device_token=token,notification=payload)
        if not sent:
            raise Exception(f"FCM failed: {info}")
        return {"status": "sent","info":info}
    except Exception as e:
        self.retry(exc=e)
