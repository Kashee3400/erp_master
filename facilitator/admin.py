from django.contrib import admin

from .models.facilitator_model import AssignedMppToFacilitator,ApiKey
from .forms.base_form import AssignedMppToFacilitatorForm

@admin.register(AssignedMppToFacilitator)
class AssignedMppToFacilitatorAdmin(admin.ModelAdmin):
    form = AssignedMppToFacilitatorForm
    list_display = ('sahayak','mpp_code','mpp_ex_code', 'mpp_name', 'mpp_type', 'mpp_opening_date', 'created_at', 'updated_at')
    search_fields = ('mpp_ex_code', 'mpp_name', 'mpp_short_name')
    list_filter = ('mpp_type', 'mpp_opening_date', 'created_at')
    ordering = ('-created_at',)

    def get_fields(self, request, obj=None):
        """
        Only show the 'mpp' field in the form.
        """
        return ['mpp','sahayak']

@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created_at', 'expires_at', 'is_active', 'description')
    search_fields = ('key', 'user__username')
    list_filter = ('is_active', 'expires_at')
