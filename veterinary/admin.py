from django.contrib import admin
from .models.models import (
    MembersMasterCopy,
    CattleStatusType,
    NonMember,
    NonMemberCattle,
)
from import_export.admin import ImportExportModelAdmin
from .models.case_models import (
    CaseEntry,
    DiagnosisRoute,
    CaseReceiverLog,
    AnimalDiagnosis,
    AnimalTreatment,
    CasePayment,
    Cattle,
    TreatmentCostConfiguration,
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

from .resources.cattle_resources import CombinedCattleResource
from django.utils.html import format_html
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

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
    search_fields = ("member_code", "mobile_no", "member_tr_code")
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
    list_display = ("id","breed", "animal_type", "origin_country", "average_milk_yield")
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
class CattleAdmin(ImportExportModelAdmin):
    resource_class = CombinedCattleResource
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
        (
            None,
            {
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
            },
        ),
        (
            "Audit Info",
            {
                "fields": ("created_at", "updated_at", "updated_by"),
            },
        ),
    )


from .models.excel_model import ExcelUploadSession


@admin.register(ExcelUploadSession)
class ExcelUploadSessionAdmin(admin.ModelAdmin):
    list_display = ["filename", "uploaded_at", "processed", "status", "total_rows"]
    list_filter = ["processed", "uploaded_at"]
    search_fields = ["filename"]
    readonly_fields = ["id", "uploaded_at", "sheets_data"]

    def get_queryset(self, request):
        return super().get_queryset(request).order_by("-uploaded_at")


@admin.register(TreatmentCostConfiguration)
class TreatmentCostConfigurationAdmin(admin.ModelAdmin):
    """
    Admin configuration for TreatmentCostConfiguration
    Enables easy management and tracking of cost configurations
    """

    # Display columns in admin list view
    list_display = (
        "membership_type",
        "time_slot",
        "animal_tag_type",
        "treatment_type",
        "formatted_cost",
        "effective_from",
        "effective_to",
        "is_active",
        "created_by",
    )

    # Filters in right sidebar
    list_filter = (
        "membership_type",
        "time_slot",
        "animal_tag_type",
        "treatment_type",
        "is_active",
        ("effective_from", admin.DateFieldListFilter),
        ("effective_to", admin.DateFieldListFilter),
    )

    # Fields searchable by admin
    search_fields = (
        "membership_type",
        "time_slot",
        "animal_tag_type",
        "treatment_type",
        "description",
    )

    # Ordering default
    ordering = ("-effective_from", "-id")

    # Fields grouped for form layout
    fieldsets = (
        (
            _("Configuration Details"),
            {
                "fields": (
                    "membership_type",
                    "time_slot",
                    "animal_tag_type",
                    "treatment_type",
                    "cost_amount",
                )
            },
        ),
        (
            _("Effectivity Period"),
            {
                "fields": ("effective_from", "effective_to", "is_active"),
            },
        ),
        (
            _("Additional Information"),
            {
                "fields": ("description", "created_by"),
            },
        ),
    )

    # Read-only fields
    readonly_fields = ("created_by",)

    # Custom method to format cost in ₹ symbol
    def formatted_cost(self, obj):
        return format_html("<b>₹{}</b>", obj.cost_amount)

    formatted_cost.short_description = _("Cost Amount")

    # Automatically set created_by to logged-in user
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        obj.save()

    # Highlight inactive records
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("created_by")

    # Optional: custom color display in list view
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["title"] = _("Treatment Cost Configurations")
        return super().changelist_view(request, extra_context=extra_context)


