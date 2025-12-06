# admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from import_export.admin import ImportExportModelAdmin
from .resources import SahayakIncentivesResource, UserResource, UserDeviceResource
from .models import *
from facilitator.models.user_profile_model import UserProfile
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .filters import PublishedFilter, RecentNewsFilter


User = get_user_model()

# Unregister the existing User admin if it’s already registered
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(ImportExportModelAdmin, DefaultUserAdmin):
    resource_class = UserResource
    list_display = ("username", "email", "first_name", "last_name", "is_staff")


@admin.action(description="Transfer MPP Code → UserProfile")
def transfer_mpp_code(modeladmin, request, queryset):
    """
    Efficiently transfers mpp_code from UserDevice to UserProfile.
    - Auto-creates missing profiles with defaults
    - Updates mpp_code in bulk
    - Normalizes existing profiles with defaults if missing
    - Runs safely inside one atomic transaction
    """

    from django.db import transaction

    DEFAULTS = {
        "salutation": "Mrs.",
        "avatar": "",
        "department": UserProfile.Department.SAHAYAK,
        "phone_number": "",
        "address": "",
        "designation": "",
        "mpp_code": "",
        "is_verified": True,
    }

    with transaction.atomic():
        # 1️⃣ Identify all users from queryset
        user_ids = list(queryset.values_list("user_id", flat=True))

        # 2️⃣ Determine which users already have profiles
        existing_profiles_qs = UserProfile.objects.filter(user_id__in=user_ids)
        existing_user_ids = set(existing_profiles_qs.values_list("user_id", flat=True))

        # 3️⃣ Bulk-create missing profiles with defaults
        missing_user_ids = [uid for uid in user_ids if uid not in existing_user_ids]
        new_profiles = [
            UserProfile(user_id=uid, **DEFAULTS) for uid in missing_user_ids
        ]
        UserProfile.objects.bulk_create(new_profiles, ignore_conflicts=True)

        # 4️⃣ Build a map of user_id → latest mpp_code
        device_map = {}
        for device in queryset.order_by("user_id", "-last_updated"):
            if device.user_id not in device_map and device.mpp_code:
                device_map[device.user_id] = device.mpp_code or ""

        # 5️⃣ Fetch all profiles again (including newly created)
        profiles = list(UserProfile.objects.filter(user_id__in=user_ids))

        # 6️⃣ Apply defaults to existing profiles if blank + update mpp_code
        updated_profiles = []
        for profile in profiles:
            # Fill missing default values
            for field, default_val in DEFAULTS.items():
                value = getattr(profile, field, None)
                if value in [None, ""]:
                    setattr(profile, field, default_val)

            # Update mpp_code if changed
            new_code = device_map.get(profile.user_id, "")
            if new_code is None:
                new_code = ""
            if profile.mpp_code != new_code:
                profile.mpp_code = new_code

            updated_profiles.append(profile)

        # 7️⃣ Bulk update all modified profiles efficiently
        UserProfile.objects.bulk_update(
            updated_profiles,
            [
                "salutation",
                "avatar",
                "department",
                "phone_number",
                "address",
                "designation",
                "mpp_code",
                "is_verified",
            ],
        )

    modeladmin.message_user(
        request,
        f"✅ Bulk transfer complete — "
        f"{len(missing_user_ids)} profile(s) created, "
        f"{len(updated_profiles)} normalized and updated.",
    )


@admin.register(UserDevice)
class UserDeviceAdmin(ImportExportModelAdmin):
    resource_class = UserDeviceResource
    list_display = ["user", "mpp_code", "module", "last_updated"]
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "mpp_code",
    )
    list_filter = ["module"]
    actions = [transfer_mpp_code]


class UserOTPAdmin(admin.ModelAdmin):
    list_display = ["phone_number", "otp", "created_at"]
    search_fields = ["phone_number"]


admin.site.register(OTP, UserOTPAdmin)


class ProductRateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "locale",
        "name_translation",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # If the object is being created
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


admin.site.register(ProductRate, ProductRateAdmin)


