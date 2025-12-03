"""
===========================================================================
 Django URL Configuration
 Comprehensive, production-grade URL mappings for the ERP platform.
===========================================================================

This module defines all primary URL routes for the system, including:

- Public home routes
- Universal Deep Link handlers (Android App Links + iOS Universal Links)
- API modules (Member, Sahayak, Facilitator, MPMS, Veterinary, etc.)
- Notification system (FCM, deep links)
- Static + Media handlers
- Documentation (OpenAPI / Swagger / Redoc)
- Admin Panel

Each module is clearly grouped and documented for maintainability.
"""

# ==========================================================================
# Django & Third-party Imports
# ==========================================================================
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from django.conf.urls.static import static

# Application Views
from member.views import (
    MyHomePage,
    SahayakIncentivesAllInOneView,
    SahayakIncentivesUpdateView,
    SahayakIncentivesCreateView,
)

# API Documentation (drf-spectacular)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

# ==========================================================================
# Admin Branding
# ==========================================================================
admin.site.site_title = "ERP Admin"
admin.site.index_title = "Site Administration"
admin.site.site_header = "ERP Administration"

# ==========================================================================
# URL Patterns
# ==========================================================================

urlpatterns = [
    # ----------------------------------------------------------------------
    # HOME PAGE
    # ----------------------------------------------------------------------
    path("", MyHomePage.as_view(), name="home"),
    # ----------------------------------------------------------------------
    # PAYMENT GATEWAY MODULES
    # ----------------------------------------------------------------------
    path("gateway/", include("gateway.phonepe_urls", namespace="phonepe")),
    # ----------------------------------------------------------------------
    # UNIVERSAL DEEP LINK ROUTER
    # Handles: Android App Links, iOS Universal Links
    # Auto-detects modules: member / sahayak / pes
    # ----------------------------------------------------------------------
    path("open/", include("notifications.urls.deeplink",namespace="deeplink")),

    # ----------------------------------------------------------------------
    # ANDROID APP LINKS VERIFICATION
    # https://domain/.well-known/assetlinks.json
    # ----------------------------------------------------------------------
    re_path(
        r"^\.well-known/assetlinks\.json$",
        serve,
        {
            "document_root": settings.STATIC_ROOT,
            "path": ".well-known/assetlinks.json",
        },
    ),
    # ----------------------------------------------------------------------
    # CKEditor 5 Integration
    # ----------------------------------------------------------------------
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    # ----------------------------------------------------------------------
    # SAHAYAK INCENTIVE MODULE
    # ----------------------------------------------------------------------
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
    # ----------------------------------------------------------------------
    # ADMIN PANEL
    # ----------------------------------------------------------------------
    path("admin/", admin.site.urls),
    # ----------------------------------------------------------------------
    # ERP API MODULES
    # ----------------------------------------------------------------------
    path("member/", include("member.urls")),
    path("mpms/", include("mpms.urls")),
    path("facilitator/", include("facilitator.urls")),
    # Management APIs
    path("management/api/", include("facilitator.user_urls")),
    # File Storage APIs
    path("storage/api/", include("facilitator.file_urls")),
    # Veterinary APIs (V1)
    path("veterinary/api/v1/", include("veterinary.urls")),
    # Feedback Module
    path("feedback/", include("feedback.urls")),
    # Firebase Cloud Messaging APIs
    path("erp-fcm/api/", include("notifications.urls.notifications")),
    # Internationalization (i18n)
    path("i18n/", include("django.conf.urls.i18n")),
    # Excel Import/Export APIs
    path("excel/api/", include("veterinary.excel_urls")),
    # ----------------------------------------------------------------------
    # API DOCUMENTATION
    # OpenAPI Schema + Swagger + Redoc
    # ----------------------------------------------------------------------
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
    # ----------------------------------------------------------------------
    # CELERY MONITORING APIs
    # ----------------------------------------------------------------------
    path("celery/api/", include("veterinary.celery_urls", namespace="celery_monitor")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
