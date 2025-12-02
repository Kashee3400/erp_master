from django.urls import path, include
from .views.choices_view import ChoicesAPIView
from .views.medicine_transaction import UserMedicineTransactionViewSet
from rest_framework.routers import DefaultRouter
from .views import (
    CattleViewSet,
    CattleTaggingViewSet,
    CattleCurrentStatusViewSet,
    CattleStatusChoiceViewSet,
    TimeSlotViewSet,
    CattleCaseStatusViewSet,
    SpeciesViewSet,
    AIChargesViewSet,
    CaseCaseTypeViewSet,
    SpeciesBreedViewSet,
    MemberMasterCopyViewSet,
    MCCViewSet,
    BusinessHierarchyViewSet,
    VehicleViewSet,
    VehicleKilometerViewSet,
    InventoryDashboardViewSet,
    FarmerMeetingViewSet,
    FarmerObservationViewSet,
    ObservationTypeViewSet,
    MedicineStockViewSet,
    NonMemberViewSet,
    AdvancedCaseSearchView,
    CaseEntryViewSet,
    quick_visit_registration,
    search_owner,
    dashboard_stats,
    recent_cases,
    bulk_sync,
    TopLevelReporteesView,
    UserMedicineStockViewSet,
    NonMemberCattleViewSet,
    calculate_cost,
    DiseaseViewset,
    SymptomViewset,
    TreatmentCostViewset,
    PaymentMethodViewset,
)


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
router.register(r"payment-methods", PaymentMethodViewset, basename="paymentmethods")

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
router.register(
    r"inventory-dashboard", InventoryDashboardViewSet, basename="inventory-dashboard"
)

router.register(
    r"medicine-transactions",
    UserMedicineTransactionViewSet,
    basename="medicine-transactions",
)

router.register(r"non-members", NonMemberViewSet, basename="non-member")
router.register(
    r"non-member-cattle", NonMemberCattleViewSet, basename="non-member-cattle"
)
router.register(r"case-entries", CaseEntryViewSet, basename="case-entry")
router.register(r"diseases", DiseaseViewset, basename="diseases")
router.register(r"symptoms", SymptomViewset, basename="symptoms")
router.register(r"costs", TreatmentCostViewset, basename="costs")

urlpatterns = [
    path("", include(router.urls)),
    path("master-choices/", ChoicesAPIView.as_view(), name="master-choices"),
    path("reportees/", TopLevelReporteesView.as_view(), name="reportees"),
    path("quick-visit/", quick_visit_registration, name="quick_visit_registration"),
    path("search-owner/", search_owner, name="search_owner"),
    path("calculate-cost/", calculate_cost, name="calculate_cost"),
    path("dashboard-stats/", dashboard_stats, name="dashboard_stats"),
    path("recent-cases/", recent_cases, name="recent_cases"),
    path("bulk-sync/", bulk_sync, name="bulk_sync"),
    path("advanced-search/", AdvancedCaseSearchView.as_view(), name="advanced_search"),
]

"""
API Endpoints Documentation:

1. ViewSet Endpoints:
   - GET /api/non-members/ - List all non-members
   - POST /api/non-members/ - Create new non-member
   - GET /api/non-members/{id}/ - Get specific non-member
   - PUT/PATCH /api/non-members/{id}/ - Update non-member
   - DELETE /api/non-members/{id}/ - Delete non-member

   - GET /api/non-member-cattle/ - List all non-member cattle
   - POST /api/non-member-cattle/ - Create new non-member cattle
   - GET /api/non-member-cattle/{id}/ - Get specific cattle
   - PUT/PATCH /api/non-member-cattle/{id}/ - Update cattle
   - DELETE /api/non-member-cattle/{id}/ - Delete cattle

   - GET /api/case-entries/ - List all case entries
   - POST /api/case-entries/ - Create new case entry
   - GET /api/case-entries/{case_no}/ - Get specific case
   - PUT/PATCH /api/case-entries/{case_no}/ - Update case
   - DELETE /api/case-entries/{case_no}/ - Delete case

2. Custom Endpoints:
   - POST /api/quick-visit/ - Quick visit registration (mobile app friendly)
   - POST /api/search-owner/ - Search for owner by mobile number
   - POST /api/calculate-cost/ - Calculate treatment cost
   - GET /api/dashboard-stats/ - Get dashboard statistics
   - GET /api/recent-cases/ - Get recent cases
   - POST /api/bulk-sync/ - Bulk sync for mobile app
   - GET /api/advanced-search/ - Advanced search with multiple filters

3. Query Parameters:

   For case-entries list:
   - ?type=member or ?type=non_member - Filter by case type
   - ?status=pending - Filter by status
   - ?mobile=1234567890 - Filter by owner mobile
   - ?emergency=true - Show only emergency cases

   For non-members list:
   - ?mobile=123 - Search by mobile number

   For non-member-cattle list:
   - ?non_member_id=NM-20240101-1234 - Filter by non-member ID

   For recent-cases:
   - ?limit=10 - Limit number of results
   - ?type=member or ?type=non_member - Filter by case type

   For advanced-search:
   - ?search=term - General search term
   - ?date_from=2024-01-01 - Filter from date
   - ?date_to=2024-12-31 - Filter to date  
   - ?disease=fever - Filter by disease name
   - ?animal_type=buffalo - Filter by animal type

4. Request/Response Examples:

   Quick Visit Registration (POST /api/quick-visit/):
   {
     "is_member": false,
     "non_member_name": "John Doe",l̥
     "non_member_mobile": "9876543210",
     "non_member_address": "Village ABC",
     "animal_tag_number": "BUF001",
     "animal_type": "buffalo",
     "treatment_entry": "Member/Shahagah/Doctor",
     "disease_name": "Fever",
     "address": "Farm location",
     "visit_date": "2024-01-15T10:30:00Z",
     "is_tagged_animal": true,
     "is_emergency": false
   }

   Search Owner (POST /api/search-owner/):
   {
     "mobile_no": "9876543210"
   }

   Calculate Cost (POST /api/calculate-cost/):
   {
     "is_member": false,
     "visit_datetime": "2024-01-15T10:30:00Z",
     "is_tagged_animal": true,
     "is_emergency": false
   }

5. Authentication:
   All endpoints require authentication. Include Authorization header:
   Authorization: Token your-auth-token

   or for session-based:
   Include CSRF token in headers for POST requests.
"""
