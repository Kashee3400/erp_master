from django.db import models
import random
import string
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from django.utils import timezone
from modeltranslation.translator import translator, TranslationOptions


User = get_user_model()

class OTP(models.Model):
    phone_number = models.CharField(max_length=10, unique=True,verbose_name=_('Phone Number'))
    otp = models.CharField(max_length=6, verbose_name=_('OTP'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created AT'))

    def save(self, *args, **kwargs):
        self.otp = ''.join(random.choices(string.digits, k=6))
        super().save(*args, **kwargs)

    def is_valid(self):
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

