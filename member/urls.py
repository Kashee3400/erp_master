from django.urls import path,include
from .views import (
    GenerateOTPView,
    VerifyOTPView,
    VerifySession,
    LogoutView,
    UserAPiView,
    ProductRateListView,
    CdaAggregationDaywiseMilktypeViewSet,
    GenerateSahayakOTPView,
    VerifySahayakOTPView,
    LocalSaleViewSet,
    SahayakIncentivesViewSet,
    MonthListAPIView,
    ProductViewSet,
    MemberHierarchyViewSet,
    SahayakFeedbackViewSet,
    NewsViewSet,
    NewsNotReadCountAPIView,
    BillingMemberMasterViewSet,
    BillingMemberDetailViewSet,
    BankViewSet,
    MemberMasterViewSet,
    MppViewSet,
    LocalSaleTxnViewSet,
    SahayakDashboardAPI,
    ShiftViewSet,
    AppInstalledData,
    SahayakAppInstalledData,
    MppIncentiveSummaryAPIView,
)
from erp_app.views import *
from rest_framework_simplejwt.views import TokenRefreshView,TokenObtainPairView
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'users',UserAPiView , basename='user')
router.register(r'banks', BankViewSet, basename='bank')
router.register(r'member-masters', MemberMasterViewSet,basename="membermaster")
router.register(r'deductions', LocalSaleTxnViewSet,basename="deduction")
router.register(r'mpps', MppViewSet,basename="mpp")
router.register(r'billing-member-details', BillingMemberDetailViewSet)
router.register(r'cda-milktypes', CdaAggregationDaywiseMilktypeViewSet, basename='cda_milktypes')
router.register(r'sahayak-incentives', SahayakIncentivesViewSet, basename='sahayak-incentives')
router.register(r'local-sale', LocalSaleViewSet)
router.register(r'products', ProductViewSet,basename="products")
router.register(r'members', MemberHierarchyViewSet, basename='member')
router.register(r'feedback', SahayakFeedbackViewSet, basename='feedback')
router.register(r'news', NewsViewSet, basename='news')
router.register(r'billing-member-master', BillingMemberMasterViewSet)
router.register(r'shifts', ShiftViewSet,basename="shifts")


urlpatterns = [
    path('api/otp/generate/', GenerateOTPView.as_view(), name='generate-otp'),
    path('api/otp/verify/', VerifyOTPView.as_view(), name='verify-otp'),
    path('api/otp/sahayak/generate/', GenerateSahayakOTPView.as_view(), name='generate-sahayak-otp'),
    path('api/otp/sahayak/verify/', VerifySahayakOTPView.as_view(), name='verify-sahayak-otp'),
    path('api/verify/session/', VerifySession.as_view(), name='verify-session'),
    path('api/members/phone/', MemberByPhoneNumberView.as_view(), name='member-by-phone'),
    path('api/member-profile/', MemberProfileView.as_view(), name='member-profile'),
    path('api/members/billing-history/', BillingMemberDetailView.as_view(), name='member-billing-history'),
    path('api/mpp-collection/', MppCollectionAggregationListView.as_view(), name='mpp-collection-list'),
    path('api/new-mpp-collection/', NewMppCollectionAggregationListView.as_view(), name='new-mpp-collection-list'),
    path('api/mpp-collection-detail/', MppCollectionDetailView.as_view(), name='mpp-collection-detail'),
    path('api/member-share-final-info/', MemberShareFinalInfoView.as_view(), name='member-share-final-info'),
    path('api/mpp-incentive-summary/', MppIncentiveSummaryAPIView.as_view()),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/', include(router.urls)),
    path('api/product-rates/', ProductRateListView.as_view(), name='product_rate_list'),
    path('api/months/', MonthListAPIView.as_view(), name='month-list'),
    path('api/news/not-read-count/', NewsNotReadCountAPIView.as_view(), name='news-not-read-count'),
    path('api/sahayak-dashboard-data/', SahayakDashboardAPI.as_view(), name='sahayak-dashboard-data'),
    path('api/app-installed-data/', AppInstalledData.as_view(), name='app-installed-data'),
    path('api/sahayak-app-installed-data/', SahayakAppInstalledData.as_view(), name='sahayak-app-installed-data'),
    ]
