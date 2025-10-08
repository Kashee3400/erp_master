import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class ExcelUploadSession(models.Model):
    """
    Tracks Excel file upload sessions.
    Used for temporary storage, auditing, and processing status.
    """

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        PROCESSING = "processing", _("Processing")
        SUCCESS = "success", _("Success")
        FAILED = "failed", _("Failed")
        QUEUED = "queued", _("Queued")

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    filename = models.CharField(
        max_length=255,
        verbose_name=_("File Name"),
        help_text=_("Original filename of the uploaded Excel file"),
    )
    filesize = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("File size"),
        help_text=_("Original filesize of the uploaded Excel file"),
    )
    task_id = models.CharField(
        max_length=255,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("Task ID"),
        help_text=_("Task id of the uploaded Excel file"),
    )
    file = models.FileField(
        upload_to="excel/%Y/%m/%d/",
        null=True,
        blank=True,
        verbose_name=_("File"),
        help_text=_("Path to the uploaded file in storage"),
    )
    uploaded_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Uploaded by"),
        related_name="excel_uploads",
        help_text=_("User who initiated the upload"),
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name=_("Status"),
    )
    processed_at = models.DateTimeField(
        null=True, blank=True, help_text=_("Timestamp when processing finished")
    )
    processed = models.BooleanField(default=False)
    total_rows = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name=_("Total rows")
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Error message"),
        help_text=_("Any error details if processing failed"),
    )
    sheets_data = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        verbose_name=_("Sheets data"),
        help_text=_("Stores preview/sample data or metadata from sheets"),
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        verbose_name=_("Metadata"),
        help_text=_("Extra info about the upload (columns, mapping, etc.)"),
    )

    class Meta:
        ordering = ["-uploaded_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["uploaded_at"]),
        ]
        verbose_name = _("Excel Upload Session")
        verbose_name_plural = _("Excel Upload Sessions")

    def mark_processed(self, success=True, total_rows=0, error=None):
        """Utility to update session status after processing."""
        self.status = self.Status.SUCCESS if success else self.Status.FAILED
        self.processed = True
        self.total_rows = total_rows
        self.error_message = error
        from django.utils.timezone import now

        self.processed_at = now()
        self.save(update_fields=["status", "processed", "total_rows", "error_message", "processed_at"])

    def __str__(self):
        return f"{self.filename} ({self.get_status_display()})"
