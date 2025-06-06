# serializers.py
from rest_framework import serializers
from ..models.vcg_model import *


class VCGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = VCGroup
        fields = ("whatsapp_num", "member_code", "member_name", "member_ex_code")


class ZeroDaysReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZeroDaysPourerReason
        fields = ("id", "reason")

    def validate_reason(self, value):
        if not value.strip():  # Check if the value is blank
            raise serializers.ValidationError("Reason cannot be blank.")
        return value


class MemberComplaintReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberComplaintReason
        fields = fields = ("id", "reason")

    def validate_reason(self, value):
        if not value.strip():
            raise serializers.ValidationError("Reason cannot be blank.")
        return value


class VCGMeetingImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = VCGMeetingImages
        fields = "__all__"


class MonthAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthAssignment
        fields = "__all__"


class VCGMemberAttendanceSerializer(serializers.ModelSerializer):
    group_member_label = serializers.SerializerMethodField()
    member_code = serializers.SerializerMethodField()

    class Meta:
        model = VCGMemberAttendance
        fields = ["id", "meeting", "member_code", "group_member_label", "status", "date"]

    def get_group_member_label(self, obj):
        if obj.group_member:
            name = obj.group_member.member_name
            ex_code = obj.group_member.member_ex_code or ""
            suffix = ex_code[-4:] if len(ex_code) >= 4 else ex_code
            return f"{name} ({suffix})"
        return None

    def get_member_code(self, obj):
        if obj.group_member:
            member_code = obj.group_member.member_code
            return member_code
        return None


class ZeroDaysPouringReportSerializer(serializers.ModelSerializer):
    reason = serializers.PrimaryKeyRelatedField(
        queryset=ZeroDaysPourerReason.objects.all(), write_only=True
    )
    reason_label = serializers.StringRelatedField(source="reason", read_only=True)

    class Meta:
        model = ZeroDaysPouringReport
        fields = [
            "id",
            "member_code",
            "member_ex_code",
            "member_name",
            "reason",
            "reason_label",
            "meeting",
        ]

    def create_or_update(self, validated_data):
        report, created = ZeroDaysPouringReport.objects.update_or_create(
            meeting=validated_data["meeting"],
            member_code=validated_data["member_code"],
            defaults={
                "member_ex_code": validated_data["member_ex_code"],
                "member_name": validated_data["member_name"],
                "reason": validated_data["reason"],
            },
        )
        return report, created



class MemberComplaintReportSerializer(serializers.ModelSerializer):
    reason = serializers.PrimaryKeyRelatedField(
        queryset=MemberComplaintReason.objects.all(), write_only=True
    )
    reason_label = serializers.StringRelatedField(source="reason", read_only=True)

    class Meta:
        model = MemberComplaintReport
        fields = [
            'id',
            "member_code",
            "member_ex_code",
            "member_name",
            "reason",  # Accepts ID on input
            "reason_label",  # Returns reason string on output
            "meeting",
        ]

    def create_or_update(self, validated_data):
        report, created = MemberComplaintReport.objects.update_or_create(
            meeting=validated_data["meeting"],
            member_code=validated_data["member_code"],
            defaults={
                "member_ex_code": validated_data["member_ex_code"],
                "member_name": validated_data["member_name"],
                "reason": validated_data["reason"],
            },
        )
        return report, created


class VCGMeetingSerializer(serializers.ModelSerializer):
    meeting_id = serializers.UUIDField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        read_only=True
    )  # Ensure user is set automatically
    conducted_by = serializers.SerializerMethodField()
    class Meta:
        model = VCGMeeting
        fields = [
            "meeting_id",
            "user",
            "conducted_by",
            "mpp_name",
            "mpp_ex_code",
            "mpp_code",
            "lat",
            "lon",
            "status",
            "started_at",
            "completed_at",
            "synced",
        ]

    def create(self, validated_data):
        """Override create to set the user as the authenticated user."""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["user"] = request.user  # Set authenticated user
        else:
            raise serializers.ValidationError({"user": "User must be authenticated."})
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Override update to prevent changing the user field."""
        validated_data.pop("user", None)  # Ensure user cannot be updated
        return super().update(instance, validated_data)
    
    def get_conducted_by(self,obj):
        return obj.user.get_full_name() if obj.user is not None else "N/A"