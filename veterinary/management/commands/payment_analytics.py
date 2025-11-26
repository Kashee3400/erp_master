# management/commands/payment_analytics.py

from django.core.management.base import BaseCommand
from django.db.models import Sum
from datetime import datetime, timedelta
from ...models.case_models import (
    CasePayment,
    CasePaymentSummary,
    PaymentStatusChoices,
    CasePaymentStatusChoices,
)


class Command(BaseCommand):
    help = "Generate payment analytics and reports"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days", type=int, default=30, help="Number of days to analyze"
        )

    def handle(self, *args, **options):
        days = options["days"]
        start_date = datetime.now() - timedelta(days=days)

        # Payment stats
        total_cases = CasePaymentSummary.objects.count()
        paid_cases = CasePaymentSummary.objects.filter(
            payment_status=CasePaymentStatusChoices.PAID
        ).count()
        unpaid_cases = CasePaymentSummary.objects.filter(
            payment_status=CasePaymentStatusChoices.UNPAID
        ).count()
        overdue_cases = CasePaymentSummary.objects.filter(is_overdue=True).count()

        # Financial stats
        stats = CasePaymentSummary.objects.aggregate(
            total_amount=Sum("total_amount"),
            amount_paid=Sum("amount_paid"),
            amount_due=Sum("amount_due"),
        )

        # Failed payments
        failed_payments = CasePayment.objects.filter(
            status=PaymentStatusChoices.FAILED, created_at__gte=start_date
        ).count()

        report = f"""
        === Payment Analytics Report ({days} days) ===
        
        Case Statistics:
        - Total Cases: {total_cases}
        - Fully Paid: {paid_cases} ({paid_cases/total_cases*100:.1f}%)
        - Unpaid: {unpaid_cases} ({unpaid_cases/total_cases*100:.1f}%)
        - Overdue: {overdue_cases}
        
        Financial Summary:
        - Total Amount: ₹{stats['total_amount'] or 0}
        - Amount Paid: ₹{stats['amount_paid'] or 0}
        - Amount Due: ₹{stats['amount_due'] or 0}
        
        Issues:
        - Failed Payments: {failed_payments}
        """

        self.stdout.write(self.style.SUCCESS(report))
