import uuid
from typing import Dict, Any
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import pytz
from django.template import Template, Context, TemplateSyntaxError
from typing import Dict, Any, Optional, List
from datetime import datetime
from .choices import (
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
    NotificationType,
    DeepLinkModule,
)
import uuid
from django.core.exceptions import ValidationError
from datetime import timedelta
import json

User = get_user_model()


class NotificationTemplate(models.Model):
    """
    Modern, scalable notification template with multi-channel support
    and declarative deep-link configuration.

    Design Principles:
    - Separation of concerns: Templates define WHAT to send, services define HOW
    - Declarative configuration: Deep links configured via JSON, not code
    - Multi-lingual support: Content templates per locale
    - Channel flexibility: Support for push, email, SMS, WhatsApp, in-app
    - Future-proof: Extensible JSON fields for new features
    """

    # ==========================================
    # IDENTIFICATION & CATEGORIZATION
    # ==========================================

    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name=_("Template Name"),
        help_text=_("Unique identifier (e.g., 'order_confirmed', 'payment_failed')"),
    )

    category = models.CharField(
        max_length=50,
        db_index=True,
        verbose_name=_("Category"),
        help_text=_(
            "Grouping category (e.g., 'orders', 'payments', 'users', 'system')"
        ),
    )

    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Internal description of this template's purpose and usage"),
    )

    # ==========================================
    # CONTENT TEMPLATES (Multi-lingual)
    # ==========================================

    locale = models.CharField(
        max_length=10,
        default="en",
        db_index=True,
        verbose_name=_("Locale"),
        help_text=_("Language/locale code (e.g., 'en', 'hi', 'en-US')"),
    )

    # Push Notification / In-App Content
    title_template = models.CharField(
        max_length=255,
        verbose_name=_("Title Template"),
        help_text=_(
            "Django template for notification title. Example: 'Order #{{ order.id }} confirmed'"
        ),
    )

    body_template = models.TextField(
        verbose_name=_("Body Template"),
        help_text=_(
            "Django template for notification body. Supports {{ variables }} and {% tags %}"
        ),
    )

    # Email-specific Content
    email_subject_template = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Email Subject Template"),
        help_text=_("Template for email subject line"),
    )

    email_body_template = models.TextField(
        blank=True,
        verbose_name=_("Email Body Template"),
        help_text=_("Django template for email body (can include HTML)"),
    )

    email_is_html = models.BooleanField(
        default=True,
        verbose_name=_("Email is HTML"),
        help_text=_("Whether email body should be rendered as HTML"),
    )

    # SMS-specific Content
    sms_template = models.CharField(
        max_length=160,
        blank=True,
        verbose_name=_("SMS Template"),
        help_text=_("Template for SMS (max 160 chars recommended)"),
    )

    # WhatsApp-specific Content
    whatsapp_template = models.TextField(
        blank=True,
        verbose_name=_("WhatsApp Template"),
        help_text=_("Template for WhatsApp message"),
    )

    # ==========================================
    # CHANNEL CONFIGURATION
    # ==========================================

    enabled_channels = models.JSONField(
        default=list,
        verbose_name=_("Enabled Channels"),
        help_text=_(
            "List of channels this template supports. Example: ['push', 'email', 'sms']"
        ),
    )

    channel_config = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Channel-specific Configuration"),
        help_text=_(
            "Optional per-channel settings. Example: "
            "{'email': {'from_name': 'Kashee Support', 'reply_to': 'support@kashee.com'}, "
            "'push': {'sound': 'default', 'badge': 1}}"
        ),
    )

    # ==========================================
    # NOTIFICATION BEHAVIOR
    # ==========================================

    default_priority = models.CharField(
        max_length=10,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
        verbose_name=_("Default Priority"),
    )

    notification_type = models.CharField(
        max_length=10,
        choices=NotificationType.choices,
        default=NotificationType.INFO,
        verbose_name=_("Notification Type"),
        help_text=_("Visual type for UI rendering (color, icon, etc.)"),
    )

    # Action buttons (for push notifications)
    action_buttons = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Action Buttons"),
        help_text=_(
            "List of action buttons for push notifications. Example: "
            "[{'label': 'View Order', 'action': 'open_order'}, "
            "{'label': 'Dismiss', 'action': 'dismiss'}]"
        ),
    )

    # ==========================================
    # DEEP LINK CONFIGURATION (Declarative)
    # ==========================================

    deeplink_config = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Deep Link Configuration"),
        help_text=_(
            "Declarative deep link configuration. DeepLinkService will use this to generate links. "
            "Example: {"
            "  'module': 'member', "
            "  'url_name': 'order:detail', "
            "  'route_template': 'orders/{{ order.id }}/', "
            "  'fallback_template': 'https://kashee.com/orders/{{ order.id }}/', "
            "  'inapp_route': 'order/{{ order.id }}', "
            "  'deeplink_type': 'order_detail', "
            "  'expires_after': 7, "
            "  'max_uses': 1, "
            "  'metadata': {'source': 'notification'}"
            "}"
        ),
    )

    # ==========================================
    # TEMPLATE VARIABLES & VALIDATION
    # ==========================================

    required_context_vars = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Required Context Variables"),
        help_text=_(
            "List of required variables for this template. Example: ['order', 'user', 'amount']. "
            "Used for validation and documentation."
        ),
    )

    sample_context = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Sample Context"),
        help_text=_(
            "Sample context data for testing/preview. Example: "
            "{'order': {'id': 123, 'total': 999}, 'user': {'name': 'John'}}"
        ),
    )

    # ==========================================
    # ANALYTICS & TRACKING
    # ==========================================

    tracking_enabled = models.BooleanField(
        default=True,
        verbose_name=_("Enable Tracking"),
        help_text=_(
            "Whether to track opens, clicks, and conversions for this template"
        ),
    )

    analytics_metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Analytics Metadata"),
        help_text=_(
            "Additional metadata for analytics. Example: {'campaign': 'summer_sale', 'cohort': 'premium'}"
        ),
    )

    # ==========================================
    # SCHEDULING & THROTTLING
    # ==========================================

    throttle_config = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Throttle Configuration"),
        help_text=_(
            "Rate limiting config. Example: "
            "{'max_per_user_per_day': 3, 'min_interval_minutes': 60}"
        ),
    )

    quiet_hours = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Quiet Hours"),
        help_text=_(
            "Do not send during these hours. Example: "
            "{'enabled': true, 'start': '22:00', 'end': '08:00', 'timezone': 'Asia/Kolkata'}"
        ),
    )

    # ==========================================
    # METADATA & STATUS
    # ==========================================

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_("Is Active"),
    )

    version = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Version"),
        help_text=_("Template version for A/B testing and rollbacks"),
    )

    tags = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Tags"),
        help_text=_(
            "Tags for filtering and organization. Example: ['transactional', 'high-priority']"
        ),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_templates",
        verbose_name=_("Created By"),
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_templates",
        verbose_name=_("Updated By"),
    )

    class Meta:
        db_table = "tbl_notification_templates"
        verbose_name = _("Notification Template")
        verbose_name_plural = _("Notification Templates")
        ordering = ["category", "name", "locale"]
        indexes = [
            models.Index(fields=["category", "name"]),
            models.Index(fields=["locale", "is_active"]),
            models.Index(fields=["category", "is_active"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "locale"], name="unique_template_per_locale"
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.locale}) - {self.category}"

    def clean(self):
        """Validate template configuration"""
        errors = {}

        # Validate Django templates
        try:
            Template(self.title_template)
        except TemplateSyntaxError as e:
            errors["title_template"] = f"Invalid template syntax: {e}"

        try:
            Template(self.body_template)
        except TemplateSyntaxError as e:
            errors["body_template"] = f"Invalid template syntax: {e}"

        # Validate enabled channels
        if not isinstance(self.enabled_channels, list):
            errors["enabled_channels"] = "Must be a list of channel names"
        else:
            valid_channels = [c.value for c in NotificationChannel]
            invalid = [ch for ch in self.enabled_channels if ch not in valid_channels]
            if invalid:
                errors["enabled_channels"] = f"Invalid channels: {invalid}"

        # Validate channel-specific templates
        if "email" in self.enabled_channels:
            if not self.email_subject_template or not self.email_body_template:
                errors["email_subject_template"] = (
                    "Email templates required when email channel is enabled"
                )

        if "sms" in self.enabled_channels and not self.sms_template:
            errors["sms_template"] = "SMS template required when SMS channel is enabled"

        if "whatsapp" in self.enabled_channels and not self.whatsapp_template:
            errors["whatsapp_template"] = (
                "WhatsApp template required when WhatsApp channel is enabled"
            )

        # Validate deeplink_config structure
        if self.deeplink_config:
            valid_keys = {
                "module",
                "url_name",
                "route_template",
                "fallback_template",
                "inapp_route",
                "deeplink_type",
                "expires_after",
                "max_uses",
                "metadata",
            }
            invalid_keys = set(self.deeplink_config.keys()) - valid_keys
            if invalid_keys:
                errors["deeplink_config"] = (
                    f"Invalid keys in deeplink_config: {invalid_keys}"
                )

            if "module" in self.deeplink_config:
                if self.deeplink_config["module"] not in [
                    m.value for m in DeepLinkModule
                ]:
                    errors["deeplink_config"] = (
                        f"Invalid module: {self.deeplink_config['module']}"
                    )

        if errors:
            raise ValidationError(errors)

    def render_content(
        self, context: Dict[str, Any], channel: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Render template content with context variables for specified channel.

        Args:
            context: Dictionary of template variables
            channel: Specific channel to render for (optional)

        Returns:
            Dictionary containing rendered content for requested channel(s)
        """
        django_context = Context(context)
        rendered = {}

        # Always render title and body (used by push, in-app)
        rendered["title"] = Template(self.title_template).render(django_context)
        rendered["body"] = Template(self.body_template).render(django_context)

        # Render channel-specific content
        if not channel or channel == "email":
            if self.email_subject_template:
                rendered["email_subject"] = Template(
                    self.email_subject_template
                ).render(django_context)
            if self.email_body_template:
                rendered["email_body"] = Template(self.email_body_template).render(
                    django_context
                )

        if not channel or channel == "sms":
            if self.sms_template:
                rendered["sms"] = Template(self.sms_template).render(django_context)

        if not channel or channel == "whatsapp":
            if self.whatsapp_template:
                rendered["whatsapp"] = Template(self.whatsapp_template).render(
                    django_context
                )

        return rendered

    def get_deeplink_config(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get declarative deep link configuration for DeepLinkService.

        This method returns the raw configuration that DeepLinkService will use
        to generate the actual deep link. It renders any template strings in the
        config using the provided context.

        Args:
            context: Template context for rendering route/fallback templates

        Returns:
            Dictionary containing deep link configuration, or None if not configured

        Example return value:
            {
                "module": "member",
                "url_name": "order:detail",
                "route_template": "orders/{{ order.id }}/",
                "route_params": {"order_id": 123},
                "fallback_template": "https://kashee.com/orders/123/",
                "inapp_route": "order/123",  # Rendered
                "deeplink_type": "order_detail",
                "expires_after": 7,
                "max_uses": 1,
                "metadata": {"source": "notification"}
            }
        """
        if not self.deeplink_config:
            return None

        config = self.deeplink_config.copy()
        django_context = Context(context)

        # Render template strings in config
        if "route_template" in config:
            config["route_template"] = Template(config["route_template"]).render(
                django_context
            )

        if "fallback_template" in config:
            config["fallback_template"] = Template(config["fallback_template"]).render(
                django_context
            )

        if "inapp_route" in config:
            config["inapp_route"] = Template(config["inapp_route"]).render(
                django_context
            )

        # Extract route parameters from context for url_name resolution
        config["route_params"] = {
            k: v
            for k, v in context.items()
            if k in ["pk", "id", "slug", "uuid", "object_id"] or k.endswith("_id")
        }

        return config

    def validate_context(self, context: Dict[str, Any]) -> List[str]:
        """
        Validate that all required context variables are present.

        Args:
            context: Context dictionary to validate

        Returns:
            List of missing variable names (empty if all present)
        """
        missing = []
        for var in self.required_context_vars:
            if var not in context:
                missing.append(var)
        return missing

    def preview(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a preview of this template with sample or provided context.

        Args:
            context: Optional context to use (defaults to sample_context)

        Returns:
            Dictionary containing rendered content and deep link config
        """
        preview_context = context or self.sample_context or {}

        return {
            "name": self.name,
            "category": self.category,
            "locale": self.locale,
            "channels": self.enabled_channels,
            "priority": self.default_priority,
            "type": self.notification_type,
            "content": self.render_content(preview_context),
            "deeplink_config": self.get_deeplink_config(preview_context),
            "context_used": preview_context,
        }


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

    def make_json_safe(self, context_data):
        import decimal
        import datetime

        if isinstance(context_data, dict):
            return {k: self.make_json_safe(v) for k, v in context_data.items()}
        elif isinstance(context_data, list):
            return [self.make_json_safe(v) for v in context_data]
        elif isinstance(context_data, decimal.Decimal):
            return float(context_data)
        elif isinstance(context_data, (datetime.date, datetime.datetime)):
            return context_data.isoformat()
        else:
            return context_data

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
                },
                "data": {
                    "notification_id": str(self.uuid),
                    "template_name": self.template.name,
                    "message": self.template.body_template,
                    "category": self.template.category,
                    "type": self.notification_type,
                    "object_id": str(self.object_id),
                    "priority": str(self.priority),
                    "route": self.app_route or "",
                    "deep_link": deep_link or "",
                    "timestamp": self.created_at.isoformat() if self.created_at else "",
                    "expires_at": (
                        self.expires_at.isoformat() if self.expires_at else ""
                    ),
                    **safe_context,
                },
                "android": {
                    "notification": {
                        "click_action": "FLUTTER_NOTIFICATION_CLICK",
                        "channel_id": "kashee_channel",
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
        max_length=200,
        choices=NotificationChannel.choices,
        default=NotificationChannel.PUSH,
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


class DeepLink(models.Model):
    """
    Universal deep link mapping model with production-ready features.
    """

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        REVOKED = "revoked", "Revoked"
        CONSUMED = "consumed", "Consumed"

    class Module(models.TextChoices):
        MEMBER = "member", "Member App"
        SAHAYAK = "sahayak", "Sahayak App"
        PES = "pes", "PES App"

    # Core fields
    token = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False, db_index=True
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deep_links",
        db_index=True,
    )

    # Deep link details
    deep_link = models.CharField(max_length=512, db_index=True)  # App deep link URL
    deep_path = models.CharField(max_length=512, blank=True)  # in app path
    module = models.CharField(
        max_length=50, choices=Module.choices, default=Module.MEMBER, db_index=True
    )

    # Platform-specific identifiers
    android_package = models.CharField(max_length=200)
    ios_bundle_id = models.CharField(max_length=200, blank=True)

    # Fallback and status
    fallback_url = models.URLField(blank=True, max_length=512)  # Web URL
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True
    )

    # Expiry management
    expires_at = models.DateTimeField(null=True, blank=True, db_index=True)

    # Usage tracking
    max_uses = models.PositiveIntegerField(default=0, help_text="0 = unlimited")
    use_count = models.PositiveIntegerField(default=0)
    last_accessed_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    meta = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "deep_links"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status", "created_at"]),
            models.Index(fields=["module", "status"]),
            models.Index(fields=["expires_at", "status"]),
        ]

    def __str__(self):
        return f"DeepLink {self.token} → {self.deep_link} [{self.status}]"

    def clean(self):
        """Validate deep link structure."""
        if "://" not in self.deep_link:
            raise ValidationError("Invalid deep link format. Must contain '://'")

        scheme = self.deep_link.split("://")[0]
        expected_schemes = {
            self.Module.MEMBER: "kashee-member",
            self.Module.SAHAYAK: "kashee-sahayak",
            self.Module.PES: "kashee-pes",
        }

        if self.module in expected_schemes:
            if scheme != expected_schemes[self.module]:
                raise ValidationError(
                    f"Scheme '{scheme}' doesn't match module '{self.module}'"
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def scheme(self) -> str:
        """Extract scheme from deep link."""
        return self.deep_link.split("://")[0] if "://" in self.deep_link else ""

    @property
    def path(self) -> str:
        """Extract path from deep link."""
        return self.deep_link.split("://")[1] if "://" in self.deep_link else ""

    @property
    def is_expired(self) -> bool:
        """Check if link has expired."""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    @property
    def is_exhausted(self) -> bool:
        """Check if max uses reached."""
        if self.max_uses == 0:
            return False
        return self.use_count >= self.max_uses

    @property
    def is_valid(self) -> bool:
        """Check if link is valid and usable."""
        return (
            self.status == self.Status.ACTIVE
            and not self.is_expired
            and not self.is_exhausted
        )

    def increment_use(self):
        """Record a link access."""
        self.use_count += 1
        self.last_accessed_at = timezone.now()

        # Auto-consume if max uses reached
        if self.is_exhausted:
            self.status = self.Status.CONSUMED

        self.save(update_fields=["use_count", "last_accessed_at", "status"])

    def revoke(self):
        """Manually revoke the link."""
        self.status = self.Status.REVOKED
        self.save(update_fields=["status", "updated_at"])

    def extend_expiry(self, days: int = 7):
        """Extend expiry by specified days."""
        if self.expires_at:
            self.expires_at += timedelta(days=days)
        else:
            self.expires_at = timezone.now() + timedelta(days=days)
        self.save(update_fields=["expires_at", "updated_at"])
