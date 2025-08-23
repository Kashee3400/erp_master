# notifications/management/commands/cleanup_notifications.py
from django.core.management.base import BaseCommand
from ...notification_service import (
    NotificationService,
    Notification,
    NotificationStatus,
)


class Command(BaseCommand):
    help = "Cleanup expired notifications"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting",
        )

    def handle(self, *args, **options):
        service = NotificationService()

        if options["dry_run"]:
            from django.utils import timezone

            count = Notification.objects.filter(
                expires_at__lt=timezone.now(),
                status__in=[NotificationStatus.SENT, NotificationStatus.DELIVERED],
            ).count()

            self.stdout.write(
                self.style.WARNING(f"Would delete {count} expired notifications")
            )
        else:
            count = service.cleanup_expired()
            self.stdout.write(
                self.style.SUCCESS(f"Deleted {count} expired notifications")
            )
