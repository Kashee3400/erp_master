from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
import uuid
from facilitator.models.facilitator_model import AssignedMppToFacilitator
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from datetime import datetime

User = get_user_model()


class VCGroup(models.Model):
    phone_validator = RegexValidator(
        regex=r"^\+?\d{10,15}$",
        message=_(
            "Enter a valid WhatsApp number with country code (e.g., +1234567890)."
        ),
    )
    mpp = models.ForeignKey(
        AssignedMppToFacilitator,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("MPP"),
        help_text=_("Member related to  mpp"),
    )
    mpp_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("Mpp Code"),
        help_text=_("Unique mpp code."),
    )
    whatsapp_num = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[phone_validator],
        verbose_name=_("WhatsApp Number"),
        help_text=_("Member's WhatsApp contact number."),
    )
    member_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_("Member Code"),
        help_text=_("Unique identifier for the VCG member."),
    )
    member_ex_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_("Member Ex Code"),
        help_text=_("Unique identifier for the VCG member."),
    )
    member_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Member Name"),
        help_text=_("Full name of the VCG member."),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("Timestamp when the member was added."),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
        help_text=_("Timestamp when the member record was last updated."),
    )

    def __str__(self):
        return f"{self.member_name} ({self.whatsapp_num})"

    class Meta:
        db_table = "tbl_vcg_member"
        verbose_name = _("VCG Group")
        verbose_name_plural = _("VCG Groups")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["member_code"]),
            models.Index(fields=["whatsapp_num"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["member_code"], name="unique_vcg_member_code"
            )
        ]


class VCGMeeting(models.Model):
    STARTED = "started"
    COMPLETED = "completed"
    DELETED = "deleted"
    STATUS_CHOICES = (
        (STARTED, _("Started")),
        (COMPLETED, _("Completed")),
        (COMPLETED, _("Deleted")),
    )

    meeting_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text=_("Unique identifier for the meeting."),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="meetings",
        verbose_name=_("User"),
        help_text=_("User who initiated the meeting."),
    )

    mpp_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default="",
        verbose_name=_("MPP Name"),
        help_text=_("Name of the MPP associated with the meeting."),
    )
    mpp_ex_code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default="",
        verbose_name=_("MPP EX Code"),
        help_text=_("External MPP Code for reference."),
    )
    mpp_code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("MPP Code"),
        help_text=_("Unique MPP code assigned."),
    )

    lat = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)],
        verbose_name=_("Latitude"),
        help_text=_("Geographical latitude of the meeting location."),
    )
    lon = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)],
        verbose_name=_("Longitude"),
        help_text=_("Geographical longitude of the meeting location."),
    )

    started_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Started At"),
        help_text=_("Timestamp when the meeting started."),
    )
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Completed At"),
        help_text=_("Timestamp when the meeting was completed."),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STARTED,
        verbose_name=_("Meeting Status"),
        help_text=_("Current status of the meeting."),
    )
    synced = models.BooleanField(
        default=True,
        verbose_name=_("Synced"),
        help_text=_("Indicated whether data is synced from mobile app or not."),
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name=_("deleted"),
        help_text=_("Indicated whether data is deleted or not."),
    )

    # Methods
    def __str__(self):
        return f"Meeting {self.meeting_id} - {self.status}"

    def is_completed(self):
        """Check if the meeting is completed."""
        return self.status == self.COMPLETED

    def duration(self):
        """Calculate the duration of the meeting in minutes."""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return delta.total_seconds() / 60
        return None  # If not completed

    class Meta:
        db_table = "tbl_vcg_meeting"
        verbose_name = _("VCG Meeting")
        verbose_name_plural = _("VCG Meetings")
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["meeting_id"]),
            models.Index(fields=["status"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["mpp_name", "mpp_code", "started_at"],
                condition=Q(status="started"),
                name="unique_mpp_meeting_per_month",
            ),
        ]

    @classmethod
    def get_ongoing_meeting(cls, mpp_code, date):
        """
        Check if an ongoing meeting exists (status=STARTED) for the given MPP in the specified year and month.
        Returns a tuple (bool, meeting_instance or None).
        """
        meeting = cls.objects.filter(
            mpp_code=mpp_code,
            status=cls.STARTED,
            started_at__year=date.year,
            started_at__month=date.month,
        ).first()

        return (bool(meeting), meeting)


