from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserProfile(models.Model):
    """Stores additional user metadata like department, contact details, and avatar."""

    class Department(models.TextChoices):
        SUPPORT = "support", _("Support")
        IT = "it", _("IT")
        PIB = "pib", _("PIB")
        SALES = "sales", _("Sales")
        ENGINEERING = "engineering", _("Engineering")
        ADMIN = "admin", _("Administration")
        VETERINARIAN = "veterinarian", _("Veterinarian")
        MAIT = "mait", _("MAIT")
        DOCTOR = "doctor", _("Doctor")
        SAHAYAK = "sahayak", _("Sahayak")
        MEMBER = "member", _("Member")

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("User"),
        help_text=_("The user to whom this profile belongs."),
    )
    reports_to = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reportees",
        verbose_name=_("Reports To"),
        help_text=_("The supervisor or manager to whom this user reports."),
    )
    salutation = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name=_("Salutation"),
        help_text=_("Prefix such as Dr., Mr., Ms., etc."),
    )
    department = models.CharField(
        max_length=32,
        choices=Department.choices,
        blank=True,
        null=True,
        verbose_name=_("Department"),
        help_text=_("Department or team of the user."),
    )
    avatar = models.ImageField(
        upload_to="profile_images/",
        blank=True,
        null=True,
        verbose_name=_("Avatar"),
        help_text=_("User profile picture."),
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name=_("Phone Number"),
        help_text=_("Contact number of the user."),
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Address"),
        help_text=_("Residential or official address."),
    )
    designation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Designation"),
        help_text=_("Official designation or title."),
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_("Verified"),
        help_text=_("Indicates whether the user's profile is verified."),
    )
    is_email_verified = models.BooleanField(
        default=False,
        verbose_name=_("Email Verified"),
        help_text=_("Indicates whether the user's email is verified."),
    )
    mpp_code = models.CharField(
        max_length=200, blank=True, null=True, verbose_name=_("MPP Code")
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    def is_internal(self):
        return self.department in [
            self.Department.IT,
            self.Department.ENGINEERING,
            self.Department.ADMIN,
        ]

    def full_contact_info(self):
        return f"{self.phone_number or '-'} | {self.address or '-'}"

    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")
        ordering = ["department", "user__username"]
        permissions = [
            ("can_view_others_reportees", "Can view reportees of other users"),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_department_display()}"

    def is_support_staff(self):
        return self.department == self.Department.SUPPORT

    def is_pib_staff(self):
        return self.department == self.Department.PIB


class UserLocation(models.Model):
    """
    Stores mapping between users and their assigned operational locations
    (MPP, MCC, etc.) while keeping cross-database compatibility.

    ✅ Supports:
        - One user → multiple locations
        - One location → multiple users
        - Text-based MCC/MPP references (not ForeignKeys)
        - Primary location flag
        - Full audit trail (who assigned, when, remarks)
    """

    # -----------------------------
    # Core Relationships
    # -----------------------------
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_locations",
        verbose_name=_("User"),
        help_text=_("The user assigned to this operational location."),
    )

    # -----------------------------
    # MCC Fields
    # -----------------------------
    mcc_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("MCC Code"),
        help_text=_("Unique identifier for the MCC (from external DB)."),
    )
    mcc_ex_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("MCC External Code"),
        help_text=_("External reference code for the MCC, if available."),
    )
    mcc_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("MCC Name"),
        help_text=_("Display name of the MCC location."),
    )

    # -----------------------------
    # MPP Fields
    # -----------------------------
    mpp_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("MPP Code"),
        help_text=_("Unique identifier for the MPP (from external DB)."),
    )
    mpp_ex_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("MPP External Code"),
        help_text=_("External reference code for the MPP, if available."),
    )
    mpp_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("MPP Name"),
        help_text=_("Display name of the MPP location."),
    )

    # -----------------------------
    # Flags & Audit
    # -----------------------------
    is_primary = models.BooleanField(
        default=False,
        verbose_name=_("Primary Location"),
        help_text=_("Marks this location as the user's main or default work location."),
    )

    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_user_locations",
        verbose_name=_("Assigned By"),
        help_text=_("Administrator or supervisor who assigned this location."),
    )

    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Assigned At"),
        help_text=_("Timestamp when this user was assigned to the location."),
    )

    active = models.BooleanField(
        default=True,
        verbose_name=_("Active Assignment"),
        help_text=_("Indicates if this user-location assignment is currently active."),
    )

    remarks = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Remarks"),
        help_text=_("Additional notes or comments about this assignment."),
    )

    # -----------------------------
    # Meta Configuration
    # -----------------------------
    class Meta:
        verbose_name = _("User Location")
        verbose_name_plural = _("User Locations")
        ordering = ["user__username", "mcc_code", "mpp_code"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "mcc_code", "mpp_code"],
                name="unique_user_mcc_mpp_assignment",
                violation_error_message=_(
                    "This user is already assigned to the specified MCC-MPP combination."
                ),
            ),
        ]
        indexes = [
            models.Index(fields=["user"], name="idx_userlocation_user"),
            models.Index(fields=["mcc_code"], name="idx_userlocation_mcc_code"),
            models.Index(fields=["mpp_code"], name="idx_userlocation_mpp_code"),
        ]

    # -----------------------------
    # String Representation
    # -----------------------------
    def __str__(self):
        parts = []
        if self.mcc_code:
            parts.append(f"MCC: {self.mcc_code}")
        if self.mpp_code:
            parts.append(f"MPP: {self.mpp_code}")
        location = " / ".join(parts) if parts else "Unassigned"
        return f"{self.user.username} → {location}"

    # -----------------------------
    # Helper / Utility Methods
    # -----------------------------
    @classmethod
    def get_user_locations(cls, user):
        """Return all active locations assigned to a user."""
        return cls.objects.filter(user=user, active=True)

    @classmethod
    def get_primary_location(cls, user):
        """Return the primary location for a given user, if marked."""
        return cls.objects.filter(user=user, is_primary=True, active=True).first()

    @classmethod
    def get_users_for_location(cls, mcc_code=None, mpp_code=None):
        """Return all active users for a given MCC or MPP code."""
        qs = cls.objects.filter(active=True)
        if mcc_code:
            qs = qs.filter(mcc_code=mcc_code)
        if mpp_code:
            qs = qs.filter(mpp_code=mpp_code)
        return qs.select_related("user")

    @classmethod
    def assign(
        cls,
        user,
        mcc_code=None,
        mcc_name=None,
        mpp_code=None,
        mpp_name=None,
        assigned_by=None,
        primary=False,
        remarks=None,
    ):
        """
        Assign or reactivate a user-location mapping.
        Avoids duplicate active assignments.
        """
        if not (mcc_code or mpp_code):
            raise ValueError(
                "Either MCC or MPP must be provided when assigning a user."
            )

        existing = cls.objects.filter(
            user=user, mcc_code=mcc_code, mpp_code=mpp_code
        ).first()

        if existing:
            if not existing.active:
                existing.active = True
                existing.save(update_fields=["active"])
            return existing

        return cls.objects.create(
            user=user,
            mcc_code=mcc_code,
            mcc_name=mcc_name,
            mpp_code=mpp_code,
            mpp_name=mpp_name,
            assigned_by=assigned_by,
            is_primary=primary,
            remarks=remarks,
        )

    @classmethod
    def deactivate(cls, user, mcc_code=None, mpp_code=None):
        """Soft-deactivate a user-location assignment."""
        qs = cls.objects.filter(user=user)
        if mcc_code:
            qs = qs.filter(mcc_code=mcc_code)
        if mpp_code:
            qs = qs.filter(mpp_code=mpp_code)
        qs.update(active=False)

