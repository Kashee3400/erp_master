"""
Production-ready view for handling deep link redirects.
"""

import logging
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from notifications.model import DeepLink
from ..deeplink_service import DeepLinkService
from django.views import View

logger = logging.getLogger(__name__)


@method_decorator(never_cache, name="dispatch")
@method_decorator(csrf_exempt, name="dispatch")
class DeepLinkRedirectView(View):
    """
    Universal App Links / Deep Link handler.

    Handles:
    - Android App Links
    - iOS Universal Links
    - Web fallback
    - Analytics tracking
    """

    def get(self, request, token=None):
        """
        Handle deep link redirect based on user agent.

        Query params:
            token: UUID token for the deep link
        """
        # Get token from URL or query params
        token = token or request.GET.get("token")

        if not token:
            return self._error_response("Missing token parameter", status=400)

        # Validate and retrieve link
        service = DeepLinkService()
        deep_link = service.validate_and_get_link(token)

        if not deep_link:
            return self._handle_invalid_link(request, token)

        # Track the access
        try:
            deep_link.increment_use()
        except Exception as e:
            logger.error(f"Error tracking link usage: {e}")

        # Detect platform
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()

        if "android" in user_agent:
            return self._redirect_android(deep_link, request)
        elif "iphone" in user_agent or "ipad" in user_agent:
            return self._redirect_ios(deep_link, request)
        else:
            return self._redirect_web(deep_link, request)

    def _redirect_android(self, deep_link: DeepLink, request):
        """Handle Android deep link redirect with Intent URL."""
        intent_url = (
            f"intent://{deep_link.path}#Intent;"
            f"scheme={deep_link.scheme};"
            f"package={deep_link.android_package};"
        )

        if deep_link.fallback_url:
            intent_url += f"S.browser_fallback_url={deep_link.fallback_url};"

        intent_url += "end"

        logger.info(f"Android redirect: {intent_url}")
        print(intent_url)
        return redirect(intent_url)

    def _redirect_ios(self, deep_link: DeepLink, request):
        """Handle iOS Universal Link redirect."""
        # For iOS, return HTML with meta tag + JavaScript fallback
        context = {
            "deep_link": deep_link.deep_link,
            "fallback_url": deep_link.fallback_url or "https://tech.kasheemilk.com:8443",
            "app_store_id": self._get_app_store_id(deep_link.module),
        }

        return render(request, "deeplink/ios_redirect.html", context)

    def _redirect_web(self, deep_link: DeepLink, request):
        """Handle web fallback redirect."""
        if deep_link.fallback_url:
            return redirect(deep_link.fallback_url)

        # Default web landing page
        return render( 
            request,
            "deeplink/web_fallback.html",
            {
                "deep_link": deep_link,
                "module": deep_link.module,
            },
        )

    def _handle_invalid_link(self, request, token):
        """Handle invalid or expired links."""
        logger.warning(f"Invalid deep link token accessed: {token}")

        # Determine home URL based on user agent
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        try:
            dl = DeepLink.objects.get(token=token)

            if "android" in user_agent:
                home_url = (
                    f"intent://home#Intent;scheme={dl.scheme};package={dl.android_package}.android;end"
                )
            else:
                home_url = "https://tech.kasheemilk.com:8443/"

            context = {"home_url": home_url}

            if dl.status == DeepLink.Status.EXPIRED:
                return render(request, "deeplink/expired.html", context, status=410)
            elif dl.status == DeepLink.Status.REVOKED:
                return render(request, "deeplink/revoked.html", context, status=410)
            elif dl.status == DeepLink.Status.CONSUMED:
                return render(request, "deeplink/consumed.html", context, status=410)

        except DeepLink.DoesNotExist:
            pass

        return self._error_response("Invalid or expired link", status=404)

    def _error_response(self, message: str, status: int = 400):
        """Return error response based on Accept header."""
        return JsonResponse({"error": message, "status": status}, status=status)

    def _get_app_store_id(self, module: str) -> str:
        """Get App Store ID for the module."""
        # Map modules to App Store IDs
        app_store_ids = {
            "member": "123456789",
            "sahayak": "234567890",
            "pes": "345678901",
        }
        return app_store_ids.get(module, "123456789")


class DeepLinkInfoView(View):
    """
    API endpoint to get deep link information.
    Useful for debugging and analytics.
    """

    def get(self, request, token):
        """Get deep link metadata."""
        service = DeepLinkService()
        deep_link = service.validate_and_get_link(token)

        if not deep_link:
            return JsonResponse({"error": "Link not found or invalid"}, status=404)

        return JsonResponse(
            {
                "token": str(deep_link.token),
                "module": deep_link.module,
                "path": deep_link.path,
                "status": deep_link.status,
                "is_valid": deep_link.is_valid,
                "is_expired": deep_link.is_expired,
                "use_count": deep_link.use_count,
                "max_uses": deep_link.max_uses,
                "expires_at": (
                    deep_link.expires_at.isoformat() if deep_link.expires_at else None
                ),
                "created_at": deep_link.created_at.isoformat(),
                "fallback_url": deep_link.fallback_url,
            }
        )


class DeepLinkHealthCheckView(View):
    """Health check endpoint for monitoring."""

    def get(self, request):
        """Simple health check."""
        try:
            # Test database connectivity
            count = DeepLink.objects.count()

            return JsonResponse(
                {
                    "status": "healthy",
                    "total_links": count,
                }
            )
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return JsonResponse({"status": "unhealthy", "error": str(e)}, status=500)
