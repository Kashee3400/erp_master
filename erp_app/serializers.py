from .models import *
from rest_framework import serializers


class MemberMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberMaster
        fields = '__all__'


class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = ['shift_code','shift_name','shift_short_name']

class BillingMemberMasterSerializer(serializers.ModelSerializer):
    from_shifts = ShiftSerializer(source='from_shift',read_only=True)
    to_shifts = ShiftSerializer(source='to_shift',read_only=True)
    class Meta:
        model = BillingMemberMaster
        fields = ['billing_member_master_code','billing_for','transaction_date','from_date','to_date','from_shifts','to_shifts']


class BillingMemberDetailSerializer(serializers.ModelSerializer):
    billing_member_master = BillingMemberMasterSerializer(source='billing_member_master_code', read_only=True)
    
    class Meta:
        model = BillingMemberDetail
        fields = ['billing_member_detail_code','billing_member_master','member_code','total_qty','balance_qty','qty','avg_fat','avg_snf','amount','share_amount','earning',
                  'deduction','previous_hold','previous_due','hold','due','adjustment','net_payable','transaction_date','bank_code','acc_no','ifsc','upi','payment_mode','status',
                  'receiver','remark']


class MppCollectionAggregationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MppCollectionAggregation
        fields = ['mpp_code','mpp_tr_code','mpp_name','payment_cycle_code','from_date','from_shift','to_date','to_shift','mpp_code','mpp_code',
                  'milk_type_name','milk_quality_type_name','qty','fat','snf','amount','no_of_pouring_days','no_of_pouring_shift']


class MppCollectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = MppCollection
        fields = '__all__'
        depth = 1


class LocalSaleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = LocalSale
        fields = '__all__'
        

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ['warehouse_code','warehouse_name']

class BinLocationSerializer(serializers.ModelSerializer):
    warehouse = WarehouseSerializer(source='warehouse_code',read_only=True)
    class Meta:
        model = BinLocation
        fields = ['bin_location_code','warehouse','bin_location_name']

class ProductGroupSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProductGroup
        fields = ['product_group_code','product_group_name','unit_code']


class ProductSubGroupSerializer(serializers.ModelSerializer):
    product_group = ProductGroupSerializer(source='product_sub_group_code',read_only=True)
    
    class Meta:
        model = ProductSubGroup
        fields = ['product_sub_group_code','product_group','product_sub_group_name']

class ProductCategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProductCategory
        fields = ['product_category_code','product_category_name']

class BrandSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Brand
        fields = ['brand_code','brand_name']

class ProductSerializer(serializers.ModelSerializer):
    product_category = ProductCategorySerializer(source='product_category_code',read_only=True)
    brand = BrandSerializer(source='brand_code',read_only=True)
    
    class Meta:
        model = Product
        fields = ['product_code','product_name','product_category','brand','sku','pack_type',
                  'description','product_type']


class LocalSaleTxnSerializer(serializers.ModelSerializer):
    binlocation = BinLocationSerializer(source='binlocation_code',read_only=True)
    product = ProductSerializer(source='product_code',read_only=True)

    class Meta:
        model = LocalSaleTxn
        fields = '__all__'
