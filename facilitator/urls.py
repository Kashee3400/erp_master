from rest_framework.routers import DefaultRouter
from .views import views , vcg_api_views as api_view,members_view as m_view
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
router.register(r'member-complaint-reports', api_view.MemberComplaintReportViewSet,basename="member-complaint-reports")
router.register(r'zero-days-reasons', api_view.ZeroDaysReasonViewSet,basename="zero-days-reasons")
router.register(r'member-complaint-reasons', api_view.MemberComplaintReasonViewSet,basename="member-complaint-reasons")
router.register(r'upload-images', api_view.VCGMeetingImagesViewSet,basename="upload-images")
router.register(r'vcg-meetings', api_view.VCGMeetingViewSet,basename="vcg-meetings-reasons")
router.register(r'dashboard-summary-data', views.DashboardSummaryViewSet,basename="dashboard-summary-data")
router.register(r'members', m_view.MemberHierarchyViewSet,basename="members")
router.register(r'local-sales', views.LocalSaleViewSet,basename="local_sales")
router.register(r'vcg-groups', api_view.VCGroupViewSet,basename="vcg-groups")


urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("password/change/", views.ChangePasswordView.as_view(), name="password_change"),
    path("dashboard-detail-data/", views.DashboardDetailAPI.as_view(), name="dashboard_detail_data"),
    path("monthly-assignment/", m_view.MonthlyDataView.as_view(), name="monthly_assignment"),
    path("poured-members/", views.GetPouredMembersData.as_view(), name="poured_members"),
    path("high-pourers/", views.GetHighPourerData.as_view(), name="high_pourers"),
    path("daily-mpp-collection/", views.GetDailyMppCollections.as_view(), name="daily_mpp_collection"),
    path("total-collection-qty/", views.GetTotalQtyForToday.as_view(), name="total_collection_qty"),
    path("total-members/", views.GetTotalMembersData.as_view(), name="total_collection_qty"),
    
] + router.urls
