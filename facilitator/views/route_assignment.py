from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from util.response import custom_response, ResponseMixin
from ..serializers.route_assignment import *
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication


class BulkLocationAssignmentView(APIView):
    """
    API endpoint for bulk assignment of user locations based on hierarchy level.

    Supports three assignment levels:
    1. MCC Level - Assign user to Market Collection Center
    2. ROUTE Level - Assign user to a specific route
    3. MPP Level - Assign user to all MPPs under a route

    Examples:

    POST /api/locations/bulk-assign/

    # MCC Level Assignment
    {
        "user_id": 123,
        "assignment_level": "mcc",
        "mcc_code": "MCC001",
        "set_as_primary": true,
        "remarks": "Regional manager assignment"
    }

    # ROUTE Level Assignment
    {
        "user_id": 456,
        "assignment_level": "route",
        "route_code": "RT001",
        "set_as_primary": true,
        "remarks": "Route supervisor assignment"
    }

    # MPP Level Assignment
    {
        "user_id": 789,
        "assignment_level": "mpp",
        "route_code": "RT001",
        "set_as_primary": false,
        "remarks": "Field officer assignment"
    }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BulkLocationAssignmentSerializer(
            data=request.data, context={"request": request}
        )

        if not serializer.is_valid():
            return Response(
                {
                    "status": "error",
                    "message": "Location assignment failed",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = serializer.save()
            assignment_level = result["assignment_level"]

            # Build response based on assignment level
            response_data = self._build_response_data(result, assignment_level)

            # Generate appropriate success message
            message = self._generate_success_message(result, assignment_level)

            return custom_response(
                status_text="success",
                message=message,
                data=response_data,
                status_code=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return custom_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                status_text="error",
                message="An error occurred during bulk assignment",
                errors=str(e),
            )

    def _build_response_data(self, result, assignment_level):
        """
        Build response data structure based on assignment level.
        """
        base_response = {
            "user_id": result["user"].id,
            "username": result["user"].username,
            "assignment_level": assignment_level,
            "created_count": result["created_count"],
            "skipped_count": result["skipped_count"],
            "total_processed": result["created_count"] + result["skipped_count"],
        }

        # Add level-specific identifiers
        if assignment_level == RouteLevelChoice.LEVEL_MCC:
            base_response["mcc_code"] = result.get("mcc_code")
            base_response["assignment_type"] = "MCC Level Assignment"
            base_response["scope"] = "Market Collection Center"

        elif assignment_level == RouteLevelChoice.LEVEL_ROUTE:
            base_response["route_code"] = result.get("route_code")
            base_response["assignment_type"] = "Route Level Assignment"
            base_response["scope"] = "Single Route"

        elif assignment_level == RouteLevelChoice.LEVEL_MPP:
            base_response["route_code"] = result.get("route_code")
            base_response["assignment_type"] = "MPP Level Assignment"
            base_response["scope"] = "All MPPs in Route"

        # Add created and skipped locations
        base_response["created_locations"] = UserLocationDetailSerializer(
            result["created_locations"], many=True
        ).data
        base_response["skipped_locations"] = result["skipped_locations"]

        return base_response

    def _generate_success_message(self, result, assignment_level):
        """
        Generate appropriate success message based on assignment level.
        """
        created = result["created_count"]
        skipped = result["skipped_count"]
        total = created + skipped

        if assignment_level == RouteLevelChoice.LEVEL_MCC:
            if created == 0 and skipped > 0:
                return f"No new MCC assignments created. {skipped} location(s) already exist."
            elif created > 0 and skipped == 0:
                return f"Successfully assigned user to {created} MCC location(s)."
            else:
                return f"Assigned {created} MCC location(s). {skipped} already existed."

        elif assignment_level == RouteLevelChoice.LEVEL_ROUTE:
            if created == 0 and skipped > 0:
                return "Route assignment already exists for this user."
            elif created == 1:
                return "Successfully assigned user to route."
            else:
                return f"Route assignment processed."

        elif assignment_level == RouteLevelChoice.LEVEL_MPP:
            if created == 0 and skipped > 0:
                return f"No new MPP assignments created. All {skipped} MPP(s) already assigned."
            elif created > 0 and skipped == 0:
                return f"Successfully assigned user to {created} MPP location(s) in the route."
            else:
                return f"Assigned {created} new MPP(s). {skipped} MPP(s) were already assigned."

        # Fallback message
        return f"Successfully processed {total} location(s): {created} created, {skipped} skipped."


# ============================================================================
# ALTERNATIVE: Separate view methods for each level (Optional Approach)
# ============================================================================


class BulkLocationAssignmentViewWithSeparateMethods(APIView):
    """
    Alternative implementation with separate handler methods for each level.
    Provides more explicit control over level-specific logic.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BulkLocationAssignmentSerializer(
            data=request.data, context={"request": request}
        )

        if not serializer.is_valid():
            return Response(
                {
                    "status": "error",
                    "message": "Location assignment failed",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = serializer.save()
            assignment_level = result["assignment_level"]

            # Route to level-specific response builder
            if assignment_level == RouteLevelChoice.LEVEL_MCC:
                return self._mcc_level_response(result)
            elif assignment_level == RouteLevelChoice.LEVEL_ROUTE:
                return self._route_level_response(result)
            elif assignment_level == RouteLevelChoice.LEVEL_MPP:
                return self._mpp_level_response(result)

        except Exception as e:
            return custom_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                status_text="error",
                message="An error occurred during bulk assignment",
                errors=str(e),
            )

    def _mcc_level_response(self, result):
        """Build response for MCC level assignment."""
        created = result["created_count"]
        skipped = result["skipped_count"]

        message = (
            f"Successfully assigned user to {created} MCC location(s)."
            if created > 0 and skipped == 0
            else (
                f"Assigned {created} MCC location(s). {skipped} already existed."
                if created > 0
                else f"No new assignments. All {skipped} MCC location(s) already exist."
            )
        )

        return custom_response(
            status_text="success",
            message=message,
            data={
                "user_id": result["user"].id,
                "username": result["user"].username,
                "assignment_level": "mcc",
                "assignment_type": "MCC Level Assignment",
                "mcc_code": result.get("mcc_code"),
                "scope": "Market Collection Center",
                "created_count": created,
                "skipped_count": skipped,
                "total_processed": created + skipped,
                "created_locations": UserLocationDetailSerializer(
                    result["created_locations"], many=True
                ).data,
                "skipped_locations": result["skipped_locations"],
                "hierarchy_populated": ["mcc_code", "mcc_name", "mcc_tr_code"],
                "null_fields": ["route_*", "mpp_*"],
            },
            status_code=status.HTTP_201_CREATED,
        )

    def _route_level_response(self, result):
        """Build response for ROUTE level assignment."""
        created = result["created_count"]
        skipped = result["skipped_count"]

        message = (
            "Successfully assigned user to route."
            if created == 1
            else (
                "Route assignment already exists."
                if skipped == 1
                else "Route assignment processed."
            )
        )

        return custom_response(
            status_text="success",
            message=message,
            data={
                "user_id": result["user"].id,
                "username": result["user"].username,
                "assignment_level": "route",
                "assignment_type": "Route Level Assignment",
                "route_code": result.get("route_code"),
                "scope": "Single Route (includes parent MCC)",
                "created_count": created,
                "skipped_count": skipped,
                "total_processed": created + skipped,
                "created_locations": UserLocationDetailSerializer(
                    result["created_locations"], many=True
                ).data,
                "skipped_locations": result["skipped_locations"],
                "hierarchy_populated": ["mcc_*", "route_*"],
                "null_fields": ["mpp_*"],
            },
            status_code=status.HTTP_201_CREATED,
        )

    def _mpp_level_response(self, result):
        """Build response for MPP level assignment."""
        created = result["created_count"]
        skipped = result["skipped_count"]

        message = (
            f"Successfully assigned user to {created} MPP location(s)."
            if created > 0 and skipped == 0
            else (
                f"Assigned {created} new MPP(s). {skipped} already existed."
                if created > 0
                else f"No new assignments. All {skipped} MPP(s) already assigned."
            )
        )

        return custom_response(
            status_text="success",
            message=message,
            data={
                "user_id": result["user"].id,
                "username": result["user"].username,
                "assignment_level": "mpp",
                "assignment_type": "MPP Level Assignment",
                "route_code": result.get("route_code"),
                "scope": f"All MPPs in Route {result.get('route_code')}",
                "created_count": created,
                "skipped_count": skipped,
                "total_processed": created + skipped,
                "mpp_count": created + skipped,
                "created_locations": UserLocationDetailSerializer(
                    result["created_locations"], many=True
                ).data,
                "skipped_locations": result["skipped_locations"],
                "hierarchy_populated": ["mcc_*", "route_*", "mpp_*"],
                "null_fields": [],
            },
            status_code=status.HTTP_201_CREATED,
        )


class RoutePreviewView(APIView):
    """
    Preview what will be assigned for a given route code.

    GET /api/locations/route-preview/?route_code=R001&level=mpp
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        route_code = request.query_params.get("route_code")
        level = request.query_params.get("level", RouteLevelChoice.LEVEL_MPP)

        if not route_code:
            return Response(
                {"success": False, "error": "route_code parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get hierarchy data
        hierarchy_records = BusinessHierarchySnapshot.objects.filter(
            route_code=route_code, is_default=True
        )

        if not hierarchy_records.exists():
            return Response(
                {
                    "success": False,
                    "error": f"No records found for route code '{route_code}'",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get count based on level
        if level == RouteLevelChoice.LEVEL_MCC:
            count = hierarchy_records.values("mcc_code").distinct().count()
            preview_data = hierarchy_records.values(
                "mcc_code", "mcc_name", "mcc_tr_code"
            ).distinct()
        elif level == RouteLevelChoice.LEVEL_ROUTE:
            count = 1
            preview_data = hierarchy_records.values(
                "mcc_code",
                "mcc_name",
                "mcc_tr_code",
                "route_code",
                "route_name",
                "route_ex_code",
            ).first()
        else:
            count = hierarchy_records.count()
            preview_data = RouteHierarchySerializer(hierarchy_records, many=True).data

        # Get route summary
        first_record = hierarchy_records.first()

        return custom_response(
            status_text="success",
            message=f"Successfully fetched route details for {first_record.route_name}",
            data={
                "route_code": route_code,
                "route_name": first_record.route_name,
                "assignment_level": level,
                "locations_count": count,
                "hierarchy_preview": preview_data,
                "company_name": first_record.company_name,
                "plant_name": first_record.plant_name,
                "mcc_name": first_record.mcc_name,
            },
            status_code=status.HTTP_200_OK,
        )


class UserLocationsListView(APIView):
    """
    List all locations for a specific user.

    GET /api/locations/user/<user_id>/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"success": False, "error": f"User with ID {user_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get all active locations
        locations = UserLocation.objects.filter(user=user, active=True).select_related(
            "assigned_by"
        )

        # Get statistics
        stats = {
            "total": locations.count(),
            "primary": locations.filter(is_primary=True).count(),
            "by_level": {
                "mcc": locations.filter(level=RouteLevelChoice.LEVEL_MCC).count(),
                "route": locations.filter(level=RouteLevelChoice.LEVEL_ROUTE).count(),
                "mpp": locations.filter(level=RouteLevelChoice.LEVEL_MPP).count(),
            },
        }
        return custom_response(
            status_text="success",
            message=f"Successfully fetched data for {user.username}",
            data={
                "user_id": user.id,
                "username": user.username,
                "statistics": stats,
                "locations": UserLocationDetailSerializer(locations, many=True).data,
            },
            status_code=status.HTTP_200_OK,
        )


class BulkDeactivateView(APIView):
    """
    Bulk deactivate locations for a user by route code.

    POST /api/locations/bulk-deactivate/
    {
        "user_id": 123,
        "route_code": "R001"
    }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.data.get("user_id")
        route_code = request.data.get("route_code")

        if not user_id or not route_code:
            return Response(
                {"success": False, "error": "user_id and route_code are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"success": False, "error": f"User with ID {user_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get locations to deactivate
        locations = UserLocation.objects.filter(
            user=user, route_code=route_code, active=True
        )

        count = locations.count()

        if count == 0:
            return Response(
                {
                    "success": False,
                    "message": "No active locations found for the given user and route",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Deactivate
        locations.update(
            active=False, remarks=f"Bulk deactivated by {request.user.username}"
        )

        return custom_response(
            status_text="success",
            message=f"Successfully deactivated {count} location(s)",
            data={
                "user_id": user_id,
                "route_code": route_code,
                "deactivated_count": count,
            },
            status_code=status.HTTP_200_OK,
        )


from veterinary.views.choices_view import BaseModelViewSet


class UserLocationViewSet(ResponseMixin, BaseModelViewSet):
    """
    ViewSet for managing user locations with comprehensive CRUD and custom actions.
    """

    queryset = UserLocation.objects.select_related("user", "assigned_by").all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        "user",
        "level",
        "is_primary",
        "active",
        "mcc_code",
        "route_code",
        "mpp_code",
    ]
    search_fields = ["user__username", "mcc_name", "route_name", "mpp_name", "remarks"]
    ordering_fields = ["assigned_at", "modified_at", "level"]
    ordering = ["-assigned_at"]
    lookup_field = "pk"

    # -------------------------------------------------------
    # SERIALIZER SELECTION
    # -------------------------------------------------------
    def get_serializer_class(self):
        if self.action == "list":
            return UserLocationListSerializer
        elif self.action == "bulk_assign":
            return BulkLocationAssignmentSerializer
        elif self.action == "bulk_deactivate":
            return BulkDeactivateSerializer
        elif self.action == "make_primary":
            return SetPrimarySerializer
        elif self.action in ["deactivate_location", "deactivate"]:
            return DeactivateSerializer
        elif self.action == "reactivate_location":
            return ReactivateSerializer
        elif self.action == "check_access":
            return CheckAccessSerializer
        return UserLocationSerializer

    # -------------------------------------------------------
    # CUSTOM QUERYSET
    # -------------------------------------------------------
    def get_queryset(self):
        queryset = super().get_queryset()

        # filter by user_id
        user_id = self.request.query_params.get("user_id")
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # filter active_only=true
        active_only = self.request.query_params.get("active_only")
        if active_only and active_only.lower() in ["true", "1", "yes"]:
            queryset = queryset.filter(active=True)

        return queryset

    # -------------------------------------------------------
    # CREATE HOOK
    # -------------------------------------------------------
    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)

    # -------------------------------------------------------
    # DELETE USING CUSTOM RESPONSE
    # -------------------------------------------------------
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return self.success_response(message="Record deleted successfully.")

    # =====================================================================
    # CUSTOM LIST ACTIONS
    # =====================================================================

    @action(detail=False, methods=["get"], url_path="active")
    def active_locations(self, request):
        locations = UserLocation.objects.active()
        serializer = self.get_serializer(locations, many=True)

        return self.success_response(
            data={
                "count": locations.count(),
                "locations": serializer.data,
            },
            message="Active locations fetched successfully.",
        )

    @action(detail=False, methods=["get"], url_path="for-user")
    def for_user(self, request):
        user_id = request.query_params.get("user_id")

        if not user_id:
            return self.error_response("user_id parameter is required")

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return self.error_response(
                message=f"User with ID {user_id} not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        locations = UserLocation.objects.for_user(user)
        serializer = self.get_serializer(locations, many=True)

        return self.success_response(
            data={
                "user_id": user.id,
                "username": user.username,
                "count": locations.count(),
                "locations": serializer.data,
            },
            message="User locations fetched successfully.",
        )

    @action(detail=False, methods=["get"], url_path="primary-only")
    def primary_only(self, request):
        locations = UserLocation.objects.primary_only()
        serializer = self.get_serializer(locations, many=True)

        return self.success_response(
            data={
                "count": locations.count(),
                "locations": serializer.data,
            },
            message="Primary locations fetched successfully.",
        )

    @action(detail=False, methods=["get"], url_path="by-level")
    def by_level(self, request):
        level = request.query_params.get("level")

        if not level:
            return self.error_response("level parameter is required (mcc, route, mpp)")

        if level not in ["mcc", "route", "mpp"]:
            return self.error_response("Invalid level. Must be mcc, route, or mpp")

        locations = UserLocation.objects.by_level(level)
        serializer = self.get_serializer(locations, many=True)

        return self.success_response(
            data={
                "level": level,
                "count": locations.count(),
                "locations": serializer.data,
            },
            message="Locations filtered by level.",
        )

    @action(detail=False, methods=["get"], url_path="user-hierarchy")
    def user_hierarchy(self, request):
        user_id = request.query_params.get("user_id")

        if not user_id:
            return self.error_response("user_id parameter is required")

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return self.error_response(
                f"User with ID {user_id} not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        hierarchy = UserLocation.objects.get_user_hierarchy(user)
        primary_location = UserLocation.get_user_primary_location(user)

        return self.success_response(
            data={
                "user_id": user.id,
                "username": user.username,
                "total_locations": sum(len(v) for v in hierarchy.values()),
                "primary_location": (
                    UserLocationSerializer(primary_location).data
                    if primary_location
                    else None
                ),
                "hierarchy": {
                    "mcc": UserLocationSerializer(hierarchy["mcc"], many=True).data,
                    "route": UserLocationSerializer(hierarchy["route"], many=True).data,
                    "mpp": UserLocationSerializer(hierarchy["mpp"], many=True).data,
                },
            },
            message="User hierarchy fetched successfully.",
        )

    # =====================================================================
    # INSTANCE ACTIONS
    # =====================================================================

    @action(detail=True, methods=["post"], url_path="make-primary")
    def make_primary(self, request, pk=None):
        location = self.get_object()

        if not location.active:
            return self.error_response("Inactive location cannot be primary")

        location.make_primary()

        return self.success_response(
            data=UserLocationSerializer(location).data,
            message="Primary location updated successfully.",
        )

    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate_location(self, request, pk=None):
        location = self.get_object()

        if not location.active:
            return self.error_response("Location is already inactive")

        serializer = DeactivateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        remarks = serializer.validated_data.get("remarks")
        location.deactivate(deactivated_by=request.user)

        if remarks:
            location.remarks = remarks
            location.save(update_fields=["remarks"])

        return self.success_response(
            data=UserLocationSerializer(location).data,
            message="Location deactivated successfully.",
        )

    @action(detail=True, methods=["post"], url_path="reactivate")
    def reactivate_location(self, request, pk=None):
        location = self.get_object()

        if location.active:
            return self.error_response("Location is already active")

        serializer = ReactivateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        remarks = serializer.validated_data.get("remarks")
        location.reactivate(reactivated_by=request.user)

        if remarks:
            location.remarks = remarks
            location.save(update_fields=["remarks"])

        return self.success_response(
            data=UserLocationSerializer(location).data,
            message="Location reactivated successfully.",
        )

    @action(detail=True, methods=["post"], url_path="check-access")
    def check_access(self, request, pk=None):
        location = self.get_object()

        serializer = CheckAccessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mcc_code = serializer.validated_data.get("mcc_code")
        route_code = serializer.validated_data.get("route_code")
        mpp_code = serializer.validated_data.get("mpp_code")

        has_access = location.has_access_to_location(
            mcc_code=mcc_code,
            route_code=route_code,
            mpp_code=mpp_code,
        )

        return self.success_response(
            data={
                "has_access": has_access,
                "location": {
                    "id": location.id,
                    "level": location.level,
                    "active": location.active,
                },
                "checked_against": {
                    "mcc_code": mcc_code,
                    "route_code": route_code,
                    "mpp_code": mpp_code,
                },
            },
            message="Location access checked successfully.",
        )

    # =====================================================================
    # STATISTICS
    # =====================================================================
    @action(detail=False, methods=["get"], url_path="statistics")
    def statistics(self, request):
        total = UserLocation.objects.count()
        active = UserLocation.objects.filter(active=True).count()
        inactive = UserLocation.objects.filter(active=False).count()
        primary = UserLocation.objects.filter(is_primary=True, active=True).count()

        by_level = (
            UserLocation.objects.filter(active=True)
            .values("level")
            .annotate(count=Count("id"))
        )

        users_with_locations = (
            UserLocation.objects.filter(active=True).values("user").distinct().count()
        )

        return self.success_response(
            data={
                "total_locations": total,
                "active_locations": active,
                "inactive_locations": inactive,
                "primary_locations": primary,
                "users_with_locations": users_with_locations,
                "by_level": {item["level"]: item["count"] for item in by_level},
            },
            message="Location statistics fetched successfully.",
        )


# ============================================================================
# API Documentation & Examples
# ============================================================================
"""
COMPLETE API ENDPOINTS:

============================================================================
STANDARD CRUD OPERATIONS
============================================================================

1. List All Locations (with filters)
   GET /api/user-locations/
   GET /api/user-locations/?user_id=123
   GET /api/user-locations/?level=mpp
   GET /api/user-locations/?active_only=true
   GET /api/user-locations/?is_primary=true
   GET /api/user-locations/?search=north
   GET /api/user-locations/?ordering=-assigned_at

2. Create Single Location
   POST /api/user-locations/
   {
       "user": 123,
       "level": "mpp",
       "mcc_code": "M001",
       "mcc_name": "Main MCC",
       "route_code": "R001",
       "route_name": "North Route",
       "mpp_code": "MPP001",
       "mpp_name": "North MPP",
       "is_primary": true,
       "remarks": "Initial assignment"
   }

3. Retrieve Single Location
   GET /api/user-locations/{id}/

4. Update Location
   PUT /api/user-locations/{id}/
   PATCH /api/user-locations/{id}/

5. Delete Location
   DELETE /api/user-locations/{id}/

============================================================================
CUSTOM LIST ACTIONS (Manager Methods)
============================================================================

6. Get Active Locations Only
   GET /api/user-locations/active/

7. Get Locations for Specific User
   GET /api/user-locations/for-user/?user_id=123

8. Get Primary Locations Only
   GET /api/user-locations/primary-only/

9. Get Locations by Level
   GET /api/user-locations/by-level/?level=mpp
   GET /api/user-locations/by-level/?level=route
   GET /api/user-locations/by-level/?level=mcc

10. Get Complete User Hierarchy
    GET /api/user-locations/user-hierarchy/?user_id=123
    Response:
    {
        "success": true,
        "data": {
            "user_id": 123,
            "username": "john.doe",
            "total_locations": 15,
            "primary_location": {...},
            "hierarchy": {
                "mcc": [...],
                "route": [...],
                "mpp": [...]
            },
            "statistics": {
                "mcc_count": 1,
                "route_count": 2,
                "mpp_count": 12
            }
        }
    }

============================================================================
INSTANCE ACTIONS (Model Helper Methods)
============================================================================

11. Make Location Primary
    POST /api/user-locations/{id}/make-primary/
    Response:
    {
        "success": true,
        "message": "Location 456 set as primary for user john.doe",
        "data": {...}
    }

12. Deactivate Location
    POST /api/user-locations/{id}/deactivate/
    Body: {"remarks": "User transferred"}
    Response:
    {
        "success": true,
        "message": "Location 456 deactivated successfully",
        "data": {...}
    }

13. Reactivate Location
    POST /api/user-locations/{id}/reactivate/
    Body: {"remarks": "User returned"}
    Response:
    {
        "success": true,
        "message": "Location 456 reactivated successfully",
        "data": {...}
    }

14. Check Access Permission
    POST /api/user-locations/{id}/check-access/
    Body: {
        "mcc_code": "M001",
        "route_code": "R001",
        "mpp_code": "MPP001"
    }
    Response:
    {
        "success": true,
        "has_access": true,
        "location": {
            "id": 456,
            "level": "route",
            "active": true
        },
        "checked_against": {
            "mcc_code": "M001",
            "route_code": "R001",
            "mpp_code": "MPP001"
        }
    }

============================================================================
BULK OPERATIONS
============================================================================

15. Bulk Assign by Route (MPP Level)
    POST /api/user-locations/bulk-assign/
    Body: {
        "user_id": 123,
        "route_code": "R001",
        "assignment_level": "mpp",
        "set_as_primary": true,
        "remarks": "Q1 2025 assignment"
    }
    Response:
    {
        "success": true,
        "message": "Successfully processed 15 location(s)",
        "data": {
            "user_id": 123,
            "username": "john.doe",
            "route_code": "R001",
            "assignment_level": "mpp",
            "created_count": 15,
            "skipped_count": 0,
            "total_processed": 15,
            "created_locations": [...],
            "skipped_locations": []
        }
    }

16. Bulk Assign by Route (Route Level)
    POST /api/user-locations/bulk-assign/
    Body: {
        "user_id": 456,
        "route_code": "R001",
        "assignment_level": "route"
    }

17. Bulk Assign by Route (MCC Level)
    POST /api/user-locations/bulk-assign/
    Body: {
        "user_id": 789,
        "route_code": "R001",
        "assignment_level": "mcc"
    }

18. Bulk Deactivate by User
    POST /api/user-locations/bulk-deactivate/
    Body: {
        "user_id": 123,
        "remarks": "User resigned"
    }

19. Bulk Deactivate by Route
    POST /api/user-locations/bulk-deactivate/
    Body: {
        "user_id": 123,
        "route_code": "R001",
        "remarks": "Route reassignment"
    }

20. Bulk Deactivate by Level
    POST /api/user-locations/bulk-deactivate/
    Body: {
        "user_id": 123,
        "level": "mpp",
        "remarks": "MPP consolidation"
    }

21. Bulk Deactivate by Route and Level
    POST /api/user-locations/bulk-deactivate/
    Body: {
        "user_id": 123,
        "route_code": "R001",
        "level": "mpp"
    }

============================================================================
STATISTICS & ANALYTICS
============================================================================

22. Get Overall Statistics
    GET /api/user-locations/statistics/
    Response:
    {
        "success": true,
        "data": {
            "total_locations": 1500,
            "active_locations": 1200,
            "inactive_locations": 300,
            "primary_locations": 150,
            "users_with_locations": 150,
            "by_level": {
                "mcc": 50,
                "route": 200,
                "mpp": 950
            }
        }
    }

============================================================================
FILTERING & SEARCHING EXAMPLES
============================================================================

23. Filter by Multiple Criteria
    GET /api/user-locations/?user=123&level=mpp&is_primary=true&active=true

24. Search by Name
    GET /api/user-locations/?search=north

25. Order Results
    GET /api/user-locations/?ordering=-assigned_at
    GET /api/user-locations/?ordering=level,assigned_at

26. Combine Filters, Search, and Ordering
    GET /api/user-locations/?user_id=123&active_only=true&search=central&ordering=-modified_at

============================================================================
PERMISSIONS & ERROR HANDLING
============================================================================

All endpoints require authentication (IsAuthenticated permission).

Error Response Format:
{
    "success": false,
    "error": "Error message here",
    "details": {...}  // Optional validation details
}

Common HTTP Status Codes:
- 200 OK: Successful GET/PUT/PATCH
- 201 Created: Successful POST
- 204 No Content: Successful DELETE
- 400 Bad Request: Invalid input data
- 401 Unauthorized: Not authenticated
- 403 Forbidden: No permission
- 404 Not Found: Resource not found
- 500 Internal Server Error: Server error

============================================================================
USAGE SCENARIOS
============================================================================

Scenario 1: Assign a field officer to all MPPs in a route
----------------------------------------------------------
Step 1: Preview what will be assigned
GET /api/user-locations/by-level/?level=route

Step 2: Bulk assign
POST /api/user-locations/bulk-assign/
{
    "user_id": 123,
    "route_code": "R001",
    "assignment_level": "mpp",
    "set_as_primary": true,
    "remarks": "New field officer - Q1 2025"
}

Step 3: Verify assignment
GET /api/user-locations/user-hierarchy/?user_id=123

Scenario 2: Change user's primary location
-------------------------------------------
Step 1: Find desired location
GET /api/user-locations/for-user/?user_id=123

Step 2: Set new primary
POST /api/user-locations/456/make-primary/

Step 3: Verify
GET /api/user-locations/user-hierarchy/?user_id=123

Scenario 3: Transfer user to different route
---------------------------------------------
Step 1: Deactivate old route assignments
POST /api/user-locations/bulk-deactivate/
{
    "user_id": 123,
    "route_code": "R001",
    "remarks": "Transferred to R002"
}

Step 2: Assign new route
POST /api/user-locations/bulk-assign/
{
    "user_id": 123,
    "route_code": "R002",
    "assignment_level": "mpp",
    "set_as_primary": true,
    "remarks": "Transfer from R001"
}

Scenario 4: Check if user has access to specific location
----------------------------------------------------------
Step 1: Get user's locations
GET /api/user-locations/for-user/?user_id=123

Step 2: Check access for each location
POST /api/user-locations/456/check-access/
{
    "mcc_code": "M001",
    "route_code": "R001",
    "mpp_code": "MPP001"
}

Scenario 5: Temporary deactivation and reactivation
----------------------------------------------------
Step 1: Deactivate
POST /api/user-locations/456/deactivate/
{"remarks": "On leave - 2 weeks"}

Step 2: Later, reactivate
POST /api/user-locations/456/reactivate/
{"remarks": "Returned from leave"}

Scenario 6: Get statistics for dashboard
-----------------------------------------
GET /api/user-locations/statistics/

============================================================================
ADVANCED FILTERING WITH DJANGO FILTERS
============================================================================

The viewset supports advanced filtering through DjangoFilterBackend:

1. Exact matches:
   ?user=123
   ?level=mpp
   ?is_primary=true
   ?active=true
   ?mcc_code=M001
   ?route_code=R001
   ?mpp_code=MPP001

2. Multiple filters (AND logic):
   ?user=123&level=mpp&active=true

3. Search (across multiple fields):
   ?search=north  // Searches username, mcc_name, route_name, mpp_name, remarks

4. Ordering:
   ?ordering=assigned_at
   ?ordering=-assigned_at  // Descending
   ?ordering=level,-assigned_at  // Multiple fields

5. Pagination (if enabled):
   ?page=1&page_size=20

============================================================================
INTEGRATION WITH FRONTEND
============================================================================

React/Vue Example - Bulk Assign:
---------------------------------
const bulkAssign = async (userId, routeCode) => {
    try {
        const response = await axios.post('/api/user-locations/bulk-assign/', {
            user_id: userId,
            route_code: routeCode,
            assignment_level: 'mpp',
            set_as_primary: true,
            remarks: 'Auto-assigned by system'
        }, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.data.success) {
            console.log(`Created: ${response.data.data.created_count}`);
            console.log(`Skipped: ${response.data.data.skipped_count}`);
            return response.data;
        }
    } catch (error) {
        console.error('Bulk assign failed:', error.response.data);
    }
};

React/Vue Example - Get User Hierarchy:
----------------------------------------
const getUserHierarchy = async (userId) => {
    try {
        const response = await axios.get(
            `/api/user-locations/user-hierarchy/?user_id=${userId}`,
            {
                headers: {'Authorization': `Bearer ${token}`}
            }
        );
        
        return response.data.data;
    } catch (error) {
        console.error('Failed to fetch hierarchy:', error);
    }
};

React/Vue Example - Check Access:
----------------------------------
const checkAccess = async (locationId, codes) => {
    try {
        const response = await axios.post(
            `/api/user-locations/${locationId}/check-access/`,
            codes,
            {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            }
        );
        
        return response.data.has_access;
    } catch (error) {
        console.error('Access check failed:', error);
        return false;
    }
};

============================================================================
TESTING EXAMPLES (pytest/Django Test)
============================================================================

import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        password='testpass123'
    )

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