class VCGMemberAttendance(models.Model):
    PRESENT = "present"
    ABSENT = "absent"
    STATUS_CHOICES = [
        (PRESENT, _("Present")),
        (ABSENT, _("Absent")),
    ]

    meeting = models.ForeignKey(
        VCGMeeting,
        on_delete=models.CASCADE,
        related_name="attendances",
        blank=True,
        null=True,
        verbose_name=_("Meeting"),
        help_text=_("The meeting to which this attendance record belongs."),
    )

    group_member = models.ForeignKey(
        VCGroup,
        on_delete=models.CASCADE,
        related_name="vcg_attendance",
        blank=True,
        null=True,
        verbose_name=_("Group Member"),
        help_text=_("The VCG member attending the meeting."),
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default=ABSENT,
        verbose_name=_("Attendance Status"),
        help_text=_("Indicates whether the member was present or absent."),
    )

    date = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Attendance Date"),
        help_text=_("Timestamp of when the attendance was recorded."),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("Timestamp of when this record was created."),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
        help_text=_("Timestamp of the last update to this record."),
    )

    def __str__(self):
        return f"{self.group_member} ({self.status})"

    class Meta:
        db_table = "tbl_member_attendance"
        verbose_name = _("VCG Member Attendance")
        verbose_name_plural = _("VCG Member Attendances")
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["meeting"]),
            models.Index(fields=["group_member"]),
            models.Index(fields=["status"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["meeting", "group_member"],
                name="unique_meeting_member_attendance",
            )
        ]


class VCGMeetingImages(models.Model):
    meeting = models.ForeignKey(
        VCGMeeting,
        on_delete=models.CASCADE,
        related_name="meeting_images",
        verbose_name=_("Meeting"),
        help_text=_("The meeting associated with this image."),
    )

    image = models.FileField(
        upload_to="meeting_images/",
        verbose_name=_("Meeting Image"),
        help_text=_("Upload an image related to the meeting."),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("Timestamp of when this image was uploaded."),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
        help_text=_("Timestamp of the last update to this record."),
    )

    def __str__(self):
        return f"Image for Meeting {self.meeting.id if self.meeting else 'N/A'}"

    class Meta:
        db_table = "tbl_meeting_images"
        verbose_name = _("VCG Meeting Image")
        verbose_name_plural = _("VCG Meeting Images")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["meeting"]),
            models.Index(fields=["created_at"]),
        ]


class ZeroDaysPourerReason(models.Model):
    reason = models.CharField(
        max_length=150,
        unique=True,
        verbose_name=_("Reason"),
        help_text=_("Reason for zero days pouring."),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("Timestamp when this reason was added."),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
        help_text=_("Timestamp when this reason was last updated."),
    )

    def __str__(self):
        return self.reason

    class Meta:
        db_table = "tbl_zero_days_pouring"
        verbose_name = _("Zero Days Pouring Reason")
        verbose_name_plural = _("Zero Days Pouring Reasons")
        ordering = ["reason"]
        indexes = [
            models.Index(fields=["reason"]),
        ]


class MemberComplaintReason(models.Model):
    reason = models.CharField(
        max_length=150,
        unique=True,
        verbose_name=_("Reason"),
        help_text=_("Reason for a member complaint."),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("Timestamp when this reason was added."),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
        help_text=_("Timestamp when this reason was last updated."),
    )

    def __str__(self):
        return self.reason

    class Meta:
        db_table = "tbl_member_complaint"
        verbose_name = _("Member Complaint Reason")
        verbose_name_plural = _("Member Complaint Reasons")
        ordering = ["reason"]
        indexes = [
            models.Index(fields=["reason"]),
        ]


