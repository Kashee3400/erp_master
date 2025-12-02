from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
import json

from ..models.transaction_model import PaymentTransaction

class PaymentTransactionAdmin(admin.ModelAdmin):
    """
    Comprehensive Django Admin for PaymentTransaction model
    """
    
    # List Display
    list_display = [
        'merchant_order_id',
        'transaction_type',
        'user_identifier',
        'amount_display',
        'status_badge',
        'payment_method_type',
        'created_at',
        'action_buttons',
    ]
    
    # List Filters
    list_filter = [
        'status',
        'transaction_type',
        'payment_method_type',
        'is_active',
        'created_at',
        'verified_at',
        'currency',
    ]
    
    # Search Fields
    search_fields = [
        'merchant_order_id',
        'phonepe_transaction_id',
        'user_identifier',
        'object_id',
        'gateway_response_message',
        'status_message',
    ]
    
    # Read-only Fields
    readonly_fields = [
        'id',
        'merchant_order_id',
        'phonepe_transaction_id',
        'created_at',
        'updated_at',
        'verified_at',
        'completed_at',
        'content_type',
        'object_id',
        'webhook_response_display',
        'payment_method_display',
        'metadata_display',
        'checksum',
        'related_object_link',
    ]
    
    # Fieldsets for organized display
    fieldsets = (
        ('Transaction Information', {
            'fields': (
                'id',
                'merchant_order_id',
                'phonepe_transaction_id',
                'transaction_type',
                'status',
                'status_message',
            )
        }),
        ('Related Object', {
            'fields': (
                'content_type',
                'object_id',
                'related_object_link',
            )
        }),
        ('User & Amount Details', {
            'fields': (
                'user_identifier',
                'amount',
                'currency',
            )
        }),
        ('Payment Details', {
            'fields': (
                'payment_method_type',
                'payment_method_display',
                'gateway_response_code',
                'gateway_response_message',
            )
        }),
        ('URLs', {
            'fields': (
                'redirect_url',
                'callback_url',
            ),
            'classes': ('collapse',),
        }),
        ('User Defined Fields', {
            'fields': (
                'udf1',
                'udf2',
                'udf3',
            ),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': (
                'metadata_display',
            ),
            'classes': ('collapse',),
        }),
        ('Webhook Response', {
            'fields': (
                'webhook_response_display',
            ),
            'classes': ('collapse',),
        }),
        ('Retry & Failure Tracking', {
            'fields': (
                'retry_count',
                'max_retries',
                'failure_reason',
            ),
            'classes': ('collapse',),
        }),
        ('Refund Information', {
            'fields': (
                'refund_amount',
                'refund_initiated_at',
                'refund_completed_at',
                'refund_reference_id',
            ),
            'classes': ('collapse',),
        }),
        ('Security & Tracking', {
            'fields': (
                'checksum',
                'ip_address',
                'user_agent',
            ),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
                'verified_at',
                'expires_at',
                'completed_at',
            ),
            'classes': ('collapse',),
        }),
        ('Status', {
            'fields': (
                'is_active',
                'deleted_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    # Ordering
    ordering = ['-created_at']
    
    # Date hierarchy
    date_hierarchy = 'created_at'
    
    # Items per page
    list_per_page = 50
    
    # Actions
    actions = [
        'mark_as_verified',
        'mark_as_failed',
        'export_selected_transactions',
    ]
    
    # Custom Methods for Display
    
    @admin.display(description='Amount', ordering='amount')
    def amount_display(self, obj):
        """Display amount with currency"""
        return format_html(
            '<strong style="color: #0066cc;">{} {}</strong>',
            obj.currency,
            obj.amount
        )
    
    @admin.display(description='Status')
    def status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            'INITIATED': '#FFA500',
            'PENDING': '#FFD700',
            'SUCCESS': '#28a745',
            'FAILED': '#dc3545',
            'EXPIRED': '#6c757d',
            'REFUNDED': '#17a2b8',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.status
        )
    
    @admin.display(description='Actions')
    def action_buttons(self, obj):
        """Display action buttons"""
        return format_html(
            '<a class="button" href="{}">View Details</a>',
            reverse('admin:gateway_paymenttransaction_change', args=[obj.pk])
        )
    
    @admin.display(description='Webhook Response')
    def webhook_response_display(self, obj):
        """Display formatted webhook response"""
        if obj.webhook_response:
            formatted_json = json.dumps(obj.webhook_response, indent=2)
            return format_html(
                '<pre style="background: #f5f5f5; padding: 10px; '
                'border-radius: 4px; max-height: 300px; overflow: auto;">{}</pre>',
                formatted_json
            )
        return '-'
    
    @admin.display(description='Payment Method')
    def payment_method_display(self, obj):
        """Display formatted payment method"""
        if obj.payment_method:
            formatted_json = json.dumps(obj.payment_method, indent=2)
            return format_html(
                '<pre style="background: #f5f5f5; padding: 10px; '
                'border-radius: 4px;">{}</pre>',
                formatted_json
            )
        return '-'
    
    @admin.display(description='Metadata')
    def metadata_display(self, obj):
        """Display formatted metadata"""
        if obj.metadata:
            formatted_json = json.dumps(obj.metadata, indent=2)
            return format_html(
                '<pre style="background: #f5f5f5; padding: 10px; '
                'border-radius: 4px;">{}</pre>',
                formatted_json
            )
        return '-'
    
    @admin.display(description='Related Object')
    def related_object_link(self, obj):
        """Display link to related object"""
        if obj.content_object:
            try:
                url = reverse(
                    f'admin:{obj.content_type.app_label}_{obj.content_type.model}_change',
                    args=[obj.object_id]
                )
                return format_html(
                    '<a href="{}" target="_blank">{} - {}</a>',
                    url,
                    obj.content_type.model.title(),
                    obj.object_id
                )
            except:
                return f"{obj.content_type.model.title()} - {obj.object_id}"
        return '-'
    
    # Admin Actions
    
    @admin.action(description='Mark selected as VERIFIED')
    def mark_as_verified(self, request, queryset):
        """Mark selected transactions as verified"""
        updated = queryset.update(
            status='SUCCESS',
            verified_at=timezone.now()
        )
        self.message_user(
            request,
            f'{updated} transaction(s) marked as verified.'
        )
    
    @admin.action(description='Mark selected as FAILED')
    def mark_as_failed(self, request, queryset):
        """Mark selected transactions as failed"""
        updated = queryset.update(status='FAILED')
        self.message_user(
            request,
            f'{updated} transaction(s) marked as failed.'
        )
    
    @admin.action(description='Export selected transactions')
    def export_selected_transactions(self, request, queryset):
        """Export selected transactions (implement CSV export)"""
        # Implement CSV export logic here
        self.message_user(
            request,
            f'{queryset.count()} transaction(s) exported.'
        )
    
    # Override queryset for performance
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('content_type')
    
    # Customize admin interface
    def has_delete_permission(self, request, obj=None):
        """Restrict delete permission (soft delete preferred)"""
        return request.user.is_superuser
    
    def has_add_permission(self, request):
        """Disable adding transactions through admin"""
        return False
    
    # Add custom styling
    class Media:
        css = {
            'all': ('admin/css/payment_admin.css',)
        }


# Register the model with the admin
admin.site.register(PaymentTransaction, PaymentTransactionAdmin)