"""
Django Admin Configuration for NotificationTemplate
Modern admin interface with preview, testing, and validation
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django import forms
from django.core.exceptions import ValidationError
import json
from ..model import NotificationTemplate


class NotificationTemplateAdminForm(forms.ModelForm):
    """Custom form with enhanced validation and widgets"""

    class Meta:
        model = None  # Set dynamically
        fields = "__all__"
        widgets = {
            "title_template": forms.TextInput(
                attrs={
                    "style": "width: 100%;",
                    "placeholder": "Order #{{ order.id }} Confirmed",
                }
            ),
            "body_template": forms.Textarea(
                attrs={
                    "rows": 4,
                    "style": "width: 100%; font-family: monospace;",
                    "placeholder": "Your order has been confirmed...",
                }
            ),
            "email_subject_template": forms.TextInput(
                attrs={
                    "style": "width: 100%;",
                    "placeholder": "Order Confirmation - #{{ order.id }}",
                }
            ),
            "email_body_template": forms.Textarea(
                attrs={
                    "rows": 6,
                    "style": "width: 100%; font-family: monospace;",
                }
            ),
            "sms_template": forms.TextInput(
                attrs={
                    "style": "width: 100%;",
                    "placeholder": "Max 160 characters",
                    "maxlength": "160",
                }
            ),
            "whatsapp_template": forms.Textarea(
                attrs={
                    "rows": 3,
                    "style": "width: 100%;",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 2,
                    "style": "width: 100%;",
                }
            ),
            "deeplink_config": forms.Textarea(
                attrs={
                    "rows": 10,
                    "style": "width: 100%; font-family: monospace;",
                    "placeholder": json.dumps(
                        {
                            "module": "member",
                            "url_name": "order:detail",
                            "route_template": "orders/{{ order.id }}/",
                            "fallback_template": "https://kashee.com/orders/{{ order.id }}/",
                            "inapp_route": "order/{{ order.id }}",
                            "deeplink_type": "order_detail",
                            "expires_after": 7,
                            "max_uses": 1,
                        },
                        indent=2,
                    ),
                }
            ),
        }

    def clean_deeplink_config(self):
        """Validate deeplink_config JSON structure"""
        config = self.cleaned_data.get("deeplink_config")
        if config:
            # Validate JSON structure
            required_keys = ["inapp_route"]
            for key in required_keys:
                if key not in config:
                    raise ValidationError(f"Missing required key: {key}")
        return config

    def clean_enabled_channels(self):
        """Validate enabled channels"""
        channels = self.cleaned_data.get("enabled_channels")
        if not channels or len(channels) == 0:
            raise ValidationError("At least one channel must be enabled")
        return channels


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """Enhanced admin interface for NotificationTemplate"""

    form = NotificationTemplateAdminForm

    # ==========================================
    # LIST VIEW
    # ==========================================

    list_display = [
        "name",
        "category_badge",
        "locale_flag",
        "channels_display",
        "priority_badge",
        "type_badge",
        "has_deeplink",
        "version_display",
        "status_display",
        "preview_button",
    ]

    list_filter = [
        "is_active",
        "category",
        "locale",
        "default_priority",
        "notification_type",
        "created_at",
    ]

    search_fields = [
        "name",
        "category",
        "description",
        "title_template",
        "body_template",
    ]

    ordering = ["-created_at"]

    list_per_page = 25

    # ==========================================
    # FORM VIEW
    # ==========================================

    fieldsets = (
        (
            _("Identification"),
            {
                "fields": (
                    "name",
                    "category",
                    "description",
                    "locale",
                    "version",
                    "tags",
                ),
                "description": "Basic template identification and categorization",
            },
        ),
        (
            _("Push / In-App Content"),
            {
                "fields": ("title_template", "body_template"),
                "description": "Content for push notifications and in-app messages",
            },
        ),
        (
            _("Email Content"),
            {
                "fields": (
                    "email_subject_template",
                    "email_body_template",
                    "email_is_html",
                ),
                "classes": ("collapse",),
                "description": "Email-specific templates",
            },
        ),
        (
            _("SMS Content"),
            {
                "fields": ("sms_template",),
                "classes": ("collapse",),
                "description": "SMS template (max 160 chars recommended)",
            },
        ),
        (
            _("WhatsApp Content"),
            {
                "fields": ("whatsapp_template",),
                "classes": ("collapse",),
                "description": "WhatsApp Business template",
            },
        ),
        (
            _("Channel Configuration"),
            {
                "fields": ("enabled_channels", "channel_config"),
                "description": "Configure which channels to use and channel-specific settings",
            },
        ),
        (
            _("Notification Behavior"),
            {
                "fields": ("default_priority", "notification_type", "action_buttons"),
            },
        ),
        (
            _("Deep Link Configuration"),
            {
                "fields": ("deeplink_config",),
                "description": "Declarative deep link configuration for DeepLinkService",
                "classes": ("wide",),
            },
        ),
        (
            _("Context & Validation"),
            {
                "fields": ("required_context_vars", "sample_context"),
                "classes": ("collapse",),
                "description": "Define required variables and sample data for testing",
            },
        ),
        (
            _("Analytics & Tracking"),
            {
                "fields": ("tracking_enabled", "analytics_metadata"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Throttling & Scheduling"),
            {
                "fields": ("throttle_config", "quiet_hours"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Status & Metadata"),
            {
                "fields": ("is_active", "created_by", "updated_by"),
            },
        ),
    )

    readonly_fields = ["created_at", "updated_at", "created_by", "updated_by"]

    autocomplete_fields = ["created_by", "updated_by"]

    # ==========================================
    # CUSTOM DISPLAY METHODS
    # ==========================================

    @admin.display(description="Category")
    def category_badge(self, obj):
        """Display category as a colored badge"""
        colors = {
            "orders": "#10b981",
            "payments": "#3b82f6",
            "users": "#8b5cf6",
            "system": "#6b7280",
        }
        color = colors.get(obj.category, "#6b7280")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.category.upper(),
        )

    @admin.display(description="Locale")
    def locale_flag(self, obj):
        """Display locale with flag emoji"""
        flags = {
            "en": "🇬🇧",
            "hi": "🇮🇳",
            "es": "🇪🇸",
            "fr": "🇫🇷",
        }
        flag = flags.get(obj.locale, "🌐")
        return format_html(
            '<span style="font-size: 18px;" title="{}">{}</span>',
            obj.locale,
            flag,
        )

    @admin.display(description="Channels")
    def channels_display(self, obj):
        """Display enabled channels with icons"""
        icons = {
            "push": "📱",
            "email": "📧",
            "sms": "💬",
            "whatsapp": "📞",
            "in_app": "🔔",
        }
        channels_html = " ".join(
            [
                f'<span title="{ch}">{icons.get(ch, "•")}</span>'
                for ch in obj.enabled_channels
            ]
        )
        return format_html(channels_html)

    @admin.display(description="Priority")
    def priority_badge(self, obj):
        """Display priority as colored badge"""
        colors = {
            "low": "#94a3b8",
            "normal": "#3b82f6",
            "high": "#f59e0b",
            "urgent": "#ef4444",
        }
        color = colors.get(obj.default_priority, "#3b82f6")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 2px; font-size: 10px; font-weight: 600;">{}</span>',
            color,
            obj.default_priority.upper(),
        )

    @admin.display(description="Type")
    def type_badge(self, obj):
        """Display notification type with icon"""
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "action": "👉",
        }
        icon = icons.get(obj.notification_type, "•")
        return format_html(
            '<span title="{}">{}</span>',
            obj.notification_type,
            icon,
        )

    @admin.display(description="Deep Link", boolean=True)
    def has_deeplink(self, obj):
        """Show if template has deep link configured"""
        return bool(obj.deeplink_config)

    @admin.display(description="Version")
    def version_display(self, obj):
        """Display version number"""
        return f"v{obj.version}"

    @admin.display(description="Status")
    def status_display(self, obj):
        """Display active/inactive status"""
        if obj.is_active:
            return format_html(
                '<span style="color: #10b981; font-weight: 600;">● Active</span>'
            )
        return format_html(
            '<span style="color: #ef4444; font-weight: 600;">● Inactive</span>'
        )

    @admin.display(description="Actions")
    def preview_button(self, obj):
        """Display preview button"""
        return format_html(
            '<a class="button" href="/admin/notifications/notificationtemplate/{}/preview/" '
            'target="_blank">Preview</a>',
            obj.pk,
        )

    # ==========================================
    # ACTIONS
    # ==========================================

    actions = [
        "activate_templates",
        "deactivate_templates",
        "duplicate_template",
        "test_template",
    ]

    @admin.action(description="Activate selected templates")
    def activate_templates(self, request, queryset):
        """Activate selected templates"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} template(s) activated.")

    @admin.action(description="Deactivate selected templates")
    def deactivate_templates(self, request, queryset):
        """Deactivate selected templates"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} template(s) deactivated.")

    @admin.action(description="Duplicate selected template")
    def duplicate_template(self, request, queryset):
        """Duplicate a template (for creating variations)"""
        for template in queryset:
            template.pk = None
            template.name = f"{template.name}_copy"
            template.save()
        self.message_user(request, f"{queryset.count()} template(s) duplicated.")

    @admin.action(description="Test selected templates")
    def test_template(self, request, queryset):
        """Test templates with sample context"""
        for template in queryset:
            try:
                preview = template.preview()
                self.message_user(
                    request,
                    f"✅ {template.name}: {preview['content']['title']}",
                )
            except Exception as e:
                self.message_user(
                    request,
                    f"❌ {template.name}: {str(e)}",
                    level="ERROR",
                )

    # ==========================================
    # SAVE HOOKS
    # ==========================================

    def save_model(self, request, obj, form, change):
        """Save with user tracking"""
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    # ==========================================
    # CUSTOM VIEWS (Add these to urls.py)
    # ==========================================

    def get_urls(self):
        """Add custom URLs for preview and testing"""
        from django.urls import path

        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:pk>/preview/",
                self.admin_site.admin_view(self.preview_view),
                name="notificationtemplate_preview",
            ),
            path(
                "<int:pk>/test/",
                self.admin_site.admin_view(self.test_view),
                name="notificationtemplate_test",
            ),
        ]
        return custom_urls + urls

    def preview_view(self, request, pk):
        """Preview template with sample context"""
        from django.shortcuts import render, get_object_or_404

        template = get_object_or_404(self.model, pk=pk)
        preview = template.preview()

        return render(
            request,
            "admin/notifications/preview.html",
            {
                "title": f"Preview: {template.name}",
                "template": template,
                "preview": preview,
                "opts": self.model._meta,
            },
        )

    def test_view(self, request, pk):
        """Test template with custom context"""
        from django.shortcuts import render, get_object_or_404
        from django.http import JsonResponse

        template = get_object_or_404(self.model, pk=pk)

        if request.method == "POST":
            # Parse custom context from POST
            import json

            custom_context = json.loads(request.POST.get("context", "{}"))

            try:
                preview = template.preview(custom_context)
                return JsonResponse(
                    {
                        "success": True,
                        "preview": preview,
                    }
                )
            except Exception as e:
                return JsonResponse(
                    {
                        "success": False,
                        "error": str(e),
                    }
                )

        return render(
            request,
            "admin/notifications/test.html",
            {
                "title": f"Test: {template.name}",
                "template": template,
                "opts": self.model._meta,
            },
        )


# ==========================================
# INLINE ADMIN FOR RELATED MODELS
# ==========================================


class NotificationLogInline(admin.TabularInline):
    """Inline for viewing notification logs (if you have a NotificationLog model)"""

    model = None  # Set to your NotificationLog model
    extra = 0
    readonly_fields = ["created_at", "status", "channel", "recipient"]
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False
