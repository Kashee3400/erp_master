from rest_framework import serializers


from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist


class MilkBillPaymentCreateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    user_identifier = serializers.CharField(max_length=255)
    transaction_type = serializers.CharField(max_length=255)
    redirect_url = serializers.URLField()

    udf1 = serializers.CharField(required=False, allow_blank=True)
    udf2 = serializers.CharField(required=False, allow_blank=True)
    udf3 = serializers.CharField(required=False, allow_blank=True)

    metadata = serializers.JSONField(required=False)

    # Generic relation support
    related_model = serializers.CharField(required=False, allow_blank=True)
    related_object_id = serializers.CharField(required=False, allow_blank=True)

    # ---------------------------------------------------
    # FIELD-LEVEL VALIDATION
    # ---------------------------------------------------

    def validate_amount(self, value):
        """Amount must be greater than zero."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate_user_identifier(self, value):
        """Clean and normalize user identifier."""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("User identifier cannot be empty.")
        return value

    def validate_metadata(self, value):
        """Ensure metadata is a dict."""
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise serializers.ValidationError("Metadata must be a valid JSON object.")
        return value

    # ---------------------------------------------------
    # CROSS-FIELD VALIDATION
    # ---------------------------------------------------

    def validate(self, attrs):
        related_model = attrs.get("related_model")
        related_object_id = attrs.get("related_object_id")

        # If one is provided, both must be provided
        if bool(related_model) != bool(related_object_id):
            raise serializers.ValidationError(
                "Both 'related_model' and 'related_object_id' must be provided together."
            )

        # Validate related model + object
        if related_model and related_object_id:
            model_name = related_model.lower().strip()

            # Validate model
            try:
                content_type = ContentType.objects.get(model=model_name)
            except ContentType.DoesNotExist:
                raise serializers.ValidationError(
                    {"related_model": f"Invalid model '{related_model}'."}
                )

            model_class = content_type.model_class()

            # Validate object instance
            try:
                model_class.objects.get(pk=related_object_id)
            except (ObjectDoesNotExist, ValueError):
                raise serializers.ValidationError(
                    {
                        "related_object_id": f"Object with ID '{related_object_id}' not found for model '{model_name}'."
                    }
                )

        return attrs
