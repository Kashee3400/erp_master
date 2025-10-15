from ..choices.choices import *
from .common_models import BaseModel, User, SpeciesBreed, CattleStatusType
import hashlib, random, uuid
from django.db import models, transaction
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# ************************  Veterinary Tables ************************ #


class MembersMasterCopy(models.Model):
    member_code = models.CharField(
        max_length=50,
        primary_key=True,
        verbose_name="Member Code",
        help_text="Unique identifier for the member.",
    )
    company_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Company Code",
        help_text="Code representing the company.",
    )
    plant_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Plant Code",
        help_text="Code representing the plant.",
    )
    mcc_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="MCC Code",
        help_text="Milk Collection Center Code.",
    )
    bmc_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="BMC Code",
        help_text="Bulk Milk Cooler code.",
    )
    mpp_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="MPP Code",
        help_text="Milk Procurement Point Code.",
    )

    member_tr_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Transaction Code",
        help_text="Member transaction code if any.",
    )
    member_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Member First Name",
        help_text="First name of the member.",
    )
    member_middle_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Middle Name",
        help_text="Middle name of the member.",
    )
    member_surname = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Surname",
        help_text="Last name of the member.",
    )
    gender = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Gender",
        help_text="Gender of the member (e.g., Male, Female).",
    )
    mobile_no = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Mobile Number",
        help_text="Mobile number of the member.",
    )
    member_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Member Type",
        help_text="Type/category of member (e.g., Regular, Associate).",
    )
    caste_category = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Caste Category",
        help_text="Caste category for the member (for regulatory tracking).",
    )
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date of Birth",
        help_text="Birth date of the member.",
    )
    age = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Age",
        help_text="Age of the member (auto-calculated or user-provided).",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Is Active",
        help_text="Is the member currently active?",
    )
    wef_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="W.E.F Date",
        help_text="With effect from date — when the member joined.",
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name="Is Default",
        help_text="Marks if this record is default for the member (used in hierarchies).",
    )
    created_at = models.DateTimeField(
        verbose_name="Created At", help_text="Timestamp when the record was created."
    )
    folio_no = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Folio Number",
        help_text="Folio or account number of the member.",
    )
    application_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Application Date",
        help_text="Date of application submission.",
    )
    application_no = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Application Number",
        help_text="Unique application number for member registration.",
    )
    created_by = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Created By (External)",
        help_text="External system or user who created the record.",
    )
    member_master_relation = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Relation Description",
        help_text="Description of the relationship (e.g., S/o, D/o).",
    )
    ex_member_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Ex-Member Code",
        help_text="Old member code if migrated from previous systems.",
    )
    device_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Device ID",
        help_text="Device identifier if data was captured via mobile.",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Linked User",
        help_text="Reference to Django user if mapped.",
    )

    class Meta:
        db_table = "member_master_copy"
        verbose_name = "Member Master Copy"
        verbose_name_plural = "Member Masters"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["member_code"]),
            models.Index(fields=["mobile_no"]),
        ]

    def __str__(self):
        return (
            f"{self.member_name or ''} {self.member_surname or ''} ({self.member_code})"
        )


