from rest_framework.routers import DefaultRouter
from .views.users_view import (
    GroupViewSet,
    PermissionViewSet,
    UserViewSet,
    UserProfileViewSet,
    SendOTPView,
    VerifyOTPView,
    create_update_user_profile,
    clear_device,
    clear_module,
    UserLocationListView,
)
from django.urls import path


router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(r"groups", GroupViewSet, basename="group")
router.register(r"permissions", PermissionViewSet, basename="permission")
router.register(r"user-profiles", UserProfileViewSet, basename="user-profiles")
urlpatterns = [
    path("send-email-otp/", SendOTPView.as_view(), name="send_email_otp"),
    path("verify-email-otp/", VerifyOTPView.as_view(), name="verify_email_otp"),
    path(
        "user-profile-update/",
        create_update_user_profile,
        name="create_update_user_profile",
    ),
    path("device/clear/", clear_device, name="clear-device"),
    path("module/clear/", clear_module, name="clear-module"),
    path("my-locations/", UserLocationListView.as_view(), name="my-locations"),
] + router.urls
