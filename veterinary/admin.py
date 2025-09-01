from django.contrib import admin
from .models.models import MembersMasterCopy, CattleStatusType
from .models.case_models import (
    CaseEntry,
    DiagnosisRoute,
    CaseReceiverLog,
    AnimalDiagnosis,
    DiseaseSeverity,
    AnimalTreatment,
    CasePayment,
    Cattle,
)
from .models.common_models import (
    Species,
    SpeciesBreed,
    AICharge,
    CattleCaseType,
    PaymentMethod,
    TimeSlot,
    CattleCaseStatus,
    OnlinePayment,
)
from .models.stock_models import (
    Location,
    Symptoms,
    Disease,
    MedicineCategory,
    Medicine,
    MedicineStock,
    UserMedicineStock,
)

from django.apps import apps

app_name = "veterinary"


@admin.register(MembersMasterCopy)
class MembersMasterCopyAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "member_code",
        "member_name",
        "mobile_no",
        "company_code",
        "plant_code",
        "mcc_code",
        "bmc_code",
        "is_active",
        "is_default",
        "created_at",
    )
    list_filter = (
        "company_code",
        "plant_code",
        "mcc_code",
        "bmc_code",
        "member_type",
        "gender",
        "caste_category",
        "is_active",
        "is_default",
        "created_at",
    )
    search_fields = (
        "member_code",
        "member_name",
        "member_middle_name",
        "member_surname",
        "mobile_no",
        "application_no",
        "folio_no",
    )
    ordering = ("-created_at",)

    fieldsets = (
        (
            "Identification",
            {"fields": ("member_code", "ex_member_code", "user", "device_id")},
        ),
        (
            "Personal Details",
            {
                "fields": (
                    "member_name",
                    "member_middle_name",
                    "member_surname",
                    "gender",
                    "birth_date",
                    "age",
                    "caste_category",
                )
            },
        ),
        ("Contact Info", {"fields": ("mobile_no",)}),
        (
            "Membership Info",
            {
                "fields": (
                    "member_type",
                    "member_master_relation",
                    "wef_date",
                    "is_active",
                    "is_default",
                )
            },
        ),
        (
            "Organizational Mapping",
            {
                "fields": (
                    "company_code",
                    "plant_code",
                    "mcc_code",
                    "bmc_code",
                    "mpp_code",
                    "member_tr_code",
                )
            },
        ),
        (
            "Application Metadata",
            {
                "fields": (
                    "application_no",
                    "application_date",
                    "folio_no",
                    "created_by",
                    "created_at",
                )
            },
        ),
    )


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = (
        "animal_type",
        "scientific_name",
        "category",
        "is_milk_producing",
        "locale",
        "slug",
    )
    search_fields = ("animal_type", "scientific_name")
    list_filter = ("category", "is_milk_producing")
    prepopulated_fields = {"slug": ("animal_type",)}
    ordering = ("animal_type",)


@admin.register(SpeciesBreed)
class SpeciesBreedAdmin(admin.ModelAdmin):
    list_display = ("breed", "animal_type", "origin_country", "average_milk_yield")
    search_fields = ("breed", "animal_type__animal_type")
    list_filter = ("animal_type",)
    raw_id_fields = ("animal_type",)
    ordering = ("breed",)


@admin.register(CattleStatusType)
class CattleStatusTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "label", "is_active")
    list_filter = ("is_active",)
    search_fields = ("label",)
    ordering = ("label",)


@admin.register(AICharge)
class AIChargeAdmin(admin.ModelAdmin):
    list_display = ("user", "user_role", "amount")
    ordering = ("user_role",)


@admin.register(CattleCaseType)
class CattleCaseTypeAdmin(admin.ModelAdmin):
    list_display = ["case_type"]


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = [
        "start_time",
        "end_time",
        "period",
        "normal_cost",
        "operational_cost",
        "sync",
    ]


