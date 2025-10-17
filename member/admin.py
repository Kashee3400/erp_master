# admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from import_export.admin import ImportExportModelAdmin
from .resources import SahayakIncentivesResource, UserResource, UserDeviceResource
from .models import *
from facilitator.models.user_profile_model import UserProfile

# Get the user model
User = get_user_model()

# Unregister the existing User admin if it’s already registered
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(ImportExportModelAdmin, DefaultUserAdmin):
    resource_class = UserResource
    list_display = ("username", "email", "first_name", "last_name", "is_staff")


from django.db import transaction


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


@admin.register(SahayakFeedback)
class SahayakFeedbackAdmin(ImportExportModelAdmin):
    list_display = (
        "feedback_id",
        "sender",
        "mpp_code",
        "status",
        "created_at",
        "resolved_at",
        "updated_at",
    )
    search_fields = (
        "feedback_id",
        "sender__username",
        "sender__first_name",
        "sender_last_name",
    )


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "module", "published_date", "is_published")
    list_filter = ("is_published", "published_date", "module")
    search_fields = ("title", "author", "tags")
    prepopulated_fields = {"slug": ("title",)}
