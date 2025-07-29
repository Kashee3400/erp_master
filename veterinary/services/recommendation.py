# services/recommendation.py

from django.db.models import Prefetch
from ..models.case_models import Disease, Medicine, Symptoms,DiseaseSeverity


SEVERITY_WEIGHT = {
    DiseaseSeverity.MILD: 1,
    DiseaseSeverity.MODERATE: 2,
    DiseaseSeverity.SEVERE: 3,
    DiseaseSeverity.CRITICAL: 4,
}

def get_ranked_recommendations(symptom_ids: list[int]):
    if not symptom_ids:
        return []

    diseases = Disease.objects.prefetch_related("symptoms", "medicines").all()

    results = []

    for disease in diseases:
        disease_symptoms = set(disease.symptoms.values_list("id", flat=True))
        matched_symptoms = disease_symptoms.intersection(symptom_ids)

        match_score = len(matched_symptoms) / len(disease_symptoms) if disease_symptoms else 0
        severity_score = SEVERITY_WEIGHT.get(disease.severity, 1)

        # Composite score (can be tuned further)
        composite_score = match_score * severity_score

        if match_score > 0:
            results.append({
                "disease": {
                    "id": disease.id,
                    "name": disease.disease,
                    "description": disease.description,
                    "treatment": disease.treatment,
                    "severity": disease.severity,
                    "match_score": round(match_score, 2),
                    "composite_score": round(composite_score, 2),
                },
                "medicines": [
                    {
                        "id": med.id,
                        "name": med.medicine,
                        "strength": med.strength,
                        "category": med.category.name if med.category else None,
                        "packaging": med.packaging,
                        "expiry_date": med.expiry_date,
                    }
                    for med in disease.medicines.all()
                ]
            })

    # Sort by composite score descending
    results.sort(key=lambda x: x["disease"]["composite_score"], reverse=True)
    return results
