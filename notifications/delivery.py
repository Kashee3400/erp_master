# notifications/delivery.py
"""
Notification delivery service - separated from main service to avoid circular imports
"""
import logging
import requests
from typing import Dict, Any, Optional, TYPE_CHECKING
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
import argparse
import json
import requests
import google.auth.transport.requests

from google.oauth2 import service_account
from decouple import config

SERVICE_ACCOUNT_PATH = config("SERVICE_ACCOUNT_PATH")

PROJECT_ID = "kashee-e-dairy"
BASE_URL = "https://fcm.googleapis.com"
FCM_ENDPOINT = "v1/projects/" + PROJECT_ID + "/messages:send"
FCM_URL = BASE_URL + "/" + FCM_ENDPOINT
SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]


if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from .model import Notification

logger = logging.getLogger(__name__)


class NotificationDeliveryService:
    """
    Handles actual delivery of notifications through various channels
    Separated from main service to avoid circular imports
    """

    def deliver(self, notification: "Notification"):
        """Deliver notification through all configured channels"""
        from .model import NotificationStatus, NotificationChannel

        notification.status = NotificationStatus.SENDING
        notification.save(update_fields=["status"])

        delivery_results = {}
        success_count = 0

        for channel in notification.channels:
            try:
                if channel == NotificationChannel.IN_APP:
                    result = self._deliver_in_app(notification)
                elif channel == NotificationChannel.PUSH:
                    result = self._deliver_push(notification)
                elif channel == NotificationChannel.EMAIL:
                    result = self._deliver_email(notification)
                elif channel == NotificationChannel.SMS:
                    result = self._deliver_sms(notification)
                elif channel == NotificationChannel.WEBHOOK:
                    result = self._deliver_webhook(notification)
                else:
                    result = {"status": "skipped", "reason": "Unsupported channel"}

                delivery_results[channel] = result

                if result.get("status") == "success":
                    success_count += 1
                    self._mark_channel_delivered(notification, channel)
                else:
                    self._mark_channel_failed(
                        notification, channel, result.get("error")
                    )

            except Exception as e:
                logger.error(f"Delivery failed for channel {channel}: {e}")
                delivery_results[channel] = {"status": "error", "error": str(e)}
                self._mark_channel_failed(notification, channel, str(e))

        # Update overall status
        if success_count > 0:
            notification.status = NotificationStatus.SENT
            notification.sent_at = timezone.now()
        else:
            notification.status = NotificationStatus.FAILED

        notification.delivery_status = delivery_results
        notification.save(update_fields=["status", "sent_at", "delivery_status"])

        logger.info(
            f"Delivery completed for notification {notification.uuid} - {success_count}/{len(notification.channels)} channels successful"
        )

    def _mark_channel_delivered(self, notification: "Notification", channel: str):
        """Mark specific channel as delivered"""
        if not notification.delivery_status:
            notification.delivery_status = {}

        notification.delivery_status[channel] = {
            "status": "delivered",
            "delivered_at": timezone.now().isoformat(),
        }

        # Check if all channels are delivered
        all_delivered = all(
            status.get("status") == "delivered"
            for status in notification.delivery_status.values()
        )

        if all_delivered:
            from .model import NotificationStatus

            notification.status = NotificationStatus.DELIVERED
            notification.delivered_at = timezone.now()

    def _mark_channel_failed(
        self, notification: "Notification", channel: str, error: Optional[str] = None
    ):
        """Mark specific channel as failed"""
        if not notification.delivery_status:
            notification.delivery_status = {}

        notification.delivery_status[channel] = {
            "status": "failed",
            "error": error,
            "failed_at": timezone.now().isoformat(),
        }

    def _deliver_in_app(self, notification: "Notification") -> Dict[str, Any]:
        """Deliver in-app notification (just mark as available)"""
        return {"status": "success", "message": "In-app notification created"}

    def _deliver_push(self, notification: "Notification") -> Dict[str, Any]:
        """Deliver push notification via FCM"""
        try:
            # Get user's FCM token
            fcm_token = self._get_user_fcm_token(notification.recipient)
            if not fcm_token:
                return {"status": "skipped", "reason": "No FCM token found"}
            payload = notification.to_fcm_payload()
            payload["to"] = fcm_token
            response = self._send_fcm_request(payload)

            if response.get("success", 0) > 0:
                return {"status": "success", "response": response}
            else:
                error_msg = "Unknown FCM error"
                if "results" in response and response["results"]:
                    error_msg = response["results"][0].get("error", error_msg)
                return {"status": "failed", "error": error_msg}

        except Exception as e:
            logger.error(f"Push notification delivery failed: {e}")
            return {"status": "error", "error": str(e)}

    def _get_fcm_access_token(self):
        """Retrieve a valid access token that can be used to authorize requests.

        :return: Access token.
        """
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_PATH, scopes=SCOPES
        )
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        return credentials.token

    def _deliver_email(self, notification: "Notification") -> Dict[str, Any]:
        """Deliver email notification"""
        try:
            subject = notification.email_subject or notification.title

            # Use email template if available
            if notification.email_body:
                message = notification.email_body
                # Try to render HTML template
                try:
                    html_message = render_to_string(
                        "notifications/email_template.html",
                        notification.to_email_context(),
                    )
                except Exception:
                    html_message = None
            else:
                message = notification.body
                html_message = None

            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(
                    settings, "DEFAULT_FROM_EMAIL", "noreply@yourapp.com"
                ),
                recipient_list=[notification.recipient.email],
                html_message=html_message,
                fail_silently=False,
            )

            return {"status": "success", "message": "Email sent successfully"}

        except Exception as e:
            logger.error(f"Email delivery failed: {e}")
            return {"status": "error", "error": str(e)}

    def _deliver_sms(self, notification: "Notification") -> Dict[str, Any]:
        """Deliver SMS notification"""
        try:
            phone_number = getattr(notification.recipient, "phone_number", None)
            if not phone_number:
                return {"status": "skipped", "reason": "No phone number found"}

            # Example Twilio integration
            return self._send_twilio_sms(phone_number, notification.body)

        except Exception as e:
            logger.error(f"SMS delivery failed: {e}")
            return {"status": "error", "error": str(e)}

    def _deliver_webhook(self, notification: "Notification") -> Dict[str, Any]:
        """Deliver notification via webhook"""
        webhook_url = getattr(settings, "NOTIFICATION_WEBHOOK_URL", None)
        if not webhook_url:
            return {"status": "skipped", "reason": "No webhook URL configured"}

        payload = {
            "notification_id": str(notification.uuid),
            "recipient": notification.recipient.email,
            "title": notification.title,
            "body": notification.body,
            "category": notification.template.category,
            "deep_link": notification.deep_link_url,
            "context": notification.context_data,
            "timestamp": notification.created_at.isoformat(),
        }

        try:
            response = requests.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            response.raise_for_status()
            return {"status": "success", "response": response.json()}

        except Exception as e:
            logger.error(f"Webhook delivery failed: {e}")
            return {"status": "error", "error": str(e)}

    def _get_user_fcm_token(self, user: "User") -> Optional[str]:
        """Get user's FCM token from your user profile/device model"""
        if hasattr(user, "profile") and hasattr(user.profile, "fcm_token"):
            return user.profile.fcm_token
        try:
            from member.models import UserDevice

            device = UserDevice.objects.filter(user=user, is_active=True).first()
            return device.device if device else None
        except ImportError:
            pass
        return None

    def _send_fcm_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send HTTP request to FCM with given message.

        Args:
        fcm_message: JSON object that will make up the body of the request.
        """
        # [START use_access_token]
        headers = {
            "Authorization": "Bearer " + self._get_fcm_access_token(),
            "Content-Type": "application/json; UTF-8",
        }
        # [END use_access_token]
        response = requests.post(FCM_URL, json=payload, headers=headers, timeout=30)

        response.raise_for_status()
        return response.json()

    def _send_twilio_sms(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Send SMS via Twilio"""
        try:
            from twilio.rest import Client

            account_sid = getattr(settings, "TWILIO_ACCOUNT_SID", "")
            auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", "")
            from_number = getattr(settings, "TWILIO_FROM_NUMBER", "")

            if not all([account_sid, auth_token, from_number]):
                return {"status": "skipped", "reason": "Twilio not configured"}

            client = Client(account_sid, auth_token)

            message = client.messages.create(
                body=message[:160],  # SMS character limit
                from_=from_number,
                to=phone_number,
            )

            return {"status": "success", "message_sid": message.sid}

        except ImportError:
            return {"status": "error", "error": "Twilio library not installed"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
