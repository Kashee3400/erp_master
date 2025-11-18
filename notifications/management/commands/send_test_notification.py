# notifications/management/commands/send_test_notification.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from ...model import Notification
from notifications.tasks import deliver_notification

User = get_user_model()


class Command(BaseCommand):
    help = "Send test notification"

    def add_arguments(self, parser):
        parser.add_argument("--user", type=str, required=True, help="User email")
        parser.add_argument("--template", type=str, required=True, help="Template name")
        parser.add_argument("--context", type=str, help="JSON context data")

    def handle(self, *args, **options):
        # res = ping.delay()
        # print(res.id)
        try:
            user = User.objects.get(username=options["user"])
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {options["user"]} not found'))
            return
        notification = Notification.objects.filter(
            recipient=user, template__name=options["template"]
        ).first()
        
        if not notification:
            self.stdout.write(self.style.ERROR("No matching notification found."))
            return

        try:
            async_result = deliver_notification.delay(notification.uuid)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Test notification task queued successfully.\n"
                    f"Notification UUID: {notification.uuid}\n"
                    f"Celery Task ID: {async_result.id}"
                )
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to send notification: {e}"))
