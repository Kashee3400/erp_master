from django.contrib import admin
from .models.models import *
from django.apps import apps

app_name = 'veterinary'
app_models = apps.get_app_config(app_name).get_models()


for model in app_models:
    if model.__name__ == 'Member':
        continue
    search_fields = [field.name for field in model._meta.fields if isinstance(field, (models.CharField, models.TextField))]

    # Create admin class attributes
    admin_class_attrs = {
        '__module__': model.__module__,
        'list_display': [field.name for field in model._meta.fields],
        'search_fields': search_fields,
    }
    
    # Create admin class dynamically
    admin_class = type(f'{model.__name__}Admin', (admin.ModelAdmin,), admin_class_attrs)
    
    # Register admin class
    admin.site.register(model, admin_class)


# class AnimalTypeAdmin(admin.ModelAdmin):
#     list_display = ['animal_type', 'created_at']
    
# admin.site.register(AnimalType,AnimalTypeAdmin)

# class BankAccountAdmin(admin.ModelAdmin):
#     list_display = ['user','account_holder_name','account_number','bank_name','bank_short_name','branch_name','IFSC_code']

# admin.site.register(BankAccount,BankAccountAdmin)

# class AnimalBreedAdmin(admin.ModelAdmin):
#     list_display = ['animal_type','breed','created_at']
    
# admin.site.register(AnimalBreed,AnimalBreedAdmin)