# urls.py
from django.urls import path
from . import device_registration as views

urlpatterns = [
    path('api/register-device/', views.register_device, name='register_device'),
    path('api/send-notification/', views.send_user_notification, name='send_user_notification'),
]
