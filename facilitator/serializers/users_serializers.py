
from rest_framework import serializers
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    module = serializers.SerializerMethodField(read_only=True)

    # Make these writable by removing `read_only=True`
    groups = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), many=True, required=False
    )
    user_permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(), many=True, required=False
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'module', 'is_active', 'is_staff','is_superuser', 'date_joined',
            'last_login', 'groups', 'user_permissions'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'module']

    def get_module(self, obj):
        return obj.device.module if hasattr(obj, 'device') and obj.device else "NA"

    def update(self, instance, validated_data):
        # Handle groups update
        groups = validated_data.pop('groups', None)
        if groups is not None:
            instance.groups.set(groups)

        # Handle user_permissions update
        user_permissions = validated_data.pop('user_permissions', None)
        if user_permissions is not None:
            instance.user_permissions.set(user_permissions)

        # Standard fields
        return super().update(instance, validated_data)



class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']


class GroupSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Permission.objects.all()
    )

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']
