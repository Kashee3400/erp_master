# ============================================================================
# serializers.py
# ============================================================================
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from erp_app.models import BusinessHierarchySnapshot
from facilitator.models.user_profile_model import UserLocation, RouteLevelChoice

User = get_user_model()


class BulkLocationAssignmentSerializer(serializers.Serializer):
    """
    Serializer for bulk location assignment.
    Takes user and route_code, creates UserLocation records for all MPPs in that route.
    """

    user_id = serializers.IntegerField(
        required=True, help_text="ID of the user to assign locations to"
    )
    route_code = serializers.CharField(
        required=True,
        max_length=10,
        help_text="Route code to assign (all MPPs under this route will be assigned)",
    )
    assignment_level = serializers.ChoiceField(
        choices=RouteLevelChoice.choices,
        default=RouteLevelChoice.LEVEL_MPP,
        help_text="Level at which to assign (mcc, route, or mpp)",
    )
    set_as_primary = serializers.BooleanField(
        default=False, help_text="Set the first location as primary"
    )
    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional remarks for the assignment",
    )

    def validate_user_id(self, value):
        """Validate that the user exists."""
        try:
            user = User.objects.get(pk=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User with ID {value} does not exist.")

    def validate_route_code(self, value):
        """Validate that the route code exists in hierarchy."""
        if not BusinessHierarchySnapshot.objects.filter(
            route_code=value, is_default=True
        ).exists():
            raise serializers.ValidationError(
                f"Route code '{value}' does not exist in the business hierarchy."
            )
        return value

    def validate(self, attrs):
        """Cross-field validation."""
        user_id = attrs.get("user_id")
        route_code = attrs.get("route_code")
        assignment_level = attrs.get("assignment_level")

        # Get hierarchy data for this route
        hierarchy_records = BusinessHierarchySnapshot.objects.filter(
            route_code=route_code, is_default=True
        )

        if not hierarchy_records.exists():
            raise serializers.ValidationError(
                {"route_code": f"No active records found for route '{route_code}'"}
            )

        # Check for existing assignments
        existing_count = UserLocation.objects.filter(
            user_id=user_id, route_code=route_code, active=True
        ).count()

        if existing_count > 0:
            attrs["existing_count"] = existing_count
            attrs["warning"] = (
                f"User already has {existing_count} active location(s) for this route."
            )

        # Validate level-specific requirements
        if assignment_level == RouteLevelChoice.LEVEL_MCC:
            # For MCC level, we need unique MCC codes
            attrs["hierarchy_count"] = (
                hierarchy_records.values("mcc_code").distinct().count()
            )
        elif assignment_level == RouteLevelChoice.LEVEL_ROUTE:
            # For Route level, we need unique route codes (should be 1)
            attrs["hierarchy_count"] = 1
        else:  # MPP level
            # For MPP level, count unique MPP codes
            attrs["hierarchy_count"] = (
                hierarchy_records.values("mpp_code").distinct().count()
            )

        attrs["hierarchy_records"] = hierarchy_records

        return attrs

    def create(self, validated_data):
        """
        Create bulk UserLocation records.
        Returns dict with created records and statistics.
        """
        user_id = validated_data["user_id"]
        route_code = validated_data["route_code"]
        assignment_level = validated_data["assignment_level"]
        set_as_primary = validated_data["set_as_primary"]
        remarks = validated_data.get("remarks", "")
        hierarchy_records = validated_data["hierarchy_records"]

        user = User.objects.get(pk=user_id)
        assigned_by = self.context["request"].user

        created_locations = []
        skipped_locations = []

        with transaction.atomic():
            if assignment_level == RouteLevelChoice.LEVEL_MCC:
                # Create one record per unique MCC
                unique_mccs = hierarchy_records.values(
                    "mcc_code", "mcc_name", "mcc_tr_code"
                ).distinct()

                for idx, mcc_data in enumerate(unique_mccs):
                    is_primary = set_as_primary and idx == 0

                    # Check if already exists
                    if UserLocation.objects.filter(
                        user=user,
                        level=RouteLevelChoice.LEVEL_MCC,
                        mcc_code=mcc_data["mcc_code"],
                        active=True,
                    ).exists():
                        skipped_locations.append(
                            {
                                "mcc_code": mcc_data["mcc_code"],
                                "reason": "Already exists",
                            }
                        )
                        continue

                    location = UserLocation.objects.create(
                        user=user,
                        level=RouteLevelChoice.LEVEL_MCC,
                        mcc_code=mcc_data["mcc_code"],
                        mcc_name=mcc_data["mcc_name"],
                        mcc_tr_code=mcc_data["mcc_tr_code"],
                        is_primary=is_primary,
                        assigned_by=assigned_by,
                        remarks=remarks or f"Bulk assigned from route {route_code}",
                    )
                    created_locations.append(location)

            elif assignment_level == RouteLevelChoice.LEVEL_ROUTE:
                # Create one record for the route
                route_data = hierarchy_records.first()

                # Check if already exists
                if UserLocation.objects.filter(
                    user=user,
                    level=RouteLevelChoice.LEVEL_ROUTE,
                    route_code=route_code,
                    active=True,
                ).exists():
                    skipped_locations.append(
                        {"route_code": route_code, "reason": "Already exists"}
                    )
                else:
                    location = UserLocation.objects.create(
                        user=user,
                        level=RouteLevelChoice.LEVEL_ROUTE,
                        mcc_code=route_data.mcc_code,
                        mcc_name=route_data.mcc_name,
                        mcc_tr_code=route_data.mcc_tr_code,
                        route_code=route_data.route_code,
                        route_name=route_data.route_name,
                        route_ex_code=route_data.route_ex_code,
                        is_primary=set_as_primary,
                        assigned_by=assigned_by,
                        remarks=remarks or f"Bulk assigned from route {route_code}",
                    )
                    created_locations.append(location)

            else:  # MPP level
                # Create one record per MPP
                for idx, hierarchy in enumerate(hierarchy_records):
                    is_primary = set_as_primary and idx == 0

                    # Check if already exists
                    if UserLocation.objects.filter(
                        user=user,
                        level=RouteLevelChoice.LEVEL_MPP,
                        mpp_code=hierarchy.mpp_code,
                        active=True,
                    ).exists():
                        skipped_locations.append(
                            {
                                "mpp_code": hierarchy.mpp_code,
                                "mpp_name": hierarchy.mpp_name,
                                "reason": "Already exists",
                            }
                        )
                        continue

                    location = UserLocation.objects.create(
                        user=user,
                        level=RouteLevelChoice.LEVEL_MPP,
                        mcc_code=hierarchy.mcc_code,
                        mcc_name=hierarchy.mcc_name,
                        mcc_tr_code=hierarchy.mcc_tr_code,
                        route_code=hierarchy.route_code,
                        route_name=hierarchy.route_name,
                        route_ex_code=hierarchy.route_ex_code,
                        mpp_code=hierarchy.mpp_code,
                        mpp_name=hierarchy.mpp_name,
                        mpp_ex_code=hierarchy.mpp_ex_code,
                        is_primary=is_primary,
                        assigned_by=assigned_by,
                        remarks=remarks or f"Bulk assigned from route {route_code}",
                    )
                    created_locations.append(location)

        return {
            "user": user,
            "route_code": route_code,
            "assignment_level": assignment_level,
            "created_count": len(created_locations),
            "skipped_count": len(skipped_locations),
            "created_locations": created_locations,
            "skipped_locations": skipped_locations,
        }


class UserLocationDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for UserLocation with all related information."""

    user_username = serializers.CharField(source="user.username", read_only=True)
    assigned_by_username = serializers.CharField(
        source="assigned_by.username", read_only=True, allow_null=True
    )
    location_display = serializers.CharField(
        source="get_hierarchy_display", read_only=True
    )
    location_code = serializers.CharField(source="get_location_code", read_only=True)

    class Meta:
        model = UserLocation
        fields = [
            "id",
            "user",
            "user_username",
            "level",
            "mcc_code",
            "mcc_name",
            "mcc_tr_code",
            "route_code",
            "route_name",
            "route_ex_code",
            "mpp_code",
            "mpp_name",
            "mpp_ex_code",
            "is_primary",
            "active",
            "assigned_by",
            "assigned_by_username",
            "assigned_at",
            "modified_at",
            "remarks",
            "location_display",
            "location_code",
        ]
        read_only_fields = ["assigned_at", "modified_at"]


class BulkAssignmentResponseSerializer(serializers.Serializer):
    """Serializer for bulk assignment response."""

    user_id = serializers.IntegerField()
    username = serializers.CharField()
    route_code = serializers.CharField()
    assignment_level = serializers.CharField()
    created_count = serializers.IntegerField()
    skipped_count = serializers.IntegerField()
    total_processed = serializers.IntegerField()
    created_locations = UserLocationDetailSerializer(many=True)
    skipped_locations = serializers.ListField()
    message = serializers.CharField()


class RouteHierarchySerializer(serializers.ModelSerializer):
    """Serializer for BusinessHierarchySnapshot to preview route data."""

    class Meta:
        model = BusinessHierarchySnapshot
        fields = [
            "company_code",
            "company_name",
            "plant_code",
            "plant_name",
            "mcc_code",
            "mcc_name",
            "route_code",
            "route_name",
            "mpp_code",
            "mpp_name",
            "mpp_type",
        ]


class UserLocationSerializer(serializers.ModelSerializer):
    """Base serializer for UserLocation."""

    user_username = serializers.CharField(source="user.username", read_only=True)
    assigned_by_username = serializers.CharField(
        source="assigned_by.username", read_only=True, allow_null=True
    )
    location_display = serializers.CharField(
        source="get_hierarchy_display", read_only=True
    )
    location_code = serializers.CharField(source="get_location_code", read_only=True)
    location_name = serializers.CharField(source="get_location_name", read_only=True)
    full_hierarchy = serializers.JSONField(source="get_full_hierarchy", read_only=True)

    class Meta:
        model = UserLocation
        fields = [
            "id",
            "user",
            "user_username",
            "level",
            "mcc_code",
            "mcc_name",
            "mcc_tr_code",
            "route_code",
            "route_name",
            "route_ex_code",
            "mpp_code",
            "mpp_name",
            "mpp_ex_code",
            "is_primary",
            "active",
            "assigned_by",
            "assigned_by_username",
            "assigned_at",
            "modified_at",
            "remarks",
            "location_display",
            "location_code",
            "location_name",
            "full_hierarchy",
        ]
        read_only_fields = ["assigned_at", "modified_at", "assigned_by"]

    def create(self, validated_data):
        """Override create to set assigned_by from request context."""
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["assigned_by"] = request.user
        return super().create(validated_data)


class UserLocationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""

    user_username = serializers.CharField(source="user.username", read_only=True)
    location_display = serializers.CharField(
        source="get_hierarchy_display", read_only=True
    )
    location_code = serializers.CharField(source="get_location_code", read_only=True)

    class Meta:
        model = UserLocation
        fields = [
            "id",
            "user",
            "user_username",
            "level",
            "location_code",
            "location_display",
            "is_primary",
            "active",
            "assigned_at",
        ]


class BulkDeactivateSerializer(serializers.Serializer):
    """Serializer for bulk deactivation."""

    user_id = serializers.IntegerField(required=True)
    route_code = serializers.CharField(required=False, allow_blank=True)
    level = serializers.ChoiceField(
        choices=[("mcc", "MCC"), ("route", "Route"), ("mpp", "MPP")], required=False
    )
    remarks = serializers.CharField(required=False, allow_blank=True)


class SetPrimarySerializer(serializers.Serializer):
    """Serializer for setting primary location."""

    location_id = serializers.IntegerField(required=True)


class DeactivateSerializer(serializers.Serializer):
    """Serializer for single location deactivation."""

    remarks = serializers.CharField(required=False, allow_blank=True)


class ReactivateSerializer(serializers.Serializer):
    """Serializer for location reactivation."""

    remarks = serializers.CharField(required=False, allow_blank=True)


class CheckAccessSerializer(serializers.Serializer):
    """Serializer for checking location access."""

    mcc_code = serializers.CharField(required=False, allow_blank=True)
    route_code = serializers.CharField(required=False, allow_blank=True)
    mpp_code = serializers.CharField(required=False, allow_blank=True)


class UserHierarchySerializer(serializers.Serializer):
    """Serializer for user hierarchy response."""

    user_id = serializers.IntegerField()
    username = serializers.CharField()
    total_locations = serializers.IntegerField()
    primary_location = UserLocationSerializer(allow_null=True)
    mcc = UserLocationSerializer(many=True)
    route = UserLocationSerializer(many=True)
    mpp = UserLocationSerializer(many=True)