@admin.register(CattleCaseStatus)
class CattleCaseStatusAdmin(admin.ModelAdmin):
    list_display = ["status"]


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ("method", "created_at", "updated_at", "is_active", "is_deleted")
    search_fields = ("method",)
    list_filter = ("is_active", "is_deleted")
    ordering = ("method",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(OnlinePayment)
class OnlinePaymentAdmin(admin.ModelAdmin):
    list_display = ("payment_method", "gateway_name", "sync")
    search_fields = ("gateway_name", "payment_method__method")
    list_filter = ("sync",)
    ordering = ("gateway_name",)


@admin.register(CaseEntry)
class CaseEntryAdmin(admin.ModelAdmin):
    list_display = (
        "case_no",
        "cattle",
        "created_by",
        "status",
        "address",
        "sync",
        "created_at",
    )
    list_filter = ("status", "sync", "created_by")
    search_fields = ("case_no", "cattle__tag_id", "created_by__username", "address")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(DiagnosisRoute)
class DiagnosisRouteAdmin(admin.ModelAdmin):
    list_display = ("route", "created_at", "sync")
    search_fields = ("route",)
    list_filter = ("sync",)
    ordering = ("route",)


@admin.register(CaseReceiverLog)
class CaseReceiverLogAdmin(admin.ModelAdmin):
    list_display = (
        "case_entry",
        "assigned_from",
        "assigned_to",
        "transferred_at",
    )
    search_fields = (
        "case_entry__case_no",
        "assigned_from__username",
        "assigned_to__username",
    )
    readonly_fields = ("transferred_at",)
    list_filter = ("assigned_to", "assigned_from")


@admin.register(AnimalDiagnosis)
class AnimalDiagnosisAdmin(admin.ModelAdmin):
    list_display = (
        "case_entry",
        "disease",
        "status",
        "milk_production",
        "case_type",
        "created_at",
    )
    search_fields = (
        "case_entry__case_no",
        "disease__name",
        "milk_production",
    )
    list_filter = ("status", "case_type", "disease")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(AnimalTreatment)
class AnimalTreatmentAdmin(admin.ModelAdmin):
    list_display = (
        "case_treatment",
        "treatment_by",
        "medicine",
        "route",
        "otp_verified",
        "created_at",
    )
    list_filter = ("otp_verified", "route", "medicine", "treatment_by")
    search_fields = (
        "case_treatment__case_no",
        "treatment_by__username",
        "medicine__name",
        "route__route",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(CasePayment)
class CasePaymentAdmin(admin.ModelAdmin):
    list_display = (
        "case_entry",
        "payment_method",
        "amount",
        "payment_status",
        "payment_date",
        "is_reconciled",
        "is_collected",
    )
    list_filter = (
        "payment_method",
        "payment_status",
        "is_reconciled",
        "is_collected",
    )
    search_fields = (
        "case_entry__case_no",
        "transaction_id",
        "collected_by__username",
        "payment_method__method",
    )
    readonly_fields = ("payment_date",)
    ordering = ("-payment_date",)


@admin.register(Cattle)
class CattleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "owner",
        "breed",
        "gender",
        "age",
        "is_alive",
        "current_status",
    )
    list_filter = (
        "gender",
        "is_alive",
        "breed",
        "current_status",
    )
    search_fields = (
        "name",
        "owner__name",
        "current_status__label",
    )
    autocomplete_fields = ("owner", "mother", "father", "current_status")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "type",
        "district",
        "state",
        "latitude",
        "longitude",
        "is_active",
    )
    list_filter = ("type", "state", "district", "is_active")
    search_fields = ("name", "code", "district", "state")
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Symptoms)
class SymptomsAdmin(admin.ModelAdmin):
    list_display = ("symptom", "description", "is_active")
    search_fields = ("symptom", "description")
    list_filter = ("is_active",)
    ordering = ("symptom",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ("disease", "severity", "is_active")
    search_fields = ("disease", "description", "treatment")
    list_filter = ("severity", "is_active")
    filter_horizontal = ("symptoms",)
    ordering = ("disease",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(MedicineCategory)
class MedicineCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "category",
        "medicine_form",
        "unit_of_quantity",
        "parent_category",
        "is_active",
    )
    search_fields = ("category", "unit_of_quantity", "parent_category__category")
    list_filter = ("medicine_form", "is_active")
    ordering = ("category",)
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("parent_category",)


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = (
        "medicine",
        "category",
        "strength",
        "packaging",
        "expiry_date",
        "is_active",
    )
    search_fields = ("medicine", "strength", "packaging")
    list_filter = ("category", "expiry_date", "is_active")
    filter_horizontal = ("diseases",)
    autocomplete_fields = ("category",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("medicine",)


@admin.register(MedicineStock)
class MedicineStockAdmin(admin.ModelAdmin):
    list_display = (
        "medicine",
        "batch_number",
        "total_quantity",
        "expiry_date",
        "last_updated",
        "is_active",
    )
    search_fields = ("medicine__medicine", "batch_number")
    list_filter = ("expiry_date", "is_active")
    autocomplete_fields = ("medicine",)
    readonly_fields = ("created_at", "updated_at", "last_updated")
    ordering = ("-last_updated",)


@admin.register(UserMedicineStock)
class UserMedicineStockAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "medicine_stock",
        "allocated_quantity",
        "used_quantity",
        "threshold_quantity",
        "min_threshold",
        "allocation_date",
        "sync",
        "allocated_by",
        "is_active",
    )
    search_fields = (
        "user__username",
        "medicine_stock__medicine__medicine",
        "allocated_by__username",
    )
    list_filter = ("sync", "allocation_date", "is_active")
    autocomplete_fields = ("user", "medicine_stock", "allocated_by")
    readonly_fields = ("created_at", "updated_at", "allocation_date")
    ordering = ("-allocation_date",)

from .models.models import FarmerMeeting


@admin.register(FarmerMeeting)
class FarmerMeetingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "mcc_code",
        "mcc_name",
        "mpp_code",
        "mpp_name",
        "total_participants",
        "created_at",
        "updated_at",
        "updated_by",
    )
    list_filter = ("mcc_code", "mpp_code", "created_at")
    search_fields = ("mcc_code", "mcc_name", "mpp_code", "mpp_name", "notes")
    readonly_fields = ("created_at", "updated_at", "updated_by")
    filter_horizontal = ("members",)  # better UX for M2M selection

    fieldsets = (
        (None, {
            "fields": (
                "mcc_code",
                "mcc_ex_code",
                "mcc_name",
                "mpp_code",
                "mpp_ex_code",
                "mpp_name",
                "total_participants",
                "members",
                "image",
                "notes",
            )
        }),
        ("Audit Info", {
            "fields": ("created_at", "updated_at", "updated_by"),
        }),
    )
