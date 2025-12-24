# Keystone Deployment Guide

## Overview

This application is now fully compatible with Keystone's path-based routing system. Keystone deploys multiple applications on a single VPS using Traefik reverse proxy with path-based routing (e.g., `http://VPS_IP/{APP_SLUG}/`).

## How Keystone Routing Works

1. **Public URL**: Users access your app via `http://VPS_IP/{APP_SLUG}/`
   - Example: `http://1.2.3.4/consult/`

2. **Traefik Path Stripping**: Traefik removes the `{APP_SLUG}` prefix before forwarding to your container
   - Browser request: `http://1.2.3.4/consult/dashboard`
   - Container receives: `/dashboard`

3. **Application Handling**: Your app must:
   - Generate all URLs relative to the app slug
   - Handle cookies scoped to the correct path
   - Configure static/media files with the correct prefix

## Required Environment Variables

### Backend (Django)

```bash
# Path-based routing support
APP_SLUG=consult  # Your app slug (without slashes)

# Host configuration
ALLOWED_HOSTS=VPS_IP,your-domain.com
CORS_ALLOWED_ORIGINS=http://VPS_IP,https://your-domain.com
CSRF_TRUSTED_ORIGINS=http://VPS_IP,https://your-domain.com

# Reverse proxy trust
USE_X_FORWARDED_HOST=True

# Database (shared or dedicated)
DB_NAME=consult_db
DB_USER=consult_user
DB_PASSWORD=your-secure-password
DB_HOST=postgres  # Keystone's shared PostgreSQL service
DB_PORT=5432

# Redis (shared or dedicated)
REDIS_URL=redis://redis:6379/0
REDIS_HOST=redis
REDIS_PORT=6379

# Security
SECRET_KEY=your-very-secure-secret-key
DEBUG=False
```

### Frontend (React/Vite)

Build-time arguments for Docker:

```bash
# App slug for path-based routing
VITE_APP_SLUG=consult

# API endpoint (includes app slug)
VITE_API_URL=http://VPS_IP/consult/api/v1

# WebSocket endpoint (includes app slug)
VITE_WS_URL=ws://VPS_IP/consult/ws
```

## Traefik Labels

Add these labels to your docker-compose.yml services for Keystone deployment:

### Backend Service

```yaml
backend:
  labels:
    - "traefik.enable=true"
    # API routes
    - "traefik.http.routers.consult-api.rule=Host(`VPS_IP`) && PathPrefix(`/consult/api`)"
    - "traefik.http.routers.consult-api.entrypoints=web"
    - "traefik.http.middlewares.consult-api-stripprefix.stripprefix.prefixes=/consult"
    - "traefik.http.routers.consult-api.middlewares=consult-api-stripprefix"
    - "traefik.http.services.consult-api.loadbalancer.server.port=8000"
    
    # WebSocket routes
    - "traefik.http.routers.consult-ws.rule=Host(`VPS_IP`) && PathPrefix(`/consult/ws`)"
    - "traefik.http.routers.consult-ws.entrypoints=web"
    - "traefik.http.middlewares.consult-ws-stripprefix.stripprefix.prefixes=/consult"
    - "traefik.http.routers.consult-ws.middlewares=consult-ws-stripprefix"
    
    # Admin routes
    - "traefik.http.routers.consult-admin.rule=Host(`VPS_IP`) && PathPrefix(`/consult/admin`)"
    - "traefik.http.routers.consult-admin.entrypoints=web"
    - "traefik.http.middlewares.consult-admin-stripprefix.stripprefix.prefixes=/consult"
    - "traefik.http.routers.consult-admin.middlewares=consult-admin-stripprefix"
    
    # Static files
    - "traefik.http.routers.consult-static.rule=Host(`VPS_IP`) && PathPrefix(`/consult/static`)"
    - "traefik.http.routers.consult-static.entrypoints=web"
    - "traefik.http.middlewares.consult-static-stripprefix.stripprefix.prefixes=/consult"
    - "traefik.http.routers.consult-static.middlewares=consult-static-stripprefix"
```

### Frontend Service

```yaml
frontend:
  labels:
    - "traefik.enable=true"
    # Frontend routes (catch-all for SPA)
    - "traefik.http.routers.consult-frontend.rule=Host(`VPS_IP`) && PathPrefix(`/consult`)"
    - "traefik.http.routers.consult-frontend.entrypoints=web"
    - "traefik.http.routers.consult-frontend.priority=1"
    - "traefik.http.services.consult-frontend.loadbalancer.server.port=80"
```

**Note**: The frontend does NOT use stripPrefix middleware because the React app is built with the base path included.

