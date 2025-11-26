import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import timedelta

from django.urls import reverse, NoReverseMatch
from django.template import Template, Context, TemplateSyntaxError
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from decouple import config

from member.models import UserDevice
from notifications.model import DeepLink
from util.deeplink_utils import make_json_safe


logger = logging.getLogger(__name__)


@dataclass
class AppConfig:
    """Configuration for each app module."""

    scheme: str
    android_package: str
    ios_bundle_id: str
    default_fallback: str = ""


class DeepLinkRegistry:
    """
    Centralized registry for app configurations.
    Makes it easy to add new apps without modifying core logic.
    """

    _apps: Dict[str, AppConfig] = {}

    @classmethod
    def register(cls, module: str, config: AppConfig):
        """Register a new app configuration."""
        cls._apps[module] = config
        logger.info(f"Registered deep link module: {module}")

    @classmethod
    def get(cls, module: str) -> Optional[AppConfig]:
        """Get app configuration by module name."""
        return cls._apps.get(module)

    @classmethod
    def get_all(cls) -> Dict[str, AppConfig]:
        """Get all registered apps."""
        return cls._apps.copy()

    @classmethod
    def exists(cls, module: str) -> bool:
        """Check if module is registered."""
        return module in cls._apps


# Register default apps
DeepLinkRegistry.register(
    "member",
    AppConfig(
        scheme="kashee-member",
        android_package="com.kasheemilk.kashee",
        ios_bundle_id="com.kasheemilk.kashee.ios",
        default_fallback="https://tech.kasheemilk.com/",
    ),
)

DeepLinkRegistry.register(
    "sahayak",
    AppConfig(
        scheme="kashee-sahayak",
        android_package="com.kasheemilk.kashee_sahayak",
        ios_bundle_id="com.kasheemilk.kashee_sahayak.ios",
        default_fallback="https://tech.kasheemilk.com/",
    ),
)

DeepLinkRegistry.register(
    "pes",
    AppConfig(
        scheme="kashee-pes",
        android_package="com.kasheemilk.pes",
        ios_bundle_id="com.kasheemilk.pes.ios",
        default_fallback="https://tech.kasheemilk.com/",
    ),
)


class DeepLinkError(Exception):
    """Base exception for deep link operations."""

    pass


class InvalidModuleError(DeepLinkError):
    """Raised when an invalid module is specified."""

    pass


class RouteResolutionError(DeepLinkError):
    """Raised when route cannot be resolved."""

    pass


