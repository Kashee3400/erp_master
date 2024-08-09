from django.contrib import admin
from django.apps import apps
from django.contrib import admin
from django.utils.translation import gettext_lazy
from .models import *
from django.contrib.auth.admin import UserAdmin

app_name = 'erp_app'
app_models = apps.get_app_config(app_name).get_models()


for model in app_models:
    search_fields = [field.name for field in model._meta.fields if isinstance(field, (models.CharField, models.TextField))]
    admin_class_attrs = {
        '__module__': model.__module__,
        'list_display': [field.name for field in model._meta.fields],
        'search_fields': search_fields,
    }
    admin_class = type(f'{model.__name__}Admin', (admin.ModelAdmin,), admin_class_attrs)
    
    admin.site.register(model, admin_class)

