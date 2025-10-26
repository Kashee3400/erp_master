import uuid
from typing import Dict, Any
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxLengthValidator
from django.db import models
from django.db.models import JSONField
from django.urls import reverse, NoReverseMatch
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import pytz
from datetime import time, datetime
from .choices import *

User = get_user_model()


class NotificationTemplate(models.Model):
    """Reusable notification templates"""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Template Name"),
        help_text=_("Unique identifier for this template"),
    )

    # Multi-channel content
    title_template = models.CharField(
        max_length=255,
        verbose_name=_("Title Template"),
        help_text=_("Template for notification title (supports variables)"),
    )

    body_template = models.TextField(
        verbose_name=_("Body Template"),
        help_text=_("Template for notification body (supports variables)"),
    )

    email_subject_template = models.CharField(
        max_length=255, blank=True, verbose_name=_("Email Subject Template")
    )

    email_body_template = models.TextField(
        blank=True, verbose_name=_("Email Body Template")
    )

    # Configuration
    enabled_channels = models.JSONField(
        default=list,
        verbose_name=_("Enabled Channels"),
        help_text=_("List of channels this template supports"),
    )

    default_priority = models.CharField(
        max_length=10,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
    )

    notification_type = models.CharField(
        max_length=10, choices=NotificationType.choices, default=NotificationType.INFO
    )

    # Deep linking configuration
    route_template = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Route Template"),
        help_text=_(
            "URL route template for deep linking (e.g., '/orders/{object_id}/')"
        ),
    )

    url_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("URL Name"),
        help_text=_("Django URL name for reverse lookup"),
    )

    # Metadata
    category = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Category"),
        help_text=_("Grouping category (e.g., 'orders', 'users', 'system')"),
    )

    locale = models.CharField(
        max_length=50,
        default="en",
        verbose_name=_("Locale"),
        help_text=_("Locale (e.g., 'hi', 'en')"),
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tbl_notification_templates"
        verbose_name = _("Notification Template")
        verbose_name_plural = _("Notification Templates")
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.name} ({self.category})"

    def render_content(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Render template content with context variables"""
        from django.template import Template, Context

        title_tmpl = Template(self.title_template)
        body_tmpl = Template(self.body_template)

        django_context = Context(context)

        rendered = {
            "title": title_tmpl.render(django_context),
            "body": body_tmpl.render(django_context),
        }

        if self.email_subject_template:
            email_subject_tmpl = Template(self.email_subject_template)
            rendered["email_subject"] = email_subject_tmpl.render(django_context)

        if self.email_body_template:
            email_body_tmpl = Template(self.email_body_template)
            rendered["email_body"] = email_body_tmpl.render(django_context)

        return rendered

    def generate_deep_link(self, context: Dict[str, Any], base_url: str = "") -> str:
        """Generate deep link URL from template and context"""
        if not self.route_template and not self.url_name:
            return ""

        try:
            # Try URL reverse lookup first
            if self.url_name:
                # Extract URL kwargs from context
                url_kwargs = {
                    k: v
                    for k, v in context.items()
                    if k in ["pk", "id", "slug", "uuid", "object_id"]
                }
                route = reverse(self.url_name, kwargs=url_kwargs)
            else:
                # Use route template
                from django.template import Template, Context

                route_tmpl = Template(self.route_template)
                route = route_tmpl.render(Context(context))

            # Combine with base URL if provided
            if base_url:
                return f"{base_url.rstrip('/')}{route}"
            return route

        except (NoReverseMatch, Exception) as e:
            # Fallback to template rendering
            if self.route_template:
                from django.template import Template, Context

                route_tmpl = Template(self.route_template)
                route = route_tmpl.render(Context(context))
                return f"{base_url.rstrip('/')}{route}" if base_url else route
            return ""


import json


class Notification(models.Model):
    """Individual notification instances with deep linking support."""

    # Identifiers
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        verbose_name=_("UUID"),
        help_text=_("Unique identifier for this notification (auto-generated)."),
    )

    # Relationships
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("Notification Template"),
        help_text=_("The template used to generate this notification."),
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_app_notifications",
        verbose_name=_("Recipient"),
        help_text=_("The user who will receive this notification."),
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_app_notifications",
        verbose_name=_("Sender"),
        help_text=_("The user who sent this notification, if applicable."),
    )

    # Generic foreign key for related object
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Content Type"),
        help_text=_("Type of the related object this notification refers to."),
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Object ID"),
        help_text=_("ID of the related object this notification refers to."),
    )
    related_object = GenericForeignKey("content_type", "object_id")

    # Rendered content
    title = models.CharField(
        max_length=255,
        verbose_name=_("Title"),
        help_text=_("Notification title displayed to the user."),
    )
    body = models.TextField(
        verbose_name=_("Body"),
        help_text=_("Notification message body displayed to the user."),
    )

    # Channel-specific content
    email_subject = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Email Subject"),
        help_text=_("Subject line for email notifications, if applicable."),
    )
    email_body = models.TextField(
        blank=True,
        verbose_name=_("Email Body"),
        help_text=_("Body content for email notifications, if applicable."),
    )

    # Deep linking
    deep_link_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name=_("Deep Link URL"),
        help_text=_("Full URL for deep linking (web or universal link)."),
    )
    app_route = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("App Route"),
        help_text=_("Internal app route for in-app navigation."),
    )
    custom_key = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Custom Key"),
        help_text=_("Optional key used for grouping or client-side logic."),
    )
    is_subroute = models.BooleanField(
        default=False,
        verbose_name=_("Is Subroute"),
        help_text=_("Indicates if the route is a sub-path or detail view."),
    )


    # Configuration
    channels = models.JSONField(
        default=list,
        verbose_name=_("Delivery Channels"),
        help_text=_(
            "List of channels to deliver this notification through (push, email, sms, in_app)."
        ),
    )
    priority = models.CharField(
        max_length=10,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
        verbose_name=_("Priority"),
        help_text=_("Priority level of the notification (low, normal, high)."),
    )
    notification_type = models.CharField(
        max_length=10,
        choices=NotificationType.choices,
        default=NotificationType.INFO,
        verbose_name=_("Notification Type"),
        help_text=_("Type of notification (info, alert, etc.)."),
    )

    # Context data for templating and deep linking
    context_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Context Data"),
        help_text=_("Additional context data for templating and deep linking."),
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
        db_index=True,
        verbose_name=_("Status"),
        help_text=_(
            "Current status of the notification (pending, sent, delivered, failed)."
        ),
    )
    delivery_status = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Delivery Status"),
        help_text=_(
            "Per-channel delivery status and responses from external services."
        ),
    )

    # Timestamps
    scheduled_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name=_("Scheduled At"),
        help_text=_("Datetime when the notification is scheduled to be sent."),
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Sent At"),
        help_text=_("Datetime when the notification was sent."),
    )
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Delivered At"),
        help_text=_("Datetime when the notification was successfully delivered."),
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Read At"),
        help_text=_("Datetime when the recipient read the notification."),
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Expires At"),
        help_text=_("Datetime after which the notification is no longer relevant."),
    )

    # In-app specific fields
    is_read = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("Is Read"),
        help_text=_("Whether the recipient has read this notification."),
    )
    is_archived = models.BooleanField(
        default=False,
        verbose_name=_("Is Archived"),
        help_text=_("Whether the notification has been archived by the recipient."),
    )

    # Record timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name=_("Created At"),
        help_text=_("Datetime when the notification record was created."),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
        help_text=_("Datetime when the notification record was last updated."),
    )
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "status", "-created_at"]),
            models.Index(fields=["recipient", "is_read", "-created_at"]),
            models.Index(fields=["template", "-created_at"]),
            models.Index(fields=["scheduled_at", "status"]),
            models.Index(fields=["priority", "-created_at"]),
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"{self.template.name} → {self.recipient.email}"

    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])

    def mark_as_delivered(self, channel: str = None):
        """Mark notification as delivered for specific channel or overall"""
        now = timezone.now()

        if channel:

            # Update specific channel status
            if not self.delivery_status:
                self.delivery_status = {}
            self.delivery_status[channel] = {
                "status": "delivered",
                "delivered_at": now.isoformat(),
            }

            # Check if all channels are delivered
            all_delivered = all(
                status.get("status") == "delivered"
                for status in self.delivery_status.values()
            )

            if all_delivered and self.status != NotificationStatus.DELIVERED:
                self.status = NotificationStatus.DELIVERED
                self.delivered_at = now
        else:
            # Mark overall as delivered
            self.status = NotificationStatus.DELIVERED
            self.delivered_at = now

        self.save(update_fields=["status", "delivered_at", "delivery_status"])

    def mark_as_failed(self, channel: str, error: str = None):
        """Mark notification as failed for specific channel"""
        if not self.delivery_status:
            self.delivery_status = {}

        # Handle legacy string data
        if isinstance(self.delivery_status, str):
            try:
                self.delivery_status = json.loads(self.delivery_status)
            except json.JSONDecodeError:
                self.delivery_status = {}

        # Update channel failure info
        self.delivery_status[channel] = {
            "status": "failed",
            "error": error,
            "failed_at": timezone.now().isoformat(),
        }

        # Check if all channels have failed
        all_failed = all(
            isinstance(status, dict) and status.get("status") in ["failed", "cancelled"]
            for status in self.delivery_status.values()
        )

        if all_failed:
            self.status = NotificationStatus.FAILED

        self.save(update_fields=["status", "delivery_status"])

    def to_fcm_payload(
        self, base_url: str = "", device_token: str = ""
    ) -> Dict[str, Any]:
        """Generate FCM payload with deep linking (FCM v1 compliant)."""

        deep_link = self.deep_link_url
        if not deep_link and base_url:
            deep_link = (
                f"{base_url.rstrip('/')}{self.app_route}"
                if self.app_route
                else base_url
            )

        # ✅ Convert context values to strings to satisfy FCM data payload rules
        safe_context = {
            k: str(v) if not isinstance(v, str) else v
            for k, v in (self.context_data or {}).items()
        }

        return {
            "message": {
                "token": device_token,
                "notification": {
                    "title": self.title,
                    "body": self.body,
                    # "image": "http://erp.kasheemilk.com:50012///FileServer/Import/Image/1C18B53A17344A5899C6A40B45ACAE2D.png",
                },
                "data": {
                    "notification_id": str(self.uuid),
                    "template_name": self.template.name,
                    "message": self.template.body_template,
                    "category": self.template.category,
                    "type": self.notification_type,
                    "object_id": str(self.object_id),
                    "content_type": (
                        self.content_type.model_class().__module__
                        + "."
                        + self.content_type.model_class().__name__
                    ),
                    "priority": str(self.priority),
                    "route": self.app_route or "",
                    "deep_link": deep_link or "",
                    "timestamp": self.created_at.isoformat(),
                    "expires_at": (
                        self.expires_at.isoformat() if self.expires_at else ""
                    ),
                    **safe_context,
                },
                "android": {
                    "notification": {
                        "click_action": "FLUTTER_NOTIFICATION_CLICK",
                        # "channel_id": f"notifications_{self.template.category}",
                    },
                },
                "apns": {
                    "headers": {
                        "apns-priority": (
                            "10" if self.priority in ["high", "urgent"] else "5"
                        )
                    },
                    "payload": {
                        "aps": {
                            "category": f"NOTIFICATION_{self.template.category.upper()}",
                            "badge": 1,
                            **(
                                {"sound": "default"}
                                if self.priority in ["high", "urgent"]
                                else {}
                            ),
                        }
                    },
                    "fcm_options": {"image": self.context_data.get("image_url", "")},
                },
            }
        }

    def to_email_context(self) -> Dict[str, Any]:
        """Generate email context"""
        return {
            "notification": self,
            "title": self.email_subject or self.title,
            "body": self.email_body or self.body,
            "deep_link": self.deep_link_url,
            "recipient": self.recipient,
            "sender": self.sender,
            **self.context_data,
        }

    def get_absolute_url(self) -> str:
        """Get the deep link URL for this notification"""
        return self.deep_link_url or self.app_route or ""


class NotificationPreferences(models.Model):
    """User-specific notification preferences per template or category."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
        verbose_name=_("User"),
        help_text=_("The user for whom these notification preferences apply."),
    )
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Notification Template"),
        help_text=_(
            "Specific notification template this preference applies to. Leave blank for category-wide preferences."
        ),
    )
    category = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Category"),
        help_text=_("Category of notifications for which these preferences apply."),
    )

    # Channel preferences
    allow_push = models.BooleanField(
        default=True,
        verbose_name=_("Allow Push Notifications"),
        help_text=_(
            "Whether the user wants to receive push notifications for this template or category."
        ),
    )
    allow_email = models.BooleanField(
        default=True,
        verbose_name=_("Allow Email Notifications"),
        help_text=_(
            "Whether the user wants to receive email notifications for this template or category."
        ),
    )
    allow_sms = models.BooleanField(
        default=False,
        verbose_name=_("Allow SMS Notifications"),
        help_text=_(
            "Whether the user wants to receive SMS notifications for this template or category."
        ),
    )
    allow_in_app = models.BooleanField(
        default=True,
        verbose_name=_("Allow In-App Notifications"),
        help_text=_(
            "Whether the user wants to receive in-app notifications for this template or category."
        ),
    )

    # Time-based preferences
    quiet_hours_start = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("Quiet Hours Start"),
        help_text=_(
            "Start time for quiet hours during which notifications should not be sent."
        ),
    )
    quiet_hours_end = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("Quiet Hours End"),
        help_text=_(
            "End time for quiet hours during which notifications should not be sent."
        ),
    )
    timezone = models.CharField(
        max_length=50,
        default="UTC",
        verbose_name=_("Timezone"),
        help_text=_(
            "Timezone used to interpret quiet hours and other time-based preferences."
        ),
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("Timestamp when this preference record was created."),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
        help_text=_("Timestamp when this preference record was last updated."),
    )

    class Meta:
        db_table = "tbl_notification"
        unique_together = [
            ("user", "template"),
            ("user", "category"),
        ]
        verbose_name = _("Notification Preference")
        verbose_name_plural = _("Notification Preferences")

    def __str__(self):
        target = self.template.name if self.template else f"Category: {self.category}"
        return f"{self.user.email} - {target}"

    # -----------------------------
    # Helper Methods
    # -----------------------------
    def is_channel_allowed(self, channel: str) -> bool:
        """Check if notifications are allowed for a specific channel."""
        channel = channel.lower()
        return {
            "push": self.allow_push,
            "email": self.allow_email,
            "sms": self.allow_sms,
            "in_app": self.allow_in_app,
        }.get(channel, False)

    def is_within_quiet_hours(self, now: datetime = None) -> bool:
        """
        Check if the current time falls within user's quiet hours.
        :param now: timezone-aware datetime, defaults to current UTC time.
        :return: True if within quiet hours, False otherwise.
        """
        if not self.quiet_hours_start or not self.quiet_hours_end:
            return False  # No quiet hours defined

        if not now:
            now = timezone.now()

        try:
            user_tz = pytz.timezone(self.timezone)
        except Exception:
            user_tz = pytz.UTC

        local_now = now.astimezone(user_tz).time()
        start = self.quiet_hours_start
        end = self.quiet_hours_end

        if start < end:
            # Quiet hours during the same day
            return start <= local_now <= end
        else:
            # Quiet hours span midnight
            return local_now >= start or local_now <= end

    def can_send(self, channel: str, now: datetime = None) -> bool:
        """
        Determine if a notification can be sent based on channel and quiet hours.
        :param channel: notification channel (push, email, sms, in_app)
        :param now: optional timezone-aware datetime
        :return: True if allowed, False otherwise
        """
        return self.is_channel_allowed(channel) and not self.is_within_quiet_hours(now)


