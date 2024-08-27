# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import OTP

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

from rest_framework_simplejwt.serializers import TokenRefreshSerializer

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    @classmethod
    def validate(cls, attrs):
        data = super().validate(attrs)
        return {
            'refresh': data.get('refresh', attrs.get('refresh')),
            'access': data['access'],
        }
