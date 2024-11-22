from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from member.views import MyHomePage,MyAppLists,SahayakIncentivesAllInOneView,SahayakIncentivesUpdateView,SahayakIncentivesCreateView

from django.conf.urls.static import static
admin.site.site_title = 'ERP Admin'
admin.site.index_title = 'Site administration'
admin.site.site_header = 'ERP Administration'
from member.views import app_ads_txt

urlpatterns = [    
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path('',MyHomePage.as_view(),name='home'),
    path('list',MyAppLists.as_view(),name='list'),
    path('sahayak-incentives/', SahayakIncentivesAllInOneView.as_view(), name='sahayak_incentives_list'),
    path('sahayak-incentives/create/', SahayakIncentivesCreateView.as_view(), name='sahayak_incentives_create'),
    path('sahayak-incentives/update/<int:pk>/', SahayakIncentivesUpdateView.as_view(), name='sahayak_incentives_update'),
    path('export_selected/', MyAppLists.export_selected, name='export_selected'),
    path('delete_selected/', MyAppLists.delete_selected, name='delete_selected'),
    path('admin/', admin.site.urls),
    path('member/', include('member.urls')),
    path('mpms/', include('mpms.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('app-ads.txt', app_ads_txt, name='app_ads_txt'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
