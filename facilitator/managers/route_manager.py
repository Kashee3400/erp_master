from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class UserLocationQuerySet(models.QuerySet):
    """Custom QuerySet for UserLocation with common filters."""

    def active(self):
        """Return only active location assignments."""
        return self.filter(active=True)

    def for_user(self, user):
        """Return all locations for a specific user."""
        return self.filter(user=user, active=True)

    def primary_only(self):
        """Return only primary location assignments."""
        return self.filter(is_primary=True, active=True)

    def by_level(self, level):
        """Filter by assignment level (mcc/route/mpp)."""
        return self.filter(level=level, active=True)

    def mcc_level(self):
        """Return MCC level assignments."""
        return self.by_level("mcc")

    def route_level(self):
        """Return Route level assignments."""
        return self.by_level("route")

    def mpp_level(self):
        """Return MPP level assignments."""
        return self.by_level("mpp")


class UserLocationManager(models.Manager):
    """Custom manager for UserLocation."""

    def get_queryset(self):
        return UserLocationQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def for_user(self, user):
        return self.get_queryset().for_user(user)

    def primary_only(self):
        return self.get_queryset().primary_only()

    def by_level(self, level):
        return self.get_queryset().by_level(level)

    def get_user_hierarchy(self, user):
        """
        Get complete hierarchy for a user.
        Returns a dict with mcc, route, and mpp lists.
        """
        locations = self.for_user(user).select_related("user", "assigned_by")

        return {
            "mcc": list(locations.mcc_level()),
            "route": list(locations.route_level()),
            "mpp": list(locations.mpp_level()),
        }

    def assign_location(
        self, user, level, assigned_by, is_primary=False, **location_data
    ):
        """
        Helper method to assign a location to a user.

        Args:
            user: User instance
            level: Assignment level ('mcc', 'route', 'mpp')
            assigned_by: User who is making the assignment
            is_primary: Whether this is the primary location
            **location_data: MCC, Route, MPP fields as needed

        Returns:
            UserLocation instance
        """
        # If setting as primary, unset other primary locations for this user
        if is_primary:
            self.filter(user=user, is_primary=True).update(is_primary=False)

        return self.create(
            user=user,
            level=level,
            assigned_by=assigned_by,
            is_primary=is_primary,
            **location_data,
        )
