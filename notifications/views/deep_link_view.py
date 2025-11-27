"""
Production-ready view for handling deep link redirects.
"""

import logging
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from notifications.model import DeepLink
from ..deeplink_service import DeepLinkService
from django.views import View
from types import SimpleNamespace


logger = logging.getLogger(__name__)
from notifications.deeplink_service import DeepLinkRegistry


@method_decorator(never_cache, name="dispatch")
@method_decorator(csrf_exempt, name="dispatch")
class DeepLinkRedirectView(View):
    """
    Handles:
    - Android App Links
    - iOS Universal Links
    - Desktop fallback
    Automatically detects:
    - Module from URL
    """

    def get(self, request, token=None):

        # Detect module from URL path
        module = detect_module_from_path(request.path.replace("app-links/", ""))
        # Get app configuration
        app_cfg = DeepLinkRegistry.get(module)
        if not app_cfg:
            return self._error_response("Unknown app module", status=400)
        # If your DB deep link is required — keep using token logic
        token = token or request.GET.get("token")

        if token:
            service = DeepLinkService()
            deep_link = service.validate_and_get_link(token)

            if not deep_link:
                return self._handle_invalid_link(request, token)

            try:
                deep_link.increment_use()
            except Exception:
                logger.exception("Failed to increment deep link usage")

        else:
            # If no token, build a simple deep path from the URL
            deep_link = SimpleNamespace(
                module=module,
                scheme=app_cfg.scheme,
                android_package=app_cfg.android_package,
                ios_bundle_id=app_cfg.ios_bundle_id,
                deep_link=f"{app_cfg.scheme}://{request.path}",
                deep_path=request.path.lstrip("/"),
                fallback_url=app_cfg.default_fallback,
            )

        # Platform detection
        ua = request.META.get("HTTP_USER_AGENT", "").lower()

        if "android" in ua:
            return self._redirect_android(deep_link, app_cfg, request)

        if "iphone" in ua or "ipad" in ua:
            return self._redirect_ios(deep_link, app_cfg, request)

        # Desktop → open module website
        return self._redirect_web(deep_link, app_cfg, request)

    def _redirect_android(self, deep_link, app_cfg, request):

        play_store_url = (
            f"https://play.google.com/store/apps/details?id={app_cfg.android_package}"
        )

        intent_url = (
            f"intent://{deep_link.deep_path}#Intent;"
            f"scheme={app_cfg.scheme};"
            f"package={app_cfg.android_package};"
            f"S.browser_fallback_url={play_store_url};"
            "end"
        )

        context = {
            "platform": "android",
            "intent_url": intent_url,
            "play_store_url": play_store_url,
            "fallback_url": deep_link.fallback_url,
            "target": deep_link.deep_link,  # kashee://member/home etc.
        }

        return render(request, "deeplink/open.html", context)

    def _redirect_ios(self, deep_link, app_cfg, request):
        app_store_url = f"https://apps.apple.com/app/{app_cfg.ios_bundle_id}"

        context = {
            "platform": "ios",
            "app_store_url": app_store_url,
            "fallback_url": deep_link.fallback_url,
            "target": deep_link.deep_link,  # kashee://something
        }

        return render(request, "deeplink/open.html", context)

    def _redirect_web(self, deep_link, app_cfg, request):
        context = {
            "platform": "web",
            "fallback_url": deep_link.fallback_url,
            "target": request.build_absolute_uri(),  # QR code target
        }

        return render(request, "deeplink/open.html", context)

    def _handle_invalid_link(self, request, token):
        """Handle invalid or expired links."""
        logger.warning(f"Invalid deep link token accessed: {token}")

        # Determine home URL based on user agent
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        try:
            dl = DeepLink.objects.get(token=token)

            if "android" in user_agent:
                home_url = f"intent://home#Intent;scheme={dl.scheme};package={dl.android_package}.android;end"
            else:
                home_url = "https://tech.kasheemilk.com/"

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


def detect_module_from_path(path: str) -> str:
    """
    Detect module from request path.
    /member/...   → member
    /sahayak/...  → sahayak
    /pes/...      → pes
    Default = member
    """
    path = path.lower()

    if path.startswith("/member"):
        return "member"
    if path.startswith("/sahayak"):
        return "sahayak"
    if path.startswith("/pes"):
        return "pes"

    return "member"
