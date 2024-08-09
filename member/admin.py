from django.contrib import admin
from .models import *
from django import forms
import openpyxl
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import admin

# Register your models here.


class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ['user','device']
    
admin.site.register(UserDevice,UserDeviceAdmin)

class UserOTPAdmin(admin.ModelAdmin):
    list_display = ['phone_number','otp','created_at']
    
admin.site.register(OTP,UserOTPAdmin)
