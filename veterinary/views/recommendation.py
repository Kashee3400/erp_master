# views/recommendation.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..serializers.recommendation import DiseaseWithMedicineSerializer
from ..services.recommendation import get_medicine_recommendations_from_symptoms

class MedicineRecommendationView(APIView):
    """
    POST endpoint to recommend medicines based on symptoms.
    """

    def post(self, request, *args, **kwargs):
        symptom_ids = request.data.get("symptom_ids", [])

        if not symptom_ids or not isinstance(symptom_ids, list):
            return Response(
                {"detail": "symptom_ids must be a list of integers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        recommendations = get_medicine_recommendations_from_symptoms(symptom_ids)
        return Response(recommendations, status=status.HTTP_200_OK)


# {
#   "symptom_ids": [1, 3, 5]
# }

# [
#   {
#     "disease": {
#       "id": 2,
#       "name": "Mastitis",
#       "description": "Inflammation of the mammary gland",
#       "treatment": "Antibiotics, udder hygiene"
#     },
#     "medicines": [
#       {
#         "id": 10,
#         "medicine": "Oxytetracycline",
#         "strength": "200mg",
#         "packaging": "10 tablets per strip",
#         "expiry_date": "2026-12-31T00:00:00Z"
#       }
#     ]
#   },
#   ...
# ]
