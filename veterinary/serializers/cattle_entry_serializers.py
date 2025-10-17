from rest_framework import serializers
from ..models.models import (
    Cattle,
    CattleStatusType,
    CattleTagging,
    CattleStatusLog,
    FarmerMeeting,
    ObservationType,
    FarmerObservation,
)
from ..choices import TagActionChoices


class CattleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cattle
        fields = [
            "id",
            "name",
            "owner",
            "breed",
            "gender",
            "age",
            "age_year",
            "no_of_calving",
            "mother",
            "father",
            "locale",
            "date_of_birth",
            "is_alive",
            "is_active",
            "current_status",
            "created_at",
            "updated_at",
            "updated_by",
            "is_deleted",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "updated_by",
            "is_deleted",
        ]

    def validate(self, data):
        """
        Model-level validations.
        """
        if not data.get("age") and not data.get("date_of_birth"):
            raise serializers.ValidationError(
                "Either age or date of birth must be provided."
            )

        if data.get("mother") and data.get("mother") == self.instance:
            raise serializers.ValidationError("Cattle cannot be its own mother.")

        if data.get("father") and data.get("father") == self.instance:
            raise serializers.ValidationError("Cattle cannot be its own father.")

        return data

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["updated_by"] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        validated_data["updated_by"] = user
        return super().update(instance, validated_data)


class CattleListSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source="owner.member_name", read_only=True)
    tag_number = serializers.CharField(
        source="cattle_tagged.tag_number", read_only=True
    )
    breed_type = serializers.CharField(source="breed.animal_type", read_only=True)
    breed_name = serializers.CharField(source="breed.breed", read_only=True)
    status = serializers.CharField(source="current_status.label", read_only=True)
    tagging_url = serializers.HyperlinkedRelatedField(
        source="cattle_tagged",
        view_name="cattletagging-detail",
        read_only=True,
        lookup_field="pk",
    )

    class Meta:
        model = Cattle
        fields = [
            "id",
            "tag_number",
            "name",
            "owner",
            "breed",
            "breed_name",
            "breed_type",
            "gender",
            "age",
            "age_year",
            "is_alive",
            "status",
            "tagging_url",
        ]


class CattleTaggingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CattleTagging
        fields = [
            "id",
            "cattle",
            "image",
            "tag_number",
            "tag_method",
            "tag_location",
            "tag_action",
            "replaced_on",
            "remarks",
            "locale",
            "created_at",
            "updated_at",
            "updated_by",
            "is_active",
            "is_deleted",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "updated_by",
            "is_deleted",
        ]

    def validate(self, data):
        if data.get("tag_action") == TagActionChoices.REPLACED and not data.get(
                "replaced_on"
        ):
            raise serializers.ValidationError(
                {"replaced_on": "This field is required when tag action is 'REPLACED'."}
            )
        return data

    def create(self, validated_data):
        validated_data["updated_by"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_by"] = self.context["request"].user
        return super().update(instance, validated_data)


class CattleTaggingListSerializer(serializers.ModelSerializer):
    cattle_id = serializers.PrimaryKeyRelatedField(
        source="cattle", queryset=Cattle.objects.all()
    )
    cattle_url = serializers.HyperlinkedRelatedField(
        source="cattle",
        view_name="cattle-detail",
        read_only=True,
        lookup_field="pk",
    )

    class Meta:
        model = CattleTagging
        fields = [
            "id",
            "tag_number",
            "tag_method",
            "tag_location",
            "tag_action",
            "cattle_id",
            "cattle_url",
        ]


class CattleStatusTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CattleStatusType
        fields = ["id", "code", "label", "is_active"]


class CattleStatusLogSerializer(serializers.ModelSerializer):
    statuses = CattleStatusTypeSerializer(many=True, read_only=True)
    cattle = serializers.PrimaryKeyRelatedField(queryset=Cattle.objects.all())

    class Meta:
        model = CattleStatusLog
        fields = [
            "id",
            "cattle",
            "last_calving_month",
            "statuses",
            "from_date",
            "to_date",
            "notes",
            "pregnancy_status",
            "lactation_count",  # 🔹 new field
            "milk_production_lpd",  # 🔹 new field
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]

    def create(self, validated_data):
        statuses = self.initial_data.get("statuses", [])
        instance = super().create(validated_data)
        if statuses:
            instance.statuses.set(statuses)
        return instance

    def update(self, instance, validated_data):
        statuses = self.initial_data.get("statuses", None)
        instance = super().update(instance, validated_data)
        if statuses is not None:
            instance.statuses.set(statuses)
        return instance


from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from ..models.models import (
    Cattle,
    CattleTagging,
    SpeciesBreed,
    MembersMasterCopy,
    CattleStatusType,
)


class BreedSerializer(serializers.ModelSerializer):
    """Serializer for Species Breed information"""

    animal_type_name = serializers.SerializerMethodField()

    class Meta:
        model = SpeciesBreed
        fields = [
            "id",
            "breed",
            "animal_type",
            "animal_type_name",
            "origin_country",
            "average_milk_yield",
            "color",
            "adaptability",
            "description",
        ]

    def get_animal_type_name(self, obj):
        if hasattr(obj, "animal_type") and hasattr(obj.animal_type, "animal_type"):
            return obj.animal_type.animal_type or ""
        return ""


class OwnerSerializer(serializers.ModelSerializer):
    """Serializer for cattle owner information"""

    class Meta:
        model = MembersMasterCopy
        fields = [
            "member_code",
            "mpp_code",
            "mcc_code",
            "member_tr_code",
            "member_name",
            "mobile_no",
        ]


class CattleStatusSerializer(serializers.ModelSerializer):
    """Serializer for cattle status information"""

    class Meta:
        model = CattleStatusType
        fields = ["id", "code", "label", "is_active"]


class SimpleCattleSerializer(serializers.ModelSerializer):
    """Simple serializer for parent cattle (mother/father) to avoid circular references"""

    breed_name = serializers.CharField(source="breed.breed", read_only=True)
    breed_type = serializers.CharField(source="breed.animal_type", read_only=True)
    tag_number = serializers.CharField(
        source="cattle_tagged.tag_number", read_only=True
    )

    class Meta:
        model = Cattle
        fields = ["id", "breed_name", "breed_type", "name", "tag_number", "gender"]


class CattleTagSerializer(serializers.ModelSerializer):
    """Serializer for cattle tagging information"""

    tag_method_display = serializers.CharField(
        source="get_tag_method_display", read_only=True
    )
    tag_location_display = serializers.CharField(
        source="get_tag_location_display", read_only=True
    )
    tag_action_display = serializers.CharField(
        source="get_tag_action_display", read_only=True
    )

    class Meta:
        model = CattleTagging
        fields = [
            "id",
            "tag_number",
            "virtual_tag_no",  # 🔹 include virtual tag no
            "tag_method",
            "tag_method_display",
            "tag_location",
            "tag_location_display",
            "tag_action",
            "tag_action_display",
            "replaced_on",
            "remarks",
            "image",
        ]
        read_only_fields = ["virtual_tag_no"]  # ensure it cannot be set manually


class CattleDetailSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for cattle detail view"""

    owner = serializers.PrimaryKeyRelatedField(queryset=MembersMasterCopy.objects.all())
    current_status = serializers.PrimaryKeyRelatedField(
        queryset=CattleStatusType.objects.all()
    )
    breed = serializers.PrimaryKeyRelatedField(queryset=SpeciesBreed.objects.all())
    mother = serializers.PrimaryKeyRelatedField(
        queryset=Cattle.objects.all(), allow_null=True
    )
    father = serializers.PrimaryKeyRelatedField(
        queryset=Cattle.objects.all(), allow_null=True
    )

    # Nested serializers for read-only (optional)
    owner_detail = OwnerSerializer(source="owner", read_only=True)
    current_status_detail = CattleStatusTypeSerializer(
        source="current_status", read_only=True
    )
    breed_detail = BreedSerializer(source="breed", read_only=True)
    mother_detail = SimpleCattleSerializer(source="mother", read_only=True)
    father_detail = SimpleCattleSerializer(source="father", read_only=True)

    # Tagging information
    cattle_tagged = CattleTagSerializer(read_only=True)

    # Display fields
    gender_display = serializers.CharField(source="get_gender_display", read_only=True)

    # Calculated fields
    age_display = serializers.SerializerMethodField()
    offspring_count = serializers.SerializerMethodField()
    is_breeding_age = serializers.SerializerMethodField()

    # Image field with proper URL
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Cattle
        fields = [
            # Basic information
            "id",
            "name",
            "gender",
            "gender_display",
            "age",
            "age_year",
            "date_of_birth",
            "is_alive",
            # Relationships
            "owner",
            "breed",
            "current_status",
            "mother",
            "father",
            "owner_detail",
            "breed_detail",
            "current_status_detail",
            "mother_detail",
            "father_detail",
            # Breeding information
            "no_of_calving",
            "offspring_count",
            "is_breeding_age",
            # Display fields
            "age_display",
            "image_url",
            # Tagging information
            "cattle_tagged",
            # Timestamps
            "created_at",
            "updated_at",
        ]

    def get_age_display(self, obj):
        """Get formatted age display (e.g., '2y 3m')"""
        if obj.age_year and obj.age:
            return f"{obj.age_year}y {obj.age}m"
        return "0"

    def get_offspring_count(self, obj):
        """Get total number of offspring"""
        male_offspring = obj.offspring_from_father.filter(is_alive=True).count()
        female_offspring = obj.offspring_from_mother.filter(is_alive=True).count()
        return male_offspring + female_offspring

    def get_is_breeding_age(self, obj):
        """Check if cattle is of breeding age"""
        if not obj.age:
            return False

        # Generally, cattle reach breeding age around 15-18 months
        breeding_age_months = 15
        return obj.age >= breeding_age_months

    def get_image_url(self, obj):
        """Get full image URL"""
        request = self.context.get("request")

        if (
                hasattr(obj, "cattle_tagged")
                and obj.cattle_tagged
                and obj.cattle_tagged.image
        ):
            if request:
                return request.build_absolute_uri(obj.cattle_tagged.image.url)
            return obj.cattle_tagged.image.url
        return None


class CattleStatsSerializer(serializers.Serializer):
    """Serializer for cattle statistics"""

    total_cattle = serializers.IntegerField()
    alive_cattle = serializers.IntegerField()
    male_cattle = serializers.IntegerField()
    female_cattle = serializers.IntegerField()
    breeding_age_cattle = serializers.IntegerField()
    total_calving = serializers.IntegerField()

    def to_representation(self, instance):
        """Custom representation for stats"""
        return {
            "total_cattle": instance.get("total_cattle", 0),
            "alive_cattle": instance.get("alive_cattle", 0),
            "male_cattle": instance.get("male_cattle", 0),
            "female_cattle": instance.get("female_cattle", 0),
            "breeding_age_cattle": instance.get("breeding_age_cattle", 0),
            "total_calving": instance.get("total_calving", 0),
            "mortality_rate": round(
                (
                        (instance.get("total_cattle", 0) - instance.get("alive_cattle", 0))
                        / max(instance.get("total_cattle", 1), 1)
                )
                * 100,
                2,
            ),
        }


from ..utils.base64field import Base64ImageField


class FarmerMeetingSerializer(serializers.ModelSerializer):
    members_detail = OwnerSerializer(source="members", many=True, read_only=True)
    updated_by_name = serializers.CharField(
        source="updated_by.get_full_name", read_only=True
    )
    image = Base64ImageField(required=False, allow_null=True)
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FarmerMeeting
        fields = [
            "id",
            "mcc_code",
            "mcc_ex_code",
            "mcc_name",
            "mpp_code",
            "mpp_ex_code",
            "mpp_name",
            "members",
            "members_detail",
            "total_participants",
            "image",
            "image_url",
            "updated_by_name",
            "notes",
            "created_at",
            "updated_at",
            "updated_by"
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "updated_by",
            "members_detail",
            "updated_by_name",
            "image_url",
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and hasattr(obj.image, "url"):
            return request.build_absolute_uri(obj.image.url)
        return None

    def create(self, validated_data):
        validated_data["updated_by"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_by"] = self.context["request"].user
        return super().update(instance, validated_data)


class ObservationSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(
        source="updated_by.get_full_name", read_only=True
    )

    class Meta:
        model = ObservationType
        fields = [
            "id",
            "name",
            "description",
            "created_at",
            "updated_at",
            "updated_by",
            "updated_by_name",
        ]
        read_only_fields = [
            "id",
            "updated_by_name",
            "created_at",
            "updated_at",
        ]


class FarmerObservationSerializer(serializers.ModelSerializer):
    member_detail = OwnerSerializer(source="member", read_only=True)
    updated_by_name = serializers.CharField(
        source="updated_by.get_full_name", read_only=True
    )
    observation_detail = ObservationSerializer(
        source="observation_type", read_only=True
    )

    class Meta:
        model = FarmerObservation
        fields = [
            "id",
            "mcc_code",
            "mcc_ex_code",
            "mcc_name",
            "mpp_code",
            "mpp_ex_code",
            "mpp_name",
            "member",
            "member_detail",
            "animal",
            "animal_detail",
            "updated_by_name",
            "observation_type",
            "observation_detail",
            "notes"
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "updated_by",
            "member_detail",
            "updated_by_name",
            "animal_detail",
            "observation_detail",
        ]
