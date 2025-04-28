from django.contrib import admin
from .models.facilitator_model import AssignedMppToFacilitator,ApiKey
from .models.vcg_model import VCGMeeting,VCGroup
from .forms.base_form import AssignedMppToFacilitatorForm
from import_export.admin import ImportExportModelAdmin

class AssignedMppToFacilitatorAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    # form = AssignedMppToFacilitatorForm
    list_display = (
        'mpp_code',
        'mpp_short_name',
        'mpp_ex_code',
        'mpp_name',
        'mpp_type',
        'sahayak',
        'created_at',
        'updated_at',
    )
    # list_editable = ["sahayak"]
    search_fields = (
        'mpp_code',
        'mpp_ex_code',
        'mpp_name',
    )

    list_filter = (
        'sahayak',
        'mpp_type',
        'created_at',
        'updated_at',
    )
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(AssignedMppToFacilitator,AssignedMppToFacilitatorAdmin)


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created_at', 'expires_at', 'is_active', 'description')
    search_fields = ('key', 'user__username')
    list_filter = ('is_active', 'expires_at')


from django.utils.translation import gettext_lazy as _

@admin.register(VCGMeeting)
class VCGMeetingAdmin(admin.ModelAdmin):
    list_display = ("user","mpp_name", "mpp_code", "status", "started_at", "completed_at", "synced")
    list_filter = ("status", "synced", "started_at")
    search_fields = ("mpp_name", "mpp_code", "mpp_ex_code")
    ordering = ("-started_at",)

    # Read-only fields
    readonly_fields = ("meeting_id", "started_at", "completed_at")

    # Fieldsets for structured display in admin
    fieldsets = (
        (_("Meeting Details"), {
            "fields": ("meeting_id","user", "mpp_name", "mpp_code", "mpp_ex_code", "status")
        }),
        (_("Location Details"), {
            "fields": ("lat", "lon"),
            "classes": ("collapse",),  # Collapsible section
        }),
        (_("Timestamps"), {
            "fields": ("started_at", "completed_at"),
        }),
        (_("Sync Information"), {
            "fields": ("synced",),
        }),
    )

    # # Customizing the Django admin interface
    # def has_add_permission(self, request):
    #     """Prevent adding new meetings from Django Admin."""
    #     return False  # Meetings should be added via API or another process

    # def has_delete_permission(self, request, obj=None):
    #     """Prevent deletion of meetings from Django Admin."""
    #     return False  # Prevent accidental deletion of meeting records



# Admin Configuration
class VCGroupAdmin(ImportExportModelAdmin):
    list_display = ('member_name', 'whatsapp_num', 'member_code', 'created_at')
    search_fields = ('member_name', 'whatsapp_num', 'member_code')
    list_filter = ('created_at', 'updated_at')

admin.site.register(VCGroup, VCGroupAdmin)
