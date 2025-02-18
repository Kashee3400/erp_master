from rest_framework.routers import DefaultRouter
from .views.views import *
from django.urls import path, include, re_path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

router = DefaultRouter()
router.register(
    r"assigned-mpp", AssignedMppToFacilitatorViewSet, basename="assigned-mpp"
)
router.register(
    r"cda-aggregation", CdaAggregationDaywiseMilktypeViewSet, basename="cda-aggregation"
)

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
] + router.urls
