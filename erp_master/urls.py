from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views

admin.site.site_title = 'ERP Admin'
admin.site.index_title = 'Site administration'
admin.site.site_header = 'ERP Administration'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('member.urls')),
]
