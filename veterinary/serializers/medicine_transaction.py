# serializers.py
from rest_framework import serializers
from django.db import transaction
from ..models.stock_models import UserMedicineTransaction, ActionTypeChoices


class UserMedicineTransactionSerializer(serializers.ModelSerializer):
    user_medicine_stock_info = serializers.SerializerMethodField()
    performed_by_name = serializers.CharField(source='performed_by.username', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = UserMedicineTransaction
        fields = [
            'id', 'user_medicine_stock', 'action', 'action_display', 
            'quantity', 'running_balance', 'performed_by', 'performed_by_name',
            'timestamp', 'note', 'user_medicine_stock_info'
        ]
        read_only_fields = ['id', 'running_balance', 'timestamp']

    def get_user_medicine_stock_info(self, obj):
        stock = obj.user_medicine_stock
        return {
            'id': stock.id,
            'user': stock.user.username,
            'medicine_name': stock.medicine_stock.medicine.medicine if stock.medicine_stock.medicine else 'Unknown',
            'allocated_quantity': float(stock.allocated_quantity),
            'used_quantity': float(stock.used_quantity),
            'remaining_quantity': float(stock.remaining_quantity()),
            'stock_status': stock.stock_status()
        }


class CreateTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMedicineTransaction
        fields = ['user_medicine_stock', 'action', 'quantity', 'note']

    def validate(self, attrs):
        user_medicine_stock = attrs['user_medicine_stock']
        action = attrs['action']
        quantity = attrs['quantity']

        # Check if the stock is approved
        if not user_medicine_stock.is_approved():
            raise serializers.ValidationError(
                "Cannot perform transactions on unapproved medicine stock."
            )

        # Validate quantity is positive
        if quantity <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")

        # For USED transactions, ensure sufficient balance
        if action == ActionTypeChoices.USED:
            current_balance = user_medicine_stock.remaining_quantity()
            if quantity > current_balance:
                raise serializers.ValidationError(
                    f"Insufficient stock. Available: {current_balance}, Requested: {quantity}"
                )

        # For RETURNED transactions, ensure not returning more than used
        if action == ActionTypeChoices.RETURNED:
            if quantity > user_medicine_stock.used_quantity:
                raise serializers.ValidationError(
                    f"Cannot return more than used. Used quantity: {user_medicine_stock.used_quantity}"
                )

        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            # Create the transaction
            transaction_obj = UserMedicineTransaction.objects.create(
                **validated_data,
                performed_by=self.context['request'].user
            )
            
            # Update the UserMedicineStock used_quantity
            user_stock = validated_data['user_medicine_stock']
            if validated_data['action'] == ActionTypeChoices.USED:
                user_stock.used_quantity += validated_data['quantity']
            elif validated_data['action'] == ActionTypeChoices.RETURNED:
                user_stock.used_quantity -= validated_data['quantity']
            # Note: ALLOCATED transactions don't update used_quantity
            
            user_stock.save()
            return transaction_obj

