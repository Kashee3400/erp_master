from django.utils.translation import gettext_lazy as _
from ..choices.choices import *
from django.db import models
from django.conf import settings
from .common_models import BaseModel, User
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, F
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from decimal import Decimal



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
        max_length=100, help_text=_("Name of the medicine"), verbose_name=_("Medicine"),db_index=True
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


from django.db import models, transaction
from django.db.models import F, ExpressionWrapper, DecimalField, Q
from .managers.medicine_stock_manager import (
    MedicineStockManager,
    UserMedicineStockManager,
    ActiveUserMedicineStockManager,
    OptimizedUserMedicineStockManager,
    PendingApprovalManager,
    RejectedStockManager,
)
# -----------------------------
# MedicineStock Model
# -----------------------------
class MedicineStock(BaseModel):
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="location_stocks",
        help_text="Location where this stock is held",
        verbose_name="Location",
        blank=True,
        null=True,
    )
    medicine = models.ForeignKey(
        "Medicine",
        on_delete=models.CASCADE,
        related_name="stocks",
        help_text="Medicine item in stock",
    )
    total_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(0)],
        help_text="Total stock for this batch",
    )
    reserved_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(0)],
        help_text="Quantity reserved/allocated to users",
    )
    batch_number = models.CharField(max_length=50, blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    objects = MedicineStockManager()

    # -----------------------------
    # Properties
    # -----------------------------
    @property
    def available_quantity(self):
        return max(self.total_quantity - self.reserved_quantity, Decimal("0.00"))

    def __str__(self):
        return (
            f"{self.medicine.medicine} - {self.available_quantity} "
            f"{self.medicine.category.unit_of_quantity} "
            f"(Batch: {self.batch_number or 'N/A'})"
        )

    # -----------------------------
    # Business Methods
    # -----------------------------
    @transaction.atomic
    def add_stock(self, amount: Decimal):
        """Increase stock (new supply arrival)."""
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        self.total_quantity = F("total_quantity") + amount
        self.save(update_fields=["total_quantity", "last_updated"])
        self.refresh_from_db()

    @transaction.atomic
    def reserve_stock(self, amount: Decimal):
        """Reserve stock for an order or allocation."""
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        if amount > self.available_quantity:
            raise ValueError("Not enough available stock to reserve.")
        self.reserved_quantity = F("reserved_quantity") + amount
        self.save(update_fields=["reserved_quantity", "last_updated"])
        self.refresh_from_db()

    @transaction.atomic
    def release_reserved(self, amount: Decimal):
        """Release reserved stock (e.g., cancelled order)."""
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        if amount > self.reserved_quantity:
            raise ValueError("Cannot release more than reserved quantity.")
        self.reserved_quantity = F("reserved_quantity") - amount
        self.save(update_fields=["reserved_quantity", "last_updated"])
        self.refresh_from_db()

    @transaction.atomic
    def consume_stock(self, amount: Decimal):
        """Consume reserved stock (e.g., dispensed to patient)."""
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        if amount > self.reserved_quantity:
            raise ValueError("Cannot consume more than reserved quantity.")
        self.total_quantity = F("total_quantity") - amount
        self.reserved_quantity = F("reserved_quantity") - amount
        self.save(update_fields=["total_quantity", "reserved_quantity", "last_updated"])
        self.refresh_from_db()

    @transaction.atomic
    def transfer_to(self, target_location, amount: Decimal):
        """Transfer stock from current location to another."""
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        if amount > self.available_quantity:
            raise ValueError("Not enough available stock to transfer.")

        # Reduce from current location
        self.total_quantity = F("total_quantity") - amount
        self.save(update_fields=["total_quantity", "last_updated"])
        self.refresh_from_db()

        # Add to target location
        target_stock, _ = MedicineStock.objects.get_or_create(
            medicine=self.medicine,
            batch_number=self.batch_number,
            location=target_location,
            defaults={"expiry_date": self.expiry_date, "total_quantity": Decimal("0.00")},
        )
        target_stock.add_stock(amount)

    # -----------------------------
    # Meta
    # -----------------------------
    class Meta:
        db_table = "tbl_medicine_stock"
        verbose_name = "Medicine Stock"
        verbose_name_plural = "Medicine Stock"
        ordering = ["-last_updated"]
        indexes = [
            models.Index(fields=["medicine"]),
            models.Index(fields=["batch_number"]),
            models.Index(fields=["expiry_date"]),
            models.Index(fields=["location"]),
        ]
        unique_together = ("medicine", "batch_number", "location")

class UserMedicineStock(BaseModel):
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
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
    allocated_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(0)],
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
    used_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(0)],
        help_text="Quantity already used by the user",
    )
    min_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(0)],
        help_text="Critical threshold value for reminder when stock is very low",
    )
    threshold_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(0)],
        help_text="Warning threshold to trigger refill reminder",
    )
    sync_status = models.CharField(
        max_length=20,
        choices=SyncStatusChoices.choices,
        default=SyncStatusChoices.PENDING,
        help_text="Sync status for offline/online data sync",
    )

    allocated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_allocations_made",
        help_text="User who made the allocation (admin or supervisor)",
    )
    approval_status = models.CharField(
        max_length=20,
        choices=ApprovalStatusChoices.choices,
        default=ApprovalStatusChoices.PENDING,
        help_text="Approval status by reporting head"
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_stock_allocations",
        help_text="Reporting head who approved/rejected the allocation"
    )
    approval_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date when the allocation was approved/rejected"
    )
    rejection_reason = models.TextField(
        blank=True,
        null=True,
        help_text="Reason for rejection (if applicable)"
    )


    objects = UserMedicineStockManager()    
    active = ActiveUserMedicineStockManager()
    optimized = OptimizedUserMedicineStockManager()
    pending_approval = PendingApprovalManager()
    rejected = RejectedStockManager()
    
    def approve(self, approved_by_user, approval_date=None):
        """Approve the stock allocation"""
        self.approval_status = ApprovalStatusChoices.APPROVED
        self.approved_by = approved_by_user
        self.approval_date = approval_date or timezone.now()
        self.save()

    def reject(self, rejected_by_user, reason="", rejection_date=None):
        """Reject the stock allocation"""
        self.approval_status = ApprovalStatusChoices.REJECTED
        self.approved_by = rejected_by_user
        self.approval_date = rejection_date or timezone.now()
        self.rejection_reason = reason
        self.save()

    def is_approved(self):
        return self.approval_status == ApprovalStatusChoices.APPROVED

    def is_pending_approval(self):
        return self.approval_status == ApprovalStatusChoices.PENDING


    # --- Business logic helpers ---
    def remaining_quantity(self):
        return self.allocated_quantity - self.used_quantity

    def remaining_quantity(self):
        if not self.is_approved():
            return Decimal("0.00")  # No remaining quantity if not approved
        return self.allocated_quantity - self.used_quantity

    def is_below_threshold(self):
        return self.remaining_quantity() <= self.min_threshold

    def stock_status(self):
        """Return stock status: OK / Warning / Critical"""
        remaining = self.remaining_quantity()
        if remaining <= self.min_threshold:
            return "Critical"
        elif remaining <= self.threshold_quantity:
            return "Warning"
        return "OK"

    # --- Validation ---
    def clean(self):
        if self.used_quantity > self.allocated_quantity:
            raise ValidationError("Used quantity cannot exceed allocated quantity.")

    def __str__(self):
        user_name = getattr(self.user, "username", "Unknown User")
        med_name = (
            getattr(self.medicine_stock.medicine, "medicine", "Unknown Medicine")
            if self.medicine_stock and self.medicine_stock.medicine
            else "Unknown Medicine"
        )
        return f"{user_name} - {med_name} - {self.allocated_quantity}"

    class Meta:
        db_table = "tbl_user_medicine_stock"
        verbose_name = "User Medicine Allocation"
        verbose_name_plural = "User Medicine Allocations"
        ordering = ["-allocation_date"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["medicine_stock"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(used_quantity__lte=F("allocated_quantity")),
                name="used_lte_allocated",
            )
        ]


