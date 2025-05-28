from all_imports import *
from django.core.validators import (
    MinLengthValidator,
    MaxLengthValidator,
    MinValueValidator,
    RegexValidator,
)
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from ..choices.choices import *

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
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",
        help_text="User who created this record",
        verbose_name=_("Created By"),
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

    class Meta:
        abstract = True
        ordering = ["-created_at"]

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


class AnimalType(BaseModel):
    animal_type = models.CharField(
        max_length=100,
        unique=True,
        validators=[MinLengthValidator(2)],
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
        if not self.slug:
            self.slug = slugify(self.animal_type)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.animal_type

    class Meta:
        db_table = "tbl_animal_type"
        verbose_name = "Cattle Type"
        verbose_name_plural = "Cattle Types"
        ordering = ["animal_type"]
        indexes = [
            models.Index(fields=["animal_type"]),
        ]


class AnimalBreed(BaseModel):
    breed = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(2)],
        help_text="Enter the breed name (e.g., Jersey, Holstein)",
        verbose_name="Breed",
    )

    animal_type = models.ForeignKey(
        AnimalType,
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
        db_table = "tbl_animal_breed"
        verbose_name = "Cattle Breed"
        verbose_name_plural = "Cattle Breeds"
        ordering = ["breed"]
        indexes = [
            models.Index(fields=["breed"]),
            models.Index(fields=["animal_type"]),
        ]

    def __str__(self):
        return f"{self.breed} ({self.animal_type.animal_type})"


class Cattle(BaseModel):

    module = models.CharField(
        max_length=20,
        help_text="Module, for ex, sahayak, member, etc",
        verbose_name=_(""),
    )
    module_code = models.CharField(
        max_length=50,
        help_text="Module code",
    )

    breed = models.ForeignKey(
        AnimalBreed,
        on_delete=models.CASCADE,
        related_name="breed_animals",
        blank=True,
        null=True,
        help_text="Select the breed of the cattle",
    )

    gender = models.CharField(
        max_length=10,
        choices=GenderChoices.choices,
        default=GenderChoices.MALE,
        help_text="Gender of the cattle",
        verbose_name=_("Gender"),
    )

    age = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        help_text="Age of the cattle in months",
        verbose_name=_("Age"),
    )

    mother = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="offspring",
        help_text="The mother of this cattle",
    )

    def __str__(self):
        return f"{self.breed.animal_type} - {self.breed} - {self.tag_detail.tag_number}"

    @property
    def children(self):
        """Returns all offspring of this cattle (if female)."""
        return self.offspring.all()

    @property
    def tag_detail(self):
        """Returns tagging detail of this cattle."""
        return self.cattle_tagged

    @property
    def sons(self):
        return self.offspring.filter(gender="Male")

    @property
    def daughters(self):
        return self.offspring.filter(gender="Female")

    @property
    def cases(self):
        """Returns all medical cases related to this cattle."""
        return self.cattle_cases.all()

    @property
    def ai_history(self):
        return self.ai_records.all().order_by("-insemination_date")

    @property
    def treatments(self):
        """Returns all treatments associated with this cattle."""
        return AnimalTreatment.objects.filter(case_treatment__animal=self)

    def all_details(self):
        """Returns a dictionary of all cattle details including cases and treatments."""
        return {
            "animal": self,
            "cases": list(self.cases),
            "treatments": list(self.treatments),
        }

    class Meta:
        db_table = "tbl_cattle"
        verbose_name = "Cattle"
        verbose_name_plural = "Cattles"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["breed"]),
        ]


