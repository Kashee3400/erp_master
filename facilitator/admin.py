from django.contrib import admin
from .models.facilitator_model import AssignedMppToFacilitator, ApiKey
from .models.vcg_model import (
    VCGMeeting,
    VCGroup,
    ZeroDaysPourerReason,
    ZeroDaysPouringReport,
    MemberComplaintReason,
    MemberComplaintReport,
)
from django.urls import reverse
from .models.member_update_model import (
    UpdateRequest,
    UpdateRequestData,
    UpdateRequestDocument,
    UpdateRequestHistory,
    RequestStatus,
    ChangeType,
)

from .models.user_profile_model import UserProfile
from import_export.admin import ImportExportModelAdmin, ExportActionModelAdmin
from .resources import FacilitatorResource, VCGroupResource, UpdateRequestResource
from .forms import base_form
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.utils.timezone import now
from django.http import HttpResponse
from .choices import *
import csv
from django.shortcuts import render, redirect
from django.contrib import admin
from django.contrib import messages
from django.urls import path
from .forms.base_form import ReasonForm


class AssignedMppToFacilitatorAdmin(ImportExportModelAdmin):
    # form = base_form.AssignedMppToFacilitatorForm
    resource_class = FacilitatorResource
    list_display = (
        "facilitator_name",
        "mpp_code",
        "mpp_ex_code",
        "mpp_name",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "mpp_code",
        "mpp_ex_code",
        "mpp_name",
    )
    list_filter = (
        "sahayak",
        "mpp_type",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")

    save_as = True
    save_on_top = True
    actions_on_bottom = True

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["custom_message"] = "🚀 Assign MPPs carefully!"
        return super().changeform_view(request, object_id, form_url, extra_context)

    @admin.display(description="Facilitator")
    def facilitator_name(self, obj):
        if obj.sahayak:
            full_name = f"{obj.sahayak.first_name} {obj.sahayak.last_name}".strip()
            if full_name.strip():
                return full_name
            if obj.sahayak.username:
                return obj.sahayak.username
        return "No Facilitator Assigned"


admin.site.register(AssignedMppToFacilitator, AssignedMppToFacilitatorAdmin)


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = (
        "key_short",
        "user",
        "is_active",
        "is_revoked",
        "created_at",
        "expires_at",
        "usage_count",
        "last_used_at",
    )
    list_filter = ("is_active", "is_revoked", "created_at", "expires_at")
    search_fields = ("key", "user__username", "description", "permissions")
    readonly_fields = (
        "key",
        "created_at",
        "last_used_at",
        "usage_count",
        "failed_attempts",
    )
    autocomplete_fields = ("user", "created_by", "last_used_by", "revoked_by")
    actions = ["revoke_api_keys", "activate_api_keys", "reset_usage_count"]

    fieldsets = (
        ("Basic Info", {"fields": ("key", "user", "description", "permissions")}),
        (
            "Validity & State",
            {
                "fields": (
                    "is_active",
                    "valid_from",
                    "expires_at",
                    "is_revoked",
                    "revoked_at",
                    "revoked_by",
                )
            },
        ),
        ("Security Restrictions", {"fields": ("allowed_ips", "allowed_urls")}),
        (
            "Usage Limits",
            {
                "fields": (
                    "usage_count",
                    "max_usage_limit",
                    "requests_per_day",
                    "requests_per_hour",
                    "usage_reset_time",
                )
            },
        ),
        (
            "Audit",
            {
                "fields": (
                    "created_at",
                    "created_by",
                    "last_used_at",
                    "last_used_by",
                    "failed_attempts",
                )
            },
        ),
    )

    def key_short(self, obj):
        return format_html("<code>{}</code>", obj.key[:8] + "…")

    key_short.short_description = "API Key"

    @admin.action(description="Revoke selected API keys")
    def revoke_api_keys(self, request, queryset):
        queryset.update(is_revoked=True, revoked_at=now(), revoked_by=request.user)

    @admin.action(description="Activate selected API keys")
    def activate_api_keys(self, request, queryset):
        queryset.update(
            is_active=True, is_revoked=False, revoked_at=None, revoked_by=None
        )

    @admin.action(description="Reset usage count to zero")
    def reset_usage_count(self, request, queryset):
        queryset.update(usage_count=0, failed_attempts=0)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user", "created_by", "last_used_by", "revoked_by")


@admin.register(VCGMeeting)
class VCGMeetingAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "mpp_name",
        "mpp_code",
        "status",
        "is_deleted",
        "started_at",
        "completed_at",
        "synced",
    )
    list_filter = ("status", "synced", "started_at")
    search_fields = ("mpp_name", "mpp_code", "mpp_ex_code")
    ordering = ("-started_at",)

    # Read-only fields
    readonly_fields = ("meeting_id", "started_at", "completed_at")

    # Fieldsets for structured display in admin
    fieldsets = (
        (
            _("Meeting Details"),
            {
                "fields": (
                    "meeting_id",
                    "user",
                    "mpp_name",
                    "mpp_code",
                    "mpp_ex_code",
                    "status",
                    "is_deleted",
                )
            },
        ),
        (
            _("Location Details"),
            {
                "fields": ("lat", "lon"),
                "classes": ("collapse",),  # Collapsible section
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": ("started_at", "completed_at"),
            },
        ),
        (
            _("Sync Information"),
            {
                "fields": ("synced",),
            },
        ),
    )


