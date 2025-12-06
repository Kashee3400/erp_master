# menu/services.py
"""
Enhanced menu filtering service integrated with Django models.
Provides caching, prefetching, and optimized database queries.
"""

from typing import List, Dict, Any, Optional, Set
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import Prefetch, Q
from django.utils.module_loading import import_string
from django.conf import settings
import logging

from .menu_model import MenuItem, Role, MenuAccessLog

logger = logging.getLogger(__name__)


class UserContext:
    """
    Encapsulates user context with lazy loading and caching.
    Optimizes permission and role checks.
    """

    def __init__(self, user: User, tenant=None):
        self.user = user
        self.tenant = tenant
        self._roles_cache = None
        self._permissions_cache = None
        self._is_superuser = user.is_superuser if user.is_authenticated else False

    @property
    def roles(self) -> Set[str]:
        """Get user's role codes (lazy loaded)"""
        if self._roles_cache is None:
            if not self.user.is_authenticated:
                self._roles_cache = set()
            else:
                # Query through Role model for active roles
                role_codes = Role.objects.filter(
                    group__user=self.user, is_active=True
                ).values_list("code", flat=True)
                self._roles_cache = set(role_codes)

                # Add admin for superusers
                if self._is_superuser:
                    self._roles_cache.add("admin")

        return self._roles_cache

    @property
    def permissions(self) -> Set[str]:
        """Get user's permission strings (lazy loaded)"""
        if self._permissions_cache is None:
            if not self.user.is_authenticated:
                self._permissions_cache = set()
            else:
                perms = set()

                # Get all user permissions efficiently
                user_perms = self.user.get_all_permissions()
                self._permissions_cache = set(user_perms)

        return self._permissions_cache

    @property
    def is_superuser(self) -> bool:
        """Check if user is superuser"""
        return self._is_superuser

    def has_role(self, role_code: str) -> bool:
        """Check if user has a specific role"""
        return role_code in self.roles

    def has_permission(self, perm: str) -> bool:
        """Check if user has a specific permission"""
        if self._is_superuser:
            return True
        return perm in self.permissions

    def has_all_permissions(self, perms: Set[str]) -> bool:
        """Check if user has all specified permissions"""
        if self._is_superuser:
            return True
        return perms.issubset(self.permissions)

    def has_any_role(self, roles: Set[str]) -> bool:
        """Check if user has any of the specified roles"""
        if self._is_superuser:
            return True
        return bool(roles.intersection(self.roles))


