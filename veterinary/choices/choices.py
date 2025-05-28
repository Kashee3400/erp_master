from django.db import models

class PaymentMethodChoices(models.TextChoices):
    """Payment methods available for transactions."""
    ONLINE = "online", "Online"   # Payment made through online platforms (UPI, net banking, etc.)
    CASH = "cash", "Cash"         # Physical cash payment

    @classmethod
    def icon(cls, value):
        return {
            cls.ONLINE: "💳",
            cls.CASH: "💵",
        }.get(value, "")


class AnimalUse(models.TextChoices):
    """Use case classification of the animal."""
    DAIRY = 'dairy', 'Dairy'             # Milk production
    BEEF = 'beef', 'Beef'               # Meat production
    DUAL = 'dual', 'Dual Purpose'       # Used for both milk and meat
    OTHER = 'other', 'Other'            # Any other specific use

    @classmethod
    def description(cls, value):
        return {
            cls.DAIRY: "Primarily used for milk production",
            cls.BEEF: "Primarily used for meat production",
            cls.DUAL: "Used for both dairy and beef purposes",
            cls.OTHER: "Uncategorized or other specific use",
        }.get(value, "Unknown")


class GenderChoices(models.TextChoices):
    """ Animal Gender"""
    
    MALE = 'male','Male',
    FEMALE = 'female',"Female"
    

class UserRoleChoices(models.TextChoices):
    DOCTOR = 'doctor','Doctor'
    MAT = 'mat', 'MAT'
    OTHER = 'other','Other'
    
    

class TagMethodChoices(models.TextChoices):
    MANUAL = "Manual", "Manual"          
    RFID = "RFID", "RFID Tag"            
    QR = "QR", "QR Code"

class TagLocationChoices(models.TextChoices):
    LEFT_EAR = "Left Ear", "Left Ear" 
    RIGHT_EAR = "Right Ear", "Right Ear"
    NECK = "Neck", "Neck"
    OTHER = "Other", "Other"

class TagActionChoices(models.TextChoices):
    CREATED = "created", "New Tag"
    REPLACED = "replaced", "Replaced"


class MedicineFormChoices(models.TextChoices):
    TABLET = "tablet", "Tablet"
    LIQUID = "liquid", "Liquid"
    INJECTION = "injection", "Injection"
    CAPSULE = "capsule", "Capsule"
    OINTMENT = "ointment", "Ointment"
    POWDER = "powder", "Powder"
    PASTE = "paste", "Paste"
    BOLUS = "bolus", "Bolus"  # Large pill/tablet for large animals
    SUSPENSION = "suspension", "Suspension"
    SOLUTION = "solution", "Solution"
    SPRAY = "spray", "Spray"
    DROPS = "drops", "Eye/Ear/Nose Drops"
    CREAM = "cream", "Cream"
    LOTION = "lotion", "Lotion"
    SHAMPOO = "shampoo", "Medicated Shampoo"
    FEED_ADDITIVE = "feed_additive", "Feed Additive"
    IMPLANT = "implant", "Implant"
    INHALANT = "inhalant", "Inhalant"
    TRANSDERMAL_PATCH = "transdermal_patch", "Transdermal Patch"
    SUPPOSITORY = "suppository", "Suppository"
    DRENCH = "drench", "Drench"  # Liquid for oral administration
    POUR_ON = "pour_on", "Pour-On"  # Topical, often antiparasitic
    INTRAMAMMARY = "intramammary", "Intramammary"  # Used in mastitis treatment
    OTHER = "other", "Other"


class TransactionTypeChoices(models.TextChoices):
    IN = "IN", "Stock In"
    OUT = "OUT", "Stock Out"
    ADJUST = "ADJUST", "Adjustment"


class ActionTypeChoices(models.TextChoices):
    ALLOCATED = "ALLOCATED", "Allocated"
    USED = "USED", "Used"
    RETURNED = "RETURNED", "Returned"


class CaseTypeChoices(models.TextChoices):
    NORMAL = "Normal", "Normal Case"
    SPECIAL = "Special", "Special Case"
    OPERATIONAL = "Operational", "Operational Case"


class PeriodChoices(models.TextChoices):
    MORNING = "Morning", "Morning"
    AFTERNOON = "Afternoon", "Afternoon"
    EVENING = "Evening", "Evening"
    NIGHT = "Night", "Night"


class StatusChoices(models.TextChoices):
    PENDING = "Pending", "Pending"
    CONFIRMED = "Confirmed", "Confirmed"
    COMPLETED = "Completed", "Completed"


class CattleStatusChoices(models.TextChoices):
    DRY = "dry", "Dry"
    PREGNANT = "pregnant", "Pregnant"
    MILKING = "milking", "Milking"
    MILKING_PREGNANT = "milking_pregnant", "Milking & Pregnant"
