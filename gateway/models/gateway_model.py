# models.py
from django.db import models
from django.contrib.auth.models import User


class PaymentTransaction(models.Model):
    """Model to store payment transactions"""

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("REFUNDED", "Refunded"),
        ("CANCELLED", "Cancelled"),
    ]

    # Transaction details
    merchant_order_id = models.CharField(max_length=255, unique=True, db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    # User information (optional, if you have user authentication)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    # PhonePe response data
    phonepe_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    payment_instrument = models.CharField(max_length=100, blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Additional info
    redirect_url = models.URLField(max_length=500)
    checkout_url = models.URLField(max_length=500, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    raw_response = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "payment_transactions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["merchant_order_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.merchant_order_id} - {self.amount} - {self.status}"


class RefundTransaction(models.Model):
    """Model to store refund transactions"""

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]

    # Refund details
    merchant_refund_id = models.CharField(max_length=255, unique=True, db_index=True)
    original_transaction = models.ForeignKey(
        PaymentTransaction, on_delete=models.CASCADE, related_name="refunds"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    # PhonePe response data
    phonepe_refund_id = models.CharField(max_length=255, blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Additional info
    error_message = models.TextField(blank=True, null=True)
    raw_response = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "refund_transactions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["merchant_refund_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.merchant_refund_id} - {self.amount} - {self.status}"


class SDKOrder(models.Model):
    """Model to store SDK orders for in-app payments"""

    merchant_order_id = models.CharField(max_length=255, unique=True, db_index=True)
    token = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    # User information
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    # Metadata
    udf1 = models.CharField(max_length=255, blank=True, null=True)
    udf2 = models.CharField(max_length=255, blank=True, null=True)
    udf3 = models.CharField(max_length=255, blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "sdk_orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.merchant_order_id} - {self.amount}"
