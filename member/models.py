import random
import string
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import uuid
from django_ckeditor_5.fields import CKEditor5Field
from django.conf import settings
from django.core.files.base import ContentFile
import base64
from decimal import Decimal
from django.db import models, transaction
from django.core.validators import MinValueValidator, MinLengthValidator
from django.utils import timezone
from .choices import TransactionType, RewardSource, WithdrawalStatus
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.urls import reverse
from .manager.news import NewsQuerySet

User = get_user_model()

HARD_CODED_NUMBER1 = "6388952128"
HARD_CODED_NUMBER2 = "6388952126"
HARD_CODED_OTP = "112233"


class OTP(models.Model):
    phone_number = models.CharField(
        max_length=10, unique=True, verbose_name=_("Phone Number")
    )
    otp = models.CharField(max_length=6, verbose_name=_("OTP"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created AT"))

    def save(self, *args, **kwargs):
        if not self.otp:
            if self.phone_number in [HARD_CODED_NUMBER1, HARD_CODED_NUMBER2]:
                self.otp = HARD_CODED_OTP
            else:
                # Generating a random OTP for other numbers
                self.otp = "".join(random.choices(string.digits, k=6))
        super().save(*args, **kwargs)

    def is_valid(self):
        # Check if the OTP is still valid (e.g., within 5 minutes)
        return (timezone.now() - self.created_at).seconds < 300

    def __str__(self):
        return self.otp

    class Meta:
        app_label = "member"
        db_table = "user_otp"
        verbose_name = _("User OTP")
        verbose_name_plural = _("Users' OTPs")


class UserDevice(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="device", verbose_name=_("User")
    )
    device = models.CharField(
        max_length=255, unique=True, blank=True, null=True, verbose_name=_("Device")
    )
    device_type = models.CharField(
        max_length=10,
        choices=[("android", "Android"), ("ios", "iOS"), ("web", "Web")],
        default="android",
    )
    mpp_code = models.CharField(
        max_length=200, blank=True, null=True, verbose_name=_("MPP Code")
    )
    fcm_token = models.TextField(blank=True, null=True, verbose_name=_("FCM Token"))
    module = models.CharField(
        max_length=200, blank=True, null=True, verbose_name=_("Module Code")
    )
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} - {self.device}"

    class Meta:
        app_label = "member"
        db_table = "user_device"
        verbose_name = _("User Device")
        verbose_name_plural = _("Users' Devices")


class SahayakIncentives(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="incentives",
        verbose_name=_("Sahayak"),
    )
    mcc_code = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("MCC Code")
    )
    mcc_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("MCC Name")
    )
    mpp_code = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("MPP Code")
    )
    mpp_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("MPP Name")
    )
    month = models.CharField(max_length=100, verbose_name=_("Month"))
    year = models.CharField(max_length=100, default="2024", verbose_name=_("Year"))
    opening = models.FloatField(default=0.0, verbose_name=_("Opening Balance"))
    milk_qty = models.FloatField(default=0.0, verbose_name=_("Milk Qty"))
    milk_incentive = models.FloatField(default=0.0, verbose_name=_("Milk Incentive"))
    tds = models.FloatField(default=0.0, verbose_name=_("TDS(%)"))
    tds_amt = models.FloatField(default=0.0, verbose_name=_("TDS (AMT)"))
    other_incentive = models.FloatField(default=0.0, verbose_name=_("Other Incentive"))
    cf_incentive = models.FloatField(
        default=0.0, verbose_name=_("Cattle Feed Incentive")
    )
    mm_incentive = models.FloatField(
        default=0.0, verbose_name=_("Mineral Mixture Incentive")
    )
    cda_recovery = models.FloatField(default=0.0, verbose_name=_("C.D.A Recovery"))
    recovery_deposited = models.FloatField(
        default=0.0, verbose_name=_("Recovery Deposited")
    )
    transporter_recovery = models.FloatField(
        default=0.0, verbose_name=_("Transporter Recovery")
    )
    asset_recovery = models.FloatField(default=0.0, verbose_name=_("Asset Recovery"))
    milk_incentive_payable = models.FloatField(
        default=0.0, verbose_name=_("Milk Incentive Payable")
    )
    payable = models.FloatField(default=0.0, verbose_name=_("Payable"))
    closing = models.FloatField(default=0.0, verbose_name=_("Closing Balance"))
    additional_data = models.JSONField(
        verbose_name=_("Additional Data"),
        blank=True,
        null=True,
        help_text=_("Add additional data to be shown in sahayak recovery"),
    )

    def __str__(self):
        return self.mpp_code

    class Meta:
        app_label = "member"
        db_table = "sahayak"
        verbose_name = _("Sahayak Incentive")
        verbose_name_plural = _("Sahayak Incentives")


