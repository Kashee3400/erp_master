from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views
from django.apps import apps

admin.site.site_title = 'ERP Admin'
admin.site.index_title = 'Site administration'
admin.site.site_header = 'ERP Administration'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('member.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', include(apps.get_app_config('oscar').urls[0])),
]
    
