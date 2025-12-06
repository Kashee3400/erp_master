# menu/views.py
"""
Django REST Framework API endpoints for menu system.
Provides filtered menu, user preferences, and analytics.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.core.cache import cache
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db import models
from .menu_config import MenuFilterService, get_user_menu
from .menu_model import MenuItem, UserMenuPreference, MenuAccessLog
from .menu_serializer import (
    MenuItemSerializer,
    UserMenuPreferenceSerializer,
    MenuPreferencesBulkUpdateSerializer,
)
from util.response import ResponseMixin
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# Main Menu API View
# ============================================================================


class MenuAPIView(APIView, ResponseMixin):
    """
    GET /api/menu/
    Returns dynamically filtered menu based on authenticated user's roles.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="refresh",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Force cache refresh",
            ),
            OpenApiParameter(
                name="include_analytics",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Include usage analytics (admin only)",
            ),
        ],
        responses={200: MenuItemSerializer(many=True)},
        description="Get filtered menu for authenticated user",
    )
    def get(self, request):
        user = request.user

        refresh = request.query_params.get("refresh", "false").lower() == "true"
        include_analytics = (
            request.query_params.get("include_analytics", "false").lower() == "true"
        )

        tenant = getattr(user, "tenant", None) if hasattr(user, "tenant") else None

        try:
            use_cache = not refresh

            filtered_menu = MenuFilterService.get_filtered_menu(
                user=user,
                tenant=tenant,
                use_cache=use_cache,
                log_access=True,
            )

            response_data = {
                "menu": filtered_menu,
                "cached": use_cache and not refresh,
                "timestamp": cache.get(f"menu_timestamp_{user.id}") or "now",
            }

            if include_analytics and (
                user.is_superuser or user.has_perm("menu.view_menuaccesslog")
            ):
                response_data["analytics"] = self._get_menu_analytics(user)

            return self.success_response(
                data=response_data,
                message="Menu loaded successfully",
            )

        except Exception as e:
            logger.error(f"Error fetching menu for user {user.id}: {e}", exc_info=True)

            return self.error_response(
                message="Failed to load menu",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors=str(e),
            )

    def _get_menu_analytics(self, user):
        """Extract menu usage analytics (last 7 days)"""
        from django.utils import timezone
        from datetime import timedelta

        since = timezone.now() - timedelta(days=7)
        logs = (
            MenuAccessLog.objects.filter(user=user, accessed_at__gte=since)
            .values("menu_item__code")
            .annotate(access_count=models.Count("id"))
            .order_by("-access_count")[:10]
        )
        return list(logs)


# ============================================================================
# Menu Paths API (for Route Guards)
# ============================================================================


