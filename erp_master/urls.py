from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from member.views import (
    MyHomePage,
    SahayakIncentivesAllInOneView,
    SahayakIncentivesUpdateView,
    SahayakIncentivesCreateView,
)
from django.conf.urls.static import static
from django.views.static import serve

admin.site.site_title = "ERP Admin"
admin.site.index_title = "Site administration"
admin.site.site_header = "ERP Administration"

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from notifications.views.deep_link_view import DeepLinkRedirectView

urlpatterns = [
    path("gateway/", include("gateway.phonepe_urls", namespace="phonepe")),
    path("open/", include("notifications.urls.deeplink", namespace="deeplink")),
    
    # Module-based universal deep links
    path("member/", DeepLinkRedirectView.as_view()),
    path("member/<path:rest>/", DeepLinkRedirectView.as_view()),

    path("sahayak/", DeepLinkRedirectView.as_view()),
    path("sahayak/<path:rest>/", DeepLinkRedirectView.as_view()),

    path("pes/", DeepLinkRedirectView.as_view()),
    path("pes/<path:rest>/", DeepLinkRedirectView.as_view()),

    re_path(
        r"^\.well-known/assetlinks\.json$",
        serve,
        {"document_root": settings.STATIC_ROOT, "path": ".well-known/assetlinks.json"},
    ),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("", MyHomePage.as_view(), name="home"),
    path(
        "sahayak-incentives/",
        SahayakIncentivesAllInOneView.as_view(),
        name="sahayak_incentives_list",
    ),
    path(
        "sahayak-incentives/create/",
        SahayakIncentivesCreateView.as_view(),
        name="sahayak_incentives_create",
    ),
    path(
        "sahayak-incentives/update/<int:pk>/",
        SahayakIncentivesUpdateView.as_view(),
        name="sahayak_incentives_update",
    ),
    path("admin/", admin.site.urls),
    path("member/", include("member.urls")),
    path("mpms/", include("mpms.urls")),
    path("facilitator/", include("facilitator.urls")),
    path("management/api/", include("facilitator.user_urls")),
    path("storage/api/", include("facilitator.file_urls")),
    path("veterinary/api/v1/", include("veterinary.urls")),
    path("feedback/", include("feedback.urls")),
    path("erp-fcm/api/", include("notifications.urls.notifications")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("excel/api/", include("veterinary.excel_urls")),
    # API Documentation
    path("openapi/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "openapi/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "openapi/docs/readoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("celery/api/", include("veterinary.celery_urls", namespace="celery_monitor")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
