# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models.case_models import (
    CaseEntry,
    CaseReceiverLog,
    CasePayment,
    PaymentStatusChoices,
)
from django.utils.translation import gettext_lazy as _
from facilitator.models.user_profile_model import UserLocation
from notifications.notification_service import NotificationServices

from django.core.mail import send_mail
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=CaseEntry)
def create_receiver_log_on_case_entry(sender, instance, created, **kwargs):
    """
    Create an initial CaseReceiverLog when a CaseEntry is created,
    and notify all users linked to the same MCC/MPP location.
    """
    if created and instance.created_by:
        CaseReceiverLog.objects.create(
            case_entry=instance,
            assigned_from=None,
            assigned_to=instance.created_by,
            remarks=_("Initial assignment on case creation."),
        )
        mcc_code = None

        if instance.cattle and instance.cattle.owner:
            mcc_code = instance.cattle.owner.mcc_code
        elif instance.non_member_cattle and instance.non_member_cattle.non_member:
            mcc_code = instance.non_member_cattle.non_member.mcc_code

        if mcc_code:
            users_in_same_mcc = (
                UserLocation.objects.filter(mcc_code=mcc_code)
                .select_related("user")
                .values_list("user", flat=True)
            )
            NotificationServices().create_bulk_notifications(
                template_name="case_entry_update_en",
                recipients=users_in_same_mcc,
                context_factory={
                    "case": instance,
                    "site_name": "Kashee Pasu Sewa",
                },
            )


@receiver(post_save, sender=CasePayment)
def update_case_payment_summary(sender, instance, created, **kwargs):
    """Update payment summary whenever a payment changes"""
    try:
        summary = instance.case_entry.payment_summary
        summary.refresh_summary()

        # Send notifications
        if created:
            notify_payment_created(instance)
        elif instance.payment_status == PaymentStatusChoices.COMPLETED:
            notify_payment_completed(instance)
        elif instance.payment_status == PaymentStatusChoices.FAILED:
            notify_payment_failed(instance)

    except Exception as e:
        logger.error(f"Error updating payment summary: {e}")


def notify_payment_created(payment):
    """Send notification when payment is created"""
    try:
        case = payment.case_entry
        user = case.created_by

        context = {
            "case_no": case.case_no,
            "amount": payment.amount,
            "payment_method": payment.get_payment_method_display(),
            "due_date": payment.due_date,
        }

        # Send email
        send_mail(
            subject=f"Payment Created for Case {case.case_no}",
            message=render_to_string("payment_created.txt", context),
            from_email="noreply@vetcare.com",
            recipient_list=[user.email],
            html_message=render_to_string("payment_created.html", context),
        )
    except Exception as e:
        logger.error(f"Error sending payment created notification: {e}")


def notify_payment_completed(payment):
    """Send notification when payment is completed"""
    try:
        case = payment.case_entry
        user = case.created_by

        context = {
            "case_no": case.case_no,
            "amount": payment.amount,
            "payment_date": payment.payment_date,
            "transaction_id": payment.transaction_id,
        }

        send_mail(
            subject=f"Payment Confirmed for Case {case.case_no}",
            message=render_to_string("payment_completed.txt", context),
            from_email="noreply@vetcare.com",
            recipient_list=[user.email],
            html_message=render_to_string("payment_completed.html", context),
        )
    except Exception as e:
        logger.error(f"Error sending payment completed notification: {e}")


def notify_payment_failed(payment):
    """Send notification when payment fails"""
    try:
        case = payment.case_entry
        user = case.created_by

        context = {
            "case_no": case.case_no,
            "amount": payment.amount,
            "retry_count": payment.retry_count,
        }

        send_mail(
            subject=f"Payment Failed for Case {case.case_no}",
            message=render_to_string("payment_failed.txt", context),
            from_email="noreply@vetcare.com",
            recipient_list=[user.email],
            html_message=render_to_string("payment_failed.html", context),
        )
    except Exception as e:
        logger.error(f"Error sending payment failed notification: {e}")
