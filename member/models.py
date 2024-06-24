from django.db import models
import random
import string
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


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


class ProductImage(models.Model):
    product_code = models.CharField(max_length=50, verbose_name=_('Product Code'))
    product_name = models.CharField(max_length=50, verbose_name=_('Product Name'), blank=True, null=True)
    image = models.ImageField(upload_to='product_images/')
    created_at = models.DateTimeField(auto_now_add=True,verbose_name= _('Created At'))
    updated_at = models.DateTimeField(auto_now=True,verbose_name= _('Updated At'))
    
    def __str__(self):
        return f'{self.product_code}'

    class Meta:
        db_table = 'product_image'
        verbose_name = _('Product Image')
        verbose_name_plural = _('Product Images')
        app_label = 'member'


class BrandImage(models.Model):
    brand_code = models.CharField(max_length=50, verbose_name=_('Brand Code'))
    brand_name = models.CharField(max_length=50, verbose_name=_('Brand Name'), blank=True, null=True)
    image = models.ImageField(upload_to='brand_images/')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True,verbose_name= _('Updated At'))

    def __str__(self):
        return f'{self.brand_code}'

    class Meta:
        db_table = 'brand_image'
        verbose_name = _('Brand Image')
        verbose_name_plural = _('Brand Images')
        app_label = 'member'


class CategoryImage(models.Model):
    category_code = models.CharField(max_length=50, verbose_name=_('Category Code'))
    category_name = models.CharField(max_length=50, verbose_name=_('Category Name'), blank=True, null=True)
    image = models.ImageField(upload_to='category_images/')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True,verbose_name= _('Updated At'))
 
    def __str__(self):
        return f'{self.category_code}'

    class Meta:
        db_table = 'category_image'
        verbose_name = _('Category Image')
        verbose_name_plural = _('Category Images')
        app_label = 'member'

