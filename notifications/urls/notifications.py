# urls.py
from django.urls import path
from ..views import device_registration as views
from ..views.notification_view import (
    UnreadNotificationCountView,
    NotificationDetailView,
    NotificationListView,
    mark_notification_read,
    archive_notification,
    mark_all_read,
    notification_stats,
    NotificationPreferencesView,
    NotificationPreferencesUpdateView,
)

app_name = "notification"

urlpatterns = [
    path("register-device/", views.register_device, name="register_device"),
    path(
        "notification-unread/",
        UnreadNotificationCountView.as_view(),
        name="notification-unread",
    ),
    path("notifications/", NotificationListView.as_view(), name="notifications"),
    path(
        "notifications/<uuid:uuid>/",
        NotificationDetailView.as_view(),
        name="notifications-detail",
    ),
    path("notifications/<uuid:uuid>/read/", mark_notification_read, name="mark_read"),
    path("notifications/<uuid:uuid>/archive/", archive_notification, name="archive"),
    path("notifications/mark-all-read/", mark_all_read, name="mark_all_read"),
    path("notifications/stats/", notification_stats, name="stats"),
    # Preferences
    path(
        "notifications/preferences/",
        NotificationPreferencesView.as_view(),
        name="preferences",
    ),
    path(
        "notifications/preferences/<int:pk>/",
        NotificationPreferencesUpdateView.as_view(),
        name="preferences_update",
    ),
]
