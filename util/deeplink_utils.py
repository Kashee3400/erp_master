# deeplink_utils.py
"""
Django utilities for generating deep links for Kashee apps
"""

from urllib.parse import urlencode
from typing import Optional


# Base URLs
KASHEE_SCHEME = "kashee://"
WEB_DOMAIN = "https://tech.kasheemilk.com:8443"
PLAY_STORE_BASE = "https://play.google.com/store/apps/details?id="
APP_STORE_BASE = "https://apps.apple.com/app/id"

# Package names
KASHEE_MEMBERS_PACKAGE = "com.kasheemilk.kashee"
KASHEE_PES_PACKAGE = "com.kasheemilk.kasheepes"
KASHEE_SAHAYAK_PACKAGE = "com.kasheemilk.kashee_sahayak"


def make_json_safe(value):
    from datetime import datetime, date
    from uuid import UUID
    from decimal import Decimal

    # Already JSON-safe
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    # Convert datetimes
    if isinstance(value, (datetime, date)):
        return value.isoformat()

    # Convert Decimal
    if isinstance(value, Decimal):
        return float(value)

    # Convert UUID to string
    if isinstance(value, UUID):
        return str(value)

    # Convert Django model -> pk or string
    if hasattr(value, "pk"):
        return value.pk

    # Convert QuerySet -> list of pks
    try:
        from django.db.models.query import QuerySet

        if isinstance(value, QuerySet):
            return list(value.values_list("pk", flat=True))
    except Exception:
        pass

    # Convert dict recursively
    if isinstance(value, dict):
        return {k: make_json_safe(v) for k, v in value.items()}

    # Convert list/tuple/set recursively
    if isinstance(value, (list, tuple, set)):
        return [make_json_safe(v) for v in value]

    # Fallback → convert to string
    return str(value)


def build_scheme_link(action: str, item_id: Optional[int] = None) -> str:
    """
    Build a kashee:// deep link

    Args:
        action: The action/route (e.g., 'product', 'news', 'feedback')
        item_id: Optional ID for detail pages

    Returns:
        Complete kashee:// URL

    Examples:
        >>> build_scheme_link('home')
        'kashee://home'

        >>> build_scheme_link('product', 123)
        'kashee://product/123'

        >>> build_scheme_link('news', 456)
        'kashee://news/456'
    """
    if item_id is not None:
        return f"{KASHEE_SCHEME}{action}/{item_id}"
    return f"{KASHEE_SCHEME}{action}"


def build_smart_link(target: str, fallback_url: Optional[str] = None) -> str:
    """
    Build a smart link that opens the app or falls back to web/store

    Args:
        target: The kashee:// deep link target
        fallback_url: Optional fallback URL (defaults to home page)

    Returns:
        Complete https://tech.kasheemilk.com:8443/open?target=... URL

    Examples:
        >>> build_smart_link('kashee://product/123')
        'https://tech.kasheemilk.com:8443/open?target=kashee%3A%2F%2Fproduct%2F123'

        >>> build_smart_link('kashee://news/456', 'https://example.com/news/456')
        'https://tech.kasheemilk.com:8443/open?target=kashee%3A%2F%2Fnews%2F456&fallback=https%3A%2F%2Fexample.com%2Fnews%2F456'
    """
    params = {"target": target}
    if fallback_url:
        params["fallback"] = fallback_url

    return f"{WEB_DOMAIN}/open?{urlencode(params)}"


def get_store_link(package_name: str, platform: str = "android") -> str:
    """
    Get Play Store or App Store link

    Args:
        package_name: App package name
        platform: 'android' or 'ios'

    Returns:
        Store URL
    """
    if platform == "ios":
        # Replace with actual App Store IDs
        app_ids = {
            KASHEE_MEMBERS_PACKAGE: "YOUR_APP_STORE_ID_MEMBERS",
            KASHEE_PES_PACKAGE: "YOUR_APP_STORE_ID_PES",
            KASHEE_SAHAYAK_PACKAGE: "YOUR_APP_STORE_ID_SAHAYAK",
        }
        app_id = app_ids.get(package_name, "YOUR_APP_STORE_ID_MEMBERS")
        return f"{APP_STORE_BASE}{app_id}"

    return f"{PLAY_STORE_BASE}{package_name}"
