from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Feedback, FeedbackComment, FeedbackLog

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

@admin.register(Feedback)
class SahayakFeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "feedback_id",
        "sender",
        "assigned_to",
        "status",
        "priority",
        "created_at",
        "resolved_at",
    )
    list_filter = ("status", "priority", "created_at", "resolved_at", "assigned_to")
    search_fields = ("feedback_id", "sender__username", "assigned_to__username", "mpp_code", "message")
    readonly_fields = ("feedback_id", "created_at", "updated_at", "resolved_at", "assigned_at")


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
