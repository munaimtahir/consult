# Nginx Reverse Proxy Configuration

## Overview

**Yes, we use Nginx reverse proxy** in this deployment. The Nginx service acts as the main entry point and handles all routing between services.

## Architecture

```
Internet → Coolify Traefik → Nginx Reverse Proxy → Backend/Frontend
```

### How It Works

1. **Coolify's Traefik** (external reverse proxy)
   - Handles SSL/TLS termination
   - Routes external traffic to the Nginx service
   - Manages domain routing

2. **Nginx Reverse Proxy** (internal routing)
   - Routes `/api/` → Backend (Django)
   - Routes `/ws/` → Backend (WebSocket)
   - Routes `/static/` → Backend static files
   - Routes `/media/` → Backend media files
   - Routes `/admin/` → Django admin
   - Routes `/` → Frontend (React app)

## Nginx Service Configuration

The Nginx service is defined in `docker-compose.yml`:

```yaml
nginx-proxy:
  image: nginx:alpine
  container_name: consult_nginx
  ports:
    - "80:80"
  volumes:
    - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
    - static_volume:/app/staticfiles:ro
    - media_volume:/app/media:ro
```

## Routing Rules

### API Endpoints
- **Path:** `/api/`
- **Target:** Backend service (port 8000)
- **Rate Limiting:** 100 requests/minute per IP

### WebSocket
- **Path:** `/ws/`
- **Target:** Backend service (port 8000)
- **Rate Limiting:** 10 connections/minute per IP
- **Upgrade:** HTTP to WebSocket

### Static Files
- **Path:** `/static/`
- **Target:** Backend static files volume
- **Cache:** 30 days

### Media Files
- **Path:** `/media/`
- **Target:** Backend media files volume
- **Cache:** 7 days

### Frontend
- **Path:** `/`
- **Target:** Frontend service (port 80)
- **Fallback:** SPA routing (all routes → index.html)

### Django Admin
- **Path:** `/admin/`
- **Target:** Backend service (port 8000)

## Benefits of Using Nginx

1. **Centralized Routing:** All routing logic in one place
2. **Static File Serving:** Efficient serving of static/media files
3. **Rate Limiting:** Protection against abuse
4. **WebSocket Support:** Proper WebSocket proxy configuration
5. **Error Handling:** Custom error pages
6. **Performance:** Efficient reverse proxy with caching

## Configuration Files

- **Nginx Config:** `nginx/default.conf`
- **Error Pages:** `nginx/error-pages/`
- **Docker Compose:** `docker-compose.yml` (nginx-proxy service)

## Alternative: Coolify Traefik Only

If you prefer to use only Coolify's Traefik (without Nginx), you would need to:

1. Remove the `nginx-proxy` service from docker-compose.yml
2. Expose frontend and backend services directly
3. Configure path-based routing in Coolify:
   - `/api/` → Backend service
   - `/ws/` → Backend service (WebSocket)
   - `/` → Frontend service
4. Handle static/media files separately (via backend or CDN)

**However, the current Nginx setup is recommended** because:
- It's already configured and tested
- Handles all edge cases (WebSockets, static files, etc.)
- Simpler Coolify configuration
- Better performance for static files

## Troubleshooting

### Nginx Not Starting
- Check logs: `docker compose logs nginx-proxy`
- Verify `nginx/default.conf` syntax
- Ensure volumes are mounted correctly

### Routes Not Working
- Check Nginx logs for routing errors
- Verify backend/frontend services are healthy
- Test direct service access (bypass Nginx)

### Static Files Not Loading
- Verify `static_volume` is mounted
- Check backend collected static files: `python manage.py collectstatic`
- Verify file permissions

### WebSocket Not Connecting
- Check `/ws/` location block in nginx config
- Verify `proxy_http_version 1.1` and `Upgrade` headers
- Check backend WebSocket configuration

---

**Status:** ✅ Nginx reverse proxy is configured and ready for deployment


