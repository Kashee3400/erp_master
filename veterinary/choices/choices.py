from django.db import models
from django.utils.translation import gettext_lazy as _


class PaymentMethodChoices(models.TextChoices):
    """Payment methods available for transactions."""
    ONLINE = "online", _("Online")   # Payment made through online platforms (UPI, net banking, etc.)
    CASH = "cash", _("Cash")         # Physical cash payment

    @classmethod
    def icon(cls, value):
        return {
            cls.ONLINE: "💳",
            cls.CASH: "💵",
        }.get(value, "")


class AnimalUse(models.TextChoices):
    """Use case classification of the animal."""
    DAIRY = "dairy", _("Dairy")              # Milk production
    BEEF = "beef", _("Beef")                # Meat production
    DUAL = "dual", _("Dual Purpose")        # Both milk and meat
    OTHER = "other", _("Other")             # Other specific uses

    @classmethod
    def description(cls, value):
        return {
            cls.DAIRY: _("Primarily used for milk production"),
            cls.BEEF: _("Primarily used for meat production"),
            cls.DUAL: _("Used for both dairy and beef purposes"),
            cls.OTHER: _("Uncategorized or other specific use"),
        }.get(value, _("Unknown"))


class GenderChoices(models.TextChoices):
    """Animal gender."""
    MALE = "male", _("Male")
    FEMALE = "female", _("Female")


class UserRoleChoices(models.TextChoices):
    """User roles in the system."""
    DOCTOR = "doctor", _("Doctor")
    MAT = "mat", _("MAT")
    OTHER = "other", _("Other")


class TagMethodChoices(models.TextChoices):
    """Animal tag type used for identification."""
    MANUAL = "Manual", _("Manual")
    RFID = "RFID", _("RFID Tag")
    QR = "QR", _("QR Code")


class TagLocationChoices(models.TextChoices):
    """Location where the tag is applied."""
    LEFT_EAR = "Left Ear", _("Left Ear")
    RIGHT_EAR = "Right Ear", _("Right Ear")
    NECK = "Neck", _("Neck")
    OTHER = "Other", _("Other")


class TagActionChoices(models.TextChoices):
    """Actions performed on tags."""
    CREATED = "created", _("New Tag")
    REPLACED = "replaced", _("Replaced")


class MedicineFormChoices(models.TextChoices):
    """Forms in which medicine is administered."""
    TABLET = "tablet", _("Tablet")
    LIQUID = "liquid", _("Liquid")
    INJECTION = "injection", _("Injection")
    CAPSULE = "capsule", _("Capsule")
    OINTMENT = "ointment", _("Ointment")
    POWDER = "powder", _("Powder")
    PASTE = "paste", _("Paste")
    BOLUS = "bolus", _("Bolus")  # Large pill/tablet for large animals
    SUSPENSION = "suspension", _("Suspension")
    SOLUTION = "solution", _("Solution")
    SPRAY = "spray", _("Spray")
    DROPS = "drops", _("Eye/Ear/Nose Drops")
    CREAM = "cream", _("Cream")
    LOTION = "lotion", _("Lotion")
    SHAMPOO = "shampoo", _("Medicated Shampoo")
    FEED_ADDITIVE = "feed_additive", _("Feed Additive")
    IMPLANT = "implant", _("Implant")
    INHALANT = "inhalant", _("Inhalant")
    TRANSDERMAL_PATCH = "transdermal_patch", _("Transdermal Patch")
    SUPPOSITORY = "suppository", _("Suppository")
    DRENCH = "drench", _("Drench")
    POUR_ON = "pour_on", _("Pour-On")
    INTRAMAMMARY = "intramammary", _("Intramammary")
    OTHER = "other", _("Other")


class TransactionTypeChoices(models.TextChoices):
    """Inventory transaction types."""
    IN = "IN", _("Stock In")
    OUT = "OUT", _("Stock Out")
    ADJUST = "ADJUST", _("Adjustment")


class ActionTypeChoices(models.TextChoices):
    """Inventory action tracking."""
    ALLOCATED = "ALLOCATED", _("Allocated")
    USED = "USED", _("Used")
    RETURNED = "RETURNED", _("Returned")


class CaseTypeChoices(models.TextChoices):
    """Classification of medical cases."""
    NORMAL = "Normal", _("Normal Case")
    SPECIAL = "Special", _("Special Case")
    OPERATIONAL = "Operational", _("Operational Case")


class PeriodChoices(models.TextChoices):
    """Time slot choices."""
    MORNING = "Morning", _("Morning")
    AFTERNOON = "Afternoon", _("Afternoon")
    EVENING = "Evening", _("Evening")
    NIGHT = "Night", _("Night")


class StatusChoices(models.TextChoices):
    """Workflow status states."""
    PENDING = "Pending", _("Pending")
    CONFIRMED = "Confirmed", _("Confirmed")
    COMPLETED = "Completed", _("Completed")


class CattleStatusChoices(models.TextChoices):
    """Cattle's reproductive/lactation status."""
    DRY = "dry", _("Dry")
    PREGNANT = "pregnant", _("Pregnant")
    MILKING = "milking", _("Milking")
    MILKING_PREGNANT = "milking_pregnant", _("Milking & Pregnant")


class DiseaseSeverity(models.TextChoices):
    MILD = "Mild", _("Mild")
    MODERATE = "Moderate", _("Moderate")
    SEVERE = "Severe", _("Severe")
    CRITICAL = "Critical", _("Critical")
    
class PaymentStatusChoices(models.TextChoices):
    """Payment processing status."""
    
    PENDING = "pending", _("Pending")
    COMPLETED = "completed", _("Completed")
    FAILED = "failed", _("Failed")
    REFUNDED = "refunded", _("Refunded")


class TransferTypeChoices(models.TextChoices):
    INWARD = "inward", _("Inward")        # For receiving new stock
    OUTWARD = "outward", _("Outward")     # For sending stock to another location
    RETURN = "return", _("Return")        # For returning stock to source (e.g., damaged/unused)

class TransferStatusChoices(models.TextChoices):
    PENDING = "pending", _("Pending")         # Awaiting approval or dispatch
    APPROVED = "approved", _("Approved")      # Completed and received
    CANCELLED = "cancelled", _("Cancelled")   # Cancelled transfer

class LocationTypeChoices(models.TextChoices):
    CENTRAL_WAREHOUSE = "central_warehouse", _("Central Warehouse")
    FIELD_OFFICE = "field_office", _("Field Office")
    MOBILE_UNIT = "mobile_unit", _("Mobile Veterinary Unit")
    CLINIC = "clinic", _("Clinic")
    VET = "vet", _("Veterinarian")
