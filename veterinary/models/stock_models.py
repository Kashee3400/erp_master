from django.utils.translation import gettext_lazy as _
from ..choices.choices import *
from django.db import models
from django.conf import settings
from .common_models import BaseModel, User
from django.utils import timezone

class Location(BaseModel):
    name = models.CharField(
        max_length=255,
        help_text=_("Name of the location (e.g., Central Store, Block Office)"),
        verbose_name=_("Location Name"),
    )

    code = models.CharField(
        max_length=50,
        unique=True,
        help_text=_("Unique identifier for the location (e.g., for integration)"),
        verbose_name=_("Location Code"),
    )

    type = models.CharField(
        max_length=30,
        choices=LocationTypeChoices.choices,
        default=LocationTypeChoices.CLINIC,
        help_text=_("Category or type of the location"),
        verbose_name=_("Location Type"),
    )

    address = models.TextField(
        blank=True,
        null=True,
        help_text=_("Full address of the location"),
        verbose_name=_("Address"),
    )

    district = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_("District in which the location falls"),
        verbose_name=_("District"),
    )

    state = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_("State or province"),
        verbose_name=_("State"),
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        help_text=_("Latitude coordinate for map integration"),
        verbose_name=_("Latitude"),
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        help_text=_("Longitude coordinate for map integration"),
        verbose_name=_("Longitude"),
    )

    class Meta:
        db_table = "tbl_location"
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["type"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def coordinates(self):
        if self.latitude is not None and self.longitude is not None:
            return (float(self.latitude), float(self.longitude))
        return None


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
    severity = models.CharField(
        max_length=10,
        choices=DiseaseSeverity.choices,
        default=DiseaseSeverity.MODERATE,
        help_text=_("Severity level of the disease"),
        verbose_name=_("Severity"),
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
    diseases = models.ManyToManyField(
        "Disease",
        related_name="medicines",
        help_text=_("Diseases this medicine is commonly prescribed for."),
        verbose_name=_("Diseases"),
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


from datetime import timedelta


class MedicineStockTransferLog(models.Model):
    from_location = models.ForeignKey(
        "Location",
        on_delete=models.CASCADE,
        related_name="outgoing_transfers",
        help_text=_("Location sending the medicine"),
    )

    to_location = models.ForeignKey(
        "Location",
        on_delete=models.CASCADE,
        related_name="incoming_transfers",
        help_text=_("Location receiving the medicine"),
    )

    medicine_stock = models.ForeignKey(
        "MedicineStock",
        on_delete=models.CASCADE,
        help_text=_("The batch of medicine being transferred"),
    )

    quantity_transferred = models.FloatField(
        help_text=_("Exact quantity of medicine transferred from stock")
    )

    transfer_type = models.CharField(
        max_length=10,
        choices=TransferTypeChoices.choices,
        default=TransferTypeChoices.OUTWARD,
        help_text=_("Type of transfer (inward, outward, return)"),
    )

    status = models.CharField(
        max_length=20,
        choices=TransferStatusChoices.choices,
        default=TransferStatusChoices.PENDING,
        help_text=_("Current status of the stock transfer"),
    )

    batch_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Snapshot of the batch number at the time of transfer"),
    )

    expiry_date = models.DateField(
        blank=True,
        null=True,
        help_text=_("Snapshot of expiry date at time of transfer"),
    )

    transferred_by = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medicine_transfers_made",
        help_text=_("User who initiated the stock transfer"),
    )

    received_by = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medicine_transfers_received",
        help_text=_("User who received the stock at destination"),
    )

    transfer_date = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Timestamp when the stock was transferred"),
    )

    received_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_("Timestamp when stock was received and confirmed"),
    )

    remarks = models.TextField(
        blank=True,
        null=True,
        help_text=_("Optional comments or notes on the transfer"),
    )

    unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Cost per unit for tracking valuation"),
    )

    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Total cost of transferred quantity"),
    )

    class Meta:
        db_table = "tbl_medicine_stock_transfer_log"
        verbose_name = _("Medicine Stock Transfer Log")
        verbose_name_plural = _("Medicine Stock Transfer Logs")
        ordering = ["-transfer_date"]
        indexes = [
            models.Index(fields=["medicine_stock"]),
            models.Index(fields=["from_location", "to_location"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Transfer {self.medicine_stock} from {self.from_location} to {self.to_location} ({self.quantity_transferred})"

    def save(self, *args, **kwargs):
        # Auto-populate batch and expiry snapshot
        if self.medicine_stock:
            if not self.batch_number:
                self.batch_number = self.medicine_stock.batch_number
            if not self.expiry_date:
                self.expiry_date = self.medicine_stock.expiry_date

        # Compute total cost if applicable
        if self.unit_cost and self.quantity_transferred:
            self.total_cost = self.unit_cost * self.quantity_transferred

        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return self.expiry_date and self.expiry_date <= timezone.now().date()

    @classmethod
    def get_expiring_transfers(cls, within_days=30):
        """Get batches that are expiring within the given days"""
        threshold_date = timezone.now().date() + timedelta(days=within_days)
        return cls.objects.filter(expiry_date__lte=threshold_date)


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
