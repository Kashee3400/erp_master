from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
import uuid
import hashlib
import logging
from veterinary.choices.choices import (
    PaymentMethodChoices,
    PaymentStatusChoices,
    PaymentTransactionTypeChoices,
)
from django.contrib.auth import get_user_model
from ulid import ULID

User = get_user_model()

logger = logging.getLogger(__name__)


class PaymentTransactionManager(models.Manager):
    """Custom manager for PaymentTransaction with useful query methods"""

    def pending_transactions(self):
        """Get all pending transactions"""
        return self.filter(status__in=["INITIATED", "PENDING"])

    def expired_transactions(self, hours=24):
        """Get transactions that should be marked as expired"""
        expiry_time = timezone.now() - timezone.timedelta(hours=hours)
        return self.filter(
            status__in=["INITIATED", "PENDING"], created_at__lt=expiry_time
        )

    def successful_transactions(self):
        """Get all successful transactions"""
        return self.filter(status="COMPLETED")

    def by_date_range(self, start_date, end_date):
        """Filter transactions by date range"""
        return self.filter(created_at__range=[start_date, end_date])

    def total_amount_by_status(self, status):
        """Calculate total amount for a specific status"""
        from django.db.models import Sum

        result = self.filter(status=status).aggregate(total=Sum("amount"))
        return result["total"] or Decimal("0.00")

    def for_object(self, obj):
        """Get all transactions for a specific object (Product, CaseEntry, etc.)"""
        content_type = ContentType.objects.get_for_model(obj.__class__)
        return self.filter(content_type=content_type, object_id=obj.id)

    def for_model(self, model_class):
        """Get all transactions for a specific model type"""
        content_type = ContentType.objects.get_for_model(model_class)
        return self.filter(content_type=content_type)


