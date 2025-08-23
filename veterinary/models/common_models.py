from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from ..choices.choices import *
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
import random
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.utils.translation import get_language


User = get_user_model()

# ************************  Veterinary Tables ************************ #


class BaseModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the record was created",
        verbose_name=_("Created At"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the record was last updated",
        verbose_name=_("Updated At"),
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated",
        help_text="User who last updated this record",
        verbose_name=_("Updated By"),
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates whether the record is active",
        verbose_name=_("Is Active"),
    )
    is_deleted = models.BooleanField(
        default=False,
        help_text="Indicates whether the record is soft-deleted",
        verbose_name=_("Is Deleted"),
    )
    sync = models.BooleanField(
        default=False,
        help_text="Indicates if the record is synced with the server",
        verbose_name=_("Synced"),
    )
    locale = models.CharField(
        max_length=10,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE,
        verbose_name=_("Locale"),
        help_text=_("Locale used for this entry (e.g. en, hi, te)"),
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(locale__in=[lang[0] for lang in settings.LANGUAGES]),
                name="valid_locale_check",
            )
        ]

    def soft_delete(self):
        """Soft delete the record."""
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active", "updated_at"])

    def sync_data(self):
        """Sync the record."""
        self.sync = True
        self.save(update_fields=["sync"])

    def restore(self):
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.is_active = True
        self.save(update_fields=["is_deleted", "is_active", "updated_at"])

    def delete(self, *args, **kwargs):
        """Override delete to perform soft delete by default."""
        self.soft_delete()


class CattleStatusType(BaseModel):

    code = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="Status Code",
        help_text="e.g., DRY, MILKING, PREGNANT",
    )

    label = models.CharField(
        max_length=100, verbose_name="Status Label", help_text="Human-readable label"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Cattle Status Type"
        verbose_name_plural = "Cattle Status Types"
        ordering = ["label"]
        unique_together = ["code", "locale"]

    def __str__(self):
        return f"{self.label} ({self.code})"


class Species(BaseModel):
    animal_type = models.CharField(
        max_length=100,
        unique=True,
        help_text="Enter the type of animal (e.g., Cow, Buffalo)",
        verbose_name="Animal Type",
    )

    scientific_name = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        help_text="Scientific name of the animal (e.g., Bos taurus for Cow)",
        verbose_name="Scientific Name",
    )

    category = models.CharField(
        max_length=50,
        choices=AnimalUse.choices,
        default=AnimalUse.DAIRY,
        help_text="Primary use category of the animal",
        verbose_name="Category",
    )

    description = models.TextField(
        null=True,
        blank=True,
        help_text="Optional detailed description or notes",
        verbose_name="Description",
    )

    average_lifespan = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Average lifespan in years (e.g., 15)",
        verbose_name="Average Lifespan",
    )

    is_milk_producing = models.BooleanField(
        default=True,
        help_text="Is this animal type typically used for milk production?",
        verbose_name="Milk Producing",
    )
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.locale:
            self.locale = get_language() or "en"
        if not self.slug:
            base_slug = slugify(self.animal_type)
            self.slug = f"{base_slug}-{self.locale}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.animal_type

    class Meta:
        db_table = "tbl_species"
        verbose_name = "Cattle Type"
        verbose_name_plural = "Cattle Types"
        ordering = ["animal_type"]
        indexes = [
            models.Index(fields=["animal_type"]),
        ]
        unique_together = ["slug", "locale"]


