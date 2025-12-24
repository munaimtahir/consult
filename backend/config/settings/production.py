"""
Production settings for Hospital Consult System.
Uses PostgreSQL and proper security settings.
"""

from .base import *

# Debug mode - MUST be False in production
DEBUG = False

# Database - PostgreSQL for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,  # Connection pooling
    }
}

# Keystone Compatibility: Reverse proxy settings
# Trust X-Forwarded-Host header from reverse proxy (Traefik/Nginx)
USE_X_FORWARDED_HOST = config('USE_X_FORWARDED_HOST', default=True, cast=bool)

# Trust X-Forwarded-Proto header for HTTPS detection behind reverse proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookie path configuration for subpath deployments
# When APP_SLUG is set, cookies are scoped to that path
SESSION_COOKIE_PATH = FORCE_SCRIPT_NAME or '/'
CSRF_COOKIE_PATH = FORCE_SCRIPT_NAME or '/'

# Security settings - Set based on environment
# In Docker behind reverse proxy, disable SSL redirect
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'

# HSTS settings - Enable only when using HTTPS
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
SECURE_HSTS_PRELOAD = SECURE_HSTS_SECONDS > 0

# Email verification - optional for dev deployments
ACCOUNT_EMAIL_VERIFICATION = config('ACCOUNT_EMAIL_VERIFICATION', default='optional')

# Logging - File-based in production
LOGGING['handlers']['file']['filename'] = config('LOG_FILE', default='/var/log/consult/django.log')
