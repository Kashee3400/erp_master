from rest_framework import serializers
from .models.models import *



class TAGTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TAGType
        fields = '__all__'


class CattleCaseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CattleCaseType
        fields = '__all__'

class TimeSlotSerializer(serializers.ModelSerializer):
    case_type = CattleCaseTypeSerializer(read_only=True)
    class Meta:
        model = TimeSlot
        fields = '__all__'
        

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'

class DiagnosisRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosisRoute
        fields = '__all__'

class SymptomsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptoms
        fields = '__all__'

class DiseaseSerializer(serializers.ModelSerializer):
    symptoms = SymptomsSerializer(many=True)
    class Meta:
        model = Disease
        fields = '__all__'

class CattleTaggingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CattleTagging
        fields = '__all__'

        
from rest_framework import serializers
from .models.models import Cattle, AnimalBreed, TAGType, AnimalType

class AnimalTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalType
        fields = '__all__'

class AnimalBreedSerializer(serializers.ModelSerializer):
    animal_type_data = AnimalTypeSerializer(source='animal_type', read_only=True)
    
    class Meta:
        model = AnimalBreed
        fields = ['breed', 'created_at', 'sync', 'animal_type_data']

class TAGTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TAGType
        fields = '__all__'

class CattleSerializer(serializers.ModelSerializer):
    breed_data = AnimalBreedSerializer(source='breed', read_only=True)
    tag_type_data = TAGTypeSerializer(source='tag_type', read_only=True)

    class Meta:
        model = Cattle
        fields = ['id', 'tag_type_data', 'breed_data', 'tag_number', 'gender', 'sync', 'farmer']

    def get_animal_type_data(self, obj):
        return AnimalTypeSerializer(obj.breed.animal_type).data


class PaymentMethodSerializer(serializers.ModelSerializer):
    method_display = serializers.SerializerMethodField()

    def get_method_display(self, obj):
        return {
            "code": obj.method,
            "name": obj.get_method_display()
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        method_display = representation.pop('method_display')
        representation.update(method_display)
        return representation

    class Meta:
        model = PaymentMethod
        fields = ['id', 'method_display', 'sync']



class CaseEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseEntry
        fields = '__all__'
