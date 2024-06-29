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
                # Hardcoding the OTP for a specific number
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


class ProductStockOpening(models.Model):
    product_stock_opening_code = models.AutoField(primary_key=True)
    financial_year_code = models.IntegerField(blank=True, null=True)
    product_code = models.CharField(max_length=50, verbose_name=_('Product Code'))
    product_name = models.CharField(max_length=50, verbose_name=_('Product Name'), blank=True, null=True)
    qty = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    as_on_date = models.DateTimeField(blank=True, null=True)
    warehouse_code = models.CharField(max_length=50,verbose_name=_('Warehouse Code'),blank=True, null=True)
    warehouse_name = models.CharField(max_length=100,verbose_name=_('Warehouse Name'),blank=True, null=True)
    bin_location_code = models.CharField(max_length=50,verbose_name=_('Bin Location Code'),blank=True, null=True)
    bin_location_name = models.CharField(max_length=100,verbose_name=_('Bin Location Name'),blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,related_name='added_user_stock')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,related_name='updated_user_stock', blank=True)

    def __str__(self):
        return f'{self.product_name} {self.qty}'
    
    class Meta:
        db_table = 'product_stock_opening'
        verbose_name = _('Product Stock Opening')
        verbose_name_plural = _('Product Stock Opening')
        app_label = 'member'


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_address',verbose_name=_('User'))
    street = models.CharField(max_length=100,verbose_name=_('Street', blank=True, null=True))
    city = models.CharField(max_length=50, verbose_name=_('City'))
    state = models.CharField(max_length=50, verbose_name=_('State'))
    country = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}, {self.country} - {self.postal_code}"
    
class PaymentMethod(models.Model):
    method = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.method
    
    class Meta:
        db_table = 'tbl_payment_method'
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'


class Order(models.Model):
    PENDING = 'Pending'
    PROCESSED = 'Processed'
    DELIVERED = 'Delivered'
    CANCELLED = 'Cancelled'

    ORDER_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSED, 'Processed'),
        (DELIVERED, 'Delivered'),
        (CANCELLED, 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_orders')
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default=PENDING)
    order_comment = models.TextField(blank=True, null=True)
    order_date = models.DateTimeField(auto_now_add=True)
    order_id = models.CharField(max_length=11, unique=True, editable=False, blank=True,null=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name="order_address")
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, related_name="order_payments", null=True)

    def save(self, *args, **kwargs):
        self.order_id = self.generate_order_id()
        super().save(*args, **kwargs)

    def generate_order_id(self):
        prefix = 'ODR'
        # Generate random 8-digit number
        random_digits = ''.join(random.choices(string.digits, k=8))
        return f'{prefix}{random_digits}'

    def __str__(self):
        return f"Order for {self.user.username} ({self.status})"

    def mark_as_processed(self):
        if self.status == self.PENDING:
            self.status = self.PROCESSED
            self.save()
        else:
            raise ValueError("Cannot mark order as processed. Current status is not Pending.")

    def mark_as_delivered(self):
        if self.status == self.PROCESSED:
            self.status = self.DELIVERED
            self.save()
        else:
            raise ValueError("Cannot mark order as delivered. Current status is not Processed.")

    def cancel_order(self):
        if self.status == self.PENDING or self.status == self.PROCESSED:
            self.status = self.CANCELLED
            self.save()
        else:
            raise ValueError("Cannot cancel order. Current status is Delivered or Cancelled.")
        
    class Meta:
        db_table = 'tbl_order'
        managed = True
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name='Order')
    product_code = models.CharField(max_length=50, verbose_name=_('Product Code'))
    product_name = models.CharField(max_length=50, verbose_name=_('Product Name'), blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1, verbose_name=_('Quantity'))

    @property
    def subtotal(self):
        return self.quantity * self.book.price

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.book.reduce_stock(self.quantity)

    def __str__(self):
        return f"{self.quantity} x {self.book.title}"

    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')
        
    class Meta:
        db_table = 'tbl_order_item'
        managed = True
        verbose_name = _('Order Item')
        verbose_name_plural =_( 'Order Items')
