# admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from import_export.admin import ImportExportModelAdmin
from .resources import SahayakIncentivesResource, UserResource,UserDeviceResource
from .models import *

# Get the user model
User = get_user_model()

# Unregister the existing User admin if it’s already registered
admin.site.unregister(User)

@admin.register(User)
class UserAdmin(ImportExportModelAdmin,DefaultUserAdmin):
    resource_class = UserResource
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')

@admin.register(UserDevice)
class UserDeviceAdmin(ImportExportModelAdmin):
    resource_class = UserDeviceResource
    list_display = ['user','mpp_code','module','last_updated']
    search_fields = ("user__username","user__first_name","user__last_name","mpp_code")
    list_filter = ['module']
    
class UserOTPAdmin(admin.ModelAdmin):
    list_display = ['phone_number','otp','created_at']
    
admin.site.register(OTP,UserOTPAdmin)


class ProductRateAdmin(admin.ModelAdmin):
    list_display = ('name', 'price','locale','name_translation','created_at', 'updated_at', 'created_by', 'updated_by')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')

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
        ("User & Location", {
            "fields": ("user", "mcc_code", "mcc_name", "mpp_code", "mpp_name")
        }),
        ("Period", {
            "fields": ("year", "month")
        }),
        ("Incentives & Recovery", {
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
            )
        }),
        ("Final Calculation", {
            "fields": ("milk_incentive_payable", "payable", "closing")
        }),
    )

    # Make some fields read-only (e.g. calculated ones)
    readonly_fields = ("milk_incentive_payable", "payable", "closing")


@admin.register(SahayakFeedback)
class SahayakFeedbackAdmin(ImportExportModelAdmin):
    list_display = ('feedback_id','sender','mpp_code','status','created_at','resolved_at','updated_at')
    search_fields = ('feedback_id','sender__username','sender__first_name','sender_last_name')
    

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'author','module', 'published_date', 'is_published')
    list_filter = ('is_published', 'published_date','module')
    search_fields = ('title', 'author', 'tags')
    prepopulated_fields = {'slug': ('title',)}