# Admin Configuration
class VCGroupAdmin(ImportExportModelAdmin):
    resource_class = VCGroupResource
    list_display = ("member_name", "mpp", "whatsapp_num", "member_code", "created_at")
    search_fields = ("member_name", "whatsapp_num", "member_code", "mpp__mpp_code")
    list_filter = ("mpp", "created_at", "updated_at")


admin.site.register(VCGroup, VCGroupAdmin)


class ZeroDaysReasonAdmin(ImportExportModelAdmin):
    list_display = ("id", "reason", "created_at")
    search_fields = ("reason",)
    list_filter = ("created_at", "updated_at")
    date_hierarchy = "created_at"


admin.site.register(ZeroDaysPourerReason, ZeroDaysReasonAdmin)


class MemberComplaintReasonAdmin(ImportExportModelAdmin):
    list_display = ("id", "reason", "created_at")
    search_fields = ("reason",)
    list_filter = ("created_at", "updated_at")
    date_hierarchy = "created_at"


admin.site.register(MemberComplaintReason, MemberComplaintReasonAdmin)


@admin.register(ZeroDaysPouringReport)
class ZeroDaysPouringReportAdmin(admin.ModelAdmin):
    list_display = ("member_code", "member_name", "reason", "meeting")
    search_fields = ("member_code", "member_name")
    list_filter = ("reason", "meeting")
    date_hierarchy = "meeting__started_at"

    fieldsets = (
        ("Member Info", {"fields": ("member_code", "member_ex_code", "member_name")}),
        ("Details", {"fields": ("reason", "meeting")}),
    )