# New Non-Member models
class NonMember(BaseModel):
    """Non-member owner details"""

    non_member_id = models.CharField(
        max_length=50, unique=True, help_text=_("Unique identifier for non-member")
    )

    name = models.CharField(max_length=255, help_text=_("Full name of non-member"))

    mobile_no = models.CharField(
        max_length=15,
        unique=True,
        validators=[RegexValidator(r"^\+?1?\d{9,15}$", "Enter a valid phone number.")],
        help_text=_("Mobile number"),
    )
    mcc_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="MCC Code",
        help_text="Milk Collection Center Code.",
    )
    mcc_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="MCC Code",
        help_text="Milk Collection Center Code.",
    )

    mpp_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="MPP Code",
        help_text="Milk Procurement Point Code.",
    )
    mpp_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="MCC Code",
        help_text="Milk Collection Center Code.",
    )

    address = models.TextField(help_text=_("Full address of non-member"))

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="non_members_created",
        help_text=_("User who registered this non-member"),
    )

    visit_count = models.PositiveIntegerField(
        default=0, help_text=_("Number of visits by this non-member")
    )

    sync = models.BooleanField(default=False, help_text=_("Sync status with server"))

    class Meta:
        db_table = "tbl_non_members"
        verbose_name = _("Non Member")
        verbose_name_plural = _("Non Members")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["mobile_no"], name="idx_nonmember_mobile"),
            models.Index(fields=["non_member_id"], name="idx_nonmember_id"),
        ]

    def __str__(self):
        return f"{self.name} ({self.mobile_no})"

    def save(self, *args, **kwargs):
        if not self.non_member_id:
            # Generate unique non_member_id: NM-YYYYMMDD-XXXX
            timestamp = timezone.now().strftime("%Y%m%d")
            rand_suffix = random.randint(1000, 9999)
            self.non_member_id = (
                f"NM-{self.mcc_code}-{self.mpp_code}-{timestamp}-{rand_suffix}"
            )

            # Ensure uniqueness
            while NonMember.objects.filter(non_member_id=self.non_member_id).exists():
                rand_suffix = random.randint(1000, 9999)
                self.non_member_id = (
                    f"NM-{self.mcc_code}{self.mpp_code}-{timestamp}-{rand_suffix}"
                )

        super().save(*args, **kwargs)


class NonMemberCattle(BaseModel):
    """Cattle owned by non-members"""

    non_member = models.ForeignKey(
        NonMember,
        on_delete=models.CASCADE,
        related_name="cattle",
        help_text=_("Non-member owner"),
    )

    tag_number = models.CharField(
        max_length=100, help_text=_("Animal tag number (can be temporary)")
    )

    breed = models.ForeignKey(
        SpeciesBreed,
        on_delete=models.CASCADE,
        related_name="animals_breed",
        blank=True,
        null=True,
        help_text=_("Breed of the cattle."),
        verbose_name=_("Breed"),
    )

    age_years = models.PositiveIntegerField(
        null=True, blank=True, help_text=_("Age in years")
    )

    age_months = models.PositiveIntegerField(
        null=True, blank=True, help_text=_("Additional months")
    )

    weight_kg = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Weight in kilograms"),
    )

    is_pregnant = models.BooleanField(
        default=False, help_text=_("Is the animal pregnant")
    )

    pregnancy_months = models.PositiveIntegerField(
        null=True, blank=True, help_text=_("Pregnancy duration in months")
    )

    additional_details = models.TextField(
        blank=True, help_text=_("Additional animal details")
    )

    is_active = models.BooleanField(
        default=True, help_text=_("Is the cattle record active")
    )

    sync = models.BooleanField(default=False, help_text=_("Sync status with server"))

    class Meta:
        db_table = "tbl_non_member_cattle"
        verbose_name = _("Non Member Cattle")
        verbose_name_plural = _("Non Member Cattle")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tag_number"], name="idx_nonmembercattle_tag"),
            models.Index(fields=["non_member"], name="idx_nonmembercattle_owner"),
        ]
        # Allow duplicate tag numbers for non-members (as they might be temporary)
        # unique_together = [['non_member', 'tag_number']]

    def __str__(self):
        return f"{self.tag_number} - {self.non_member.name} ({self.breed})"


