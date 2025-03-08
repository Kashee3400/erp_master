from rest_framework.routers import DefaultRouter
from .views import views , vcg_api_views as api_view
from django.urls import path, include, re_path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

router = DefaultRouter()
router.register(
    r"assigned-mpp", views.AssignedMppToFacilitatorViewSet, basename="assigned-mpp"
)
router.register(
    "incentives", views.SahayakIncentivesViewSet, basename="incentive"
)
router.register(r'shifts', views.ShiftViewSet,basename="shifts")

router.register(r'attendances', api_view.VCGMemberAttendanceViewSet,basename="attendances")
router.register(r'zero-days-pouring-reports', api_view.ZeroDaysPouringReportViewSet,basename="zero-days-pouring-reports")
router.register(r'month-assignment', api_view.MonthAssignmentViewSet,basename="month-assignment")
router.register(r'member-complaint-reports', api_view.MemberComplaintReportViewSet,basename="member-complaint-reports")
router.register(r'zero-days-reasons', api_view.ZeroDaysReasonViewSet,basename="zero-days-reasons")
router.register(r'member-complaint-reasons', api_view.MemberComplaintReasonViewSet,basename="member-complaint-reasons")
router.register(r'upload-images', api_view.VCGMeetingImagesViewSet,basename="upload-images")
router.register(r'vcg-meetings', api_view.VCGMeetingViewSet,basename="vcg-meetings-reasons")

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("password/change/", views.ChangePasswordView.as_view(), name="password_change"),
    path("dashboard-data/", views.DashboardAPI.as_view(), name="dashboard_data"),
] + router.urls