class NonMemberCattleInline(admin.TabularInline):
    """Inline admin for cattle owned by non-members"""

    model = NonMemberCattle
    extra = 1
    fields = (
        "tag_number",
        "breed",
        "age_years",
        "age_months",
        "weight_kg",
        "is_pregnant",
        "pregnancy_months",
        "is_active",
    )
    readonly_fields = ("created_at", "updated_at")
    classes = ["collapse"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("breed")


from django.db.models import Count, Q
from django.utils.safestring import mark_safe


class NonMemberCattleInline(admin.TabularInline):
    """Inline admin for cattle owned by non-members"""

    model = NonMemberCattle
    extra = 1
    fields = (
        "tag_number",
        "breed",
        "age_years",
        "age_months",
        "weight_kg",
        "is_pregnant",
        "pregnancy_months",
        "is_active",
    )
    readonly_fields = ("created_at", "updated_at")
    classes = ["collapse"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("breed")


@admin.register(NonMember)
class NonMemberAdmin(admin.ModelAdmin):
    """Admin configuration for NonMember model"""

    # Jazzmin customization
    list_display_links = ("non_member_id", "name")

    list_display = (
        "non_member_id",
        "name",
        "mobile_no",
        "location_info",
        "cattle_count",
        "visit_count",
        "sync_status",
        "created_at",
    )

    list_filter = ("sync", "created_at", "updated_at", "mcc_code", "mpp_code")

    search_fields = (
        "non_member_id",
        "name",
        "mobile_no",
        "mcc_code",
        "mpp_code",
        "address",
    )

    readonly_fields = (
        "non_member_id",
        "created_at",
        "updated_at",
        "created_by",
        "visit_count",
        "member_card",
    )

    fieldsets = (
        (
            _("👤 Basic Information"),
            {
                "fields": ("member_card", "non_member_id", "name", "mobile_no"),
                "description": "Core details of the non-member",
            },
        ),
        (
            _("📍 Location Details"),
            {
                "fields": (
                    ("mcc_code", "mcc_name"),
                    ("mpp_code", "mpp_name"),
                    "address",
                ),
                "description": "Milk collection center and procurement point information",
            },
        ),
        (
            _("⚙️ System Information"),
            {"fields": ("created_by", "visit_count", "sync"), "classes": ("collapse",)},
        ),
        (
            _("🕒 Timestamps"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    inlines = [NonMemberCattleInline]

    list_per_page = 25
    date_hierarchy = "created_at"
    save_on_top = True

    actions = ["mark_as_synced", "mark_as_unsynced", "reset_visit_count"]

    # Jazzmin specific settings
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["title"] = "🧑‍🌾 Non-Members Management"
        return super().changelist_view(request, extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["title"] = "📝 Edit Non-Member"
        return super().change_view(request, object_id, form_url, extra_context)

    def add_view(self, request, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["title"] = "➕ Add New Non-Member"
        return super().add_view(request, form_url, extra_context)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("created_by").annotate(total_cattle=Count("cattle"))

    def member_card(self, obj):
        """Display a beautiful member card"""
        if not obj.pk:
            return "-"

        cattle_count = obj.cattle.count()
        sync_badge = "🟢 Synced" if obj.sync else "🟠 Pending"

        card_html = f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 20px;
            color: white;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            max-width: 400px;
            margin: 20px 0;
        ">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                <div>
                    <div style="font-size: 11px; opacity: 0.8; text-transform: uppercase; letter-spacing: 1px;">Non-Member ID</div>
                    <div style="font-size: 18px; font-weight: bold; margin-top: 5px;">{obj.non_member_id}</div>
                </div>
                <div style="background: rgba(255,255,255,0.2); padding: 5px 12px; border-radius: 20px; font-size: 11px;">
                    {sync_badge}
                </div>
            </div>
            
            <div style="margin: 15px 0;">
                <div style="font-size: 24px; font-weight: bold; margin-bottom: 5px;">👤 {obj.name}</div>
                <div style="font-size: 14px; opacity: 0.9;">📱 {obj.mobile_no}</div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.2);">
                <div>
                    <div style="font-size: 11px; opacity: 0.8;">Cattle Count</div>
                    <div style="font-size: 20px; font-weight: bold;">🐄 {cattle_count}</div>
                </div>
                <div>
                    <div style="font-size: 11px; opacity: 0.8;">Total Visits</div>
                    <div style="font-size: 20px; font-weight: bold;">🔄 {obj.visit_count}</div>
                </div>
            </div>
            
            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.2); font-size: 12px; opacity: 0.8;">
                📍 {obj.mcc_name or obj.mcc_code or 'N/A'} • {obj.mpp_name or obj.mpp_code or 'N/A'}
            </div>
        </div>
        """
        return mark_safe(card_html)

    member_card.short_description = _("Member Card")

    def location_info(self, obj):
        """Display location with nice formatting"""
        mcc = obj.mcc_name or obj.mcc_code or "-"
        mpp = obj.mpp_name or obj.mpp_code or "-"
        return format_html(
            '<div style="line-height: 1.6;">'
            '<span style="background: #e3f2fd; color: #1976d2; padding: 2px 8px; border-radius: 12px; font-size: 11px; margin-right: 5px;">MCC: {}</span><br/>'
            '<span style="background: #f3e5f5; color: #7b1fa2; padding: 2px 8px; border-radius: 12px; font-size: 11px; margin-top: 4px; display: inline-block;">MPP: {}</span>'
            "</div>",
            mcc,
            mpp,
        )

    location_info.short_description = _("📍 Location")

    def cattle_count(self, obj):
        """Display count of cattle owned by non-member"""
        count = getattr(obj, "total_cattle", obj.cattle.count())
        if count > 0:
            return format_html(
                '<div style="text-align: center;">'
                '<span style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 6px 14px; border-radius: 20px; font-weight: bold; font-size: 14px; box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);">'
                "🐄 {}"
                "</span>"
                "</div>",
                count,
            )
        return format_html(
            '<span style="background: #f5f5f5; color: #999; padding: 6px 14px; border-radius: 20px; font-size: 13px;">No cattle</span>'
        )

    cattle_count.short_description = _("🐄 Cattle")
    cattle_count.admin_order_field = "total_cattle"

    def sync_status(self, obj):
        """Display sync status with visual indicator"""
        if obj.sync:
            return format_html(
                '<span style="background: #4caf50; color: white; padding: 6px 12px; border-radius: 15px; font-size: 12px; font-weight: 600;">'
                "✓ Synced"
                "</span>"
            )
        return format_html(
            '<span style="background: #ff9800; color: white; padding: 6px 12px; border-radius: 15px; font-size: 12px; font-weight: 600;">'
            "⏳ Pending"
            "</span>"
        )

    sync_status.short_description = _("🔄 Sync Status")
    sync_status.admin_order_field = "sync"

    def save_model(self, request, obj, form, change):
        """Auto-assign created_by on new record"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    @admin.action(description=_("✅ Mark selected as synced"))
    def mark_as_synced(self, request, queryset):
        updated = queryset.update(sync=True)
        self.message_user(
            request, _(f"✅ {updated} non-member(s) marked as synced."), level="success"
        )

    @admin.action(description=_("⏳ Mark selected as unsynced"))
    def mark_as_unsynced(self, request, queryset):
        updated = queryset.update(sync=False)
        self.message_user(
            request,
            _(f"⏳ {updated} non-member(s) marked as unsynced."),
            level="warning",
        )

    @admin.action(description=_("🔄 Reset visit count to zero"))
    def reset_visit_count(self, request, queryset):
        updated = queryset.update(visit_count=0)
        self.message_user(
            request,
            _(f"🔄 Visit count reset for {updated} non-member(s)."),
            level="info",
        )


@admin.register(NonMemberCattle)
class NonMemberCattleAdmin(admin.ModelAdmin):
    """Admin configuration for NonMemberCattle model"""

    list_display_links = ("tag_number",)

    list_display = (
        "tag_number",
        "non_member_info",
        "breed",
        "age_display",
        "weight_display",
        "pregnancy_status",
        "active_status",
        "sync_status",
    )

    list_filter = (
        "is_active",
        "is_pregnant",
        "sync",
        "breed",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "tag_number",
        "non_member__name",
        "non_member__mobile_no",
        "non_member__non_member_id",
        "breed__name",
    )

    readonly_fields = ("created_at", "updated_at", "cattle_profile_card")

    autocomplete_fields = ["non_member", "breed"]

    fieldsets = (
        (
            _("🐄 Cattle Profile"),
            {
                "fields": ("cattle_profile_card",),
                "description": "Overview of the cattle information",
            },
        ),
        (_("👤 Owner Information"), {"fields": ("non_member",)}),
        (
            _("📋 Cattle Details"),
            {
                "fields": (
                    "tag_number",
                    "breed",
                    ("age_years", "age_months"),
                    "weight_kg",
                )
            },
        ),
        (
            _("🤰 Pregnancy Information"),
            {"fields": ("is_pregnant", "pregnancy_months"), "classes": ("collapse",)},
        ),
        (
            _("📝 Additional Information"),
            {
                "fields": ("additional_details", "is_active", "sync"),
                "classes": ("collapse",),
            },
        ),
        (
            _("🕒 Timestamps"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    list_per_page = 25
    date_hierarchy = "created_at"
    save_on_top = True

    actions = [
        "mark_as_synced",
        "mark_as_unsynced",
        "mark_as_active",
        "mark_as_inactive",
    ]

    # Jazzmin specific settings
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["title"] = "🐄 Non-Member Cattle Management"
        return super().changelist_view(request, extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["title"] = "📝 Edit Cattle"
        return super().change_view(request, object_id, form_url, extra_context)

    def add_view(self, request, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["title"] = "➕ Add New Cattle"
        return super().add_view(request, form_url, extra_context)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("non_member", "breed")

    def cattle_profile_card(self, obj):
        """Display a beautiful cattle profile card"""
        if not obj.pk:
            return "-"

        # Calculate age display
        age_str = ""
        if obj.age_years or obj.age_months:
            parts = []
            if obj.age_years:
                parts.append(f"{obj.age_years} years")
            if obj.age_months:
                parts.append(f"{obj.age_months} months")
            age_str = " ".join(parts)
        else:
            age_str = "Unknown"

        # Pregnancy info
        pregnancy_html = ""
        if obj.is_pregnant:
            pregnancy_html = f"""
            <div style="background: #fce4ec; padding: 12px; border-radius: 10px; margin-top: 15px; border-left: 4px solid #e91e63;">
                <div style="color: #c2185b; font-weight: bold; margin-bottom: 5px;">🤰 Pregnant</div>
                <div style="color: #880e4f; font-size: 13px;">Duration: {obj.pregnancy_months or '?'} months</div>
            </div>
            """

        # Status badge
        status_color = "#4caf50" if obj.is_active else "#f44336"
        status_text = "Active" if obj.is_active else "Inactive"

        card_html = f"""
        <div style="
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            border-radius: 15px;
            padding: 20px;
            color: #333;
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
            max-width: 500px;
            margin: 20px 0;
        ">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                <div>
                    <div style="font-size: 11px; opacity: 0.7; text-transform: uppercase; letter-spacing: 1px; color: #fff;">Tag Number</div>
                    <div style="font-size: 20px; font-weight: bold; margin-top: 5px; color: #fff;">🏷️ {obj.tag_number}</div>
                </div>
                <div style="background: {status_color}; color: white; padding: 5px 12px; border-radius: 20px; font-size: 11px; font-weight: 600;">
                    {status_text}
                </div>
            </div>
            
            <div style="background: white; border-radius: 12px; padding: 15px; margin: 15px 0;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div>
                        <div style="font-size: 11px; color: #999; text-transform: uppercase; margin-bottom: 5px;">Breed</div>
                        <div style="font-size: 16px; font-weight: bold; color: #333;">🐮 {obj.breed.name if obj.breed else 'Unknown'}</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: #999; text-transform: uppercase; margin-bottom: 5px;">Age</div>
                        <div style="font-size: 16px; font-weight: bold; color: #333;">⏰ {age_str}</div>
                    </div>
                </div>
                
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee;">
                    <div style="font-size: 11px; color: #999; text-transform: uppercase; margin-bottom: 5px;">Weight</div>
                    <div style="font-size: 18px; font-weight: bold; color: #333;">⚖️ {obj.weight_kg or 'Not recorded'} {'kg' if obj.weight_kg else ''}</div>
                </div>
            </div>
            
            {pregnancy_html}
            
            <div style="background: rgba(255,255,255,0.3); border-radius: 10px; padding: 12px; margin-top: 15px;">
                <div style="font-size: 11px; color: rgba(0,0,0,0.6); margin-bottom: 5px;">Owner</div>
                <div style="font-size: 14px; font-weight: 600; color: #333;">👤 {obj.non_member.name}</div>
                <div style="font-size: 12px; color: rgba(0,0,0,0.7); margin-top: 3px;">📱 {obj.non_member.mobile_no}</div>
            </div>
        </div>
        """
        return mark_safe(card_html)

    cattle_profile_card.short_description = _("Cattle Profile")

    def non_member_info(self, obj):
        """Display non-member name and mobile"""
        return format_html(
            '<div style="line-height: 1.6;">'
            '<div style="font-weight: 600; color: #333; margin-bottom: 3px;">👤 {}</div>'
            '<div style="font-size: 12px; color: #666;">📱 {}</div>'
            "</div>",
            obj.non_member.name,
            obj.non_member.mobile_no,
        )

    non_member_info.short_description = _("👤 Owner")
    non_member_info.admin_order_field = "non_member__name"

    def age_display(self, obj):
        """Display formatted age"""
        if obj.age_years or obj.age_months:
            years = obj.age_years or 0
            months = obj.age_months or 0
            parts = []
            if years:
                parts.append(f"{years}y")
            if months:
                parts.append(f"{months}m")
            age_text = " ".join(parts)
            return format_html(
                '<span style="background: #e8f5e9; color: #2e7d32; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;">⏰ {}</span>',
                age_text,
            )
        return format_html('<span style="color: #999;">-</span>')

    age_display.short_description = _("⏰ Age")

    def weight_display(self, obj):
        """Display weight with nice formatting"""
        if obj.weight_kg:
            return format_html(
                '<span style="background: #fff3e0; color: #e65100; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;">⚖️ {} kg</span>',
                obj.weight_kg,
            )
        return format_html('<span style="color: #999;">-</span>')

    weight_display.short_description = _("⚖️ Weight")

    def pregnancy_status(self, obj):
        """Display pregnancy status with visual indicator"""
        if obj.is_pregnant:
            months = obj.pregnancy_months or "?"
            return format_html(
                '<span style="background: #fce4ec; color: #c2185b; padding: 6px 12px; border-radius: 15px; font-size: 12px; font-weight: 600;">'
                "🤰 {} months"
                "</span>",
                months,
            )
        return format_html('<span style="color: #ccc; font-size: 12px;">-</span>')

    pregnancy_status.short_description = _("🤰 Pregnancy")

    def active_status(self, obj):
        """Display active status with visual indicator"""
        if obj.is_active:
            return format_html(
                '<span style="background: #4caf50; color: white; padding: 6px 12px; border-radius: 15px; font-size: 12px; font-weight: 600;">'
                "✓ Active"
                "</span>"
            )
        return format_html(
            '<span style="background: #f44336; color: white; padding: 6px 12px; border-radius: 15px; font-size: 12px; font-weight: 600;">'
            "✗ Inactive"
            "</span>"
        )

    active_status.short_description = _("📊 Status")
    active_status.admin_order_field = "is_active"

    def sync_status(self, obj):
        """Display sync status with visual indicator"""
        if obj.sync:
            return format_html(
                '<span style="font-size: 18px;" title="Synced">✅</span>'
            )
        return format_html('<span style="font-size: 18px;" title="Pending">⏳</span>')

    sync_status.short_description = _("🔄 Sync")
    sync_status.admin_order_field = "sync"

    @admin.action(description=_("✅ Mark selected as synced"))
    def mark_as_synced(self, request, queryset):
        updated = queryset.update(sync=True)
        self.message_user(
            request,
            _(f"✅ {updated} cattle record(s) marked as synced."),
            level="success",
        )

    @admin.action(description=_("⏳ Mark selected as unsynced"))
    def mark_as_unsynced(self, request, queryset):
        updated = queryset.update(sync=False)
        self.message_user(
            request,
            _(f"⏳ {updated} cattle record(s) marked as unsynced."),
            level="warning",
        )

    @admin.action(description=_("✓ Mark selected as active"))
    def mark_as_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            _(f"✅ {updated} cattle record(s) marked as active."),
            level="success",
        )

    @admin.action(description=_("✗ Mark selected as inactive"))
    def mark_as_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            _(f"⚠️ {updated} cattle record(s) marked as inactive."),
            level="warning",
        )
