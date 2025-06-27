from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

User = get_user_model()

class UserProfile(models.Model):
    """Stores additional user metadata like department, contact details, and avatar."""

    class Department(models.TextChoices):
        SUPPORT = "support", _("Support")
        IT = "it", _("IT")
        PIB = "pib", _("PIB")
        SALES = "sales", _("Sales")
        HR = "hr", _("Human Resources")
        ENGINEERING = "engineering", _("Engineering")
        ADMIN = "admin", _("Administration")

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_("User"),
        help_text=_("The user to whom this profile belongs.")
    )
    department = models.CharField(
        max_length=32,
        choices=Department.choices,
        blank=True,
        null=True,
        verbose_name=_("Department"),
        help_text=_("Department or team of the user.")
    )
    avatar = models.ImageField(
        upload_to="profile_images/",
        blank=True,
        null=True,
        verbose_name=_("Avatar"),
        help_text=_("User profile picture.")
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name=_("Phone Number"),
        help_text=_("Contact number of the user.")
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Address"),
        help_text=_("Residential or official address.")
    )
    designation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Designation"),
        help_text=_("Official designation or title.")
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_("Verified"),
        help_text=_("Indicates whether the user's profile is verified.")
    )
    is_email_verified = models.BooleanField(
        default=False,
        verbose_name=_("Email Verified"),
        help_text=_("Indicates whether the user's email is verified.")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At")
    )


    def is_internal(self):
        return self.department in [
            self.Department.IT,
            self.Department.ENGINEERING,
            self.Department.ADMIN,
        ]

    def full_contact_info(self):
        return f"{self.phone_number or '-'} | {self.address or '-'}"
    
    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")
        ordering = ["department","user__username"]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_department_display()}"

    def is_support_staff(self):
        return self.department == self.Department.SUPPORT

    def is_pib_staff(self):
        return self.department == self.Department.PIB
