from django.conf import settings
from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import logging
from .model import (
    Notification,
    NotificationTemplate,
    NotificationPreferences,
    NotificationChannel,
    NotificationStatus,
)
from notifications.deeplink_service import DeepLinkService, DeepLink

import datetime
import decimal
from django.utils.functional import Promise
from django.utils.encoding import force_str

from django.contrib.auth import get_user_model

if TYPE_CHECKING:
    from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class NotificationServices:
    """
    Generic notification service that can be used across any app
    Main service for creating and managing notifications
    """

    def __init__(
        self, base_url: str = None, deeplink_service: Optional[DeepLinkService] = None
    ):
        self.base_url = base_url or getattr(
            settings, "SITE_URL", "https://tech.kasheemilk.com/open/"
        )
        # allow injection for easier testing; fallback to instantiation
        self.deeplink_service = deeplink_service or DeepLinkService()

    def _serialize_context(self, context: dict) -> dict:
        """
        Safely convert model instances and lazy strings in context to JSON-serializable types.
        """

        def safe_value(value):
            # Lazy gettext/lazy strings
            if isinstance(value, Promise):
                return force_str(value)

            # Model instance
            if hasattr(value, "_meta"):
                return {
                    "id": value.pk,
                    "model": value._meta.label_lower,
                    "str": str(value),
                }

            # Datetime/date/time
            if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
                return value.isoformat()

            # Decimal
            if isinstance(value, decimal.Decimal):
                return float(value)

            # List / Tuple
            if isinstance(value, (list, tuple)):
                return [safe_value(v) for v in value]

            # Dict
            if isinstance(value, dict):
                return {k: safe_value(v) for k, v in value.items()}

            return value

        return {k: safe_value(v) for k, v in (context or {}).items()}

    def create_notification(
        self,
        template_name: str,
        recipient: Union["User", int, str],
        context: Dict[str, Any] = None,
        related_object: Any = None,
        sender: Optional["User"] = None,
        channels: List[str] = None,
        priority: str = "normal",
        scheduled_at: Optional[timezone.datetime] = None,
        expires_at: Optional[timezone.datetime] = None,
    ) -> Notification:
        """
        Create a new notification instance

        Args:
            template_name: Name of the notification template
            recipient: User instance, ID, or email
            context: Template context variables
            related_object: Related model instance for generic FK
            sender: User who triggered the notification
            channels: List of delivery channels
            priority: Notification priority
            scheduled_at: When to send the notification
            expires_at: When the notification expires
        """
        UserModel = get_user_model()
        # Get template
        try:
            template = NotificationTemplate.objects.get(
                name=template_name, is_active=True
            )
        except NotificationTemplate.DoesNotExist:
            logger.error(f"Notification template '{template_name}' not found")
            raise ValueError(f"Template '{template_name}' not found")

        # Resolve recipient
        if isinstance(recipient, str):
            if "@" in recipient:
                recipient = UserModel.objects.get(email=recipient)
            else:
                recipient = UserModel.objects.get(pk=recipient)
        elif isinstance(recipient, int):
            recipient = UserModel.objects.get(pk=recipient)

        # Prepare context
        context = context or {}
        if related_object:
            context.update(
                {
                    "object": related_object,
                    "object_id": related_object.pk,
                    "model_name": related_object._meta.model_name,
                    "app_label": related_object._meta.app_label,
                }
            )

        # Add recipient and sender to context
        context.update(
            {"recipient": recipient, "sender": sender, "base_url": self.base_url}
        )

        # Render content
        rendered_content = template.render_content(context)
        config = template.get_deeplink_config(context)

        if not channels:
            channels = self._get_preferred_channels(recipient, template)

        safe_context = self._serialize_context(context)
        # choose module from config or device (use whatever logic you already have)

        dl = self.deeplink_service.create_notification_deep_link(
            user_id=recipient.pk,
            clean_route=config.get("deeplink_type"),
            context=safe_context,
            fallback_url=config.get("fallback_template"),
            meta={
                **config.get("meta", {}),
                "template_name": getattr(template, "name", None),
            },
        )

        # Create notification
        notification = Notification.objects.create(
            template=template,
            recipient=recipient,
            sender=sender,
            title=rendered_content.get("title", ""),
            body=rendered_content.get("body", ""),
            email_subject=rendered_content.get("email_subject", ""),
            email_body=rendered_content.get("email_body", ""),
            deep_link_url=dl.deep_link,
            app_route=dl.deep_path,
            channels=channels,
            priority=priority or template.default_priority,
            notification_type=template.notification_type,
            context_data=safe_context,
            scheduled_at=scheduled_at or timezone.now(),
            expires_at=expires_at,
        )

        # Set content type and object id for related object
        if related_object:
            notification.content_type = ContentType.objects.get_for_model(
                related_object
            )
            notification.object_id = related_object.pk
            notification.save(update_fields=["content_type", "object_id"])

        logger.info(f"Created notification {notification.uuid} for {recipient.email}")

        # Queue for delivery if not scheduled for future
        if notification.scheduled_at <= timezone.now():
            self.queue_notification(notification)

        return notification

    def create_bulk_notifications(
        self,
        template_name: str,
        recipients: List[Union["User", int, str]],
        context_factory: Optional[callable] = None,
        related_object: Any = None,
        **kwargs,
    ) -> List[Notification]:
        """
        Create multiple notifications efficiently

        Args:
            template_name: Name of the notification template
            recipients: List of users, IDs, or emails
            context_factory: Function that takes (recipient, index) and returns context dict
            **kwargs: Additional arguments passed to create_notification
        """

        notifications = []

        for i, recipient in enumerate(recipients):
            context = {}
            if context_factory:
                context = context_factory(recipient, i)
            elif "context" in kwargs:
                context = kwargs["context"].copy()

            try:
                notification = self.create_notification(
                    template_name=template_name,
                    recipient=recipient,
                    context=context,
                    related_object=related_object,
                    **{k: v for k, v in kwargs.items() if k != "context"},
                )
                notifications.append(notification)
            except Exception as e:
                logger.error(
                    f"Failed to create notification for recipient {recipient}: {e}"
                )
                continue

        logger.info(
            f"Created {len(notifications)} bulk notifications using template '{template_name}'"
        )
        return notifications

    def _create_bulk_via_task(
        self,
        template_name: str,
        recipients: List[Union["User", int, str]],
        context_factory: Optional[callable] = None,
        **kwargs,
    ) -> List[int]:
        """Create bulk notifications via Celery task"""

        # Convert recipients to IDs
        recipient_ids = []
        for recipient in recipients:
            if isinstance(recipient, str):
                if "@" in recipient:
                    recipient_ids.append(User.objects.get(email=recipient).id)
                else:
                    recipient_ids.append(int(recipient))
            elif isinstance(recipient, int):
                recipient_ids.append(recipient)
            else:
                recipient_ids.append(recipient.id)

        # Import task here to avoid circular import
        from .tasks import send_bulk_notifications_task

        # Queue bulk task
        task = send_bulk_notifications_task.delay(
            template_name=template_name,
            recipient_ids=recipient_ids,
            context=kwargs.get("context", {}),
            **{k: v for k, v in kwargs.items() if k != "context"},
        )

        logger.info(
            f"Queued bulk notification task {task.id} for {len(recipient_ids)} recipients"
        )
        return recipient_ids

    def schedule_notification(
        self,
        template_name: str,
        recipient: Union["User", int, str],
        scheduled_at: timezone.datetime,
        context: Dict[str, Any] = None,
        **kwargs,
    ) -> Notification:
        """Create a scheduled notification"""

        notification = self.create_notification(
            template_name=template_name,
            recipient=recipient,
            context=context,
            scheduled_at=scheduled_at,
            **kwargs,
        )

        # Schedule delivery task
        from .tasks import schedule_notification_delivery_task

        schedule_notification_delivery_task.apply_async(
            args=[notification.id], eta=scheduled_at
        )

        return notification

    def _get_preferred_channels(
        self, user: "User", template: NotificationTemplate
    ) -> List[str]:
        """Get user's preferred channels for this template"""

        # Get user preferences for this specific template
        try:
            prefs = NotificationPreferences.objects.get(user=user, template=template)
        except NotificationPreferences.DoesNotExist:
            # Try category-based preferences
            try:
                prefs = NotificationPreferences.objects.get(
                    user=user, category=template.category
                )
            except NotificationPreferences.DoesNotExist:
                # Use template defaults
                return template.enabled_channels or [NotificationChannel.IN_APP]

        channels = []
        if (
            prefs.allow_in_app
            and NotificationChannel.IN_APP in template.enabled_channels
        ):
            channels.append(NotificationChannel.IN_APP)
        if prefs.allow_push and NotificationChannel.PUSH in template.enabled_channels:
            channels.append(NotificationChannel.PUSH)
        if prefs.allow_email and NotificationChannel.EMAIL in template.enabled_channels:
            channels.append(NotificationChannel.EMAIL)
        if prefs.allow_sms and NotificationChannel.SMS in template.enabled_channels:
            channels.append(NotificationChannel.SMS)

        return channels or [NotificationChannel.IN_APP]

    def cleanup_expired(self) -> int:
        """Remove expired notifications"""

        now = timezone.now()
        count = Notification.objects.filter(
            expires_at__lt=now,
            status__in=[NotificationStatus.SENT, NotificationStatus.DELIVERED],
        ).delete()[0]

        logger.info(f"Cleaned up {count} expired notifications")
        return count

    def queue_notification(self, notification: Notification):
        """Queue notification for delivery"""
        from .model import NotificationStatus
        from .tasks import deliver_notification

        notification.status = NotificationStatus.QUEUED
        notification.save(update_fields=["status"])
        # Queue async task for delivery
        deliver_notification.delay(notification.id)
        logger.info(f"Queued notification {notification.uuid} for delivery")

    def send_immediate(
        self,
        template_name: str,
        recipient: Union["User", int, str],
        context: Dict[str, Any] = None,
        **kwargs,
    ) -> Notification:
        """Create and immediately send a notification"""
        from .tasks import deliver_notification

        notification = self.create_notification(
            template_name=template_name, recipient=recipient, context=context, **kwargs
        )
        deliver_notification.apply(args=[notification.id])
        return notification


