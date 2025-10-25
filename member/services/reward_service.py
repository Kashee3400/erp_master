from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from ..models import (
    RewardedAdTransaction,
    RewardLedger,
    models,
    RewardWithdrawalRequest,
    TransactionType,
    WithdrawalStatus,
)


class RewardService:
    """
    Central service for managing user reward operations.
    Ensures transactional consistency and audit traceability.
    """

    @staticmethod
    @transaction.atomic
    def credit_reward_from_ad(user, ad_transaction: RewardedAdTransaction):
        """
        Credits a verified ad reward to the user's ledger.
        Prevents double-crediting of the same ad reward.
        """
        if not ad_transaction.is_verified:
            raise ValidationError("Cannot credit unverified ad reward.")

        existing_entry = RewardLedger.objects.filter(source_ad=ad_transaction).first()
        if existing_entry:
            return existing_entry  # Already credited safely

        entry = RewardLedger.credit_user(
            user=user,
            amount=ad_transaction.reward_amount,
            description=f"Ad Reward from {ad_transaction.reward_source}",
            source_ad=ad_transaction,
        )
        return entry

    @staticmethod
    @transaction.atomic
    def request_withdrawal(user, amount: Decimal) -> RewardWithdrawalRequest:
        """
        Creates a withdrawal request if sufficient balance is available.
        """
        current_balance = RewardLedger.get_user_balance(user)
        if amount > current_balance:
            raise ValidationError("Insufficient balance for withdrawal request.")

        withdrawal = RewardWithdrawalRequest.objects.create(
            user=user,
            amount=amount,
            status=WithdrawalStatus.PENDING,
        )
        return withdrawal

    @staticmethod
    @transaction.atomic
    def approve_withdrawal(request: RewardWithdrawalRequest, reference_id: str):
        """
        Approves and finalizes a withdrawal request.
        Deducts balance and records the transaction.
        """
        if request.status != WithdrawalStatus.PENDING:
            raise ValidationError("Withdrawal request already processed.")

        RewardLedger.debit_user(
            user=request.user,
            amount=request.amount,
            description=f"Withdrawal Approved (Ref: {reference_id})",
        )

        request.status = WithdrawalStatus.APPROVED
        request.transaction_reference = reference_id
        request.processed_at = timezone.now()
        request.save(update_fields=["status", "transaction_reference", "processed_at"])

        return request

    @staticmethod
    @transaction.atomic
    def reject_withdrawal(request: RewardWithdrawalRequest, remarks: str = ""):
        """
        Rejects a pending withdrawal request and adds remarks.
        """
        if request.status != WithdrawalStatus.PENDING:
            raise ValidationError("Withdrawal already processed.")

        request.status = WithdrawalStatus.REJECTED
        request.remarks = remarks or "Rejected by admin"
        request.processed_at = timezone.now()
        request.save(update_fields=["status", "remarks", "processed_at"])
        return request

    @staticmethod
    def get_user_summary(user) -> dict:
        """
        Returns a summary snapshot for user dashboard.
        """
        total_earned = RewardLedger.objects.filter(
            user=user, transaction_type=TransactionType.CREDIT
        ).aggregate(total=models.Sum("amount"))["total"] or Decimal("0.00")

        total_withdrawn = RewardLedger.objects.filter(
            user=user, transaction_type=TransactionType.DEBIT
        ).aggregate(total=models.Sum("amount"))["total"] or Decimal("0.00")

        balance = RewardLedger.get_user_balance(user)

        return {
            "user": user.username,
            "total_earned": total_earned,
            "total_withdrawn": total_withdrawn,
            "balance": balance,
        }
