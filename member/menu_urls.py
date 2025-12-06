# ============================================================================
# URLs Configuration
# ============================================================================

# menu/urls.py
"""
URL configuration for menu API
"""

from django.urls import path
from .menu_views import (
    MenuAPIView,
    MenuPathsAPIView,
    MenuPreferencesAPIView,
    MenuPreferenceDetailAPIView,
    MenuAnalyticsAPIView,
    MenuBadgeRefreshAPIView,
)

app_name = "menu"

urlpatterns = [
    # Main menu endpoints
    path("menu/", MenuAPIView.as_view(), name="menu"),
    path("paths/", MenuPathsAPIView.as_view(), name="menu-paths"),
    # User preferences
    path("preferences/", MenuPreferencesAPIView.as_view(), name="menu-preferences"),
    path(
        "preferences/<str:menu_code>/",
        MenuPreferenceDetailAPIView.as_view(),
        name="menu-preference-detail",
    ),
    # Analytics
    path("analytics/", MenuAnalyticsAPIView.as_view(), name="menu-analytics"),
    # Utilities
    path(
        "badges/refresh/",
        MenuBadgeRefreshAPIView.as_view(),
        name="menu-badges-refresh",
    ),
]