class AICharge(models.Model):

    user_role = models.CharField(
        max_length=20,
        choices=UserRoleChoices.choices,
        default=UserRoleChoices.MAT,
        help_text="Role of the user performing AI",
        verbose_name="User Role",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
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


class ArtificialInsemination(BaseModel):
    RESULT_CHOICES = (
        ("Pending", "Pending"),
        ("Successful", "Successful"),
        ("Failed", "Failed"),
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="performed_ais",
        help_text="User who performed the insemination (e.g., Doctor, MAT)",
        verbose_name="Performed By",
    )

    cattle = models.ForeignKey(
        Cattle,
        on_delete=models.CASCADE,
        related_name="ai_records",
        help_text="Cattle that received the insemination",
    )
    insemination_date = models.DateField(help_text="Date when the AI was performed")

    semen_batch_number = models.CharField(
        max_length=50, help_text="Batch number or ID of the semen used"
    )
    technician_name = models.CharField(
        max_length=100, help_text="Name of the technician or vet who performed the AI"
    )
    result = models.CharField(
        max_length=20,
        choices=RESULT_CHOICES,
        default="Pending",
        help_text="Outcome of the insemination",
    )
    notes = models.TextField(
        blank=True, null=True, help_text="Additional notes or observations"
    )

    otp_sent_to = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Phone number or contact where OTP was sent",
        verbose_name="OTP Sent To",
    )
    otp_verified = models.BooleanField(
        default=False,
        help_text="Indicates whether the OTP has been verified",
        verbose_name="OTP Verified",
    )
    otp_sent_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp when OTP was sent",
        verbose_name="OTP Sent At",
    )
    otp_verified_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp when OTP was successfully verified",
        verbose_name="OTP Verified At",
    )

    def get_charge_amount(self):
        if not self.performed_by:
            return 0
        charge = AICharge.objects.filter(user=self.performed_by).first()
        if charge:
            return charge.amount
        user_role = getattr(self.performed_by, "role", None)
        charge = AICharge.objects.filter(user_role=user_role).first()
        if charge:
            return charge.amount
        return 0

    def __str__(self):
        return f"AI for {self.cattle.tag_detail.tag_number} on {self.insemination_date}"

    class Meta:
        db_table = "tbl_artificial_insemination"
        verbose_name = "Artificial Insemination"
        verbose_name_plural = "Artificial Inseminations"
        ordering = ["-insemination_date"]
        indexes = [
            models.Index(fields=["cattle"]),
            models.Index(fields=["insemination_date"]),
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
        validators=[
            MinLengthValidator(3),
            RegexValidator(
                r"^[A-Z0-9\-]+$",
                message="Only uppercase letters, numbers, and hyphens allowed.",
            ),
        ],
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


class Symptoms(BaseModel):
    symptom = models.CharField(
        max_length=100,
        unique=True,
        help_text="Name of the symptom (e.g., Fever, Coughing)",
        verbose_name="Symptom Name",
    )

    description = models.TextField(
        null=True,
        blank=True,
        help_text="Detailed description of the symptom and its signs",
        verbose_name="Description",
    )

    def __str__(self):
        return self.symptom

    class Meta:
        db_table = "tbl_animal_symptoms"
        verbose_name = "Symptom"
        verbose_name_plural = "Symptoms"
        ordering = ["symptom"]
        indexes = [
            models.Index(fields=["symptom"]),
        ]


class Disease(BaseModel):
    disease = models.CharField(
        max_length=100,
        unique=True,
        help_text="Name of the disease (e.g., Mastitis, FMD)",
        verbose_name="Disease Name",
    )

    description = models.TextField(
        null=True,
        blank=True,
        help_text="Brief overview of the disease, symptoms, and progression",
        verbose_name="Description",
    )

    treatment = models.TextField(
        null=True,
        blank=True,
        help_text="Suggested treatment or veterinary advice",
        verbose_name="Treatment",
    )

    symptoms = models.ManyToManyField(
        Symptoms,
        related_name="diseases",
        help_text="Symptoms commonly associated with this disease",
    )

    def __str__(self):
        return self.disease

    class Meta:
        db_table = "tbl_animal_disease"
        verbose_name = "Disease"
        verbose_name_plural = "Diseases"
        ordering = ["disease"]
        indexes = [
            models.Index(fields=["disease"]),
        ]


class MedicineCategory(BaseModel):
    category = models.CharField(
        max_length=100,
        help_text=_("eg. tablet, liquid, injection, etc"),
        verbose_name=_("Category"),
    )

    medicine_form = models.CharField(
        max_length=20,
        choices=MedicineFormChoices.choices,
        default=MedicineFormChoices.TABLET,
        help_text="Form in which the medicine is administered",
    )

    unit_of_quantity = models.CharField(
        max_length=20, help_text="e.g., ml, mg, tablets"
    )

    parent_category = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
        help_text="Parent category if this is a subcategory",
        verbose_name=_("Parent Category"),
    )

    class Meta:
        db_table = "tbl_medicine_category"
        verbose_name = "Medicine Category"
        verbose_name_plural = "Medicine Categories"
        unique_together = ("category", "parent_category")

    def __str__(self):
        if self.parent_category:
            return f"{self.parent_category} > {self.category} ({self.medicine_form}) - {self.unit_of_quantity}"
        return f"{self.category} ({self.medicine_form}) - {self.unit_of_quantity}"


