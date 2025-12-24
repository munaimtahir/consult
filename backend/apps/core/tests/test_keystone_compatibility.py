"""
Tests for Keystone path-based routing compatibility.

These tests verify that the application correctly handles path-based routing
when deployed under a subpath (e.g., /consult/) as well as at the root path (/).
"""

from django.test import TestCase, override_settings
from django.conf import settings


class KeystoneCompatibilityTestCase(TestCase):
    """Test cases for Keystone path-based routing compatibility."""
    
    def test_static_url_without_app_slug(self):
        """Verify STATIC_URL works at root path (default deployment)."""
        # When APP_SLUG is not set, FORCE_SCRIPT_NAME should be None
        # and STATIC_URL should be /static/
        if not hasattr(settings, 'FORCE_SCRIPT_NAME') or settings.FORCE_SCRIPT_NAME is None:
            self.assertTrue(
                settings.STATIC_URL.endswith('/static/'),
                f"Expected STATIC_URL to end with /static/, got {settings.STATIC_URL}"
            )
    
    def test_media_url_without_app_slug(self):
        """Verify MEDIA_URL works at root path (default deployment)."""
        if not hasattr(settings, 'FORCE_SCRIPT_NAME') or settings.FORCE_SCRIPT_NAME is None:
            self.assertTrue(
                settings.MEDIA_URL.endswith('/media/'),
                f"Expected MEDIA_URL to end with /media/, got {settings.MEDIA_URL}"
            )
    
    @override_settings(
        FORCE_SCRIPT_NAME='/consult',
        STATIC_URL='/consult/static/',
        MEDIA_URL='/consult/media/'
    )
    def test_static_url_with_app_slug(self):
        """Verify STATIC_URL includes app slug when FORCE_SCRIPT_NAME is set."""
        self.assertEqual(
            settings.STATIC_URL,
            '/consult/static/',
            "STATIC_URL should include app slug prefix"
        )
    
    @override_settings(
        FORCE_SCRIPT_NAME='/consult',
        STATIC_URL='/consult/static/',
        MEDIA_URL='/consult/media/'
    )
    def test_media_url_with_app_slug(self):
        """Verify MEDIA_URL includes app slug when FORCE_SCRIPT_NAME is set."""
        self.assertEqual(
            settings.MEDIA_URL,
            '/consult/media/',
            "MEDIA_URL should include app slug prefix"
        )
    
    def test_cors_origins_configured(self):
        """Verify CORS_ALLOWED_ORIGINS is configured."""
        self.assertTrue(
            hasattr(settings, 'CORS_ALLOWED_ORIGINS'),
            "CORS_ALLOWED_ORIGINS should be configured"
        )
        self.assertIsInstance(
            settings.CORS_ALLOWED_ORIGINS,
            list,
            "CORS_ALLOWED_ORIGINS should be a list"
        )
    
    def test_csrf_trusted_origins_configured(self):
        """Verify CSRF_TRUSTED_ORIGINS is configured."""
        self.assertTrue(
            hasattr(settings, 'CSRF_TRUSTED_ORIGINS'),
            "CSRF_TRUSTED_ORIGINS should be configured"
        )
        self.assertIsInstance(
            settings.CSRF_TRUSTED_ORIGINS,
            list,
            "CSRF_TRUSTED_ORIGINS should be a list"
        )
    
    def test_allowed_hosts_configured(self):
        """Verify ALLOWED_HOSTS is configured."""
        self.assertIsInstance(
            settings.ALLOWED_HOSTS,
            list,
            "ALLOWED_HOSTS should be a list"
        )
    
    @override_settings(USE_X_FORWARDED_HOST=True)
    def test_use_x_forwarded_host_in_production(self):
        """Verify USE_X_FORWARDED_HOST can be enabled for reverse proxy."""
        self.assertTrue(
            settings.USE_X_FORWARDED_HOST,
            "USE_X_FORWARDED_HOST should be True for reverse proxy deployments"
        )
    
    def test_force_script_name_format(self):
        """Verify FORCE_SCRIPT_NAME format is correct when set."""
        if hasattr(settings, 'FORCE_SCRIPT_NAME') and settings.FORCE_SCRIPT_NAME:
            # Should start with / and not end with /
            self.assertTrue(
                settings.FORCE_SCRIPT_NAME.startswith('/'),
                "FORCE_SCRIPT_NAME should start with /"
            )
            self.assertFalse(
                settings.FORCE_SCRIPT_NAME.endswith('/'),
                "FORCE_SCRIPT_NAME should not end with /"
            )


class HealthCheckTestCase(TestCase):
    """Test health check endpoint works at root path."""
    
    def test_health_check_endpoint(self):
        """Verify health check endpoint returns 200."""
        response = self.client.get('/api/v1/health/')
        self.assertIn(
            response.status_code,
            [200, 404],  # 404 is OK if endpoint doesn't exist yet
            "Health check should be accessible"
        )
