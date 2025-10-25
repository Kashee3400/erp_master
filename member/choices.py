from django.db import models


class RewardSource(models.TextChoices):
    """Enumerates possible ad networks or reward sources."""

    GOOGLE = "google", "Google AdMob"
    FACEBOOK = "facebook", "Facebook Audience Network"
    UNITY = "unity", "Unity Ads"
    OTHER = "other", "Other"


class TransactionType(models.TextChoices):
    CREDIT = "credit", "Credit (Earned)"
    DEBIT = "debit", "Debit (Withdrawal/Spend)"
    ADJUSTMENT = "adjustment", "Manual Adjustment"


class WithdrawalStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    COMPLETED = "completed", "Completed"
