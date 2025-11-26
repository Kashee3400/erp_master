"""
Comprehensive test suite for deep link system.
"""

import uuid
from datetime import timedelta
from unittest.mock import patch, MagicMock

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.utils import timezone

from notifications.model import DeepLink
from ..deeplink_service import (
    DeepLinkService,
    DeepLinkRegistry,
    AppConfig,
    InvalidModuleError,
    RouteResolutionError,
)
from ..views.deep_link_view import DeepLinkRedirectView


class DeepLinkModelTest(TestCase):
    """Test DeepLink model functionality."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com"
        )

    def test_create_deep_link(self):
        """Test creating a basic deep link."""
        dl = DeepLink.objects.create(
            user=self.user,
            module="member",
            deep_link="kashee-member://products/123",
            deep_path="products/123",
            android_package="com.kasheemilk.kashee",
            ios_bundle_id="com.kasheemilk.kashee.ios",
        )

        self.assertIsNotNone(dl.token)
        self.assertEqual(dl.scheme, "kashee-member")
        self.assertEqual(dl.path, "products/123")
        self.assertTrue(dl.is_valid)

    def test_expired_link(self):
        """Test link expiry detection."""
        dl = DeepLink.objects.create(
            user=self.user,
            module="member",
            deep_link="kashee-member://test",
            android_package="com.kasheemilk.kashee",
            expires_at=timezone.now() - timedelta(days=1),
        )

        self.assertTrue(dl.is_expired)
        self.assertFalse(dl.is_valid)

    def test_max_uses(self):
        """Test max uses enforcement."""
        dl = DeepLink.objects.create(
            user=self.user,
            module="member",
            deep_link="kashee-member://test",
            android_package="com.kasheemilk.kashee",
            max_uses=3,
        )

        # Use it 3 times
        for _ in range(3):
            self.assertTrue(dl.is_valid)
            dl.increment_use()

        # Should be exhausted now
        self.assertTrue(dl.is_exhausted)
        self.assertEqual(dl.status, DeepLink.Status.CONSUMED)
        self.assertFalse(dl.is_valid)

    def test_revoke_link(self):
        """Test manual link revocation."""
        dl = DeepLink.objects.create(
            user=self.user,
            module="member",
            deep_link="kashee-member://test",
            android_package="com.kasheemilk.kashee",
        )

        self.assertTrue(dl.is_valid)

        dl.revoke()

        self.assertEqual(dl.status, DeepLink.Status.REVOKED)
        self.assertFalse(dl.is_valid)

    def test_extend_expiry(self):
        """Test expiry extension."""
        original_expiry = timezone.now() + timedelta(days=7)
        dl = DeepLink.objects.create(
            user=self.user,
            module="member",
            deep_link="kashee-member://test",
            android_package="com.kasheemilk.kashee",
            expires_at=original_expiry,
        )

        dl.extend_expiry(days=7)

        self.assertGreater(dl.expires_at, original_expiry)


class DeepLinkServiceTest(TestCase):
    """Test DeepLinkService functionality."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com"
        )
        self.service = DeepLinkService()

    @patch("member.models.UserDevice.objects.filter")
    def test_get_user_module(self, mock_filter):
        """Test user module resolution."""
        mock_device = MagicMock()
        mock_device.module = "sahayak"
        mock_filter.return_value.order_by.return_value.first.return_value = mock_device

        module = self.service.get_user_module(self.user.id)

        self.assertEqual(module, "sahayak")

    @patch("member.models.UserDevice.objects.filter")
    def test_get_user_module_fallback(self, mock_filter):
        """Test fallback to member when no device found."""
        mock_filter.return_value.order_by.return_value.first.return_value = None

        module = self.service.get_user_module(self.user.id)

        self.assertEqual(module, "member")

    def test_resolve_route_with_url_name(self):
        """Test route resolution with URL name."""
        # This would need actual URL configuration
        # Just testing the structure
        context = {"pk": 123}

        with self.assertRaises(RouteResolutionError):
            # Will fail without proper URL config
            self.service.resolve_route(url_name="nonexistent-url", context=context)

    def test_resolve_route_with_template(self):
        """Test route resolution with template."""
        route = self.service.resolve_route(
            route_template="products/{{ product_id }}/details",
            context={"product_id": 123},
        )

        self.assertEqual(route, "products/123/details")

    def test_resolve_route_no_input(self):
        """Test route resolution fails without input."""
        with self.assertRaises(RouteResolutionError):
            self.service.resolve_route(context={})

    def test_generate_deep_link(self):
        """Test full deep link generation."""
        link = self.service.generate_deep_link(
            user_id=self.user.id,
            route_template="products/{{ id }}",
            context={"id": 123},
            module="member",
            expires_in_days=7,
            max_uses=5,
        )

        self.assertTrue(link.startswith(self.service.SMART_HOST))

        # Extract token and verify
        token = link.split("token=")[-1]
        dl = DeepLink.objects.get(token=token)

        self.assertEqual(dl.user_id, self.user.id)
        self.assertEqual(dl.module, "member")
        self.assertEqual(dl.max_uses, 5)
        self.assertIsNotNone(dl.expires_at)

    def test_invalid_module_error(self):

        """Test error on invalid module."""
        with self.assertRaises(InvalidModuleError):
            self.service.generate_deep_link(
                user_id=self.user.id,
                route_template="test",
                context={},
                module="invalid-module",
            )

    def test_create_manual_deep_link(self):
        """Test manual deep link creation."""
        link = self.service.create_manual_deep_link(
            user_id=self.user.id,
            module="sahayak",
            path="gateway/payment/callback",
            expires_in_days=1,
        )

        token = link.split("token=")[-1]
        dl = DeepLink.objects.get(token=token)

        self.assertEqual(dl.module, "sahayak")
        self.assertIn("kashee-sahayak://", dl.deep_link)
        self.assertEqual(dl.deep_path, "gateway/payment/callback")

    def test_bulk_generation(self):
        """Test bulk link generation."""
        configs = [
            {
                "user_id": self.user.id,
                "route_template": "product/{{ id }}",
                "context": {"id": i},
                "module": "member",
            }
            for i in range(5)
        ]

        links = self.service.generate_bulk_deep_links(configs)

        self.assertEqual(len(links), 5)
        self.assertTrue(all(link is not None for link in links))

    def test_validate_and_get_link(self):
        """Test link validation."""
        dl = DeepLink.objects.create(
            user=self.user,
            module="member",
            deep_link="kashee-member://test",
            android_package="com.kasheemilk.kashee",
        )

        # Valid link
        result = self.service.validate_and_get_link(str(dl.token))
        self.assertIsNotNone(result)
        self.assertEqual(result.id, dl.id)

        # Invalid token
        result = self.service.validate_and_get_link(str(uuid.uuid4()))
        self.assertIsNone(result)

        # Expired link
        dl.expires_at = timezone.now() - timedelta(days=1)
        dl.save()
        result = self.service.validate_and_get_link(str(dl.token))
        self.assertIsNone(result)


