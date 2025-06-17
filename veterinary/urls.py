from .views.views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"cattle-case-types", CattleCaseTypeViewSet)
router.register(r"time-slots", TimeSlotViewSet)
router.register(r"diagnosis-routes", DiagnosisRouteViewSet)
router.register(r"symptoms", SymptomsViewSet)
router.register(r"diseases", DiseaseViewSet)
router.register(r"cattle-tagging", CattleTaggingViewSet)
router.register(r"payment-methods", PaymentMethodViewSet)
router.register(r"caseentries", CaseEntryViewSet)

urlpatterns = [
    path("api/v1/", include(router.urls)),
]
