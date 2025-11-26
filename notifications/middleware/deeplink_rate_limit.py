# ============================================
# middleware.py - Optional Rate Limiting
# ============================================

from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings


class DeepLinkRateLimitMiddleware:
    """
    Rate limit deep link creation per user.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, "DEEPLINK_RATE_LIMIT_ENABLED", False)
        self.max_per_day = getattr(settings, "DEEPLINK_MAX_LINKS_PER_USER_PER_DAY", 100)

    def __call__(self, request):
        if self.enabled and request.path.startswith("/api/deeplink/generate"):
            if request.user.is_authenticated:
                cache_key = f"deeplink_rate:{request.user.id}"
                count = cache.get(cache_key, 0)

                if count >= self.max_per_day:
                    return JsonResponse(
                        {
                            "error": "Rate limit exceeded",
                            "limit": self.max_per_day,
                        },
                        status=429,
                    )

                cache.set(cache_key, count + 1, 86400)  # 24 hours

        return self.get_response(request)