class DeepLinkViewTest(TestCase):
    """Test deep link redirect views."""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com"
        )
        self.view = DeepLinkRedirectView.as_view()

    def test_android_redirect(self):
        """Test Android intent URL generation."""
        dl = DeepLink.objects.create(
            user=self.user,
            module="member",
            deep_link="kashee-member://products/123",
            deep_path="products/123",
            android_package="com.kasheemilk.kashee",
            fallback_url="https://kmpcl.netlify.app",
        )

        request = self.factory.get(f"/open?token={dl.token}")
        request.META["HTTP_USER_AGENT"] = "Android"

        response = self.view(request)

        self.assertEqual(response.status_code, 302)
        self.assertIn("intent://", response.url)
        self.assertIn("com.kasheemilk.kashee", response.url)

    def test_invalid_token_handling(self):
        """Test handling of invalid tokens."""
        request = self.factory.get("/open?token=invalid-token")

        response = self.view(request)

        self.assertEqual(response.status_code, 404)

    def test_missing_token(self):
        """Test handling of missing token."""
        request = self.factory.get("/open")

        response = self.view(request)

        self.assertEqual(response.status_code, 400)

    def test_link_usage_tracking(self):
        """Test that link usage is tracked."""
        dl = DeepLink.objects.create(
            user=self.user,
            module="member",
            deep_link="kashee-member://test",
            android_package="com.kasheemilk.kashee",
        )

        initial_count = dl.use_count

        request = self.factory.get(f"/open?token={dl.token}")
        request.META["HTTP_USER_AGENT"] = "Android"

        self.view(request)

        dl.refresh_from_db()
        self.assertEqual(dl.use_count, initial_count + 1)
        self.assertIsNotNone(dl.last_accessed_at)


class DeepLinkRegistryTest(TestCase):
    """Test app registry functionality."""

    def test_register_app(self):
        """Test registering a new app."""
        config = AppConfig(
            scheme="test-app",
            android_package="com.test.app",
            ios_bundle_id="com.test.app.ios",
        )

        DeepLinkRegistry.register("test", config)

        self.assertTrue(DeepLinkRegistry.exists("test"))
        retrieved = DeepLinkRegistry.get("test")
        self.assertEqual(retrieved.scheme, "test-app")

    def test_get_nonexistent_app(self):
        """Test getting non-existent app returns None."""
        result = DeepLinkRegistry.get("nonexistent")
        self.assertIsNone(result)
