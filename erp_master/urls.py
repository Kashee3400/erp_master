from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from member.views import (
    MyHomePage,
    SahayakIncentivesAllInOneView,
    SahayakIncentivesUpdateView,
    SahayakIncentivesCreateView,
)
from django.conf.urls.static import static

admin.site.site_title = "ERP Admin"
admin.site.index_title = "Site administration"
admin.site.site_header = "ERP Administration"

from member.views import app_ads_txt

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
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
                  path("erp-fcm/", include("notifications.urls")),
                  path("i18n/", include("django.conf.urls.i18n")),
                  path('excel/api/', include('veterinary.excel_urls')),
                  path("app-ads.txt", app_ads_txt, name="app_ads_txt"),

                  # API Documentation
                  path("openapi/schema/", SpectacularAPIView.as_view(), name="schema"),
                  path(
                      "openapi/docs/swagger/",
                      SpectacularSwaggerView.as_view(url_name="schema"),
                      name="swagger-ui",
                  ),
                  path(
                      "openapi/docs/readoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
                  ),

                  path('celery/api/', include('veterinary.celery_urls', namespace='celery_monitor')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