class UserMedicineTransaction(models.Model):
    """
    Tracks all allocation, usage, and return transactions
    against a user's allocated medicine stock.
    """

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
        help_text="Allocated, Used, or Returned",
    )

    quantity = models.FloatField(
        help_text="Quantity involved in this transaction (e.g., 10 tablets, 5 ml)",
    )

    running_balance = models.FloatField(
        help_text="Remaining stock balance for this user after this transaction",
        default=0.0, validators=[MinValueValidator(0)],verbose_name="Running Balance"
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="user_medicine_transactions",
        help_text="User who performed this transaction",
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When this transaction occurred",
    )

    note = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "tbl_user_medicine_stock_transaction"
        verbose_name = "User Medicine Transaction"
        verbose_name_plural = "User Medicine Transactions"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user_medicine_stock"]),
            models.Index(fields=["action"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"{self.user_medicine_stock.user.username} - {self.get_action_display()} ({self.quantity})"

    def save(self, *args, **kwargs):
        """
        Auto-update the running balance at save time.
        """
        if not self.pk:  # only on create
            last_txn = (
                UserMedicineTransaction.objects.filter(
                    user_medicine_stock=self.user_medicine_stock
                )
                .order_by("-timestamp")
                .first()
            )
            last_balance = last_txn.running_balance if last_txn else 0

            if self.action == ActionTypeChoices.ALLOCATED:
                self.running_balance = last_balance + self.quantity
            elif self.action == ActionTypeChoices.USED:
                self.running_balance = last_balance - self.quantity
            elif self.action == ActionTypeChoices.RETURNED:
                self.running_balance = last_balance + self.quantity

        super().save(*args, **kwargs)


class MedicineStockAudit(models.Model):
    """
    Immutable audit log of all stock changes at the global (warehouse/pharmacy) level.
    """

    medicine = models.ForeignKey(
        "Medicine",
        on_delete=models.CASCADE,
        related_name="audit_logs",
    )

    transaction_type = models.CharField(
        max_length=10,
        choices=TransactionTypeChoices.choices,
    )

    quantity = models.FloatField(help_text="Quantity added/removed")

    balance_after = models.FloatField(
        help_text="Stock balance after this transaction",
        default=0.0,
        verbose_name="Balance After Transaction",
        validators=[MinValueValidator(0)]
    )

    description = models.TextField(blank=True, null=True)

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

    def save(self, *args, **kwargs):
        if not self.pk:  # only on create
            last_log = (
                MedicineStockAudit.objects.filter(medicine=self.medicine)
                .order_by("-created_at")
                .first()
            )
            last_balance = last_log.balance_after if last_log else 0

            if self.transaction_type == TransactionTypeChoices.INWARD:
                self.balance_after = last_balance + self.quantity
            else:
                self.balance_after = last_balance - self.quantity

        super().save(*args, **kwargs)


class MedicineStockTransferLog(models.Model):
    """
    Tracks movement of medicine stock between locations (warehouse/pharmacy/user).
    """

    from_location = models.ForeignKey(
        "Location",
        on_delete=models.CASCADE,
        related_name="outgoing_transfers",
    )
    to_location = models.ForeignKey(
        "Location",
        on_delete=models.CASCADE,
        related_name="incoming_transfers",
    )

    medicine_stock = models.ForeignKey(
        "MedicineStock",
        on_delete=models.CASCADE,
    )

    quantity_transferred = models.FloatField()

    transfer_type = models.CharField(
        max_length=10,
        choices=TransferTypeChoices.choices,
        default=TransferTypeChoices.OUTWARD,
    )

    status = models.CharField(
        max_length=20,
        choices=TransferStatusChoices.choices,
        default=TransferStatusChoices.PENDING,
    )

    batch_number = models.CharField(max_length=50, blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)

    transferred_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medicine_transfers_made",
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medicine_transfers_received",
    )

    transfer_date = models.DateTimeField(auto_now_add=True)
    received_at = models.DateTimeField(blank=True, null=True)

    remarks = models.TextField(blank=True, null=True)

    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = "tbl_medicine_stock_transfer_log"
        verbose_name = "Medicine Stock Transfer Log"
        verbose_name_plural = "Medicine Stock Transfer Logs"
        ordering = ["-transfer_date"]
        indexes = [
            models.Index(fields=["medicine_stock"]),
            models.Index(fields=["from_location", "to_location"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Transfer {self.medicine_stock} from {self.from_location} to {self.to_location} ({self.quantity_transferred})"

    def save(self, *args, **kwargs):
        if not self.batch_number and self.medicine_stock:
            self.batch_number = self.medicine_stock.batch_number
        if not self.expiry_date and self.medicine_stock:
            self.expiry_date = self.medicine_stock.expiry_date
        if self.unit_cost and self.quantity_transferred:
            self.total_cost = self.unit_cost * self.quantity_transferred

        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return self.expiry_date and self.expiry_date <= timezone.now().date()

    @classmethod
    def get_expiring_transfers(cls, within_days=30):
        threshold_date = timezone.now().date() + timedelta(days=within_days)
        return cls.objects.filter(expiry_date__lte=threshold_date)


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