class SpeciesBreed(BaseModel):
    breed = models.CharField(
        max_length=100,
        help_text="Enter the breed name (e.g., Jersey, Holstein)",
        verbose_name="Breed",
    )

    animal_type = models.ForeignKey(
        Species,
        on_delete=models.CASCADE,
        related_name="breeds",
        help_text="Select the animal type this breed belongs to",
    )

    origin_country = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Country or region where this breed originated",
        verbose_name="Country of Origin",
    )

    average_milk_yield = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Average daily milk yield in liters (e.g., 22.50)",
        verbose_name="Avg Milk Yield (L/day)",
    )

    color = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Typical coat color of the breed (e.g., brown, black-and-white)",
        verbose_name="Coat Color",
    )

    adaptability = models.TextField(
        null=True,
        blank=True,
        help_text="Notes on climate or region adaptability",
        verbose_name="Adaptability",
    )

    description = models.TextField(
        null=True,
        blank=True,
        help_text="Additional notes or characteristics",
        verbose_name="Description",
    )

    class Meta:
        db_table = "tbl_species_breed"
        verbose_name = "Cattle Breed"
        verbose_name_plural = "Cattle Breeds"
        ordering = ["breed"]
        indexes = [
            models.Index(fields=["breed"]),
            models.Index(fields=["animal_type"]),
        ]

    def __str__(self):
        return f"{self.breed} ({self.animal_type.animal_type})"

    def save(self, *args, **kwargs):
        if not self.locale:
            self.locale = get_language() or "en"
        super().save(*args, **kwargs)


class AICharge(models.Model):

    user_role = models.CharField(
        max_length=20,
        choices=UserRoleChoices.choices,
        default=UserRoleChoices.MAT,
        help_text="Role of the user performing AI",
        verbose_name="User Role",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="Specific user this charge applies to (overrides role)",
        verbose_name="User",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Charge amount for AI",
        verbose_name="Charge Amount",
    )

    class Meta:
        db_table = "tbl_ai_charge"
        verbose_name = "AI Charge"
        verbose_name_plural = "AI Charges"
        unique_together = (("user_role", "user"),)

    def __str__(self):
        if self.user:
            return f"{self.user.username}: ₹{self.amount}"
        return f"{self.user_role}: ₹{self.amount}"


class CattleCaseType(BaseModel):
    case_type = models.CharField(
        max_length=20,
        choices=CaseTypeChoices.choices,
        default=CaseTypeChoices.NORMAL,
        unique=True,
        help_text="Type of case for cattle service (Normal, Special, Operational)",
        verbose_name="Case Type",
    )

    description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional description or notes about this case type",
        verbose_name="Description",
    )

    def __str__(self):
        return self.get_case_type_display()

    class Meta:
        db_table = "tbl_cattle_case_type"
        verbose_name = "Cattle Case Type"
        verbose_name_plural = "Cattle Case Types"
        ordering = ["case_type"]
        indexes = [
            models.Index(fields=["case_type"]),
        ]


class TimeSlot(BaseModel):

    start_time = models.TimeField(
        help_text="Start time of the slot", verbose_name="Start Time"
    )

    end_time = models.TimeField(
        blank=True,
        null=True,
        help_text="End time of the slot (optional)",
        verbose_name="End Time",
    )

    period = models.CharField(
        max_length=20,
        choices=PeriodChoices.choices,
        help_text="Time of day this slot belongs to (e.g., Morning, Evening)",
        verbose_name="Period of Day",
    )

    normal_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Standard cost for this time slot",
        verbose_name="Normal Cost",
    )

    operational_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Cost during operational cases (if different from normal)",
        verbose_name="Operational Cost",
    )

    sync = models.BooleanField(
        default=False,
        help_text="Indicates if the record is synced with the server",
        verbose_name="Synced",
    )

    def __str__(self):
        time_range = (
            f'{self.start_time.strftime("%I:%M %p")} - {self.end_time.strftime("%I:%M %p")}'
            if self.end_time
            else f'{self.start_time.strftime("%I:%M %p")}'
        )
        return f"{self.period} | {time_range} | ₹{self.normal_cost}"

    class Meta:
        db_table = "tbl_time_slot"
        verbose_name = "Time Slot"
        verbose_name_plural = "Time Slots"
        ordering = ["start_time"]
        indexes = [
            models.Index(fields=["period"]),
            models.Index(fields=["start_time", "end_time"]),
        ]


