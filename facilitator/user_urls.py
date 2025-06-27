from rest_framework.routers import DefaultRouter
from .views.users_view import GroupViewSet, PermissionViewSet,UserViewSet,UserProfileViewSet,SendOTPView,VerifyOTPView
from django.urls import path

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'user-profiles', UserProfileViewSet, basename='user-profiles')
urlpatterns = [
    path("send-email-otp/", SendOTPView.as_view(), name="send_email_otp"),
    path("verify-email-otp/", VerifyOTPView.as_view(), name="verify_email_otp"),
] + router.urls
