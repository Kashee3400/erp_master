# urls.py
from django.urls import path
from .views import GenerateOTPView, VerifyOTPView
from erp_app.views import *

urlpatterns = [
    path('api/otp/generate/', GenerateOTPView.as_view(), name='generate-otp'),
    path('api/otp/verify/', VerifyOTPView.as_view(), name='verify-otp'),
    path('api/members/phone/<str:phone_number>/', MemberByPhoneNumberView.as_view(), name='member-by-phone'),
    path('api/members/billing-history/<str:member_code>/', BillingMemberDetailHistoryView.as_view(), name='member-billing-history'),
]
