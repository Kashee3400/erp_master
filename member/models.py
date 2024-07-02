from django.db import models
import random
import string
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from oscar.apps.catalogue.abstract_models import AbstractProduct
from oscar.apps.catalogue.models import Product as OscarProduct
from oscar.core.loading import get_model



User = get_user_model()

HARD_CODED_NUMBER = '9415829988'
HARD_CODED_OTP = '112233'

class OTP(models.Model):
    phone_number = models.CharField(max_length=10, unique=True, verbose_name=_('Phone Number'))
    otp = models.CharField(max_length=6, verbose_name=_('OTP'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created AT'))

    def save(self, *args, **kwargs):
        if not self.otp:
            if self.phone_number == HARD_CODED_NUMBER:
                self.otp = HARD_CODED_OTP
            else:
                # Generating a random OTP for other numbers
                self.otp = ''.join(random.choices(string.digits, k=6))
        super().save(*args, **kwargs)

    def is_valid(self):
        # Check if the OTP is still valid (e.g., within 5 minutes)
        return (timezone.now() - self.created_at).seconds < 300

    def __str__(self):
        return self.otp

    class Meta:
        app_label = 'member'
        db_table = 'user_otp'
        verbose_name = _('User OTP')
        verbose_name_plural = _('Users\' OTPs')


class UserDevice(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE, related_name='device', verbose_name=_('User'))
    device = models.CharField(max_length=255, unique=True, blank=True, null=True,verbose_name=_('Device'))
    
    def __str__(self):
        return f'{self.user} - {self.device}'
    
    class Meta:
        app_label = 'member'
        db_table = 'user_device'
        verbose_name = _('User Device')
        verbose_name_plural = _('Users\' Devices')

