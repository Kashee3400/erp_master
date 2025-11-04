# views/choice_view.py

from rest_framework.views import APIView

from error_formatter import simplify_errors
from ..choices.choices import serialize_choices
from ..choices.choices import (
    PaymentMethodChoices,
    AnimalUse,
    GenderChoices,
    UserRoleChoices,
    TagMethodChoices,
    TagLocationChoices,
    TagActionChoices,
    MonthChoices,
    MedicineFormChoices,
    TransactionTypeChoices,
    ActionTypeChoices,
    CaseTypeChoices,
    PeriodChoices,
    StatusChoices,
    CattleStatusChoices,
    DiseaseSeverity,
    PaymentStatusChoices,
    TransferTypeChoices,
    TransferStatusChoices,
    LocationTypeChoices,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets, status
from facilitator.authentication import ApiKeyAuthentication
from util.response import custom_response, StandardResultsSetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from ..serializers.choices_serializers import *
from ..serializers.cattle_entry_serializers import (
    CattleStatusLogSerializer,
    CattleStatusLog,
)
from rest_framework_simplejwt.authentication import JWTAuthentication

from facilitator.models.user_profile_model import UserProfile
from veterinary.models.case_models import Disease, Symptoms


class ChoicesAPIView(APIView):
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [AllowAny]
    """Return all model choice enums used in the application."""

    def get(self, request):
        data = {
            "payment_methods": serialize_choices(PaymentMethodChoices),
            "animal_use": serialize_choices(AnimalUse),
            "gender": serialize_choices(GenderChoices),
            "user_roles": serialize_choices(UserRoleChoices),
            "tag_methods": serialize_choices(TagMethodChoices),
            "tag_locations": serialize_choices(TagLocationChoices),
            "tag_actions": serialize_choices(TagActionChoices),
            "months": serialize_choices(MonthChoices),
            "medicine_forms": serialize_choices(MedicineFormChoices),
            "transaction_types": serialize_choices(TransactionTypeChoices),
            "action_types": serialize_choices(ActionTypeChoices),
            "case_types": serialize_choices(CaseTypeChoices),
            "periods": serialize_choices(PeriodChoices),
            "workflow_status": serialize_choices(StatusChoices),
            "cattle_status": serialize_choices(CattleStatusChoices),
            "disease_severity": serialize_choices(DiseaseSeverity),
            "payment_status": serialize_choices(PaymentStatusChoices),
            "transfer_types": serialize_choices(TransferTypeChoices),
            "transfer_status": serialize_choices(TransferStatusChoices),
            "location_types": serialize_choices(LocationTypeChoices),
        }

        return custom_response(
            status_text="success",
            message="Choices retrieved",
            data=data,
            status_code=status.HTTP_200_OK,
        )


from ..permissions import UserHierarchyChecker


class BaseModelViewSet(viewsets.ModelViewSet):
    """
    A reusable base viewset for handling common CRUD operations with:
    - API key authentication
    - Standard pagination
    - Custom responses
    """

    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields = None
    ordering = None
    lookup_field = "pk"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hierarchy_checker = UserHierarchyChecker()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return custom_response(
            status_text="success",
            message="Record retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            instance = serializer.instance
            instance.refresh_from_db()
            response_serializer = self.get_serializer(instance)
            return custom_response(
                status_text="success",
                message="Record created successfully.",
                data=response_serializer.data,
                status_code=status.HTTP_201_CREATED,
            )
        except serializers.ValidationError as e:
            return custom_response(
                status_text="error",
                message="Validation failed.",
                errors=simplify_errors(error_dict=e.detail),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=kwargs.get("partial", False),
            context={"request": request},
        )
        try:
            serializer.is_valid(raise_exception=True)
            instance = serializer.save(updated_by=request.user)
            self.perform_update(serializer)

            # 🔑 refresh instance to include M2M members
            instance.refresh_from_db()

            response_serializer = self.get_serializer(instance)
            return custom_response(
                status_text="success",
                message="Record updated successfully.",
                data=response_serializer.data,
                status_code=status.HTTP_200_OK,
            )
        except serializers.ValidationError as e:
            return custom_response(
                status_text="error",
                message="Validation failed.",
                errors=simplify_errors(error_dict=e.detail),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete()
        return custom_response(
            status_text="success",
            message="Record deleted successfully.",
            data=None,
            status_code=status.HTTP_200_OK,
        )

    def get_manageable_users(self, user):
        """Get list of user IDs that this user can manage (including themselves)."""
        from django.contrib.auth import get_user_model

        User = get_user_model()

        manageable_ids = [user.id]

        try:
            if user.is_superuser:
                return list(User.objects.values_list("id", flat=True))

            # Check hierarchy for all other users
            all_users = User.objects.select_related("profile").exclude(id=user.id)

            for potential_subordinate in all_users:
                if self.hierarchy_checker.is_supervisor_of(user, potential_subordinate):
                    manageable_ids.append(potential_subordinate.id)

        except Exception:
            # Fallback to just the user themselves
            pass

        return manageable_ids


class SpeciesViewSet(BaseModelViewSet):
    queryset = Species.objects.all()
    filterset_fields = ["is_deleted", "sync", "locale"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.action in ["list"]:
            return SpeciesListSerializer
        return SpeciesDetailSerializer


class SpeciesBreedViewSet(BaseModelViewSet):
    serializer_class = SpeciesBreedSerializer
    queryset = SpeciesBreed.objects.all()
    filterset_fields = ["is_deleted", "sync", "breed", "locale", "animal_type__id"]


class TimeSlotViewSet(BaseModelViewSet):
    serializer_class = TimeSlotSerializer
    queryset = TimeSlot.objects.all()
    filterset_fields = ["is_deleted", "sync", "locale"]


class AIChargesViewSet(BaseModelViewSet):
    serializer_class = AIChargeSerializer
    queryset = AICharge.objects.all()
    filterset_fields = ["is_deleted", "sync", "locale"]


class CattleCaseStatusViewSet(BaseModelViewSet):
    serializer_class = CattleCaseStatusSerializer
    queryset = CattleCaseStatus.objects.all()
    filterset_fields = ["is_deleted", "sync", "locale"]


class CaseCaseTypeViewSet(BaseModelViewSet):
    serializer_class = CattleCaseTypeSerializer
    queryset = CattleCaseType.objects.all()
    filterset_fields = ["is_deleted", "sync", "locale"]


class MCCViewSet(BaseModelViewSet):
    serializer_class = MccSerializer
    queryset = Mcc.objects.all()
    filterset_fields = ["is_active", "mcc_code", "mcc_ex_code"]
    search_fields = ["mcc_name"]
    ordering_fields = ["mcc_ex_code"]
    ordering = ["mcc_ex_code"]


class BusinessHierarchyViewSet(BaseModelViewSet):
    serializer_class = BusinessHierarchySnapshotSerializer
    queryset = BusinessHierarchySnapshot.objects.all()
    filterset_fields = [
        "mcc_tr_code",
        "mcc_code",
        "mpp_code",
        "mpp_ex_code",
        "mpp_tr_code",
    ]
    search_fields = ["mcc_name", "mpp_code", "mpp_ex_code"]
    ordering_fields = ["mpp_ex_code"]
    ordering = ["mpp_ex_code"]


class MemberMasterCopyViewSet(BaseModelViewSet):
    queryset = MembersMasterCopy.objects.all()
    filterset_fields = ["mcc_code", "mpp_code", "mobile_no", "is_active", "is_default"]

    def get_serializer_class(self):
        if self.action in ["list"]:
            return MembersMasterListSerializer
        return MembersMasterDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        member_code = self.request.GET.get("member_code")
        member = self.queryset.filter(
            member_code=member_code, is_active=True, is_default=True
        ).first()

        serializer = self.get_serializer(member)
        
        return custom_response(
            status_text="success",
            message="Member details retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class CattleCurrentStatusViewSet(BaseModelViewSet):
    serializer_class = CattleStatusLogSerializer
    queryset = CattleStatusLog.objects.all()
    filterset_fields = ["cattle"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]


from ..serializers.cattle_entry_serializers import CattleStatusTypeSerializer
from ..models.common_models import CattleStatusType


class CattleStatusChoiceViewSet(BaseModelViewSet):
    serializer_class = CattleStatusTypeSerializer
    queryset = CattleStatusType.objects.all()
    filterset_fields = ["label", "locale"]
    ordering_fields = ["label"]
    ordering = ["label"]


class VehicleViewSet(BaseModelViewSet):
    serializer_class = VehicleSerializer
    queryset = Vehicle.objects.all()
    filterset_fields = ["vehicle_type", "locale"]
    ordering_fields = ["model_name"]
    ordering = ["model_name"]


class VehicleKilometerViewSet(BaseModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = VehicleKilometerLogSerializer

    def get_queryset(self):
        user = self.request.user
        base_qs = VehicleKiloMeterLog.objects.select_related("user", "vehicle")

        # Full access for admin/superusers
        if user.is_superuser or user.is_staff:
            return base_qs

        profile = getattr(user, "profile", None)
        if not profile:
            return base_qs.none()

        # Admin-level department: full access
        if profile.department == UserProfile.Department.ADMIN:
            return base_qs

        # Supervisor via reportees: include own + subordinates
        reportee_ids = profile.reportees.values_list("user_id", flat=True)
        if reportee_ids.exists():
            return base_qs.filter(user__in=[user.id, *reportee_ids])

        return base_qs.filter(user=user)


from ..serializers.cattle_entry_serializers import (
    FarmerMeetingSerializer,
    ObservationSerializer,
    FarmerObservationSerializer,
    FarmerMeeting,
    FarmerObservation,
    ObservationType,
)


class FarmerMeetingViewSet(BaseModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FarmerMeetingSerializer
    filterset_fields = ["mcc_code", "mpp_code", "updated_by", "members", "is_deleted"]

    def get_queryset(self):
        user = self.request.user
        base_qs = FarmerMeeting.objects.select_related("updated_by").prefetch_related(
            "members"
        )

        # Full access for admin/superusers
        if user.is_superuser or user.is_staff:
            return base_qs

        profile = getattr(user, "profile", None)
        if not profile:
            return base_qs.none()

        # Admin-level department: full access
        if profile.department == UserProfile.Department.ADMIN:
            return base_qs

        # Supervisor via reportees: include own + subordinates
        reportee_ids = profile.reportees.values_list("user_id", flat=True)
        if reportee_ids.exists():
            return base_qs.filter(updated_by__in=[user.id, *reportee_ids])

        return base_qs.filter(updated_by=user)


class ObservationTypeViewSet(BaseModelViewSet):
    serializer_class = ObservationSerializer
    queryset = ObservationType.objects.all()
    filterset_fields = ["locale"]
    ordering_fields = ["name"]
    ordering = ["name"]


class FarmerObservationViewSet(BaseModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FarmerObservationSerializer
    filterset_fields = ["mcc_code", "mpp_code", "updated_by", "member", "animal"]

    def get_queryset(self):
        user = self.request.user
        base_qs = FarmerObservation.objects.select_related(
            "updated_by", "member", "animal"
        )

        # Full access for admin/superusers
        if user.is_superuser or user.is_staff:
            return base_qs

        profile = getattr(user, "profile", None)
        if not profile:
            return base_qs.none()

        # Admin-level department: full access
        if profile.department == UserProfile.Department.ADMIN:
            return base_qs

        # Supervisor via reportees: include own + subordinates
        reportee_ids = profile.reportees.values_list("user_id", flat=True)
        if reportee_ids.exists():
            return base_qs.filter(updated_by__in=[user.id, *reportee_ids])

        return base_qs.filter(updated_by=user)


from ..serializers.disease_serializer import SymptomSerializer, DiseaseSerializer


class SymptomViewset(BaseModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = SymptomSerializer
    filterset_fields = ["locale"]
    queryset = Disease.objects.all()


from django_filters import rest_framework as filters


class DiseaseFilter(filters.FilterSet):
    symptoms = filters.CharFilter(method="filter_symptoms")

    def filter_symptoms(self, queryset, name, value):
        """
        Support comma-separated IDs in ?symptoms=1,2,3
        """
        ids = value.split(",")
        return queryset.filter(symptoms__id__in=ids).distinct()

    class Meta:
        model = Disease
        fields = ["symptoms", "severity", "locale"]


class DiseaseViewset(BaseModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = DiseaseSerializer
    queryset = Disease.objects.all()
    filterset_class = DiseaseFilter