class Medicine(BaseModel):
    medicine = models.CharField(
        max_length=100, help_text=_("Name of the medicine"), verbose_name=_("Medicine")
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text=_("Some description of the medicine"),
        verbose_name=_("Description"),
    )
    icon = models.ImageField(
        upload_to="medicine/icon",
        help_text="Upload an icon image for the medicine (recommended size 200x200 px)",
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        MedicineCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medicines",
        help_text="Category and form of the medicine",
    )

    strength = models.CharField(
        max_length=50, help_text="e.g., 500mg, 5ml per dose", blank=True, null=True
    )

    packaging = models.CharField(
        max_length=100,
        help_text="e.g., 10 tablets per strip, 100ml bottle",
        blank=True,
        null=True,
        verbose_name=_("Packaging"),
    )

    expiry_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_("Expiry Date of the medicine"),
        verbose_name=_("Expiry Date"),
    )

    recommended_for_disease = models.ForeignKey(
        Disease,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recommended_medicines",
        help_text=_("Recommended to disease"),
        verbose_name=_("Recommended For Disease"),
    )

    def __str__(self):
        return f"{self.medicine} ({self.strength})"

    class Meta:
        db_table = "tbl_medicine"
        verbose_name = "Medicine"
        verbose_name_plural = "Medicines"


class MedicineStock(BaseModel):
    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.CASCADE,
        related_name="stocks",
        help_text="Medicine item in stock",
    )

    total_quantity = models.FloatField(
        default=0, help_text="Total quantity available (e.g., tablets, ml, vials)"
    )

    batch_number = models.CharField(
        max_length=50, blank=True, null=True, help_text="Batch number for traceability"
    )

    expiry_date = models.DateField(
        blank=True, null=True, help_text="Expiry date of this stock batch"
    )

    last_updated = models.DateTimeField(
        auto_now=True, help_text="Last time this stock was updated"
    )

    def __str__(self):
        return (
            f"{self.medicine.medicine} - {self.total_quantity} {self.medicine.category.unit_of_quantity} "
            f"(Batch: {self.batch_number or 'N/A'})"
        )

    class Meta:
        db_table = "tbl_medicine_stock"
        verbose_name = "Medicine Stock"
        verbose_name_plural = "Medicine Stock"
        ordering = ["-last_updated"]
        indexes = [
            models.Index(fields=["medicine"]),
        ]


class MedicineStockAudit(models.Model):
    medicine = models.ForeignKey(
        Medicine, on_delete=models.CASCADE, related_name="audit_logs"
    )

    transaction_type = models.CharField(
        max_length=10,
        choices=TransactionTypeChoices.choices,
        help_text="Type of stock transaction",
    )

    quantity = models.PositiveIntegerField(help_text="Quantity added/removed")

    description = models.TextField(
        null=True, blank=True, help_text="Optional notes for the stock change"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medicine_stock_changes",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tbl_medicine_stock_audit"
        verbose_name = "Medicine Stock Audit"
        verbose_name_plural = "Medicine Stock Audits"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["medicine", "transaction_type"]),
        ]

    def __str__(self):
        return f"{self.transaction_type} - {self.medicine.name} ({self.quantity})"


