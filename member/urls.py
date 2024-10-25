from django.urls import path,include
from .views import GenerateOTPView, VerifyOTPView,VerifySession,LogoutView,UserAPiView,ProductRateListView,CdaAggregationDaywiseMilktypeViewSet
from erp_app.views import *
from rest_framework_simplejwt.views import TokenRefreshView,TokenObtainPairView
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'users',UserAPiView , basename='user')
router.register(r'cda-milktypes', CdaAggregationDaywiseMilktypeViewSet, basename='cda_milktypes')


urlpatterns = [
    path('api/otp/generate/', GenerateOTPView.as_view(), name='generate-otp'),
    path('api/otp/verify/', VerifyOTPView.as_view(), name='verify-otp'),
    path('api/verify/session/', VerifySession.as_view(), name='verify-session'),
    path('api/members/phone/', MemberByPhoneNumberView.as_view(), name='member-by-phone'),
    path('api/members/billing-history/', BillingMemberDetailView.as_view(), name='member-billing-history'),
    path('api/mpp-collection/', MppCollectionAggregationListView.as_view(), name='mpp-collection-list'),
    path('api/mpp-collection-detail/', MppCollectionDetailView.as_view(), name='mpp-collection-detail'),
    path('api/member-share-final-info/', MemberShareFinalInfoView.as_view(), name='member-share-final-info'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/', include(router.urls)),
    path('api/product-rates/', ProductRateListView.as_view(), name='product_rate_list'),
    
    ]