@admin.register(SahayakIncentives)
class SahayakIncentivesAdmin(ImportExportModelAdmin):
    resource_class = SahayakIncentivesResource

    # Show key summary fields in the list view
    list_display = (
        "user",
        "mcc_code",
        "mpp_code",
        "year",
        "month",
        "opening",
        "milk_incentive",
        "other_incentive",
        "payable",
        "closing",
    )

    # Enable searching across related user & code/name fields
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "mcc_code",
        "mcc_name",
        "mpp_code",
        "mpp_name",
    )

    # Filters on the right-hand sidebar
    list_filter = (
        "year",
        "month",
        "mcc_code",
        "mpp_code",
    )

    # Add date hierarchy for quicker drilldown
    date_hierarchy = "created_at" if hasattr(SahayakIncentives, "created_at") else None

    # Keep related user info inline editable
    autocomplete_fields = ("user",)

    # Make list view more performant on large datasets
    list_select_related = ("user",)

    # Default ordering (newest records first)
    ordering = ("-year", "-month", "user")

    # Optional: group fields in admin form for readability
    fieldsets = (
        (
            "User & Location",
            {"fields": ("user", "mcc_code", "mcc_name", "mpp_code", "mpp_name")},
        ),
        ("Period", {"fields": ("year", "month")}),
        (
            "Incentives & Recovery",
            {
                "fields": (
                    "opening",
                    "milk_qty",
                    "milk_incentive",
                    "cf_incentive",
                    "mm_incentive",
                    "other_incentive",
                    "tds",
                    "tds_amt",
                    "cda_recovery",
                    "asset_recovery",
                    "additional_data",
                )
            },
        ),
        (
            "Final Calculation",
            {"fields": ("milk_incentive_payable", "payable", "closing")},
        ),
    )

    # Make some fields read-only (e.g. calculated ones)
    readonly_fields = ("milk_incentive_payable", "payable", "closing")


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    """
    Comprehensive admin configuration for News model.
    Optimized for production with proper query optimization and UX.
    """

    # List view configuration
    list_display = [
        "title_with_status",
        "author",
        "module_badge",
        "published_date",
        "view_count",
        "featured_indicator",
        "read_status",
        "quick_actions",
    ]

    list_filter = [
        PublishedFilter,
        RecentNewsFilter,
        "module",
        "is_featured",
        "is_read",
        "author",
        "published_date",
    ]

    search_fields = [
        "title",
        "summary",
        "content",
        "author",
        "tags",
    ]

    list_per_page = 25

    # Make certain fields editable directly in list view
    # list_editable = ["is_featured", "is_read"]

    # Date hierarchy for better navigation
    date_hierarchy = "published_date"

    # Ordering
    ordering = ["-published_date", "-updated_date"]

    # Detail view configuration
    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": ("title", "slug", "author", "module"),
                "description": _("Core article information"),
            },
        ),
        (
            _("Content"),
            {
                "fields": ("summary", "content", "image"),
                "classes": ("wide",),
            },
        ),
        (
            _("Categorization"),
            {
                "fields": ("tags",),
                "description": _("Enter comma-separated tags"),
            },
        ),
        (
            _("Publication Settings"),
            {
                "fields": ("is_published", "is_featured"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Status & Analytics"),
            {
                "fields": ("is_read", "view_count", "published_date", "updated_date"),
                "classes": ("collapse",),
                "description": _("Read-only fields showing article statistics"),
            },
        ),
    )

    # Read-only fields
    readonly_fields = [
        "published_date",
        "updated_date",
        "view_count",
        "slug",  # Auto-generated
    ]

    # Prepopulated fields
    prepopulated_fields = {"slug": ("title",)}

    # Autocomplete fields (if using newer Django versions)
    autocomplete_fields = []

    # Actions
    actions = [
        "make_published",
        "make_draft",
        "mark_as_featured",
        "unmark_featured",
        "mark_as_read",
        "mark_as_unread",
        "duplicate_article",
    ]

    # Save configuration
    save_on_top = True

    # Custom methods for list display
    @admin.display(description=_("Title"), ordering="title")
    def title_with_status(self, obj):
        """Display title with publication status indicator"""
        status_icon = "✅" if obj.is_published else "📝"
        color = "#28a745" if obj.is_published else "#ffc107"
        return format_html(
            '<span style="color: {};">{}</span> <strong>{}</strong>',
            color,
            status_icon,
            obj.title[:50] + ("..." if len(obj.title) > 50 else ""),
        )

    @admin.display(description=_("Module"), ordering="module")
    def module_badge(self, obj):
        """Display module as a colored badge"""
        colors = {
            "member": "#007bff",
            "facilitator": "#28a745",
            "sahayak": "#ffc107",
            "admin": "#dc3545",
            "all": "#6f42c1",
        }
        color = colors.get(obj.module, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_module_display(),
        )

    @admin.display(description=_("Featured"), boolean=True, ordering="is_featured")
    def featured_indicator(self, obj):
        """Show if article is featured"""
        return obj.is_featured

    @admin.display(description=_("Read"), boolean=True, ordering="is_read")
    def read_status(self, obj):
        """Show read status"""
        return obj.is_read

    @admin.display(description=_("Actions"))
    def quick_actions(self, obj):
        """Quick action links"""
        view_url = obj.get_absolute_url()
        return format_html(
            '<a class="button" href="{}" target="_blank">👁 View</a>', view_url
        )

    # Custom admin actions
    @admin.action(description=_("Publish selected articles"))
    def make_published(self, request, queryset):
        """Bulk publish articles"""
        updated = queryset.update(is_published=True)
        self.message_user(
            request,
            _(f"{updated} article(s) successfully published."),
        )

    @admin.action(description=_("Unpublish selected articles"))
    def make_draft(self, request, queryset):
        """Bulk unpublish articles"""
        updated = queryset.update(is_published=False)
        self.message_user(
            request,
            _(f"{updated} article(s) moved to draft."),
        )

    @admin.action(description=_("Mark as featured"))
    def mark_as_featured(self, request, queryset):
        """Mark articles as featured"""
        updated = queryset.update(is_featured=True)
        self.message_user(
            request,
            _(f"{updated} article(s) marked as featured."),
        )

    @admin.action(description=_("Unmark as featured"))
    def unmark_featured(self, request, queryset):
        """Remove featured status"""
        updated = queryset.update(is_featured=False)
        self.message_user(
            request,
            _(f"{updated} article(s) unmarked as featured."),
        )

    @admin.action(description=_("Mark as read"))
    def mark_as_read(self, request, queryset):
        """Mark articles as read"""
        updated = queryset.update(is_read=True)
        self.message_user(
            request,
            _(f"{updated} article(s) marked as read."),
        )

    @admin.action(description=_("Mark as unread"))
    def mark_as_unread(self, request, queryset):
        """Mark articles as unread"""
        updated = queryset.update(is_read=False)
        self.message_user(
            request,
            _(f"{updated} article(s) marked as unread."),
        )

    @admin.action(description=_("Duplicate selected articles"))
    def duplicate_article(self, request, queryset):
        """Duplicate selected articles"""
        count = 0
        for article in queryset:
            article.pk = None
            article.title = f"Copy of {article.title}"
            article.slug = None
            article.is_published = False
            article.save()
            count += 1

        self.message_user(
            request,
            _(f"{count} article(s) duplicated successfully."),
        )

    # Query optimization
    def get_queryset(self, request):
        """Optimize queryset to reduce database queries"""
        qs = super().get_queryset(request)
        # Add select_related/prefetch_related when you have ForeignKey relationships
        return qs

    # Custom form validation
    def save_model(self, request, obj, form, change):
        """Custom save logic"""
        # Auto-set author from current user if not set
        if not change and not obj.author:
            obj.author = request.user.get_full_name() or request.user.username

        super().save_model(request, obj, form, change)

    # Change form template with additional context
    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        """Add extra context to change form"""
        extra_context = extra_context or {}

        if object_id:
            obj = self.get_object(request, object_id)
            extra_context["reading_time"] = obj.reading_time
            extra_context["tags_list"] = obj.get_tags_list()

        return super().changeform_view(
            request, object_id, form_url, extra_context=extra_context
        )

    # # Customize admin site appearance
    # class Media:
    #     css = {
    #         'all': ('admin/css/news_admin.css',)  # Add custom CSS if needed
    #     }
    #     js = ('admin/js/news_admin.js',)  # Add custom JS if needed


@admin.register(RewardedAdTransaction)
class RewardedAdTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "reward_source",
        "reward_amount",
        "is_verified",
        "ad_unit_id",
        "created_at",
    )
    list_filter = ("reward_source", "is_verified", "created_at")
    search_fields = ("user__username", "ad_unit_id", "transaction_token")
    readonly_fields = ("uuid", "created_at", "verified_at", "updated_at")
    date_hierarchy = "created_at"