class UserMedicineStock(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="medicine_stocks",
        help_text="User (e.g., vet or worker) allocated with this medicine",
    )
    medicine_stock = models.ForeignKey(
        MedicineStock,
        on_delete=models.CASCADE,
        related_name="user_allocations",
        help_text="Batch and quantity of the medicine stock allocated",
    )
    allocated_quantity = models.FloatField(
        default=0,
        help_text="Quantity allocated from the stock (e.g., 10 tablets or 50 ml)",
    )
    allocation_date = models.DateField(
        auto_now_add=True, help_text="Date on which the stock was allocated"
    )
    remarks = models.TextField(
        blank=True,
        null=True,
        help_text="Optional notes for the allocation (e.g., emergency supply)",
    )
    used_quantity = models.PositiveIntegerField(
        default=0, help_text="Quantity already used by the user"
    )
    min_threshold = models.PositiveIntegerField(
        default=0, help_text="Threshold value for reminder when stock is low"
    )
    sync = models.BooleanField(
        default=False, help_text="Indicates if this record has been synced"
    )
    threshold_quantity = models.FloatField(
        default=0,
        help_text="Minimum required quantity for this user to trigger a refill reminder",
    )

    allocated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_allocations_made",
        help_text="User who made the allocation (admin or supervisor)",
    )

    def remaining_quantity(self):
        return self.allocated_quantity - self.used_quantity

    def is_below_threshold(self):
        return self.remaining_quantity() <= self.min_threshold

    def __str__(self):
        return f"{self.user.username} - {self.medicine_stock.medicine.medicine} - {self.allocated_quantity} {self.medicine_stock.medicine.category.unit_of_quantity}"

    class Meta:
        db_table = "tbl_user_medicine_stock"
        verbose_name = "User Medicine Allocation"
        verbose_name_plural = "User Medicine Allocations"
        ordering = ["-allocation_date"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["medicine_stock"]),
        ]


class UserMedicineTransaction(models.Model):
    user_medicine_stock = models.ForeignKey(
        UserMedicineStock,
        on_delete=models.CASCADE,
        related_name="transactions",
        help_text="The user's allocated medicine stock this transaction relates to",
    )

    action = models.CharField(
        max_length=10,
        choices=ActionTypeChoices.choices,
        default=ActionTypeChoices.ALLOCATED,
        help_text="The type of action performed: Allocated, Used, or Returned",
        verbose_name="Action Type",
    )

    quantity = models.FloatField(
        validators=[MinValueValidator(0.01)],
        help_text="The quantity involved in this transaction (e.g., 10 tablets, 5 ml)",
        verbose_name="Transaction Quantity",
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time when this transaction occurred",
        verbose_name="Transaction Timestamp",
    )

    note = models.TextField(
        blank=True,
        null=True,
        help_text="Optional remarks or notes about this transaction",
        verbose_name="Notes",
    )

    class Meta:
        db_table = "tbl_user_medicine_stock_transaction"
        verbose_name = "Medicine Transaction"
        verbose_name_plural = "Medicine Transactions"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user_medicine_stock"]),
            models.Index(fields=["action"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"{self.user_medicine_stock.user.username} - {self.get_action_display()}"


def transfer_stock_to_user(medicine, quantity, user, admin_user):

    stock = MedicineStock.objects.select_for_update().get(medicine=medicine)

    if stock.total_quantity < quantity:
        raise ValueError("Not enough stock available")

    # Deduct from central stock
    stock.total_quantity -= quantity
    stock.save()

    # Assign to user
    user_stock, created = UserMedicineStock.objects.get_or_create(
        user=user,
        medicine_stock=stock,
        defaults={"allocated_quantity": quantity},
    )
    if not created:
        user_stock.allocated_quantity += quantity
        user_stock.save()

    # Audit log
    MedicineStockAudit.objects.create(
        medicine=medicine,
        transaction_type="OUT",
        quantity=quantity,
        description=f"Transferred to {user.username}",
        created_by=admin_user,
    )
    UserMedicineTransaction.objects.create(
        user_medicine_stock=user_stock,
        action="ALLOCATED",
        quantity=quantity,
        note=f"Allocated stock to {user.username}",
    )


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


class CattleStatus(BaseModel):
    status = models.CharField(
        max_length=20,
        choices=CattleStatusChoices.choices,
        default=CattleStatusChoices.DRY,
        help_text=_("Cattle case status,eg:- dry, pregnant, etc"),
        verbose_name=_("Cattle Status"),
    )

    def __str__(self):
        return f"{self.diagnosis_status}"

    class Meta:
        db_table = "tbl_cattle_status"
        verbose_name = "Cattle Status"
        verbose_name_plural = "Cattle Statuses"


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


class DiagnosisRoute(models.Model):
    route = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now=True)
    sync = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.route}"

    class Meta:
        db_table = "tbl_diagnosis_route"
        verbose_name = "Diagnosis Route"
        verbose_name_plural = "Diagnosis Routes"


