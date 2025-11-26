# ============================================
# urls.py
# ============================================

from django.urls import path
from ..views.deep_link_view import (
    DeepLinkRedirectView,
    DeepLinkInfoView,
    DeepLinkHealthCheckView,
)

app_name = "deeplink"

urlpatterns = [
    # Main redirect endpoint
    path("open/", DeepLinkRedirectView.as_view(), name="redirect"),
    path("open/<uuid:token>/", DeepLinkRedirectView.as_view(), name="redirect_token"),
    # API endpoints
    path("api/info/<uuid:token>/", DeepLinkInfoView.as_view(), name="info"),
    path("api/health/", DeepLinkHealthCheckView.as_view(), name="health"),
]
