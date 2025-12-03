from django.core.management.base import BaseCommand
from django.utils import timezone

from veterinary.models.common_models import TreatmentCostConfiguration


class Command(BaseCommand):
    help = "Create default cost configurations for English and Hindi locales with localized descriptions"

    def handle(self, *args, **options):
        default_configs = [
            # Member - Before 10:00 AM
            {
                "membership_type": "member",
                "time_slot": "before_10am",
                "animal_tag_type": "tagged",
                "treatment_type": "normal",
                "cost_amount": 300,
            },
            {
                "membership_type": "member",
                "time_slot": "before_10am",
                "animal_tag_type": "non_tagged",
                "treatment_type": "normal",
                "cost_amount": 400,
            },
            {
                "membership_type": "member",
                "time_slot": "before_10am",
                "animal_tag_type": "tagged",
                "treatment_type": "emergency",
                "cost_amount": 1200,
            },
            {
                "membership_type": "member",
                "time_slot": "before_10am",
                "animal_tag_type": "non_tagged",
                "treatment_type": "emergency",
                "cost_amount": 800,
            },
            # Member - After 10:00 AM
            {
                "membership_type": "member",
                "time_slot": "after_10am",
                "animal_tag_type": "tagged",
                "treatment_type": "normal",
                "cost_amount": 500,
            },
            {
                "membership_type": "member",
                "time_slot": "after_10am",
                "animal_tag_type": "non_tagged",
                "treatment_type": "normal",
                "cost_amount": 600,
            },
            {
                "membership_type": "member",
                "time_slot": "after_10am",
                "animal_tag_type": "tagged",
                "treatment_type": "emergency",
                "cost_amount": 1500,
            },
            {
                "membership_type": "member",
                "time_slot": "after_10am",
                "animal_tag_type": "non_tagged",
                "treatment_type": "emergency",
                "cost_amount": 1000,
            },
            # Non-Member - Before 10:00 AM
            {
                "membership_type": "non_member",
                "time_slot": "before_10am",
                "animal_tag_type": "tagged",
                "treatment_type": "normal",
                "cost_amount": 500,
            },
            {
                "membership_type": "non_member",
                "time_slot": "before_10am",
                "animal_tag_type": "non_tagged",
                "treatment_type": "normal",
                "cost_amount": 600,
            },
            {
                "membership_type": "non_member",
                "time_slot": "before_10am",
                "animal_tag_type": "tagged",
                "treatment_type": "emergency",
                "cost_amount": 1500,
            },
            {
                "membership_type": "non_member",
                "time_slot": "before_10am",
                "animal_tag_type": "non_tagged",
                "treatment_type": "emergency",
                "cost_amount": 1000,
            },
            # Non-Member - After 10:00 AM
            {
                "membership_type": "non_member",
                "time_slot": "after_10am",
                "animal_tag_type": "tagged",
                "treatment_type": "normal",
                "cost_amount": 600,
            },
            {
                "membership_type": "non_member",
                "time_slot": "after_10am",
                "animal_tag_type": "non_tagged",
                "treatment_type": "normal",
                "cost_amount": 700,
            },
            {
                "membership_type": "non_member",
                "time_slot": "after_10am",
                "animal_tag_type": "tagged",
                "treatment_type": "emergency",
                "cost_amount": 2000,
            },
            {
                "membership_type": "non_member",
                "time_slot": "after_10am",
                "animal_tag_type": "non_tagged",
                "treatment_type": "emergency",
                "cost_amount": 1200,
            },
        ]

        # Simple Hindi translations
        translations = {
            "member": "सदस्य",
            "non_member": "गैर-सदस्य",
            "before_10am": "सुबह 10 बजे से पहले",
            "after_10am": "सुबह 10 बजे के बाद",
            "tagged": "टैग किया हुआ",
            "non_tagged": "बिना टैग का",
            "normal": "सामान्य",
            "emergency": "आपातकालीन",
        }

        today = timezone.now().date()
        locales = ["en", "hi"]
        created_count = 0

        for locale in locales:
            for config_data in default_configs:
                config_data["effective_from"] = today
                config_data["is_active"] = True
                config_data["locale"] = locale

                # Localized description
                if locale == "en":
                    desc = (
                        f"Default configuration for {config_data['membership_type']} "
                        f"{config_data['time_slot']} {config_data['treatment_type']}"
                    )
                else:  # Hindi version
                    desc = (
                        f"डिफ़ॉल्ट विन्यास ({translations.get(config_data['membership_type'])}, "
                        f"{translations.get(config_data['time_slot'])}, "
                        f"{translations.get(config_data['treatment_type'])})"
                    )

                config_data["description"] = desc

                obj, created = TreatmentCostConfiguration.objects.get_or_create(
                    membership_type=config_data["membership_type"],
                    time_slot=config_data["time_slot"],
                    animal_tag_type=config_data["animal_tag_type"],
                    treatment_type=config_data["treatment_type"],
                    effective_from=config_data["effective_from"],
                    locale=config_data["locale"],
                    defaults=config_data,
                )

                if created:
                    created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Default bilingual cost configurations created successfully ({created_count} new entries)."
            )
        )
