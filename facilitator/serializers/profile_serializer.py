from rest_framework import serializers
from ..models.user_profile_model import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    name = serializers.SerializerMethodField()
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = UserProfile
        fields = [
            "id",
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
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_name(self, obj):
        first_name = obj.user.first_name or ""
        last_name = obj.user.last_name or ""
        full_name = f"{first_name} {last_name}".strip()

        return full_name if full_name else obj.user.username
