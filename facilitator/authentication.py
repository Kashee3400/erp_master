from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models.facilitator_model import ApiKey
from django.utils.timezone import now
from django.core.cache import cache
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import now
from django.contrib.auth.models import AnonymousUser
from django.db.models import F


class ApiKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Check if the API key is provided in the request headers
        api_key = request.headers.get('X-API-KEY')

        if not api_key:
            raise AuthenticationFailed("API key is required for access.")

        try:
            # Check if the API key exists and is active
            api_key_obj = ApiKey.objects.get(key=api_key, is_active=True)
        except ApiKey.DoesNotExist:
            raise AuthenticationFailed("Invalid API key or API key is not active.")

        if api_key_obj.expires_at and api_key_obj.expires_at < now():
            raise AuthenticationFailed("API key has expired.")
        return (None, api_key_obj)

class ApiKeyAuthentication2(BaseAuthentication):
    def authenticate(self, request):
        api_key_value = request.headers.get("X-API-KEY")

        if not api_key_value:
            raise AuthenticationFailed("API key is required.")

        try:
            api_key_obj = ApiKey.objects.select_related("user").get(
                key=api_key_value, is_active=True, is_revoked=False
            )
        except ApiKey.DoesNotExist:
            self._increment_failed_attempts(api_key_value)
            raise AuthenticationFailed("Invalid or revoked API key.")

        # Check revocation or expiration
        current_time = now()
        if api_key_obj.expires_at and api_key_obj.expires_at < current_time:
            raise AuthenticationFailed("API key has expired.")

        if api_key_obj.valid_from and api_key_obj.valid_from > current_time:
            raise AuthenticationFailed("API key is not yet active.")

        # IP Restriction
        request_ip = request.META.get("REMOTE_ADDR")
        if api_key_obj.allowed_ips:
            allowed_ips = [ip.strip() for ip in api_key_obj.allowed_ips.split(",")]
            if request_ip not in allowed_ips:
                raise AuthenticationFailed("IP not allowed for this API key.")

        # URL Restriction
        if api_key_obj.allowed_urls:
            allowed_urls = [url.strip() for url in api_key_obj.allowed_urls.split(",")]
            if not any(request.path.startswith(url) for url in allowed_urls):
                raise AuthenticationFailed("Access to this URL is not allowed.")

        # Daily/Hourly Limits (custom implementation recommended)
        if not self._check_usage_limits(api_key_obj, current_time):
            raise AuthenticationFailed("API key usage limit exceeded.")

        # Max usage limit
        if (
            api_key_obj.max_usage_limit is not None
            and api_key_obj.usage_count >= api_key_obj.max_usage_limit
        ):
            raise AuthenticationFailed("API key maximum usage limit reached.")

        # Audit and update usage
        ApiKey.objects.filter(pk=api_key_obj.pk).update(
            usage_count=F("usage_count") + 1,
            last_used_at=current_time,
            last_used_by=api_key_obj.user,
        )
        return (api_key_obj.user or AnonymousUser(), api_key_obj)

    def _increment_failed_attempts(self, api_key_value: str):
        """Increments failed attempts for a known key."""
        ApiKey.objects.filter(key=api_key_value).update(
            failed_attempts=F("failed_attempts") + 1
        )

    def _check_usage_limits(self, api_key: ApiKey, current_time: datetime) -> bool:
        """
        Enforce per-day rate limit using Redis.
        Returns True if within limit, False otherwise.
        """
        if not api_key.requests_per_day:
            return True  # Unlimited usage

        # Format: api_key_usage:<api_key>:<YYYYMMDD>
        date_str = current_time.strftime("%Y%m%d")
        redis_key = f"api_key_usage:{api_key.key}:{date_str}"

        tomorrow = timezone.make_aware(
            datetime.combine(current_time.date() + timedelta(days=1), datetime.min.time()),
            timezone.get_current_timezone()
        )

        ttl = int((tomorrow - current_time).total_seconds())

        # Atomically add or increment key
        added = cache.add(redis_key, 1, timeout=ttl)
        if added:
            usage_today = 1
        else:
            try:
                usage_today = cache.incr(redis_key)
            except ValueError:
                # Race condition fallback
                cache.set(redis_key, 1, timeout=ttl)
                usage_today = 1

        # Return whether usage is within daily quota
        return usage_today <= api_key.requests_per_day
