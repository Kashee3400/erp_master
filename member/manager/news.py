from django.db import models


class NewsQuerySet(models.QuerySet):
    """Custom QuerySet for chainable queries"""

    def published(self):
        """Return only published news"""
        return self.filter(is_published=True)

    def by_module(self, module):
        """Filter news by module"""
        return self.filter(module=module)

    def unread(self):
        """Return unread news"""
        return self.filter(is_read=False)

    def recent(self, days=30):
        """Return news from last N days"""
        from django.utils import timezone
        from datetime import timedelta

        date_threshold = timezone.now() - timedelta(days=days)
        return self.filter(published_date__gte=date_threshold)

    def with_author_info(self):
        """Optimize query for author information if ForeignKey in future"""
        return self.select_related()  # Will be useful when author becomes FK
