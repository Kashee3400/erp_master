from django.db import models
import random
import string
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone



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

class SahayakIncentives(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incentives', verbose_name=_('Sahayak'))
    mcc_code = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('MCC Code'))
    mcc_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('MCC Name'))
    mpp_code = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('MPP Code'))
    mpp_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('MPP Name'))
    month = models.CharField(max_length=100, verbose_name=_('Month'))
    opening = models.FloatField(default=0.0, verbose_name=_('Previous Month Opening'))
    milk_incentive = models.FloatField(default=0.0, verbose_name=_('Milk Incentive'))
    other_incentive = models.FloatField(default=0.0, verbose_name=_('Other Incentive'))
    payable = models.FloatField(default=0.0, verbose_name=_('Net Payable'))
    closing = models.FloatField(default=0.0, verbose_name=_('Closing'))

    def __str__(self):
        return self.mpp_code
    
    class Meta:
        app_label = 'member'
        db_table = 'sahayak'
        verbose_name = _('Sahayak Incentive')
        verbose_name_plural = _('Sahayak Incentives')

class ProductRate(models.Model):
    LOCALE_CHOICES = (
        ('en', _('English')),
        ('hi', _('Hindi')),
    )

    name = models.CharField(max_length=100, verbose_name=_('Product Name'),
                            help_text=_('The name of product'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Product Price'),
                                help_text=_('Rate of the product'))
    image = models.ImageField(upload_to='products/', null=True, blank=True,verbose_name=_('Product Image'),
                            help_text=_('Image of the product to display as icon, size should be 100x100'))
    locale = models.CharField(max_length=10, choices=LOCALE_CHOICES, default='en', verbose_name=_('Locale'),
                            help_text=_('Locale of the product data (e.g., en for English, hi for Hindi)'))
    
    name_translation = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Translated Product Name'),
                                        help_text=_('Translated name of the product in the selected locale'))
    price_description = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Price Description'),
                                        help_text=_('Description of the product price, e.g., price of 1 bag or 1 pill'))


    created_at = models.DateTimeField(auto_now_add=True,verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    created_by = models.ForeignKey(User,verbose_name=_('Created By') ,related_name='products_created', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ForeignKey(User,verbose_name=_('Updated By'), related_name='products_updated', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.name} {self.price} ({self.get_locale_display()})'


    class Meta:
        app_label = 'member'
        db_table = 'product_rate'
        verbose_name = _('Product Rate')
        verbose_name_plural = _('Product Rates')