class CattleCaseStatus(BaseModel):
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        help_text=_("case status of cattle"),
        verbose_name=_("Case Status"),
    )

    def __str__(self):
        return f"{self.status}"

    class Meta:
        db_table = "tbl_cattle_case_status"
        verbose_name = "Case Status"
        verbose_name_plural = "Case Statuses"


class VeterinaryAuditLog(models.Model):
    action = models.CharField(
        max_length=50,
        choices=[
            ("created", "Created"),
            ("updated", "Updated"),
            ("deleted", "Deleted"),
        ],
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=100)
    content_object = GenericForeignKey("content_type", "object_id")

    changed_by = models.CharField(max_length=100)  # or FK to a User
    changed_at = models.DateTimeField(auto_now_add=True)
    change_data = models.JSONField()

    class Meta:
        ordering = ["-changed_at"]


class PaymentMethod(BaseModel):
    method = models.CharField(
        max_length=100, choices=PaymentMethodChoices.choices, unique=True
    )

    def __str__(self):
        return self.get_method_display()


class OnlinePayment(models.Model):
    payment_method = models.OneToOneField(
        PaymentMethod,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="online_payment",
    )
    gateway_name = models.CharField(max_length=100)
    sync = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.gateway_name}"

    class Meta:
        db_table = "tbl_online_payment_methods"
        verbose_name = "Online Payment Method"
        verbose_name_plural = "Online Payment Methods"


from django.core.exceptions import ValidationError
from django.utils import timezone


