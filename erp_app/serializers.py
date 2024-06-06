from .models import *
from rest_framework import serializers



class MemberMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberMaster
        fields = '__all__'
 

class BillingMemberDetailHistorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BillingMemberDetailHistory
        fields = '__all__'
 
