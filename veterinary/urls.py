from .views.cattle_entry_view import CattleViewSet, CattleTaggingViewSet
from .views.reportees_view import TopLevelReporteesView
from .views.choices_view import (
    CattleCaseStatusViewSet,
    SpeciesViewSet,
    TimeSlotViewSet,
    AIChargesViewSet,
    CaseCaseTypeViewSet,
    SpeciesBreedViewSet,
    MemberMasterCopyViewSet,
    MCCViewSet,
    BusinessHierarchyViewSet,
    CattleCurrentStatusViewSet,
    CattleStatusChoiceViewSet,
    VehicleKilometerViewSet,
    VehicleViewSet,
    FarmerObservationViewSet,
    FarmerMeetingViewSet,
    ObservationTypeViewSet,
)
from .views.medicine_stock_view import (
    MedicineStockViewSet,
    InventoryDashboardViewSet,
    UserMedicineStockViewSet,
)
from django.urls import path, include
from .views.choices_view import ChoicesAPIView
from  .views.medicine_transaction import UserMedicineTransactionViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"cattles", CattleViewSet, basename="cattle")

router.register(r"cattle-tagging", CattleTaggingViewSet, basename="cattletagging")
router.register(r"cattle-statuses", CattleCurrentStatusViewSet, basename="cattlestatus")
router.register(
    r"cattle-status-choices", CattleStatusChoiceViewSet, basename="cattlestatuschoices"
)

router.register(r"time-slots", TimeSlotViewSet, basename="timeslots")

router.register(
    r"cattle-case-statuses", CattleCaseStatusViewSet, basename="cattlescasetatuses"
)

router.register(r"species", SpeciesViewSet, basename="species")

router.register(r"ai-charges", AIChargesViewSet, basename="aicharges")

router.register(r"case-types", CaseCaseTypeViewSet, basename="casetypes")

router.register(r"species-breed", SpeciesBreedViewSet, basename="speciesbreed")

router.register(r"members", MemberMasterCopyViewSet, basename="members")

router.register(r"mccs", MCCViewSet, basename="mccs")
router.register(r"mppsnapshots", BusinessHierarchyViewSet, basename="mppsnapshots")
router.register(r"vehicles", VehicleViewSet, basename="vehicles")
router.register(r"vehicle-logs", VehicleKilometerViewSet, basename="vehiclelogs")
router.register(r"farmer-meetings", FarmerMeetingViewSet, basename="farmermeetings")
router.register(
    r"farmer-observations", FarmerObservationViewSet, basename="farmerobservations"
)
router.register(
    r"observation-types", ObservationTypeViewSet, basename="observationtypes"
)

router.register(r"medicine-stocks", MedicineStockViewSet, basename="medicinestock")
router.register(
    r"user-medicine-stocks", UserMedicineStockViewSet, basename="usermedicinestock"
)
router.register(r"inventory-dashboard", InventoryDashboardViewSet, basename="inventory-dashboard")

router.register(r'medicine-transactions', UserMedicineTransactionViewSet, basename='medicine-transactions')

urlpatterns = [
    path("", include(router.urls)),
    path("master-choices/", ChoicesAPIView.as_view(), name="master-choices"),
    path("reportees/", TopLevelReporteesView.as_view(), name="reportees"),
]
