from django.db import models
from django.utils import timezone
import uuid
from django.conf import settings
from django.utils.translation import gettext_lazy as _, get_language
from datetime import timedelta
from django.core.validators import MaxValueValidator, MinValueValidator
# ------------------------------
# STATUS: Internal codes + labels
# ------------------------------
STATUS_CHOICES = [
    ("open", _("Open")),
    ("assigned", _("Assigned")),
    ("in progress", _("In Progress")),
    ("resolved", _("Resolved")),
    ("closed", _("Closed")),
    ("reopened", _("Reopened")),
]

# ------------------------------
# Priority Choices
# ------------------------------
PRIORITY_CHOICES = (
    ("low", _("Low")),
    ("medium", _("Medium")),
    ("high", _("High")),
    ("critical", _("Critical")),
)

# ------------------------------
# ALLOWED STATUS TRANSITIONS
# ------------------------------
# ALLOWED_TRANSITIONS = {
#     "open": ["assigned", "closed", "reopened"],
#     "assigned": ["in_progress", "closed"],
#     "in progress": ["resolved", "closed"],
#     "resolved": ["reopened", "closed"],
#     "closed": ["reopened"],
#     "reopened": ["assigned", "closed"],
# }
ALLOWED_TRANSITIONS = {
    "open": ["assigned"],  # Must be assigned first
    "assigned": ["in_progress", "reopened"],  # Start work or reopen due to rejection
    "in_progress": ["resolved", "reopened"],  # Work done or need re-evaluation
    "resolved": ["closed", "reopened"],  # Verification leads to closure or reopen
    "closed": ["reopened"],  # If problem resurfaces
    "reopened": ["assigned"],  # Must reassign to begin the loop again
}



def is_valid_transition(current, new):
    return new in ALLOWED_TRANSITIONS.get(current, [])


# ------------------------------
# MAIN MODEL
# ------------------------------
from django.core.exceptions import ValidationError


