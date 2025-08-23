# urls.py
from django.urls import path, include
from . import device_registration as views
from rest_framework.routers import DefaultRouter
from .views import (
    AppNotificationViewSet,
    UnreadNotificationCountView,
    AppNotification,
    NotificationDetailView,
    NotificationListView,
    mark_notification_read,
    archive_notification,
    mark_all_read,
    notification_stats,
    NotificationPreferencesView,
    NotificationPreferencesUpdateView
    
)

router = DefaultRouter()
router.register(r"notifications", AppNotificationViewSet, basename="notifications")

app_name = "notifications"

urlpatterns = [
    path("api/register-device/", views.register_device, name="register_device"),
    path(
        "api/notification-unread/",
        UnreadNotificationCountView.as_view(),
        name="notification-unread",
    ),
    path("api/", include(router.urls)),
    # API endpoints
    path("", NotificationListView.as_view(), name="list"),
    path("<uuid:uuid>/", NotificationDetailView.as_view(), name="detail"),
    path("<uuid:uuid>/read/", mark_notification_read, name="mark_read"),
    path("<uuid:uuid>/archive/", archive_notification, name="archive"),
    path("mark-all-read/", mark_all_read, name="mark_all_read"),
    path("stats/", notification_stats, name="stats"),
    # Preferences
    path("preferences/", NotificationPreferencesView.as_view(), name="preferences"),
    path(
        "preferences/<int:pk>/",
        NotificationPreferencesUpdateView.as_view(),
        name="preferences_update",
    ),
]
