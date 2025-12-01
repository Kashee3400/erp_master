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


class MemberStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    PENDING_VERIFICATION = "PENDING_VERIFICATION", "Pending Verification"
    ACTIVE = "ACTIVE", "Active"
    REJECTED = "REJECTED", "Rejected"
    SUSPENDED = "SUSPENDED", "Suspended"
    CLOSED = "CLOSED", "Closed"


class RelationType(models.TextChoices):
    HUSBAND = "HUSBAND", "Husband"
    WIFE = "WIFE", "Wife"
    SON = "SON", "Son"
    DAUGHTER = "DAUGHTER", "Daughter"
    FATHER = "FATHER", "Father"
    MOTHER = "MOTHER", "Mother"
    BROTHER = "BROTHER", "Brother"
    SISTER = "SISTER", "Sister"
    GRANDFATHER = "GRANDFATHER", "Grandfather"
    GRANDMOTHER = "GRANDMOTHER", "Grandmother"
    OTHER = "OTHER", "Other"


class GenderChoices(models.TextChoices):
    MALE = "MALE", "Male"
    FEMALE = "FEMALE", "Female"
    OTHER = "OTHER", "Other"


class SessionStatus(models.TextChoices):
    INITIATED = "INITIATED", "Initiated"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    COMPLETED = "COMPLETED", "Completed"
    SUBMITTED = "SUBMITTED", "Submitted for Verification"
    ABANDONED = "ABANDONED", "Abandoned"


class DocumentType(models.TextChoices):
    PROFILE_PHOTO = "PROFILE_PHOTO", "Farmer Profile Photo"
    AADHAAR_FRONT = "AADHAAR_FRONT", "Aadhaar Front"
    AADHAAR_BACK = "AADHAAR_BACK", "Aadhaar Back"
    BANK_PASSBOOK = "BANK_PASSBOOK", "Bank Passbook Front"
    AADHAAR_QR_DATA = "AADHAAR_QR_DATA", "Aadhaar QR Scan Data"
    PAN_CARD = "PAN_CARD", "PAN Card"
    RATION_CARD = "RATION_CARD", "Ration Card"
    OTHER = "OTHER", "Other Document"


class VerificationStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    VERIFIED = "VERIFIED", "Verified"
    REJECTED = "REJECTED", "Rejected"


class UploadStatus(models.TextChoices):
    PENDING_UPLOAD = "PENDING_UPLOAD", "Pending Upload"
    UPLOADED = "UPLOADED", "Uploaded"
    SYNCED_TO_CLOUD = "SYNCED_TO_CLOUD", "Synced to Cloud"
    FAILED = "FAILED", "Failed"


class SyncStatus(models.TextChoices):
    LOCAL_ONLY = "LOCAL_ONLY", "Local Only"
    SYNC_PENDING = "SYNC_PENDING", "Sync Pending"
    SYNCED = "SYNCED", "Synced"
    SYNC_FAILED = "SYNC_FAILED", "Sync Failed"
    CONFLICT = "CONFLICT", "Sync Conflict"


class AnimalCategory(models.TextChoices):
    INDIGENOUS_COW = "INDIGENOUS_COW", "Indigenous/Desi Cow"
    CROSSBRED_COW = "CROSSBRED_COW", "Crossbred/Mix Cow"
    BUFFALO = "BUFFALO", "Buffalo"
