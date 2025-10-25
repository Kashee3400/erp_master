# notifications/delivery.py
"""
Notification delivery service - separated from main service to avoid circular imports
"""
import logging
import requests
from typing import Dict, Any, Optional, List
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.utils import timezone


logger = logging.getLogger(__name__)


class NotificationDeliveryService:
    """
    Handles actual delivery of notifications through various channels
    Separated from main service to avoid circular imports
    """

    from .model import Notification, NotificationStatus
    from member.models import User

    def deliver_batch(self, notifications: List[Notification], max_workers: int = 20):
        """
        Deliver a batch of notifications with parallel channel delivery.
        """
        from .model import NotificationStatus

        processed_notifs = []

        for notification in notifications:
            try:
                notification.status = NotificationStatus.SENDING
                delivery_results = {}
                success_count = 0
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = {
                        executor.submit(
                            self._deliver_channel_safe, notification, channel
                        ): channel
                        for channel in notification.channels
                    }

                    for future in as_completed(futures):
                        channel = futures[future]
                        result = future.result()
                        delivery_results[channel] = result
                        if result.get("status") == "success":
                            success_count += 1

                # Determine final notification status
                if success_count == len(notification.channels):
                    notification.status = NotificationStatus.SENT
                elif success_count == 0:
                    notification.status = NotificationStatus.FAILED
                else:
                    notification.status = NotificationStatus.PARTIALLY_SENT

                notification.delivery_status = delivery_results
                notification.sent_at = timezone.now()
                processed_notifs.append(notification)

                logger.info(
                    f"Notification {notification.uuid} delivered - {success_count}/{len(notification.channels)} channels successful"
                )

            except Exception as exc:
                logger.exception(
                    f"Fatal error processing notification {notification.uuid}: {exc}"
                )
                notification.status = NotificationStatus.FAILED
                notification.delivery_status = {"error": str(exc)}
                processed_notifs.append(notification)

        # Bulk update at end of batch
        if processed_notifs:
            from django.db import transaction
            from .model import Notification

            with transaction.atomic():
                Notification.objects.bulk_update(
                    processed_notifs, ["status", "sent_at", "delivery_status"]
                )

        return len(processed_notifs)

    def _deliver_channel_safe(self, notification, channel):
        """
        Deliver a single channel safely, catching exceptions.
        """
        from .choices import NotificationChannel

        try:
            if channel == NotificationChannel.IN_APP:
                return self._deliver_in_app(notification)
            elif channel == NotificationChannel.PUSH:
                return self._deliver_push(notification)
            elif channel == NotificationChannel.EMAIL:
                return self._deliver_email(notification)
            elif channel == NotificationChannel.WEBHOOK:
                return self._deliver_webhook(notification)
            else:
                return {"status": "skipped", "reason": "Unsupported channel"}
        except Exception as e:
            logger.error(f"Delivery failed for channel {channel}: {e}")
            return {"status": "error", "error": str(e)}

    def deliver(self, notification: Notification):
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
                elif channel == NotificationChannel.WEBHOOK:
                    result = self._deliver_webhook(notification)
                else:
                    result = {"status": "skipped", "reason": "Unsupported channel"}

                delivery_results[channel] = result

                if result.get("status") == "success":
                    success_count += 1

            except Exception as e:
                logger.error(f"Delivery failed for channel {channel}: {e}")
                delivery_results[channel] = {"status": "error", "error": str(e)}
                notification.mark_as_failed(channel=channel, error=str(e))

        notification.delivery_status = delivery_results
        notification.save(update_fields=["status", "sent_at", "delivery_status"])

        logger.info(
            f"Delivery completed for notification {notification.uuid} - {success_count}/{len(notification.channels)} channels successful"
        )

    def _deliver_in_app(self, notification: Notification) -> Dict[str, Any]:
        """Deliver in-app notification (just mark as available)"""
        return {"status": "success", "message": "In-app notification created"}

    def _deliver_push(self, notification: Notification) -> Dict[str, Any]:
        """Deliver push notification via FCM"""
        from .fcm import _send_fcm_message

        try:
            # Get user's FCM token
            fcm_token = self._get_user_fcm_token(notification.recipient)
            if not fcm_token:
                return {"status": "skipped", "reason": "No FCM token found"}

            sent, info = _send_fcm_message(
                notification.to_fcm_payload(
                    base_url="http://10.10.10.43:8000", device_token=fcm_token
                )
            )

            if sent:
                return {"status": "success", "response": info}
            else:

                return {"status": "failed", "error": info}

        except Exception as e:
            logger.error(f"Push notification delivery failed: {e}")
            return {"status": "error", "error": str(e)}

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

    def _get_user_fcm_token(self, user) -> Optional[str]:
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
