from django.contrib import admin
from django.apps import apps
from django.contrib import admin
from django.utils.translation import gettext_lazy
from .models import *
from django.contrib.auth.admin import UserAdmin

app_name = 'erp_app'
app_models = apps.get_app_config(app_name).get_models()


# for model in app_models:
#     search_fields = [field.name for field in model._meta.fields if isinstance(field, (models.CharField, models.TextField))]
#     admin_class_attrs = {
#         '__module__': model.__module__,
#         'list_display': [field.name for field in model._meta.fields],
#         'search_fields': search_fields,
#     }
#     admin_class = type(f'{model.__name__}Admin', (admin.ModelAdmin,), admin_class_attrs)
    
#     admin.site.register(model, admin_class)

class MppAdmin(admin.ModelAdmin):
    list_display = (
        'mpp_code',
        'mpp_short_name',
        'mpp_ex_code',        
        'mpp_name',
        'mpp_type',
        'created_at',
        'updated_at',
    )

    # Define the fields that can be searched
    search_fields = (
        'mpp_code',
        'mpp_short_name',
        'mpp_name',
        'mpp_type',
    )

    # Define the fields that can be filtered
    list_filter = (
        'mpp_type',
        'originating_type',
        'created_at',
        'updated_at',
    )

    # Enable editing of specific fields
    fields = (
        'mpp_code',
        'mpp_ex_code',
        'mpp_short_name',
        'mpp_name',
        'mpp_type',
        'created_at',
        'created_by',
        'updated_at',
        'updated_by',
    )

    # You can also define the readonly fields if needed
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')

# Register the Mpp model with the custom admin class
admin.site.register(Mpp, MppAdmin)

class MccAdmin(admin.ModelAdmin):
    # Define the fields to be displayed in the list view
    list_display = (
        'mcc_code',
        'mcc_name',
        'description',
        'is_active',
        'created_at',
        'updated_at',
    )

    # Define the fields that can be searched
    search_fields = (
        'mcc_code',
        'mcc_name',
        'description',
    )

    # Define the fields that can be filtered
    list_filter = (
        'is_active',
        'originating_type',
        'created_at',
        'updated_at',
    )

    # Enable editing of specific fields
    fields = (
        'mcc_code',
        'mcc_ex_code',
        'mcc_name',
        'description',
        'is_active',
        'created_at',
        'created_by',
        'updated_at',
        'updated_by',
    )

    # You can also define the readonly fields if needed
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')

# Register the Mcc model with the custom admin class
admin.site.register(Mcc, MccAdmin)


class MppCollectionAggregationAdmin(admin.ModelAdmin):

    # Define the fields that can be searched
    search_fields = (
        'mcc_code',
        'mcc_name',
        'bmc_code',
        'mpp_code',
        'member_code',
    )

    # Define the fields that can be filtered
    list_filter = (
        'payment_cycle_code',
        'from_date',
        'to_date',
        'created_at',
        'updated_at',
    )

    # Enable editing of specific fields
    list_display = (
        'mcc_code',
        'mcc_tr_code',
        'mcc_name',
        'bmc_code',
        'bmc_tr_code',
        'bmc_name',
        'mpp_code',
        'mpp_tr_code',
        'mpp_name',
        'member_code',
        'member_tr_code',
        'member_name',
        'payment_cycle_code',
        'from_date',
        'from_shift',
        'to_date',
        'to_shift',
        'qty',
        'fat',
        'snf',
        'clr',
        'kg_fat',
        'kg_snf',
        'kg_clr',
        'amount',
        'no_of_pouring_days',
        'no_of_pouring_shift',
        'created_at',
        'created_by',
        'updated_at',
        'updated_by',
        'flg_sentbox_entry',
        'originating_type',
        'originating_org_code',
    )

    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')

# Register the MppCollectionAggregation model
admin.site.register(MppCollectionAggregation, MppCollectionAggregationAdmin)