class Cattle(BaseModel):
    # Add a unique business identifier
    cattle_code = models.CharField(
        max_length=40,
        unique=True,
        editable=False,
        null=True,
        blank=True,
        help_text=_("Deterministic unique cattle identifier"),
        verbose_name=_("Cattle Code"),
    )

    name = models.CharField(max_length=100, null=True, blank=True)
    owner = models.ForeignKey(
        MembersMasterCopy,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_cattles",
        help_text=_("Member who currently owns this cattle."),
        verbose_name=_("Owner"),
    )

    breed = models.ForeignKey(
        SpeciesBreed,
        on_delete=models.CASCADE,
        related_name="breed_animals",
        blank=True,
        null=True,
        help_text=_("Breed of the cattle."),
        verbose_name=_("Breed"),
    )

    gender = models.CharField(
        max_length=10,
        choices=GenderChoices.choices,
        default=GenderChoices.MALE,
        help_text=_("Gender of the cattle."),
        verbose_name=_("Gender"),
    )

    age = models.PositiveIntegerField(
        help_text=_("Age of the cattle in months."),
        verbose_name=_("Age (months)"),
    )
    age_year = models.PositiveIntegerField(
        help_text=_("Age of the cattle in year."),
        verbose_name=_("Age (year)"),
        null=True,
        blank=True,
    )
    no_of_calving = models.PositiveIntegerField(
        help_text=_("No Of Calving."),
        verbose_name=_("Lactation Count"),
        null=True,
        blank=True,
        default=0,
    )
    weight_kg = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Weight in kilograms"),
    )

    mother = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="offspring_from_mother",
        help_text=_("The mother of this cattle."),
        verbose_name=_("Mother"),
    )

    father = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="offspring_from_father",
        help_text=_("The father of this cattle."),
        verbose_name=_("Father"),
    )

    date_of_birth = models.DateField(null=True, blank=True)
    is_alive = models.BooleanField(default=True)

    current_status = models.ForeignKey(
        CattleStatusType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="animals_currently_in_status",
        verbose_name="Current Status",
    )

    # Add business constraint fields
    is_sold = models.BooleanField(
        default=False, help_text=_("Whether this cattle has been sold")
    )
    sold_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)

    # Add tracking fields
    last_status_update = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Auto-generate cattle_code if not exists
        if not self.cattle_code:
            self.cattle_code = self._generate_deterministic_code()

        # Auto-generate name if not provided
        if not self.name:
            owner_name = self.owner.member_name if self.owner else "Unknown"
            self.name = f"{owner_name} cattle"

        # Update last_status_update when current_status changes
        if self.pk:
            try:
                old_instance = Cattle.objects.get(pk=self.pk)
                if old_instance.current_status != self.current_status:
                    self.last_status_update = timezone.now()
            except Cattle.DoesNotExist:
                pass

        # self.clean()
        super().save(*args, **kwargs)

    def _generate_deterministic_code(self):
        """Generate cattle code based on Member Code + Age + Age_Year + Gender."""
        member_part = (
            self.owner.member_code[-4:]
            if self.owner and self.owner.member_code
            else "0000"
        )

        age_part = f"A{self.age or 0}"
        age_year_part = f"Y{self.age_year or 0}"
        gender_part = self.gender[0].upper() if self.gender else "U"

        base_code = f"CTL-{member_part}-{age_part}{age_year_part}-{gender_part}"

        # Check for collision (another cattle with same base_code)
        if Cattle.objects.filter(cattle_code=base_code).exclude(pk=self.pk).exists():
            # Add short deterministic hash from owner + age to disambiguate
            raw_string = (
                f"{self.owner.member_code or 0}{self.age}{self.age_year}{self.gender}"
            )
            hash_suffix = hashlib.sha1(raw_string.encode()).hexdigest()[:4].upper()
            base_code = f"{base_code}-{hash_suffix}"

        return base_code

    def transfer_ownership(self, new_owner, *, updated_by=None, reason=None, save=True):
        """Enhanced ownership transfer with history tracking"""
        if not isinstance(new_owner, MembersMasterCopy):
            raise ValueError("new_owner must be a valid MembersMasterCopy instance.")

        if self.owner == new_owner:
            return False

        old_owner = self.owner
        self.owner = new_owner

        if save:
            with transaction.atomic():
                self.save(update_fields=["owner", "updated_at"])

                # Create ownership history record (if you have such model)
                CattleOwnershipHistory.objects.create(
                    cattle=self,
                    from_owner=old_owner,
                    to_owner=new_owner,
                    transfer_date=timezone.now().date(),
                    reason=reason,
                    updated_by=updated_by,
                )

        return True

    @property
    def tag_detail(self):
        """Tag assigned to the cattle (1-1 relationship)."""
        return getattr(self, "cattle_tagged", None)

    @property
    def current_milk_production(self):
        """Get current milk production from latest status log"""
        latest_status = self.status_logs.filter(to_date__isnull=True).first()
        return latest_status.milk_production_lpd if latest_status else 0

    @property
    def is_pregnant(self):
        """Check if cattle is currently pregnant"""
        latest_status = self.status_logs.filter(to_date__isnull=True).first()
        return latest_status.pregnancy_status if latest_status else False

    def __str__(self):
        tag_info = self.tag_detail.tag_number if self.tag_detail else "No Tag"
        return f"{self.cattle_code} - {self.breed or 'No Breed'} - {tag_info}"

    class Meta:
        db_table = "tbl_cattle"
        verbose_name = _("Cattle")
        verbose_name_plural = _("Cattles")
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["cattle_code"]),
            models.Index(fields=["owner", "is_alive"]),
            models.Index(fields=["breed"]),
            models.Index(fields=["is_alive", "is_sold"]),
        ]
        constraints = [
            # Business constraint: sold cattle should have sold_date
            models.CheckConstraint(
                check=models.Q(is_sold=False) | models.Q(sold_date__isnull=False),
                name="sold_cattle_must_have_sold_date",
            ),
            # Business constraint: dead cattle should have death_date
            models.CheckConstraint(
                check=models.Q(is_alive=True) | models.Q(death_date__isnull=False),
                name="dead_cattle_must_have_death_date",
            ),
        ]