class DeepLinkService:
    """
    Production-ready universal deep link generator.

    Features:
    - Extensible app registry
    - Comprehensive error handling
    - Caching for performance
    - Analytics tracking
    - Link expiry and usage limits
    - Batch operations
    """

    SMART_HOST = config("DEEPLINK_SMART_HOST", "https://tech.kasheemilk.com/open/")

    DEFAULT_EXPIRY_DAYS = config("DEEPLINK_DEFAULT_EXPIRY_DAYS", 30)
    CACHE_TIMEOUT = config("DEEPLINK_CACHE_TIMEOUT", 3600)

    def __init__(self):
        self.registry = DeepLinkRegistry

    # ------------------------
    # New: create DB record and return DeepLink model
    # ------------------------

    def create_notification_deep_link(
        self,
        *,
        user_id: int,
        clean_route: str,
        context: Optional[Dict[str, Any]] = None,
        fallback_url: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> DeepLink:
        """
        Create and return a Notification DeepLink model instance. Does not return the smart URL —
        it returns the actual DB object so callers can inspect token, fields, etc.
        """
        context = context or {}
        meta = meta or {}
        module = self.get_user_module(user_id)

        # Validate module presence in registry
        if not self.registry.exists(module):
            raise InvalidModuleError(f"Module '{module}' not registered")

        app_cfg = self.registry.get(module)

        final_fallback = fallback_url or app_cfg.default_fallback

        # Create DB record atomically
        from notifications.model import DeepLink

        clean_meta = make_json_safe(
            {
                **(meta or {}),
                "context": context,
            }
        )
        if not DeepLinkService.SMART_HOST.endswith("/"):
            link = f"{DeepLinkService.SMART_HOST}/"
        link = f"{DeepLinkService.SMART_HOST}"

        with transaction.atomic():
            dl = DeepLink.objects.create(
                user_id=user_id,
                module=module,
                deep_link=f"{link}{clean_route.lstrip('/')}",
                android_package=getattr(app_cfg, "android_package", ""),
                ios_bundle_id=getattr(app_cfg, "ios_bundle_id", ""),
                fallback_url=final_fallback or "",
                deep_path=f"{app_cfg.scheme}://{clean_route.lstrip('/')}",
                meta=clean_meta,
            )
        logger.info(
            "Created DeepLink record %s for user %s module=%s path=%s",
            dl.token,
            user_id,
            module,
            dl.deep_path,
        )
        return dl

    def create_deep_link_record(
        self,
        *,
        user_id: int,
        module: str,
        clean_route: str,
        url_name: Optional[str] = None,
        route_template: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        fallback_url: Optional[str] = None,
        expires_in_days: Optional[int] = None,
        max_uses: int = 0,
        meta: Optional[Dict[str, Any]] = None,
    ) -> DeepLink:
        """
        Create and return a DeepLink model instance. Does not return the smart URL —
        it returns the actual DB object so callers can inspect token, fields, etc.
        """
        context = context or {}
        meta = meta or {}
        # Auto-detect module if needed
        if module is None:
            module = self.get_user_module(user_id)

        # Validate module presence in registry
        if not self.registry.exists(module):
            raise InvalidModuleError(f"Module '{module}' not registered")

        app_cfg = self.registry.get(module)

        # Determine expiry
        expires_at = None
        if expires_in_days is not None:
            expires_at = timezone.now() + timedelta(days=expires_in_days)
        elif self.DEFAULT_EXPIRY_DAYS:
            expires_at = timezone.now() + timedelta(days=self.DEFAULT_EXPIRY_DAYS)

        final_fallback = fallback_url or app_cfg.default_fallback

        # Create DB record atomically
        from notifications.model import DeepLink

        clean_meta = make_json_safe(
            {
                **(meta or {}),
                "url_name": url_name,
                "route_template": route_template,
                "context": context,
            }
        )

        with transaction.atomic():
            dl = DeepLink.objects.create(
                user_id=user_id,
                module=module,
                deep_link=f"{app_cfg.scheme}://{clean_route.lstrip('/')}",
                android_package=getattr(app_cfg, "android_package", ""),
                ios_bundle_id=getattr(app_cfg, "ios_bundle_id", ""),
                fallback_url=final_fallback or "",
                deep_path=clean_route.lstrip("/"),
                expires_at=expires_at,
                max_uses=max_uses or 0,
                meta=clean_meta,
            )
        logger.info(
            "Created DeepLink record %s for user %s module=%s path=%s",
            dl.token,
            user_id,
            module,
            dl.deep_path,
        )
        return dl

    # ------------------------
    # New: turn a DeepLink instance into a smart URL
    # ------------------------
    def smart_url_for_deeplink(self, dl) -> str:
        """
        Return the smart link wrapper URL for a DeepLink instance (or object with .token).
        """
        token = getattr(dl, "token", None)
        if token is None:
            raise ValueError("Provided object does not have a token attribute")
        # Ensure SMART_HOST ends with slash (or format accordingly)
        if not self.SMART_HOST.endswith("/"):
            return f"{self.SMART_HOST}/?token={token}"
        return f"{self.SMART_HOST}?token={token}"

    # ------------------------
    # Backwards-compatible public API (keeps original generate_deep_link signature)
    # ------------------------
    def generate_deep_link(
        self,
        *,
        user_id: int,
        url_name: Optional[str] = None,
        route_template: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        fallback_url: Optional[str] = None,
        module: Optional[str] = None,
        expires_in_days: Optional[int] = None,
        max_uses: int = 0,
        meta: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Old behavior preserved: returns the smart link URL (string).
        Internally uses create_deep_link_record + smart_url_for_deeplink.
        """
        context = context or {}
        try:
            # Resolve route (existing method)
            route = self.resolve_route(url_name, route_template, context)
            clean_route = route.lstrip("/")

            # Auto-detect module if needed
            if module is None:
                module = self.get_user_module(user_id)

            # Create DB record
            dl = self.create_deep_link_record(
                user_id=user_id,
                module=module,
                clean_route=clean_route,
                url_name=url_name,
                route_template=route_template,
                context=context,
                fallback_url=fallback_url,
                expires_in_days=expires_in_days,
                max_uses=max_uses,
                meta=meta or {},
            )

            # Return smart URL (what callers currently expect)
            return self.smart_url_for_deeplink(dl)

        except Exception as exc:
            logger.error(
                "Error generating deep link for user %s: %s",
                user_id,
                exc,
                exc_info=True,
            )
            raise

    # ---------------------------------------------------------
    # User Module Resolution with Caching
    # ---------------------------------------------------------
    def get_user_module(self, user_id: int) -> str:
        """
        Resolve user's app module with caching.

        Args:
            user_id: User ID to lookup

        Returns:
            Module name (member, sahayak, pes)
        """
        cache_key = f"user_module:{user_id}"
        module = cache.get(cache_key)

        if module is None:
            try:
                device = (
                    UserDevice.objects.filter(user_id=user_id).order_by("-id").first()
                )

                module = device.module if device else "member"

                # Validate module exists
                if not self.registry.exists(module):
                    logger.warning(
                        f"Unknown module '{module}' for user {user_id}, "
                        f"falling back to 'member'"
                    )
                    module = "member"

                cache.set(cache_key, module, self.CACHE_TIMEOUT)

            except Exception as e:
                logger.error(f"Error fetching user module: {e}", exc_info=True)
                module = "member"

        return module

    # ---------------------------------------------------------
    # Route Resolution with Error Handling
    # ---------------------------------------------------------
    def resolve_route(
        self,
        url_name: Optional[str] = None,
        route_template: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Resolve route from URL name or template.

        Args:
            url_name: Django URL name to reverse
            route_template: Django template string
            context: Context data for template/URL params

        Returns:
            Resolved route path

        Raises:
            RouteResolutionError: If route cannot be resolved
        """
        context = context or {}

        if url_name:
            try:
                # Extract URL kwargs from context
                url_kwargs = {
                    k: v
                    for k, v in context.items()
                    if k in ["pk", "id", "slug", "uuid", "object_id"]
                }
                return reverse(url_name, kwargs=url_kwargs)

            except NoReverseMatch as e:
                raise RouteResolutionError(f"Could not reverse URL '{url_name}': {e}")

        if route_template:
            try:
                template = Template(route_template)
                return template.render(Context(context))

            except TemplateSyntaxError as e:
                raise RouteResolutionError(
                    f"Template syntax error in '{route_template}': {e}"
                )
            except Exception as e:
                raise RouteResolutionError(f"Error rendering template: {e}")

        raise RouteResolutionError("Either url_name or route_template must be provided")

    # ---------------------------------------------------------
    # Manual Deep Link Creation
    # ---------------------------------------------------------
    def create_manual_deep_link(
        self,
        *,
        user_id: int,
        module: str,
        path: str,
        fallback_url: Optional[str] = None,
        expires_in_days: Optional[int] = None,
        max_uses: int = 0,
        meta: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create deep link with explicit path.

        Args:
            user_id: User ID
            module: App module name
            path: Deep link path (e.g., "gateway/payment/callback")
            fallback_url: Web fallback URL
            expires_in_days: Days until expiry
            max_uses: Maximum uses
            meta: Additional metadata

        Returns:
            Smart link URL
        """
        meta = meta or {}

        if not self.registry.exists(module):
            logger.warning(f"Module '{module}' not found, using user's module")
            module = self.get_user_module(user_id)

        cfg = self.registry.get(module)

        # Clean path
        clean_path = path.lstrip("/")
        deep_link = f"{cfg.scheme}://{clean_path}"

        # Set expiry
        expires_at = None
        if expires_in_days is not None:
            expires_at = timezone.now() + timedelta(days=expires_in_days)
        elif self.DEFAULT_EXPIRY_DAYS:
            expires_at = timezone.now() + timedelta(days=self.DEFAULT_EXPIRY_DAYS)

        final_fallback = fallback_url or cfg.default_fallback

        dl = DeepLink.objects.create(
            user_id=user_id,
            module=module,
            deep_link=deep_link,
            android_package=cfg.android_package,
            ios_bundle_id=cfg.ios_bundle_id,
            fallback_url=final_fallback,
            deep_path=clean_path,
            expires_at=expires_at,
            max_uses=max_uses,
            meta={**meta, "manual": True},
        )

        logger.info(f"Created manual deep link {dl.token} for {module}:{clean_path}")

        return f"{self.SMART_HOST}{dl.token}"

    # ---------------------------------------------------------
    # Batch Operations
    # ---------------------------------------------------------
    def generate_bulk_deep_links(self, links_config: List[Dict[str, Any]]) -> List[str]:
        """
        Generate multiple deep links in batch.

        Args:
            links_config: List of config dicts for generate_deep_link

        Returns:
            List of generated smart link URLs
        """
        results = []

        for config in links_config:
            try:
                link = self.generate_deep_link(**config)
                results.append(link)
            except Exception as e:
                logger.error(f"Failed to generate link in batch: {e}")
                results.append(None)

        return results

    # ---------------------------------------------------------
    # Link Validation and Retrieval
    # ---------------------------------------------------------
    def validate_and_get_link(self, token: str) -> Optional[DeepLink]:
        """
        Validate and retrieve a deep link by token.

        Args:
            token: UUID token string

        Returns:
            DeepLink instance if valid, None otherwise
        """
        try:
            dl = DeepLink.objects.get(token=token)

            if not dl.is_valid:
                logger.warning(
                    f"Invalid deep link {token}: "
                    f"status={dl.status}, expired={dl.is_expired}, "
                    f"exhausted={dl.is_exhausted}"
                )

                # Update status if needed
                if dl.is_expired and dl.status == DeepLink.Status.ACTIVE:
                    dl.status = DeepLink.Status.EXPIRED
                    dl.save(update_fields=["status"])

                return None

            return dl

        except DeepLink.DoesNotExist:
            logger.warning(f"Deep link not found: {token}")
            return None
        except Exception as e:
            logger.error(f"Error validating deep link: {e}", exc_info=True)
            return None

    # ---------------------------------------------------------
    # Analytics and Cleanup
    # ---------------------------------------------------------
    def get_user_links(
        self, user_id: int, status: Optional[str] = None, limit: int = 100
    ) -> List[DeepLink]:
        """Get all links for a user."""
        qs = DeepLink.objects.filter(user_id=user_id)

        if status:
            qs = qs.filter(status=status)

        return list(qs[:limit])

    def cleanup_expired_links(self, batch_size: int = 1000) -> int:
        """
        Mark expired links as EXPIRED status.

        Returns:
            Number of links updated
        """
        now = timezone.now()
        updated = DeepLink.objects.filter(
            expires_at__lt=now, status=DeepLink.Status.ACTIVE
        )[:batch_size].update(status=DeepLink.Status.EXPIRED)

        logger.info(f"Marked {updated} expired deep links")
        return updated

    # ---------------------------------------------------------
    # Utility Methods
    # ---------------------------------------------------------
    def build_deep_link_url(self, module: str, path: str) -> str:
        """
        Build a raw deep link URL without creating DB record.

        Args:
            module: App module name
            path: Deep link path

        Returns:
            Full deep link URL
        """
        cfg = self.registry.get(module)
        if not cfg:
            cfg = self.registry.get("member")

        return f"{cfg.scheme}://{path.lstrip('/')}"

    def get_module_config(self, module: str) -> Optional[AppConfig]:
        """Get configuration for a specific module."""
        return self.registry.get(module)
