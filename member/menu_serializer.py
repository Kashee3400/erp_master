# menu/serializers.py

from rest_framework import serializers
from django.utils.module_loading import import_string
from .menu_model import MenuItem, UserMenuPreference, MenuAccessLog


class MenuItemSerializer(serializers.ModelSerializer):
    """
    Serializer for MenuItem with:
    - Recursive children
    - Automatic badge resolving
    - Permissions/roles not exposed in output
    - External link options
    - Feature flag evaluated by caller
    """

    children = serializers.SerializerMethodField()
    badge = serializers.SerializerMethodField()

    class Meta:
        model = MenuItem
        fields = [
            "id",
            "code",
            "label",
            "icon",
            "path",
            "is_external",
            "opens_new_tab",
            "order",
            "badge",
            "badge_color",
            "css_class",
            "children",
        ]

    # ------------------------------------
    # Recursive Child Serialization
    # ------------------------------------
    def get_children(self, obj):
        """Serialize only active + visible children."""
        user = self.context.get("user")
        feature_flags = self.context.get("feature_flags", set())

        # Filter backend: is_active, is_visible, feature flag
        qs = obj.children.filter(is_active=True, is_visible=True).order_by("order")

        # Apply feature_flag filtering
        qs = (
            qs.exclude(feature_flag__isnull=False)
            .exclude(feature_flag__exact="")
            .exclude(feature_flag__in=feature_flags)
        )

        # Apply role + permission filtering (context-provided function)
        filter_fn = self.context.get("filter_fn")
        if filter_fn:
            qs = [child for child in qs if filter_fn(child, user)]

        return MenuItemSerializer(qs, many=True, context=self.context).data

    # ------------------------------------
    # Badge Resolver Logic
    # ------------------------------------
    def get_badge(self, obj):
        """
        Resolve badge using python-path function if present.
        Example: "menu.badges.get_pending_users_count"
        """
        resolver_path = obj.badge_resolver
        if not resolver_path:
            return None

        try:
            resolver_fn = import_string(resolver_path)
        except Exception:
            return None

        user = self.context.get("user")
        try:
            return resolver_fn(user)
        except Exception:
            return None


class UserMenuPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for user-specific menu preferences.
    This is used for:
    - Pinning items
    - Collapsing menu sections
    - Custom ordering
    - Hiding items
    """

    menu_item_code = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserMenuPreference
        fields = [
            "id",
            "menu_item",
            "menu_item_code",
            "is_pinned",
            "is_collapsed",
            "custom_order",
            "is_hidden",
            "created",
            "modified",
        ]
        read_only_fields = ["id", "menu_item_code", "created", "modified"]

    # Used by frontend to uniquely identify items without UUID
    def get_menu_item_code(self, obj):
        return obj.menu_item.code

    # Ensure user cannot change preferences of another user
    def validate(self, attrs):
        request = self.context.get("request")
        if self.instance:
            if self.instance.user != request.user:
                raise serializers.ValidationError(
                    "Not allowed to update this preference."
                )
        return attrs

    # Automatically assign the logged-in user
    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["user"] = request.user
        return super().create(validated_data)


class MenuAccessLogSerializer(serializers.ModelSerializer):
    """
    Serializer for MenuAccessLog.

    Features:
    - READ (GET): Returns expanded details for User and MenuItem (friendly names, not just IDs).
    - WRITE (POST/PUT/PATCH): Accepts standard IDs for User and MenuItem.
    - VALIDATION: Ensures ID and accessed_at cannot be tampered with.
    """

    class Meta:
        model = MenuAccessLog
        fields = ["id", "user", "menu_item", "accessed_at", "ip_address", "user_agent"]
        # These fields are auto-generated or immutable, so we prevent users from editing them.
        read_only_fields = ["id", "accessed_at"]

    def to_representation(self, instance):
        """
        Customize the output serialization (GET requests).
        We override this to provide detailed nested objects while keeping
        the input flat (just IDs) for easy writing.
        """
        response = super().to_representation(instance)

        # Enrich the 'user' field with readable details
        # We assume the User model has 'username' and 'email' fields
        if instance.user:
            response["user_details"] = {
                "id": instance.user.id,
                "username": instance.user.username,
                # Add email or full_name here if needed
            }

        # Enrich the 'menu_item' field
        # The prompt's __str__ method referenced 'self.menu_item.label'
        if instance.menu_item:
            response["menu_item_details"] = {
                "id": instance.menu_item.id,
                "label": getattr(instance.menu_item, "label", str(instance.menu_item)),
                # You can add 'url' or 'slug' here if useful for navigation
            }

        return response

    def create(self, validated_data):
        """
        Optional: Override create if you want to automatically
        capture IP/Agent from the request context if they weren't provided in the body.

        Usage in View: serializer = MenuAccessLogSerializer(data=data, context={'request': request})
        """
        request = self.context.get("request")

        # If ip_address wasn't sent in the body, try to get it from request
        if request and "ip_address" not in validated_data:
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                validated_data["ip_address"] = x_forwarded_for.split(",")[0]
            else:
                validated_data["ip_address"] = request.META.get("REMOTE_ADDR")

        # If user_agent wasn't sent in the body, try to get it from request
        if request and "user_agent" not in validated_data:
            validated_data["user_agent"] = request.META.get("HTTP_USER_AGENT", "")

        return super().create(validated_data)


class MenuPreferenceUpdateSerializer(serializers.Serializer):
    """Serializer for updating menu preferences"""

    menu_code = serializers.CharField(max_length=100)
    is_pinned = serializers.BooleanField(required=False)
    is_collapsed = serializers.BooleanField(required=False)
    is_hidden = serializers.BooleanField(required=False)
    custom_order = serializers.IntegerField(required=False, allow_null=True)


class MenuPreferencesBulkUpdateSerializer(serializers.Serializer):
    """Serializer for bulk preference updates"""

    preferences = MenuPreferenceUpdateSerializer(many=True)