from django.core.validators import MinLengthValidator


class CaseEntry(BaseModel):
    animal = models.ForeignKey(
        Cattle,
        on_delete=models.CASCADE,
        related_name="cattle_cases",
        help_text="The cattle associated with this case entry",
        verbose_name="Cattle",
    )

    applied_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="case_entries",
        help_text="User who applied or recorded this case",
        verbose_name="Applied By",
    )

    status = models.ForeignKey(
        CattleCaseStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Current status of the cattle case",
        verbose_name="Case Status",
    )

    address = models.CharField(
        max_length=255,
        default="",
        help_text="Address where the case occurred or was reported",
        verbose_name="Address",
    )

    remark = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes or remarks about the case",
        verbose_name="Remarks",
    )

    advice = models.TextField(
        blank=True,
        null=True,
        help_text="Advice or instructions given for the case",
        verbose_name="Advice",
    )

    case_no = models.CharField(
        max_length=250,
        primary_key=True,
        validators=[MinLengthValidator(3)],
        help_text="Unique identifier for the case (e.g., CASE-2024-001)",
        verbose_name="Case Number",
    )

    sync = models.BooleanField(
        default=False,
        help_text="Indicates whether the entry is synced with the server",
        verbose_name="Sync Status",
    )

    def __str__(self):
        applied_by = self.applied_by.get_full_name() if self.applied_by else "N/A"
        return f"{self.case_no} - {applied_by}"

    class Meta:
        db_table = "tbl_case_entries"
        verbose_name = "Case Entry"
        verbose_name_plural = "Case Entries"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["case_no"]),
            models.Index(fields=["animal"]),
        ]

    def save(self, *args, **kwargs):
        if not self.case_no:
            farmer_code = self.animal.module_code[-6:]
            if self.animal:
                case_id = f"{farmer_code}{self.animal.tag_detail.tag_number}"
            else:
                random_number = random.randint(100, 999)
                case_id = f"{farmer_code}{random_number}"
            self.case_no = case_id
        super().save(*args, **kwargs)


class CaseReceiverLog(BaseModel):
    case_entry = models.ForeignKey(
        CaseEntry,
        on_delete=models.CASCADE,
        related_name="receiver_logs",
        blank=True,
        null=True,
        verbose_name="Case Entry",
        help_text="Reference to the case entry being transferred",
    )

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="case_transferred_from",
        verbose_name="Transferred From",
        help_text="User who previously handled the case",
    )

    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="case_transferred_to",
        verbose_name="Transferred To",
        help_text="User who is receiving the case",
    )

    remarks = models.TextField(
        blank=True,
        null=True,
        verbose_name="Remarks",
        help_text="Optional remarks for the transfer",
    )

    transferred_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Transferred At",
        help_text="Timestamp of when the case was transferred",
    )

    def __str__(self):
        return f"Case: {self.case_entry.case_no if self.case_entry else 'N/A'} | {self.from_user} ➝ {self.to_user} @ {self.transferred_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        db_table = "tbl_case_receiver_logs"
        verbose_name = "Case Receiver Log"
        verbose_name_plural = "Case Receiver Logs"
        ordering = ["-transferred_at"]
        indexes = [
            models.Index(fields=["case_entry"]),
            models.Index(fields=["to_user"]),
            models.Index(fields=["transferred_at"]),
        ]