class CattleTagging(BaseModel):
    cattle = models.OneToOneField(
        Cattle,
        on_delete=models.CASCADE,
        related_name="cattle_tagged",
        help_text="The cattle being tagged",
    )

    image = models.ImageField(upload_to="tagging/images/", null=True, blank=True)

    tag_number = models.CharField(
        max_length=20,
        help_text="Physical tag number for the cattle (e.g., IND-12345)",
        verbose_name="Tag Number",
    )

    tag_method = models.CharField(
        max_length=10,
        choices=TagMethodChoices.choices,
        default=TagMethodChoices.MANUAL,
        help_text="Method used for tagging the cattle",
    )

    tag_location = models.CharField(
        max_length=20,
        choices=TagLocationChoices.choices,
        default=TagLocationChoices.LEFT_EAR,
        help_text="Physical location on the body where the tag is placed",
    )

    tag_action = models.CharField(
        max_length=10,
        choices=TagActionChoices.choices,
        default=TagActionChoices.CREATED,
        help_text="Whether this tag is newly created or a replacement",
    )

    replaced_on = models.DateField(
        null=True,
        blank=True,
        help_text="If tag was replaced, provide the replacement date",
    )

    remarks = models.TextField(
        blank=True,
        null=True,
        help_text="Additional comments, reason for replacement, etc.",
    )

    virtual_tag_no = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        blank=True,
        null=True,
        help_text="Auto-generated virtual tag number",
    )

    # Add status tracking
    is_active = models.BooleanField(
        default=True, help_text="Whether this tag is currently active"
    )
    tag_status = models.CharField(
        max_length=20,
        choices=[
            ("ACTIVE", "Active"),
            ("LOST", "Lost"),
            ("DAMAGED", "Damaged"),
            ("REPLACED", "Replaced"),
        ],
        default="ACTIVE",
    )

    def clean(self):
        """Validation for tagging business rules"""
        if self.tag_action == TagActionChoices.REPLACED and not self.replaced_on:
            raise ValidationError(
                _("Replacement date is required when tag action is REPLACED")
            )

        if self.replaced_on and self.replaced_on > timezone.now().date():
            raise ValidationError(_("Replacement date cannot be in the future"))

    def save(self, *args, **kwargs):
        # Generate virtual tag number if not exists
        if not self.virtual_tag_no:
            self.virtual_tag_no = self._generate_virtual_tag_no()
        if not self.tag_number:
            self.tag_number = self._generate_unique_tag()

        # Update tag status based on action
        if self.tag_action == TagActionChoices.REPLACED:
            self.is_active = False
            self.tag_status = "REPLACED"

        self.clean()
        super().save(*args, **kwargs)

    def _generate_unique_tag(self):
        """
        Generate a unique tag number.
        You can adjust the format as per business rules.
        """
        prefix = "CTL"
        while True:
            candidate = f"{prefix}-{uuid.uuid4().hex[:12].upper()}"
            if not Cattle.objects.filter(tag_number=candidate).exists():
                return candidate

    def _generate_virtual_tag_no(self):
        """Generate unique virtual tag number"""
        while True:
            # Format: OWNER_CODE-CATTLE_CODE-TAG_SEQUENCE
            owner_code = (
                self.cattle.owner.member_tr_code if self.cattle.owner else "UNK"
            )
            cattle_code = self.cattle.cattle_code.split("-")[-1]

            # Count existing tags for this cattle (for sequence)
            sequence = (
                CattleTagging.objects.filter(cattle__owner=self.cattle.owner).count()
                + 1
            )

            virtual_tag = f"{owner_code}-{cattle_code}-{sequence:03d}"

            if not CattleTagging.objects.filter(virtual_tag_no=virtual_tag).exists():
                return virtual_tag

    def replace_tag(self, new_tag_number, reason=None):
        """Replace this tag with a new one"""
        with transaction.atomic():
            # Mark current tag as replaced
            self.tag_action = TagActionChoices.REPLACED
            self.replaced_on = timezone.now().date()
            self.is_active = False
            self.tag_status = "REPLACED"
            self.remarks = f"Replaced: {reason}" if reason else "Tag replaced"
            self.save()

            # Create new tag
            new_tag = CattleTagging.objects.create(
                cattle=self.cattle,
                tag_number=new_tag_number,
                tag_method=self.tag_method,
                tag_location=self.tag_location,
                tag_action=TagActionChoices.CREATED,
                remarks=f"Replacement for {self.tag_number}",
            )

            return new_tag

    def __str__(self):
        status = f"({self.tag_status})" if self.tag_status != "ACTIVE" else ""
        return f"{self.cattle} | Tag: {self.tag_number} | Virtual: {self.virtual_tag_no} {status}"

    class Meta:
        db_table = "tbl_cattle_tagging"
        verbose_name = "Cattle Tagging"
        verbose_name_plural = "Cattle Tagging"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tag_number", "is_active"]),
            models.Index(fields=["cattle"]),
            models.Index(fields=["virtual_tag_no"]),
            models.Index(fields=["tag_status"]),
        ]
        constraints = [
            # Ensure tag_number is unique among active tags
            models.UniqueConstraint(
                fields=["tag_number"],
                condition=models.Q(is_active=True),
                name="unique_active_tag_number",
            ),
            # Ensure only one active tag per cattle
            models.UniqueConstraint(
                fields=["cattle"],
                condition=models.Q(is_active=True),
                name="one_active_tag_per_cattle",
            ),
        ]