class MenuPathsAPIView(APIView, ResponseMixin):
    """
    GET /api/menu/paths/

    Returns flat list of all accessible paths for route validation.
    Useful for frontend navigation guards.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: {
                "type": "object",
                "properties": {
                    "paths": {"type": "array", "items": {"type": "string"}},
                    "internal_paths": {"type": "array", "items": {"type": "string"}},
                    "external_paths": {"type": "array", "items": {"type": "string"}},
                    "count": {"type": "integer"},
                },
            }
        },
        description="Get all accessible menu paths for route guards",
    )
    def get(self, request):
        user = request.user

        try:
            tenant = getattr(user, "tenant", None) if hasattr(user, "tenant") else None

            # Get filtered menu tree
            filtered_menu = MenuFilterService.get_filtered_menu(user, tenant)

            internal_paths = []
            external_paths = []

            def extract_paths(items):
                for item in items:
                    path = item.get("path")
                    if path:
                        if item.get("is_external"):
                            external_paths.append(path)
                        else:
                            internal_paths.append(path)

                    # Recursive traversal
                    if item.get("children"):
                        extract_paths(item["children"])

            extract_paths(filtered_menu)

            response_data = {
                "paths": internal_paths + external_paths,
                "internal_paths": internal_paths,
                "external_paths": external_paths,
                "count": len(internal_paths) + len(external_paths),
            }

            return self.success_response(
                data=response_data,
                message="Menu paths retrieved successfully",
            )

        except Exception as e:
            logger.error(
                f"Error fetching menu paths for user {user.id}: {e}", exc_info=True
            )

            return self.error_response(
                message="Failed to load menu paths",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors=str(e),
            )


# ============================================================================
# User Preferences API
# ============================================================================


class MenuPreferencesAPIView(APIView, ResponseMixin):
    """
    GET /api/menu/preferences/ - Get user's menu preferences
    POST /api/menu/preferences/ - Bulk update preferences
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: UserMenuPreferenceSerializer(many=True)},
        description="Get user menu preferences",
    )
    def get(self, request):
        """Get all menu preferences for the authenticated user"""
        try:
            preferences = UserMenuPreference.objects.filter(
                user=request.user
            ).select_related("menu_item")

            serializer = UserMenuPreferenceSerializer(preferences, many=True)

            return self.success_response(
                data=serializer.data,
                message="Menu preferences fetched successfully",
            )

        except Exception as e:
            logger.error(
                f"Error fetching preferences for user {request.user.id}: {e}",
                exc_info=True,
            )
            return self.error_response(
                message="Failed to load preferences",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors=str(e),
            )

    @extend_schema(
        request=MenuPreferencesBulkUpdateSerializer,
        responses={200: UserMenuPreferenceSerializer(many=True)},
        description="Bulk update menu preferences",
    )
    def post(self, request):
        """Bulk update menu preferences"""
        serializer = MenuPreferencesBulkUpdateSerializer(data=request.data)

        if not serializer.is_valid():
            return self.error_response(
                message="Invalid preference data",
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors,
            )

        preferences_data = serializer.validated_data["preferences"]
        user = request.user

        try:
            with transaction.atomic():
                updated_preferences = []

                for pref_data in preferences_data:
                    menu_code = pref_data.pop("menu_code")

                    # Validate menu item
                    try:
                        menu_item = MenuItem.objects.get(code=menu_code)
                    except MenuItem.DoesNotExist:
                        logger.warning(
                            f"Menu code '{menu_code}' does not exist, skipping."
                        )
                        continue

                    # insert/update
                    preference, created = UserMenuPreference.objects.update_or_create(
                        user=user,
                        menu_item=menu_item,
                        defaults=pref_data,
                    )
                    updated_preferences.append(preference)

                # Invalidate user cache
                MenuFilterService.invalidate_user_cache(
                    user.id,
                    tenant_id=getattr(user, "tenant_id", None),
                )

                result_serializer = UserMenuPreferenceSerializer(
                    updated_preferences, many=True
                )

                return self.success_response(
                    data={
                        "preferences": result_serializer.data,
                        "updated_count": len(updated_preferences),
                    },
                    message="Preferences updated successfully",
                )

        except Exception as e:
            logger.error(
                f"Error updating preferences for user {user.id}: {e}", exc_info=True
            )

            return self.error_response(
                message="Failed to update preferences",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors=str(e),
            )