def test_bulk_assign(authenticated_client, user):
    response = authenticated_client.post(
        '/api/user-locations/bulk-assign/',
        {
            'user_id': user.id,
            'route_code': 'R001',
            'assignment_level': 'mpp',
            'set_as_primary': True
        },
        format='json'
    )
    
    assert response.status_code == 201
    assert response.data['success'] is True
    assert response.data['data']['created_count'] > 0

def test_user_hierarchy(authenticated_client, user):
    response = authenticated_client.get(
        f'/api/user-locations/user-hierarchy/?user_id={user.id}'
    )
    
    assert response.status_code == 200
    assert response.data['success'] is True
    assert 'hierarchy' in response.data['data']

def test_make_primary(authenticated_client, user, location):
    response = authenticated_client.post(
        f'/api/user-locations/{location.id}/make-primary/'
    )
    
    assert response.status_code == 200
    assert response.data['success'] is True

============================================================================
PERFORMANCE OPTIMIZATION TIPS
============================================================================

1. Use select_related for foreign keys:
   Already implemented in ViewSet queryset optimization

2. Use prefetch_related for reverse relations:
   locations = UserLocation.objects.prefetch_related('user__locations')

3. Use only() to limit fields:
   locations = UserLocation.objects.only('id', 'user', 'level', 'active')

