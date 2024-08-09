from django.contrib import admin
from django.urls import path, include
from django.apps import apps
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

admin.site.site_title = 'ERP Admin'
admin.site.index_title = 'Site administration'
admin.site.site_header = 'ERP Administration'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('member/', include('member.urls')),
    path('mpms/', include('mpms.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path("oscarapi/", include("oscarapi.urls")),
    path('', include(apps.get_app_config('oscar').urls[0])),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