class ProductRate(models.Model):
    LOCALE_CHOICES = (
        ("en", _("English")),
        ("hi", _("Hindi")),
    )

    name = models.CharField(
        max_length=100,
        verbose_name=_("Product Name"),
        help_text=_("The name of product"),
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Product Price"),
        help_text=_("Rate of the product"),
    )
    image = models.ImageField(
        upload_to="products/",
        null=True,
        blank=True,
        verbose_name=_("Product Image"),
        help_text=_("Image of the product to display as icon, size should be 100x100"),
    )
    locale = models.CharField(
        max_length=10,
        choices=LOCALE_CHOICES,
        default="en",
        verbose_name=_("Locale"),
        help_text=_("Locale of the product data (e.g., en for English, hi for Hindi)"),
    )

    name_translation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Translated Product Name"),
        help_text=_("Translated name of the product in the selected locale"),
    )
    price_description = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Price Description"),
        help_text=_("Description of the product price, e.g., price of 1 bag or 1 pill"),
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    created_by = models.ForeignKey(
        User,
        verbose_name=_("Created By"),
        related_name="products_created",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        User,
        verbose_name=_("Updated By"),
        related_name="products_updated",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.name} {self.price} ({self.get_locale_display()})"

    class Meta:
        app_label = "member"
        db_table = "product_rate"
        verbose_name = _("Product Rate")
        verbose_name_plural = _("Product Rates")


