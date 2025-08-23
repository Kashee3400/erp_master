# notifications/management/commands/send_test_notification.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from ...notification_service import notify

User = get_user_model()


class Command(BaseCommand):
    help = "Send test notification"

    def add_arguments(self, parser):
        parser.add_argument("--user", type=str, required=True, help="User email")
        parser.add_argument("--template", type=str, required=True, help="Template name")
        parser.add_argument("--context", type=str, help="JSON context data")

    def handle(self, *args, **options):
        try:
            user = User.objects.get(email=options["user"])
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {options["user"]} not found'))
            return

        context = {}
        if options["context"]:
            import json

            context = json.loads(options["context"])

        try:
            notification = notify(
                template_name=options["template"], recipient=user, context=context
            )

            self.stdout.write(
                self.style.SUCCESS(f"Test notification sent: {notification.uuid}")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to send notification: {e}"))
