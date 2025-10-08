# Utility functions for easier querying
from django.db import models


class CaseEntryQuerySet(models.QuerySet):
    def member_cases(self):
        return self.filter(cattle__isnull=False)

    def non_member_cases(self):
        return self.filter(non_member_cattle__isnull=False)

    def by_owner_mobile(self, mobile):
        from django.db.models import Q
        return self.filter(
            Q(cattle__owner__mobile_no=mobile) |
            Q(non_member_cattle__non_member__mobile_no=mobile)
        )


class CaseEntryManager(models.Manager):
    def get_queryset(self):
        return CaseEntryQuerySet(self.model, using=self._db)

    def member_cases(self):
        return self.get_queryset().member_cases()

    def non_member_cases(self):
        return self.get_queryset().non_member_cases()

    def by_owner_mobile(self, mobile):
        return self.get_queryset().by_owner_mobile(mobile)
