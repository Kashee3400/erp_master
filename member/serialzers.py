# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import OTP


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ['phone_number']

class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=10)
    otp = serializers.CharField(max_length=6)
