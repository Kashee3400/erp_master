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
    Serializer for hierarchical bulk location assignment.

    Assignment Levels:
    - MCC: Requires mcc_code, creates records with only MCC fields
    - ROUTE: Requires route_code, creates records with MCC + Route fields
    - MPP: Requires route_code, creates records with MCC + Route + MPP fields
    """

    user_id = serializers.IntegerField(
        required=True, help_text="ID of the user to assign locations to"
    )

    assignment_level = serializers.ChoiceField(
        choices=RouteLevelChoice.choices,
        required=True,
        help_text="Level at which to assign (mcc, route, or mpp)",
    )

    mcc_code = serializers.CharField(
        required=False,
        allow_null=True,
        max_length=20,
        help_text="MCC code (required only for MCC level assignment)",
    )

    route_code = serializers.CharField(
        required=False,
        allow_null=True,
        max_length=20,
        help_text="Route code (required for ROUTE and MPP level assignments)",
    )
    mpp_code = serializers.CharField(
        required=False,
        allow_null=True,
        max_length=20,
        help_text="Route code (required for ROUTE and MPP level assignments)",
    )

    set_as_primary = serializers.BooleanField(
        default=False, help_text="Set the first location as primary"
    )

    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="Optional remarks for the assignment",
    )

    def validate_user_id(self, value):
        """Validate that the user exists."""
        if not User.objects.filter(pk=value).exists():
            raise serializers.ValidationError(f"User with ID {value} does not exist.")
        return value

    def validate(self, attrs):
        """
        Cross-field validation based on assignment level.
        Ensures required fields are provided for each level.
        """
        assignment_level = attrs.get("assignment_level")
        mcc_code = attrs.get("mcc_code")
        route_code = attrs.get("route_code")
        user_id = attrs.get("user_id")

        # Level-specific validation
        if assignment_level == RouteLevelChoice.LEVEL_MCC:
            if not mcc_code:
                raise serializers.ValidationError(
                    {"mcc_code": "MCC code is required for MCC level assignment."}
                )

            # Validate MCC exists in hierarchy
            hierarchy_records = BusinessHierarchySnapshot.objects.filter(
                mcc_code=mcc_code, is_default=True
            )

            if not hierarchy_records.exists():
                raise serializers.ValidationError(
                    {
                        "mcc_code": f"MCC code '{mcc_code}' does not exist in the business hierarchy."
                    }
                )

            # Check for existing assignments
            existing_count = UserLocation.objects.filter(
                user_id=user_id,
                level=RouteLevelChoice.LEVEL_MCC,
                mcc_code=mcc_code,
                active=True,
            ).count()

            attrs["hierarchy_records"] = hierarchy_records
            attrs["hierarchy_count"] = (
                hierarchy_records.values("mcc_code").distinct().count()
            )

        elif assignment_level == RouteLevelChoice.LEVEL_ROUTE:
            if not route_code:
                raise serializers.ValidationError(
                    {"route_code": "Route code is required for ROUTE level assignment."}
                )

            # Validate route exists in hierarchy
            hierarchy_records = BusinessHierarchySnapshot.objects.filter(
                route_code=route_code, is_default=True
            )

            if not hierarchy_records.exists():
                raise serializers.ValidationError(
                    {
                        "route_code": f"Route code '{route_code}' does not exist in the business hierarchy."
                    }
                )

            # Check for existing assignments
            existing_count = UserLocation.objects.filter(
                user_id=user_id,
                level=RouteLevelChoice.LEVEL_ROUTE,
                route_code=route_code,
                active=True,
            ).count()

            attrs["hierarchy_records"] = hierarchy_records
            attrs["hierarchy_count"] = 1

        elif assignment_level == RouteLevelChoice.LEVEL_MPP:
            mpp_code = attrs.get("mpp_code")

            if not mpp_code:
                raise serializers.ValidationError(
                    {"mpp_code": "MPP code is required for MPP level assignment."}
                )

            # Fetch hierarchy by mpp_code (full hierarchy)
            hierarchy_records = BusinessHierarchySnapshot.objects.filter(
                mpp_code=mpp_code, is_default=True
            )

            if not hierarchy_records.exists():
                raise serializers.ValidationError(
                    {
                        "mpp_code": f"MPP code '{mpp_code}' does not exist in the business hierarchy."
                    }
                )
            existing_count = UserLocation.objects.filter(
                user_id=user_id,
                level=RouteLevelChoice.LEVEL_ROUTE,
                route_code=route_code,
                active=True,
            ).count()
            # Save SINGLE record, not queryset
            attrs["hierarchy_record"] = hierarchy_records.first()
            attrs["hierarchy_count"] = 1

        else:
            raise serializers.ValidationError(
                {"assignment_level": f"Invalid assignment level: {assignment_level}"}
            )

        # Add warning if there are existing assignments
        if existing_count > 0:
            attrs["existing_count"] = existing_count
            attrs["warning"] = (
                f"User already has {existing_count} active location(s) at this level."
            )

        return attrs

    def create(self, validated_data):
        """
        Create bulk UserLocation records based on assignment level.
        Returns dict with created records and statistics.
        """
        assignment_level = validated_data["assignment_level"]

        # Route to appropriate handler based on level
        if assignment_level == RouteLevelChoice.LEVEL_MCC:
            return self._handle_mcc_assignment(validated_data)
        elif assignment_level == RouteLevelChoice.LEVEL_ROUTE:
            return self._handle_route_assignment(validated_data)
        elif assignment_level == RouteLevelChoice.LEVEL_MPP:
            return self._handle_mpp_assignment(validated_data)

    def _handle_mcc_assignment(self, validated_data):
        """
        Handle MCC level assignment.
        Creates one UserLocation record per unique MCC.
        Only populates MCC fields, route and MPP fields remain NULL.
        """
        user_id = validated_data["user_id"]
        mcc_code = validated_data["mcc_code"]
        set_as_primary = validated_data["set_as_primary"]
        remarks = validated_data.get("remarks", "")
        hierarchy_records = validated_data["hierarchy_records"]

        user = User.objects.get(pk=user_id)
        assigned_by = self.context["request"].user

        created_locations = []
        skipped_locations = []

        with transaction.atomic():
            # Get unique MCC data from hierarchy
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
                            "mcc_name": mcc_data.get("mcc_name"),
                            "reason": "Already exists",
                        }
                    )
                    continue

                # Create MCC level assignment (route and MPP fields are NULL)
                location = UserLocation.objects.create(
                    user=user,
                    level=RouteLevelChoice.LEVEL_MCC,
                    mcc_code=mcc_data["mcc_code"],
                    mcc_name=mcc_data.get("mcc_name"),
                    mcc_tr_code=mcc_data.get("mcc_tr_code"),
                    is_primary=is_primary,
                    assigned_by=assigned_by,
                    remarks=remarks
                    or f"MCC level assignment for {mcc_data['mcc_code']}",
                )
                created_locations.append(location)

        return {
            "user": user,
            "assignment_level": RouteLevelChoice.LEVEL_MCC,
            "mcc_code": mcc_code,
            "created_count": len(created_locations),
            "skipped_count": len(skipped_locations),
            "created_locations": created_locations,
            "skipped_locations": skipped_locations,
        }

    def _handle_route_assignment(self, validated_data):
        """
        Handle ROUTE level assignment.
        Creates EXACTLY ONE UserLocation record for the route.
        Populates MCC + Route fields, MPP fields remain NULL.
        """
        user_id = validated_data["user_id"]
        route_code = validated_data["route_code"]
        set_as_primary = validated_data["set_as_primary"]
        remarks = validated_data.get("remarks", "")
        hierarchy_records = validated_data["hierarchy_records"]

        user = User.objects.get(pk=user_id)
        assigned_by = self.context["request"].user

        created_locations = []
        skipped_locations = []

        with transaction.atomic():
            # Get route data (use first record as they all have same route info)
            route_data = hierarchy_records.first()

            # Check if already exists
            if UserLocation.objects.filter(
                user=user,
                level=RouteLevelChoice.LEVEL_ROUTE,
                route_code=route_code,
                active=True,
            ).exists():
                skipped_locations.append(
                    {
                        "route_code": route_code,
                        "route_name": route_data.route_name,
                        "reason": "Already exists",
                    }
                )
            else:
                # Create ROUTE level assignment (MPP fields are NULL)
                location = UserLocation.objects.create(
                    user=user,
                    level=RouteLevelChoice.LEVEL_ROUTE,
                    # MCC fields
                    mcc_code=route_data.mcc_code,
                    mcc_name=route_data.mcc_name,
                    mcc_tr_code=route_data.mcc_tr_code,
                    # Route fields
                    route_code=route_data.route_code,
                    route_name=route_data.route_name,
                    route_ex_code=route_data.route_ex_code,
                    # mpp_code, mpp_name, mpp_ex_code remain NULL
                    is_primary=set_as_primary,
                    assigned_by=assigned_by,
                    remarks=remarks or f"Route level assignment for {route_code}",
                )
                created_locations.append(location)

        return {
            "user": user,
            "assignment_level": RouteLevelChoice.LEVEL_ROUTE,
            "route_code": route_code,
            "created_count": len(created_locations),
            "skipped_count": len(skipped_locations),
            "created_locations": created_locations,
            "skipped_locations": skipped_locations,
        }

    def _handle_mpp_assignment(self, validated_data):
        """
        Handle MPP level assignment.
        Creates ONE UserLocation record for a single MPP.
        Populates MCC + Route + MPP fields (full hierarchy).
        """
        user_id = validated_data["user_id"]
        mpp_code = validated_data["mpp_code"]  # Use MPP code directly
        set_as_primary = validated_data["set_as_primary"]
        remarks = validated_data.get("remarks", "")
        hierarchy_record = validated_data["hierarchy_record"]

        user = User.objects.get(pk=user_id)
        assigned_by = self.context["request"].user

        # Check if already exists
        if UserLocation.objects.filter(
            user=user,
            level=RouteLevelChoice.LEVEL_MPP,
            mpp_code=mpp_code,
            active=True,
        ).exists():
            return {
                "user": user,
                "assignment_level": RouteLevelChoice.LEVEL_MPP,
                "mpp_code": mpp_code,
                "created_count": 0,
                "skipped_count": 1,
                "created_locations": [],
                "skipped_locations": [
                    {
                        "mpp_code": mpp_code,
                        "reason": "MPP already assigned to this user",
                    }
                ],
            }

        # Create ONE MPP assignment
        location = UserLocation.objects.create(
            user=user,
            level=RouteLevelChoice.LEVEL_MPP,
            # MCC fields
            mcc_code=hierarchy_record.mcc_code,
            mcc_name=hierarchy_record.mcc_name,
            mcc_tr_code=hierarchy_record.mcc_tr_code,
            # Route fields
            route_code=hierarchy_record.route_code,
            route_name=hierarchy_record.route_name,
            route_ex_code=hierarchy_record.route_ex_code,
            # MPP fields
            mpp_code=hierarchy_record.mpp_code,
            mpp_name=hierarchy_record.mpp_name,
            mpp_ex_code=hierarchy_record.mpp_ex_code,
            is_primary=set_as_primary,
            assigned_by=assigned_by,
            remarks=remarks or f"MPP level assignment for MPP {mpp_code}",
        )

        return {
            "user": user,
            "assignment_level": RouteLevelChoice.LEVEL_MPP,
            "mpp_code": mpp_code,
            "created_count": 1,
            "skipped_count": 0,
            "created_locations": [location],
            "skipped_locations": [],
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