class MenuPreferenceDetailAPIView(APIView, ResponseMixin):
    """
    GET    /api/menu/preferences/<menu_code>/  - Get specific preference
    PUT    /api/menu/preferences/<menu_code>/  - Update preference
    DELETE /api/menu/preferences/<menu_code>/  - Delete preference (reset)
    """

    permission_classes = [IsAuthenticated]

    def get_menu_item(self, menu_code):
        """Helper: returns MenuItem or None."""
        try:
            return MenuItem.objects.get(code=menu_code)
        except MenuItem.DoesNotExist:
            return None

    # -------------------------------
    # GET — Fetch preference
    # -------------------------------
    def get(self, request, menu_code):
        menu_item = self.get_menu_item(menu_code)
        if not menu_item:
            return self.error_response(
                message="Menu item not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        try:
            preference = UserMenuPreference.objects.get(
                user=request.user,
                menu_item=menu_item,
            )
            serializer = UserMenuPreferenceSerializer(preference)

            return self.success_response(
                data=serializer.data,
                message="Menu preference fetched successfully",
            )

        except UserMenuPreference.DoesNotExist:
            return self.error_response(
                message="No custom preference set",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            logger.error(
                f"Error fetching preference for user {request.user.id}: {e}",
                exc_info=True,
            )
            return self.error_response(
                message="Failed to fetch preference",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors=str(e),
            )

    # -------------------------------
    # PUT — Update preference
    # -------------------------------
    def put(self, request, menu_code):
        menu_item = self.get_menu_item(menu_code)
        if not menu_item:
            return self.error_response(
                message="Menu item not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        try:
            preference, created = UserMenuPreference.objects.update_or_create(
                user=request.user,
                menu_item=menu_item,
                defaults=request.data,
            )

            # Invalidate cache
            MenuFilterService.invalidate_user_cache(
                request.user.id,
                tenant_id=getattr(request.user, "tenant_id", None),
            )

            serializer = UserMenuPreferenceSerializer(preference)

            return self.success_response(
                data=serializer.data,
                message="Menu preference updated successfully",
            )

        except Exception as e:
            logger.error(
                f"Error updating preference for user {request.user.id}: {e}",
                exc_info=True,
            )

            return self.error_response(
                message="Failed to update preference",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors=str(e),
            )

    # -------------------------------
    # DELETE — Reset preference
    # -------------------------------
    def delete(self, request, menu_code):
        menu_item = self.get_menu_item(menu_code)
        if not menu_item:
            return self.error_response(
                message="Menu item not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        try:
            deleted_count, _ = UserMenuPreference.objects.filter(
                user=request.user,
                menu_item=menu_item,
            ).delete()

            if deleted_count > 0:
                MenuFilterService.invalidate_user_cache(
                    request.user.id,
                    tenant_id=getattr(request.user, "tenant_id", None),
                )

            return self.success_response(
                data={"detail": "Preference reset to default"},
                message="Preference removed successfully",
                status_code=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(
                f"Error deleting preference for user {request.user.id}: {e}",
                exc_info=True,
            )

            return self.error_response(
                message="Failed to delete preference",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors=str(e),
            )


# ============================================================================
# Menu Analytics API (Admin Only)
# ============================================================================
class MenuAnalyticsAPIView(APIView, ResponseMixin):
    """
    GET /api/menu/analytics/
    Menu usage analytics (admin only).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get menu analytics"""

        # -------------------------------
        # Permission check
        # -------------------------------
        if not (
            request.user.is_superuser
            or request.user.has_perm("menu.view_menuaccesslog")
        ):
            return self.error_response(
                message="Permission denied",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        try:
            from django.db.models import Count
            from django.utils import timezone
            from datetime import timedelta

            # -------------------------------
            # Days range (default: 7)
            # -------------------------------
            days = int(request.query_params.get("days", 7))
            since = timezone.now() - timedelta(days=days)

            logs = MenuAccessLog.objects.filter(accessed_at__gte=since)

            # -------------------------------
            # Most accessed menu items
            # -------------------------------
            most_accessed = (
                logs.values("menu_item__code", "menu_item__label")
                .annotate(access_count=Count("id"))
                .order_by("-access_count")[:20]
            )

            # -------------------------------
            # User engagement
            # -------------------------------
            unique_users = logs.values("user").distinct().count()
            total_accesses = logs.count()

            response_data = {
                "period_days": days,
                "total_accesses": total_accesses,
                "unique_users": unique_users,
                "most_accessed_items": list(most_accessed),
                "avg_accesses_per_user": (
                    total_accesses / unique_users if unique_users > 0 else 0
                ),
            }

            return self.success_response(
                data=response_data,
                message="Menu analytics retrieved successfully",
            )

        except Exception as e:
            logger.error(
                f"Error fetching menu analytics for user {request.user.id}: {e}",
                exc_info=True,
            )

            return self.error_response(
                message="Failed to load menu analytics",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors=str(e),
            )


# ============================================================================
# Badge Refresh API
# ============================================================================


class MenuBadgeRefreshAPIView(APIView, ResponseMixin):
    """
    POST /api/menu/badges/refresh/
    Force refresh of menu badge counts.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Refresh badge counts for user's menu"""
        try:
            user = request.user
            tenant = getattr(user, "tenant", None) if hasattr(user, "tenant") else None

            # Get all menu items with badge resolvers
            items = MenuItem.objects.filter(
                is_active=True,
                is_visible=True,
                badge_resolver__isnull=False,
            )

            # Filter by tenant if applicable
            if tenant:
                from django.db.models import Q

                items = items.filter(Q(tenant=tenant) | Q(tenant__isnull=True))

            items_list = list(items)

            # Refresh and prefetch badge cache
            MenuFilterService.prefetch_badge_cache(user, items_list)

            return self.success_response(
                data={
                    "items_refreshed": len(items_list),
                },
                message="Badge counts refreshed successfully",
            )

        except Exception as e:
            logger.error(
                f"Error refreshing menu badges for user {request.user.id}: {e}",
                exc_info=True,
            )

            return self.error_response(
                message="Failed to refresh menu badges",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors=str(e),
            )
