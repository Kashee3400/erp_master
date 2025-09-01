# serializers.py
from rest_framework import serializers
from django.db.models import Sum, F
from ..models.stock_models import (
    Medicine,
    MedicineCategory,
    MedicineStock,
    UserMedicineStock,
    UserMedicineTransaction,
    MedicineStockAudit,
)
from django.contrib.auth import get_user_model

User = get_user_model()


class MedicineCategorySerializer(serializers.ModelSerializer):
    parent_category_name = serializers.CharField(
        source="parent_category.category", read_only=True
    )

    class Meta:
        model = MedicineCategory
        fields = [
            "id",
            "category",
            "medicine_form",
            "unit_of_quantity",
            "parent_category",
            "parent_category_name",
        ]


class MedicineBasicSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.category", read_only=True)
    unit_of_quantity = serializers.CharField(
        source="category.unit_of_quantity", read_only=True
    )

    class Meta:
        model = Medicine
        fields = ["id", "medicine", "strength", "category_name", "unit_of_quantity"]


class MedicineStockSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source="medicine.medicine", read_only=True)
    updated_by_name = serializers.CharField(source="updated_by.get_full_name", read_only=True)
    
    medicine_strength = serializers.CharField(
        source="medicine.strength", read_only=True
    )
    unit_of_quantity = serializers.CharField(
        source="medicine.category.unit_of_quantity", read_only=True
    )
    category_name = serializers.CharField(
        source="medicine.category.category", read_only=True
    )
    is_expired = serializers.SerializerMethodField()
    days_to_expiry = serializers.SerializerMethodField()
    allocated_quantity = serializers.SerializerMethodField()
    available_quantity = serializers.SerializerMethodField()

    class Meta:
        model = MedicineStock
        fields = [
            "id",
            "medicine",
            "medicine_name",
            "medicine_strength",
            "total_quantity",
            "batch_number",
            "expiry_date",
            "unit_of_quantity",
            "category_name",
            "is_expired",
            "days_to_expiry",
            "allocated_quantity",
            "available_quantity",
            "last_updated",
            "locale",
            "created_at",
            "updated_by",
            "updated_by_name",
            "sync",
            "is_deleted",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_by",
            "last_updated",
            "locale",
            "sync",
        ]

    def get_is_expired(self, obj):
        if obj.expiry_date:
            from django.utils import timezone

            return obj.expiry_date < timezone.now().date()
        return False

    def get_days_to_expiry(self, obj):
        if obj.expiry_date:
            from django.utils import timezone

            delta = obj.expiry_date - timezone.now().date()
            return delta.days
        return None

    def get_allocated_quantity(self, obj):
        return (
            obj.user_allocations.aggregate(total=Sum("allocated_quantity"))["total"]
            or 0
        )

    def get_available_quantity(self, obj):
        allocated = self.get_allocated_quantity(obj)
        return obj.total_quantity - allocated


class MedicineStockCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineStock
        fields = ["medicine", "total_quantity", "batch_number", "expiry_date"]

    def validate(self, data):
        if data.get("expiry_date"):
            from django.utils import timezone

            if data["expiry_date"] < timezone.now().date():
                raise serializers.ValidationError("Expiry date cannot be in the past")
        return data


class UserMedicineStockSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    medicine_name = serializers.CharField(
        source="medicine_stock.medicine.medicine", read_only=True
    )
    medicine_strength = serializers.CharField(
        source="medicine_stock.medicine.strength", read_only=True
    )
    batch_number = serializers.CharField(
        source="medicine_stock.batch_number", read_only=True
    )
    unit_of_quantity = serializers.CharField(
        source="medicine_stock.medicine.category.unit_of_quantity", read_only=True
    )
    remaining_quantity = serializers.SerializerMethodField()
    is_below_threshold = serializers.SerializerMethodField()
    allocated_by_name = serializers.CharField(
        source="allocated_by.get_full_name", read_only=True
    )

    class Meta:
        model = UserMedicineStock
        fields = [
            "id",
            "user",
            "user_name",
            "username",
            "medicine_stock",
            "medicine_name",
            "medicine_strength",
            "batch_number",
            "allocated_quantity",
            "used_quantity",
            "remaining_quantity",
            "allocation_date",
            "remarks",
            "min_threshold",
            "threshold_quantity",
            "is_below_threshold",
            "unit_of_quantity",
            "allocated_by",
            "allocated_by_name",
            "sync",
            "is_deleted",
            "locale",
        ]
        read_only_fields = ["id","allocation_date"]

    def get_remaining_quantity(self, obj):
        return obj.remaining_quantity()

    def get_is_below_threshold(self, obj):
        return obj.is_below_threshold()


class UserMedicineStockCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMedicineStock
        fields = [
            "user",
            "medicine_stock",
            "allocated_quantity",
            "remarks",
            "min_threshold",
            "threshold_quantity",
        ]

    def validate(self, data):
        medicine_stock = data["medicine_stock"]
        allocated_quantity = data["allocated_quantity"]

        # Check if enough stock is available
        current_allocated = (
            medicine_stock.user_allocations.aggregate(total=Sum("allocated_quantity"))[
                "total"
            ]
            or 0
        )

        available_quantity = medicine_stock.total_quantity - current_allocated

        if allocated_quantity > available_quantity:
            raise serializers.ValidationError(
                f"Insufficient stock. Available: {available_quantity} "
                f"{medicine_stock.medicine.category.unit_of_quantity}"
            )

        return data

    def create(self, validated_data):
        # Set allocated_by to current user
        validated_data["allocated_by"] = self.context["request"].user
        return super().create(validated_data)


class UserMedicineTransactionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(
        source="user_medicine_stock.user.get_full_name", read_only=True
    )
    medicine_name = serializers.CharField(
        source="user_medicine_stock.medicine_stock.medicine.medicine", read_only=True
    )
    action_display = serializers.CharField(source="get_action_display", read_only=True)

    class Meta:
        model = UserMedicineTransaction
        fields = [
            "id",
            "user_medicine_stock",
            "action",
            "action_display",
            "quantity",
            "timestamp",
            "note",
            "user_name",
            "medicine_name",
        ]
        read_only_fields = ["timestamp"]


class MedicineStockAuditSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source="medicine.medicine", read_only=True)
    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True
    )
    transaction_type_display = serializers.CharField(
        source="get_transaction_type_display", read_only=True
    )

    class Meta:
        model = MedicineStockAudit
        fields = [
            "id",
            "medicine",
            "medicine_name",
            "transaction_type",
            "transaction_type_display",
            "quantity",
            "description",
            "created_by",
            "created_by_name",
            "created_at",
        ]
        read_only_fields = ["created_by", "created_at"]


# Dashboard specific serializers
class InventoryAlertSerializer(serializers.Serializer):
    type = serializers.CharField()  # 'global_stock' or 'user_stock'
    severity = serializers.CharField()  # 'critical', 'warning', 'expired'
    medicine_name = serializers.CharField()
    medicine_strength = serializers.CharField()
    current_quantity = serializers.FloatField()
    threshold_quantity = serializers.FloatField(required=False)
    unit_of_quantity = serializers.CharField()
    user_name = serializers.CharField(required=False)
    batch_number = serializers.CharField(required=False)
    expiry_date = serializers.DateField(required=False)
    days_to_expiry = serializers.IntegerField(required=False)
    message = serializers.CharField()


class DashboardStatsSerializer(serializers.Serializer):
    total_medicines = serializers.IntegerField()
    total_stock_items = serializers.IntegerField()
    total_user_allocations = serializers.IntegerField()
    expired_stock_count = serializers.IntegerField()
    expiring_soon_count = serializers.IntegerField()
    low_stock_count = serializers.IntegerField()
    critical_user_stock_count = serializers.IntegerField()
    total_stock_value = serializers.FloatField(required=False)
