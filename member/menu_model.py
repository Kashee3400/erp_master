# menu/models.py
"""
Production-ready menu system with role-based access control.
Supports: hierarchical menus, dynamic badges, caching, audit trails, multi-tenancy.
"""

from django.db import models
from django.contrib.auth.models import Group, Permission
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()


class TimeStampedModel(models.Model):
    """Abstract base model with timestamp fields"""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(class)s_created",
        blank=True,
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(class)s_updated",
        blank=True,
    )

    class Meta:
        abstract = True


class Role(TimeStampedModel):
    """
    Custom role model extending Django's Group.
    Allows for more flexible role management and business logic.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, db_index=True)
    code = models.SlugField(max_length=50, unique=True, db_index=True)
    description = models.TextField(blank=True)
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name="role")
    is_active = models.BooleanField(default=True, db_index=True)
    priority = models.IntegerField(
        default=0, help_text="Higher priority roles take precedence"
    )

    # Multi-tenancy support (optional)
    tenant = models.ForeignKey(
        "Tenant", on_delete=models.CASCADE, null=True, blank=True, related_name="roles"
    )

    class Meta:
        db_table = "menu_roles"
        ordering = ["-priority", "name"]
        indexes = [
            models.Index(fields=["code", "is_active"]),
            models.Index(fields=["tenant", "is_active"]),
        ]

    def __str__(self):
        return self.name

    def get_permissions(self):
        """Get all permissions for this role"""
        return self.group.permissions.all()


class Tenant(TimeStampedModel):
    """
    Multi-tenancy support for SaaS applications.
    Each tenant can have isolated menu configurations.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    schema_name = models.CharField(max_length=63, unique=True, null=True, blank=True)

    class Meta:
        db_table = "menu_tenants"
        ordering = ["name"]

    def __str__(self):
        return self.name


