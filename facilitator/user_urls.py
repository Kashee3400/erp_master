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
)
from .views.auth import UpdateDeviceModuleAPIView
from .views.route_assignment import (
    BulkDeactivateView,
    BulkLocationAssignmentView,
    BulkLocationAssignmentViewWithSeparateMethods,
    RoutePreviewView,
    UserLocationsListView,
    UserLocationViewSet,
)
from django.urls import path


router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(r"groups", GroupViewSet, basename="group")
router.register(r"permissions", PermissionViewSet, basename="permission")
router.register(r"user-profiles", UserProfileViewSet, basename="user-profiles")
router.register(r"user-locations", UserLocationViewSet, basename="user-location")

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
    path(
        "device/update-module/",
        UpdateDeviceModuleAPIView.as_view(),
        name="update-device-module",
    ),
    # Bulk assignment
    path(
        "locations/bulk-assign/",
        BulkLocationAssignmentView.as_view(),
        name="bulk-location-assign",
    ),
    path(
        "locations/bulk-assign-method/",
        BulkLocationAssignmentViewWithSeparateMethods.as_view(),
        name="bulk-location-assign-method",
    ),
    # Preview route data before assignment
    path("locations/route-preview/", RoutePreviewView.as_view(), name="route-preview"),
    # List user locations
    path(
        "locations/user/<int:user_id>/",
        UserLocationsListView.as_view(),
        name="user-locations-list",
    ),
    # Bulk deactivate
    path(
        "locations/bulk-deactivate/",
        BulkDeactivateView.as_view(),
        name="bulk-location-deactivate",
    ),
] + router.urls
