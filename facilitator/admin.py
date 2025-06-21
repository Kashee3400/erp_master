from django.contrib import admin
from .models.facilitator_model import AssignedMppToFacilitator, ApiKey
from .models.vcg_model import (
    VCGMeeting,
    VCGroup,
    ZeroDaysPourerReason,
    ZeroDaysPouringReport,
    MemberComplaintReason,
    MemberComplaintReport,
)
from .models.user_profile_model import UserProfile
from import_export.admin import ImportExportModelAdmin
from .resources import FacilitatorResource, VCGroupResource
from .forms import base_form
from django.utils.translation import gettext_lazy as _



class AssignedMppToFacilitatorAdmin(ImportExportModelAdmin):
    # form = base_form.AssignedMppToFacilitatorForm
    resource_class = FacilitatorResource
    list_display = (
        "facilitator_name",
        "mpp_code",
        "mpp_ex_code",
        "mpp_name",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "mpp_code",
        "mpp_ex_code",
        "mpp_name",
    )
    list_filter = (
        "sahayak",
        "mpp_type",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")

    save_as = True
    save_on_top = True
    actions_on_bottom = True

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["custom_message"] = "🚀 Assign MPPs carefully!"
        return super().changeform_view(request, object_id, form_url, extra_context)

    @admin.display(description="Facilitator")
    def facilitator_name(self, obj):
        if obj.sahayak:
            full_name = f"{obj.sahayak.first_name} {obj.sahayak.last_name}".strip()
            if full_name.strip():
                return full_name
            if obj.sahayak.username:
                return obj.sahayak.username
        return "No Facilitator Assigned"


admin.site.register(AssignedMppToFacilitator, AssignedMppToFacilitatorAdmin)


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "key",
        "created_at",
        "expires_at",
        "is_active",
        "description",
    )
    search_fields = ("key", "user__username")
    list_filter = ("is_active", "expires_at")


@admin.register(VCGMeeting)
class VCGMeetingAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "mpp_name",
        "mpp_code",
        "status",
        "is_deleted",
        "started_at",
        "completed_at",
        "synced",
    )
    list_filter = ("status", "synced", "started_at")
    search_fields = ("mpp_name", "mpp_code", "mpp_ex_code")
    ordering = ("-started_at",)

    # Read-only fields
    readonly_fields = ("meeting_id", "started_at", "completed_at")

    # Fieldsets for structured display in admin
    fieldsets = (
        (
            _("Meeting Details"),
            {
                "fields": (
                    "meeting_id",
                    "user",
                    "mpp_name",
                    "mpp_code",
                    "mpp_ex_code",
                    "status",
                    "is_deleted",
                )
            },
        ),
        (
            _("Location Details"),
            {
                "fields": ("lat", "lon"),
                "classes": ("collapse",),  # Collapsible section
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": ("started_at", "completed_at"),
            },
        ),
        (
            _("Sync Information"),
            {
                "fields": ("synced",),
            },
        ),
    )


# Admin Configuration
class VCGroupAdmin(ImportExportModelAdmin):
    resource_class = VCGroupResource
    list_display = ("member_name", "mpp", "whatsapp_num", "member_code", "created_at")
    search_fields = ("member_name", "whatsapp_num", "member_code", "mpp__mpp_code")
    list_filter = ("mpp", "created_at", "updated_at")


admin.site.register(VCGroup, VCGroupAdmin)

class ZeroDaysReasonAdmin(ImportExportModelAdmin):
    list_display = ("id", "reason", "created_at")
    search_fields = ("reason",)
    list_filter = ("created_at", "updated_at")
    date_hierarchy = "created_at"


admin.site.register(ZeroDaysPourerReason, ZeroDaysReasonAdmin)


class MemberComplaintReasonAdmin(ImportExportModelAdmin):
    list_display = ("id", "reason", "created_at")
    search_fields = ("reason",)
    list_filter = ("created_at", "updated_at")
    date_hierarchy = "created_at"


admin.site.register(MemberComplaintReason, MemberComplaintReasonAdmin)

@admin.register(ZeroDaysPouringReport)
class ZeroDaysPouringReportAdmin(admin.ModelAdmin):
    list_display = ("member_code", "member_name", "reason", "meeting")
    search_fields = ("member_code", "member_name")
    list_filter = ("reason", "meeting")
    date_hierarchy = "meeting__started_at"
    
    fieldsets = (
        ("Member Info", {
            "fields": ("member_code", "member_ex_code", "member_name")
        }),
        ("Details", {
            "fields": ("reason", "meeting")
        }),
    )


@admin.register(MemberComplaintReport)
class MemberComplaintReportAdmin(admin.ModelAdmin):
    list_display = ("member_code", "member_name", "reason", "meeting")
    search_fields = ("member_code", "member_name")
    list_filter = ("reason", "meeting")
    date_hierarchy = "meeting__started_at"
    fieldsets = (
        ("Member Info", {
            "fields": ("member_code", "member_ex_code", "member_name")
        }),
        ("Details", {
            "fields": ("reason", "meeting")
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'designation', 'phone_number', 'is_verified')
    list_filter = ('department', 'is_verified', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number', 'designation')
    readonly_fields = ('created_at', 'updated_at')
