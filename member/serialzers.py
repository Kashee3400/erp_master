# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import OTP, ProductRate, SahayakIncentives, SahayakFeedback
from erp_app.models import (
    CdaAggregationDateshiftWiseMilktype,
    Shift,
    MemberMaster,
    LocalSale,
    LocalSaleTxn,
    Unit,
    BillingMemberMaster,
    BillingMemberDetail,
    Bank,
    Mpp,
)
from erp_app.serializers import (
    BinLocationSerializer,
    ProductCategorySerializer,
    BrandSerializer,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["password", "groups", "user_permissions"]


class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = "__all__"


class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ["phone_number"]


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=10)
    otp = serializers.CharField(max_length=6)


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def validate(cls, attrs):
        # Call the parent class method to get the validated data
        data = super().validate(attrs)
        return {
            "status_code": 200,
            "message": "Token successfully obtained",
            "refresh": data["refresh"],
            "access": data["access"],
        }


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRate
        fields = [
            "name",
            "price",
            "price_description",
            "image",
            "locale",
            "name_translation",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]


class MemberMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberMaster
        fields = [
            "url",
            "member_code",
            "member_name",
            "member_ex_code",
            "member_middle_name",
            "member_surname",
            "mobile_no",
            "is_active",
        ]


class LocalSaleSerializer(serializers.ModelSerializer):
    member = serializers.SerializerMethodField()

    class Meta:
        model = LocalSale
        fields = "__all__"

    def get_member(self, obj):
        """
        Fetch the member data from MemberMaster using module_code.
        """
        try:
            member = MemberMaster.objects.get(member_code=obj.module_code)
            return MemberMasterSerializer(member).data
        except MemberMaster.DoesNotExist:
            return None

class DeductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalSale
        fields = ['module_code','local_sale_no']



class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ["unit_code", "unit", "unit_short_name"]


class ERProductSerializer(serializers.ModelSerializer):
    product_category = ProductCategorySerializer(
        source="product_category_code", read_only=True
    )
    brand = BrandSerializer(source="brand_code", read_only=True)
    unit = serializers.SerializerMethodField()

    class Meta:
        from erp_app.models import Product

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
            "informative_price",
            "standard_rate",
            "unit",
        ]

    def get_unit(self, obj):
        try:
            unit = Unit.objects.get(unit_code=obj.unit_code)
            return UnitSerializer(unit).data
        except:
            None


class LocalSaleTxnSerializer(serializers.ModelSerializer):
    binlocation = BinLocationSerializer(source="binlocation_code", read_only=True)
    product = ERProductSerializer(source="product_code", read_only=True)
    local_sale_code = DeductionSerializer(read_only=True)

    class Meta:
        model = LocalSaleTxn
        fields = "__all__"


class CdaAggregationDaywiseMilktypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CdaAggregationDateshiftWiseMilktype
        fields = [
            "id",
            "mcc_code",
            "mcc_tr_code",
            "mcc_name",
            "mpp_code",
            "mpp_tr_code",
            "mpp_name",
            "shift",
            "collection_date",
            "milk_type_code",
            "milk_type_name",
            "milk_quality_type_code",
            "milk_quality_type_name",
            "composite_qty",
            "composite_fat",
            "composite_snf",
            "dispatch_qty",
            "dispatch_fat",
            "dispatch_snf",
            "dispatch_kg_fat",
            "dispatch_kg_snf",
            "dispatch_amount",
            "actual_qty",
            "actual_fat",
            "actual_snf",
            "actual_amount",
        ]


class SahayakIncentivesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SahayakIncentives
        fields = "__all__"


from rest_framework import serializers
from .models import SahayakFeedback


class SahayakFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = SahayakFeedback
        fields = "__all__"
        read_only_fields = [
            "feedback_id",
            "remark",
            "created_at",
            "resolved_at",
            "sender",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["sender"] = request.user
            validated_data["mpp_code"] = request.user.device.mpp_code

        return super().create(validated_data)


from .models import News
from django.utils.timezone import now


class NewsSerializer(serializers.ModelSerializer):
    relative_published_date = serializers.SerializerMethodField()
    verbose_names = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = [
            "id",
            "image",
            "title",
            "content",
            "author",
            "published_date",
            "updated_date",
            "tags",
            "is_published",
            "relative_published_date",
            "is_read",
            "verbose_names",
        ]
        read_only_fields = [
            "id",
            "slug",
            "is_published",
            "updated_date",
            "published_date",
        ]

    def get_relative_published_date(self, obj):
        """Calculate the relative published date."""
        delta = now() - obj.published_date

        if delta.days == 0:
            return "Today"
        elif delta.days == 1:
            return "Yesterday"
        elif delta.days < 7:
            return "This week"
        elif delta.days < 30:
            return "This month"
        else:
            return f"{delta.days} days ago"

    def get_verbose_names(self, obj):
        """Extract verbose names for model fields."""
        verbose_dict = {}
        for field in obj._meta.fields:
            verbose_dict[field.name] = field.verbose_name
        return verbose_dict

    def validate(self, data):
        """Perform validation dynamically."""
        if "published_date" in data and data["published_date"] > now():
            raise serializers.ValidationError(
                {"published_date": "Cannot be in the future."}
            )

        if "content" in data and len(data["content"]) < 50:
            raise serializers.ValidationError(
                {"content": "Content must be at least 50 characters long."}
            )

        return data

    def update(self, instance, validated_data):
        """Dynamically update the fields based on validated data."""
        for field, value in validated_data.items():
            if hasattr(instance, field):
                setattr(instance, field, value)

        instance.save()
        return instance


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = [
            "bank_code",
            "bank_name",
            "checked_ac_no",
            "is_active",
            "nationalized_bank",
            "short_name",
            "ac_no_length",
        ]


class MppSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mpp
        fields = [
            "mpp_code",
            "mpp_ex_code",
            "mpp_short_name",
            "mpp_name",
            "mpp_type",
            "mpp_opening_date",
        ]


class BillingMemberDetailSerializer(serializers.ModelSerializer):
    member = serializers.SerializerMethodField()

    class Meta:
        model = BillingMemberDetail
        fields = [
            "url",
            "billing_member_detail_code",
            "billing_member_master_code",
            "member",
            "total_qty",
            "balance_qty",
            "qty",
            "avg_fat",
            "avg_snf",
            "member_code",
            "member",
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
            "acc_no",
            "ifsc",
            "upi",
            "payment_mode",
            "status",
        ]

    def get_member(self, obj):
        try:
            member = MemberMaster.objects.get(member_code=obj.member_code)
            return MemberMasterSerializer(member, context=self.context).data
        except MemberMaster.DoesNotExist:
            return None

class BillingMemberMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingMemberMaster
        fields = [
            "url",
            "billing_member_master_code",
            "mcc_code",
            "bmc_code",
            "mpp_code",
            "billing_for",
            "transaction_date",
            "from_date",
            "from_shift",
            "to_date",
            "to_shift",
            "payment_cycle",
            "no_of_payable",
            "qty",
            "avg_fat",
            "avg_snf",
            "amount",
            "earning",
            "deduction",
            "net_payable",
            "status",
        ]
