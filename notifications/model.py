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

User = get_user_model()


class NotificationMedium(models.TextChoices):
    SYSTEM = "system", _("System")
    FCM = "fcm", _("Firebase Push")
    EMAIL = "email", _("Email")


class NotificationChannel(models.TextChoices):
    """Available notification channels"""

    IN_APP = "in_app", _("In-App")
    PUSH = "push", _("Push Notification")
    EMAIL = "email", _("Email")
    SMS = "sms", _("SMS")
    WEBHOOK = "webhook", _("Webhook")


class NotificationStatus(models.TextChoices):
    """Notification delivery status"""

    PENDING = "pending", _("Pending")
    QUEUED = "queued", _("Queued")
    SENDING = "sending", _("Sending")
    SENT = "sent", _("Sent")
    DELIVERED = "delivered", _("Delivered")
    FAILED = "failed", _("Failed")
    CANCELLED = "cancelled", _("Cancelled")


class NotificationPriority(models.TextChoices):
    """Notification priority levels"""

    LOW = "low", _("Low")
    NORMAL = "normal", _("Normal")
    HIGH = "high", _("High")
    URGENT = "urgent", _("Urgent")


class NotificationType(models.TextChoices):
    """Notification types for UI styling"""

    INFO = "info", _("Information")
    SUCCESS = "success", _("Success")
    WARNING = "warning", _("Warning")
    ERROR = "error", _("Error")


class AppNotification(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_notifications",
        verbose_name=_("Sender"),
        help_text=_("User who triggered the notification."),
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("Recipient"),
        help_text=_("User who will receive the notification."),
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_("Title"),
        help_text=_("Title or heading for the notification."),
    )
    body = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Body"),
        help_text=_("Short summary or preview for the notification."),
    )
    message = models.TextField(
        verbose_name=_("Message"),
        help_text=_("Detailed notification message to be shown."),
        validators=[MaxLengthValidator(1000)],
    )
    model = models.CharField(
        max_length=100,
        verbose_name=_("Model Type"),
        help_text=_(
            "Name of the model related to this notification, e.g., 'feedback', 'report'."
        ),
    )
    object_id = models.PositiveIntegerField(
        verbose_name=_("Object ID"),
        help_text=_("Primary key of the related model instance."),
    )
    route = models.CharField(
        max_length=255,
        verbose_name=_("Route"),
        help_text=_("Frontend route name for redirection."),
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
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.INFO,
        verbose_name=_("Notification Type"),
        help_text=_("Classifies the type of notification."),
    )
    sent_via = models.CharField(
        max_length=20,
        choices=NotificationMedium.choices,
        default=NotificationMedium.SYSTEM,
        verbose_name=_("Sent Via"),
        help_text=_("Medium through which the notification was sent."),
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name=_("Is Read"),
        help_text=_("Indicates whether the user has read the notification."),
    )
    allowed_email = models.BooleanField(
        default=False,
        verbose_name=_("Allowed Email"),
        help_text=_("Used to handle if email notification allowed or not."),
    )
    read_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Read At"),
        help_text=_("Timestamp when the notification was read."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("Timestamp when the notification was created."),
    )
    deleted = models.BooleanField(
        default=False,
        help_text=_("Indicates whether this object has been deleted or not."),
        verbose_name=_("Deleted"),
    )
    delivery_status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
        verbose_name=_("Delivery Status"),
        help_text=_("Tracks whether the notification was successfully delivered."),
    )
    delivery_response = JSONField(
        blank=True,
        null=True,
        verbose_name=_("Delivery Response"),
        help_text=_("Raw response from the notification delivery system (e.g., FCM)."),
    )
    delivery_attempted_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Delivery Attempted At"),
        help_text=_("Timestamp of the last delivery attempt."),
    )

    class Meta:
        verbose_name = _("App Notification")
        verbose_name_plural = _("App Notifications")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["model", "object_id"]),
        ]

    def mark_as_read(self):
        """Mark the notification as read and store the timestamp."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])

    def to_payload(self) -> dict:
        """Return flat dict suitable for FCM data payload."""
        return {
            "title": self.title,
            "body": self.body or "",
            "sender": self.sender.get_full_name() if self.sender else "N/A",
            "recipient": self.recipient.get_full_name() if self.recipient else "N/A",
            "status": self.delivery_status,
            "via": self.sent_via,
            "message": self.message,
            "read": str(self.is_read).lower(),
            "read_at": self.read_at.isoformat() if self.read_at else "",
            "route": self.route,
            "id": str(self.object_id),
            "model": self.model,
            "customKey": self.custom_key or "",
            "is_subroute": str(self.is_subroute).lower(),
            "notification_type": self.notification_type,
        }

    def mark_delivery_result(self, status: str, response: dict = None):
        self.delivery_status = status
        self.delivery_response = response
        self.delivery_attempted_at = timezone.now()
        self.save(
            update_fields=[
                "delivery_status",
                "delivery_response",
                "delivery_attempted_at",
            ]
        )

    def __str__(self):
        return f"[{self.notification_type.upper()}] {self.title} → {self.recipient}"


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

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
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


class Notification(models.Model):
    """Individual notification instances with deep linking support"""

    # Identifiers
    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True
    )

    # Relationships
    template = models.ForeignKey(
        NotificationTemplate, on_delete=models.CASCADE, related_name="notifications"
    )

    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_app_notifications"
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_app_notifications",
    )

    # Generic foreign key for related object
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey("content_type", "object_id")

    # Rendered content
    title = models.CharField(max_length=255)
    body = models.TextField()

    # Channel-specific content
    email_subject = models.CharField(max_length=255, blank=True)
    email_body = models.TextField(blank=True)

    # Deep linking
    deep_link_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name=_("Deep Link URL"),
        help_text=_("Full URL for deep linking (web/universal link)"),
    )

    app_route = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("App Route"),
        help_text=_("Internal app route for navigation"),
    )

    # Configuration
    channels = models.JSONField(
        default=list,
        verbose_name=_("Delivery Channels"),
        help_text=_("Channels to deliver this notification through"),
    )

    priority = models.CharField(
        max_length=10,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
    )

    notification_type = models.CharField(
        max_length=10, choices=NotificationType.choices, default=NotificationType.INFO
    )

    # Context data for templating and deep linking
    context_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Context Data"),
        help_text=_("Additional data for templating and deep linking"),
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
        db_index=True,
    )

    # Channel-specific delivery status
    delivery_status = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Delivery Status"),
        help_text=_("Per-channel delivery status and responses"),
    )

    # Timestamps
    scheduled_at = models.DateTimeField(default=timezone.now, db_index=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # In-app specific fields
    is_read = models.BooleanField(default=False, db_index=True)
    is_archived = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

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

        self.delivery_status[channel] = {
            "status": "failed",
            "error": error,
            "failed_at": timezone.now().isoformat(),
        }

        # Check if all channels have failed
        all_failed = all(
            status.get("status") in ["failed", "cancelled"]
            for status in self.delivery_status.values()
        )

        if all_failed:
            self.status = NotificationStatus.FAILED

        self.save(update_fields=["status", "delivery_status"])

    def to_fcm_payload(
        self, base_url: str = "", device_token: str = ""
    ) -> Dict[str, Any]:
        """Generate FCM payload with deep linking"""
        # Construct deep link
        deep_link = self.deep_link_url
        if not deep_link and base_url:
            deep_link = (
                f"{base_url.rstrip('/')}{self.app_route}"
                if self.app_route
                else base_url
            )

        # Base payload
        payload = {
            "to": device_token,
            "notification": {
                "title": self.title,
                "body": self.body,
            },
            "data": {
                "notification_id": str(self.uuid),
                "template_name": self.template.name,
                "message":self.template.body_template,
                "category": self.template.category,
                "type": self.notification_type,
                "object_id":self.object_id,
                "content_type":self.content_type.model_class().__module__ + "." + self.content_type.model_class().__name__,
                "priority": self.priority,
                "route": self.app_route,
                "deep_link": deep_link,
                "timestamp": self.created_at.isoformat(),
                "expires_at": self.expires_at.isoformat() if self.expires_at else "",
                **self.context_data,
            },
            "android": {
                "notification": {
                    "click_action": "FLUTTER_NOTIFICATION_CLICK",
                    "channel_id": f"notifications_{self.template.category}",
                    "priority": (
                        "high" if self.priority in ["high", "urgent"] else "normal"
                    ),
                }
            },
            "apns": {
                "payload": {
                    "aps": {
                        "category": f"NOTIFICATION_{self.template.category.upper()}",
                        "sound": (
                            "default" if self.priority in ["high", "urgent"] else None
                        ),
                        "badge": 1,
                    }
                },
                "fcm_options": {"image": self.context_data.get("image_url", "")},
            },
        }

        return payload

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
    """User notification preferences per template/category"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notification_preferences"
    )
    template = models.ForeignKey(
        NotificationTemplate, on_delete=models.CASCADE, null=True, blank=True
    )
    category = models.CharField(
        max_length=50, blank=True
    )  # For category-wide preferences

    # Channel preferences
    allow_push = models.BooleanField(default=True)
    allow_email = models.BooleanField(default=True)
    allow_sms = models.BooleanField(default=False)
    allow_in_app = models.BooleanField(default=True)

    # Time-based preferences
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    timezone = models.CharField(max_length=50, default="UTC")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [
            ("user", "template"),
            ("user", "category"),
        ]
        verbose_name = _("Notification Preference")
        verbose_name_plural = _("Notification Preferences")

    def __str__(self):
        target = self.template.name if self.template else f"Category: {self.category}"
        return f"{self.user.email} - {target}"


