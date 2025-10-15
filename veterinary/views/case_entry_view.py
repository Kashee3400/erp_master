# views.py
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
import error_formatter
from util.response import custom_response
from .choices_view import BaseModelViewSet
from ..models.models import NonMember, NonMemberCattle, MembersMasterCopy
from ..models.case_models import CaseEntry, TreatmentCostConfiguration
from ..serializers.case_entry_serializer import (
    NonMemberSerializer,
    NonMemberCattleSerializer,
    CaseEntrySerializer,
    QuickVisitRegistrationSerializer,
    CaseEntryListSerializer,
    OwnerSearchSerializer,
    CostCalculationSerializer,
    TreatmentCostConfigurationSerializer,
)
from rest_framework.decorators import action
from django.db.models import Count
from django.db.models.functions import TruncMonth
from ..choices import StatusChoices

class NonMemberViewSet(BaseModelViewSet):
    """ViewSet for managing non-members"""

    queryset = NonMember.objects.all()
    serializer_class = NonMemberSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "non_member_id"
    filterset_fields = ("is_deleted", "locale", "sync", "mobile_no")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TreatmentCostViewset(BaseModelViewSet):
    """ViewSet for managing non-members"""

    queryset = TreatmentCostConfiguration.objects.all()
    serializer_class = TreatmentCostConfigurationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"
    filterset_fields = (
        "is_deleted",
        "locale",
        "sync",
        "membership_type",
        "animal_tag_type",
        "treatment_type",
    )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class NonMemberCattleViewSet(BaseModelViewSet):
    """ViewSet for managing non-member cattle"""

    queryset = NonMemberCattle.objects.all()
    serializer_class = NonMemberCattleSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    filterset_fields = ("is_deleted", "locale", "sync", "non_member_id")


class CaseEntryViewSet(BaseModelViewSet):
    """Enhanced ViewSet for managing case entries (both member and non-member)"""
    queryset = CaseEntry.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = (
        "is_deleted",
        "locale",
        "sync",
        "status",
        "is_tagged_animal",
        "is_emergency",
    )
    lookup_field = "case_no"

    def get_serializer_class(self):
        if self.action == "list":
            return CaseEntryListSerializer
        return CaseEntrySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        request = self.request
        case_type = request.GET.get("type")
        mobile = request.GET.get("mobile")

        if case_type == "member":
            queryset = queryset.member_cases()
        elif case_type == "non_member":
            queryset = queryset.non_member_cases()

        if mobile:
            queryset = queryset.by_owner_mobile(mobile)

        return queryset.select_related(
            "cattle__owner", "non_member_cattle__non_member", "created_by"
        ).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    # ----------------------------
    # 🧭 Dashboard Statistics API
    # ----------------------------
    @action(detail=False, methods=["get"], url_path="dashboard")
    def dashboard(self, request):
        """
        Provides aggregated statistics for case entries.
        This endpoint replaces multiple client-side filtered requests.
        """
        qs = self.get_queryset()
        qs = qs.filter(created_by=self.request.user)
        total_cases = qs.count()
        today = timezone.localdate()
        today_cases = qs.filter(created_at__date=today).count()
        member_cases = qs.member_cases().count()
        non_member_cases = qs.non_member_cases().count()
        emergency_cases = qs.filter(is_emergency=True).count()

        # Status-based counts
        pending_cases = qs.filter(status=StatusChoices.PENDING).count()
        completed_cases = qs.filter(status=StatusChoices.COMPLETED).count()
        confirmed_cases = qs.filter(status=StatusChoices.CONFIRMED).count()
        cancelled_cases = qs.filter(status=StatusChoices.CANCELLED).count()

        recent_cases_qs = qs.order_by("-created_at")[:5]
        recent_cases = CaseEntryListSerializer(recent_cases_qs, many=True).data

        monthly_stats_qs = (
            qs.annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(count=Count("case_no"))
            .order_by("month")
        )
        cases_by_month = {
            entry["month"].strftime("%Y-%m"): entry["count"]
            for entry in monthly_stats_qs
            if entry["month"]
        }

        data = {
            "total_cases": total_cases,
            "member_cases": member_cases,
            "non_member_cases": non_member_cases,
            "emergency_cases": emergency_cases,
            "pending_cases": pending_cases,
            "today_cases": today_cases,
            "cancelled_cases": cancelled_cases,
            "completed_cases": completed_cases,
            "confirmed_cases": confirmed_cases,
            "recent_cases": recent_cases,
            "cases_by_month": cases_by_month,
        }

        return custom_response(
            status_text="success",
            data=data,
            message=_("Dashboard Loaded..."),
            status_code=status.HTTP_200_OK,
            errors={}
        )


