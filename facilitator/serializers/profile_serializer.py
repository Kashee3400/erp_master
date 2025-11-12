from rest_framework import serializers
from ..models.user_profile_model import UserProfile,UserLocation
from django.contrib.auth import get_user_model

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    name = serializers.SerializerMethodField()
    avatar = serializers.ImageField(required=False, allow_null=True)
    reportee_count = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "salutation",
            "user",
            "username",
            "email",
            "name",
            "department",
            "avatar",
            "phone_number",
            "address",
            "designation",
            "is_verified",
            "is_email_verified",
            "created_at",
            "updated_at",
            "reportee_count",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_name(self, obj):
        first_name = obj.user.first_name or ""
        last_name = obj.user.last_name or ""
        full_name = f"{first_name} {last_name}".strip()
        return full_name if full_name else obj.user.username

    def get_reportee_count(self, obj):
        return 0

    def to_representation(self, instance):
        """Override default representation to ensure no null values are returned."""
        data = super().to_representation(instance)

        # Define default values for any potentially null fields
        defaults = {
            "avatar": "",
            "salutation": "",
            "address": "",
            "designation": "",
            "phone_number": "",
            "email": "",
            "department": "",
            "name": "",
        }

        # Replace None values with defaults
        for field, default in defaults.items():
            if data.get(field) is None:
                data[field] = default

        return data




class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
        extra_kwargs = {
            "username": {"required": False},
            "email": {"required": False},
            "first_name": {"required": False},
            "last_name": {"required": False},
        }

    def validate_email(self, value):
        """Validate that email is unique, excluding current user in update case."""
        user_id = self.instance.id if self.instance else None
        if User.objects.filter(email=value).exclude(id=user_id).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_username(self, value):
        """Validate that username is unique, excluding current user in update case."""
        user_id = self.instance.id if self.instance else None
        if User.objects.filter(username=value).exclude(id=user_id).exists():
            raise serializers.ValidationError("This username is already in use.")
        return value


class UserUpdateProfileSerializer(serializers.ModelSerializer):
    user = UserUpdateSerializer(required=False)

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "user",
            "reports_to",
            "salutation",
            "department",
            "avatar",
            "phone_number",
            "address",
            "designation",
            "is_verified",
            "is_email_verified",
            "mpp_code",
        ]
        extra_kwargs = {
            "reports_to": {"required": False, "allow_null": True},
            "department": {"required": False},
            "phone_number": {"required": False},
            "address": {"required": False},
            "designation": {"required": False},
            "mpp_code": {"required": False},
        }

    def validate_phone_number(self, value):
        """Validate phone number format."""
        if value and len(value) < 10:
            raise serializers.ValidationError(
                "Phone number must be at least 10 digits."
            )
        return value

    def validate_reports_to(self, value):
        """Ensure user doesn't report to themselves."""
        if value and hasattr(self, "instance") and self.instance:
            if value.user_id == self.instance.user_id:
                raise serializers.ValidationError("A user cannot report to themselves.")
        return value


class UserLocationSerializer(serializers.ModelSerializer):
    """Serializer for returning user location details."""

    user = serializers.StringRelatedField(read_only=True)
    assigned_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = UserLocation
        fields = [
            "id",
            "user",
            "mcc_code",
            "mcc_ex_code",
            "mcc_name",
            "mpp_code",
            "mpp_ex_code",
            "mpp_name",
            "is_primary",
            "active",
            "assigned_by",
            "assigned_at",
            "remarks",
        ]
        read_only_fields = ("assigned_at",)
