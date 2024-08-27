from django.contrib import admin
from .models import *
from django import forms
import openpyxl
from django.shortcuts import render, redirect
from django.urls import path

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group

from unfold.admin import ModelAdmin


admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    pass


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass

class UserDeviceAdmin(ModelAdmin):
    list_display = ['user','device']
    
admin.site.register(UserDevice,UserDeviceAdmin)

class UserOTPAdmin(ModelAdmin):
    list_display = ['phone_number','otp','created_at']
    
admin.site.register(OTP,UserOTPAdmin)
