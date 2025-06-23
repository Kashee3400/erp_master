from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxLengthValidator
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class NotificationType(models.TextChoices):
    INFO = "info", _("Information")
    WARNING = "warning", _("Warning")
    ALERT = "alert", _("Alert")
    SUCCESS = "success", _("Success")


class NotificationMedium(models.TextChoices):
    SYSTEM = "system", _("System")
    FCM = "fcm", _("Firebase Push")
    EMAIL = "email", _("Email")


class AppNotification(models.Model):
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
        """Convert the notification to a dictionary payload for frontend."""
        return {
            "title": self.title,
            "message": self.message,
            "route": self.route,
            "id": str(self.object_id),
            "model": self.model,
            "customKey": self.custom_key or "",
            "is_subroute": str(self.is_subroute).lower(),
            "notification_type": self.notification_type,
        }

    def __str__(self):
        return f"[{self.notification_type.upper()}] {self.title} -> {self.recipient}"