class News(models.Model):
    """
    News model for managing articles across different modules.
    Optimized for production with proper indexing, validation, and query optimization.
    """

    MODULE_CHOICES = [
        ("member", _("Member")),
        ("facilitator", _("Facilitator")),
        ("sahayak", _("Sahayak")),
        ("admin", _("Admin")),
        ("all", _("All Modules")),
    ]

    # Core fields
    title = models.CharField(
        max_length=255,
        verbose_name=_("Title"),
        help_text=_("Enter the title of the news article (max 255 characters)."),
        validators=[
            MinLengthValidator(5, _("Title must be at least 5 characters long."))
        ],
        db_index=True,  # Index for faster search
    )

    slug = models.SlugField(
        unique=True,
        max_length=255,
        verbose_name=_("Slug"),
        help_text=_(
            "Unique identifier for the news article (auto-generated from title)."
        ),
        db_index=True,
    )

    summary = models.TextField(
        max_length=500,
        verbose_name=_("Summary"),
        help_text=_("Brief summary (max 500 characters) - shown in listings."),
        validators=[
            MinLengthValidator(10, _("Summary must be at least 10 characters."))
        ],
    )

    content = CKEditor5Field(
        verbose_name=_("Content"),
        help_text=_("Full article content with rich text formatting."),
        config_name="extends",
    )

    # Author information - Consider making this a ForeignKey to User model in future
    author = models.CharField(
        max_length=100,
        verbose_name=_("Author"),
        help_text=_("Name of the article author."),
        db_index=True,  # Index for author filtering
    )

    # Timestamps
    published_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Published Date"),
        help_text=_("Date and time when article was first published."),
        db_index=True,  # Important for ordering and filtering
    )

    updated_date = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated Date"),
        help_text=_("Date and time of last update."),
    )

    # Media
    image = models.ImageField(
        upload_to="news/images/%Y/%m/",  # Organize by year/month
        blank=True,
        null=True,
        verbose_name=_("Featured Image"),
        help_text=_("Optional featured image (recommended: 1200x630px)."),
    )

    # Categorization
    tags = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Tags"),
        help_text=_(
            "Comma-separated tags for categorization (e.g., policy, update, event)."
        ),
    )

    module = models.CharField(
        max_length=50,
        choices=MODULE_CHOICES,
        default="member",
        verbose_name=_("Target Module"),
        help_text=_("Which module this news is for."),
        db_index=True,  # Critical for filtering
    )

    # Status flags
    is_published = models.BooleanField(
        default=False,
        verbose_name=_("Published"),
        help_text=_("Check to make this article visible to users."),
        db_index=True,  # Important for filtering published content
    )

    is_featured = models.BooleanField(
        default=False,
        verbose_name=_("Featured"),
        help_text=_("Mark as featured to show prominently."),
        db_index=True,
    )

    is_read = models.BooleanField(
        default=False,
        verbose_name=_("Mark as Read"),
        help_text=_("Internal flag to track read status."),
        db_index=True,  # For quick unread counts
    )

    # Analytics
    view_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("View Count"),
        help_text=_("Number of times this article has been viewed."),
    )

    # Custom manager
    objects = NewsQuerySet.as_manager()

    class Meta:
        app_label = "member"
        db_table = "news"
        ordering = ["-published_date"]
        verbose_name = _("News Article")
        verbose_name_plural = _("News Articles")

        # Database constraints for data integrity
        constraints = [
            models.CheckConstraint(
                check=models.Q(view_count__gte=0),
                name="%(app_label)s_%(class)s_positive_view_count",
                violation_error_message=_("View count cannot be negative."),
            ),
        ]

        # Composite indexes for common queries
        indexes = [
            models.Index(
                fields=["-published_date", "is_published"],
                name="news_pub_date_status_idx",
            ),
            models.Index(
                fields=["module", "is_published", "-published_date"],
                name="news_module_pub_idx",
            ),
            models.Index(
                fields=["is_published", "is_featured", "-published_date"],
                name="news_featured_idx",
            ),
            models.Index(
                fields=["author", "-published_date"],
                name="news_author_date_idx",
            ),
        ]

        # Permissions
        permissions = [
            ("can_feature_news", _("Can mark news as featured")),
            ("can_publish_news", _("Can publish news articles")),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Override save to auto-generate slug if not provided"""
        if not self.slug:
            self.slug = self.generate_unique_slug()

        # Call full_clean to validate constraints
        if kwargs.pop("validate", True):
            self.full_clean()

        super().save(*args, **kwargs)

    def clean(self):
        """Model-level validation"""
        super().clean()

        # Validate that published articles have required fields
        if self.is_published:
            if not self.summary.strip():
                raise ValidationError(
                    {"summary": _("Summary is required for published articles.")}
                )
            if not self.content:
                raise ValidationError(
                    {"content": _("Content is required for published articles.")}
                )

    def generate_unique_slug(self):
        """Generate a unique slug from the title"""
        base_slug = slugify(self.title)
        slug = base_slug
        counter = 1

        # Ensure slug uniqueness
        while News.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    def get_absolute_url(self):
        """Return the canonical URL for this news article"""
        return reverse("news:detail", kwargs={"slug": self.slug})

    def increment_view_count(self):
        """Atomically increment view count to avoid race conditions"""
        News.objects.filter(pk=self.pk).update(view_count=models.F("view_count") + 1)
        # Refresh from database
        self.refresh_from_db(fields=["view_count"])

    def get_tags_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(",") if tag.strip()]
        return []

    @property
    def reading_time(self):
        """Estimate reading time in minutes (assumes 200 words per minute)"""
        from django.utils.html import strip_tags

        word_count = len(strip_tags(self.content).split())
        return max(1, round(word_count / 200))

    @classmethod
    def get_unread_count(cls, module=None):
        """
        Return count of unread news articles.
        Optimized version using aggregation instead of count().
        """
        queryset = cls.objects.filter(is_read=False, is_published=True)
        if module:
            queryset = queryset.filter(module__in=[module, "all"])
        return queryset.count()

    @classmethod
    def mark_as_read_bulk(cls, article_ids):
        """Bulk update articles as read (more efficient than updating individually)"""
        return cls.objects.filter(id__in=article_ids).update(is_read=True)


# class News(models.Model):
#     title = models.CharField(
#         max_length=255,
#         verbose_name="Title",
#         help_text="Enter the title of the news article.",
#     )
#     slug = models.SlugField(
#         unique=True,
#         max_length=255,
#         verbose_name="Slug",
#         help_text="Unique identifier for the news article (auto-generated from the title).",
#     )
#     summary = models.TextField(
#         verbose_name="Summary",
#         help_text="Enter a brief summary or introduction to the news article.",
#     )
#     content = CKEditor5Field(
#         verbose_name="Content",
#         help_text="Enter the full content of the news article using a rich text editor.",
#     )
#     author = models.CharField(
#         max_length=100,
#         verbose_name="Author",
#         help_text="Name of the author of the article.",
#     )
#     published_date = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name="Published Date",
#         help_text="The date and time when the article was published.",
#     )
#     updated_date = models.DateTimeField(
#         auto_now=True,
#         verbose_name="Updated Date",
#         help_text="The date and time when the article was last updated.",
#     )
#     image = models.ImageField(
#         upload_to="news/images/",
#         blank=True,
#         null=True,
#         verbose_name="Image",
#         help_text="Upload an optional image for the news article.",
#     )
#     tags = models.CharField(
#         max_length=255,
#         blank=True,
#         verbose_name="Tags",
#         help_text="Comma-separated tags for categorizing the article.",
#     )
#     is_published = models.BooleanField(
#         default=False,
#         verbose_name="Is Published",
#         help_text="Check this box to publish the article.",
#     )
#     is_read = models.BooleanField(
#         default=False,
#         verbose_name="Is Read",
#         help_text="Check this box to mark the article as read.",
#     )

#     module = models.CharField(
#         max_length=255,
#         default="member",
#         verbose_name="Module",
#         help_text="Module Specific News. For ex:- member, facilitator, sahayak",
#     )

#     @classmethod
#     def not_read_count(cls):
#         """
#         Return the count of news articles that are marked as 'not read'.
#         """
#         return cls.objects.filter(is_read=False).count()

#     def __str__(self):
#         return self.title

#     class Meta:
#         app_label = "member"
#         ordering = ["-published_date"]
#         verbose_name = "News"
#         verbose_name_plural = "News"


class RewardedAdTransaction(models.Model):
    """
    Represents a single reward event generated by a user viewing a rewarded ad.
    This is the server-authoritative record to prevent fraudulent claims.
    """

    # Identifiers
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        verbose_name="Transaction UUID",
        help_text="System-generated unique identifier for this rewarded ad transaction.",
    )

    # Relationships
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="rewarded_ad_transactions",
        verbose_name="User",
        help_text="The user who earned this reward by completing a rewarded ad.",
    )

    # Core attributes
    reward_source = models.CharField(
        max_length=20,
        choices=RewardSource.choices,
        default=RewardSource.GOOGLE,
        verbose_name="Reward Source",
        help_text="Identifies which ad network generated this reward (e.g., Google, Facebook).",
    )

    ad_unit_id = models.CharField(
        max_length=255,
        verbose_name="Ad Unit ID",
        help_text="Unique ad unit identifier as configured in the ad network console.",
    )

    reward_type = models.CharField(
        max_length=100,
        default="coins",
        verbose_name="Reward Type",
        help_text="Type of reward granted (e.g., coins, points, tokens).",
    )

    reward_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Reward Amount",
        help_text="Numeric value of the reward granted (e.g., 10 coins).",
    )

    transaction_token = models.CharField(
        max_length=512,
        unique=True,
        verbose_name="Transaction Token",
        help_text="Unique token provided by the ad network to verify server-side callbacks.",
    )

    # Metadata & tracking
    device_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Device ID",
        help_text="Optional unique device identifier to detect abuse or duplication.",
    )

    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name="IP Address",
        help_text="IP address from which the rewarded ad completion was received.",
    )

    is_verified = models.BooleanField(
        default=False,
        verbose_name="Is Verified",
        help_text="Indicates whether this transaction was verified via Google’s server-side verification API.",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text="Timestamp when the transaction record was created.",
    )

    verified_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Verified At",
        help_text="Timestamp when the ad reward was verified successfully.",
    )

    # Audit fields
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Updated",
        help_text="Auto-updated timestamp of the last modification to this record.",
    )

    class Meta:
        verbose_name = "Rewarded Ad Transaction"
        verbose_name_plural = "Rewarded Ad Transactions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "reward_source"]),
            models.Index(fields=["transaction_token"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "transaction_token"],
                name="unique_user_reward_transaction",
            ),
        ]
        db_table = "rewarded_ad_transaction"

    def __str__(self):
        return f"{self.user.username} - {self.reward_amount} {self.reward_type} ({self.reward_source})"

    # Helper methods
    def mark_verified(self):
        """Mark this transaction as verified and timestamp it."""
        self.is_verified = True
        self.verified_at = timezone.now()
        self.save(update_fields=["is_verified", "verified_at", "updated_at"])

    @property
    def is_pending(self):
        """Check if the transaction is awaiting verification."""
        return not self.is_verified

    @classmethod
    def total_rewards_for_user(cls, user):
        """Aggregate total verified rewards for a given user."""
        return cls.objects.filter(user=user, is_verified=True).aggregate(
            total=models.Sum("reward_amount")
        ).get("total") or Decimal("0.00")