def notify(
    template_name: str,
    recipient: Union["User", int, str],
    context: Dict[str, Any] = None,
    **kwargs,
) -> Notification:
    """
    Convenience function for creating notifications

    Usage:
        from notifications.services import notify

        notify(
            'order_shipped',
            user,
            context={'order': order, 'tracking_code': '123456'},
            related_object=order
        )
    """
    service = NotificationServices()
    return service.d(template_name, recipient, context, **kwargs)


def notify_bulk(
    template_name: str,
    recipients: List[Union["User", int, str]],
    context: Dict[str, Any] = None,
    **kwargs,
) -> List[Notification]:
    """
    Convenience function for bulk notifications

    Usage:
        from notifications.services import notify_bulk

        notify_bulk(
            'system_maintenance',
            User.objects.filter(is_active=True),
            context={'maintenance_date': date.today()}
        )
    """
    service = NotificationServices()
    return service.create_bulk_notifications(
        template_name, recipients, context=context, **kwargs
    )


def notify_immediate(
    template_name: str,
    recipient: Union["User", int, str],
    context: Dict[str, Any] = None,
    **kwargs,
) -> Notification:
    """
    Convenience function for immediate notifications

    Usage:
        from notifications.services import notify_immediate

        notify_immediate(
            'password_reset',
            'user@example.com',
            context={'reset_link': 'https://...'}
        )
    """
    service = NotificationServices()
    return service.send_immediate(template_name, recipient, context, **kwargs)
