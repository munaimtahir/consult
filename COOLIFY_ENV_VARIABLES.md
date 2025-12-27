# Coolify Environment Variables Reference

Copy these variables to Coolify's environment variables section and replace placeholder values.

## Required Environment Variables

```bash
# Django Configuration
SECRET_KEY=062ea43b72adeb8c8b73e691994e25bc18e488406bd50cf4b329134b92ea6c63
DEBUG=0
ALLOWED_HOSTS=your-domain.com,your-vps-ip,localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=config.settings.production

# Database Configuration
DATABASE=postgres
DB_NAME=consult_db
DB_USER=consult_user
DB_PASSWORD=your-secure-db-password-here
DB_HOST=db
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://redis:6379/0
REDIS_HOST=redis
REDIS_PORT=6379

# CORS Configuration
CORS_ALLOWED_ORIGINS=https://your-domain.com,http://your-vps-ip,http://localhost:3000
CSRF_TRUSTED_ORIGINS=https://your-domain.com,http://your-vps-ip,http://localhost:3000

# Frontend Build Configuration
VITE_API_URL=https://your-domain.com/api/v1
VITE_WS_URL=wss://your-domain.com/ws
```

## Optional Environment Variables

```bash
# Email Configuration
EMAIL_HOST_USER=consult@pmc.edu.pk
EMAIL_HOST_PASSWORD=your_email_password
EMAIL_DOMAIN=pmc.edu.pk

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret
DOMAIN=pmc.edu.pk

# Security Settings (for HTTPS)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SITE_ID=1
```

## Instructions

1. **SECRET_KEY is already configured:**
   - Value: `062ea43b72adeb8c8b73e691994e25bc18e488406bd50cf4b329134b92ea6c63`
   - No need to generate a new one

2. **Replace placeholders:**
   - `your-domain.com` → Your actual domain
   - `your-vps-ip` → Your VPS IP address
   - `your-secure-db-password-here` → Strong database password

3. **For HTTPS deployments:**
   - Use `https://` and `wss://` in URLs
   - Set security flags to `True`

4. **For HTTP deployments:**
   - Use `http://` and `ws://` in URLs
   - Keep security flags as `False`

