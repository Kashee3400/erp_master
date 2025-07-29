# serializers/recommendation.py

from rest_framework import serializers
from ..models.case_models import Disease, Medicine

class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = ["id", "medicine", "strength", "packaging", "expiry_date"]

class DiseaseWithMedicineSerializer(serializers.Serializer):
    disease = serializers.DictField()
    medicines = MedicineSerializer(many=True)
