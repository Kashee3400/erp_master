import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class PaymentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SUCCESS = "SUCCESS", "Success"
    FAILED = "FAILED", "Failed"
    CANCELLED = "CANCELLED", "Cancelled"


class PaymentOrder(models.Model):
    """
    Your business order mapped to a PhonePe merchantTransactionId.
    You can also link to your own CaseEntry / Invoice models.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant_transaction_id = models.CharField(
        max_length=64, unique=True, db_index=True
    )
    merchant_user_id = models.CharField(max_length=64)
    amount_paise = models.PositiveIntegerField()
    status = models.CharField(
        max_length=16,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
    )
    phonepe_transaction_id = models.CharField(max_length=64, null=True, blank=True)
    raw_response = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Optional: link to your own user/case models
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="phonepe_orders",
    )
    # case = models.ForeignKey("veterinary.CaseEntry", ...)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.merchant_transaction_id} ({self.status})"
