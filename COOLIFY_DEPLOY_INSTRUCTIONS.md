# Coolify Deployment Instructions - consult.alshifalab.pk

## Domain Configuration
**Domain:** `consult.alshifalab.pk`

## Step-by-Step Deployment

### 1. Access Coolify Dashboard
- Navigate to: `http://your-vps-ip:8000` (or your Coolify URL)
- Login to Coolify

### 2. Create New Resource

1. Click **"New Resource"** or **"+"** button
2. Select **"Docker Compose"** as resource type
3. Configure:
   - **Name:** `consult` or `hospital-consult-system`
   - **Source Type:** 
     - Option A: **Git Repository** (Recommended)
       - Repository: `https://github.com/munaimtahir/consult`
       - Branch: `main` (or your default branch)
     - Option B: **Local Path**
       - Path: `/home/munaim/repos/consult`
   - **Docker Compose File:** `docker-compose.coolify.yml` (or `docker-compose.yml`)

### 3. Configure Domain

1. In the resource settings, go to **"Domains"** section
2. Add domain: `consult.alshifalab.pk`
3. Coolify will automatically:
   - Configure SSL certificate (Let's Encrypt)
   - Set up Traefik routing
   - Enable HTTPS

### 4. Set Environment Variables

Go to **"Environment Variables"** section and add:

```bash
# Django Configuration
SECRET_KEY=062ea43b72adeb8c8b73e691994e25bc18e488406bd50cf4b329134b92ea6c63
DEBUG=0
ALLOWED_HOSTS=consult.alshifalab.pk,localhost,127.0.0.1,backend
DJANGO_SETTINGS_MODULE=config.settings.production

# Database Configuration
DATABASE=postgres
DB_NAME=consult_db
DB_USER=consult_user
DB_PASSWORD=consult_password
DB_HOST=db
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://redis:6379/0
REDIS_HOST=redis
REDIS_PORT=6379

# CORS Configuration
CORS_ALLOWED_ORIGINS=https://consult.alshifalab.pk,http://consult.alshifalab.pk,http://localhost:3000
CSRF_TRUSTED_ORIGINS=https://consult.alshifalab.pk,http://consult.alshifalab.pk,http://localhost:3000

# Frontend Build Configuration
VITE_API_URL=https://consult.alshifalab.pk/api/v1
VITE_WS_URL=wss://consult.alshifalab.pk/ws

# Security Settings (for HTTPS)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SITE_ID=1
```

### 5. Configure Routing in Coolify

Since we're using Nginx reverse proxy, Coolify should route:
- **Domain:** `consult.alshifalab.pk`
- **Target Service:** `nginx-proxy` (port 80)
- **Path:** `/` (all paths)

If using Coolify's Traefik directly (without Nginx):
- Route `/api/` → `backend` service (port 8000)
- Route `/ws/` → `backend` service (WebSocket, port 8000)
- Route `/admin/` → `backend` service (port 8000)
- Route `/static/` → `backend` service (port 8000)
- Route `/media/` → `backend` service (port 8000)
- Route `/` → `frontend` service (port 80)

### 6. Deploy

1. Click **"Deploy"** or **"Start"** button
2. Monitor deployment logs
3. Wait for services to initialize (2-5 minutes)

### 7. Verify Deployment

After deployment, test:

1. **Frontend:** https://consult.alshifalab.pk
2. **Backend Health:** https://consult.alshifalab.pk/api/v1/health/
3. **Django Admin:** https://consult.alshifalab.pk/admin/

Expected health response:
```json
{"status":"healthy","checks":{"database":"ok","cache":"ok"}}
```

## DNS Configuration

Before deployment, ensure DNS is configured:

1. **A Record:**
   - Name: `consult` (or `@` for root)
   - Type: `A`
   - Value: Your VPS IP address
   - TTL: 300 (or default)

2. **CNAME (Alternative):**
   - Name: `consult`
   - Type: `CNAME`
   - Value: `alshifalab.pk` (if using subdomain)

## Post-Deployment

### 1. Verify SSL Certificate
- Coolify should automatically obtain SSL certificate
- Check in Coolify dashboard under "Domains"
- Certificate should be valid and auto-renewing

### 2. Test All Endpoints
```bash
# Frontend
curl https://consult.alshifalab.pk

# Backend API
curl https://consult.alshifalab.pk/api/v1/health/

# WebSocket (test in browser console)
new WebSocket('wss://consult.alshifalab.pk/ws/')
```

### 3. Login and Test
- Use demo credentials from README.md
- Test consult workflow
- Verify WebSocket notifications

## Troubleshooting

### Domain Not Resolving
- Check DNS records
- Wait for DNS propagation (up to 48 hours, usually < 1 hour)
- Verify: `nslookup consult.alshifalab.pk`

### SSL Certificate Issues
- Check domain DNS is pointing to VPS
- Verify port 80 and 443 are open
- Check Coolify logs for Let's Encrypt errors

### Services Not Starting
- Check logs in Coolify dashboard
- Verify environment variables are set correctly
- Check database and Redis connections

### Frontend Not Loading
- Verify `VITE_API_URL` and `VITE_WS_URL` are correct
- Check browser console for errors
- Verify backend is healthy

## Access Points After Deployment

- **Frontend:** https://consult.alshifalab.pk
- **Backend API:** https://consult.alshifalab.pk/api/v1/
- **Django Admin:** https://consult.alshifalab.pk/admin/
- **WebSocket:** wss://consult.alshifalab.pk/ws/

## Default Login Credentials

| Role | Email | Password |
|------|-------|----------|
| **Superuser** | admin@pmc.edu.pk | adminpassword123 |
| **System Admin** | sysadmin@pmc.edu.pk | password123 |

⚠️ **Change passwords in production!**

---

**Status:** Ready for deployment with domain `consult.alshifalab.pk`