4. Use values() for simple data:
   locations = UserLocation.objects.values('id', 'user_id', 'level')

5. Use pagination for large datasets:
   Add pagination_class to ViewSet

6. Cache frequently accessed data:
   Use Django cache framework for statistics

7. Database indexes:
   Already implemented in UserLocation.Meta.indexes

============================================================================
SECURITY CONSIDERATIONS
============================================================================

1. Always use IsAuthenticated permission
2. Add object-level permissions if needed (IsOwnerOrAdmin)
3. Validate user_id in bulk operations
4. Use transactions for bulk operations
5. Log all location assignments for audit trail
6. Implement rate limiting for bulk operations
7. Add CSRF protection for non-API views
8. Use HTTPS in production
9. Implement API versioning
10. Add request throttling

"""


# ============================================================================
# Example Usage & Test Cases
# ============================================================================
"""
# Example 1: Preview what will be assigned
GET /api/locations/route-preview/?route_code=R001&level=mpp

Response:
{
    "success": true,
    "data": {
        "route_code": "R001",
        "route_name": "North Route",
        "assignment_level": "mpp",
        "locations_count": 15,
        "company_name": "ABC Dairy",
        "plant_name": "North Plant",
        "mcc_name": "Main Collection Center",
        "hierarchy_preview": [...]
    }
}

