# ============================================
# admin.py - Django Admin Configuration
# ============================================
from django.contrib import admin
from django.utils.html import format_html
from notifications.model import DeepLink


@admin.register(DeepLink)
class DeepLinkAdmin(admin.ModelAdmin):
    """Admin interface for deep links."""

    list_display = [
        "token",
        "user",
        "module",
        "status_badge",
        "use_count",
        "max_uses",
        "expires_at",
        "created_at",
        "smart_link",
    ]

    list_filter = [
        "status",
        "module",
        "created_at",
        "expires_at",
    ]

    search_fields = [
        "token",
        "user__username",
        "user__email",
        "deep_link",
        "deep_path",
    ]

    readonly_fields = [
        "token",
        "created_at",
        "updated_at",
        "use_count",
        "last_accessed_at",
        "smart_link_display",
        "is_valid",
        "is_expired",
        "is_exhausted",
    ]

    fieldsets = (
        ("Basic Info", {"fields": ("token", "user", "module", "status")}),
        ("Deep Link", {"fields": ("deep_link", "deep_path", "smart_link_display")}),
        (
            "Platform Config",
            {"fields": ("android_package", "ios_bundle_id", "fallback_url")},
        ),
        (
            "Validity",
            {
                "fields": (
                    "expires_at",
                    "max_uses",
                    "is_valid",
                    "is_expired",
                    "is_exhausted",
                )
            },
        ),
        ("Usage", {"fields": ("use_count", "last_accessed_at")}),
        ("Metadata", {"fields": ("meta",), "classes": ("collapse",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    actions = ["revoke_links", "extend_expiry"]

    def status_badge(self, obj):
        """Display colored status badge."""
        colors = {
            "active": "green",
            "expired": "orange",
            "revoked": "red",
            "consumed": "gray",
        }
        color = colors.get(obj.status, "gray")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"

    def smart_link(self, obj):
        """Display clickable smart link."""
        from ..deeplink_service import DeepLinkService

        link = f"{DeepLinkService.SMART_HOST}{obj.token}"
        return format_html('<a href="{}" target="_blank">Open Link</a>', link)

    smart_link.short_description = "Test Link"

    def smart_link_display(self, obj):
        """Display full smart link in detail view."""
        from ..deeplink_service import DeepLinkService

        link = f"{DeepLinkService.SMART_HOST}{obj.token}"
        return format_html('<a href="{0}" target="_blank">{0}</a>', link)

    smart_link_display.short_description = "Smart Link URL"

    def revoke_links(self, request, queryset):
        """Bulk revoke selected links."""
        updated = queryset.filter(status=DeepLink.Status.ACTIVE).update(
            status=DeepLink.Status.REVOKED
        )

        self.message_user(request, f"{updated} link(s) were revoked.")

    revoke_links.short_description = "Revoke selected links"

    def extend_expiry(self, request, queryset):
        """Bulk extend expiry by 7 days."""
        from django.utils import timezone
        from datetime import timedelta

        for obj in queryset:
            obj.extend_expiry(days=7)

        self.message_user(
            request, f"{queryset.count()} link(s) expiry extended by 7 days."
        )

    extend_expiry.short_description = "Extend expiry by 7 days"
