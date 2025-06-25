# urls.py
from django.urls import path, include
from . import device_registration as views
from rest_framework.routers import DefaultRouter
from .views import AppNotificationViewSet, UnreadNotificationCountView

router = DefaultRouter()
router.register(r"notifications", AppNotificationViewSet, basename="notifications")

urlpatterns = []

urlpatterns = [
    path("api/register-device/", views.register_device, name="register_device"),
    path(
        "api/notification-unread/",
        UnreadNotificationCountView.as_view(),
        name="notification-unread",
    ),
    path("api/", include(router.urls)),
]
