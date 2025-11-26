# tasks.py (for Celery background tasks)

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

from .models.excel_model import ExcelUploadSession
from .utils.exce_util import process_import_enhanced
from .utils.inventory_utils import get_inventory_alerts
from django.core.management import call_command
from .models.case_models import (
    CasePayment,
    PaymentStatusChoices,
)
from django.utils import timezone

import os, logging

logger = logging.getLogger(__name__)


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
    from .models.stock_models import MedicineStock

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


@shared_task()
def process_excel_import(session_id, temp_file_path, selected_sheets, target_model):
    session = None
    try:
        session = ExcelUploadSession.objects.get(id=session_id)
        session.status = ExcelUploadSession.Status.PROCESSING
        session.save(update_fields=["status"])
        results = process_import_enhanced(temp_file_path, selected_sheets, target_model)
        has_errors = any(
            sheet_result.get("errors") for sheet_result in results.values()
        )
        if has_errors:
            session.status = ExcelUploadSession.Status.FAILED
            session.error_message = str(results)
            session.results = results
            session.processed = False
        else:
            session.status = ExcelUploadSession.Status.SUCCESS
            session.results = results
            session.processed = True

        session.save()
        try:
            os.remove(temp_file_path)
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")

        return results

    except Exception as e:
        logger.error(f"Excel import task failed: {e}", exc_info=True)
        if session:
            session.status = ExcelUploadSession.Status.FAILED
            session.error_message = str(e)
            session.save()
        raise


@shared_task(bind=True, max_retries=3)
def process_member_sync_notifications(self):
    """
    Celery task to process MPP collection notifications.
    Runs the management command to create and send notifications.
    """
    try:
        logger.info("Starting MPP collection notification processing...")
        call_command("sync_member_master")
        logger.info("MPP collection notification processing completed successfully.")
        return "Success"
    except Exception as exc:
        logger.error(f"Error processing MPP collection notifications: {exc}")
        # Retry after 5 minutes if failed
        raise self.retry(exc=exc, countdown=300)


@shared_task
def check_overdue_payments():
    """
    Check for overdue payments and send reminders
    Run this daily using celery beat
    """
    try:
        overdue_payments = CasePayment.objects.filter(
            status=PaymentStatusChoices.PENDING, due_date__lt=timezone.now().date()
        )

        for payment in overdue_payments:
            send_overdue_reminder.delay(payment.id)

        return f"Checked {overdue_payments.count()} overdue payments"
    except Exception as e:
        logger.error(f"Error checking overdue payments: {e}")


@shared_task
def send_overdue_reminder(payment_id):
    """Send reminder for overdue payment"""
    try:
        payment = CasePayment.objects.get(id=payment_id)

        if payment.is_overdue():
            case = payment.case_entry
            user = case.created_by

            context = {
                "case_no": case.case_no,
                "amount_due": case.payment_summary.amount_due,
                "due_date": payment.due_date,
                "days_overdue": (timezone.now().date() - payment.due_date).days,
            }

            from django.core.mail import send_mail
            from django.template.loader import render_to_string

            send_mail(
                subject=f"⚠️ Payment Overdue for Case {case.case_no}",
                message=render_to_string("payment_overdue.txt", context),
                from_email="noreply@vetcare.com",
                recipient_list=[user.email],
                html_message=render_to_string("payment_overdue.html", context),
            )
    except Exception as e:
        logger.error(f"Error sending overdue reminder: {e}")


@shared_task
def retry_failed_payments():
    """
    Auto-retry failed payments (only for online methods with retries < 3)
    Run this periodically using celery beat
    """
    try:
        failed_payments = CasePayment.objects.filter(
            status=PaymentStatusChoices.FAILED,
            retry_count__lt=3,
            last_retry_at__isnull=True,  # Not yet retried
        )

        for payment in failed_payments[:10]:  # Process 10 at a time
            retry_payment_task.delay(payment.id)

        return f"Scheduled {failed_payments.count()} payments for retry"
    except Exception as e:
        logger.error(f"Error retrying failed payments: {e}")

# TODO:process_payment_with_gateway(payment)
@shared_task
def retry_payment_task(payment_id):
    """Retry a specific failed payment"""
    try:
        payment = CasePayment.objects.get(id=payment_id)

        if payment.payment_status == PaymentStatusChoices.FAILED:
            payment.payment_status = PaymentStatusChoices.PROCESSING
            payment.retry_count += 1
            payment.last_retry_at = timezone.now()
            payment.save()

            # Call your payment gateway integration here
            # process_payment_with_gateway(payment)

    except Exception as e:
        logger.error(f"Error retrying payment {payment_id}: {e}")
