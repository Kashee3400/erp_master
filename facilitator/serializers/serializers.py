# serializers.py
from rest_framework import serializers
from django.utils.timezone import now

from erp_app.models import (
    CdaAggregation,
    Shift,
    MemberMaster,
    LocalSale,
    LocalSaleTxn,
    Unit,
    BillingMemberMaster,
    BillingMemberDetail,
    MemberMasterHistory,
    Bank,
    Mpp,
    MemberHierarchyView,
    FacilitatorDashboardSummary
)
from erp_app.serializers import (
    BinLocationSerializer,
    ProductCategorySerializer,
    BrandSerializer,
    MemberHierarchyViewSerializer,
)
from member.models import OTP, SahayakIncentives

from rest_framework import serializers
from ..models.facilitator_model import AssignedMppToFacilitator
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class AssignedMppToFacilitatorSerializer(serializers.ModelSerializer):
    sahayak = serializers.StringRelatedField()

    class Meta:
        model = AssignedMppToFacilitator
        fields = [
            "id",
            "sahayak",
            "mpp_code",
            "mpp_ex_code",
            "mpp_name",
            "mpp_short_name",
            "mpp_type",
            "mpp_logo",
            "mpp_icon",
            "mpp_punch_line",
            "mpp_opening_date",
            "created_at",
            "updated_at",
        ]


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
        fields = [
            "local_sale_code",
            "local_sale_date",
            "module_code",
            "module_name",
            "transaction_date",
            "status",
            "net_amount",
            "round_amount",
            "total_amount",
            "credit_limit",
            "member",
        ]

    def get_member(self, obj):
        """
        Fetch the member data from MemberMaster using module_code.
        """
        try:
            member = MemberHierarchyView.objects.filter(member_code=obj.module_code,is_default=True).last()
            return MemberHierarchyViewSerializer(member, context=self.context).data
        except MemberHierarchyView.DoesNotExist:
            return None


class DeductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalSale
        fields = ["module_code", "local_sale_no"]


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


class DeductionTxnSerializer(serializers.ModelSerializer):
    binlocation = BinLocationSerializer(source="binlocation_code", read_only=True)
    product = ERProductSerializer(source="product_code", read_only=True)
    local_sale_code = DeductionSerializer(read_only=True)

    class Meta:
        model = LocalSaleTxn
        fields = "__all__"


class LocalSaleTxnSerializer(serializers.ModelSerializer):
    product = ERProductSerializer(source="product_code", read_only=True)
    local_sale_code = LocalSaleSerializer(read_only=True)
    class Meta:
        model = LocalSaleTxn
        fields = [
            "local_sale_txn_code",
            "local_sale_code",
            "qty",
            "rate",
            "amount",
            "product",
        ]


class CdaAggregationDaywiseMilktypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CdaAggregation
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
from member.models import SahayakFeedback, News


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
            member = MemberHierarchyView.objects.get(member_code=obj.member_code)
            return MemberHierarchyViewSerializer(member, context=self.context).data
        except MemberHierarchyView.DoesNotExist:
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


class MemberHierarchySerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberHierarchyView
        fields = [
            "mcc_code",
            "bmc_code",
            "mpp_code",
            "member_code",
            "member_tr_code",
            "member_name",
            "member_middle_name",
            "member_surname",
            "gender",
            "mobile_no",
            "caste_category",
            "member_type",
            "is_active",
            "application_date",
            "application_no",
            "member_master_relation",
            "ex_member_code",
        ]


from django.urls import reverse


class TopPourerSerializer(serializers.Serializer):
    member_code = serializers.CharField()
    total_qty = serializers.DecimalField(max_digits=18, decimal_places=2)
    detail_url = serializers.SerializerMethodField()

    def get_detail_url(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(
                reverse("members-detail", args=[obj["member_code"]])
            )
        return reverse("members-detail", args=[obj["member_code"]])


class MonthAssignmentSerializer(serializers.Serializer):
    mpp_code = serializers.CharField()
    month = serializers.CharField()
    milk_collection = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_members = serializers.IntegerField()
    no_of_pourers = serializers.IntegerField()
    pourers_15_days = serializers.IntegerField()
    pourers_25_days = serializers.IntegerField()
    zero_days_pourers = serializers.IntegerField()
    top_pourers = TopPourerSerializer(many=True)


class MemberMasterHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberMasterHistory
        fields = [
            "history_created_at",
            "operation_type",
            "member_code",
            "operation_type",
            "member_code",
            "member_name",
            "member_ex_code",
            "mobile_no",
            "is_active",
        ]

class FacilitatorDashboardSummarySerializer(serializers.ModelSerializer):
    actual_qty = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    actual_fat = serializers.DecimalField(max_digits=5, decimal_places=2, coerce_to_string=False)
    actual_snf = serializers.DecimalField(max_digits=5, decimal_places=2, coerce_to_string=False)
    composite_qty = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    composite_fat = serializers.DecimalField(max_digits=5, decimal_places=2, coerce_to_string=False)
    composite_snf = serializers.DecimalField(max_digits=5, decimal_places=2, coerce_to_string=False)
    composite_amount = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False)
    new_actual_amount = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False)
    variation = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False)

    class Meta:
        model = FacilitatorDashboardSummary
        fields = [
            "mpp_code",
            "shift_code",
            "actual_qty",
            "actual_fat",
            "actual_snf",
            "composite_qty",
            "composite_fat",
            "composite_snf",
            "composite_amount",
            "new_actual_amount",
            "variation",
        ]
        read_only_fields = ("mpp_code", "shift_code")