class ZeroDaysPouringReport(models.Model):
    member_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_("Member Code"),
        help_text=_("Unique identifier for the VCG member."),
    )
    member_ex_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_("Member Code"),
        help_text=_("Unique identifier for the VCG member."),
    )
    member_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Member Name"),
        help_text=_("Full name of the VCG member."),
    )
    reason = models.ForeignKey(
        ZeroDaysPourerReason,
        on_delete=models.CASCADE,
        related_name="zero_pouring_reason",
    )
    meeting = models.ForeignKey(
        VCGMeeting, on_delete=models.CASCADE, related_name="meeting_zero_days_pouring"
    )

    def __str__(self):
        return f"{self.member_name} - {self.reason.reason}"

    class Meta:
        db_table = "tbl_zerodays_report"
        verbose_name = "Zero Days Pouring Report"
        verbose_name_plural = "Zero Days Pouring Reports"


class MemberComplaintReport(models.Model):
    member_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("Member Code"),
        help_text=_("Unique identifier for the VCG member."),
    )
    member_ex_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("Member External Code"),
        help_text=_("External identifier for the VCG member."),
    )
    member_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Member Name"),
        help_text=_("Full name of the VCG member."),
    )
    reason = models.ForeignKey(
        MemberComplaintReason,
        on_delete=models.CASCADE,
        related_name="member_complaint_reason",
    )
    meeting = models.ForeignKey(
        VCGMeeting, on_delete=models.CASCADE, related_name="meeting_member_complaints"
    )

    def __str__(self):
        return f"{self.member_name} ({self.member_code}) - {self.reason}"

    class Meta:
        db_table = "tbl_member_complaint_report"
        verbose_name = "Member Complaint Report"
        verbose_name_plural = "Member Complaint Reports"


class MonthAssignment(models.Model):
    mpp_name = models.CharField(
        max_length=100,
        default="",
        verbose_name=_("MPP Name"),
        help_text=_("Name of the MPP associated with the meeting."),
    )
    mpp_ex_code = models.CharField(
        max_length=100,
        default="",
        verbose_name=_("MPP EX Code"),
        help_text=_("External MPP Code for reference."),
    )
    mpp_code = models.CharField(
        max_length=100,
        verbose_name=_("MPP Code"),
        help_text=_("Unique MPP code assigned."),
    )

    month = models.DateField(
        verbose_name=_("Month"),
        help_text=_("The month for which the assignment is created."),
    )

    milk_collection = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Milk Collection (Liters/Day)"),
        help_text=_("Total milk collected per day in liters."),
    )
    no_of_members = models.PositiveIntegerField(
        default=0, verbose_name=_("No of Members")
    )
    pourers_15_days = models.PositiveIntegerField(
        default=0, verbose_name=_(">=15 Days Pourers")
    )
    pourers_25_days = models.PositiveIntegerField(
        default=0, verbose_name=_(">=25 Days Pourers")
    )
    zero_days_pourers = models.PositiveIntegerField(
        default=0, verbose_name=_("Zero Days Pourers")
    )
    cattle_feed_sale = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Cattle Feed Sale (KG)"),
    )
    mineral_mixture_sale = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Mineral Mixture Sale (KG)"),
    )
    sahayak_recovery = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Sahayak Recovery (%)"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    def __str__(self):
        return f"{self.mpp_code} - {self.month.strftime('%Y-%m')}"

    class Meta:
        db_table = "tbl_month_assignment"
        verbose_name = _("Month Assignment")
        verbose_name_plural = _("Month Assignments")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["mpp_code"]),
            models.Index(fields=["milk_collection"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["mpp_code", "month"], name="unique_mpp_month_assignment"
            ),
        ]
