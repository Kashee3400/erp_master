# serializers.py
from rest_framework import serializers
from ..models.vcg_model import *


class VCGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = VCGroup
        fields = ('whatsapp_num', 'member_code',"member_name", 'member_ex_code')

class ZeroDaysReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZeroDaysPourerReason
        fields = ('id', 'reason')

    def validate_reason(self, value):
        if not value.strip():  # Check if the value is blank
            raise serializers.ValidationError("Reason cannot be blank.")
        return value
    
class MemberComplaintReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberComplaintReason
        fields = fields = ('id', 'reason')
    
    def validate_reason(self, value):
        if not value.strip():
            raise serializers.ValidationError("Reason cannot be blank.")
        return value
    
class VCGMeetingImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = VCGMeetingImages
        fields = '__all__'

class MonthAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthAssignment
        fields = '__all__'


class VCGMemberAttendanceSerializer(serializers.ModelSerializer):
    member = VCGroupSerializer()
    class Meta:
        model = VCGMemberAttendance
        fields =['group_member','status','date']


class ZeroDaysPouringReportSerializer(serializers.ModelSerializer):
    reason = serializers.StringRelatedField()
    class Meta:
        model = ZeroDaysPouringReport
        fields = ['member_code', 'member_ex_code','member_name','reason','meeting']
        
class MemberComplaintReportSerializer(serializers.ModelSerializer):
    reason = serializers.StringRelatedField()
    class Meta:
        model = MemberComplaintReport
        fields = ['member_code', 'member_ex_code','member_name','reason','meeting']


from rest_framework import serializers

class VCGMeetingSerializer(serializers.ModelSerializer):
    meeting_id = serializers.UUIDField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)  # Ensure user is set automatically

    class Meta:
        model = VCGMeeting
        fields = [
            'meeting_id', 'user', 'mpp_name', 'mpp_ex_code', 'mpp_code', 
            'lat', 'lon', 'status', 'started_at', 'completed_at', 'synced'
        ]

    def create(self, validated_data):
        """Override create to set the user as the authenticated user."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user  # Set authenticated user
        else:
            raise serializers.ValidationError({"user": "User must be authenticated."})
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Override update to prevent changing the user field."""
        validated_data.pop('user', None)  # Ensure user cannot be updated
        return super().update(instance, validated_data)