class PaymentTransaction(models.Model):
    """
    Production-ready payment transaction model with generic relations

    This model can be linked to any other model (Product, CaseEntry, Subscription, etc.)
    using Django's ContentType framework (Generic Foreign Key)
    """

    # Primary identifiers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant_order_id = models.CharField(
        max_length=255, unique=True, db_index=True, help_text="Unique merchant order ID"
    )
    phonepe_transaction_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text="PhonePe transaction ID",
    )

    # Generic Foreign Key - Links to ANY model (Product, CaseEntry, etc.)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="The model this transaction is related to (Product, CaseEntry, etc.)",
    )
    object_id = models.CharField(
        max_length=255, db_index=True, help_text="The ID of the related object"
    )
    content_object = GenericForeignKey("content_type", "object_id")

    # Transaction type for easier filtering
    transaction_type = models.CharField(
        max_length=30,
        choices=PaymentTransactionTypeChoices.choices,
        db_index=True,
        help_text="Type of transaction",
    )

    # User reference (add your user model reference)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    user_identifier = models.CharField(
        max_length=255, db_index=True, help_text="User ID or identifier for tracking"
    )

    # Amount details
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Transaction amount in INR"
    )
    currency = models.CharField(max_length=3, default="INR")

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=PaymentStatusChoices.choices,
        default=PaymentStatusChoices.INITIATED,
        db_index=True,
    )
    status_message = models.TextField(blank=True, help_text="Detailed status message")

    # Payment details
    payment_method_type = models.CharField(
        max_length=20, choices=PaymentMethodChoices.choices, null=True, blank=True
    )
    payment_method = models.JSONField(
        null=True, blank=True, help_text="Detailed payment method information"
    )

    # URLs
    redirect_url = models.URLField(help_text="Redirect URL after payment")
    callback_url = models.URLField(
        null=True, blank=True, help_text="Webhook callback URL"
    )

    # Metadata (flexible fields for additional data)
    udf1 = models.CharField(
        max_length=255, blank=True, help_text="User defined field 1"
    )
    udf2 = models.CharField(
        max_length=255, blank=True, help_text="User defined field 2"
    )
    udf3 = models.CharField(
        max_length=255, blank=True, help_text="User defined field 3"
    )
    metadata = models.JSONField(
        default=dict, blank=True, help_text="Additional metadata as key-value pairs"
    )

    # Response tracking
    webhook_response = models.JSONField(
        null=True, blank=True, help_text="Full webhook response from payment gateway"
    )
    gateway_response_code = models.CharField(max_length=50, blank=True)
    gateway_response_message = models.TextField(blank=True)

    # Retry and failure tracking
    retry_count = models.IntegerField(default=0, help_text="Number of retry attempts")
    max_retries = models.IntegerField(
        default=3, help_text="Maximum retry attempts allowed"
    )
    failure_reason = models.TextField(
        blank=True, help_text="Reason for payment failure"
    )

    # Refund tracking
    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Amount refunded",
    )
    refund_initiated_at = models.DateTimeField(null=True, blank=True)
    refund_completed_at = models.DateTimeField(null=True, blank=True)
    refund_reference_id = models.CharField(max_length=255, blank=True)

    # Security
    checksum = models.CharField(
        max_length=255, blank=True, help_text="Checksum for data integrity verification"
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(
        null=True, blank=True, help_text="Transaction expiry time"
    )
    completed_at = models.DateTimeField(null=True, blank=True)

    # Soft delete
    is_active = models.BooleanField(default=True, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = PaymentTransactionManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["merchant_order_id"]),
            models.Index(fields=["phonepe_transaction_id"]),
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["user_identifier", "status"]),
            models.Index(fields=["is_active", "status"]),
            models.Index(fields=["-created_at"]),
            models.Index(
                fields=["content_type", "object_id"]
            ),  # For generic relation queries
            models.Index(fields=["transaction_type", "status"]),
        ]
        verbose_name = "Payment Transaction"
        verbose_name_plural = "Payment Transactions"

    def __str__(self):
        return f"{self.merchant_order_id} - {self.get_transaction_type_display()} - {self.status} - ₹{self.amount}"

    def clean(self):
        """Validate model data"""
        if self.amount <= 0:
            raise ValidationError({"amount": "Amount must be greater than 0"})

        if self.refund_amount > self.amount:
            raise ValidationError(
                {"refund_amount": "Refund amount cannot exceed transaction amount"}
            )

    def save(self, *args, **kwargs):
        """Override save to set default values and generate checksum"""
        if not self.expires_at and self.status == PaymentStatusChoices.INITIATED:
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)

        if not self.checksum:
            self.checksum = self.generate_checksum()

        self.full_clean()
        super().save(*args, **kwargs)

    # Utility methods for Generic Relations

    def get_related_object(self):
        """Get the related object (Product, CaseEntry, etc.)"""
        return self.content_object

    def get_related_object_display(self):
        """Get display string for related object"""
        obj = self.get_related_object()
        if obj:
            return f"{self.content_type.model.title()} - {str(obj)}"
        return "No related object"

    @classmethod
    def create_for_object(
        cls, obj, amount, user_identifier, transaction_type, **kwargs
    ):
        """
        Factory method to create transaction for any object

        Usage:
            product = Product.objects.get(id=1)
            transaction = PaymentTransaction.create_for_object(
                obj=product,
                amount=999.99,
                user_identifier="user_123",
                transaction_type='PRODUCT_PURCHASE',
                redirect_url='https://example.com/success'
            )
        """
        content_type = ContentType.objects.get_for_model(obj.__class__)

        # Generate unique merchant order ID
        merchant_order_id = f"ORD-{ULID()}"
        return cls.objects.create(
            content_type=content_type,
            object_id=obj.pk,
            amount=amount,
            user_identifier=user_identifier,
            transaction_type=transaction_type,
            merchant_order_id=merchant_order_id,
            **kwargs,
        )

    # Existing utility methods

    def generate_checksum(self):
        """Generate checksum for data integrity"""
        data = f"{self.merchant_order_id}{self.amount}{self.user_identifier}"
        return hashlib.sha256(data.encode()).hexdigest()

    def verify_checksum(self):
        """Verify checksum integrity"""
        return self.checksum == self.generate_checksum()

    def mark_as_completed(self, phonepe_transaction_id=None, payment_method=None):
        """Mark transaction as completed"""
        self.status = PaymentStatusChoices.COMPLETED
        self.completed_at = timezone.now()
        self.verified_at = timezone.now()

        if phonepe_transaction_id:
            self.phonepe_transaction_id = phonepe_transaction_id

        if payment_method:
            self.payment_method = payment_method

        self.save(
            update_fields=[
                "status",
                "completed_at",
                "verified_at",
                "phonepe_transaction_id",
                "payment_method",
                "updated_at",
            ]
        )

        logger.info(f"Transaction {self.merchant_order_id} marked as completed")

        # Trigger post-payment actions
        self._trigger_post_payment_actions()

        return True

    def _trigger_post_payment_actions(self):
        """
        Trigger actions after successful payment
        Override this or use signals for custom logic
        """
        # Example: Update related object status
        related_obj = self.get_related_object()
        if related_obj and hasattr(related_obj, "mark_as_paid"):
            related_obj.mark_as_paid()

    def mark_as_failed(self, reason="", gateway_code="", gateway_message=""):
        """Mark transaction as failed"""
        self.status = PaymentStatusChoices.FAILED
        self.failure_reason = reason
        self.gateway_response_code = gateway_code
        self.gateway_response_message = gateway_message
        self.verified_at = timezone.now()

        self.save(
            update_fields=[
                "status",
                "failure_reason",
                "gateway_response_code",
                "gateway_response_message",
                "verified_at",
                "updated_at",
            ]
        )

        logger.warning(
            f"Transaction {self.merchant_order_id} marked as failed: {reason}"
        )
        return True

    def mark_as_expired(self):
        """Mark transaction as expired"""
        if self.status in [
            PaymentStatusChoices.INITIATED,
            PaymentStatusChoices.PENDING,
        ]:
            self.status = PaymentStatusChoices.EXPIRED
            self.save(update_fields=["status", "updated_at"])
            logger.info(f"Transaction {self.merchant_order_id} marked as expired")
            return True
        return False

    def can_retry(self):
        """Check if transaction can be retried"""
        return (
            self.status == PaymentStatusChoices.FAILED
            and self.retry_count < self.max_retries
        )

    def increment_retry(self):
        """Increment retry count"""
        if self.can_retry():
            self.retry_count += 1
            self.status = PaymentStatusChoices.INITIATED
            self.save(update_fields=["retry_count", "status", "updated_at"])
            logger.info(
                f"Transaction {self.merchant_order_id} retry count: {self.retry_count}"
            )
            return True
        return False

    def is_expired(self):
        """Check if transaction is expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def initiate_refund(self, amount=None):
        """Initiate refund process"""
        if self.status != PaymentStatusChoices.COMPLETED:
            raise ValidationError("Can only refund completed transactions")

        refund_amt = amount or self.amount

        if refund_amt > (self.amount - self.refund_amount):
            raise ValidationError("Refund amount exceeds available amount")

        self.refund_amount += refund_amt
        self.refund_initiated_at = timezone.now()

        if self.refund_amount >= self.amount:
            self.status = PaymentStatusChoices.REFUNDED
        else:
            self.status = PaymentStatusChoices.PARTIALLY_REFUNDED

        self.save(
            update_fields=[
                "refund_amount",
                "refund_initiated_at",
                "status",
                "updated_at",
            ]
        )

        logger.info(f"Refund initiated for {self.merchant_order_id}: ₹{refund_amt}")
        return True

    def complete_refund(self, refund_reference_id):
        """Complete refund process"""
        self.refund_completed_at = timezone.now()
        self.refund_reference_id = refund_reference_id
        self.save(
            update_fields=["refund_completed_at", "refund_reference_id", "updated_at"]
        )

        logger.info(f"Refund completed for {self.merchant_order_id}")
        return True

    def soft_delete(self):
        """Soft delete the transaction"""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_active", "deleted_at", "updated_at"])

    def update_webhook_response(self, response_data):
        """Update webhook response data"""
        self.webhook_response = response_data
        self.verified_at = timezone.now()
        self.save(update_fields=["webhook_response", "verified_at", "updated_at"])

    def get_status_display_verbose(self):
        """Get verbose status display with additional context"""
        status_messages = {
            PaymentStatusChoices.INITIATED: "🔵 Payment initiated",
            PaymentStatusChoices.PENDING: "🟡 Payment pending",
            PaymentStatusChoices.COMPLETED: "✅ Payment successful",
            PaymentStatusChoices.FAILED: "❌ Payment failed",
            PaymentStatusChoices.EXPIRED: "⏰ Payment expired",
            PaymentStatusChoices.REFUNDED: "↩️ Amount refunded",
            PaymentStatusChoices.PARTIALLY_REFUNDED: "↩️ Partially refunded",
        }
        return status_messages.get(self.status, self.get_status_display())

    def to_dict(self):
        """Convert transaction to dictionary"""
        return {
            "id": str(self.id),
            "merchant_order_id": self.merchant_order_id,
            "phonepe_transaction_id": self.phonepe_transaction_id,
            "amount": str(self.amount),
            "currency": self.currency,
            "status": self.status,
            "transaction_type": self.transaction_type,
            "related_object": self.get_related_object_display(),
            "payment_method_type": self.payment_method_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
        }

    @property
    def is_successful(self):
        """Check if transaction is successful"""
        return self.status == PaymentStatusChoices.COMPLETED

    @property
    def is_pending(self):
        """Check if transaction is pending"""
        return self.status in [
            PaymentStatusChoices.INITIATED,
            PaymentStatusChoices.PENDING,
        ]

    @property
    def time_since_creation(self):
        """Get time since creation"""
        return timezone.now() - self.created_at

    @property
    def remaining_refund_amount(self):
        """Get remaining amount that can be refunded"""
        return self.amount - self.refund_amount
