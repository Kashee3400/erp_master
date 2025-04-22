from django.contrib import admin
from django.apps import apps
from .models import *
from import_export.admin import ImportExportModelAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from datetime import datetime

app_name = 'erp_app'
app_models = apps.get_app_config(app_name).get_models()


class MppAdmin(ImportExportModelAdmin, admin.ModelAdmin):
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
        'mpp_ex_code',
        'mpp_name',
    )

    # Enable editing of specific fields
    fields = (
        'mpp_code',
        'mpp_ex_code',
        'mpp_short_name',
        'mpp_name',
        'mpp_type',
    )

    # Define readonly fields
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
    )

    # Enable editing of specific fields
    fields = (
        'mcc_code',
        'mcc_ex_code',
        'mcc_name',
        'description',
        'is_active',
    )

    # You can also define the readonly fields if needed
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')

# Register the Mcc model with the custom admin class
admin.site.register(Mcc, MccAdmin)

@admin.register(MemberMaster)
class MemberMasterAdmin(admin.ModelAdmin):
    list_display = [
        'member_code',
        'member_name',
        'member_ex_code',
        'member_middle_name',
        'member_surname', 
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

from rangefilter.filters import DateRangeFilter
@admin.register(MppCollection)
class MppCollectionAdmin(admin.ModelAdmin):
    list_display = ["member_code","get_mpp_code","collection_date","shift_code","qty",
                    "fat","snf","rate","amount",
                    ]
    search_fields = ['member_code']
    list_filter = ['shift_code','references__mpp_code',('collection_date', DateRangeFilter)]

    def get_mpp_code(self, obj):
        """Returns the related mpp_code value."""
        if obj.references and obj.references.mpp_code:
            return obj.references.mpp_code.mpp_name
        return "-"

    get_mpp_code.short_description = "MPP Code"
    get_mpp_code.admin_order_field = "references__mpp_code__mpp_code"

    def get_queryset(self, request):
        """Prevents initial data from loading until a filter is applied."""
        qs = super().get_queryset(request)
        if not request.GET:
            return qs.none()
        return qs


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
        'module_code',
    ]
    
    def get_queryset(self, request):
        """Prevents initial data from loading until a filter is applied."""
        qs = super().get_queryset(request)
        if not request.GET:  # If no filters are applied, return an empty queryset
            return qs.none()
        return qs

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
    
    def get_queryset(self, request):
        """Prevents initial data from loading until a filter is applied."""
        qs = super().get_queryset(request)
        if not request.GET:  # If no filters are applied, return an empty queryset
            return qs.none()
        return qs

    
@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('shift_code', 'shift_name', 'shift_short_name', 'shift_at', 'is_active')
    search_fields = ('shift_name', 'shift_short_name', 'shift_code')
    list_filter = ('is_active', 'originating_type')
    ordering = ('shift_code',)


@admin.register(LocalSaleTxn)
class LocalSaleTxnAdmin(admin.ModelAdmin):
    # Dynamically get all fields from the model
    list_display = [field.name for field in LocalSaleTxn._meta.fields]
    search_fields = ["local_sale_code__local_sale_code"]
    list_filter = ['created_at', 'updated_at']  # Add fields to filter by, if applicable
    readonly_fields = ['created_at', 'updated_at']  # Example of read-only fields

    # Optional: Customize display for related fields
    def local_sale_code_display(self, obj):
        return obj.local_sale_code.local_sale_txn_code if obj.local_sale_code else "-"
    local_sale_code_display.short_description = "Local Sale Code"
    
    
@admin.register(LocalSale)
class LocalSaleAdmin(admin.ModelAdmin):
    # Dynamically get all fields from the model
    list_display = [field.name for field in LocalSale._meta.fields]
    search_fields = ["module_code"]
    list_filter = ['local_sale_date', 'transaction_date', 'status']  # Add fields to filter by
    readonly_fields = ['created_at', 'updated_at']  # Example of read-only fields

    # Optional: Customize display for related fields
    def local_sale_code_display(self, obj):
        return obj.local_sale_code
    local_sale_code_display.short_description = "Local Sale Code"
    
    def module_name_display(self, obj):
        return obj.module_name
    module_name_display.short_description = "Module Name"
    
    def status_display(self, obj):
        return obj.status
    status_display.short_description = "Sale Status"

class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_code', 'product_name', 'sku', 'pack_type', 'is_purchase', 'is_saleable', 'created_at']
    search_fields = ['product_name', 'sku', 'brand_code__brand_name']
    list_filter = ['is_saleable', 'is_purchase']
    ordering = ['product_name']

admin.site.register(Product, ProductAdmin)


class MemberHierarchyViewAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = [field.name for field in MemberHierarchyView._meta.fields]
    search_fields = ('member_code',)
    list_filter = ('is_active', 'created_at')

admin.site.register(MemberHierarchyView, MemberHierarchyViewAdmin)

class UnitAdmin(admin.ModelAdmin):
    # List display: specify the fields to be displayed in the list view
    list_display = ('unit_code', 'unit', 'unit_short_name', 'created_at', 'updated_at', 'is_decimal_allow')
    
    # Search functionality: enable search by fields
    search_fields = ('unit', 'unit_short_name', 'created_by', 'updated_by')
    
    # Filtering options: enable filters in the sidebar
    list_filter = ('is_decimal_allow', 'originating_org_code', 'originating_type')
    
    # Allow ordering the records based on certain fields
    ordering = ('unit_code',)
    
    # Enable date-based filtering if needed
    date_hierarchy = 'created_at'

# Register the model along with the UnitAdmin configuration
admin.site.register(Unit, UnitAdmin)


@admin.register(BillingMemberMaster)
class BillingMemberMasterAdmin(admin.ModelAdmin):
    list_display = [field.name for field in BillingMemberMaster._meta.fields]
    search_fields = ['company_code', 'plant_code', 'mcc_code','mpp_code']


@admin.register(BillingMemberDetail)
class BillingMemberDetailAdmin(admin.ModelAdmin):
    list_display = [field.name for field in BillingMemberDetail._meta.fields]
    search_fields = ['billing_member_master_code__billing_member_master_code']
    list_filter = ['transaction_date', 'status', 'payment_mode']

@admin.register(MppDispatchTxn)
class MppDispatchTxnAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ["mpp_dispatch_txn_code","dispatch_qty","fat","snf","rate","amount","created_at"]
    search_fields = ('mpp_dispatch_code__mpp_code',)
    list_filter = ('created_at',)


