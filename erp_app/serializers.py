from .models import (
    MemberMaster,
    MemberHierarchyView,
    Shift,
    Mcc,
    Mpp,
    Product,
    ProductCategory,
    Brand,
    BillingMemberMaster,
    BillingMemberDetail,
    MilkType,
    MppCollectionAggregation,
    MppCollection,
    LocalSale,
    LocalSaleTxn,
    BinLocation,
    ProductGroup,
    ProductSubGroup,
    MppCollectionReferences,
    MilkQualityType,
    MemberShareFinalInfo,
    Warehouse,
    CdaAggregation,
    MemberSahayakBankDetail,
    Bank,Branch
)

from rest_framework import serializers


class MemberMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = MemberMaster
        fields = "__all__"

class BankSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Bank
        fields = "__all__"

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = "__all__"
    
class MemberBankSerializer(serializers.ModelSerializer):
    bank = BankSerializer()
    branch = BranchSerializer()
    class Meta:
        model = MemberSahayakBankDetail
        fields = "__all__"

class MccSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mcc
        fields = ("mcc_code", "mcc_ex_code", "mcc_name", "is_active")


class MppSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mpp
        fields = ("mpp_code", "mpp_ex_code", "mpp_name")

class MemberProfileSerializer(serializers.ModelSerializer):
    mcc_name = serializers.SerializerMethodField()
    mcc_tr_code = serializers.SerializerMethodField()
    mpp_name = serializers.SerializerMethodField()
    mpp_tr_code = serializers.SerializerMethodField()

    class Meta:
        model = MemberHierarchyView
        fields = (
            "mcc_code",
            "mcc_tr_code",
            "mcc_name",
            "mpp_code",
            "mpp_tr_code",
            "mpp_name",
            "member_code",
            "member_tr_code",
            "member_name",
            "member_middle_name",
            "member_surname",
            "gender",
            "mobile_no",
            "member_type",
            "caste_category",
            "birth_date",
            "age",
            "is_active",
            "wef_date",
            "is_default",
            "created_at",
            "folio_no",
            "application_no",
            "application_date",
            "member_master_relation",
            "ex_member_code",
        )

    def get_mcc_name(self, obj):
        mcc = Mcc.objects.filter(mcc_code=obj.mcc_code).last()
        return mcc.mcc_name if mcc else "-"

    def get_mcc_tr_code(self, obj):
        mcc = Mcc.objects.filter(mcc_code=obj.mcc_code).last()
        return mcc.mcc_ex_code if mcc else "-"

    def get_mpp_name(self, obj):
        mpp = Mpp.objects.filter(mpp_code=obj.mpp_code).last()
        return mpp.mpp_name if mpp else "-"

    def get_mpp_tr_code(self, obj):
        mpp = Mpp.objects.filter(mpp_code=obj.mpp_code).last()
        return mpp.mpp_ex_code if mpp else "-"

class ShiftSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shift
        fields = ["shift_code", "shift_name", "shift_short_name"]


class BillingMemberMasterSerializer(serializers.ModelSerializer):
    from_shifts = ShiftSerializer(source="from_shift", read_only=True)
    to_shifts = ShiftSerializer(source="to_shift", read_only=True)

    class Meta:
        model = BillingMemberMaster
        fields = [
            "billing_member_master_code",
            "billing_for",
            "transaction_date",
            "from_date",
            "to_date",
            "from_shifts",
            "to_shifts",
        ]


class BillingMemberDetailSerializer(serializers.ModelSerializer):
    billing_member_master = BillingMemberMasterSerializer(
        source="billing_member_master_code", read_only=True
    )

    class Meta:
        model = BillingMemberDetail
        fields = [
            "billing_member_detail_code",
            "billing_member_master",
            "member_code",
            "total_qty",
            "balance_qty",
            "qty",
            "avg_fat",
            "avg_snf",
            "amount",
            "share_amount",
            "earning",
            "deduction",
            "previous_hold",
            "previous_due",
            "hold",
            "due",
            "adjustment",
            "net_payable",
            "transaction_date",
            "bank_code",
            "acc_no",
            "ifsc",
            "upi",
            "payment_mode",
            "status",
        ]


class MppCollectionAggregationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MppCollectionAggregation
        fields = [
            "mpp_tr_code",
            "mpp_name",
            "payment_cycle_code",
            "from_date",
            "from_shift",
            "to_date",
            "to_shift",
            "mpp_code",
            "milk_type_name",
            "milk_quality_type_name",
            "qty",
            "fat",
            "snf",
            "amount",
            "no_of_pouring_days",
            "no_of_pouring_shift",
        ]


class MilkTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = MilkType
        fields = [
            "milk_type_code",
            "milk_type_name",
            "milk_type_short_name",
            "is_active",
            "is_milch",
        ]


class MilkQualityTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = MilkQualityType
        fields = ["milk_quality_type_code", "milk_quality_type_name", "is_active"]


class MppCollectionReferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MppCollectionReferences
        fields = [
            "mpp_collection_references_code",
            "company_code",
            "collection_point_code",
            "collection_date",
            "purchase_rate_code",
            "version_no",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
            "flg_sentbox_entry",
            "originating_type",
            "originating_org_code",
            "recalculate_purchase_rate_code",
            "uuid",
            "device_id",
            "received_timestamp",
            "mpp_code",
            "shift_code",
        ]


class MppCollectionSerializer(serializers.ModelSerializer):
    shift = ShiftSerializer(source="shift_code", read_only=True)
    milk_type = MilkTypeSerializer(source="milk_type_code", read_only=True)
    milk_quality_type = MilkQualityTypeSerializer(
        source="milk_quality_type_code", read_only=True
    )
    mpp_collection_references_code = serializers.SerializerMethodField()

    class Meta:
        model = MppCollection
        fields = [
            "member_code",
            "collection_date",
            "shift",
            "milk_type",
            "milk_quality_type",
            "sampleno",
            "qty",
            "fat",
            "snf",
            "rate",
            "amount",
            "mpp_collection_code",
            "mpp_collection_references_code",
        ]
        depth = 1

    def get_mpp_collection_references_code(self, obj):
        return obj.references.mpp_collection_references_code


class LocalSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalSale
        fields = "__all__"


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ["warehouse_code", "warehouse_name"]


class BinLocationSerializer(serializers.ModelSerializer):
    warehouse = WarehouseSerializer(source="warehouse_code", read_only=True)

    class Meta:
        model = BinLocation
        fields = ["bin_location_code", "warehouse", "bin_location_name"]


class ProductGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductGroup
        fields = ["product_group_code", "product_group_name", "unit_code"]


class ProductSubGroupSerializer(serializers.ModelSerializer):
    product_group = ProductGroupSerializer(
        source="product_sub_group_code", read_only=True
    )

    class Meta:
        model = ProductSubGroup
        fields = ["product_sub_group_code", "product_group", "product_sub_group_name"]


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ["product_category_code", "product_category_name"]


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["brand_code", "brand_name"]


class ProductSerializer(serializers.ModelSerializer):
    product_category = ProductCategorySerializer(
        source="product_category_code", read_only=True
    )
    brand = BrandSerializer(source="brand_code", read_only=True)

    class Meta:
        model = Product
        fields = [
            "product_code",
            "product_name",
            "product_category",
            "brand",
            "sku",
            "pack_type",
            "description",
            "product_type",
            "standard_rate",
        ]


class LocalSaleTxnSerializer(serializers.ModelSerializer):
    binlocation = BinLocationSerializer(source="binlocation_code", read_only=True)
    product = ProductSerializer(source="product_code", read_only=True)
    local_sale_code = serializers.PrimaryKeyRelatedField(
        queryset=LocalSale.objects.all()
    )
    binlocation_code = serializers.PrimaryKeyRelatedField(
        queryset=BinLocation.objects.all()
    )
    product_code = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    warehouse_code = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all()
    )

    class Meta:
        model = LocalSaleTxn
        fields = (
            "local_sale_txn_code",
            "local_sale_code",
            "binlocation_code",
            "product_code",
            "warehouse_code",
            "binlocation",
            "product",
            "qty",
            "rate",
            "amount",
            "discount_type",
            "discount_type_value",
            "discount_amount",
            "tax_code",
            "tax_amount",
            "net_amount",
            "inventory_item_value",
            "remarks",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
            "originating_org_code",
            "flg_sentbox_entry",
            "originating_type",
        )


class MemberShareFinalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberShareFinalInfo
        fields = ["no_of_share", "issue_date", "certificate_no"]


class CdaAggregationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CdaAggregation
        fields = "__all__"

    def validate(self, data):
        return data


class MemberHierarchyViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberHierarchyView
        fields = (
            "member_code",
            "member_tr_code",
            "member_name",
            "member_master_relation",
            "member_middle_name",
            "member_surname",
            "mobile_no",
            "age",
            "is_active",
            "folio_no",
            "created_at",
        )