class MenuFilterService:
    """
    Service for filtering menu items based on user permissions and roles.
    Integrates with MenuItem model and provides optimized queries.
    """

    CACHE_TIMEOUT = 600  # 10 minutes
    BADGE_CACHE_TIMEOUT = 300  # 5 minutes

    @classmethod
    def get_cache_key(cls, user_id: int, tenant_id: Optional[int] = None) -> str:
        """Generate cache key for user's menu"""
        tenant_part = f"_tenant_{tenant_id}" if tenant_id else ""
        return f"menu_filtered_{user_id}{tenant_part}"

    @classmethod
    def invalidate_user_cache(cls, user_id: int, tenant_id: Optional[int] = None):
        """Invalidate cached menu for a user"""
        cache_key = cls.get_cache_key(user_id, tenant_id)
        cache.delete(cache_key)

    @classmethod
    def invalidate_all_caches(cls):
        """Invalidate all menu caches (use after menu structure changes)"""
        cache.delete_pattern("menu_filtered_*")

    @classmethod
    def get_menu_items_queryset(cls, tenant=None):
        """
        Get optimized queryset for menu items.
        Uses select_related and prefetch_related to minimize queries.
        """
        queryset = (
            MenuItem.objects.filter(is_active=True, is_visible=True)
            .select_related("parent", "tenant")
            .prefetch_related(
                "roles",
                "required_permissions__content_type",
                Prefetch(
                    "children",
                    queryset=MenuItem.objects.filter(
                        is_active=True, is_visible=True
                    ).order_by("order", "label"),
                ),
            )
        )

        # Filter by tenant
        if tenant:
            queryset = queryset.filter(Q(tenant=tenant) | Q(tenant__isnull=True))
        else:
            queryset = queryset.filter(tenant__isnull=True)

        return queryset.order_by("tree_id", "lft", "order")

    @classmethod
    def check_feature_flag(cls, flag_name: str) -> bool:
        """Check if a feature flag is enabled"""
        if not flag_name:
            return True

        flags = getattr(settings, "FEATURE_FLAGS", {})
        return flags.get(flag_name, False)

    @classmethod
    def has_item_access(
        cls, item: MenuItem, user_context: UserContext
    ) -> tuple[bool, str]:
        """
        Check if user has access to a menu item.

        Returns:
            (has_access: bool, reason: str)
        """
        # Superuser bypass
        if user_context.is_superuser:
            return True, "Superuser access"

        # Check feature flag
        if item.feature_flag and not cls.check_feature_flag(item.feature_flag):
            return False, f"Feature flag '{item.feature_flag}' not enabled"

        # Check tenant match
        if item.tenant and user_context.tenant and item.tenant != user_context.tenant:
            return False, "Tenant mismatch"

        # Check roles (OR logic - user needs ANY of the roles)
        item_roles = set(item.roles.values_list("code", flat=True))
        if item_roles and not user_context.has_any_role(item_roles):
            return False, f"Missing required role(s): {', '.join(item_roles)}"

        # Check permissions (AND logic - user needs ALL permissions)
        required_perms = set()
        for perm in item.required_permissions.all():
            perm_string = f"{perm.content_type.app_label}.{perm.codename}"
            required_perms.add(perm_string)

        if required_perms and not user_context.has_all_permissions(required_perms):
            missing = required_perms - user_context.permissions
            return False, f"Missing permission(s): {', '.join(missing)}"

        return True, "Access granted"

    @classmethod
    def resolve_badge(cls, item: MenuItem, user: User) -> Optional[Dict[str, Any]]:
        """
        Resolve dynamic badge for menu item with caching.

        Returns:
            Dict with 'count' and 'color' keys, or None
        """
        if not item.badge_resolver:
            return None

        cache_key = f"menu_badge_{item.code}_{user.id}"
        cached_badge = cache.get(cache_key)

        if cached_badge is not None:
            return cached_badge

        try:
            # Import and execute resolver function
            resolver_func = import_string(item.badge_resolver)
            count = resolver_func(user)

            if count is not None and count > 0:
                badge_data = {"count": count, "color": item.badge_color}
                cache.set(cache_key, badge_data, cls.BADGE_CACHE_TIMEOUT)
                return badge_data
            else:
                # Cache None result to avoid repeated calls
                cache.set(cache_key, None, cls.BADGE_CACHE_TIMEOUT)
                return None

        except (ImportError, AttributeError, TypeError) as e:
            logger.error(f"Badge resolver error for '{item.code}': {e}")
            return None
        except Exception as e:
            logger.exception(
                f"Unexpected error in badge resolver for '{item.code}': {e}"
            )
            return None

    @classmethod
    def get_user_preferences(
        cls, user: User, menu_items: List[MenuItem]
    ) -> Dict[str, Dict]:
        """
        Get user preferences for menu items in bulk.

        Returns:
            Dict mapping menu_item.code to preference dict
        """
        from .menu_model import UserMenuPreference

        if not user.is_authenticated:
            return {}

        item_ids = [item.id for item in menu_items]

        preferences = UserMenuPreference.objects.filter(
            user=user, menu_item_id__in=item_ids
        ).select_related("menu_item")

        return {
            pref.menu_item.code: {
                "is_pinned": pref.is_pinned,
                "is_collapsed": pref.is_collapsed,
                "is_hidden": pref.is_hidden,
                "custom_order": pref.custom_order,
            }
            for pref in preferences
        }

    @classmethod
    def build_menu_item_dict(
        cls, item: MenuItem, user: User, user_preferences: Dict[str, Dict]
    ) -> Dict[str, Any]:
        """
        Convert MenuItem model to serializable dict with user-specific data.
        """
        pref = user_preferences.get(item.code, {})

        item_dict = {
            "id": item.code,  # Use code as frontend ID
            "label": item.label,
            "icon": item.icon,
            "path": item.path,
            "is_external": item.is_external,
            "opens_new_tab": item.opens_new_tab,
        }

        # Add optional fields
        if item.css_class:
            item_dict["css_class"] = item.css_class

        # Add badge if present
        badge = cls.resolve_badge(item, user)
        if badge:
            item_dict["badge"] = badge

        # Add user preferences
        if pref:
            item_dict["preferences"] = pref

        return item_dict

    @classmethod
    def filter_menu_tree(
        cls,
        items: List[MenuItem],
        user_context: UserContext,
        user_preferences: Dict[str, Dict],
    ) -> List[Dict[str, Any]]:
        """
        Recursively filter menu tree based on access rights.
        Builds tree structure from flat MPTT queryset.
        """
        filtered_items = []
        items_by_id = {item.id: item for item in items}
        accessible_ids = set()

        # First pass: determine accessible items
        for item in items:
            has_access, reason = cls.has_item_access(item, user_context)
            if has_access:
                accessible_ids.add(item.id)
                # Check user preference to hide
                pref = user_preferences.get(item.code, {})
                if pref.get("is_hidden"):
                    accessible_ids.discard(item.id)

        # Second pass: build tree structure
        root_items = [item for item in items if item.parent_id is None]

        for root_item in root_items:
            if root_item.id in accessible_ids:
                item_dict = cls._build_tree_node(
                    root_item,
                    items_by_id,
                    accessible_ids,
                    user_context.user,
                    user_preferences,
                )

                # Only include parent if it has children or a path
                if item_dict:
                    if "children" in item_dict or item_dict.get("path"):
                        filtered_items.append(item_dict)

        # Sort by custom order if preferences exist
        def sort_key(item):
            pref = user_preferences.get(item["id"], {})
            custom_order = pref.get("custom_order")
            is_pinned = pref.get("is_pinned", False)

            # Pinned items come first, then by custom order, then normal order
            return (
                not is_pinned,  # False (pinned) sorts before True
                custom_order if custom_order is not None else float("inf"),
                item.get("label", ""),
            )

        filtered_items.sort(key=sort_key)

        return filtered_items

    @classmethod
    def _build_tree_node(
        cls,
        item: MenuItem,
        items_by_id: Dict,
        accessible_ids: Set,
        user: User,
        user_preferences: Dict[str, Dict],
    ) -> Optional[Dict[str, Any]]:
        """
        Recursively build a single tree node with its children.
        """
        if item.id not in accessible_ids:
            return None

        item_dict = cls.build_menu_item_dict(item, user, user_preferences)

        # Build children recursively
        children = []
        for child in item.get_children():
            if child.id in items_by_id and child.id in accessible_ids:
                child_dict = cls._build_tree_node(
                    child, items_by_id, accessible_ids, user, user_preferences
                )
                if child_dict:
                    children.append(child_dict)

        if children:
            # Sort children
            def sort_key(child):
                pref = user_preferences.get(child["id"], {})
                custom_order = pref.get("custom_order")
                return (
                    custom_order if custom_order is not None else float("inf"),
                    child.get("label", ""),
                )

            children.sort(key=sort_key)
            item_dict["children"] = children

        return item_dict

    @classmethod
    def get_filtered_menu(
        cls, user: User, tenant=None, use_cache: bool = True, log_access: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Main entry point: Get filtered menu for user.

        Args:
            user: Django User instance
            tenant: Optional tenant for multi-tenancy
            use_cache: Whether to use cached results
            log_access: Whether to log menu access

        Returns:
            List of filtered menu items as dicts
        """
        if not user.is_authenticated:
            return []

        # Check cache
        if use_cache:
            cache_key = cls.get_cache_key(user.id, tenant.id if tenant else None)
            cached_menu = cache.get(cache_key)
            if cached_menu is not None:
                return cached_menu

        # Build user context
        user_context = UserContext(user, tenant)

        # Get menu items with optimized query
        items = list(cls.get_menu_items_queryset(tenant))

        # Get user preferences in bulk
        user_preferences = cls.get_user_preferences(user, items)

        # Filter and build tree
        filtered_menu = cls.filter_menu_tree(items, user_context, user_preferences)

        # Cache results
        if use_cache:
            cache_key = cls.get_cache_key(user.id, tenant.id if tenant else None)
            cache.set(cache_key, filtered_menu, cls.CACHE_TIMEOUT)

        # Optional: Log access for analytics
        if log_access and filtered_menu:
            cls._log_menu_access(user, items, user_context)

        return filtered_menu

    @classmethod
    def _log_menu_access(
        cls, user: User, items: List[MenuItem], user_context: UserContext
    ):
        """
        Log menu access for analytics (async task recommended).
        """
        try:
            # Only log root level items the user can access
            root_items = [item for item in items if item.parent_id is None]
            logs = []

            for item in root_items:
                has_access, _ = cls.has_item_access(item, user_context)
                if has_access:
                    logs.append(MenuAccessLog(user=user, menu_item=item))

            # Bulk create for efficiency
            if logs:
                MenuAccessLog.objects.bulk_create(logs, ignore_conflicts=True)

        except Exception as e:
            logger.error(f"Failed to log menu access: {e}")

    @classmethod
    def prefetch_badge_cache(cls, user: User, items: List[MenuItem]):
        """
        Warm up badge cache for all menu items.
        Useful for initial page load optimization.
        """
        for item in items:
            if item.badge_resolver:
                cls.resolve_badge(item, user)


# Convenience function for views
def get_user_menu(user: User, tenant=None, **kwargs) -> List[Dict[str, Any]]:
    """
    Convenience function to get filtered menu for a user.

    Usage:
        from menu.services import get_user_menu
        menu = get_user_menu(request.user)
    """
    return MenuFilterService.get_filtered_menu(user, tenant, **kwargs)
