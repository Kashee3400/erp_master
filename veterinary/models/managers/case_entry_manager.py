from django.db import models
from django.db.models import OuterRef, Subquery, Q
from django.db.models.functions import Coalesce


class CaseEntryQuerySet(models.QuerySet):
    """Custom queryset for CaseEntry to support domain-specific filtering."""

    def member_cases(self):
        """Return cases linked to registered member cattle."""
        return self.filter(cattle__isnull=False)

    def non_member_cases(self):
        """Return cases linked to non-member cattle."""
        return self.filter(non_member_cattle__isnull=False)

    def by_owner_mobile(self, mobile):
        """Find cases using the cattle owner's mobile number."""
        return self.filter(
            Q(cattle__owner__mobile_no=mobile)
            | Q(non_member_cattle__non_member__mobile_no=mobile)
        )

    def by_mcc_mpp(self, mcc_code=None, mpp_code=None, strict=False):
        """
        Filter cases by MCC and/or MPP code from either member or non-member cattle.

        Args:
            mcc_code (str | None): MCC code to match.
            mpp_code (str | None): MPP code to match.
            strict (bool):
                If True → require both MCC and MPP to match.
                If False → match whichever code(s) provided.

        Returns:
            QuerySet[CaseEntry]
        """
        q_obj = Q()

        # Normalize safely (preserve leading zeros)
        if mcc_code:
            mcc_code = str(mcc_code).upper().strip()
        if mpp_code:
            mpp_code = str(mpp_code).upper().strip()

        if strict and mcc_code and mpp_code:
            # Require both MCC and MPP to match
            q_obj = Q(
                Q(
                    cattle__owner__mcc_code=mcc_code,
                    cattle__owner__mpp_code=mpp_code,
                )
                | Q(
                    non_member_cattle__non_member__mcc_code=mcc_code,
                    non_member_cattle__non_member__mpp_code=mpp_code,
                )
            )
        else:
            # Match whichever codes provided
            if mcc_code:
                q_obj |= Q(cattle__owner__mcc_code=mcc_code) | Q(
                    non_member_cattle__non_member__mcc_code=mcc_code
                )
            if mpp_code:
                q_obj |= Q(cattle__owner__mpp_code=mpp_code) | Q(
                    non_member_cattle__non_member__mpp_code=mpp_code
                )

        # Return filtered queryset
        return self.filter(q_obj)

    def with_active_payment(self):
        """
        Annotates each CaseEntry with the ID of the active payment:
            Priority = pending → unpaid → partial → None
        """

        from veterinary.models.case_models import CasePayment

        # priority: pending
        pending_qs = CasePayment.objects.filter(
            case_entry=OuterRef("pk"), payment_status="pending"
        ).order_by("created_at")

        # next: unpaid
        unpaid_qs = CasePayment.objects.filter(
            case_entry=OuterRef("pk"), payment_status="unpaid"
        ).order_by("created_at")

        # next: partial
        partial_qs = CasePayment.objects.filter(
            case_entry=OuterRef("pk"), payment_status="partial"
        ).order_by("created_at")

        return self.annotate(
            pending_payment_id=Subquery(pending_qs.values("id")[:1]),
            unpaid_payment_id=Subquery(unpaid_qs.values("id")[:1]),
            partial_payment_id=Subquery(partial_qs.values("id")[:1]),
            # active priority logic (Coalesce picks first non-null)
            active_payment_id=Coalesce(
                "pending_payment_id",
                "unpaid_payment_id",
                "partial_payment_id",
            ),
        )


class CaseEntryManager(models.Manager):
    """Custom manager exposing domain-level shortcuts for CaseEntry."""

    def get_queryset(self):
        return CaseEntryQuerySet(self.model, using=self._db)

    # Shortcuts that proxy to the QuerySet
    def member_cases(self):
        """Return cases linked to registered member cattle."""
        return self.get_queryset().member_cases()

    def non_member_cases(self):
        """Return cases linked to non-member cattle."""
        return self.get_queryset().non_member_cases()

    def by_owner_mobile(self, mobile):
        """Return cases matching an owner’s mobile number."""
        return self.get_queryset().by_owner_mobile(mobile)

    def by_mcc_mpp(self, mcc_code=None, mpp_code=None, strict=False):
        """Return cases filtered by MCC/MPP code(s)."""
        return self.get_queryset().by_mcc_mpp(mcc_code, mpp_code, strict)

    def with_active_payment(self):
        """Include active payment annotation in queryset."""
        return self.get_queryset().with_active_payment()