# Example 2: Bulk assign MPPs for a route
POST /api/locations/bulk-assign/
{
    "user_id": 123,
    "route_code": "R001",
    "assignment_level": "mpp",
    "set_as_primary": true,
    "remarks": "Field officer assignment for Q1 2025"
}

Response:
{
    "success": true,
    "message": "Successfully processed 15 location(s)",
    "data": {
        "user_id": 123,
        "username": "john.doe",
        "route_code": "R001",
        "assignment_level": "mpp",
        "created_count": 15,
        "skipped_count": 0,
        "total_processed": 15,
        "created_locations": [...],
        "skipped_locations": []
    }
}

# Example 3: Assign at Route level (single record)
POST /api/locations/bulk-assign/
{
    "user_id": 456,
    "route_code": "R001",
    "assignment_level": "route"
}

# Example 4: Assign at MCC level
POST /api/locations/bulk-assign/
{
    "user_id": 789,
    "route_code": "R001",
    "assignment_level": "mcc"
}

# Example 5: List user's locations
GET /api/locations/user/123/

Response:
{
    "success": true,
    "data": {
        "user_id": 123,
        "username": "john.doe",
        "statistics": {
            "total": 15,
            "primary": 1,
            "by_level": {
                "mcc": 0,
                "route": 0,
                "mpp": 15
            }
        },
        "locations": [...]
    }
}

# Example 6: Bulk deactivate
POST /api/locations/bulk-deactivate/
{
    "user_id": 123,
    "route_code": "R001"
}

Response:
{
    "success": true,
    "message": "Successfully deactivated 15 location(s)",
    "data": {
        "user_id": 123,
        "route_code": "R001",
        "deactivated_count": 15
    }
}
"""