class NotificationGroup(models.Model):
    """Group related notifications together"""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Related object that triggered this group
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey("content_type", "object_id")
    icon = models.CharField(max_length=50, blank=True)  # Icon class or emoji
    color = models.CharField(max_length=7, default="#007bff")  # Hex color

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Notification Group")
        verbose_name_plural = _("Notification Groups")
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class NotificationDelivery(models.Model):
    """Track delivery attempts across different channels"""

    notification = models.ForeignKey(
        Notification, on_delete=models.CASCADE, related_name="deliveries"
    )
    channel = models.CharField(
        choices=NotificationChannel.choices, default=NotificationChannel.PUSH
    )
    # Delivery details
    recipient = models.CharField(
        max_length=255
    )  # Email, phone number, device token, etc.
    status = models.CharField(
        max_length=20, choices=NotificationStatus.choices, default=NotificationStatus.PENDING
    )

    # Attempt tracking
    attempt_count = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=3)
    next_attempt_at = models.DateTimeField(null=True, blank=True)

    # Response tracking
    external_id = models.CharField(max_length=255, blank=True)  # Provider's message ID
    response_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)

    # Timestamps
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notification_deliveries"
        unique_together = ["notification", "channel"]
        indexes = [
            models.Index(fields=["status", "next_attempt_at"]),
            models.Index(fields=["channel", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.notification} via {self.channel}"


class NotificationClickTracking(models.Model):
    """Track clicks on notification links"""

    notification = models.ForeignKey(
        Notification, on_delete=models.CASCADE, related_name="clicks"
    )
    clicked_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        db_table = "notification_click_tracking"


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
        db_table = "notification_analytics"
        unique_together = ["template", "channel", "date"]
