# serializers.py
from rest_framework import serializers
from ..models.transaction_model import PaymentTransaction


class PaymentTransactionListSerializer(serializers.ModelSerializer):
    """Serializer for list view - optimized with minimal fields"""

    amount_display = serializers.SerializerMethodField()
    status_color = serializers.SerializerMethodField()
    related_object_info = serializers.SerializerMethodField()
    duration_minutes = serializers.SerializerMethodField()

    class Meta:
        model = PaymentTransaction
        fields = [
            "id",
            "merchant_order_id",
            "phonepe_transaction_id",
            "transaction_type",
            "user_identifier",
            "amount",
            "amount_display",
            "currency",
            "status",
            "status_color",
            "status_message",
            "payment_method_type",
            "related_object_info",
            "created_at",
            "updated_at",
            "verified_at",
            "completed_at",
            "duration_minutes",
            "is_active",
        ]

    def get_amount_display(self, obj):
        return f"{obj.currency} {obj.amount}"

    def get_status_color(self, obj):
        colors = {
            "INITIATED": "#FFA500",
            "PENDING": "#FFD700",
            "SUCCESS": "#28a745",
            "FAILED": "#dc3545",
            "EXPIRED": "#6c757d",
            "REFUNDED": "#17a2b8",
        }
        return colors.get(obj.status, "#6c757d")

    def get_related_object_info(self, obj):
        if obj.content_type and obj.object_id:
            return {
                "model": obj.content_type.model,
                "app_label": obj.content_type.app_label,
                "object_id": obj.object_id,
            }
        return None

    def get_duration_minutes(self, obj):
        """Calculate transaction duration in minutes"""
        if obj.completed_at and obj.created_at:
            delta = obj.completed_at - obj.created_at
            return round(delta.total_seconds() / 60, 2)
        return None


class PaymentTransactionDetailSerializer(serializers.ModelSerializer):
    """Serializer for detail view - all fields"""

    amount_display = serializers.SerializerMethodField()
    status_color = serializers.SerializerMethodField()
    related_object_info = serializers.SerializerMethodField()
    duration_minutes = serializers.SerializerMethodField()
    refund_status = serializers.SerializerMethodField()

    class Meta:
        model = PaymentTransaction
        fields = "__all__"

    def get_amount_display(self, obj):
        return f"{obj.currency} {obj.amount}"

    def get_status_color(self, obj):
        colors = {
            "INITIATED": "#FFA500",
            "PENDING": "#FFD700",
            "SUCCESS": "#28a745",
            "FAILED": "#dc3545",
            "EXPIRED": "#6c757d",
            "REFUNDED": "#17a2b8",
        }
        return colors.get(obj.status, "#6c757d")

    def get_related_object_info(self, obj):
        if obj.content_type and obj.object_id:
            return {
                "model": obj.content_type.model,
                "app_label": obj.content_type.app_label,
                "object_id": obj.object_id,
            }
        return None

    def get_duration_minutes(self, obj):
        if obj.completed_at and obj.created_at:
            delta = obj.completed_at - obj.created_at
            return round(delta.total_seconds() / 60, 2)
        return None

    def get_refund_status(self, obj):
        if obj.refund_amount > 0:
            return {
                "is_refunded": True,
                "refund_amount": str(obj.refund_amount),
                "refund_percentage": (
                    round((obj.refund_amount / obj.amount) * 100, 2)
                    if obj.amount > 0
                    else 0
                ),
                "refund_initiated_at": obj.refund_initiated_at,
                "refund_completed_at": obj.refund_completed_at,
            }
        return {"is_refunded": False}


class PaymentStatisticsSerializer(serializers.Serializer):
    """Serializer for statistics"""

    total_transactions = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    successful_transactions = serializers.IntegerField()
    successful_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    failed_transactions = serializers.IntegerField()
    pending_transactions = serializers.IntegerField()
    refunded_transactions = serializers.IntegerField()
    refunded_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    success_rate = serializers.FloatField()
    average_transaction_amount = serializers.DecimalField(
        max_digits=15, decimal_places=2
    )
