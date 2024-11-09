# admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from import_export.admin import ImportExportModelAdmin
from .resources import SahayakIncentivesResource, UserResource
from .models import *

# Get the user model
User = get_user_model()

# Unregister the existing User admin if it’s already registered
admin.site.unregister(User)

# Register the User model with ImportExportModelAdmin and the default UserAdmin
@admin.register(User)
class UserAdmin(ImportExportModelAdmin, DefaultUserAdmin):
    resource_class = UserResource
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')

class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ['user','device']
    
admin.site.register(UserDevice,UserDeviceAdmin)

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
    list_display = ("user",'mcc_code','mcc_name','mpp_code','mpp_name','month','opening','milk_incentive','other_incentive','payable','closing')
    search_fields = ('user__first_name','user__lastname','user__username','mcc_code','mcc_name','mpp_code','mpp_name','month',)
    