@admin.register(MemberComplaintReport)
class MemberComplaintReportAdmin(admin.ModelAdmin):
    list_display = ("member_code", "member_name", "reason", "meeting")
    search_fields = ("member_code", "member_name")
    list_filter = ("reason", "meeting")
    date_hierarchy = "meeting__started_at"
    fieldsets = (
        ("Member Info", {"fields": ("member_code", "member_ex_code", "member_name")}),
        ("Details", {"fields": ("reason", "meeting")}),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for managing User Profiles efficiently."""

    # Display essentials only for fast listing
    list_display = (
        "user",
        "department",
        "designation",
        "phone_number",
        "is_verified",
        "mpp_code",
    )
    list_filter = (
        "department",
        "is_verified",
        "mpp_code",
        "is_email_verified",
        "created_at",
    )
    search_fields = (
        "user__username",
        "user__email",
        "phone_number",
        "designation",
        "mpp_code",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

    # Reduce memory usage when loading related fields
    raw_id_fields = ("user", "reports_to")

    # Prepopulated fields are not appropriate here because "user" and "reports_to"
    # are foreign keys, not text fields. Removing it prevents unnecessary lookups.
    # prepopulated_fields = {"slug": ("user",)}  # Example if you had a slug

    # Use autocomplete fields (recommended Django approach for large datasets)
    autocomplete_fields = ("user", "reports_to")

    # Use select_related to avoid N+1 queries in changelist view
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user", "reports_to")

    # Group related fields logically for clarity
    fieldsets = (
        (_("User Information"), {
            "fields": (
                "user",
                "salutation",
                "designation",
                "department",
                "reports_to",
            ),
        }),
        (_("Contact & Identity"), {
            "fields": (
                "phone_number",
                "address",
                "avatar",
                "is_verified",
                "is_email_verified",
                "mpp_code",
            ),
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
        }),
    )

    # Pagination to avoid heavy list rendering
    list_per_page = 25

    # Filter optimization
    preserve_filters = True



@admin.register(UpdateRequestData)
class UpdateRequestDataAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "field_name",
        "old_value",
        "new_value",
        "data_type",
        "created_at",
        "updated_at",
    ]
    readonly_fields = ["created_at", "updated_at"]

    def get_readonly_fields(self, request, obj=None):
        base = self.readonly_fields
        if obj and getattr(obj.update_request, "status", None) in [
            RequestStatus.UPDATED,
            RequestStatus.REJECTED,
        ]:
            return base + ["field_name", "old_value", "new_value", "data_type"]
        return base


@admin.register(UpdateRequestDocument)
class UpdateRequestDocumentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "request_title",
        "created_by_full_name",
        "document_type",
        "original_filename",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "created_at",
        "created_by",
    ]
    readonly_fields = ["created_at", "updated_at", "file_size", "content_type"]

    def get_readonly_fields(self, request, obj=None):
        base = self.readonly_fields
        if obj and getattr(obj.request, "status", None) in [
            RequestStatus.UPDATED,
            RequestStatus.REJECTED,
        ]:
            return base + ["document_type", "file", "original_filename", "description"]
        return base

    @admin.display(description="Created By")
    def created_by_full_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.get_full_name()}"

    @admin.display(description="Requests")
    def request_title(self, obj):
        if obj.request:
            return f"{obj.request.request_id}"


@admin.register(UpdateRequestHistory)
class UpdateRequestHistoryAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "change_type",
        "field_name",
        "old_value",
        "new_value",
        "changed_by",
        "created_at",
    ]
    readonly_fields = [
        "change_type",
        "field_name",
        "old_value",
        "new_value",
        "changed_by",
        "created_at",
        "change_reason",
    ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


from import_export.formats.base_formats import XLSX

@admin.register(UpdateRequest)
class UpdateRequestAdmin(ExportActionModelAdmin):
    resource_class = UpdateRequestResource
    list_display = [
        "member_name",
        "member_code",
        "created_by",
        "request_type",
        "status_badge",
        "created_at",
        "reviewed_by",
        "reviewed_at",
    ]
    list_filter = [
        "status",
        "request_type",
        "role_type",
        "created_at",
        "reviewed_at",
        "created_by",
    ]
    search_fields = [
        "member_name",
        "member_code",
        "created_by__username",
        "created_by__first_name",
        "created_by__last_name",
    ]
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "reviewed_at",
        "history_link",
    ]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "id",
                    "created_by",
                    "member_code",
                    "member_name",
                    "mobile_number",
                    "role_type",
                    "request_type",
                )
            },
        ),
        (
            "Status & Review",
            {
                "fields": (
                    "status",
                    "reviewed_by",
                    "reviewed_at",
                    "ho_comments",
                    "rejection_reason",
                )
            },
        ),
        (
            "Audit Trail",
            {
                "fields": ("created_at", "updated_at", "updated_by"),
                "classes": ("collapse",),
            },
        ),
        ("History", {"fields": ("history_link",), "classes": ("collapse",)}),
    )

    actions = ["approve_selected_requests", "reject_selected_requests"]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "bulk-approve/",
                self.admin_site.admin_view(self.bulk_approve_view),
                name="bulk-approve",
            ),
        ]
        return custom_urls + urls
    

    def approve_selected_requests(self, request, queryset):
        from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME

        selected = request.POST.getlist(ACTION_CHECKBOX_NAME)
        return redirect(f"bulk-approve/?ids={','.join(selected)}")

    def bulk_approve_view(self, request):
        ids = request.GET.get("ids", "")
        id_list = ids.split(",")

        if request.method == "POST":
            form = ReasonForm(request.POST)
            if form.is_valid():
                reason = form.cleaned_data["reason"]
                raw_ids = request.GET.getlist("ids")
                if raw_ids:
                    selected_ids = (
                        raw_ids[0].split(",") if len(raw_ids) == 1 else raw_ids
                    )
                else:
                    selected_ids = []

                queryset = self.model.objects.filter(pk__in=selected_ids)
                updated = 0
                for obj in queryset.filter(status=RequestStatus.PENDING):
                    try:
                        updated += 1
                        obj.approve(request.user, reason)
                    except Exception as e:
                        self.message_user(
                            request,
                            f"Error approving {obj.request_id}: {str(e)}",
                            level=messages.ERROR,
                        )

                self.message_user(request, f"Successfully approved {updated} requests.")
                return redirect("..")  # Redirect back to changelist
        else:
            form = ReasonForm(initial={"_selected_action": id_list})

        return render(
            request,
            "admin/request_reason_form.html",
            {
                "objects": self.model.objects.filter(pk__in=id_list),
                "form": form,
                "title": "Provide reason for bulk approval",
                "action_label": "Updated",
                "button_class": "btn btn-success",  # 👈 here
            },
        )

    approve_selected_requests.short_description = "Approve selected requests"

    def reject_selected_requests(self, request, queryset):
        if "apply" in request.POST:
            form = ReasonForm(request.POST)
            if form.is_valid():
                reason = form.cleaned_data["reason"]
                updated = 0
                raw_ids = request.GET.getlist("ids")
                if raw_ids:
                    selected_ids = (
                        raw_ids[0].split(",") if len(raw_ids) == 1 else raw_ids
                    )
                else:
                    selected_ids = []

                for obj in queryset.filter(
                    pk__in=selected_ids, status=RequestStatus.PENDING
                ):
                    try:
                        obj.reject(request.user, reason)
                        updated += 1
                    except Exception as e:
                        self.message_user(
                            request,
                            f"Error rejecting {obj.request_id}: {str(e)}",
                            level=messages.ERROR,
                        )
                self.message_user(request, f"Successfully rejected {updated} requests.")
                return redirect(request.get_full_path())
        else:
            form = ReasonForm()

        return render(
            request,
            "admin/request_reason_form.html",
            {
                "form": form,
                "title": "Provide a reason for rejecting selected requests",
                "action_label": "Reject",
                "button_class": "btn btn-danger",  # 👈 here
            },
        )

    reject_selected_requests.short_description = "Reject selected requests"

    def status_badge(self, obj):
        colors = {
            RequestStatus.PENDING: "orange",
            RequestStatus.UPDATED: "green",
            RequestStatus.REJECTED: "red",
        }
        color = colors.get(obj.status, "gray")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"

    def history_link(self, obj):
        if obj.pk:
            url = reverse("admin:facilitator_updaterequesthistory_changelist")
            return format_html(
                '<a href="{}?request__id__exact={}" target="_blank">View History ({})</a>',
                url,
                obj.pk,
                obj.history.count(),
            )
        return "-"

    history_link.short_description = "History"
