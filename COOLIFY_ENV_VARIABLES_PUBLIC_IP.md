# Coolify Environment Variables Reference (Public IP)

Complete reference for environment variables used in Coolify deployment with public IP configuration.

## Public IP Configuration

- **Public VPS IP**: `34.124.150.231`
- **Domain**: `consult.alshifalab.pk`
- **Coolify Dashboard**: `http://34.124.150.231:8000`

## Required Environment Variables

### Django Configuration

```bash
# Secret key (already configured)
SECRET_KEY=062ea43b72adeb8c8b73e691994e25bc18e488406bd50cf4b329134b92ea6c63

# Debug mode (disabled for production)
DEBUG=0

# Allowed hosts (includes domain and public IP)
ALLOWED_HOSTS=consult.alshifalab.pk,34.124.150.231,localhost,127.0.0.1,backend

# Django settings module
DJANGO_SETTINGS_MODULE=config.settings.production
```

### Database Configuration

```bash
# Database type
DATABASE=postgres

# Database name
DB_NAME=consult_db

# Database user
DB_USER=consult_user

# Database password (change in production!)
DB_PASSWORD=consult_password

# Database host (service name in Docker Compose)
DB_HOST=db

# Database port
DB_PORT=5432
```

### Redis Configuration

```bash
# Redis URL
REDIS_URL=redis://redis:6379/0

# Redis host (service name in Docker Compose)
REDIS_HOST=redis

# Redis port
REDIS_PORT=6379
```

### CORS Configuration

```bash
# CORS allowed origins (includes domain and public IP)
CORS_ALLOWED_ORIGINS=https://consult.alshifalab.pk,http://consult.alshifalab.pk,http://34.124.150.231,http://34.124.150.231:3000

# CSRF trusted origins (includes domain and public IP)
CSRF_TRUSTED_ORIGINS=https://consult.alshifalab.pk,http://consult.alshifalab.pk,http://34.124.150.231,http://34.124.150.231:3000
```

### Frontend Build Configuration

```bash
# API URL for frontend (uses domain with HTTPS)
VITE_API_URL=https://consult.alshifalab.pk/api/v1

# WebSocket URL for frontend (uses domain with WSS)
VITE_WS_URL=wss://consult.alshifalab.pk/ws
```

**Note**: These are build-time variables. The frontend is built with these URLs baked in.

### Security Settings (HTTPS)

```bash
# Force SSL redirect
SECURE_SSL_REDIRECT=True

# Secure session cookies
SESSION_COOKIE_SECURE=True

# Secure CSRF cookies
CSRF_COOKIE_SECURE=True

# HSTS seconds (1 year)
SECURE_HSTS_SECONDS=31536000

# Site ID
SITE_ID=1
```

## Optional Environment Variables

### Email Configuration

```bash
# Email host user
EMAIL_HOST_USER=consult@pmc.edu.pk

# Email host password
EMAIL_HOST_PASSWORD=your_email_password

# Email domain
EMAIL_DOMAIN=pmc.edu.pk
```

### Google OAuth

```bash
# Google OAuth client ID
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id

# Google OAuth client secret
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret

# Domain for OAuth
DOMAIN=pmc.edu.pk
```

## Environment Variable Usage

### In Docker Compose

Environment variables are passed to containers via the `environment` section in `docker-compose.coolify.yml`:

```yaml
environment:
  - SECRET_KEY=${SECRET_KEY}
  - ALLOWED_HOSTS=${ALLOWED_HOSTS}
  - DB_PASSWORD=${DB_PASSWORD}
  # ... etc
```

### In Coolify

1. Navigate to your application in Coolify dashboard
2. Go to "Environment Variables" or "Secrets" section
3. Add each variable from `coolify-deploy.env`
4. Or use the deployment script which sets them automatically

## Important Notes

### Public IP vs Domain

- **Domain** (`consult.alshifalab.pk`): Preferred for production, supports SSL/HTTPS
- **Public IP** (`34.124.150.231`): Fallback, useful for testing before DNS propagates

Both are included in:
- `ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
- `CSRF_TRUSTED_ORIGINS`

### Security

- **SECRET_KEY**: Already configured, but should be rotated in production
- **DB_PASSWORD**: Currently `consult_password`, change to strong password
- **HTTPS**: Enabled via `SECURE_SSL_REDIRECT=True` and SSL settings

### Build-Time vs Runtime Variables

- **VITE_API_URL** and **VITE_WS_URL**: Build-time variables, baked into frontend during build
- **Other variables**: Runtime variables, can be changed without rebuilding

## Verification

After setting environment variables, verify they're applied:

```bash
# Check in Coolify dashboard
# Or via API:
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://34.124.150.231:8000/api/v1/applications/{app_uuid}/environment-variables
```

## File Locations

- **Source**: `coolify-deploy.env` - Contains all variables
- **Template**: `coolify-api-config.env.example` - Template for API config
- **Config**: `coolify-api-config.env` - API configuration

## Quick Reference

| Variable | Value | Purpose |
|----------|-------|---------|
| `ALLOWED_HOSTS` | `consult.alshifalab.pk,34.124.150.231,...` | Django allowed hosts |
| `CORS_ALLOWED_ORIGINS` | `https://consult.alshifalab.pk,http://34.124.150.231,...` | CORS configuration |
| `VITE_API_URL` | `https://consult.alshifalab.pk/api/v1` | Frontend API URL |
| `VITE_WS_URL` | `wss://consult.alshifalab.pk/ws` | Frontend WebSocket URL |
| `DB_PASSWORD` | `consult_password` | Database password |
| `SECRET_KEY` | `062ea43b72adeb8c8b73e691994e25bc18e488406bd50cf4b329134b92ea6c63` | Django secret key |

---

**Last Updated**: 2024-12-28
**Public IP**: 34.124.150.231
**Domain**: consult.alshifalab.pk