from rest_framework import serializers


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def quick_visit_registration(request):
    """
    Quick visit registration endpoint for mobile app.
    Handles both member and non-member cases in a unified workflow.
    """

    serializer = QuickVisitRegistrationSerializer(
        data=request.data, context={"request": request}
    )

    try:
        serializer.is_valid(raise_exception=True)
        case_entry = serializer.create(serializer.validated_data)
        response_serializer = CaseEntrySerializer(case_entry)

        return custom_response(
            status_text="success",
            message=_("Visit registered successfully."),
            data=response_serializer.data,
            status_code=status.HTTP_201_CREATED,
        )

    except serializers.ValidationError as ve:
        # Handles invalid or missing data
        return custom_response(
            status_text="error",
            message=_("Validation failed."),
            errors=error_formatter.simplify_errors(ve.detail),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as e:
        # Handles unexpected runtime or database errors
        return custom_response(
            status_text="error",
            message=_("An unexpected error occurred during registration."),
            errors=error_formatter.format_exception(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def search_owner(request):
    """
    Search for owner (member or non-member) by mobile number
    Returns owner details and their cattle list
    """
    serializer = OwnerSearchSerializer(data=request.data)

    if serializer.is_valid():
        mobile = serializer.validated_data["mobile_no"]
        results = []
        members = MembersMasterCopy.objects.filter(
            mobile_no__icontains=mobile
        ).prefetch_related("cattle")

        for member in members:
            cattle_list = []
            for cattle in member.owned_cattles.filter(
                is_active=True
            ):  # Assuming is_active field
                cattle_list.append(
                    {
                        "id": cattle.id,
                        "tag_number": getattr(cattle, "tag_number", "N/A"),
                        "animal_type": getattr(cattle, "animal_type", "N/A"),
                        "breed": getattr(cattle, "breed", "N/A"),
                    }
                )

            results.append(
                {
                    "is_member": True,
                    "member_code": member.member_code,
                    "member_tr_code": member.member_tr_code,
                    "member_name": member.member_name,
                    "mobile": member.mobile_no,
                    "address": getattr(member, "address", ""),
                    "cattle_list": cattle_list,
                }
            )

        # Search in non-members
        non_members = NonMember.objects.filter(
            mobile_no__icontains=mobile
        ).prefetch_related("cattle")

        for non_member in non_members:
            cattle_list = []
            for cattle in non_member.cattle.filter(is_active=True):
                cattle_list.append(
                    {
                        "id": cattle.id,
                        "tag_number": cattle.tag_number,
                        "animal_type": cattle.animal_type,
                        "breed": cattle.breed or "N/A",
                    }
                )

            results.append(
                {
                    "is_member": False,
                    "member_code": non_member.non_member_id,
                    "member_tr_code": "",
                    "member_name": non_member.name,
                    "mobile": non_member.mobile_no,
                    "address": non_member.address,
                    "cattle_list": cattle_list,
                }
            )
        return custom_response(
            status_text="success",
            message=_("Visit registered successfully"),
            data=results,
            status_code=status.HTTP_200_OK,
        )

    return custom_response(
        status_text="error",
        message=_("Visit registration failed"),
        status_code=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def calculate_cost(request):
    """
    Calculate treatment cost based on member type, visit time, and other factors
    """
    serializer = CostCalculationSerializer(data=request.data)

    if serializer.is_valid():
        cost_data = serializer.calculate_cost()
        return custom_response(
            status_text="success",
            message=_("Cost calculated successfully"),
            data=cost_data,
            status_code=status.HTTP_200_OK,
        )
    return custom_response(
        status_text="error",
        message=_("Cost calculation failed"),
        status_code=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    """
    Get dashboard statistics for cases
    """
    from django.utils import timezone
    from datetime import timedelta

    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    stats = {
        "total_cases": CaseEntry.objects.count(),
        "member_cases": CaseEntry.objects.member_cases().count(),
        "non_member_cases": CaseEntry.objects.non_member_cases().count(),
        "pending_cases": CaseEntry.objects.filter(status="pending").count(),
        "emergency_cases": CaseEntry.objects.filter(is_emergency=True).count(),
        # Time-based stats
        "today_cases": CaseEntry.objects.filter(created_at__date=today).count(),
        "week_cases": CaseEntry.objects.filter(created_at__date__gte=week_ago).count(),
        "month_cases": CaseEntry.objects.filter(
            created_at__date__gte=month_ago
        ).count(),
        # Non-member stats
        "total_non_members": NonMember.objects.count(),
        "total_non_member_cattle": NonMemberCattle.objects.count(),
        # Status breakdown
        "status_breakdown": {
            "pending": CaseEntry.objects.filter(status="pending").count(),
            "in_progress": CaseEntry.objects.filter(status="in_progress").count(),
            "completed": CaseEntry.objects.filter(status="completed").count(),
            "cancelled": CaseEntry.objects.filter(status="cancelled").count(),
        },
    }
    return custom_response(
        status_text="success",
        message=_("Dashboard statistics calculated successfully"),
        data=stats,
        status_code=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def recent_cases(request):
    """
    Get recent cases for quick access
    """
    limit = int(request.query_params.get("limit", 10))
    case_type = request.query_params.get("type", None)

    queryset = CaseEntry.objects.all()

    if case_type == "member":
        queryset = queryset.member_cases()
    elif case_type == "non_member":
        queryset = queryset.non_member_cases()

    recent_cases_list = queryset.select_related(
        "cattle__owner", "non_member_cattle__non_member"
    ).order_by("-created_at")[:limit]

    serializer = CaseEntryListSerializer(recent_cases_list, many=True)
    return custom_response(
        status_text="success",
        message=_("Recent cases list retrieved successfully"),
        data=serializer.data,
        status_code=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def bulk_sync(request):
    """
    Bulk sync endpoint for mobile app
    Handles syncing multiple case entries at once
    """
    case_ids = request.data.get("case_ids", [])

    if not case_ids:
        return Response(
            {"success": False, "message": _("No case IDs provided")},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        updated_count = CaseEntry.objects.filter(case_no__in=case_ids).update(sync=True)

        # Also sync related non-members and cattle
        NonMember.objects.filter(cattle__cattle_cases__case_no__in=case_ids).update(
            sync=True
        )

        NonMemberCattle.objects.filter(cattle_cases__case_no__in=case_ids).update(
            sync=True
        )
        return custom_response(
            status_text="success",
            message=_("Bulk sync completed successfully"),
            data=updated_count,
            status_code=status.HTTP_200_OK,
        )

    except Exception as e:
        return custom_response(
            status_text="error",
            message=_("Failed to sync cases"),
            errors=error_formatter.format_exception(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# Optional: Custom filtering and search views
class AdvancedCaseSearchView(generics.ListAPIView):
    """
    Advanced search view with multiple filter options
    """

    serializer_class = CaseEntryListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = CaseEntry.objects.select_related(
            "cattle__owner", "non_member_cattle__non_member", "created_by"
        )

        # Multiple search parameters
        search_term = self.request.GET.get("search", None)
        date_from = self.request.GET.get("date_from", None)
        date_to = self.request.GET.get("date_to", None)
        disease = self.request.GET.get("disease", None)
        animal_type = self.request.GET.get("animal_type", None)

        if search_term:
            queryset = queryset.filter(
                Q(case_no__icontains=search_term)
                | Q(cattle__owner__name__icontains=search_term)
                | Q(non_member_cattle__non_member__name__icontains=search_term)
                | Q(disease_name__icontains=search_term)
                | Q(treatment_entry__icontains=search_term)
            )

        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)

        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        if disease:
            queryset = queryset.filter(disease_name__icontains=disease)

        if animal_type:
            queryset = queryset.filter(
                Q(cattle__animal_type__icontains=animal_type)
                | Q(non_member_cattle__animal_type__icontains=animal_type)
            )

        return queryset.order_by("-created_at")