## Docker Compose Configuration

Example for Keystone deployment:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: consult_backend
    command: uvicorn config.asgi:application --host 0.0.0.0 --port 8000
    environment:
      - APP_SLUG=consult
      - DEBUG=False
      - SECRET_KEY=${SECRET_KEY}
      - ALLOWED_HOSTS=${VPS_IP},${DOMAIN}
      - DB_NAME=consult_db
      - DB_USER=consult_user
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=postgres
      - REDIS_URL=redis://redis:6379/0
      - CORS_ALLOWED_ORIGINS=http://${VPS_IP},https://${DOMAIN}
      - CSRF_TRUSTED_ORIGINS=http://${VPS_IP},https://${DOMAIN}
      - USE_X_FORWARDED_HOST=True
    networks:
      - keystone_network
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      args:
        - VITE_APP_SLUG=consult
        - VITE_API_URL=http://${VPS_IP}/consult/api/v1
        - VITE_WS_URL=ws://${VPS_IP}/consult/ws
    container_name: consult_frontend
    networks:
      - keystone_network
    restart: unless-stopped

networks:
  keystone_network:
    external: true
```

## Internal Port

- **Backend**: Port 8000 (internal)
- **Frontend**: Port 80 (internal)

These ports are only used internally within the Docker network. Traefik handles all external routing.

## Static Files Collection

Before deploying, collect Django static files:

```bash
docker-compose exec backend python manage.py collectstatic --noinput
```

This is typically done automatically during container startup via the entrypoint script.

## Deployment Steps

1. **Set Environment Variables**:
   ```bash
   export APP_SLUG=consult
   export VITE_APP_SLUG=consult
   export VPS_IP=1.2.3.4
   export DOMAIN=yourdomain.com
   export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(50))")
   export DB_PASSWORD=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
   ```

2. **Build and Deploy**:
   ```bash
   docker-compose build
   docker-compose up -d
   ```

3. **Verify Deployment**:
   - Open browser: `http://VPS_IP/consult/`
   - Login page should load with correct CSS/JS
   - Navigate to dashboard, consults pages
   - Verify API calls work (check browser network tab)
   - Test WebSocket connection (notifications)
   - Logout and login again

## Troubleshooting

### Issue: Static files not loading (404 errors)

**Cause**: Django STATIC_URL not configured with app slug prefix.

**Solution**: Ensure `APP_SLUG` environment variable is set in backend container.

### Issue: Login redirects to root path `/` instead of `/consult/`

**Cause**: Frontend not configured with correct basename.

**Solution**: Ensure `VITE_APP_SLUG` is passed as build argument to frontend.

### Issue: API calls fail with CORS errors

**Cause**: CORS_ALLOWED_ORIGINS doesn't include the full origin.

**Solution**: Set `CORS_ALLOWED_ORIGINS=http://VPS_IP` (without path).

### Issue: WebSocket connection fails

**Cause**: WebSocket URL not configured correctly or Traefik not stripping prefix.

**Solution**: 
1. Ensure `VITE_WS_URL=ws://VPS_IP/consult/ws`
2. Verify Traefik labels include WebSocket route with stripPrefix middleware

### Issue: CSRF verification failed

**Cause**: CSRF_TRUSTED_ORIGINS not configured correctly.

**Solution**: Set `CSRF_TRUSTED_ORIGINS=http://VPS_IP` (without path).

### Issue: Session/auth cookies not working

**Cause**: Cookie path not set correctly.

**Solution**: Django automatically sets cookie path based on `FORCE_SCRIPT_NAME`. Verify `APP_SLUG` is set.

## Compatibility with Local Development

The application still works at root path `/` for local development:

1. Leave `APP_SLUG` and `VITE_APP_SLUG` empty (or unset)
2. Use standard URLs:
   - `VITE_API_URL=http://localhost:8000/api/v1`
   - `VITE_WS_URL=ws://localhost:8000/ws`

The code automatically detects the configuration and adjusts paths accordingly.

## Security Considerations

1. **HTTPS**: In production with HTTPS, update:
   - `CSRF_COOKIE_SECURE=True`
   - `SESSION_COOKIE_SECURE=True`
   - `SECURE_SSL_REDIRECT=True`

2. **Secret Key**: Always use a strong, unique secret key in production.

3. **Allowed Hosts**: Limit to only your VPS IP and domain.

4. **Database Passwords**: Use strong passwords for database credentials.

5. **CORS Origins**: Only allow trusted origins.

## Testing Keystone Deployment Locally

See [KEYSTONE_TEST_PLAN.md](./KEYSTONE_TEST_PLAN.md) for detailed testing instructions.
