from django.contrib import admin
from .models import *
# from .models import ProductImage
# from erp_app.models import Product,Brand,ProductCategory
# from .forms import ProductImageForm, BrandImageForm,CategoryImageForm,Warehouse,BinLocation
from django import forms
import openpyxl
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import admin, messages
# from .forms import ExcelUploadForm, ProductStockOpeningForm
from django.http import HttpResponse

# Register your models here.


class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ['user','device']
    
admin.site.register(UserDevice,UserDeviceAdmin)

class UserOTPAdmin(admin.ModelAdmin):
    list_display = ['phone_number','otp','created_at']
    
admin.site.register(OTP,UserOTPAdmin)

# class ProductImageAdmin(admin.ModelAdmin):
#     form = ProductImageForm
#     list_display = ('product_code', 'product_name','created_at', 'updated_at')

#     def formfield_for_dbfield(self, db_field, request, **kwargs):
#         if db_field.name == 'product_code':
#             kwargs['queryset'] = Product.objects.all(is_saleable=True)
#             return forms.ModelChoiceField(queryset=kwargs['queryset'])
#         return super().formfield_for_dbfield(db_field, request, **kwargs)

# admin.site.register(ProductImage, ProductImageAdmin)


# class BrandImageAdmin(admin.ModelAdmin):
#     form = BrandImageForm
#     list_display = ('brand_code', 'brand_name','image','created_at', 'updated_at') 
    
#     def formfield_for_dbfield(self, db_field, request, **kwargs):
#         if db_field.name == 'brand_code':
#             kwargs['queryset'] = Brand.objects.all()
#             return forms.ModelChoiceField(queryset=kwargs['queryset'])
#         return super().formfield_for_dbfield(db_field, request, **kwargs)

# admin.site.register(BrandImage,BrandImageAdmin)

# class CategoryImageAdmin(admin.ModelAdmin):
#     form = CategoryImageForm
#     list_display = ('category_code', 'category_name','image','created_at', 'updated_at') 
    
#     def formfield_for_dbfield(self, db_field, request, **kwargs):
#         if db_field.name == 'category_code':
#             kwargs['queryset'] = ProductCategory.objects.all()
#             return forms.ModelChoiceField(queryset=kwargs['queryset'])
#         return super().formfield_for_dbfield(db_field, request, **kwargs)

# admin.site.register(CategoryImage,CategoryImageAdmin)

# from .forms import ProductStockOpeningForm

# class ProductStockOpeningAdmin(admin.ModelAdmin):
#     form = ProductStockOpeningForm
#     list_display = ('product_stock_opening_code', 'product_name','qty','as_on_date', 'warehouse_code','warehouse_name','bin_location_code','bin_location_name','created_by','created_at','updated_at','updated_by') 

#     def save_model(self, request, obj, form, change):
#         if not obj.pk:  # Only set created_by during the first save
#             obj.created_by = request.user
#         obj.save()

# admin.site.register(ProductStockOpening, ProductStockOpeningAdmin)


# class ProductStockOpeningAdmin(admin.ModelAdmin):
#     form = ProductStockOpeningForm
#     change_list_template = 'admin/erp_app/productstockopening/change_list.html'  # Specify the custom template

#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('upload-excel/', self.admin_site.admin_view(self.upload_excel), name='upload_excel'),
#             path('download-excel-format/', self.admin_site.admin_view(self.download_excel_format), name='download_excel_format'),
#         ]
#         return custom_urls + urls
    
#     def download_excel_format(self,request):
#         # Create a workbook and a worksheet
#         wb = openpyxl.Workbook()
#         ws = wb.active
#         ws.title = "Product Stock Opening"
        
#         # Define the header
#         headers = ["Product Code", "Warehouse Code", "Bin Location Code", "Quantity", "As On Date"]
#         ws.append(headers)
        
#         # Set the response headers
#         response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#         response['Content-Disposition'] = 'attachment; filename=product_stock_opening_format.xlsx'
        
#         # Save the workbook to the response
#         wb.save(response)
        
#         return response

#     def upload_excel(self, request):
#         if request.method == 'POST':
#             form = ExcelUploadForm(request.POST, request.FILES)
#             if form.is_valid():
#                 excel_file = request.FILES['excel_file']
#                 wb = openpyxl.load_workbook(excel_file)
#                 sheet = wb.active
                
#                 for row in sheet.iter_rows(min_row=2, values_only=True):
#                     product_code_value = row[0]
#                     warehouse_code_value = row[1]
#                     bin_location_code_value = row[2]
#                     qty_value = row[3]
#                     as_on_date_value = row[4]

#                     try:
#                         product = Product.objects.get(product_code=product_code_value)
#                         warehouse = Warehouse.objects.get(warehouse_code=warehouse_code_value)
#                         bin_location = BinLocation.objects.get(bin_location_code=bin_location_code_value)

#                         ProductStockOpening.objects.create(
#                             product_code=product_code_value,
#                             product_name=product.product_name,
#                             warehouse_code=warehouse_code_value,
#                             warehouse_name=warehouse.warehouse_name,
#                             bin_location_code=bin_location_code_value,
#                             bin_location_name=bin_location.bin_location_name,
#                             qty=qty_value,
#                             as_on_date=as_on_date_value,
#                             created_by=request.user
#                         )
#                     except Product.DoesNotExist:
#                         messages.error(request, f"Product with code {product_code_value} does not exist.")
#                     except Warehouse.DoesNotExist:
#                         messages.error(request, f"Warehouse with code {warehouse_code_value} does not exist.")
#                     except BinLocation.DoesNotExist:
#                         messages.error(request, f"Bin location with code {bin_location_code_value} does not exist.")
#                     except Exception as e:
#                         messages.error(request, str(e))

#                 messages.success(request, "Excel file has been uploaded and processed.")
#                 return redirect('..')
#         else:
#             form = ExcelUploadForm()

#         context = {
#             'form': form,
#             'title': 'Upload Excel File',
#         }
#         return render(request, 'admin/upload_excel.html', context)

#     def save_model(self, request, obj, form, change):
#         if not obj.pk:  # Only set created_by during the first save
#             obj.created_by = request.user
#         obj.save()

# admin.site.register(ProductStockOpening, ProductStockOpeningAdmin)
