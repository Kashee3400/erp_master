from rest_framework.routers import DefaultRouter
from .views.file_handling_view import UploadedFileViewSet
from django.urls import path

router = DefaultRouter()
router.register(r'upload-files', UploadedFileViewSet, basename='upload-files')
urlpatterns = [] + router.urls
