from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from ..serializers.reportees_serializers import ReporteeSerializer, UserProfile
from django.contrib.auth.models import User
from util.response import StandardResultsSetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import BasePermission


class CanViewOthersReportees(BasePermission):
    """
    Always allows access, but provides a helper to check
    if the user has permission to view other users' reportees.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    @staticmethod
    def can_view_others(user: User):
        return user.is_superuser or user.has_perm(
            "facilitator.can_view_others_reportees"
        )


from django.shortcuts import get_object_or_404
from django.db.models import Count


class TopLevelReporteesView(ListAPIView):
    pagination_class = StandardResultsSetPagination
    serializer_class = ReporteeSerializer
    permission_classes = [IsAuthenticated, CanViewOthersReportees]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["reports_to", "department", "is_email_verified", "is_verified"]

    def get_queryset(self):
        user = self.request.user
        target_user_id = self.request.query_params.get("user_id")

        # Determine whose reportees we are fetching
        if user.is_superuser or (
            user.is_staff and CanViewOthersReportees.can_view_others(user)
        ):
            # Staff/Admin can see any user's reportees
            if target_user_id:
                target_profile = get_object_or_404(UserProfile, user__id=target_user_id)
            else:
                target_profile = user.profile
        else:
            if target_user_id:
                target_profile = get_object_or_404(UserProfile, user__id=target_user_id)
            else:
                target_profile = user.profile

        queryset = (
            target_profile.reportees.select_related("user")
            .annotate(reportee_count=Count("reportees"))
            .order_by("user__username")
        )

        return queryset
