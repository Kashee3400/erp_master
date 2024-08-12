from django.urls import path,include
from rest_framework_simplejwt.views import TokenRefreshView

from rest_framework.routers import DefaultRouter
from .views import TblfarmercollectionViewSet,OldDataCollectionView

router = DefaultRouter()
router.register(r'farmercollections', TblfarmercollectionViewSet, basename='farmercollection')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/oldmpp-collection-detail/', OldDataCollectionView.as_view(), name='old-mpp-collection-detail'),
]