class Feedback(models.Model):
    feedback_id = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        editable=False,
        verbose_name=_("Feedback ID"),
        help_text=_("Unique identifier for this feedback entry. Auto-generated."),
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_sent_feedbacks",
        verbose_name=_("Sender"),
        help_text=_("User who submitted the feedback."),
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_assigned_feedbacks",
        verbose_name=_("Assigned To"),
        help_text=_("User assigned to review or resolve this feedback."),
    )

    assigned_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Assigned At"),
        help_text=_("Timestamp when the feedback was assigned."),
    )

    mpp_code = models.CharField(
        max_length=9,
        blank=True,
        null=True,
        verbose_name=_("MPP Code"),
        help_text=_("MPP Code related to the feedback. Must be exactly 9 characters."),
    )

    mcc_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("MCC Code"),
        help_text=_("Milk Collection Center code linked to this feedback."),
    )

    member_code = models.CharField(
        blank=True,
        null=True,
        max_length=50,
        verbose_name=_("Member Code"),
        help_text=_("Unique identifier for the member associated with this feedback."),
    )

    member_tr_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Member Transaction Code"),
        help_text=_("Transaction code related to the member, if applicable."),
    )

    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Member Name"),
        help_text=_("Full name of the member."),
    )

    mobile_no = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name=_("Mobile Number"),
        help_text=_("Contact mobile number of the member."),
    )

    status = models.CharField(
        max_length=100,
        choices=STATUS_CHOICES,
        default="open",
        verbose_name=_("Feedback Status"),
        help_text=_("Current status of the feedback."),
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="medium",
        verbose_name=_("Priority"),
        help_text=_("Priority level of the feedback."),
    )

    category = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Category"),
        help_text=_("Category or type of feedback."),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("Timestamp when the feedback was created."),
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Resolved At"),
        help_text=_("Timestamp when the feedback was marked as resolved."),
    )
    progress = models.FloatField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        verbose_name=_("Progress"),
        help_text=_("Progress of feedback resolution in percentage."),
    )

    rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Rating"),
        help_text=_("Rating given by the user after feedback resolution."),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Last Updated At"),
        help_text=_("Timestamp of the most recent update to the feedback."),
    )

    message = models.TextField(
        verbose_name=_("Message"),
        help_text=_("Detailed description or content of the feedback."),
    )
    @property
    def response_time(self) -> timedelta | None:
        """Time between creation and assignment if assigned; else None"""
        if self.assigned_at and self.created_at:
            return self.assigned_at - self.created_at
        return None

    @property
    def resolution_time(self) -> timedelta | None:
        """Time between assignment and resolution"""
        if self.assigned_at and self.resolved_at:
            return self.resolved_at - self.assigned_at
        return None

    @property
    def full_resolution_time(self) -> timedelta | None:
        """Time from creation to resolution"""
        if self.created_at and self.resolved_at:
            return self.resolved_at - self.created_at
        return None
    
    deleted = models.BooleanField(
        default=False,
        verbose_name=_("Is Deleted"),
        help_text=_("Indicates whether this feedback is deleted (soft delete)."),
    )

    class Meta:
        verbose_name = _("Feedback")
        verbose_name_plural = _("Feedbacks")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Feedback #{self.feedback_id or 'Unassigned'} by {self.sender}"

    def clean(self):
        super().clean()
        if self.rating and self.status != 'resolved':
            raise ValidationError("Rating can only be given when the feedback is resolved.")

        # Prevent resolved_at if status is not resolved or closed
        if self.resolved_at and self.status not in ["resolved", "closed"]:
            raise ValidationError(
                {
                    "resolved_at": _(
                        "Cannot set resolved time if feedback is not resolved or closed."
                    )
                }
            )

        # Prevent assigning without assigned_to
        if self.assigned_at and not self.assigned_to:
            raise ValidationError(
                {
                    "assigned_to": _(
                        "Assigned to cannot be empty when assigned time is set."
                    )
                }
            )

    def __str__(self):
        return f"{self.feedback_id} - {self.status}"


    def save(self, *args, **kwargs):
        # Auto-generate feedback_id on first save
        if not self.feedback_id:
            self.feedback_id = "FEED" + uuid.uuid4().hex[:6].upper()

        # Check if object exists already
        if self.pk:
            # Fetch previous instance from DB
            previous = Feedback.objects.filter(pk=self.pk).first()

            # If assigned_to is set now but was not before
            if self.assigned_to and not previous.assigned_to:
                self.assigned_at = timezone.now()

            # If status is being changed to resolved
            if self.status == "resolved" and previous.status != "resolved":
                self.resolved_at = timezone.now()
        else:
            # New instance, set if applicable
            if self.assigned_to:
                self.assigned_at = timezone.now()
            if self.status == "resolved":
                self.resolved_at = timezone.now()

        super().save(*args, **kwargs)

    def update_status(self, new_status, user, reason=""):
        """
        Validates and updates feedback status with logging and timestamp updates.
        """
        if not is_valid_transition(self.status, new_status):
            raise ValueError(
                _(f"Invalid status transition from '{self.status}' to '{new_status}'")
            )

        previous_status = self.status
        self.status = new_status

        if new_status in ["resolved", "closed"]:
            self.resolved_at = timezone.now()

        self.save()

        FeedbackLog.objects.create(
            feedback=self,
            user=user,
            previous_status=previous_status,
            new_status=new_status,
            reason=reason,
        )


# ------------------------------
# LOG MODEL
# ------------------------------
class FeedbackLog(models.Model):
    feedback = models.ForeignKey(
        Feedback, on_delete=models.CASCADE, related_name="feedbacklogs"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_feedback_logs"
    )
    previous_status = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("Previous Status")
    )
    new_status = models.CharField(max_length=100, verbose_name=_("New Status"))
    reason = models.TextField(blank=True, verbose_name=_("Log Remark"))
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.feedback.feedback_id} → {self.new_status}"


class FeedbackFile(models.Model):
    feedback = models.ForeignKey(
        Feedback, on_delete=models.CASCADE, related_name="attachments"
    )
    file = models.FileField(upload_to="feedback_files/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File for {self.feedback.feedback_id}"


class FeedbackComment(models.Model):
    feedback = models.ForeignKey(
        Feedback, on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Save the name as it was at the time of comment
    commented_by = models.CharField(max_length=150)

    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-fill commented_by if not already set
        if not self.commented_by:
            self.commented_by = str(self.user.get_full_name() or self.user.username)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Comment by {self.commented_by} on {self.feedback.feedback_id}"


