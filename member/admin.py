from django.contrib import admin
from .models import *


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
