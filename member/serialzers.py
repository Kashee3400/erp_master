# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import OTP,ProductRate,SahayakIncentives
from erp_app.models import  CdaAggregationDaywiseMilktype

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password','groups','user_permissions'] 
        

class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ['phone_number']

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
            'status_code': 200,
            'message': 'Token successfully obtained',
            'refresh': data['refresh'],
            'access': data['access'],
        }

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRate
        fields = ['name', 'price', 'price_description','image','locale','name_translation', 'created_at', 'updated_at', 'created_by', 'updated_by']

class CdaAggregationDaywiseMilktypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CdaAggregationDaywiseMilktype
        fields = [
            'id',
            'mcc_code',
            'mcc_tr_code',
            'mcc_name',
            'mpp_code',
            'mpp_tr_code',
            'mpp_name',
            'collection_date',
            'milk_type_code',
            'milk_type_name',
            'milk_quality_type_code',
            'milk_quality_type_name',
            'composite_qty',
            'composite_fat',
            'composite_snf',
            'dispatch_qty',
            'dispatch_fat',
            'dispatch_snf',
            'dispatch_kg_fat',
            'dispatch_kg_snf',
            'dispatch_amount',
            'actual_qty',
            'actual_fat',
            'actual_snf',
            'actual_amount',
        ]


class SahayakIncentivesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SahayakIncentives
        fields = '__all__'
