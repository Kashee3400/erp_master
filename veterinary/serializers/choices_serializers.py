from rest_framework import serializers

from ..models.common_models import (
    Species,
    SpeciesBreed,
    AICharge,
    CattleCaseStatus,
    CattleCaseType,
    TimeSlot,
    Vehicle,
    VehicleKiloMeterLog,
)
from erp_app.models import Mcc
from ..models.models import MembersMasterCopy


# ✅ List Serializer — for lightweight responses in list views
class SpeciesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Species
        fields = [
            "id",
            "scientific_name",
            "animal_type",
            "category",
            "slug",
            "is_milk_producing",
        ]
        read_only_fields = fields


# ✅ Detail Serializer — for full object representation
class SpeciesDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Species
        fields = [
            "id",
            "animal_type",
            "scientific_name",
            "category",
            "description",
            "average_lifespan",
            "is_milk_producing",
            "slug",
        ]
        read_only_fields = ["id", "slug"]


class SpeciesBreedSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeciesBreed
        fields = [
            "id",
            "breed",
            "animal_type",
            "origin_country",
            "average_milk_yield",
            "color",
            "adaptability",
            "description",
        ]
        read_only_fields = ["id"]


class AIChargeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = AICharge
        fields = ["id", "user_role", "user", "amount"]
        read_only_fields = ["id"]


class CattleCaseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CattleCaseType
        fields = ["id", "case_type", "description"]
        read_only_fields = ["id"]


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = [
            "id",
            "start_time",
            "end_time",
            "period",
            "normal_cost",
            "operational_cost",
            "sync",
        ]
        read_only_fields = ["id"]


class CattleCaseStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CattleCaseStatus
        fields = ["id", "status"]
        read_only_fields = ["id"]


class MembersMasterListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembersMasterCopy
        fields = [
            "mcc_code",
            "bmc_code",
            "mpp_code",
            "member_code",
            "member_tr_code",
            "member_name",
            "member_middle_name",
            "member_surname",
            "gender",
            "mobile_no",
            "is_active",
            "created_at",
        ]


class MembersMasterDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembersMasterCopy
        fields = [
            "company_code",
            "plant_code",
            "mcc_code",
            "bmc_code",
            "mpp_code",
            "member_code",
            "member_tr_code",
            "member_name",
            "member_middle_name",
            "member_surname",
            "gender",
            "mobile_no",
            "member_type",
            "caste_category",
            "birth_date",
            "age",
            "is_active",
            "wef_date",
            "is_default",
            "created_at",
            "folio_no",
            "application_date",
            "application_no",
            "created_by",
            "member_master_relation",
            "ex_member_code",
            "device_id",
            "user",
        ]


class MccSerializer(serializers.ModelSerializer):

    class Meta:
        model = Mcc
        fields = ["mcc_code", "mcc_ex_code", "mcc_name", "is_active"]


from erp_app.models import BusinessHierarchySnapshot


class BusinessHierarchySnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessHierarchySnapshot
        fields = [
            "mcc_code",
            "mcc_tr_code",
            "mcc_name",
            "bmc_code",
            "bmc_tr_code",
            "bmc_name",
            "mpp_code",
            "mpp_ex_code",
            "mpp_tr_code",
            "mpp_name",
            "mpp_type",
            "route_code",
            "route_ex_code",
            "route_name",
        ]


class VehicleSerializer(serializers.ModelSerializer):

    class Meta:

        model = Vehicle
        fields = [
            "id",
            "created_at",
            "updated_at",
            "is_deleted",
            "is_active",
            "updated_by",
            "sync",
            "locale",
            # Model fields
            "registration_number",
            "model_name",
            "vehicle_type",
            "chassis_number",
            "engine_number",
            "purchase_date",
            "registration_date",
            "seating_capacity",
            "fuel_type",
            "insurance_valid_upto",
            "puc_valid_upto",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "updated_by",
        ]

class VehicleKilometerLogSerializer(serializers.ModelSerializer):
    vehicle = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all())
    vehicle_detail = VehicleSerializer(source="vehicle", read_only=True)

    # 👇 extra fields for human-readable names
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    updated_by_name = serializers.CharField(source="updated_by.get_full_name", read_only=True)

    class Meta:
        model = VehicleKiloMeterLog
        fields = [
            "id",
            "user",
            "user_name",        # 👈 added
            "district",
            "vehicle",
            "vehicle_detail",
            "driver_name",
            "opening_datetime",
            "closing_datetime",
            "opening_km",
            "closing_km",
            "place_of_visit",
            "purpose_of_journey",
            "created_at",
            "updated_at",
            "is_deleted",
            "is_active",
            "updated_by",
            "updated_by_name",  # 👈 added
            "sync",
            "locale",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "updated_by",
            "user_full_name",
            "updated_by_full_name",
        ]