class MenuItem(MPTTModel, TimeStampedModel):
    """
    Hierarchical menu item using MPTT for efficient tree queries.
    Supports: nested menus, role-based access, dynamic badges, external links.
    """

    ICON_CHOICES = [
        ("LayoutDashboard", "Dashboard"),
        ("Package", "Package"),
        ("Users", "Users"),
        ("User", "User"),
        ("UserCheck", "User Check"),
        ("Shield", "Shield"),
        ("BarChart3", "Bar Chart"),
        ("TrendingUp", "Trending Up"),
        ("BarChart", "Bar Chart Simple"),
        ("DollarSign", "Dollar Sign"),
        ("Settings", "Settings"),
        ("Sliders", "Sliders"),
        ("Plug", "Plug"),
        ("HelpCircle", "Help Circle"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.SlugField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Unique identifier for programmatic access",
    )
    label = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, choices=ICON_CHOICES, blank=True)

    # Path handling
    path = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Internal route path or external URL",
    )
    is_external = models.BooleanField(
        default=False, help_text="Whether the path is an external URL"
    )
    opens_new_tab = models.BooleanField(default=False)

    # Hierarchy using MPTT
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        db_index=True,
    )

    # Access control
    roles = models.ManyToManyField(
        Role,
        blank=True,
        related_name="menu_items",
        help_text="Leave empty for public access",
    )
    required_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="menu_items",
        help_text="User must have ALL these permissions",
    )

    # Badge system
    badge_resolver = models.CharField(
        max_length=255,
        blank=True,
        help_text="Python path to badge resolver function (e.g., 'menu.badges.get_pending_count')",
    )
    badge_color = models.CharField(
        max_length=50,
        default="red",
        choices=[
            ("red", "Red"),
            ("blue", "Blue"),
            ("green", "Green"),
            ("yellow", "Yellow"),
            ("gray", "Gray"),
        ],
    )

    # Display options
    is_active = models.BooleanField(default=True, db_index=True)
    is_visible = models.BooleanField(
        default=True, help_text="Hide from menu but keep accessible via direct URL"
    )
    order = models.IntegerField(default=0, db_index=True)
    css_class = models.CharField(max_length=100, blank=True)

    # Multi-tenancy
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="menu_items",
    )

    # Feature flags
    feature_flag = models.CharField(
        max_length=100,
        blank=True,
        help_text="Feature flag to check before showing this menu item",
    )

    class MPTTMeta:
        order_insertion_by = ["order", "label"]

    class Meta:
        db_table = "menu_items"
        ordering = ["tree_id", "lft", "order"]
        indexes = [
            models.Index(fields=["parent", "is_active", "is_visible"]),
            models.Index(fields=["tenant", "is_active"]),
            models.Index(fields=["code", "tenant"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["code", "tenant"], name="unique_code_per_tenant"
            )
        ]

    def __str__(self):
        return f"{self.get_level_indicator()}{self.label}"

    def get_level_indicator(self):
        """Visual indicator of menu depth"""
        return "└─ " * self.level

    def clean(self):
        """Validation logic"""
        if self.parent and self.parent.pk == self.pk:
            raise ValidationError("Menu item cannot be its own parent")

        if self.is_external and not self.path:
            raise ValidationError("External links must have a path")

        if self.parent and self.parent.tenant != self.tenant:
            raise ValidationError("Parent must belong to the same tenant")

    def get_badge_count(self, user):
        """
        Execute badge resolver function and return count.
        Cached for 5 minutes to avoid excessive database queries.
        """
        if not self.badge_resolver:
            return None

        cache_key = f"menu_badge_{self.code}_{user.id}"
        cached_value = cache.get(cache_key)

        if cached_value is not None:
            return cached_value

        try:
            from django.utils.module_loading import import_string

            resolver_func = import_string(self.badge_resolver)
            count = resolver_func(user)

            # Cache for 5 minutes
            cache.set(cache_key, count, 300)
            return count
        except (ImportError, AttributeError, Exception) as e:
            # Log error but don't break the menu
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Badge resolver error for {self.code}: {e}")
            return None

    def user_has_access(self, user):
        """
        Check if user has access to this menu item.
        Returns: (has_access: bool, reason: str)
        """
        if not self.is_active:
            return False, "Menu item is inactive"

        # Check tenant access
        if self.tenant and hasattr(user, "tenant") and user.tenant != self.tenant:
            return False, "Tenant mismatch"

        # Check feature flag
        if self.feature_flag:
            from django.conf import settings

            flags = getattr(settings, "FEATURE_FLAGS", {})
            if not flags.get(self.feature_flag, False):
                return False, "Feature not enabled"

        # Check roles (OR logic - user needs ANY of the roles)
        if self.roles.exists():
            user_roles = (
                user.role_set.filter(is_active=True)
                if hasattr(user, "role_set")
                else []
            )
            if not any(role in self.roles.all() for role in user_roles):
                return False, "Missing required role"

        # Check permissions (AND logic - user needs ALL permissions)
        required_perms = list(
            self.required_permissions.values_list("codename", "content_type__app_label")
        )
        for codename, app_label in required_perms:
            perm = f"{app_label}.{codename}"
            if not user.has_perm(perm):
                return False, f"Missing permission: {perm}"

        return True, "Access granted"

    @classmethod
    def get_menu_for_user(cls, user, tenant=None):
        """
        Get filtered menu tree for a specific user.
        Returns only items the user has access to.
        Uses MPTT for efficient tree queries.
        """
        cache_key = f"menu_tree_{user.id}_{tenant.id if tenant else 'global'}"
        cached_menu = cache.get(cache_key)

        if cached_menu is not None:
            return cached_menu

        # Get all active, visible menu items
        queryset = cls.objects.filter(is_active=True, is_visible=True).prefetch_related(
            "roles", "required_permissions", "children"
        )

        if tenant:
            queryset = queryset.filter(
                models.Q(tenant=tenant) | models.Q(tenant__isnull=True)
            )
        else:
            queryset = queryset.filter(tenant__isnull=True)

        # Filter based on user access
        accessible_items = []
        for item in queryset:
            has_access, _ = item.user_has_access(user)
            if has_access:
                accessible_items.append(item)

        # Build tree structure
        menu_tree = []
        for item in accessible_items:
            if item.parent is None or item.parent not in accessible_items:
                menu_tree.append(
                    cls._build_menu_tree_node(item, accessible_items, user)
                )

        # Cache for 10 minutes
        cache.set(cache_key, menu_tree, 600)
        return menu_tree

    @classmethod
    def _build_menu_tree_node(cls, item, accessible_items, user):
        """Recursively build menu tree node"""
        node = {
            "id": str(item.id),
            "code": item.code,
            "label": item.label,
            "icon": item.icon,
            "path": item.path,
            "is_external": item.is_external,
            "opens_new_tab": item.opens_new_tab,
            "css_class": item.css_class,
            "badge": item.get_badge_count(user),
            "badge_color": item.badge_color,
            "children": [],
        }

        for child in item.get_children():
            if child in accessible_items:
                node["children"].append(
                    cls._build_menu_tree_node(child, accessible_items, user)
                )

        return node


class MenuAccessLog(models.Model):
    """
    Audit trail for menu access.
    Useful for compliance and analytics.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    accessed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)

    class Meta:
        db_table = "menu_access_logs"
        ordering = ["-accessed_at"]
        indexes = [
            models.Index(fields=["user", "-accessed_at"]),
            models.Index(fields=["menu_item", "-accessed_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} accessed {self.menu_item.label} at {self.accessed_at}"


class UserMenuPreference(TimeStampedModel):
    """
    Store user-specific menu preferences.
    Allows users to pin favorites, collapse sections, etc.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="menu_preferences"
    )
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)

    is_pinned = models.BooleanField(default=False)
    is_collapsed = models.BooleanField(default=False)
    custom_order = models.IntegerField(null=True, blank=True)
    is_hidden = models.BooleanField(default=False)

    class Meta:
        db_table = "menu_user_preferences"
        unique_together = [["user", "menu_item"]]
        indexes = [
            models.Index(fields=["user", "is_pinned"]),
        ]

    def __str__(self):
        return f"{self.user.username}'s preference for {self.menu_item.label}"
