# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import OTP,ProductRate

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
        fields = ['name', 'price', 'image','locale','name_translation', 'created_at', 'updated_at', 'created_by', 'updated_by']
