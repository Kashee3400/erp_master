from rest_framework.routers import DefaultRouter
from .views.users_view import GroupViewSet, PermissionViewSet,UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'permissions', PermissionViewSet, basename='permission')

urlpatterns = router.urls