class RewardLedger(models.Model):
    """
    A user’s reward ledger that records all credit and debit transactions
    including ad earnings, withdrawals, or manual adjustments.
    """

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        verbose_name="Ledger Entry UUID",
        help_text="System-generated unique identifier for this ledger transaction.",
    )

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="reward_ledger_entries",
        verbose_name="User",
        help_text="The user whose reward balance is affected.",
    )

    source_ad = models.ForeignKey(
        "RewardedAdTransaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ledger_entries",
        verbose_name="Source Ad Transaction",
        help_text="Reference to the original ad reward transaction (if applicable).",
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        verbose_name="Transaction Type",
        help_text="Indicates whether this record is a credit, debit, or adjustment.",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Amount",
        help_text="The amount credited or debited to the user’s balance.",
    )

    balance_after = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Balance After Transaction",
        help_text="The user’s balance immediately after this transaction.",
    )

    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Description",
        help_text="Optional note or reason for this transaction (e.g., 'Ad Reward', 'Withdrawal').",
    )

    is_finalized = models.BooleanField(
        default=False,
        verbose_name="Is Finalized",
        help_text="Indicates whether this transaction has been locked from modification.",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text="Timestamp when this ledger entry was created.",
    )

    class Meta:
        verbose_name = "Reward Ledger Entry"
        verbose_name_plural = "Reward Ledger Entries"
        ordering = ["-created_at"]
        db_table = "reward_ledger"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["transaction_type"]),
        ]

    def __str__(self):
        return f"{self.user.username} | {self.transaction_type} | {self.amount} | Bal: {self.balance_after}"

    # --- Helper & Business Logic ---

    @classmethod
    @transaction.atomic
    def credit_user(cls, user, amount: Decimal, description="", source_ad=None):
        """Credit a user's account and return the new ledger entry."""
        current_balance = cls.get_user_balance(user)
        new_balance = current_balance + amount
        entry = cls.objects.create(
            user=user,
            source_ad=source_ad,
            transaction_type=TransactionType.CREDIT,
            amount=amount,
            balance_after=new_balance,
            description=description or "Ad Reward Credited",
            is_finalized=True,
        )
        return entry

    @classmethod
    @transaction.atomic
    def debit_user(cls, user, amount: Decimal, description=""):
        """Debit (withdraw) from a user's account safely."""
        current_balance = cls.get_user_balance(user)
        if amount > current_balance:
            raise ValueError("Insufficient balance for withdrawal.")
        new_balance = current_balance - amount
        entry = cls.objects.create(
            user=user,
            transaction_type=TransactionType.DEBIT,
            amount=amount,
            balance_after=new_balance,
            description=description or "User Withdrawal",
            is_finalized=True,
        )
        return entry

    @classmethod
    def get_user_balance(cls, user) -> Decimal:
        """Return the user’s latest available balance."""
        last_entry = cls.objects.filter(user=user).order_by("-created_at").first()
        return last_entry.balance_after if last_entry else Decimal("0.00")


