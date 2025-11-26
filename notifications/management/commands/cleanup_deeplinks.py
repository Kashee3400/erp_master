# ============================================
# management/commands/cleanup_deeplinks.py
# ============================================

from django.core.management.base import BaseCommand
from ...deeplink_service import DeepLinkService


class Command(BaseCommand):
    help = 'Cleanup expired deep links'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=5000,
            help='Number of links to process per batch'
        )
    
    def handle(self, *args, **options):
        batch_size = options['batch_size']
        service = DeepLinkService()
        
        self.stdout.write('Starting cleanup...')
        
        updated = service.cleanup_expired_links(batch_size=batch_size)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully marked {updated} expired links'
            )
        )