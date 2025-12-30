# Multi-App Deployment Guide

Complete guide for deploying and managing multiple applications on a single server.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [Adding a New App](#adding-a-new-app)
5. [Removing an App](#removing-an-app)
6. [Managing Apps](#managing-apps)
7. [Configuration](#configuration)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

## Overview

This deployment configuration allows you to run multiple applications on a single server using:
- **Docker Compose** for container orchestration
- **Nginx** as a reverse proxy with path-based routing
- **Shared resources** (PostgreSQL, Redis) for all apps
- **Health checks** and monitoring for all services
- **Resource limits** to prevent resource exhaustion

## Architecture

```
Internet
   ↓
Port 80 (Nginx Reverse Proxy)
   ├── / → consult_frontend:80 (Consult App - Primary)
   ├── /api/ → consult_backend:8000 (Consult App API)
   ├── /admin/ → consult_backend:8000 (Consult App Admin)
   ├── /ws/ → consult_backend:8000 (Consult App WebSocket)
   │
   ├── /app2/ → app2_frontend:80 (App 2 Frontend)
   ├── /app2/api/ → app2_backend:8000 (App 2 API)
   │
   ├── /app3/ → app3_frontend:80 (App 3 Frontend)
   └── /app3/api/ → app3_backend:8000 (App 3 API)
```

### Key Features

- **Path-based routing**: Each app has its own path prefix
- **No port conflicts**: All apps use port 80 through Nginx
- **Shared database**: PostgreSQL shared across all apps
- **Shared cache**: Redis shared across all apps
- **Health monitoring**: All services have health checks
- **Resource limits**: CPU and memory limits per service
- **Rate limiting**: Per-app rate limiting in Nginx

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Server with public IP: `172.104.53.127`
- At least 4GB RAM recommended
- Root or sudo access

### Initial Deployment

1. **Clone and navigate to the repository**
   ```bash
   cd /home/munaim/apps/consult
   ```

2. **Validate environment**
   ```bash
   bash scripts/validate-env.sh
   ```

3. **Deploy all services**
   ```bash
   ./deploy.sh
   ```

4. **Check status**
   ```bash
   bash scripts/manage-apps.sh list
   bash scripts/manage-apps.sh health
   ```

### Access URLs

- **Consult App**: http://172.104.53.127
- **Consult API**: http://172.104.53.127/api/v1/
- **Health Check**: http://172.104.53.127/health

## Adding a New App

### Method 1: Using the Add Script (Recommended)

The easiest way to add a new app is using the automated script:

```bash
./scripts/add-app.sh <app_name> <app_path> [backend_port] [frontend_port]
```

**Example:**
```bash
./scripts/add-app.sh app2 /app2 8000 80
```

This will:
- Add services to `docker-compose.yml`
- Add Nginx configuration
- Add volumes
- Update dependencies
- Validate configurations

**After running the script:**

1. **Create app directory structure**
   ```bash
   mkdir -p app2/{backend,frontend}
   ```

2. **Add your app code**
   - Backend code in `app2/backend/`
   - Frontend code in `app2/frontend/`

3. **Create Dockerfiles**
   - `app2/backend/Dockerfile`
   - `app2/frontend/Dockerfile`

4. **Build and start**
   ```bash
   docker compose build app2_backend app2_frontend
   docker compose up -d app2_backend app2_frontend
   docker compose restart nginx-proxy
   ```

### Method 2: Manual Configuration

If you prefer manual configuration:

1. **Add services to docker-compose.yml**
   - Use template: `templates/docker-compose-app-template.yml`
   - Replace `APP_NAME`, `APP_PATH`, ports, etc.

2. **Add Nginx configuration**
   - Use template: `templates/nginx-app-template.conf`
   - Add rate limiting zones
   - Add upstream definitions
   - Add location blocks

3. **Add volumes**
   - Add static and media volumes for the app

4. **Update nginx-proxy dependencies**
   - Add app services to `depends_on`

5. **Validate and deploy**
   ```bash
   docker compose config
   docker compose up -d
   docker compose restart nginx-proxy
   ```

### App Requirements

Your app must:

1. **Backend Health Check**
   - Implement `/health/` endpoint
   - Return 200 OK when healthy
   - Return 503 when unhealthy

2. **Frontend Health Check**
   - Root path should return 200 OK

3. **Dockerfile**
   - Backend: Expose port (default 8000)
   - Frontend: Expose port (default 80)

4. **Environment Variables**
   - Use shared database: `db:5432`
   - Use shared redis: `redis:6379`
   - Configure CORS/CSRF with server IP

## Removing an App

### Using the Remove Script

```bash
./scripts/remove-app.sh <app_name>
```

**Example:**
```bash
./scripts/remove-app.sh app2
```

This will:
- Stop and remove containers
- Remove from `docker-compose.yml`
- Remove from Nginx configuration
- Validate configurations
- Restart nginx-proxy

**Note:** This does NOT delete:
- App directories
- App volumes (remove manually if needed)

### Manual Removal

1. **Stop and remove containers**
   ```bash
   docker compose stop app2_backend app2_frontend
   docker compose rm -f app2_backend app2_frontend
   ```

2. **Remove from docker-compose.yml**
   - Remove backend service
   - Remove frontend service
   - Remove volumes

3. **Remove from nginx/default.conf**
   - Remove rate limiting zones
   - Remove upstream definitions
   - Remove location blocks

4. **Restart nginx**
   ```bash
   docker compose restart nginx-proxy
   ```

## Managing Apps

### List All Apps

```bash
bash scripts/manage-apps.sh list
```

### Check App Status

```bash
# All apps
bash scripts/manage-apps.sh status

# Specific app
bash scripts/manage-apps.sh status app2_backend
```

### Start/Stop/Restart Apps

```bash
# Start all apps
bash scripts/manage-apps.sh start

# Start specific app
bash scripts/manage-apps.sh start app2_backend app2_frontend

# Stop app
bash scripts/manage-apps.sh stop app2_backend

# Restart app
bash scripts/manage-apps.sh restart app2_backend
```

### View Logs

```bash
# All logs
bash scripts/manage-apps.sh logs

# Specific app
bash scripts/manage-apps.sh logs app2_backend
```

### Health Checks

```bash
# All apps
bash scripts/manage-apps.sh health

# Specific app
bash scripts/manage-apps.sh health app2_backend
```

### Validate Configuration

```bash
bash scripts/manage-apps.sh validate
```

## Configuration

### Environment Variables

Each app can have its own environment variables. Common variables:

```bash
# Database (shared)
DB_HOST=db
DB_PORT=5432
DB_NAME=consult_db
DB_USER=consult_user
DB_PASSWORD=consult_password

# Redis (shared)
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_URL=redis://redis:6379/0

# App-specific
ALLOWED_HOSTS=localhost,127.0.0.1,app2_backend,172.104.53.127
CORS_ALLOWED_ORIGINS=http://172.104.53.127
CSRF_TRUSTED_ORIGINS=http://172.104.53.127
```

### Resource Limits

Default resource limits per app:

**Backend:**
- CPU Limit: 1.0 cores
- Memory Limit: 1GB
- CPU Reservation: 0.5 cores
- Memory Reservation: 512MB

**Frontend:**
- CPU Limit: 1.0 cores
- Memory Limit: 512MB
- CPU Reservation: 0.5 cores
- Memory Reservation: 256MB

Adjust in `docker-compose.yml` under `deploy.resources`.

### Rate Limiting

Default rate limits per app:

- **API**: 100 requests/minute with burst of 20
- **WebSocket**: 10 connections/minute with burst of 5

Adjust in `nginx/default.conf`:

```nginx
limit_req_zone $binary_remote_addr zone=app2_api_limit:10m rate=100r/m;
```

### Nginx Logging

- **Access logs**: `/var/log/nginx/access.log`
- **Error logs**: `/var/log/nginx/error.log`
- **Per-app logs**: `/var/log/nginx/{app}_access.log` (if configured)

View logs:
```bash
docker compose exec nginx-proxy tail -f /var/log/nginx/access.log
```

## Troubleshooting

### App Not Accessible

1. **Check service status**
   ```bash
   docker compose ps
   bash scripts/manage-apps.sh status app2_backend
   ```

2. **Check logs**
   ```bash
   docker compose logs app2_backend
   bash scripts/manage-apps.sh logs app2_backend
   ```

3. **Check Nginx configuration**
   ```bash
   docker compose exec nginx-proxy nginx -t
   ```

4. **Check health**
   ```bash
   curl http://172.104.53.127/app2/api/health/
   bash scripts/manage-apps.sh health app2_backend
   ```

5. **Restart services**
   ```bash
   docker compose restart app2_backend app2_frontend nginx-proxy
   ```

### Port Conflicts

- Ensure all apps use `expose` not `ports` in docker-compose.yml
- Only nginx-proxy should expose port 80
- Check for port conflicts: `netstat -tulpn | grep :80`

### Database Connection Issues

1. **Check database is running**
   ```bash
   docker compose ps db
   ```

2. **Check database health**
   ```bash
   docker compose exec db pg_isready -U consult_user
   ```

3. **Check connection from app**
   ```bash
   docker compose exec app2_backend ping db
   ```

### Nginx Configuration Errors

1. **Test configuration**
   ```bash
   docker compose exec nginx-proxy nginx -t
   ```

2. **Check error logs**
   ```bash
   docker compose logs nginx-proxy
   ```

3. **Reload configuration**
   ```bash
   docker compose exec nginx-proxy nginx -s reload
   ```

### Health Check Failures

1. **Check health endpoint**
   ```bash
   curl http://localhost:8000/health/
   ```

2. **Check from container**
   ```bash
   docker compose exec app2_backend curl http://localhost:8000/health/
   ```

3. **Check health check command**
   - Verify health check URL in docker-compose.yml
   - Ensure health endpoint returns 200 OK

### Resource Exhaustion

1. **Check resource usage**
   ```bash
   docker stats
   ```

2. **Check limits**
   ```bash
   docker inspect app2_backend | grep -A 10 Resources
   ```

3. **Adjust limits** in docker-compose.yml if needed

## Best Practices

### 1. Naming Conventions

- Use lowercase app names: `app2`, `app3`
- Use descriptive paths: `/app2`, `/app3`
- Keep service names consistent: `{app}_backend`, `{app}_frontend`

### 2. Health Checks

- Always implement health check endpoints
- Use meaningful health check responses
- Include database and cache checks in health endpoints

### 3. Resource Management

- Set appropriate resource limits
- Monitor resource usage
- Scale horizontally if needed

### 4. Security

- Use strong secrets
- Configure CORS properly
- Use rate limiting
- Keep images updated

### 5. Logging

- Use structured logging
- Monitor error logs
- Set up log rotation
- Use per-app logs for debugging

### 6. Backup

- Backup database regularly
- Backup volumes if needed
- Keep configuration backups

### 7. Testing

- Test health checks before deployment
- Test Nginx configuration
- Test app isolation
- Test resource limits

## Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Multi-App Deployment Plan](./MULTI_APP_DEPLOYMENT_PLAN.md)
- [Deployment Status](./DEPLOYMENT_STATUS.md)

## Support

For issues or questions:
1. Check troubleshooting section
2. Review logs
3. Validate configuration
4. Check health status

