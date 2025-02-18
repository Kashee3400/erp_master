from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()
import secrets

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
import secrets


class ApiKey(models.Model):
    key = models.CharField(
        max_length=40, 
        unique=True, 
        editable=False,
        verbose_name=_("API Key"),
        help_text=_("Unique identifier for the API key.")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="api_keys",
        verbose_name=_("User"),
        help_text=_("The user to whom this API key belongs.")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("The date and time when the API key was created.")
    )
    expires_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name=_("Expiration Date"),
        help_text=_("The date and time when the API key expires.")
    )
    valid_from = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name=_("Valid From"),
        help_text=_("The date and time from which the API key becomes valid.")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
        help_text=_("Indicates whether the API key is active.")
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_("Description"),
        help_text=_("A description of the purpose or use case for the API key.")
    )

    # Usage tracking fields
    usage_count = models.IntegerField(
        default=0,
        verbose_name=_("Usage Count"),
        help_text=_("The number of times this API key has been used.")
    )
    max_usage_limit = models.IntegerField(
        null=True, 
        blank=True,
        verbose_name=_("Maximum Usage Limit"),
        help_text=_("The maximum number of requests allowed for this API key.")
    )
    usage_reset_time = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name=_("Usage Reset Time"),
        help_text=_("The time at which the usage count will reset.")
    )
    requests_per_day = models.IntegerField(
        default=1000,
        verbose_name=_("Requests Per Day"),
        help_text=_("The maximum number of requests allowed per day for this API key.")
    )
    requests_per_hour = models.IntegerField(
        default=100,
        verbose_name=_("Requests Per Hour"),
        help_text=_("The maximum number of requests allowed per hour for this API key.")
    )

    # Permissions
    permissions = models.CharField(
        max_length=255,
        blank=True, 
        null=True,
        verbose_name=_("Permissions"),
        help_text=_("The scope of actions allowed by this API key (e.g., 'read', 'write').")
    )
    allowed_ips = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_("Allowed IPs"),
        help_text=_("Comma-separated list of IP addresses allowed to use this API key.")
    )
    allowed_urls = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_("Allowed URLs"),
        help_text=_("Comma-separated list of URLs or endpoints this API key can access.")
    )

    # Audit and security fields
    last_used_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name=_("Last Used At"),
        help_text=_("The date and time when this API key was last used.")
    )
    created_by = models.ForeignKey(
        User,
        related_name="api_keys_created",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Created By"),
        help_text=_("The user who created this API key.")
    )
    last_used_by = models.ForeignKey(
        User,
        related_name="api_keys_used",
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        verbose_name=_("Last Used By"),
        help_text=_("The last user who used this API key.")
    )
    is_revoked = models.BooleanField(
        default=False,
        verbose_name=_("Is Revoked"),
        help_text=_("Indicates whether the API key has been revoked.")
    )
    revoked_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name=_("Revoked At"),
        help_text=_("The date and time when this API key was revoked.")
    )
    revoked_by = models.ForeignKey(
        User,
        related_name="revoked_api_keys",
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        verbose_name=_("Revoked By"),
        help_text=_("The user who revoked this API key.")
    )
    failed_attempts = models.IntegerField(
        default=0,
        verbose_name=_("Failed Attempts"),
        help_text=_("The number of failed authentication attempts using this API key.")
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_hex(20)  # Generate a 40-character API key
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s API Key: {self.key}"

    class Meta:
        verbose_name = _("API Key")
        verbose_name_plural = _("API Keys")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user"], name="user_api_key_idx"),
            models.Index(fields=["is_active"], name="active_api_key_idx"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["key"], name="unique_api_key_constraint"),
        ]


class AssignedMppToFacilitator(models.Model):
    sahayak = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="mpps", 
        verbose_name=_("Facilitator"), 
        blank=True, 
        null=True,
        help_text=_("The user assigned as the facilitator for this MPP.")
    )
    mpp_code = models.CharField(
        max_length=9, 
        unique=True, 
        verbose_name=_("MPP Code"), 
        help_text=_("A unique code assigned to the MPP. This code must be 9 characters long.")
    )
    mpp_ex_code = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        verbose_name=_("MPP External Code"), 
        help_text=_("An external code for the MPP, if applicable.")
    )
    mpp_short_name = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name=_("MPP Short Name"), 
        help_text=_("A short name or abbreviation for the MPP.")
    )
    mpp_name = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name=_("MPP Name"), 
        help_text=_("The full name of the MPP.")
    )
    mpp_type = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        verbose_name=_("MPP Type"), 
        help_text=_("The type/category of the MPP.")
    )
    mpp_logo = models.CharField(
        max_length=150, 
        blank=True, 
        null=True, 
        verbose_name=_("MPP Logo URL"), 
        help_text=_("The URL or path to the logo image of the MPP.")
    )
    mpp_icon = models.CharField(
        max_length=150, 
        blank=True, 
        null=True, 
        verbose_name=_("MPP Icon URL"), 
        help_text=_("The URL or path to the icon image of the MPP.")
    )
    mpp_punch_line = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name=_("MPP Punch Line"), 
        help_text=_("A catchy tagline or punch line associated with the MPP.")
    )
    mpp_opening_date = models.DateTimeField(
        blank=True, 
        null=True, 
        verbose_name=_("MPP Opening Date"), 
        help_text=_("The date and time when the MPP is officially opened.")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_("Created At"), 
        help_text=_("The date and time when the MPP assignment was created.")
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name=_("Updated At"), 
        help_text=_("The date and time when the MPP assignment was last updated.")
    )

    class Meta:
        db_table = 'assigned_mpp_to_facilitator'  # Specify the table name in the database
        ordering = ['-created_at']  # Default ordering when queried (newest first)
        verbose_name = _('Assigned MPP to Facilitator')  # Singular form of model name
        verbose_name_plural = _('Assigned MPPs to Facilitators')  # Plural form of model name
        constraints = [
            models.UniqueConstraint(
                fields=['mpp_code'], 
                name='unique_mpp_code'  # Unique constraint for mpp_code
            ),
        ]

    def __str__(self):
        return f"{self.mpp_code} - {self.mpp_name}"
