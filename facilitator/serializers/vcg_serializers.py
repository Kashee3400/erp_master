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
        fields = '__all__'

class MemberComplaintReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberComplaintReason
        fields = '__all__'

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
        fields = ['member_code', 'member_ex_code','member_name','reason']
        
class MemberComplaintReportSerializer(serializers.ModelSerializer):
    reason = serializers.StringRelatedField()
    class Meta:
        model = MemberComplaintReport
        fields = ['member_code', 'member_ex_code','member_name','reason']


class VCGMeetingSerializer(serializers.ModelSerializer):
    meeting_id = serializers.UUIDField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    class Meta:
        model = VCGMeeting
        fields = ['meeting_id', 'user', 'mpp_name', 'mpp_ex_code', 'mpp_code', 
                'lat', 'lon', 'status', 'started_at', 'completed_at', 'synced']
