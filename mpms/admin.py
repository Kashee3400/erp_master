from django.apps import apps
from django.contrib import admin
from django.utils.translation import gettext_lazy
from django.contrib.auth.admin import UserAdmin
from .models import *

from member.models import *


class TblFarmerAdmin(admin.ModelAdmin):
    list_display = [
        'farmerid',
        'farmercode',
        'firstname',
        'phonenumber',
        'gender',
        'birthdate',
        'caste',
        'mccid',
        'city',
        'villageid',
        'uniquemembercode',
    ]
    
    search_fields = [
        'phonenumber',
        'farmerid',
        'firstname',
        'lastname',
        'middlename',
        'farmercode',
        
    ]
admin.site.register(Tblfarmer,TblFarmerAdmin)

from datetime import date
class TblFarmerCollectionAdmin(admin.ModelAdmin):
    list_display = ['rowid', 'dumpdate', 'dumptime', 'shift', 'farmerid','soccode','member_other_code',
                    'weight', 'fat', 'lr', 'snf', 'totalamount']
    
    search_fields = ['farmerid__firstname', 'farmerid__lastname', 'member_other_code']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(dumpdate__range=[date(2024, 4, 1),date(2024, 4, 20)],isapproved=True,isdelete=False)

admin.site.register(Tblfarmercollection, TblFarmerCollectionAdmin)



class TblmccAdmin(admin.ModelAdmin):
    list_display = ['mccid','mccname','validfrom','districtid','stateid',
                    'countryid','contactperson','mcccode','isactive']
    
    search_fields = ['mccname','mcccode']
    
    list_filter = ['isactive']
    
admin.site.register(Tblmcc,TblmccAdmin)


class TblmmilkAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Tblmmilk._meta.fields]

admin.site.register(Tblmmilk, TblmmilkAdmin)