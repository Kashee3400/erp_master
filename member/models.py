from django.db import models
import random
import string
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid



User = get_user_model()

HARD_CODED_NUMBER1 = '6388952128'
HARD_CODED_NUMBER2 = '6388952126'
HARD_CODED_OTP = '112233'

class OTP(models.Model):
    phone_number = models.CharField(max_length=10, unique=True, verbose_name=_('Phone Number'))
    otp = models.CharField(max_length=6, verbose_name=_('OTP'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created AT'))

    def save(self, *args, **kwargs):
        if not self.otp:
            if self.phone_number in [HARD_CODED_NUMBER1,HARD_CODED_NUMBER2]:
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
    mpp_code = models.CharField(max_length=200,blank=True,null=True,verbose_name=_("MPP Code"))
    fcm_token = models.TextField(blank=True,null=True,verbose_name=_("FCM Token"))
    module = models.CharField(max_length=200,blank=True,null=True,verbose_name=_("Module Code"))
    last_updated = models.DateTimeField(auto_now=True)

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
    year = models.CharField(max_length=100,default='2024', verbose_name=_('Year'))
    opening = models.FloatField(default=0.0, verbose_name=_('Opening Balance'))
    milk_qty = models.FloatField(default=0.0,verbose_name=_('Milk Qty'))
    milk_incentive = models.FloatField(default=0.0, verbose_name=_('Milk Incentive'))
    tds = models.FloatField(default=0.0, verbose_name=_('TDS(%)'))
    tds_amt = models.FloatField(default=0.0, verbose_name=_('TDS (AMT)'))
    other_incentive = models.FloatField(default=0.0, verbose_name=_('Other Incentive'))
    cf_incentive = models.FloatField(default=0.0, verbose_name=_('Cattle Feed Incentive'))
    mm_incentive = models.FloatField(default=0.0, verbose_name=_('Mineral Mixture Incentive'))
    cda_recovery = models.FloatField(default=0.0, verbose_name=_('C.D.A Recovery'))
    asset_recovery = models.FloatField(default=0.0, verbose_name=_('Asset Recovery'))
    milk_incentive_payable = models.FloatField(default=0.0, verbose_name=_('Milk Incentive Payable'))
    payable = models.FloatField(default=0.0, verbose_name=_('Payable'))
    closing = models.FloatField(default=0.0, verbose_name=_('Closing Balance'))
    additional_data = models.JSONField(verbose_name=_('Additional Data'),blank=True,null=True,help_text=_("Add additional data to be shown in sahayak recovery"))


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

from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.files.base import ContentFile
import base64


class SahayakFeedback(models.Model):
    feedback_id = models.CharField(
        max_length=50, unique=True, blank=True, editable=False
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_feedbacks"
    )
    mpp_code = models.CharField(
        max_length=9, blank=True, null=True, verbose_name=_("MPP Code")
    )
    status = models.CharField(
        max_length=100,
        choices=settings.FEEDBACK_STATUS,
        verbose_name=_("Feedback Status"),
        default=settings.OPEN,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    resolved_at = models.DateTimeField(verbose_name=_("Resolved At"), null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    remark = models.TextField(blank=True, verbose_name=_("Remark"))
    message = models.TextField(verbose_name=_("Message"))

    # New file field for uploaded files
    files = models.FileField(
        upload_to="feedback_files/", blank=True, null=True, verbose_name=_("Files")
    )

    def save_base64_files(self, base64_file_list):
        """
        Save Base64-encoded files to the `files` field.
        :param base64_file_list: List of base64-encoded strings
        """
        for idx, base64_file in enumerate(base64_file_list):
            file_data = base64.b64decode(base64_file.get("file", ""))
            filename = f"{self.feedback_id}_file_{idx}.jpg"
            self.files.save(filename, ContentFile(file_data), save=False)

    def close_feedback(self, user, reason="Feedback resolved"):
        self.resolved_at = timezone.now()
        self.save()
        FeedbackLog.objects.create(
            feedback=self,
            user=user,
            status=settings.CLOSED,
            reason=reason,
        )

    def reopen_feedback(self, user, reason="Feedback reopened"):
        FeedbackLog.objects.create(
            feedback=self,
            user=user,
            status=settings.RE_OPENED,
            reason=reason,
        )

    def save(self, *args, **kwargs):
        if not self.feedback_id:
            self.feedback_id = 'FEED' + str(uuid.uuid4().hex)[:6]
        super().save(*args, **kwargs)

    class Meta:
        app_label = 'member'
        db_table = 'sahayak_feedback'
        verbose_name = _('Sahayak Feedback')
        verbose_name_plural = _('Sahayak Feedbacks')


class FeedbackLog(models.Model):
    feedback = models.ForeignKey(
        SahayakFeedback, 
        on_delete=models.CASCADE, 
        related_name="logs"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="feedback_logs")
    status = models.CharField(max_length=20, )
    reason = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'member'
        db_table = 'feedback_logs'
        verbose_name = _('Feedback Log')
        verbose_name_plural = _('Feedback Logs')

    def __str__(self):
        return f"{self.status} - {self.feedback.feedback_id} by {self.user.username}"

from django_ckeditor_5.fields import CKEditor5Field
from django.db import models

class News(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name="Title",
        help_text="Enter the title of the news article."
    )
    slug = models.SlugField(
        unique=True,
        max_length=255,
        verbose_name="Slug",
        help_text="Unique identifier for the news article (auto-generated from the title)."
    )
    summary = models.TextField(
        verbose_name="Summary",
        help_text="Enter a brief summary or introduction to the news article."
    )
    content = CKEditor5Field(
        verbose_name="Content",
        help_text="Enter the full content of the news article using a rich text editor."
    )
    author = models.CharField(
        max_length=100,
        verbose_name="Author",
        help_text="Name of the author of the article."
    )
    published_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Published Date",
        help_text="The date and time when the article was published."
    )
    updated_date = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated Date",
        help_text="The date and time when the article was last updated."
    )
    image = models.ImageField(
        upload_to='news/images/',
        blank=True,
        null=True,
        verbose_name="Image",
        help_text="Upload an optional image for the news article."
    )
    tags = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Tags",
        help_text="Comma-separated tags for categorizing the article."
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name="Is Published",
        help_text="Check this box to publish the article."
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name="Is Read",
        help_text="Check this box to mark the article as read."
    )
    
    @classmethod
    def not_read_count(cls):
        """
        Return the count of news articles that are marked as 'not read'.
        """
        return cls.objects.filter(is_read=False).count()

    def __str__(self):
        return self.title

    class Meta:
        app_label = 'member'
        ordering = ['-published_date']
        verbose_name = 'News'
        verbose_name_plural = 'News'

