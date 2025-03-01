from rest_framework.routers import DefaultRouter
from .views.views import *
from django.urls import path, include, re_path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

router = DefaultRouter()
router.register(
    r"assigned-mpp", AssignedMppToFacilitatorViewSet, basename="assigned-mpp"
)
router.register(
    "incentives", SahayakIncentivesViewSet, basename="incentive"
)
router.register(r'shifts', ShiftViewSet,basename="shifts")

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("password/change/", ChangePasswordView.as_view(), name="password_change"),
    path("dashboard-data/", DashboardAPI.as_view(), name="dashboard_data"),
] + router.urls
