# Guide: Adding a New App to Multi-App Deployment

This guide explains how to add a new application to the existing multi-app deployment configuration.

## Prerequisites

- Docker and Docker Compose installed
- Access to the server
- New app code ready in a directory

## Step-by-Step Instructions

### Step 1: Prepare Your App Directory

Create a directory structure for your new app:

```bash
mkdir -p /workspace/app2/{backend,frontend}
```

Your app should have:
- Backend service (if applicable)
- Frontend service (if applicable)
- Dockerfile(s) for building images

### Step 2: Add Service to docker-compose.yml

Add your app's services to `docker-compose.yml`. Use this template:

```yaml
# App2 - Backend Service
app2_backend:
  build: ./app2/backend
  expose:
    - "8000"
  environment:
    - APP_NAME=app2
    - DB_HOST=db
    - DB_NAME=app2_db  # Or use shared DB
    - DB_USER=consult_user
    - DB_PASSWORD=consult_password
    - REDIS_HOST=redis
    - REDIS_URL=redis://redis:6379/1  # Use different DB number
    - ALLOWED_HOSTS=localhost,127.0.0.1,app2_backend,172.104.53.127
    - CORS_ALLOWED_ORIGINS=http://172.104.53.127
    - CSRF_TRUSTED_ORIGINS=http://172.104.53.127
  depends_on:
    db:
      condition: service_healthy
    redis:
      condition: service_healthy
  networks:
    - consult_network
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s
  restart: unless-stopped
  logging:
    driver: "json-file"
    options:
      max-size: "10m"
      max-file: "3"
  deploy:
    resources:
      limits:
        cpus: '1.0'
        memory: 1G
      reservations:
        cpus: '0.5'
        memory: 512M

# App2 - Frontend Service
app2_frontend:
  build:
    context: ./app2/frontend
    args:
      - VITE_API_URL=http://172.104.53.127/app2/api/v1
  expose:
    - "80"
  depends_on:
    app2_backend:
      condition: service_healthy
  networks:
    - consult_network
  healthcheck:
    test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:80/"]
    interval: 30s
    timeout: 10s
    retries: 3
  restart: unless-stopped
  deploy:
    resources:
      limits:
        cpus: '0.5'
        memory: 512M
```

### Step 3: Configure Nginx Routing

Add location blocks to `nginx/default.conf`:

```nginx
# Rate limiting for app2
limit_req_zone $binary_remote_addr zone=app2_api_limit:10m rate=100r/m;

# Upstream for app2 backend
upstream app2_backend {
    server app2_backend:8000 max_fails=3 fail_timeout=30s;
}

upstream app2_frontend {
    server app2_frontend:80 max_fails=3 fail_timeout=30s;
}

# Add to existing server block:
server {
    listen 80;
    server_name 172.104.53.127 _;
    
    # ... existing locations ...
    
    # App2 - Health check
    location /app2/api/health/ {
        proxy_pass http://app2_backend;
        proxy_set_header Host $host;
        access_log off;
    }
    
    # App2 - API endpoints
    location /app2/api/ {
        limit_req zone=app2_api_limit burst=20 nodelay;
        proxy_pass http://app2_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;
    }
    
    # App2 - Frontend
    location /app2/ {
        proxy_pass http://app2_frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Step 4: Implement Health Check Endpoint

Your backend must implement a health check endpoint:

**Django Example:**
```python
# app2/backend/apps/core/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_GET

@require_GET
def health_check(request):
    return JsonResponse({"status": "healthy"}, status=200)
```

**FastAPI Example:**
```python
# app2/backend/main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/health/")
def health_check():
    return {"status": "healthy"}
```

### Step 5: Update Environment Variables

If your app needs specific environment variables:

1. Add them to `docker-compose.yml` under your service's `environment` section
2. Document them in `.env.example` (if using shared env file)
3. Update `MULTI_APP_DEPLOYMENT_PLAN.md` with your app's requirements

### Step 6: Test Configuration

1. **Validate Nginx config:**
   ```bash
   docker compose exec nginx-proxy nginx -t
   ```

2. **Start your app:**
   ```bash
   docker compose up -d app2_backend app2_frontend
   ```

3. **Check health:**
   ```bash
   curl http://172.104.53.127/app2/api/health/
   ```

4. **Restart Nginx:**
   ```bash
   docker compose restart nginx-proxy
   ```

5. **Verify access:**
   ```bash
   curl http://172.104.53.127/app2/
   ```

### Step 7: Update Documentation

1. Add your app to `MULTI_APP_DEPLOYMENT_PLAN.md` under "Current Apps"
2. Update `DEPLOYMENT_STATUS.md` with your app's URLs
3. Add any app-specific notes to `README.md`

## Path Naming Conventions

- Use lowercase with underscores: `app2`, `patient_portal`, `admin_dashboard`
- Keep paths short but descriptive
- Avoid conflicts with existing paths:
  - Reserved: `/api/`, `/admin/`, `/ws/`, `/static/`, `/media/`, `/health`
  - Use: `/app2/`, `/portal/`, `/dashboard/`

## Database Strategy

You have two options:

1. **Shared Database** (Recommended for related apps):
   - Use existing `db` service
   - Use different database name: `DB_NAME=app2_db`
   - Share connection pool

2. **Separate Database**:
   - Add new `app2_db` service to docker-compose.yml
   - Configure separate connection
   - More isolation but more resources

## Resource Allocation

Default resource limits per app:
- **Backend**: 1 CPU, 1GB RAM (limit), 0.5 CPU, 512MB RAM (reservation)
- **Frontend**: 0.5 CPU, 512MB RAM (limit), 0.25 CPU, 256MB RAM (reservation)

Adjust based on your app's needs.

## Troubleshooting

### App not accessible
- Check service status: `docker compose ps app2_backend`
- Check logs: `docker compose logs app2_backend`
- Verify Nginx config: `docker compose exec nginx-proxy nginx -t`
- Check health: `curl http://localhost/app2/api/health/`

### Port conflicts
- Ensure all apps use `expose` not `ports`
- Only Nginx should expose port 80

### Database connection issues
- Verify database is healthy: `docker compose ps db`
- Check connection string in environment variables
- Verify network: `docker network inspect consult_consult_network`

### Nginx routing issues
- Check location block order (more specific paths first)
- Verify proxy_pass URL matches upstream name
- Check proxy headers are set correctly

## Example: Complete App Configuration

See `docs/app2_example/` for a complete example app configuration.

## Next Steps

After adding your app:
1. Test all endpoints
2. Monitor resource usage
3. Set up monitoring/alerts
4. Document app-specific requirements
5. Update deployment scripts if needed
