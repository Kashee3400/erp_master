from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Feedback, FeedbackComment, FeedbackLog
from import_export.admin import ImportExportActionModelAdmin
from .models import FeedbackFile


class FeedbackAttachmentInline(admin.TabularInline):
    model = FeedbackFile
    extra = 0
    readonly_fields = ("uploaded_at",)
    fields = ("file", "uploaded_at")


@admin.register(FeedbackFile)
class FeedbackAttachmentAdmin(admin.ModelAdmin):
    list_display = ("feedback", "file", "uploaded_at")
    search_fields = ("feedback__feedback_id", "file")
    list_filter = ("uploaded_at",)


from .forms.feedback_form import FeedbackAdminForm


@admin.register(Feedback)
class FeedbackAdmin(ImportExportActionModelAdmin):
    form = FeedbackAdminForm

    list_display = (
        "feedback_id",
        "sender",
        "assigned_to",
        "status",
        "priority",
        "progress",
        "rating",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "priority", "created_at", "assigned_to")
    search_fields = ("feedback_id", "member_code", "mobile_no", "name")

    readonly_fields = ("feedback_id", "created_at", "updated_at")

    fieldsets = (
        (
            "Feedback Meta",
            {
                "fields": (
                    "feedback_id",
                    "sender",
                    "status",
                    "priority",
                    "category",
                    "progress",
                    "rating",
                )
            },
        ),
        (
            "Assignment Details",
            {"fields": ("assigned_to", "assigned_at", "resolved_at")},
        ),
        (
            "Member Info",
            {
                "fields": (
                    "mpp_code",
                    "mcc_code",
                    "member_code",
                    "member_tr_code",
                    "name",
                    "mobile_no",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(FeedbackComment)
class FeedbackCommentAdmin(admin.ModelAdmin):
    list_display = ("feedback", "user", "commented_by", "timestamp")
    list_filter = ("timestamp",)
    search_fields = ("feedback__feedback_id", "comment", "commented_by")


@admin.register(FeedbackLog)
class FeedbackLogAdmin(admin.ModelAdmin):
    list_display = ("feedback", "user", "previous_status", "new_status", "timestamp")
    list_filter = ("timestamp", "previous_status", "new_status")
    search_fields = ("feedback__feedback_id", "user__username", "reason")