class CattleStatusLog(BaseModel):
    cattle = models.ForeignKey(
        Cattle,
        on_delete=models.CASCADE,
        related_name="status_logs",
        verbose_name="Cattle",
    )

    last_calving_month = models.CharField(
        max_length=10,
        choices=MonthChoices.choices,
        blank=True,
        null=True,
        help_text="Month of last calving (optional)",
        verbose_name=_("Last Calving Month"),
    )

    statuses = models.ManyToManyField(
        CattleStatusType,
        related_name="cattle_logs",
        verbose_name="Cattle Statuses",
        help_text="Multiple statuses like MILKING, PREGNANT, DRY etc.",
    )

    from_date = models.DateField(verbose_name="From Date")
    to_date = models.DateField(null=True, blank=True, verbose_name="To Date")

    notes = models.TextField(
        blank=True, null=True, help_text="Any remarks from field vet or technician"
    )

    pregnancy_status = models.BooleanField(
        default=False,
        verbose_name=_("Pregnancy Status"),
        help_text=_("Indicates whether the cattle is pregnant."),
    )

    milk_production_lpd = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        default=0,
        verbose_name=_("Milk Production (LPD)"),
        help_text=_("Average milk production in Liters per Day."),
    )

    # Enhanced tracking
    recorded_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who recorded this status",
    )

    is_current = models.BooleanField(
        default=True, help_text="Whether this is the current active status"
    )

    def clean(self):
        """Business validation for status logs"""
        if self.from_date and self.to_date and self.from_date > self.to_date:
            raise ValidationError(_("From date cannot be after to date"))

        if self.from_date and self.from_date > timezone.now().date():
            raise ValidationError(_("From date cannot be in the future"))

        if self.milk_production_lpd and self.milk_production_lpd < 0:
            raise ValidationError(_("Milk production cannot be negative"))

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        self.clean()

        with transaction.atomic():
            if is_new and self.is_current:
                # Mark all other status logs for this cattle as not current
                CattleStatusLog.objects.filter(
                    cattle=self.cattle, is_current=True
                ).update(is_current=False, to_date=timezone.now().date())

            super().save(*args, **kwargs)

            # Update cattle's current status if this is the current log
            if self.is_current and not self.to_date:
                # Update cattle's current_status with the primary status
                primary_status = self.statuses.first()
                if primary_status:
                    self.cattle.current_status = primary_status
                    self.cattle.last_status_update = timezone.now()
                    self.cattle.save(
                        update_fields=["current_status", "last_status_update"]
                    )

    def close_status(self, end_date=None, reason=None):
        """Close this status log"""
        self.to_date = end_date or timezone.now().date()
        self.is_current = False
        if reason:
            self.notes = f"{self.notes or ''}\nClosed: {reason}".strip()
        self.save()

    @property
    def duration_days(self):
        """Calculate duration of this status in days"""
        end_date = self.to_date or timezone.now().date()
        return (end_date - self.from_date).days

    @property
    def status_names(self):
        """Get comma-separated status names"""
        return ", ".join(s.code for s in self.statuses.all())

    def __str__(self):
        status_labels = self.status_names
        pregnant_info = " (Pregnant)" if self.pregnancy_status else ""
        milk_info = f" | Milk: {self.milk_production_lpd or 0} LPD"
        current_info = " [CURRENT]" if self.is_current else ""

        return (
            f"{self.cattle} → {status_labels}{pregnant_info} "
            f"({self.from_date} - {self.to_date or 'Ongoing'})"
            f"{milk_info}{current_info}"
        )

    class Meta:
        verbose_name = "Cattle Status Log"
        verbose_name_plural = "Cattle Status Logs"
        ordering = ["-from_date", "-created_at"]
        indexes = [
            models.Index(fields=["cattle", "from_date"]),
            models.Index(fields=["cattle", "is_current"]),
            models.Index(fields=["from_date", "to_date"]),
        ]
        constraints = [
            # Ensure only one current status per cattle
            models.UniqueConstraint(
                fields=["cattle"],
                condition=models.Q(is_current=True, to_date__isnull=True),
                name="one_current_status_per_cattle",
            ),
        ]


