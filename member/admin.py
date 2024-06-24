from django.contrib import admin
from .models import *

# Register your models here.


class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ['user','device']
    
admin.site.register(UserDevice,UserDeviceAdmin)

class UserOTPAdmin(admin.ModelAdmin):
    list_display = ['phone_number','otp','created_at']
    
admin.site.register(OTP,UserOTPAdmin)


from .models import ProductImage
from erp_app.models import Product,Brand,ProductCategory
from .forms import ProductImageForm, BrandImageForm,CategoryImageForm
from django import forms

class ProductImageAdmin(admin.ModelAdmin):
    form = ProductImageForm
    list_display = ('product_code', 'product_name','created_at', 'updated_at')

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'product_code':
            kwargs['queryset'] = Product.objects.all(is_saleable=True)
            return forms.ModelChoiceField(queryset=kwargs['queryset'])
        return super().formfield_for_dbfield(db_field, request, **kwargs)

admin.site.register(ProductImage, ProductImageAdmin)


class BrandImageAdmin(admin.ModelAdmin):
    form = BrandImageForm
    list_display = ('brand_code', 'brand_name','image','created_at', 'updated_at') 
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'brand_code':
            kwargs['queryset'] = Brand.objects.all()
            return forms.ModelChoiceField(queryset=kwargs['queryset'])
        return super().formfield_for_dbfield(db_field, request, **kwargs)

admin.site.register(BrandImage,BrandImageAdmin)

class CategoryImageAdmin(admin.ModelAdmin):
    form = CategoryImageForm
    list_display = ('category_code', 'category_name','image','created_at', 'updated_at') 
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'category_code':
            kwargs['queryset'] = ProductCategory.objects.all()
            return forms.ModelChoiceField(queryset=kwargs['queryset'])
        return super().formfield_for_dbfield(db_field, request, **kwargs)

admin.site.register(CategoryImage,CategoryImageAdmin)
