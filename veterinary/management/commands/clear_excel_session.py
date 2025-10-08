# management/commands/cleanup_excel_sessions.py
# Management command to clean up old sessions
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from ...models.excel_model import ExcelUploadSession


class Command(BaseCommand):
    help = 'Clean up old Excel upload sessions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Delete sessions older than this many days (default: 7)'
        )

    def handle(self, *args, **options):
        days = options['days']
        cutoff_date = timezone.now() - timedelta(days=days)

        deleted_count = ExcelUploadSession.objects.filter(
            uploaded_at__lt=cutoff_date
        ).delete()[0]

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted {deleted_count} old Excel upload sessions'
            )
        )