class NotificationGroup(models.Model):
    """Group related notifications together for organized delivery and display."""

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name=_("UUID"),
        help_text=_("Unique identifier for this notification group (auto-generated)."),
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_("Name"),
        help_text=_("Human-readable name for the notification group."),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Optional description explaining the purpose of this group."),
    )

    # Related object that triggered this group
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Content Type"),
        help_text=_("Type of the related object triggering this notification group."),
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Object ID"),
        help_text=_("ID of the related object triggering this group."),
    )
    related_object = GenericForeignKey("content_type", "object_id")

    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Icon"),
        help_text=_("Icon class or emoji representing the notification group."),
    )
    color = models.CharField(
        max_length=7,
        default="#007bff",
        verbose_name=_("Color"),
        help_text=_("Hex color code representing this notification group."),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("Timestamp when this notification group was created."),
    )

    class Meta:
        db_table = "tbl_notification_group"
        verbose_name = _("Notification Group")
        verbose_name_plural = _("Notification Groups")
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    # -----------------------------
    # Utility / Helper Methods
    # -----------------------------
    def display_icon(self):
        """Return icon HTML or emoji for frontend display."""
        if self.icon:
            return (
                f'<i class="{self.icon}"></i>'
                if self.icon.startswith("fa")
                else self.icon
            )
        return ""

    def display_color(self):
        """Return the hex color of the group."""
        return self.color

    def has_related_object(self):
        """Check if this group is associated with a related object."""
        return self.related_object is not None


