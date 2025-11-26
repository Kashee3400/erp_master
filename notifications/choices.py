from django.db import models
from django.utils.translation import gettext_lazy as _


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
    PARTIALLY_SENT = "partialy_sent", _("Partially Sent")


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


class DeepLinkModule(models.TextChoices):
    """Target app modules for deep links"""

    MEMBER = "member", _("Member App")
    SAHAYAK = "sahayak", _("Sahayak App")
    PES = "pes", _("PES App")
    AUTO = "auto", _("Auto-detect Module")
