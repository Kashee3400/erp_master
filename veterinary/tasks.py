# tasks.py (for Celery background tasks)

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .utils.inventory_utils import get_inventory_alerts, calculate_stock_metrics


@shared_task
def send_daily_inventory_report():
    """
    Send daily inventory report with alerts
    """
    alerts = get_inventory_alerts()

    # Filter critical and expired alerts
    critical_alerts = [
        alert for alert in alerts if alert["severity"] in ["critical", "expired"]
    ]

    if critical_alerts:
        subject = (
            f"Critical Inventory Alerts - {len(critical_alerts)} items need attention"
        )
        message = "Critical inventory alerts:\n\n"

        for alert in critical_alerts:
            message += f"- {alert['message']}\n"

        # Send to inventory managers
        recipient_list = settings.INVENTORY_MANAGERS_EMAIL

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )

    return f"Sent report with {len(critical_alerts)} critical alerts"


@shared_task
def check_expiring_medicines():
    """
    Check for medicines expiring in next 7 days
    """
    from django.utils import timezone
    from datetime import timedelta
    from .models import MedicineStock

    future_date = timezone.now().date() + timedelta(days=7)

    expiring_stocks = MedicineStock.objects.filter(
        expiry_date__lte=future_date, expiry_date__gte=timezone.now().date()
    ).select_related("medicine", "medicine__category")

    if expiring_stocks.exists():
        subject = f"Medicines Expiring Soon - {expiring_stocks.count()} items"
        message = "The following medicines are expiring within 7 days:\n\n"

        for stock in expiring_stocks:
            days_remaining = (stock.expiry_date - timezone.now().date()).days
            message += (
                f"- {stock.medicine.medicine} ({stock.medicine.strength})\n"
                f"  Batch: {stock.batch_number}, Quantity: {stock.total_quantity} "
                f"{stock.medicine.category.unit_of_quantity}\n"
                f"  Expires in: {days_remaining} days\n\n"
            )

        recipient_list = settings.INVENTORY_MANAGERS_EMAIL

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )

    return f"Checked {expiring_stocks.count()} expiring medicines"
