# models.py
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.utils import timezone
import json
from ..choices import (
    RoleType,
    RequestStatus,
    RequestTypeChoices,
    ChangeType,
    DocumentTypeChoice,
)


class BaseModel(models.Model):
    """Base model with common fields"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True,null=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="%(class)s_created",
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="%(class)s_updated",
        null=True,
        blank=True,
    )
    is_deleted = models.BooleanField(
        default=False,
        help_text=_("Indicates whether this entry has been deleted."),
        verbose_name=_("Deleted"),
    )

    class Meta:
        abstract = True


class UpdateRequest(BaseModel):
    """
    Streamlined update request model focusing on core functionality
    """

    phone_validator = RegexValidator(
        regex=r"^\+?\d{10,15}$",
        message=_(
            "Enter a valid WhatsApp number with country code (e.g., +1234567890)."
        ),
    )
    request_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("Request ID"),
        help_text=_("Auto-generated unique request identifier (e.g., REQ-2025-001234)"),
        editable=False,
        blank=True,
        null=True
    )
    mpp_code = models.CharField(
        max_length=9,
        blank=True,
        null=True,
        verbose_name=_("MPP Code"),
        help_text=_(
            "A unique code assigned to the MPP. This code must be 9 characters long."
        ),
    )
    mpp_ex_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("MPP External Code"),
        help_text=_("An external code for the MPP, if applicable."),
    )
    mcc_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("MPP Short Name"),
        help_text=_("A short name or abbreviation for the MPP."),
    )
    mpp_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("MPP Name"),
        help_text=_("The full name of the MPP."),
    )

    # Member identification
    member_code = models.CharField(
        max_length=20,
        verbose_name=_("Member Code"),
        blank=True,
        null=True,
        help_text=_("Unique identifier for the member."),
    )
    member_ex_code = models.CharField(
        max_length=20,
        verbose_name=_("Member Ex Code"),
        blank=True,
        null=True,
        help_text=_("Unique identifier for the member."),
    )

    member_name = models.CharField(
        max_length=100,
        verbose_name=_("Member Name"),
        help_text=_("Full name of the member."),
        blank=True,
        null=True,

    )

    mobile_number = models.CharField(
        max_length=20,
        validators=[phone_validator],
        verbose_name=_("Mobile Number"),
        help_text=_("Member's  contact number."),
        blank=True,
        null=True,

    )

    # Request details
    role_type = models.CharField(
        max_length=10, choices=RoleType.choices, verbose_name=_("Role Type")
    )

    request_type = models.CharField(
        max_length=10, choices=RequestTypeChoices.choices, verbose_name=_("Update Type")
    )

    status = models.CharField(
        max_length=10,
        choices=RequestStatus.choices,
        default=RequestStatus.PENDING,
        verbose_name=_("Status"),
    )
    # Bank update fields
    new_account_number = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="New Account Number"
    )

    new_account_holder_name = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="New Account Holder Name"
    )

    bank_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Bank Name",
        help_text="Enter the name of the bank (e.g., State Bank of India)",
    )

    branch_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Branch Name",
        help_text="Enter the branch name (e.g., Main Branch, Jaipur)",
    )

    ifsc = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="IFSC Code",
        help_text="Enter the IFSC code associated with this bank branch (e.g., SBIN0001234)",
    )

    # Review fields
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="reviewed_requests",
        verbose_name=_("Reviewed By"),
    )

    reviewed_at = models.DateTimeField(
        blank=True, null=True, verbose_name=_("Reviewed At")
    )

    ho_comments = models.TextField(blank=True, null=True, verbose_name=_("HO Comments"))

    rejection_reason = models.TextField(
        blank=True, null=True, verbose_name=_("Rejection Reason")
    )

    class Meta:
        verbose_name = _("Update Request")
        verbose_name_plural = _("Update Requests")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["member_code", "status"]),
            models.Index(fields=["created_by", "created_at"]),
            models.Index(fields=["status", "request_type"]),
        ]

    def __str__(self):
        return f"{self.member_name} - {self.get_request_type_display()} ({self.get_status_display()})"

    @classmethod
    def generate_request_id(cls):
        """Generate a unique request ID"""
        from datetime import datetime

        # Get current year
        current_year = datetime.now().year

        # Get the last request ID for this year
        last_request = (
            cls.objects.filter(request_id__startswith=f"REQ-{current_year}-")
            .order_by("-request_id")
            .first()
        )

        if last_request:
            # Extract the sequence number and increment
            try:
                last_sequence = int(last_request.request_id.split("-")[-1])
                next_sequence = last_sequence + 1
            except (ValueError, IndexError):
                next_sequence = 1
        else:
            next_sequence = 1

        # Format: REQ-YYYY-NNNNNN (6-digit sequence)
        return f"REQ-{current_year}-{next_sequence:06d}"

    def save(self, *args, **kwargs):
        if not self.request_id:  # Only generate if not already set
            self.request_id = self.generate_request_id()
        return super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        # Custom validation logic
        if self.status == RequestStatus.UPDATED and not self.reviewed_by:
            raise ValidationError(_("Approved requests must have a reviewer."))

        if self.status == RequestStatus.REJECTED and not self.rejection_reason:
            raise ValidationError(_("Rejected requests must have a rejection reason."))

    def approve(self, reviewed_by, comments=None):
        """Approve the request"""
        self.status = RequestStatus.UPDATED
        self.reviewed_by = reviewed_by
        self.reviewed_at = timezone.now()
        if comments:
            self.ho_comments = comments
        self.save()

    def reject(self, reviewed_by, reason, comments=None):
        """Reject the request"""
        self.status = RequestStatus.REJECTED
        self.reviewed_by = reviewed_by
        self.reviewed_at = timezone.now()
        self.rejection_reason = reason
        if comments:
            self.ho_comments = comments
        self.save()


class UpdateRequestData(BaseModel):
    """
    Flexible data storage for update request changes
    """

    request = models.ForeignKey(
        UpdateRequest, on_delete=models.CASCADE, related_name="request_data"
    )

    field_name = models.CharField(max_length=100, verbose_name=_("Field Name"))

    old_value = models.TextField(blank=True, null=True, verbose_name=_("Old Value"))

    new_value = models.TextField(blank=True, null=True, verbose_name=_("New Value"))

    data_type = models.CharField(
        max_length=20,
        choices=[
            ("text", _("Text")),
            ("number", _("Number")),
            ("file", _("File")),
            ("json", _("JSON")),
        ],
        default="text",
        verbose_name=_("Data Type"),
    )

    class Meta:
        verbose_name = _("Update Request Data")
        verbose_name_plural = _("Update Request Data")
        unique_together = ["request", "field_name"]
        indexes = [
            models.Index(fields=["request", "field_name"]),
        ]

    def __str__(self):
        return f"{self.request.member_name} - {self.field_name}"

    def get_parsed_value(self, value):
        """Parse value based on data type"""
        if not value:
            return None

        if self.data_type == "json":
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        elif self.data_type == "number":
            try:
                return float(value) if "." in value else int(value)
            except (ValueError, TypeError):
                return value
        return value

    @property
    def parsed_old_value(self):
        return self.get_parsed_value(self.old_value)

    @property
    def parsed_new_value(self):
        return self.get_parsed_value(self.new_value)


class UpdateRequestDocument(BaseModel):
    """
    Document attachments for update requests
    """

    request = models.ForeignKey(
        UpdateRequest, on_delete=models.CASCADE, related_name="documents"
    )
    document_type = models.CharField(
        max_length=50,
        choices=DocumentTypeChoice.choices,
        verbose_name=_("Document Type"),
    )

    file = models.FileField(
        upload_to="update_requests/%Y/%m/%d/", verbose_name=_("Document File")
    )

    original_filename = models.CharField(
        max_length=255, verbose_name=_("Original Filename")
    )

    file_size = models.PositiveIntegerField(verbose_name=_("File Size (bytes)"))

    content_type = models.CharField(max_length=100, verbose_name=_("Content Type"))

    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Update Request Document")
        verbose_name_plural = _("Update Request Documents")
        indexes = [
            models.Index(fields=["request", "document_type"]),
        ]

    def __str__(self):
        return f"{self.request.member_name} - {self.get_document_type_display()}"

    def clean(self):
        super().clean()
        # Validate file size (10MB limit)
        if self.file and self.file.size > 10 * 1024 * 1024:
            raise ValidationError(_("File size cannot exceed 10MB."))

        # Validate file type
        allowed_types = ["application/pdf", "image/jpeg", "image/png", "image/jpg"]
        if self.content_type and self.content_type not in allowed_types:
            raise ValidationError(_("Only PDF and image files are allowed."))


class UpdateRequestHistory(BaseModel):
    """
    Comprehensive history tracking for update requests
    """

    request = models.ForeignKey(
        UpdateRequest, on_delete=models.CASCADE, related_name="history"
    )

    change_type = models.CharField(
        max_length=20, choices=ChangeType.choices, verbose_name=_("Change Type")
    )

    field_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("Field Name")
    )

    old_value = models.TextField(blank=True, null=True, verbose_name=_("Old Value"))

    new_value = models.TextField(blank=True, null=True, verbose_name=_("New Value"))

    changed_by = models.ForeignKey(
        User, on_delete=models.PROTECT, verbose_name=_("Changed By")
    )

    change_reason = models.TextField(
        blank=True, null=True, verbose_name=_("Change Reason")
    )

    ip_address = models.GenericIPAddressField(
        blank=True, null=True, verbose_name=_("IP Address")
    )

    user_agent = models.TextField(blank=True, null=True, verbose_name=_("User Agent"))

    metadata = models.JSONField(
        default=dict, blank=True, verbose_name=_("Additional Metadata")
    )

    class Meta:
        verbose_name = _("Update Request History")
        verbose_name_plural = _("Update Request Histories")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["request", "created_at"]),
            models.Index(fields=["changed_by", "created_at"]),
            models.Index(fields=["change_type", "created_at"]),
        ]

    def __str__(self):
        return f"{self.request.member_name} - {self.get_change_type_display()} ({self.created_at})"


class UpdateRequestManager(models.Manager):
    """Custom manager for UpdateRequest with useful methods"""

    def pending(self):
        return self.filter(status=RequestStatus.PENDING)

    def approved(self):
        return self.filter(status=RequestStatus.UPDATED)

    def rejected(self):
        return self.filter(status=RequestStatus.REJECTED)

    def by_created_by(self, created_by):
        return self.filter(created_by=created_by)

    def by_member_code(self, member_code):
        return self.filter(member_code=member_code)

    def mobile_updates(self):
        return self.filter(request_type=RequestTypeChoices.MOBILE)

    def bank_updates(self):
        return self.filter(request_type=RequestTypeChoices.BANK)


# Add the manager to UpdateRequest
UpdateRequest.add_to_class("objects", UpdateRequestManager())
