from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from ..managers.route_manager import UserLocationManager
from django.core.exceptions import ValidationError
from django.db.models import Q
from ..choices import RouteLevelChoice

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
    Represents a hierarchical location assignment (MCC → Route → MPP) for a user.

    Users can be assigned at different hierarchy levels:
    - MCC Level: Market Collection Center (highest level)
    - Route Level: Distribution route within an MCC
    - MPP Level: Milk Procurement Point (most granular level)

    A user may have multiple location assignments depending on their access level.
    """

    # =========================================================================
    # USER RELATIONSHIP
    # =========================================================================
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="locations",
        db_index=True,
        help_text="User to whom this location is assigned",
    )

    # =========================================================================
    # ASSIGNMENT LEVEL
    # =========================================================================
    level = models.CharField(
        max_length=10,
        choices=RouteLevelChoice.choices,
        default=RouteLevelChoice.LEVEL_ROUTE,
        db_index=True,
        help_text="Hierarchy level at which the user is assigned (MCC, Route, or MPP)",
    )

    # =========================================================================
    # MCC (Market Collection Center) FIELDS
    # =========================================================================
    mcc_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        db_index=True,
        help_text="Unique code identifying the Market Collection Center",
    )
    mcc_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Display name of the Market Collection Center",
    )
    mcc_tr_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Transaction/Reference code for MCC (legacy system identifier)",
    )

    # =========================================================================
    # ROUTE FIELDS
    # =========================================================================
    route_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        db_index=True,
        help_text="Unique code identifying the distribution route",
    )
    route_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Display name of the distribution route",
    )
    route_ex_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="External/legacy system code for the route",
    )

    # =========================================================================
    # MPP (Milk Procurement Point) FIELDS
    # =========================================================================
    mpp_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        db_index=True,
        help_text="Unique code identifying the Milk Procurement Point",
    )
    mpp_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Display name of the Milk Procurement Point",
    )
    mpp_ex_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="External/legacy system code for the MPP",
    )

    # =========================================================================
    # STATUS & AUDIT FIELDS
    # =========================================================================
    is_primary = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Indicates if this is the user's primary/default location",
    )
    active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this location assignment is currently active",
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assignments_done",
        help_text="User who created this location assignment",
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True, help_text="Timestamp when this location was assigned"
    )
    modified_at = models.DateTimeField(
        auto_now=True, help_text="Timestamp of the last modification"
    )
    remarks = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes or comments about this assignment",
    )

    # =========================================================================
    # MANAGERS
    # =========================================================================
    objects = UserLocationManager()

    # =========================================================================
    # META
    # =========================================================================
    class Meta:
        verbose_name = "User Location"
        verbose_name_plural = "User Locations"
        db_table = "tbl_user_locations"
        ordering = ["-assigned_at"]

        # Composite indexes for common query patterns
        indexes = [
            # User + level lookup (most common)
            models.Index(
                fields=["user", "level", "active"], name="idx_user_level_active"
            ),
            # User + primary location lookup
            models.Index(
                fields=["user", "is_primary", "active"], name="idx_user_primary"
            ),
            # Level-based filtering with active status
            models.Index(fields=["level", "active"], name="idx_level_active"),
            # MCC code lookups
            models.Index(fields=["mcc_code", "active"], name="idx_mcc_active"),
            # Route code lookups
            models.Index(fields=["route_code", "active"], name="idx_route_active"),
            # MPP code lookups
            models.Index(fields=["mpp_code", "active"], name="idx_mpp_active"),
            # Audit trail queries
            models.Index(
                fields=["assigned_by", "assigned_at"], name="idx_assigned_by_at"
            ),
            # Temporal queries
            models.Index(fields=["assigned_at", "active"], name="idx_time_active"),
        ]

        # Ensure only one primary location per user
        constraints = [
            models.UniqueConstraint(
                fields=["user", "level", "mcc_code", "route_code", "mpp_code"],
                condition=Q(active=True),
                name="unique_active_location_per_user",
            ),
        ]

        # Permissions
        permissions = [
            ("assign_location", "Can assign locations to users"),
            ("bulk_assign_location", "Can bulk assign locations"),
            ("view_all_locations", "Can view all user locations"),
        ]

    # =========================================================================
    # VALIDATION
    # =========================================================================
    def clean(self):
        """Validate model data before saving."""
        super().clean()

        # Validate level-specific required fields
        if self.level == RouteLevelChoice.LEVEL_MCC:
            if not self.mcc_code:
                raise ValidationError(
                    {"mcc_code": "MCC code is required for MCC level assignments."}
                )

        elif self.level == RouteLevelChoice.LEVEL_ROUTE:
            if not (self.mcc_code and self.route_code):
                raise ValidationError(
                    "MCC code and Route code are required for Route level assignments."
                )

        elif self.level == RouteLevelChoice.LEVEL_MPP:
            if not (self.mcc_code and self.route_code and self.mpp_code):
                raise ValidationError(
                    "MCC, Route, and MPP codes are required for MPP level assignments."
                )

    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.full_clean()
        super().save(*args, **kwargs)

    # =========================================================================
    # STRING REPRESENTATION
    # =========================================================================
    def __str__(self):
        location_code = self.get_location_code()
        return f"{self.user.username} → {self.level.upper()} ({location_code})"

    def __repr__(self):
        return f"<UserLocation: {self.user.username} - {self.level} - {self.get_location_code()}>"

    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    def get_location_code(self):
        """Return the most specific location code for this assignment."""
        if self.level == RouteLevelChoice.LEVEL_MPP:
            return self.mpp_code
        elif self.level == RouteLevelChoice.LEVEL_ROUTE:
            return self.route_code
        return self.mcc_code

    def get_location_name(self):
        """Return the most specific location name for this assignment."""
        if self.level == RouteLevelChoice.LEVEL_MPP and self.mpp_name:
            return self.mpp_name
        elif self.level == RouteLevelChoice.LEVEL_ROUTE and self.route_name:
            return self.route_name
        return self.mcc_name or self.get_location_code()

    def get_full_hierarchy(self):
        """
        Return a dictionary with the complete hierarchy information.
        Useful for displaying breadcrumb navigation.
        """
        hierarchy = {}

        if self.mcc_code:
            hierarchy["mcc"] = {
                "code": self.mcc_code,
                "name": self.mcc_name,
                "tr_code": self.mcc_tr_code,
            }

        if self.route_code:
            hierarchy["route"] = {
                "code": self.route_code,
                "name": self.route_name,
                "ex_code": self.route_ex_code,
            }

        if self.mpp_code:
            hierarchy["mpp"] = {
                "code": self.mpp_code,
                "name": self.mpp_name,
                "ex_code": self.mpp_ex_code,
            }

        return hierarchy

    def get_hierarchy_display(self):
        """Return a human-readable hierarchy path."""
        parts = []

        if self.mcc_name:
            parts.append(self.mcc_name)
        if self.route_name:
            parts.append(self.route_name)
        if self.mpp_name:
            parts.append(self.mpp_name)

        return " → ".join(parts) if parts else self.get_location_code()

    def deactivate(self, deactivated_by=None):
        """Soft delete by setting active to False."""
        self.active = False
        if deactivated_by:
            self.remarks = (
                f"Deactivated by {deactivated_by.username} on {self.modified_at}"
            )
        self.save(update_fields=["active", "remarks", "modified_at"])

    def reactivate(self, reactivated_by=None):
        """Reactivate a previously deactivated location."""
        self.active = True
        if reactivated_by:
            self.remarks = (
                f"Reactivated by {reactivated_by.username} on {self.modified_at}"
            )
        self.save(update_fields=["active", "remarks", "modified_at"])

    def make_primary(self):
        """Set this location as primary and unset others for the same user."""
        # Unset other primary locations for this user
        UserLocation.objects.filter(user=self.user, is_primary=True).exclude(
            pk=self.pk
        ).update(is_primary=False)

        self.is_primary = True
        self.save(update_fields=["is_primary"])

    @classmethod
    def get_user_primary_location(cls, user):
        """Get the primary location for a user."""
        try:
            return cls.objects.get(user=user, is_primary=True, active=True)
        except cls.DoesNotExist:
            return None
        except cls.MultipleObjectsReturned:
            # In case of data inconsistency, return the most recent one
            return (
                cls.objects.filter(user=user, is_primary=True, active=True)
                .order_by("-assigned_at")
                .first()
            )

    def has_access_to_location(self, mcc_code=None, route_code=None, mpp_code=None):
        """
        Check if this assignment grants access to the specified location.
        Higher levels grant access to all lower levels within their scope.
        """
        if not self.active:
            return False

        # MCC level: has access to all routes and MPPs under this MCC
        if self.level == RouteLevelChoice.LEVEL_MCC:
            return self.mcc_code == mcc_code if mcc_code else True

        # Route level: has access to all MPPs under this route
        elif self.level == RouteLevelChoice.LEVEL_ROUTE:
            if mcc_code and self.mcc_code != mcc_code:
                return False
            return self.route_code == route_code if route_code else True

        # MPP level: only has access to this specific MPP
        elif self.level == RouteLevelChoice.LEVEL_MPP:
            if mcc_code and self.mcc_code != mcc_code:
                return False
            if route_code and self.route_code != route_code:
                return False
            return self.mpp_code == mpp_code if mpp_code else True

        return False