# Optional: Add ownership history tracking
class CattleOwnershipHistory(BaseModel):
    """Track ownership changes for audit purposes"""

    cattle = models.ForeignKey(
        Cattle, on_delete=models.CASCADE, related_name="ownership_history"
    )
    from_owner = models.ForeignKey(
        MembersMasterCopy,
        on_delete=models.SET_NULL,
        null=True,
        related_name="cattle_transferred_from",
    )
    to_owner = models.ForeignKey(
        MembersMasterCopy,
        on_delete=models.SET_NULL,
        null=True,
        related_name="cattle_transferred_to",
    )
    transfer_date = models.DateField()
    reason = models.TextField(null=True, blank=True)
    transfer_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    class Meta:
        db_table = "tbl_cattle_ownership_history"
        ordering = ["-transfer_date"]


class FarmerMeeting(BaseModel):
    """
    Represents a farmer meeting held at an MCC (Milk Collection Center) or MPP (Milk Producer Point).
    """

    mcc_code = models.CharField(
        max_length=50,
        verbose_name=_("MCC Code"),
        help_text=_("Unique code identifying the Milk Collection Center."),
    )
    mcc_name = models.CharField(
        max_length=255,
        verbose_name=_("MCC Name"),
        help_text=_("Name of the Milk Collection Center where the meeting is held."),
    )
    mcc_ex_code = models.CharField(
        max_length=50,
        verbose_name=_("MCC External Code"),
        help_text=_(
            "External reference code for the Milk Collection Center (for integration purposes)."
        ),
        blank=True,
        null=True,
    )
    mpp_code = models.CharField(
        max_length=50,
        verbose_name=_("MPP Code"),
        help_text=_("Unique code identifying the Milk Pulling Point."),
    )
    mpp_ex_code = models.CharField(
        max_length=50,
        verbose_name=_("MPP External Code"),
        help_text=_(
            "External reference code for the Milk Pulling Point (for integration purposes)."
        ),
        blank=True,
        null=True,
    )
    mpp_name = models.CharField(
        max_length=255,
        verbose_name=_("MPP Name"),
        help_text=_("Name of the Milk Pulling Point where the meeting is held."),
    )
    members = models.ManyToManyField(
        MembersMasterCopy,
        related_name="farmer_meetings",
        verbose_name=_("Members"),
        help_text=_("Members who attended or are associated with this meeting."),
        blank=True,
    )
    total_participants = models.PositiveIntegerField(
        verbose_name=_("Total Participants"),
        help_text=_("Total number of participants who attended the meeting."),
    )
    image = models.ImageField(
        upload_to="farmer_meetings/",
        verbose_name=_("Meeting Image"),
        help_text=_("Image related to the meeting (e.g., group photo, event capture)."),
        blank=True,
        null=True,
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Additional Notes"),
        help_text=_("Any notes(optional)"),
    )

    class Meta:
        db_table = "farmer_meetings"
        verbose_name = _("Farmer Meeting")
        verbose_name_plural = _("Farmer Meetings")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["mcc_code"], name="idx_farmermeeting_mcc_code"),
            models.Index(fields=["mpp_code"], name="idx_farmermeeting_mpp_code"),
        ]

    def __str__(self):
        return f"Farmer Meeting at {self.mpp_name} ({self.mcc_name})"


