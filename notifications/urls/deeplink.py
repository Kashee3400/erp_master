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
    path("", DeepLinkRedirectView.as_view(), name="redirect"),
    path("member/", DeepLinkRedirectView.as_view()),
    path("member/<path:rest>/", DeepLinkRedirectView.as_view()),
    path("sahayak/", DeepLinkRedirectView.as_view()),
    path("sahayak/<path:rest>/", DeepLinkRedirectView.as_view()),
    path("pes/", DeepLinkRedirectView.as_view()),
    path("pes/<path:rest>/", DeepLinkRedirectView.as_view()),
    path("<uuid:token>/", DeepLinkRedirectView.as_view(), name="redirect_token"),
    # API endpoints
    path("api/info/<uuid:token>/", DeepLinkInfoView.as_view(), name="info"),
    path("api/health/", DeepLinkHealthCheckView.as_view(), name="health"),
]