class RewardWithdrawalRequest(models.Model):
    """
    Represents a user's request to withdraw earned rewards from the ledger.
    """

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="withdrawal_requests",
        verbose_name="User",
        help_text="The user who requested the withdrawal.",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("1.00"))],
        verbose_name="Requested Amount",
        help_text="Amount user has requested to withdraw.",
    )

    status = models.CharField(
        max_length=20,
        choices=WithdrawalStatus.choices,
        default=WithdrawalStatus.PENDING,
        verbose_name="Withdrawal Status",
        help_text="Current processing state of this withdrawal request.",
    )

    transaction_reference = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Transaction Reference",
        help_text="Payment gateway or internal reference ID once processed.",
    )

    requested_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Requested At",
        help_text="Timestamp when the withdrawal was initiated.",
    )

    processed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Processed At",
        help_text="Timestamp when the withdrawal was approved or completed.",
    )

    remarks = models.TextField(
        blank=True,
        null=True,
        verbose_name="Admin Remarks",
        help_text="Optional remarks from admin during approval or rejection.",
    )

    class Meta:
        verbose_name = "Reward Withdrawal Request"
        verbose_name_plural = "Reward Withdrawal Requests"
        ordering = ["-requested_at"]
        db_table = "reward_withdrawal_request"

    def __str__(self):
        return f"{self.user.username} | ₹{self.amount} | {self.status}"