class MppCollectionAggregationWithoutMilktypeAdmin(admin.ModelAdmin):

    search_fields = (
        'company_code',
        'company_name',
        'plant_code',
        'mcc_code',
        'bmc_code',
        'mpp_code',
        'member_code',
        'payment_cycle_code',
    )

    list_filter = (
        'payment_cycle_code',
        'from_date',
        'to_date',
        'created_at',
        'updated_at',
    )

    list_display = (
        'company_code',
        'company_name',
        'plant_code',
        'plant_tr_code',
        'plant_name',
        'mcc_code',
        'mcc_tr_code',
        'mcc_name',
        'bmc_code',
        'bmc_tr_code',
        'bmc_name',
        'mpp_code',
        'mpp_tr_code',
        'mpp_name',
        'member_code',
        'member_tr_code',
        'member_name',
        'payment_cycle_code',
        'from_date',
        'from_shift',
        'to_date',
        'to_shift',
        'qty',
        'fat',
        'snf',
        'clr',
        'kg_fat',
        'kg_snf',
        'kg_clr',
        'amount',
        'no_of_pouring_days',
        'no_of_pouring_shift',
        'created_at',
        'created_by',
        'updated_at',
        'updated_by',
        'flg_sentbox_entry',
        'originating_type',
        'originating_org_code',
        'share_value',
    )

    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')

admin.site.register(MppCollectionAggregationWithoutMilktype, MppCollectionAggregationWithoutMilktypeAdmin)

@admin.register(MemberMaster)
class MemberMasterAdmin(admin.ModelAdmin):
    list_display = [
        'member_code',
        'member_name',
        'member_ex_code',
        'member_middle_name',
        'member_surname', 
        'mobile_no',
        'member_relation',
        'mobile_no',
        'is_active',
        'folio_no',
        'application_no',
        'application_date',
        'created_at',
        ]
    search_fields = ['member_code', 'member_name', 'mobile_no']
    list_filter = ['is_active', 'member_type', 'application_date','created_at']

@admin.register(MppCollectionDateMilkWiseAggregation)
class MppCollectionDateMilkWiseAggregationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in MppCollectionDateMilkWiseAggregation._meta.fields]
    search_fields = ['company_code', 'company_name', 'collection_date']
    list_filter = ['company_code', 'collection_date']
    
@admin.register(MppCollectionDateShiftMilkWiseAggregation)
class MppCollectionDateShiftMilkWiseAggregationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in MppCollectionDateShiftMilkWiseAggregation._meta.fields]
    search_fields = ['company_code', 'company_name', 'collection_date', 'shift_name']
    list_filter = ['company_code', 'collection_date', 'shift_name']

@admin.register(MppCollectionDateShiftWiseAggregation)
class MppCollectionDateShiftWiseAggregationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in MppCollectionDateShiftWiseAggregation._meta.fields]
    search_fields = ['company_code', 'company_name', 'collection_date', 'shift_name']
    list_filter = ['company_code', 'collection_date', 'shift_name']

@admin.register(RmrdCollectionAggregation)
class RmrdCollectionAggregationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in RmrdCollectionAggregation._meta.fields]
    
    search_fields = [
        'company_code', 
        'company_name', 
        'plant_code', 
        'plant_name', 
        'mcc_code', 
        'mcc_name', 
        'bmc_code', 
        'bmc_name', 
        'mpp_code', 
        'mpp_name', 
        'from_shift', 
        'to_shift', 
        'milk_type_name', 
        'milk_quality_type_name', 
        'created_by', 
        'updated_by'
    ]
    
    # Define filters
    list_filter = [
        'company_code', 
        'plant_code', 
        'mcc_code', 
        'bmc_code', 
        'mpp_code', 
        'from_date', 
        'to_date', 
        'payment_cycle_code', 
        'milk_type_code', 
        'milk_quality_type_code', 
        'created_at'
    ]

@admin.register(RmrdMilkCollection)
class RmrdMilkCollectionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in RmrdMilkCollection._meta.fields]
    
    search_fields = [
        'rmrd_milk_collection_code',
        'rmrd_milk_collection_references_code',
        'vehicle_no',
        'module_code',
    ]
    
    list_filter = [
        'collection_date',
        'shift_code',
        'milk_type_code',
        'milk_quality_type_code',
        'created_at',
        'updated_at'
    ]

@admin.register(RmrdMilkCollectionDetail)
class RmrdMilkCollectionDetailAdmin(admin.ModelAdmin):
    list_display = [field.name for field in RmrdMilkCollectionDetail._meta.fields]
    
    search_fields = [
        'own_module_code',
        'own_module_name',
        'module_code',
        'module_name',
        'vehicle_no'
    ]
    
    list_filter = [
        'collection_date',
        'shift_code',
        'milk_type_code',
        'milk_quality_type_code',
    ]

