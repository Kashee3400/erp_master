from django.contrib import admin
from django.urls import path, include
from django.apps import apps
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from erp_app.mysites import new_admin_site
admin.site.site_title = 'ERP Admin'
admin.site.index_title = 'Site administration'
admin.site.site_header = 'ERP Administration'
from member.views import app_ads_txt

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path("erpadmin/", new_admin_site.urls),
    path('member/', include('member.urls')),
    path('mpms/', include('mpms.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('app-ads.txt', app_ads_txt, name='app_ads_txt'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
