from rest_framework.routers import DefaultRouter
from .views.users_view import GroupViewSet, PermissionViewSet,UserViewSet,UserProfileViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'user-profiles', UserProfileViewSet, basename='user-profiles')

urlpatterns = router.urls
