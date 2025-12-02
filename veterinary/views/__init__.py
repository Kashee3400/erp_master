# views/__init__.py

# Cattle entry views
from .cattle_entry_view import CattleViewSet, CattleTaggingViewSet

# Reportees
from .reportees_view import TopLevelReporteesView

# Case entry
from .case_entry_view import (
    CaseEntryViewSet,
    AdvancedCaseSearchView,
    NonMemberViewSet,
    NonMemberCattleViewSet,
    search_owner,
    recent_cases,
    bulk_sync,
    dashboard_stats,
    quick_visit_registration,
    calculate_cost,
    TreatmentCostViewset,
)

# Celery Views
from .celery_views import (
    CeleryDashboardAPIView,
    TasksAPIView,
    TasksByNameAPIView,
    TaskControlAPIView,
    QueueControlAPIView,
    QueueLengthAPIView,
    TaskDetailAPIView,
    TaskHistoryAPIView,
    RegisteredTasksAPIView,
    ReservedTasksAPIView,
    ScheduledTasksAPIView,
    WorkerStatsAPIView,
    WorkerControlAPIView,
)

# Choices views
from .choices_view import (
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
    DiseaseViewset,
    SymptomViewset,
    PaymentMethodViewset,
)

# Medicine stock views
from .medicine_stock_view import (
    MedicineStockViewSet,
    InventoryDashboardViewSet,
    UserMedicineStockViewSet,
)

# Optional: define __all__ to control what gets exported
__all__ = [
    "CattleViewSet",
    "CattleTaggingViewSet",
    "TopLevelReporteesView",
    "CattleCaseStatusViewSet",
    "SpeciesViewSet",
    "TimeSlotViewSet",
    "AIChargesViewSet",
    "CaseCaseTypeViewSet",
    "SpeciesBreedViewSet",
    "MemberMasterCopyViewSet",
    "MCCViewSet",
    "BusinessHierarchyViewSet",
    "CattleCurrentStatusViewSet",
    "CattleStatusChoiceViewSet",
    "VehicleKilometerViewSet",
    "VehicleViewSet",
    "FarmerObservationViewSet",
    "FarmerMeetingViewSet",
    "ObservationTypeViewSet",
    "MedicineStockViewSet",
    "InventoryDashboardViewSet",
    "UserMedicineStockViewSet",
    "CaseEntryViewSet",
    "NonMemberViewSet",
    "AdvancedCaseSearchView",
    "TasksAPIView",
    "TasksByNameAPIView",
    "TaskControlAPIView",
    "TaskDetailAPIView",
    "RegisteredTasksAPIView",
    "ReservedTasksAPIView",
    "ScheduledTasksAPIView",
    "WorkerStatsAPIView",
    "WorkerControlAPIView",
    "QueueControlAPIView",
    "QueueLengthAPIView",
    "TaskHistoryAPIView",
    "search_owner",
    "quick_visit_registration",
    "bulk_sync",
    "recent_cases",
    "dashboard_stats",
    "calculate_cost",
    "NonMemberCattleViewSet",
    "DiseaseViewset",
    "SymptomViewset",
    "TreatmentCostViewset",
    "PaymentMethodViewset",
    "CeleryDashboardAPIView",
]
