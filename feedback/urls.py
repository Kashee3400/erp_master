from django.urls import path, include

from rest_framework.routers import DefaultRouter
from .views import FeedbackViewSet,FeedbackFileViewsets

router = DefaultRouter()
router.register(r"feedbacks", FeedbackViewSet, basename="feedbacks")
router.register(r"feedback-file", FeedbackFileViewsets, basename="feedback-file")


urlpatterns = [
    path("api/", include(router.urls)),
]
