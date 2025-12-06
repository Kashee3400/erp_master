from rest_framework import serializers
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from veterinary.choices.choices import *

from ..models.models import NonMember, NonMemberCattle, Cattle, CattleStatusLog
from ..models.case_models import (
    CaseEntry,
    TreatmentCostConfiguration,
)
from django.utils.timezone import datetime
from ..serializers.choices_serializers import SpeciesBreedSerializer


class NonMemberSerializer(serializers.ModelSerializer):
    """Serializer for NonMember model"""

    class Meta:
        model = NonMember
        fields = [
            "id",
            "non_member_id",
            "name",
            "mobile_no",
            "address",
            "visit_count",
            "created_at",
            "updated_at",
            "sync",
            "mpp_code",
            "mpp_name",
            "mcc_code",
            "mcc_name",
            "is_deleted",
            "locale",
        ]
        read_only_fields = [
            "id",
            "non_member_id",
            "visit_count",
            "created_at",
            "updated_at",
        ]

    def validate_mobile_no(self, value):
        # Check if mobile number already exists
        if NonMember.objects.filter(mobile_no=value, is_deleted=False).exists():
            if self.instance and self.instance.mobile_no == value:
                return value  # Allow same mobile for update
            raise serializers.ValidationError(
                _("Non-member with this mobile number already exists.")
            )
        return value


class NonMemberCattleSerializer(serializers.ModelSerializer):
    """Serializer for NonMemberCattle model"""

    non_member_name = serializers.CharField(source="non_member.name", read_only=True)
    non_member_mobile = serializers.CharField(
        source="non_member.mobile_no", read_only=True
    )

    class Meta:
        model = NonMemberCattle
        fields = [
            "id",
            "non_member",
            "non_member_name",
            "non_member_mobile",
            "tag_number",
            "breed",
            "age_years",
            "age_months",
            "weight_kg",
            "is_pregnant",
            "pregnancy_months",
            "additional_details",
            "is_active",
            "created_at",
            "updated_at",
            "sync",
            "is_deleted",
        ]
        read_only_fields = ["created_at", "updated_at"]


class CaseEntrySerializer(serializers.ModelSerializer):
    """Enhanced CaseEntry serializer including nested location details."""

    member_name = serializers.CharField(read_only=True)
    member_mobile = serializers.CharField(read_only=True)
    animal_tag = serializers.CharField(read_only=True)
    is_member_case = serializers.BooleanField(read_only=True)

    cattle_detail = serializers.SerializerMethodField()
    non_member_cattle_detail = serializers.SerializerMethodField()
    payment_status = serializers.SerializerMethodField()
    location_detail = serializers.SerializerMethodField()  # nested

    class Meta:
        model = CaseEntry
        fields = [
            "case_no",
            "cattle",
            "non_member_cattle",
            "created_by",
            "status",
            "address",
            "remark",
            "disease_name",
            "visit_date",
            "is_tagged_animal",
            "is_emergency",
            "calculated_cost",
            "created_at",
            "updated_at",
            "sync",
            # Existing
            "member_name",
            "member_mobile",
            "animal_tag",
            "is_member_case",
            "cattle_detail",
            "payment_status",
            "non_member_cattle_detail",
            # Nested location
            "location_detail",
        ]
        read_only_fields = ["case_no", "calculated_cost", "created_at", "updated_at"]

    # --------------------------
    # LOCATION DETAIL METHOD
    # --------------------------
    def get_location_detail(self, obj: CaseEntry):
        qs = obj.get_case_locations
        snapshot = qs.first()

        if not snapshot:
            return None

        return {
            "mcc": {
                "code": snapshot.mcc_code or "",
                "tr_code": snapshot.mcc_tr_code or "",
                "name": snapshot.mcc_name or "",
            },
            "bmc": {
                "code": snapshot.bmc_code or "",
                "tr_code": snapshot.bmc_tr_code or "",
                "name": snapshot.bmc_name or "",
            },
            "mpp": {
                "code": snapshot.mpp_code or "",
                "ex_code": snapshot.mpp_ex_code or "",
                "tr_code": snapshot.mpp_tr_code or "",
                "name": snapshot.mpp_name or "",
                "type": snapshot.mpp_type or "",
            },
            "route": {
                "code": snapshot.route_code or "",
                "ex_code": snapshot.route_ex_code or "",
                "name": snapshot.route_name or "",
            },
        }

    # --------------------------
    # OTHER METHODS
    # --------------------------
    def get_cattle_detail(self, obj):
        if obj.cattle:
            breed_data = None
            if getattr(obj.cattle, "breed", None):
                breed_data = SpeciesBreedSerializer(obj.cattle.breed).data

            return {
                "id": obj.cattle.id,
                "tag_number": getattr(obj.cattle, "tag_number", "N/A"),
                "breed": breed_data or "N/A",
                "member_name": (
                    obj.cattle.owner.member_name
                    if getattr(obj.cattle, "owner", None)
                    else "N/A"
                ),
            }
        return None

    def get_non_member_cattle_detail(self, obj):
        if obj.non_member_cattle:
            return NonMemberCattleSerializer(obj.non_member_cattle).data
        return None

    def get_payment_status(self, obj: CaseEntry):
        return obj.get_payment_status()

    def validate(self, data):
        cattle = data.get("cattle")
        non_member_cattle = data.get("non_member_cattle")

        if not cattle and not non_member_cattle:
            raise serializers.ValidationError(
                _("Either member cattle or non-member cattle must be specified.")
            )

        if cattle and non_member_cattle:
            raise serializers.ValidationError(
                _("Cannot specify both member cattle and non-member cattle.")
            )

        return data


class CaseEntryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing case entries"""

    owner_name = serializers.CharField(read_only=True)
    owner_mobile = serializers.CharField(read_only=True)
    animal_tag = serializers.CharField(read_only=True)
    is_member_case = serializers.BooleanField(read_only=True)
    case_type = serializers.SerializerMethodField()

    class Meta:
        model = CaseEntry
        fields = [
            "case_no",
            "status",
            "owner_name",
            "owner_mobile",
            "animal_tag",
            "disease_name",
            "visit_date",
            "calculated_cost",
            "is_member_case",
            "case_type",
            "created_at",
            "is_emergency",
        ]

    def get_case_type(self, obj):
        return "Member" if obj.is_member_case else "Non-Member"


from erp_app.models import BusinessHierarchySnapshot


class QuickVisitRegistrationSerializer(serializers.Serializer):
    """Simplified serializer for quick visit registration from mobile app"""

    mpp_code = serializers.CharField(max_length=255, required=False, allow_blank=True)
    is_member = serializers.BooleanField(
        help_text="True for member, False for non-member"
    )
    member_code = serializers.CharField(
        max_length=255, required=False, allow_blank=True
    )

    # Member fields
    cattle_id = serializers.IntegerField(required=False, allow_null=True)

    # Non-member fields
    non_member_name = serializers.CharField(
        max_length=255, required=False, allow_blank=True
    )
    non_member_mobile = serializers.CharField(
        max_length=15, required=False, allow_blank=True
    )
    non_member_address = serializers.CharField(required=False, allow_blank=True)

    # Common animal info
    animal_tag_number = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )
    age_month = serializers.CharField(max_length=100, required=False, allow_blank=True)
    gender = serializers.CharField(max_length=100, required=True)
    age_year = serializers.CharField(max_length=100, required=False, allow_blank=True)
    weight_kg = serializers.DecimalField(required=False, max_digits=6, decimal_places=2)
    is_pregnant = serializers.BooleanField(required=False)
    pregnancy_months = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )
    breed_id = serializers.IntegerField(required=True)
    animal_details = serializers.CharField(required=False, allow_blank=True)

    # Case details
    disease_name = serializers.CharField(max_length=255)
    address = serializers.CharField(max_length=255)
    remark = serializers.CharField(required=False, allow_blank=True)
    visit_date = serializers.DateTimeField()
    is_tagged_animal = serializers.BooleanField(default=True)
    is_emergency = serializers.BooleanField(default=False)

    # ---------------- VALIDATION ----------------

    def validate(self, data):
        is_member = data.get("is_member")
        owner = data.get("member_code")
        is_tagged = data.get("is_tagged_animal", True)

        if is_member:
            if not owner:
                raise serializers.ValidationError(
                    _("Member code is required for if type is member")
                )
            # If the animal is tagged, cattle_id is mandatory
            if is_tagged and not data.get("cattle_id"):
                raise serializers.ValidationError(
                    _("Cattle ID is required for tagged member animals.")
                )

            # If untagged, we’ll create a new cattle record from provided data
            if not is_tagged:
                required_fields = ["age_month", "age_year"]
                missing_fields = [f for f in required_fields if not data.get(f)]
                if missing_fields:
                    raise serializers.ValidationError(
                        _(
                            f"Missing required fields for untagged member cattle: {', '.join(missing_fields)}"
                        )
                    )

        else:
            # Non-member: basic required fields
            if is_tagged and not data.get("animal_tag_number"):
                raise serializers.ValidationError(_(f"Animal Tag Number is required"))

            for field in ["non_member_name", "non_member_mobile"]:
                if not data.get(field):
                    raise serializers.ValidationError(
                        _(f"{field} is required for non-member cases.")
                    )

        return data

    # ---------------- HELPERS ----------------
    def _get_user(self):
        """Safely extract request user from context."""
        return self.context["request"].user if "request" in self.context else None

    def _get_mpp(self, code):
        """Fetch MPP snapshot safely."""
        return BusinessHierarchySnapshot.objects.filter(mpp_ex_code=code).first()

    def _create_case_entry(self, cattle_obj, validated_data, non_member_cattle=None):
        """Centralized CaseEntry creation."""
        return CaseEntry.objects.create(
            cattle=cattle_obj if not non_member_cattle else None,
            non_member_cattle=non_member_cattle,
            disease_name=validated_data["disease_name"],
            address=validated_data["address"],
            remark=validated_data.get("remark", ""),
            visit_date=validated_data["visit_date"],
            is_tagged_animal=validated_data["is_tagged_animal"],
            is_emergency=validated_data["is_emergency"],
            created_by=self._get_user(),
        )

    # ---------------- CREATE ----------------
    @transaction.atomic
    def create(self, validated_data):
        is_member = validated_data["is_member"]
        mpp = self._get_mpp(validated_data.get("mpp_code"))

        if is_member:
            cattle_id = validated_data.get("cattle_id")

            if cattle_id:
                # Existing cattle
                cattle = Cattle.objects.get(id=cattle_id)
                created = False
            else:
                # Create a new cattle
                cattle = Cattle.objects.create(
                    owner_id=validated_data.get("member_code"),
                    breed_id=validated_data.get("breed_id"),
                    gender=validated_data.get("gender"),
                    age=validated_data.get("age_month"),
                    age_year=validated_data.get("age_year"),
                    weight_kg=validated_data.get("weight_kg"),
                    no_of_calving=validated_data.get("no_of_calving"),
                )
                created = True

            if created:
                CattleStatusLog.objects.create(
                    cattle=cattle,
                    is_current=True,
                    pregnancy_status=validated_data.get("is_pregnant"),
                    from_date=datetime.today().date(),
                )

            case_entry = self._create_case_entry(cattle, validated_data)

        else:
            # Non-member flow
            non_member, _ = NonMember.objects.get_or_create(
                mobile_no=validated_data["non_member_mobile"],
                defaults={
                    "mcc_code": mpp.mcc_tr_code if mpp else None,
                    "mcc_name": mpp.mcc_name if mpp else "",
                    "mpp_code": mpp.mpp_ex_code if mpp else "",
                    "mpp_name": mpp.mpp_name if mpp else "",
                    "name": validated_data["non_member_name"],
                    "address": validated_data.get("non_member_address", ""),
                    "created_by": self._get_user(),
                },
            )

            non_member_cattle, _ = NonMemberCattle.objects.get_or_create(
                non_member=non_member,
                tag_number=validated_data["animal_tag_number"],
                defaults={
                    "breed_id": validated_data.get("breed_id"),
                    "age_years": validated_data.get("age_year"),
                    "age_months": validated_data.get("age_month"),
                    "weight_kg": validated_data.get("weight_kg"),
                    "is_pregnant": validated_data.get("is_pregnant"),
                    "pregnancy_months": (
                        validated_data.get("pregnancy_months")
                        if validated_data.get("pregnancy_months")
                        else None
                    ),
                    "additional_details": validated_data.get("animal_details", ""),
                },
            )

            case_entry = self._create_case_entry(
                None, validated_data, non_member_cattle
            )

        return case_entry


# Utility serializers for mobile app
class OwnerSearchSerializer(serializers.Serializer):
    """Serializer for searching owners by mobile number"""

    mobile_no = serializers.CharField(max_length=15)

    def validate_mobile_no(self, value):
        if len(value) < 10:
            raise serializers.ValidationError(
                _("Mobile number should be at least 10 digits.")
            )
        return value


class OwnerSearchResultSerializer(serializers.Serializer):
    """Results for owner search"""

    is_member = serializers.BooleanField()
    owner_id = serializers.IntegerField()
    owner_name = serializers.CharField()
    owner_mobile = serializers.CharField()
    owner_address = serializers.CharField()
    cattle_list = serializers.ListField(child=serializers.DictField())


class CostCalculationSerializer(serializers.Serializer):
    """Serializer for calculating treatment cost"""

    is_member = serializers.BooleanField()
    visit_datetime = serializers.DateTimeField()
    is_tagged_animal = serializers.BooleanField(default=True)
    is_emergency = serializers.BooleanField(default=False)

    def calculate_cost(self):
        """Calculate treatment cost based on provided data"""
        from datetime import time

        is_member = self.validated_data["is_member"]
        visit_datetime = self.validated_data["visit_datetime"]
        is_tagged = self.validated_data["is_tagged_animal"]
        is_emergency = self.validated_data["is_emergency"]

        visit_time = visit_datetime.time()
        is_after_10 = visit_time >= time(10, 0)  # After 10:00 AM

        # Cost calculation logic from your pricing table
        if is_member:
            if is_after_10:
                base_cost = 500 if is_tagged else 600
                emergency_cost = 1500 if is_tagged else 1000
            else:
                base_cost = 300 if is_tagged else 400
                emergency_cost = 1200 if is_tagged else 800
        else:  # Non-member
            if is_after_10:
                base_cost = 600 if is_tagged else 700
                emergency_cost = 2000 if is_tagged else 1200
            else:
                base_cost = 500 if is_tagged else 600
                emergency_cost = 1500 if is_tagged else 1000

        final_cost = emergency_cost if is_emergency else base_cost

        return {
            "calculated_cost": final_cost,
            "is_member": is_member,
            "is_emergency": is_emergency,
            "is_after_10am": is_after_10,
            "is_tagged_animal": is_tagged,
            "cost_breakdown": {
                "base_cost": base_cost,
                "emergency_cost": emergency_cost,
                "applied_cost": final_cost,
            },
        }


from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


class TreatmentCostConfigurationSerializer(serializers.ModelSerializer):
    """
    Serializer for TreatmentCostConfiguration model.
    Handles creation, update, and detailed representation with choice labels.
    """

    # Add display fields for better readability in API responses
    membership_type_display = serializers.CharField(
        source="get_membership_type_display", read_only=True
    )
    time_slot_display = serializers.CharField(
        source="get_time_slot_display", read_only=True
    )
    animal_tag_type_display = serializers.CharField(
        source="get_animal_tag_type_display", read_only=True
    )
    treatment_type_display = serializers.CharField(
        source="get_treatment_type_display", read_only=True
    )

    created_by_username = serializers.CharField(
        source="created_by.username", read_only=True
    )

    class Meta:
        model = TreatmentCostConfiguration
        fields = [
            "id",
            "membership_type",
            "membership_type_display",
            "time_slot",
            "time_slot_display",
            "animal_tag_type",
            "animal_tag_type_display",
            "treatment_type",
            "treatment_type_display",
            "cost_amount",
            "is_active",
            "effective_from",
            "effective_to",
            "description",
            "created_by",
            "created_by_username",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "created_by",
            "created_by_username",
            "created_at",
            "updated_at",
        )

    # Custom validation logic
    def validate(self, attrs):
        effective_from = attrs.get("effective_from")
        effective_to = attrs.get("effective_to")

        # Check date consistency
        if effective_to and effective_to < effective_from:
            raise serializers.ValidationError(
                _("Effective to date cannot be earlier than effective from date.")
            )

        # Ensure no overlapping configurations for the same combination
        qs = TreatmentCostConfiguration.objects.filter(
            membership_type=attrs.get("membership_type"),
            time_slot=attrs.get("time_slot"),
            animal_tag_type=attrs.get("animal_tag_type"),
            treatment_type=attrs.get("treatment_type"),
            is_active=True,
        )

        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        for existing in qs:
            if (
                not existing.effective_to or existing.effective_to >= effective_from
            ) and existing.effective_from <= (effective_to or effective_from):
                raise serializers.ValidationError(
                    _("Overlapping effective date range found for same configuration.")
                )

        return attrs

    # Automatically set created_by from request user
    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["created_by"] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated and not instance.created_by:
            validated_data["created_by"] = request.user
        return super().update(instance, validated_data)
