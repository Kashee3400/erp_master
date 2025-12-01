# Signal handlers (optional - create in signals.py)
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models.transaction_model import PaymentTransaction
import logging

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=PaymentTransaction)
def check_expiry_before_save(sender, instance, **kwargs):
    """Check and mark transaction as expired before saving"""
    if instance.is_expired() and instance.status in ["INITIATED", "PENDING"]:
        instance.status = "EXPIRED"
        logger.info(f"Auto-expired transaction: {instance.merchant_order_id}")


@receiver(post_save, sender=PaymentTransaction)
def log_status_change(sender, instance, created, **kwargs):
    """Log status changes"""
    if not created:
        logger.info(
            f"Transaction {instance.merchant_order_id} updated: "
            f"Status={instance.status}, Amount=₹{instance.amount}, "
            f"Related to: {instance.get_related_object_display()}"
        )