@admin.register(RewardLedger)
class RewardLedgerAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "transaction_type",
        "amount",
        "balance_after",
        "description",
        "created_at",
    )
    list_filter = ("transaction_type", "created_at")
    search_fields = ("user__username", "description")
    readonly_fields = (
        "uuid",
        "balance_after",
        "created_at",
        "is_finalized",
        "source_ad",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"


@admin.register(RewardWithdrawalRequest)
class RewardWithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "amount",
        "status",
        "transaction_reference",
        "requested_at",
        "processed_at",
    )
    list_filter = ("status", "requested_at")
    search_fields = ("user__username", "transaction_reference")
    readonly_fields = ("requested_at", "processed_at")
    actions = ["approve_selected", "reject_selected"]

    def approve_selected(self, request, queryset):
        from .services.reward_service import RewardService

        count = 0
        for withdrawal in queryset.filter(status="pending"):
            reference = f"ADMIN-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            RewardService.approve_withdrawal(withdrawal, reference_id=reference)
            count += 1
        self.message_user(request, f"{count} withdrawal(s) approved successfully.")

    approve_selected.short_description = "Approve selected withdrawals"

    def reject_selected(self, request, queryset):
        from .services.reward_service import RewardService

        count = 0
        for withdrawal in queryset.filter(status="pending"):
            RewardService.reject_withdrawal(withdrawal, remarks="Admin bulk rejection")
            count += 1
        self.message_user(request, f"{count} withdrawal(s) rejected.")

    reject_selected.short_description = "Reject selected withdrawals"
