# choices.py

from django.db import models
from django.utils.translation import gettext_lazy as _


class RequestTypeChoices(models.TextChoices):
    MOBILE = "MOBILE", _("Mobile Number")
    BANK = "BANK", _("Bank Account Details")


class RoleType(models.TextChoices):
    MOBILE = "SAHAYAK", _("Sahayak")
    MEMBER = "MEMBER", _("Member")


class RequestStatus(models.TextChoices):
    PENDING = "PENDING", _("Pending")
    REJECTED = "REJECTED", _("Rejected")
    UPDATED = "UPDATED", _("Updated")


class ChangeType(models.TextChoices):
    CREATE = "CREATE", _("Created")
    UPDATE = "UPDATE", _("Updated")
    DELETE = "DELETE", _("Deleted")
    STATUS_CHANGE = "STATUS_CHANGE", _("Status Changed")
    REVIEW = "REVIEW", _("Reviewed")


class DocumentTypeChoice(models.TextChoices):
    PASSBOOK = (
        "passbook",
        _("Passbook Copy"),
    )
    APPLICATION = (
        "application",
        _("Application Letter"),
    )
    AFFIDAVIT = (
        "affidavit",
        _("Affidavit Copy"),
    )


class RouteLevelChoice(models.TextChoices):
    LEVEL_MCC = "mcc", _("MCC Level")
    LEVEL_ROUTE = "route", _("Route Level")
    LEVEL_MPP = "mpp", _("MPP Level")
