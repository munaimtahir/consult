# Multi-App Deployment Configuration Plan

## Overview

This document outlines the comprehensive plan for configuring the server to support multiple applications simultaneously using Docker Compose and Nginx reverse proxy.

## Objectives

1. **Path-Based Routing**: All apps accessible through a single domain/IP using path-based routing
2. **No Port Conflicts**: All apps use port 80 through Nginx proxy
3. **Scalability**: Easy to add new apps without modifying existing configurations
4. **Health Monitoring**: Health checks for all services
5. **Resource Management**: Proper resource limits and isolation
6. **Documentation**: Clear guide for adding new apps

## Architecture

```
Internet
   ↓
Port 80 (Nginx Reverse Proxy)
   ├── /api/ → consult_backend:8000 (Consult App)
   ├── /admin/ → consult_backend:8000 (Consult App)
   ├── /ws/ → consult_backend:8000 (Consult App WebSocket)
   ├── /static/ → Static files (Consult App)
   ├── /media/ → Media files (Consult App)
   ├── / → consult_frontend:80 (Consult App Frontend)
   │
   ├── /app2/ → app2_backend:8000 (Future App 2)
   ├── /app2/api/ → app2_backend:8000 (Future App 2 API)
   └── /app3/ → app3_frontend:80 (Future App 3)
```

## Implementation Tasks

### Task 1: Create Comprehensive Multi-App Deployment Configuration Plan Document
- [x] Document architecture and objectives
- [x] Define routing strategy
- [x] Outline implementation tasks

### Task 2: Enhance Nginx Configuration
- [ ] Add health check endpoints
- [ ] Implement proper load balancing (if needed)
- [ ] Add rate limiting per app
- [ ] Configure SSL/TLS termination (future)
- [ ] Add request logging per app
- [ ] Implement proper error pages

### Task 3: Update Docker Compose Configuration
- [ ] Add health checks for all services
- [ ] Implement resource limits (CPU, memory)
- [ ] Add restart policies
- [ ] Configure logging drivers
- [ ] Set up proper network isolation
- [ ] Add environment variable templates

### Task 4: Create App Configuration Template
- [ ] Create template for new app services
- [ ] Document required configuration steps
- [ ] Create example app configuration
- [ ] Add validation scripts

### Task 5: Environment Variable Management
- [ ] Create centralized env file structure
- [ ] Document required variables per app
- [ ] Add validation for required variables
- [ ] Create example .env files

### Task 6: Health Check and Monitoring
- [ ] Add health check endpoints to backend
- [ ] Configure Nginx health check routes
- [ ] Set up service dependency management
- [ ] Add monitoring/logging configuration

### Task 7: Deployment Scripts
- [ ] Create script to add new app
- [ ] Create script to remove app
- [ ] Create script to list all apps
- [ ] Create script to check app health
- [ ] Update main deployment script

### Task 8: Documentation
- [ ] Create multi-app deployment guide
- [ ] Document adding new app process
- [ ] Create troubleshooting guide
- [ ] Update main README

## Current Apps

### Consult App (Primary)
- **Path**: `/` (root), `/api/`, `/admin/`, `/ws/`
- **Backend**: `backend:8000`
- **Frontend**: `frontend:80`
- **Status**: ✅ Active

## Adding New Apps

### Quick Method (Recommended)

Use the automated script:

```bash
./scripts/add-app.sh <app_name> <app_path> [backend_port] [frontend_port]
```

**Example:**
```bash
./scripts/add-app.sh app2 /app2 8000 80
```

Then create your app directories and code, build, and deploy.

### Manual Method

See [MULTI_APP_DEPLOYMENT_GUIDE.md](./MULTI_APP_DEPLOYMENT_GUIDE.md) for detailed manual instructions.

**Templates available:**
- `templates/docker-compose-app-template.yml` - Docker Compose service template
- `templates/nginx-app-template.conf` - Nginx configuration template
- `templates/env-app-template.example` - Environment variables template

## Health Checks

All services should implement health check endpoints:
- Backend: `/health/` or `/api/health/`
- Frontend: Root path should return 200 OK

## Resource Limits

Each app should have resource limits:
```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 512M
```

## Network Isolation

- All apps share the same Docker network (`consult_network`)
- Apps can communicate with each other using service names
- External access only through Nginx proxy

## Security Considerations

1. **CORS**: Configure per app in backend settings
2. **CSRF**: Configure trusted origins per app
3. **Rate Limiting**: Implement per app in Nginx
4. **Authentication**: Each app handles its own auth
5. **SSL/TLS**: Configure at Nginx level (future)

## Monitoring and Logging

- All services log to stdout/stderr
- Docker Compose collects logs
- Nginx access logs per app location
- Health check logs

## Troubleshooting

### App not accessible
1. Check service status: `docker compose ps`
2. Check logs: `docker compose logs app_name`
3. Check Nginx config: `docker compose exec nginx-proxy nginx -t`
4. Verify health checks: `curl http://localhost/health/`

### Port conflicts
- Ensure all apps use `expose` not `ports`
- Only Nginx should expose port 80

### Service dependencies
- Use `depends_on` with health checks
- Ensure database/redis are healthy before starting apps

## Future Enhancements

1. **SSL/TLS Support**: Add Let's Encrypt integration
2. **Load Balancing**: Multiple backend instances per app
3. **Auto-scaling**: Based on load metrics
4. **Service Discovery**: Dynamic app registration
5. **API Gateway**: Centralized API management
6. **Monitoring Dashboard**: Grafana/Prometheus integration

## Notes

- This configuration supports horizontal scaling
- New apps can be added without downtime
- Each app maintains independence
- Shared resources (DB, Redis) can be used by multiple apps
