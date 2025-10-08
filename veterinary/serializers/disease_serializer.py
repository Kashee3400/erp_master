from rest_framework import serializers
from ..models.case_models import Disease, Symptoms


class SymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptoms
        fields = ["id", "symptom", "description"]
        read_only_fields = ["id"]


class DiseaseSerializer(serializers.ModelSerializer):
    # For nested read (list/retrieve) → shows full symptom objects
    symptoms = SymptomSerializer(many=True, read_only=True)

    # For create/update → allow passing a list of symptom IDs
    symptom_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Symptoms.objects.all(),
        source="symptoms",  # maps directly to the M2M field
        required=False,
    )

    class Meta:
        model = Disease
        fields = [
            "id",
            "disease",
            "description",
            "treatment",
            "severity",
            "symptoms",
            "symptom_ids",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        # Pop symptom list if provided
        symptoms = validated_data.pop("symptoms", [])
        disease = Disease.objects.create(**validated_data)
        if symptoms:
            disease.symptoms.set(symptoms)
        return disease

    def update(self, instance, validated_data):
        symptoms = validated_data.pop("symptoms", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if symptoms is not None:
            instance.symptoms.set(symptoms)

        return instance