@admin.register(RmrdQualityCollection)
class RmrdQualityCollectionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in RmrdQualityCollection._meta.fields]
    
    search_fields = [
        'rmrd_quality_collection_code',
        'own_module_code',
        'own_module_name',
        'originating_org_code',
    ]
    
    list_filter = [
        'collection_date',
        'shift_code',
        'dock_no',
        'is_quality_auto',
        'is_merge',
        'created_at',
        'updated_at'
    ]

@admin.register(CdaAggregation)
class CdaAggregationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CdaAggregation._meta.get_fields()]
    
    search_fields = [
        'mcc_code',
        'mcc_name', 
        'mpp_code',
        'mpp_name',
        ]

    list_filter = [
        'company_code', 
        'plant_code', 
        'shift', 
    ]

    ordering = ['collection_date']

@admin.register(CdaAggregationDateshiftWiseMilktype)
class CdaAggregationDateshiftWiseMilktypeAdmin(admin.ModelAdmin):
    # Display all fields in the list view
    list_display = [field.name for field in CdaAggregationDateshiftWiseMilktype._meta.get_fields()]
    
    # Add search functionality on certain fields
    search_fields = [
        'company_code', 
        'company_name', 
        'plant_code', 
        'plant_tr_code', 
        'plant_name', 
        'mcc_code', 
        'mcc_name', 
        'bmc_code', 
        'mpp_code', 
        'mpp_name', 
        'shift', 
        'milk_type_name', 
        'milk_quality_type_name',
    ]

    list_filter = [
        'shift', 
        'milk_type_code', 
        'milk_quality_type_code', 
    ]

    ordering = ['collection_date']  # Order by collection date by default

@admin.register(CdaAggregationDateshiftWiseMilktypeRealTime)
class CdaAggregationDateshiftWiseMilktypeRealTimeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CdaAggregationDateshiftWiseMilktypeRealTime._meta.get_fields()]
    
    search_fields = [
        'mcc_code', 
        'mcc_name', 
        'bmc_code', 
        'mpp_code', 
        'mpp_name', 
        'shift', 
        'milk_type_name', 
        'milk_quality_type_name',
    ]

    list_filter = [
        'shift', 
        'milk_type_code', 
        'milk_quality_type_code', 
    ]

    ordering = ['collection_date']


@admin.register(CdaAggregationDateshiftWiseWithoutMilktypeRealTime)
class CdaAggregationDateshiftWiseWithoutMilktypeRealTimeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CdaAggregationDateshiftWiseWithoutMilktypeRealTime._meta.get_fields()]
    
    search_fields = [
        'company_code', 
        'company_name', 
        'plant_code', 
        'plant_tr_code', 
        'plant_name', 
        'mcc_code', 
        'mcc_name', 
        'bmc_code', 
        'bmc_name', 
        'mpp_code', 
        'mpp_name', 
        'shift',
    ]

    list_filter = [
        'company_code', 
        'plant_code', 
        'shift', 
    ]

    ordering = ['collection_date'] 

@admin.register(CdaAggregationDaywiseMilktype)
class CdaAggregationDaywiseMilktypeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CdaAggregationDaywiseMilktype._meta.get_fields()]

    search_fields = [
        'mcc_code', 
        'mcc_name', 
        'bmc_code', 
        'bmc_name', 
        'mpp_code', 
        'mpp_name', 
    ]

    list_filter = [
        'company_code', 
        'plant_code', 
        'milk_type_code', 
        'milk_quality_type_code', 
    ]

    ordering = ['collection_date']


@admin.register(CdaAggregationPaymentCycleWiseMilktype)
class CdaAggregationPaymentCycleWiseMilktypeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CdaAggregationPaymentCycleWiseMilktype._meta.get_fields()]

    search_fields = [
        'mcc_code', 
        'mcc_name', 
        'bmc_code', 
        'bmc_name', 
        'mpp_code', 
        'mpp_name', 
    ]

    # Add filter functionality
    list_filter = [
        'payment_cycle_code', 
        'milk_type_code', 
        'milk_quality_type_code', 
    ]

    ordering = ['from_date']
