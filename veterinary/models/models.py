from django.utils.translation import gettext_lazy as _
from ..choices.choices import *
from django.db import models
from django.utils import timezone
from .common_models import BaseModel, User, SpeciesBreed, CattleStatusType

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


class Cattle(BaseModel):
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
        verbose_name=_("Age (year)"),
        null=True,
        blank=True,
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

    def __str__(self):
        return f"{self.breed.animal_type if self.breed else 'Unknown'} - {self.breed or 'No Breed'} - {self.tag_detail.tag_number if self.tag_detail else 'No Tag'}"

    # --- Relationships ---
    @property
    def children(self):
        """All offspring born from this cattle (mother only)."""
        return self.offspring_from_mother.all()

    @property
    def sons(self):
        return self.children.filter(gender=GenderChoices.MALE)

    @property
    def daughters(self):
        return self.children.filter(gender=GenderChoices.FEMALE)

    @property
    def tag_detail(self):
        """Tag assigned to the cattle (1-1 relationship)."""
        return getattr(self, "cattle_tagged", None)

    @property
    def cases(self):
        """All medical cases related to this cattle."""
        return self.cattle_cases.all()

    @property
    def ai_history(self):
        return self.ai_records.all().order_by("-insemination_date")

    def all_details(self):
        """Return a dictionary of full cattle details."""
        return {
            "animal": self,
            "cases": list(self.cases),
            "treatments": list(self.treatments),
        }

    def transfer_ownership(self, new_owner, *, updated_by=None, reason=None, save=True):
        """
        Transfers ownership of this cattle to another member.

        Args:
            new_owner (MemberMaster): New owner to transfer the cattle to.
            updated_by (User, optional): User initiating the transfer.
            reason (str, optional): Business reason for transfer.
            save (bool): Whether to save the object immediately.

        Returns:
            bool: True if the transfer occurred.
        """
        if not isinstance(new_owner, MembersMasterCopy):
            raise ValueError("new_owner must be a valid MemberMaster instance.")

        if self.owner == new_owner:
            return False

        old_owner = self.owner
        self.owner = new_owner

        if save:
            self.save(update_fields=["owner", "updated_at"])
        return True

    class Meta:
        db_table = "tbl_cattle"
        verbose_name = _("Cattle")
        verbose_name_plural = _("Cattles")
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["breed"]),
        ]


class CattleTagging(BaseModel):
    cattle = models.OneToOneField(
        Cattle,
        on_delete=models.CASCADE,
        related_name="cattle_tagged",
        help_text="The cattle being tagged",
    )
    image = models.ImageField(upload_to="tagging/images/")

    tag_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique tag number for the cattle (e.g., IND-12345)",
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

    def __str__(self):
        return (
            f"{self.cattle} | Tag: {self.tag_number} | Date: {self.created_at.date()}"
        )

    def is_recent(self):
        return (timezone.now().date() - self.created_at.date()).days <= 30

    class Meta:
        db_table = "tbl_cattle_tagging"
        verbose_name = "Cattle Tagging"
        verbose_name_plural = "Cattle Tagging"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tag_number"]),
            models.Index(fields=["cattle"]),
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

    class Meta:
        verbose_name = "Cattle Status Log"
        verbose_name_plural = "Cattle Status Logs"
        ordering = ["-from_date"]
        indexes = [
            models.Index(fields=["cattle", "from_date"]),
        ]

    def __str__(self):
        status_labels = ", ".join(s.code for s in self.statuses.all())
        return f"{self.cattle} → {status_labels} ({self.from_date} - {self.to_date or 'Ongoing'})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.to_date:
            self.cattle.current_status.set(self.statuses.all())


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
