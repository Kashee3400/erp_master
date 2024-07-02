from django.urls import path
from .views import GenerateOTPView, VerifyOTPView,VerifySession,LogoutView
from erp_app.views import *
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('api/otp/generate/', GenerateOTPView.as_view(), name='generate-otp'),
    path('api/otp/verify/', VerifyOTPView.as_view(), name='verify-otp'),
    path('api/verify/session/', VerifySession.as_view(), name='verify-otp'),
    path('api/members/phone/', MemberByPhoneNumberView.as_view(), name='member-by-phone'),
    path('api/members/billing-history/', BillingMemberDetailView.as_view(), name='member-billing-history'),
    path('api/mpp-collection/', MppCollectionAggregationListView.as_view(), name='mpp-collection-list'),
    path('api/mpp-collection-detail/', MppCollectionDetailView.as_view(), name='mpp-collection-detail'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    # urls for ecommerce application
    path('brand/list/' , BrandListAPIView.as_view(), name='brand_list'),
    path('product/list/' , ProductListAPIView.as_view(), name='product_list')
]