class AnimalDiagnosis(BaseModel):
    case_entry = models.ForeignKey(
        CaseEntry,
        on_delete=models.CASCADE,
        related_name="diagnoses",
        verbose_name="Case Entry",
        help_text="The case entry associated with this diagnosis",
    )

    disease = models.ForeignKey(
        Disease,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Disease",
        help_text="Identified disease during the diagnosis",
    )

    status = models.ForeignKey(
        CattleStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Cattle Status",
        help_text="Current physiological or production status of the animal",
    )

    milk_production = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Milk Production",
        help_text="Optional note on milk production (e.g., '2.5L/day')",
    )

    case_type = models.ForeignKey(
        CattleCaseType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Case Type",
        help_text="Type of the veterinary case (e.g., Normal, Special, Operational)",
    )

    def __str__(self):
        animal_id = (
            getattr(self.case_entry.animal.tag_detail, "tag_number", "Unknown")
            if self.case_entry and hasattr(self.case_entry, "animal")
            else "N/A"
        )
        disease_name = self.disease.disease if self.disease else "Unknown Disease"
        return f"{animal_id} - {disease_name} @ {self.created_at.strftime('%Y-%m-%d')}"

    class Meta:
        db_table = "tbl_animal_diagnosis"
        verbose_name = "Animal Diagnosis"
        verbose_name_plural = "Animal Diagnoses"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["case_entry"]),
            models.Index(fields=["disease"]),
            models.Index(fields=["status"]),
        ]


class DiagnosedSymptomHistory(BaseModel):
    symptom = models.ForeignKey(
        Symptoms,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Symptom",
        help_text="Symptom associated with this diagnosis",
    )

    diagnosis = models.ForeignKey(
        AnimalDiagnosis,
        on_delete=models.CASCADE,
        related_name="diagnosis_symptoms",
        verbose_name="Animal Diagnosis",
        help_text="Diagnosis entry this symptom is related to",
    )

    remark = models.TextField(
        blank=True,
        null=True,
        verbose_name="Remark",
        help_text="Additional notes or observations about the symptom",
    )

    def __str__(self):
        diagnosis_str = (
            self.diagnosis.disease.disease
            if self.diagnosis and self.diagnosis.disease
            else "Unknown Diagnosis"
        )
        symptom_str = self.symptom.symptom if self.symptom else "Unknown Symptom"
        return (
            f"{diagnosis_str} - {symptom_str} @ {self.created_at.strftime('%Y-%m-%d')}"
        )

    class Meta:
        db_table = "tbl_animal_diagnosed_symptom"
        verbose_name = "Diagnosed Symptom"
        verbose_name_plural = "Diagnosed Symptoms"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["diagnosis"]),
            models.Index(fields=["symptom"]),
        ]