class ObservationType(BaseModel):
    """
    Master table for types of observations recorded for cattle.
    """

    name = models.CharField(
        max_length=255,
        verbose_name=_("Name"),
        help_text=_("Human-readable name of the observation type."),
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description"),
        help_text=_("Detailed explanation of this observation type."),
    )

    class Meta:
        db_table = "observation_types"
        verbose_name = _("Observation Type")
        verbose_name_plural = _("Observation Types")
        ordering = ["name"]

    def __str__(self):
        return self.name


class FarmerObservation(BaseModel):
    """
    Represents an observation recorded for a farmer's cattle at an MCC/MPP level.
    """

    # MCC (Milk Collection Center) info
    mcc_code = models.CharField(
        max_length=50,
        verbose_name=_("MCC Code"),
        help_text=_("Unique code identifying the Milk Collection Center."),
    )
    mcc_name = models.CharField(
        max_length=255,
        verbose_name=_("MCC Name"),
        help_text=_("Name of the Milk Collection Center."),
    )
    mcc_ex_code = models.CharField(
        max_length=50,
        verbose_name=_("MCC External Code"),
        help_text=_("External reference code for the Milk Collection Center."),
        blank=True,
        null=True,
    )

    # MPP (Milk Producer Point) info
    mpp_code = models.CharField(
        max_length=50,
        verbose_name=_("MPP Code"),
        help_text=_("Unique code identifying the Milk Producer Point."),
    )
    mpp_ex_code = models.CharField(
        max_length=50,
        verbose_name=_("MPP External Code"),
        help_text=_("External reference code for the Milk Producer Point."),
        blank=True,
        null=True,
    )
    mpp_name = models.CharField(
        max_length=255,
        verbose_name=_("MPP Name"),
        help_text=_("Name of the Milk Producer Point."),
    )

    # Relations
    member = models.ForeignKey(
        MembersMasterCopy,
        on_delete=models.CASCADE,
        related_name="farmer_observations",
        verbose_name=_("Member"),
        help_text=_("Reference to the member associated with this observation."),
    )
    animal = models.ForeignKey(
        Cattle,
        on_delete=models.CASCADE,
        related_name="observations",
        verbose_name=_("Animal"),
        help_text=_("The cattle for which the observation is recorded."),
    )

    observation_type = models.ForeignKey(
        ObservationType,
        on_delete=models.PROTECT,
        related_name="observations",
        verbose_name=_("Observation Type"),
        help_text=_("Type of observation recorded for this animal."),
    )

    notes = models.TextField(
        blank=True, null=True, help_text="Any remarks from field vet or technician"
    )

    class Meta:
        db_table = "farmer_observations"
        verbose_name = _("Farmer Observation")
        verbose_name_plural = _("Farmer Observations")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["mcc_code"], name="idx_farmerobservation_mcc_code"),
            models.Index(fields=["mpp_code"], name="idx_farmerobservation_mpp_code"),
            models.Index(fields=["member"], name="idx_farmerobservation_member"),
            models.Index(fields=["animal"], name="idx_farmerobservation_animal"),
        ]

    def __str__(self):
        return f"Observation ({self.get_observation_display()}) - {self.animal} by {self.member}"