class NotificationDelivery(models.Model):
    """Track delivery attempts of notifications across different channels."""

    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name="deliveries",
        verbose_name="Notification",
        help_text="The notification instance associated with this delivery attempt.",
    )
    channel = models.CharField(
        max_length=50,
        choices=NotificationChannel.choices,
        default=NotificationChannel.PUSH,
        verbose_name="Delivery Channel",
        help_text="The channel used to deliver the notification (e.g., email, SMS, push).",
    )

    # Delivery details
    recipient = models.CharField(
        max_length=255,
        verbose_name="Recipient",
        help_text="Recipient identifier: email, phone number, or device token.",
    )
    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
        verbose_name="Delivery Status",
        help_text="Current status of the delivery attempt.",
    )

    # Attempt tracking
    attempt_count = models.IntegerField(
        default=0,
        verbose_name="Attempt Count",
        help_text="Number of delivery attempts made for this notification.",
    )
    max_attempts = models.IntegerField(
        default=3,
        verbose_name="Maximum Attempts",
        help_text="Maximum allowed attempts before marking as failed.",
    )
    next_attempt_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Next Attempt At",
        help_text="Scheduled time for the next delivery attempt.",
    )

    # Response tracking
    external_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="External ID",
        help_text="ID provided by the external delivery service.",
    )
    response_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Response Data",
        help_text="Raw response data returned by the delivery channel.",
    )
    error_message = models.TextField(
        blank=True,
        verbose_name="Error Message",
        help_text="Error message if the delivery attempt failed.",
    )

    # Timestamps
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Sent At",
        help_text="Timestamp when the notification was sent.",
    )
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Delivered At",
        help_text="Timestamp when the notification was successfully delivered.",
    )
    failed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Failed At",
        help_text="Timestamp when the delivery attempt failed.",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text="Timestamp when this record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
        help_text="Timestamp when this record was last updated.",
    )

    class Meta:
        db_table = "tbl_notification_deliveries"
        unique_together = ["notification", "channel"]
        indexes = [
            models.Index(fields=["status", "next_attempt_at"]),
            models.Index(fields=["channel", "-created_at"]),
        ]
        verbose_name = "Notification Delivery"
        verbose_name_plural = "Notification Deliveries"

    def __str__(self):
        return f"{self.notification} via {self.channel}"

    # -----------------------------
    # Delivery Status Helper Methods
    # -----------------------------
    def mark_sent(self):
        """Mark the delivery as sent."""
        self.status = NotificationStatus.SENT
        self.sent_at = timezone.now()
        self.attempt_count += 1
        self.save(update_fields=["status", "sent_at", "attempt_count", "updated_at"])

    def mark_delivered(self):
        """Mark the delivery as successfully delivered."""
        self.status = NotificationStatus.DELIVERED
        self.delivered_at = timezone.now()
        self.save(update_fields=["status", "delivered_at", "updated_at"])

    def mark_failed(self, error_message=None):
        """Mark the delivery as failed and store an optional error message."""
        self.status = NotificationStatus.FAILED
        self.failed_at = timezone.now()
        if error_message:
            self.error_message = error_message
        self.save(update_fields=["status", "failed_at", "error_message", "updated_at"])

    def can_retry(self):
        """Return True if another delivery attempt can be made."""
        return (
            self.attempt_count < self.max_attempts
            and self.status != NotificationStatus.DELIVERED
        )


class NotificationClickTracking(models.Model):
    """Track clicks on notification links"""

    notification = models.ForeignKey(
        Notification, on_delete=models.CASCADE, related_name="clicks"
    )
    clicked_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        db_table = "tbl_notification_click_tracking"


class NotificationAnalytics(models.Model):
    """Analytics for notification performance"""

    template = models.ForeignKey(
        NotificationTemplate, on_delete=models.CASCADE, related_name="analytics"
    )
    channel = models.CharField(
        choices=NotificationChannel.choices, default=NotificationChannel.PUSH
    )
    date = models.DateField(db_index=True)

    # Metrics
    sent_count = models.IntegerField(default=0)
    delivered_count = models.IntegerField(default=0)
    read_count = models.IntegerField(default=0)
    clicked_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)

    # Calculated rates
    delivery_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    read_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    click_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tbl_notification_analytics"
        unique_together = ["template", "channel", "date"]


class NotificationTrackMppCollection(models.Model):
    collection_code = models.CharField(
        max_length=200, verbose_name=_("Mpp Collection Code")
    )
    is_sent = models.BooleanField(default=False)

    class Meta:
        db_table = "tbl_notification_track"