class AnimalTreatment(BaseModel):
    case_treatment = models.ForeignKey(
        CaseEntry,
        on_delete=models.CASCADE,
        related_name="animal_treatments",
        blank=True,
        null=True,
        verbose_name="Case Entry",
        help_text="The case entry to which this treatment belongs",
    )
    treatment_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="treatments_done",
        verbose_name="Treatment Provider",
        help_text="User (doctor or vet) who performed the treatment",
    )
    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Medicine",
        help_text="Medicine used in the treatment, if any",
    )
    route = models.ForeignKey(
        DiagnosisRoute,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Administration Route",
        help_text="Route of administration for the medicine",
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes",
        help_text="Additional notes or instructions for the treatment",
    )

    otp_verified = models.BooleanField(
        default=False,
        verbose_name="OTP Verified",
        help_text="Indicates whether the treatment has been verified via OTP",
    )

    def __str__(self):
        case_no = self.case_treatment.case_no if self.case_treatment else "No Case"
        medicine_name = self.medicine.name if self.medicine else "No Medicine"
        return f"Treatment for Case: {case_no} | Medicine: {medicine_name} | By: {self.treatment_by.username}"

    class Meta:
        db_table = "tbl_animal_treatments"
        verbose_name = "Animal Treatment"
        verbose_name_plural = "Animal Treatments"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["case_treatment"]),
            models.Index(fields=["treatment_by"]),
            models.Index(fields=["medicine"]),
        ]


class CasePayment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    case_entry = models.ForeignKey(
        CaseEntry,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Case Entry",
        help_text="Case associated with this payment",
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.CASCADE,
        verbose_name="Payment Method",
        help_text="Method used for payment",
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Amount", help_text="Amount paid"
    )
    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Payment Date",
        help_text="Date and time when payment was made",
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Transaction ID",
        help_text="Payment gateway transaction reference number or manual receipt ID",
    )
    payment_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="Payment Status",
        help_text="Current status of the payment",
    )
    gateway_response = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Gateway Response",
        help_text="Raw payment gateway response data (only for online payments)",
    )
    is_reconciled = models.BooleanField(
        default=False,
        verbose_name="Is Reconciled",
        help_text="Indicates if the payment is reconciled in accounting",
    )

    # Additional fields for COD/Offline payments
    is_collected = models.BooleanField(
        default=False,
        verbose_name="Is Cash Collected",
        help_text="Indicates if cash payment has been collected (for COD)",
    )
    collected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="collected_payments",
        verbose_name="Collected By",
        help_text="User who collected the cash (for COD)",
    )
    collected_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Collected Date",
        help_text="Date and time when cash was collected",
    )

    def __str__(self):
        method_name = (
            self.payment_method.online_payment.gateway_name
            if hasattr(self.payment_method, "online_payment")
            and self.payment_method.online_payment
            else self.payment_method.method
        )
        return f"Payment: {self.amount} for Case: {self.case_entry.case_no} via {method_name} [{self.payment_status}]"

    class Meta:
        db_table = "tbl_case_payments"
        verbose_name = "Case Payment"
        verbose_name_plural = "Case Payments"
        ordering = ["-payment_date"]
        indexes = [
            models.Index(fields=["case_entry"]),
            models.Index(fields=["payment_method"]),
            models.Index(fields=["payment_status"]),
            models.Index(fields=["transaction_id"]),
        ]


from math import radians, sin, cos, sqrt, atan2


class TravelRecord(models.Model):
    case_entry = models.OneToOneField(
        CaseEntry, on_delete=models.CASCADE, related_name="travel_records"
    )
    from_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    from_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    to_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    to_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    distance_travelled = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"Case Entry: {self.case_entry.case_no} - Distance Travelled: {self.distance_travelled} km - Date: {self.date}"

    class Meta:
        verbose_name = "Travel Record"
        verbose_name_plural = "Travel Records"

    def save(self, *args, **kwargs):
        if (
            self.from_latitude
            and self.from_longitude
            and self.to_latitude
            and self.to_longitude
        ):
            self.distance_travelled = self.calculate_distance()
        super().save(*args, **kwargs)

    def calculate_distance(self):
        from_lat = radians(float(self.from_latitude))
        from_lon = radians(float(self.from_longitude))
        to_lat = radians(float(self.to_latitude))
        to_lon = radians(float(self.to_longitude))
        R = 6371.0
        # Calculate the differences in latitude and longitude
        dlat = to_lat - from_lat
        dlon = to_lon - from_lon
        a = sin(dlat / 2) ** 2 + cos(from_lat) * cos(to_lat) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c

        return distance
