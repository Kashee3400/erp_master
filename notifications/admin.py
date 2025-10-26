from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html

from .model import (
    NotificationTemplate,
    Notification,
    NotificationPreferences,
    NotificationGroup,
    NotificationDelivery,
    NotificationClickTracking,
    NotificationAnalytics,
)


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "notification_type",
        "default_priority",
        "active_status",
        "channels_display",
        "notification_count",
        "updated_at",
    )
    list_filter = (
        "is_active",
        "category",
        "notification_type",
        "default_priority",
        "created_at",
    )
    search_fields = ("name", "category", "title_template", "body_template")
    readonly_fields = (
        "created_at",
        "updated_at",
        "notification_count",
        "usage_stats",
    )

    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": (
                    "name",
                    "category",
                    "is_active",
                    "notification_type",
                    "default_priority",
                )
            },
        ),
        (
            _("Content"),
            {
                "fields": (
                    "title_template",
                    "body_template",
                    "email_subject_template",
                    "email_body_template",
                )
            },
        ),
        (
            _("Channels & Configuration"),
            {
                "fields": ("enabled_channels",),
                "description": _("Select channels this template supports"),
            },
        ),
        (
            _("Deep Linking"),
            {
                "fields": ("route_template", "url_name"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Statistics"),
            {
                "fields": ("notification_count", "usage_stats"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Metadata"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    ordering = ("category", "name")
    date_hierarchy = "created_at"

    def active_status(self, obj):
        """Display active status as colored badge"""
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; '
                'padding: 3px 10px; border-radius: 3px;">Active</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; '
            'padding: 3px 10px; border-radius: 3px;">Inactive</span>'
        )

    active_status.short_description = _("Status")

    def channels_display(self, obj):
        """Display enabled channels as badges"""
        if not obj.enabled_channels:
            return "-"
        badges = []
        colors = {
            "push": "#007bff",
            "email": "#17a2b8",
            "sms": "#ffc107",
            "in_app": "#28a745",
        }
        for channel in obj.enabled_channels:
            color = colors.get(channel, "#6c757d")
            badges.append(
                f'<span style="background-color: {color}; color: white; '
                f'padding: 3px 8px; border-radius: 3px; margin-right: 5px;">{channel}</span>'
            )
        return format_html(" ".join(badges))

    channels_display.short_description = _("Channels")

    def notification_count(self, obj):
        """Show number of notifications created from this template"""
        count = obj.notifications.count()
        return format_html(
            '<span style="font-weight: bold; color: #007bff;">{}</span>', count
        )

    notification_count.short_description = _("Total Notifications")

    def usage_stats(self, obj):
        """Display detailed usage statistics"""
        total = obj.notifications.count()
        delivered = obj.notifications.filter(status="delivered").count()
        failed = obj.notifications.filter(status="failed").count()
        read = obj.notifications.filter(is_read=True).count()

        delivery_rate = ((delivered / total) * 100) if total > 0 else 0
        read_rate = ((read / total) * 100) if total > 0 else 0

        stats = (
            f"<strong>Total:</strong> {total}<br>"
            f"<strong>Delivered:</strong> {delivered} ({delivery_rate:.1f}%)<br>"
            f"<strong>Failed:</strong> {failed}<br>"
            f"<strong>Read:</strong> {read} ({read_rate:.1f}%)"
        )
        return format_html(stats)

    usage_stats.short_description = _("Usage Statistics")

    # def has_delete_permission(self, request, obj=None):
    #     """Prevent deletion of templates with active notifications"""
    #     if obj and obj.notifications.filter(status__in=["pending", "queued"]).exists():
    #         return False
    #     return super().has_delete_permission(request, obj)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "uuid_short",
        "template_name",
        "recipient_email",
        "status_badge",
        "channels_display",
        "priority_badge",
        "scheduled_at",
        "delivered_at",
    )
    list_filter = (
        "status",
        "priority",
        "notification_type",
        ("scheduled_at", admin.DateFieldListFilter),
        ("delivered_at", admin.DateFieldListFilter),
        "is_read",
        "template__category",
    )
    search_fields = (
        "uuid",
        "recipient__email",
        "recipient__username",
        "title",
        "body",
        "template__name",
    )
    readonly_fields = (
        "uuid",
        "created_at",
        "updated_at",
        "delivery_summary",
        "content_preview",
    )

    fieldsets = (
        (
            _("Identifiers"),
            {"fields": ("uuid", "template")},
        ),
        (
            _("Recipients"),
            {
                "fields": ("recipient", "sender"),
            },
        ),
        (
            _("Content"),
            {
                "fields": (
                    "title",
                    "body",
                    "content_preview",
                    "email_subject",
                    "email_body",
                )
            },
        ),
        (
            _("Configuration"),
            {
                "fields": (
                    "channels",
                    "priority",
                    "notification_type",
                    "context_data",
                )
            },
        ),
        (
            _("Deep Linking"),
            {
                "fields": ("deep_link_url", "app_route"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Status & Delivery"),
            {
                "fields": (
                    "status",
                    "delivery_summary",
                    "delivery_status",
                    "scheduled_at",
                    "sent_at",
                    "delivered_at",
                    "read_at",
                    "expires_at",
                )
            },
        ),
        (
            _("In-App Status"),
            {
                "fields": ("is_read", "is_archived"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Metadata"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    def uuid_short(self, obj):
        """Display shortened UUID"""
        return format_html(
            '<code style="font-size: 11px; background: #f5f5f5; padding: 2px 5px;">{}</code>',
            str(obj.uuid)[:8],
        )

    uuid_short.short_description = _("UUID")

    def template_name(self, obj):
        """Display template with link to edit"""
        url = reverse("admin:notifications_notificationtemplate_change", args=[obj.template.id])
        return format_html(
            '<a href="{}">{}</a>', url, obj.template.name
        )

    template_name.short_description = _("Template")

    def recipient_email(self, obj):
        """Display recipient email with link"""
        url = reverse("admin:auth_user_change", args=[obj.recipient.id])
        return format_html(
            '<a href="{}">{}</a>', url, obj.recipient.email if obj.recipient.email else obj.recipient.username
        )

    recipient_email.short_description = _("Recipient")

    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            "pending": "#6c757d",
            "queued": "#007bff",
            "processing": "#0dcaf0",
            "delivered": "#28a745",
            "failed": "#dc3545",
            "expired": "#fd7e14",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = _("Status")

    def channels_display(self, obj):
        """Display channels as compact badges"""
        if not obj.channels:
            return "-"
        badges = []
        colors = {
            "push": "#007bff",
            "email": "#17a2b8",
            "sms": "#ffc107",
            "in_app": "#28a745",
        }
        for channel in obj.channels:
            color = colors.get(channel, "#6c757d")
            badges.append(
                f'<span style="background-color: {color}; color: white; '
                f'padding: 2px 6px; border-radius: 2px; margin-right: 3px; font-size: 11px;">{channel}</span>'
            )
        return format_html(" ".join(badges))

    channels_display.short_description = _("Channels")

    def priority_badge(self, obj):
        """Display priority as colored badge"""
        colors = {
            "low": "#6c757d",
            "normal": "#0dcaf0",
            "high": "#ffc107",
            "urgent": "#dc3545",
        }
        color = colors.get(obj.priority, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 2px; font-size: 11px;">{}</span>',
            color,
            obj.priority.upper(),
        )

    priority_badge.short_description = _("Priority")

    def content_preview(self, obj):
        """Preview of notification content"""
        preview = (
            f"<strong>Title:</strong> {obj.title}<br>"
            f"<strong>Body:</strong> {obj.body[:200]}..."
            if len(obj.body) > 200
            else f"<strong>Title:</strong> {obj.title}<br>"
            f"<strong>Body:</strong> {obj.body}"
        )
        return format_html(preview)

    content_preview.short_description = _("Content Preview")

    def delivery_summary(self, obj):
        """Display delivery status summary"""
        summary = "<strong>Per-Channel Status:</strong><br>"
        if obj.delivery_status:
            for channel, status in obj.delivery_status.items():
                status_text = status.get("status", "unknown")
                delivered_at = status.get("delivered_at", "N/A")
                summary += f"<strong>{channel}:</strong> {status_text} ({delivered_at})<br>"
        else:
            summary += "No per-channel tracking"
        return format_html(summary)

    delivery_summary.short_description = _("Delivery Summary")

    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        queryset = super().get_queryset(request)
        return queryset.select_related(
            "template", "recipient", "sender", "content_type"
        )

    def has_add_permission(self, request):
        """Notifications should be created via service, not admin"""
        return False

    # def has_delete_permission(self, request, obj=None):
    #     """Allow deletion only for old/expired notifications"""
    #     if obj and obj.created_at > timezone.now() - timedelta(days=30):
    #         return False
    #     return True


@admin.register(NotificationPreferences)
class NotificationPreferencesAdmin(admin.ModelAdmin):
    list_display = (
        "user_email",
        "template_or_category",
        "channel_preferences",
        "quiet_hours_display",
    )
    list_filter = (
        "allow_push",
        "allow_email",
        "allow_sms",
        "allow_in_app",
        "created_at",
    )
    search_fields = ("user__email", "user__username", "template__name", "category")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            _("User & Target"),
            {
                "fields": ("user", "template", "category"),
                "description": _("Set preferences for a specific template or category"),
            },
        ),
        (
            _("Channel Preferences"),
            {
                "fields": (
                    "allow_push",
                    "allow_email",
                    "allow_sms",
                    "allow_in_app",
                )
            },
        ),
        (
            _("Quiet Hours"),
            {
                "fields": (
                    "quiet_hours_start",
                    "quiet_hours_end",
                    "timezone",
                )
            },
        ),
        (
            _("Metadata"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    ordering = ("user", "template", "category")

    def user_email(self, obj):
        """Display user email with link"""
        url = reverse("admin:auth_user_change", args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)

    user_email.short_description = _("User")

    def template_or_category(self, obj):
        """Display template or category"""
        if obj.template:
            return format_html(
                '<strong>Template:</strong> {}<br><small>Category: {}</small>',
                obj.template.name,
                obj.template.category,
            )
        return format_html(
            '<strong>Category:</strong> {}', obj.category or "All"
        )

    template_or_category.short_description = _("Target")

    def channel_preferences(self, obj):
        """Display channel preferences summary"""
        prefs = []
        if obj.allow_push:
            prefs.append('<span style="color: #007bff;">✓ Push</span>')
        if obj.allow_email:
            prefs.append('<span style="color: #17a2b8;">✓ Email</span>')
        if obj.allow_sms:
            prefs.append('<span style="color: #ffc107;">✓ SMS</span>')
        if obj.allow_in_app:
            prefs.append('<span style="color: #28a745;">✓ In-App</span>')

        if not prefs:
            return format_html('<span style="color: #dc3545;">All Disabled</span>')

        return format_html(" | ".join(prefs))

    channel_preferences.short_description = _("Channels")

    def quiet_hours_display(self, obj):
        """Display quiet hours"""
        if obj.quiet_hours_start and obj.quiet_hours_end:
            return format_html(
                "{} - {} ({})",
                obj.quiet_hours_start.strftime("%H:%M"),
                obj.quiet_hours_end.strftime("%H:%M"),
                obj.timezone,
            )
        return "-"

    quiet_hours_display.short_description = _("Quiet Hours")

    def get_queryset(self, request):
        """Optimize queryset"""
        queryset = super().get_queryset(request)
        return queryset.select_related("user", "template")


@admin.register(NotificationGroup)
class NotificationGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "notification_count", "created_at", "related_object_display")
    list_filter = ("created_at",)
    search_fields = ("name", "description", "uuid")
    readonly_fields = ("uuid", "created_at", "notification_list")

    fieldsets = (
        (
            _("Information"),
            {
                "fields": ("uuid", "name", "description"),
            },
        ),
        (
            _("Related Object"),
            {
                "fields": ("content_type", "object_id"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Styling"),
            {
                "fields": ("icon", "color"),
            },
        ),
        (
            _("Notifications"),
            {
                "fields": ("notification_list",),
            },
        ),
        (
            _("Metadata"),
            {
                "fields": ("created_at",),
                "classes": ("collapse",),
            },
        ),
    )

    ordering = ("-created_at",)

    def notification_count(self, obj):
        """Display number of notifications in group"""
        count = obj.notifications.count() if hasattr(obj, "notifications") else 0
        return format_html(
            '<span style="background-color: #007bff; color: white; '
            'padding: 2px 8px; border-radius: 3px;">{}</span>',
            count,
        )

    notification_count.short_description = _("Notifications")

    def notification_list(self, obj):
        """Display list of notifications in group"""
        if not hasattr(obj, "notifications"):
            return "-"
        notifications = obj.notifications.all()[:10]
        if not notifications:
            return "-"
        items = []
        for notif in notifications:
            items.append(
                f"<li>{notif.template.name} → {notif.recipient.email} "
                f'<span style="color: #6c757d;">({notif.status})</span></li>'
            )
        html = f"<ul>{''.join(items)}</ul>"
        if obj.notifications.count() > 10:
            html += f'<small style="color: #6c757d;">... and {obj.notifications.count() - 10} more</small>'
        return format_html(html)

    notification_list.short_description = _("Notifications in Group")

    def related_object_display(self, obj):
        """Display related object"""
        if obj.related_object:
            return str(obj.related_object)
        return "-"

    related_object_display.short_description = _("Related Object")

    def has_add_permission(self, request):
        """Groups created automatically"""
        return False


@admin.register(NotificationDelivery)
class NotificationDeliveryAdmin(admin.ModelAdmin):
    list_display = (
        "notification_short",
        "channel",
        "status_badge",
        "recipient",
        "attempt_display",
        "sent_at",
    )
    list_filter = ("status", "channel", ("sent_at", admin.DateFieldListFilter))
    search_fields = ("notification__uuid", "recipient", "external_id")
    readonly_fields = (
        "created_at",
        "updated_at",
        "response_display",
    )

    fieldsets = (
        (
            _("Notification & Channel"),
            {
                "fields": ("notification", "channel"),
            },
        ),
        (
            _("Recipient & Status"),
            {
                "fields": ("recipient", "status", "external_id"),
            },
        ),
        (
            _("Delivery Attempts"),
            {
                "fields": (
                    "attempt_count",
                    "max_attempts",
                    "next_attempt_at",
                )
            },
        ),
        (
            _("Response"),
            {
                "fields": ("response_display", "error_message"),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": ("sent_at", "delivered_at", "failed_at"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Metadata"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    def notification_short(self, obj):
        """Display notification with link"""
        url = reverse(
            "admin:notifications_notification_change", args=[obj.notification.id]
        )
        return format_html(
            '<a href="{}">{}</a>',
            url,
            str(obj.notification.uuid)[:8],
        )

    notification_short.short_description = _("Notification")

    def status_badge(self, obj):
        """Display delivery status as badge"""
        colors = {
            "pending": "#6c757d",
            "sent": "#0dcaf0",
            "delivered": "#28a745",
            "failed": "#dc3545",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 7px; '
            'border-radius: 2px;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = _("Status")

    def attempt_display(self, obj):
        """Display attempt count"""
        return format_html(
            "{} / {}",
            obj.attempt_count,
            obj.max_attempts,
        )

    attempt_display.short_description = _("Attempts")

    def response_display(self, obj):
        """Display response data formatted"""
        if obj.response_data:
            import json

            return format_html(
                "<pre>{}</pre>",
                json.dumps(obj.response_data, indent=2),
            )
        return "-"

    response_display.short_description = _("Response Data")

    def get_queryset(self, request):
        """Optimize queryset"""
        queryset = super().get_queryset(request)
        return queryset.select_related("notification")

    def has_add_permission(self, request):
        """Deliveries created automatically"""
        return False


@admin.register(NotificationClickTracking)
class NotificationClickTrackingAdmin(admin.ModelAdmin):
    list_display = (
        "notification_short",
        "clicked_at",
        "ip_address",
        "user_agent_short",
    )
    list_filter = (("clicked_at", admin.DateFieldListFilter),)
    search_fields = ("notification__uuid", "ip_address")
    readonly_fields = ("notification", "clicked_at", "user_agent")

    fieldsets = (
        (
            _("Click Information"),
            {
                "fields": ("notification", "clicked_at"),
            },
        ),
        (
            _("User Information"),
            {
                "fields": ("ip_address", "user_agent"),
            },
        ),
    )

    date_hierarchy = "clicked_at"
    ordering = ("-clicked_at",)

    def notification_short(self, obj):
        """Display notification with link"""
        url = reverse(
            "admin:notifications_notification_change", args=[obj.notification.id]
        )
        return format_html(
            '<a href="{}">{}</a>',
            url,
            str(obj.notification.uuid)[:8],
        )

    notification_short.short_description = _("Notification")

    def user_agent_short(self, obj):
        """Display shortened user agent"""
        if obj.user_agent:
            short = obj.user_agent[:50] + "..." if len(obj.user_agent) > 50 else obj.user_agent
            return format_html(
                '<small title="{}">{}</small>', obj.user_agent, short
            )
        return "-"

    user_agent_short.short_description = _("User Agent")

    def get_queryset(self, request):
        """Optimize queryset"""
        queryset = super().get_queryset(request)
        return queryset.select_related("notification")

    def has_add_permission(self, request):
        """Tracking created automatically"""
        return False


@admin.register(NotificationAnalytics)
class NotificationAnalyticsAdmin(admin.ModelAdmin):
    list_display = (
        "template_name",
        "channel",
        "date",
        "sent_count",
        "delivery_rate_display",
        "read_rate_display",
        "click_rate_display",
    )
    list_filter = ("channel", ("date", admin.DateFieldListFilter), "template")
    search_fields = ("template__name",)
    readonly_fields = (
        "template",
        "channel",
        "date",
        "sent_count",
        "delivered_count",
        "read_count",
        "clicked_count",
        "failed_count",
        "delivery_rate",
        "read_rate",
        "click_rate",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            _("Template & Channel"),
            {
                "fields": ("template", "channel", "date"),
            },
        ),
        (
            _("Metrics"),
            {
                "fields": (
                    "sent_count",
                    "delivered_count",
                    "read_count",
                    "clicked_count",
                    "failed_count",
                )
            },
        ),
        (
            _("Rates"),
            {
                "fields": (
                    "delivery_rate",
                    "read_rate",
                    "click_rate",
                )
            },
        ),
        (
            _("Metadata"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    date_hierarchy = "date"
    ordering = ("-date", "template", "channel")

    def template_name(self, obj):
        """Display template name with link"""
        url = reverse(
            "admin:notifications_notificationtemplate_change", args=[obj.template.id]
        )
        return format_html('<a href="{}">{}</a>', url, obj.template.name)

    template_name.short_description = _("Template")

    def delivery_rate_display(self, obj):
        """Display delivery rate as percentage with color"""
        rate = float(obj.delivery_rate) * 100
        color = "#28a745" if rate >= 80 else "#ffc107" if rate >= 50 else "#dc3545"
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 2px;">{:.1f}%</span>',
            color,
            rate,
        )

    delivery_rate_display.short_description = _("Delivery Rate")

    def read_rate_display(self, obj):
        """Display read rate as percentage with color"""
        rate = float(obj.read_rate) * 100
        color = "#28a745" if rate >= 50 else "#ffc107" if rate >= 25 else "#dc3545"
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 2px;">{:.1f}%</span>',
            color,
            rate,
        )

    read_rate_display.short_description = _("Read Rate")

    def click_rate_display(self, obj):
        """Display click rate as percentage with color"""
        rate = float(obj.click_rate) * 100
        color = "#28a745" if rate >= 20 else "#ffc107" if rate >= 10 else "#dc3545"
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 2px;">{:.1f}%</span>',
            color,
            rate,
        )

    click_rate_display.short_description = _("Click Rate")

    def get_queryset(self, request):
        """Optimize queryset"""
        queryset = super().get_queryset(request)
        return queryset.select_related("template")

    def has_add_permission(self, request):
        """Analytics created automatically"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of analytics data"""
        return False