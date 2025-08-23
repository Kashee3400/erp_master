from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework import viewsets, status
from ..models.models import Cattle, CattleTagging
from django.db.models import Count, Q, OuterRef, Subquery, Exists
from facilitator.authentication import ApiKeyAuthentication
from util.response import custom_response, StandardResultsSetPagination
from ..serializers.cattle_entry_serializers import (
    CattleSerializer,
    CattleListSerializer,
    serializers,
    CattleTaggingListSerializer,
    CattleTaggingSerializer,
    CattleDetailSerializer,
)
from facilitator.models.user_profile_model import UserProfile
from django.core.cache import cache
from rest_framework.decorators import action
from ..utils.compute_tag_stats import get_period_range
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class CattleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        "owner",
        "is_deleted",
        "breed__animal_type__id",
        "breed",
        "gender",
    ]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.action in ["list"]:
            return CattleListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return CattleDetailSerializer
        return CattleDetailSerializer

    def get_queryset(self):
        user = self.request.user
        base_qs = Cattle.objects.select_related(
            "owner", "breed", "current_status", "cattle_tagged"
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

        # MAIT or VETERINARIAN: only self-owned data
        if profile.department in [
            UserProfile.Department.MAIT,
            UserProfile.Department.VETERINARIAN,
        ]:
            return base_qs.filter(updated_by=user)

        # Supervisor via reportees: include own + subordinates
        reportee_ids = profile.reportees.values_list("user_id", flat=True)
        if reportee_ids.exists():
            return base_qs.filter(updated_by__in=[user.id, *reportee_ids])
        return base_qs.filter(updated_by=user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return custom_response(
            status_text="success",
            message="Cattle details retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save(updated_by=request.user)
            return custom_response(
                status_text="success",
                message="Cattle created successfully.",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED,
            )
        except serializers.ValidationError as e:
            return custom_response(
                status_text="error",
                message="Validation failed.",
                errors=e.detail,
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
            serializer.save(updated_by=request.user)
            return custom_response(
                status_text="success",
                message="Cattle updated successfully.",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        except serializers.ValidationError as e:
            return custom_response(
                status_text="error",
                message="Validation failed.",
                errors=e.detail,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete()
        return custom_response(
            status_text="success",
            message="Cattle deleted successfully.",
            data=None,
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        period = request.query_params.get("type", "week")
        date_str = request.query_params.get("date")

        start, end, prev_start, prev_end, input_date = get_period_range(
            date_str, period
        )
        if not start or not end:
            return custom_response(
                status_text="error",
                message="Invalid date or type.",
                data={},
                status_code=400,
            )

        qs_current = self.get_queryset().filter(
            created_at__gte=start, created_at__lt=end
        )
        qs_previous = self.get_queryset().filter(
            created_at__gte=prev_start, created_at__lt=prev_end
        )

        # 🔢 Get counts for both
        current_stats = qs_current.aggregate(
            total=Count("id"),
            alive=Count("id", filter=Q(is_alive=True)),
            male=Count("id", filter=Q(gender="male")),
            female=Count("id", filter=Q(gender="female")),
        )
        current_stats["dead"] = current_stats["total"] - current_stats["alive"]

        previous_stats = qs_previous.aggregate(
            total=Count("id"),
            alive=Count("id", filter=Q(is_alive=True)),
            male=Count("id", filter=Q(gender="male")),
            female=Count("id", filter=Q(gender="female")),
        )
        previous_stats["dead"] = previous_stats["total"] - previous_stats["alive"]

        def pct_change(curr, prev):
            return round(((curr - prev) / (prev + 1e-6)) * 100, 2)

        percent_stats = {
            key: pct_change(current_stats[key], previous_stats.get(key, 0))
            for key in current_stats
        }

        return custom_response(
            status_text="success",
            message="Cattle statistics with period comparison fetched successfully.",
            data={
                "meta": {
                    "period_type": period,
                    "input_date": str(input_date.date()),
                    "start_date": str(start.date()),
                    "end_date": str(end.date()),
                    "previous_start": str(prev_start.date()),
                    "previous_end": str(prev_end.date()),
                },
                "stats": current_stats,
                "percentage_change": percent_stats,
            },
            status_code=status.HTTP_200_OK,
        )


from rest_framework.parsers import MultiPartParser, FormParser


class CattleTaggingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    parser_classes = (MultiPartParser, FormParser)
    filterset_fields = ["cattle", "tag_method", "tag_location", "tag_action"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.action == "list":
            return CattleTaggingListSerializer
        return CattleTaggingSerializer

    def get_queryset(self):
        user = self.request.user
        base_qs = CattleTagging.objects.select_related("cattle")

        if user.is_superuser or user.is_staff:
            return base_qs

        profile = getattr(user, "profile", None)
        if not profile:
            return base_qs.none()

        # Admins get full access
        if profile.department == UserProfile.Department.ADMIN:
            return base_qs

        # MAIT/Vet: only own records
        if profile.department in [
            UserProfile.Department.MAIT,
            UserProfile.Department.VETERINARIAN,
        ]:
            return base_qs.filter(updated_by=user)

        # Supervisor: own + reportees' records
        reportee_ids = profile.reportees.values_list("user_id", flat=True)
        if reportee_ids.exists():
            return base_qs.filter(updated_by__in=[user.id, *reportee_ids])

        # Default fallback: only own records
        return base_qs.filter(updated_by=user)

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        period = request.query_params.get("type", "week")
        date_str = request.query_params.get("date")

        start, end, prev_start, prev_end, input_date = get_period_range(
            date_str, period
        )
        if not start or not end:
            return custom_response(
                status_text="error",
                message="Invalid date or type. Supported types: day, week, month, year.",
                data={},
                status_code=400,
            )

        user = request.user

        def get_role_based_cattle_qs(from_date, to_date):
            qs = Cattle.objects.select_related(
                "owner", "breed", "current_status", "cattle_tagged"
            ).filter(created_at__gte=from_date, created_at__lt=to_date)

            if user.is_superuser or user.is_staff:
                return qs
            if hasattr(user, "profile"):
                profile = user.profile
                if profile.department == UserProfile.Department.ADMIN:
                    return qs
                elif profile.department in [
                    UserProfile.Department.MAIT,
                    UserProfile.Department.VETERINARIAN,
                ]:
                    return qs.filter(owner=user)
                else:
                    reportee_ids = profile.reportees.values_list("user_id", flat=True)
                    return qs.filter(owner__in=[user.id, *reportee_ids])
            return qs.none()

        def pct_change(curr, prev):
            return round(((curr - prev) / (prev + 1e-6)) * 100, 2)

        # 🔄 Current period
        tagging_qs = self.get_queryset().filter(
            created_at__gte=start, created_at__lt=end
        )
        cattle_qs = get_role_based_cattle_qs(start, end)

        # ⏮️ Previous period
        prev_tagging_qs = self.get_queryset().filter(
            created_at__gte=prev_start, created_at__lt=prev_end
        )
        prev_cattle_qs = get_role_based_cattle_qs(prev_start, prev_end)

        # 🎯 Cattle stats
        total_cattle = cattle_qs.count()
        tagged = cattle_qs.filter(cattle_tagged__isnull=False).count()
        untagged = total_cattle - tagged

        prev_total_cattle = prev_cattle_qs.count()
        prev_tagged = prev_cattle_qs.filter(cattle_tagged__isnull=False).count()
        prev_untagged = prev_total_cattle - prev_tagged

        # 🏷️ Tagging stats
        tagging_stats = {
            "total_tags": tagging_qs.count(),
            "manual_tags": tagging_qs.filter(tag_method="manual").count(),
            "electronic_tags": tagging_qs.filter(tag_method="electronic").count(),
            "replaced_tags": tagging_qs.exclude(replaced_on=None).count(),
        }
        prev_tagging_stats = {
            "total_tags": prev_tagging_qs.count(),
            "manual_tags": prev_tagging_qs.filter(tag_method="manual").count(),
            "electronic_tags": prev_tagging_qs.filter(tag_method="electronic").count(),
            "replaced_tags": prev_tagging_qs.exclude(replaced_on=None).count(),
        }

        cattle_stats = {
            "total_cattle": total_cattle,
            "tagged_cattle": tagged,
            "untagged_cattle": untagged,
        }
        prev_cattle_stats = {
            "total_cattle": prev_total_cattle,
            "tagged_cattle": prev_tagged,
            "untagged_cattle": prev_untagged,
        }

        # 📈 Percentage change
        tagging_change = {
            key: pct_change(tagging_stats[key], prev_tagging_stats.get(key, 0))
            for key in tagging_stats
        }
        cattle_change = {
            key: pct_change(cattle_stats[key], prev_cattle_stats.get(key, 0))
            for key in cattle_stats
        }

        # 🧾 Final response
        data = {
            "meta": {
                "period_type": period,
                "input_date": str(input_date.date()),
                "start_date": str(start.date()),
                "end_date": str(end.date()),
                "previous_start": str(prev_start.date()),
                "previous_end": str(prev_end.date()),
            },
            "tagging_stats": tagging_stats,
            "tagging_change": tagging_change,
            "cattle_stats": cattle_stats,
            "cattle_change": cattle_change,
        }

        return custom_response(
            status_text="success",
            message="Cattle and tagging statistics with trend comparison retrieved successfully.",
            data=data,
            status_code=status.HTTP_200_OK,
        )

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
            message="Tagging detail fetched successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save(updated_by=request.user)
            return custom_response(
                status_text="success",
                message="Cattle tag created successfully.",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED,
            )
        except serializers.ValidationError as e:
            return custom_response(
                status_text="error",
                message="Validation failed.",
                errors=e.detail,
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
            serializer.save(updated_by=request.user)
            return custom_response(
                status_text="success",
                message="Cattle tag updated successfully.",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        except serializers.ValidationError as e:
            return custom_response(
                status_text="error",
                message="Validation failed.",
                errors=e.detail,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return custom_response(
            status_text="success",
            message="Cattle tag deleted successfully.",
            data=None,
            status_code=status.HTTP_204_NO_CONTENT,
        )
