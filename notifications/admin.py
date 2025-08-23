from django.contrib import admin
from .model import AppNotification


@admin.register(AppNotification)
class AppNotificationAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "recipient",
        "sender",
        "model",
        "object_id",
        "notification_type",
        "sent_via",
        "is_read",
        "created_at",
        "deleted",
    )
    list_filter = (
        "notification_type",
        "sent_via",
        "is_read",
        "deleted",
        "model",
    )
    search_fields = (
        "title",
        "message",
        "recipient__username",
        "recipient__email",
        "sender__username",
        "sender__email",
    )
    date_hierarchy = "created_at"
    readonly_fields = (
        "title",
        "body",
        "message",
        "recipient",
        "sender",
        "model",
        "object_id",
        "route",
        "custom_key",
        "is_subroute",
        "notification_type",
        "sent_via",
        "created_at",
        "read_at",
    )
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        # Disallow manual creation
        return False

    def has_change_permission(self, request, obj=None):
        # Prevent changing existing records
        return False
