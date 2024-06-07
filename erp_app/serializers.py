from .models import *
from rest_framework import serializers


class MemberMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberMaster
        fields = '__all__'


class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = ['shift_code','shift_name','shift_short_name']



class BillingMemberDetailHistorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BillingMemberDetailHistory
        fields = '__all__'


class MppCollectionAggregationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MppCollectionAggregation
        fields = '__all__'


class MppCollectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = MppCollection
        fields = '__all__'
        depth = 1