class Vehicle(BaseModel):
    """Production-ready Vehicle master model"""

    registration_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("Registration Number"),
        help_text=_("Unique registration number of the vehicle (e.g., UP65AB1234)."),
    )

    model_name = models.CharField(
        max_length=100,
        verbose_name=_("Model Name"),
        help_text=_("Manufacturer and model name (e.g., Tata 407, Maruti Swift)."),
    )

    vehicle_type = models.CharField(
        max_length=20,
        choices=VehicleTypeChoices.choices,
        default=VehicleTypeChoices.OTHER,
        verbose_name=_("Vehicle Type"),
        help_text=_("Type of vehicle."),
    )

    chassis_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Chassis Number"),
        help_text=_("Unique chassis number of the vehicle."),
    )

    engine_number = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        verbose_name=_("Engine Number"),
        help_text=_("Unique engine number of the vehicle."),
    )

    purchase_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Purchase Date"),
        help_text=_("Date when the vehicle was purchased."),
    )

    registration_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Registration Date"),
        help_text=_("Date when the vehicle was registered with RTO."),
    )

    seating_capacity = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Seating Capacity"),
        help_text=_("Number of seats in the vehicle."),
    )

    fuel_type = models.CharField(
        max_length=20,
        choices=[
            ("PETROL", _("Petrol")),
            ("DIESEL", _("Diesel")),
            ("CNG", _("CNG")),
            ("ELECTRIC", _("Electric")),
            ("HYBRID", _("Hybrid")),
        ],
        verbose_name=_("Fuel Type"),
        help_text=_("Primary fuel type of the vehicle."),
    )

    insurance_valid_upto = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Insurance Valid Upto"),
        help_text=_("Date until which the vehicle insurance is valid."),
    )

    puc_valid_upto = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("PUC Valid Upto"),
        help_text=_(
            "Date until which the Pollution Under Control certificate is valid."
        ),
    )

    class Meta:
        verbose_name = _("Vehicle")
        verbose_name_plural = _("Vehicles")
        ordering = ["registration_number"]
        indexes = [
            models.Index(fields=["registration_number"]),
            models.Index(fields=["vehicle_type"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.registration_number} - {self.model_name}"

    # ----------------------------
    # Helper Methods
    # ----------------------------
    @property
    def is_insurance_valid(self) -> bool:
        """Check if insurance is still valid"""
        from django.utils import timezone

        return (
            self.insurance_valid_upto
            and self.insurance_valid_upto >= timezone.now().date()
        )

    @property
    def is_puc_valid(self) -> bool:
        """Check if PUC is still valid"""
        from django.utils import timezone

        return self.puc_valid_upto and self.puc_valid_upto >= timezone.now().date()

    def deactivate(self, reason: str = None):
        """Mark vehicle as inactive"""
        self.is_active = False
        self.save(update_fields=["is_active"])
        # Could log reason to an audit table if needed


class VehicleKiloMeterLog(BaseModel):
    """Log entry for vehicle journeys and kilometer usage"""

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_("Log associated with user"),
        verbose_name=_("User"),
    )

    district = models.CharField(
        max_length=100,
        verbose_name=_("District"),
        help_text=_("District where the journey took place."),
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="kilometer_logs",
        verbose_name=_("Vehicle"),
        help_text=_("Vehicle for which this journey log is recorded."),
    )

    driver_name = models.CharField(
        max_length=150,
        verbose_name=_("Driver Name"),
        help_text=_("Full name of the driver."),
    )

    opening_datetime = models.DateTimeField(
        verbose_name=_("Opening Date & Time"),
        help_text=_("Date and time when the journey started."),
    )
    closing_datetime = models.DateTimeField(
        verbose_name=_("Closing Date & Time"),
        help_text=_("Date and time when the journey ended."),
    )

    opening_km = models.PositiveIntegerField(
        verbose_name=_("Opening Kilometer Reading"),
        help_text=_("Odometer reading at the start of the journey."),
    )
    closing_km = models.PositiveIntegerField(
        verbose_name=_("Closing Kilometer Reading"),
        help_text=_("Odometer reading at the end of the journey."),
    )

    place_of_visit = models.TextField(
        verbose_name=_("Place of Visit"),
        help_text=_("Locations or places visited during the journey."),
    )
    purpose_of_journey = models.TextField(
        verbose_name=_("Purpose of Journey"),
        help_text=_("Reason or objective of the journey."),
    )

    class Meta:
        verbose_name = _("Vehicle Kilometer Log")
        verbose_name_plural = _("Vehicle Kilometer Logs")
        ordering = ["-opening_datetime"]
        indexes = [
            models.Index(fields=["vehicle", "opening_datetime"]),
            models.Index(fields=["district"]),
        ]

    def __str__(self):
        return f"{self.vehicle} | {self.opening_datetime:%Y-%m-%d} | {self.driver_name}"

    # ----------------------------
    # Validation
    # ----------------------------
    def clean(self):
        """Custom validations"""
        if self.closing_datetime < self.opening_datetime:
            raise ValidationError(
                _("Closing datetime cannot be earlier than opening datetime.")
            )

        if self.closing_km < self.opening_km:
            raise ValidationError(
                _(
                    "Closing kilometer reading cannot be less than opening kilometer reading."
                )
            )

        if (
            self.opening_datetime > timezone.now()
            or self.closing_datetime > timezone.now()
        ):
            raise ValidationError(_("Journey datetimes cannot be in the future."))

    # ----------------------------
    # Helper Methods
    # ----------------------------
    @property
    def distance_travelled(self) -> int:
        """Total kilometers traveled in this journey"""
        return (
            self.closing_km - self.opening_km
            if self.closing_km and self.opening_km
            else 0
        )

    @property
    def journey_duration(self):
        """Return journey duration as timedelta"""
        return (
            self.closing_datetime - self.opening_datetime
            if self.closing_datetime and self.opening_datetime
            else None
        )

    def is_round_trip(self) -> bool:
        """Helper to check if place_of_visit suggests a round trip"""
        return (
            "return" in self.place_of_visit.lower()
            or "back" in self.place_of_visit.lower()
        )
