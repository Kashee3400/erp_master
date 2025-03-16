from django.contrib import admin
from .models.facilitator_model import AssignedMppToFacilitator,ApiKey
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
