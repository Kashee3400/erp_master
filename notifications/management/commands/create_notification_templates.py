# notifications/management/commands/create_notification_templates.py
from django.core.management.base import BaseCommand
from ...model import NotificationTemplate, NotificationChannel


class Command(BaseCommand):
    help = "Create default notification templates"

    def add_arguments(self, parser):
        parser.add_argument("--app", type=str, help="Create templates for specific app")

    def handle(self, *args, **options):
        templates = [
            # Generic templates
            {
                "name": "welcome_user",
                "title_template": "Welcome to {{ site_name }}!",
                "body_template": "Hello {{ recipient.first_name }}, welcome to our platform!",
                "email_subject_template": "Welcome to {{ site_name }}",
                "email_body_template": "Hello {{ recipient.first_name }},\n\nWelcome to {{ site_name }}! We are excited to have you on board.",
                "route_template": "/profile/",
                "category": "user",
                "enabled_channels": [
                    NotificationChannel.IN_APP,
                    NotificationChannel.EMAIL,
                    NotificationChannel.PUSH,
                ],
            },
            {
                "name": "password_reset",
                "title_template": "Password Reset Request",
                "body_template": "Click the link to reset your password",
                "email_subject_template": "Reset your password",
                "route_template": "/reset-password/",
                "category": "auth",
                "enabled_channels": [
                    NotificationChannel.EMAIL,
                    NotificationChannel.PUSH,
                ],
            },
            # E-commerce templates
            {
                "name": "order_created",
                "title_template": "Order Confirmed #{{ object.order_number }}",
                "body_template": "Your order has been confirmed and is being processed.",
                "route_template": "/orders/{{ object_id }}/",
                "url_name": "orders:detail",
                "category": "orders",
                "enabled_channels": [
                    NotificationChannel.IN_APP,
                    NotificationChannel.EMAIL,
                    NotificationChannel.PUSH,
                ],
            },
            {
                "name": "order_shipped",
                "title_template": "Order Shipped #{{ object.order_number }}",
                "body_template": "Your order has been shipped! Track: {{ tracking_code }}",
                "route_template": "/orders/{{ object_id }}/track/",
                "category": "orders",
                "enabled_channels": [
                    NotificationChannel.IN_APP,
                    NotificationChannel.EMAIL,
                    NotificationChannel.PUSH,
                    NotificationChannel.SMS,
                ],
            },
            {
                "name": "payment_received",
                "title_template": "Payment Received",
                "body_template": "We have received your payment of ${{ amount }}",
                "route_template": "/payments/{{ object_id }}/",
                "category": "payments",
                "enabled_channels": [
                    NotificationChannel.IN_APP,
                    NotificationChannel.EMAIL,
                ],
            },
            # System templates
            {
                "name": "system_maintenance",
                "title_template": "System Maintenance Scheduled",
                "body_template": "System maintenance is scheduled for {{ maintenance_date }}",
                "route_template": "/system/maintenance/",
                "category": "system",
                "enabled_channels": [
                    NotificationChannel.IN_APP,
                    NotificationChannel.EMAIL,
                    NotificationChannel.PUSH,
                ],
            },
            {
                "name": "security_alert",
                "title_template": "Security Alert",
                "body_template": "Unusual activity detected on your account",
                "route_template": "/security/alerts/",
                "category": "security",
                "enabled_channels": [
                    NotificationChannel.IN_APP,
                    NotificationChannel.EMAIL,
                    NotificationChannel.PUSH,
                    NotificationChannel.SMS,
                ],
            },
        ]

        app_filter = options.get("app")
        if app_filter:
            templates = [t for t in templates if t["category"] == app_filter]

        created_count = 0
        for template_data in templates:
            template, created = NotificationTemplate.objects.get_or_create(
                name=template_data["name"], defaults=template_data
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Created template: {template.name}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Template already exists: {template.name}")
                )

        self.stdout.write(
            self.style.SUCCESS(f"\nCreated {created_count} new templates")
        )
