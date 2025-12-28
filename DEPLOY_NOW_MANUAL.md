# Quick Manual Deployment Guide

Since the Coolify API structure may vary, here's the quickest way to deploy manually via the Coolify dashboard.

## Step-by-Step Manual Deployment

### 1. Access Coolify Dashboard
- Open: `http://34.124.150.231:8000`
- Login to your Coolify instance

### 2. Navigate to Project
- Go to project: **FMU** (UUID: `ewsc80ck8scc8sw8s4ksc08g`)
- Select environment: **production** (UUID: `fcs8ssg8w4gwck00gkgwsgck`)

### 3. Create New Application
- Click **"+ New"** or **"New Resource"**
- Select **"Docker Compose"** as resource type

### 4. Configure Application

**Basic Settings:**
- **Name**: `consult`
- **Description**: `Hospital Consult System`

**Source Configuration:**
- **Source Type**: `Git Repository`
- **Repository**: `https://github.com/munaimtahir/consult`
- **Branch**: `main`
- **Docker Compose File**: `docker-compose.coolify.yml`

**Server/Destination:**
- **Server**: `localhost` (or select your server)

### 5. Add Environment Variables

Go to **"Environment Variables"** or **"Secrets"** section and add all variables from `coolify-deploy.env`:

```bash
SECRET_KEY=062ea43b72adeb8c8b73e691994e25bc18e488406bd50cf4b329134b92ea6c63
DEBUG=0
ALLOWED_HOSTS=consult.alshifalab.pk,34.124.150.231,localhost,127.0.0.1,backend
DJANGO_SETTINGS_MODULE=config.settings.production
DATABASE=postgres
DB_NAME=consult_db
DB_USER=consult_user
DB_PASSWORD=consult_password
DB_HOST=db
DB_PORT=5432
REDIS_URL=redis://redis:6379/0
REDIS_HOST=redis
REDIS_PORT=6379
CORS_ALLOWED_ORIGINS=https://consult.alshifalab.pk,http://consult.alshifalab.pk,http://34.124.150.231,http://34.124.150.231:3000
CSRF_TRUSTED_ORIGINS=https://consult.alshifalab.pk,http://consult.alshifalab.pk,http://34.124.150.231,http://34.124.150.231:3000
VITE_API_URL=https://consult.alshifalab.pk/api/v1
VITE_WS_URL=wss://consult.alshifalab.pk/ws
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SITE_ID=1
```

### 6. Configure Domain

- Go to **"Domains"** section
- Click **"Add Domain"**
- Enter: `consult.alshifalab.pk`
- Enable **SSL/HTTPS** (Let's Encrypt will auto-configure)
- Enable **Force HTTPS**

### 7. Deploy

- Click **"Deploy"** or **"Start"** button
- Monitor the deployment logs
- Wait for services to initialize (2-5 minutes)

### 8. Verify Deployment

After deployment completes:

```bash
# Check health endpoint
curl https://consult.alshifalab.pk/api/v1/health/
# Expected: {"status":"healthy","checks":{"database":"ok","cache":"ok"}}

# Check frontend
curl -I https://consult.alshifalab.pk
# Expected: HTTP 200

# Check via public IP (if domain not ready)
curl http://34.124.150.231/api/v1/health/
```

## Access Points After Deployment

- **Frontend**: https://consult.alshifalab.pk
- **Backend API**: https://consult.alshifalab.pk/api/v1/
- **Django Admin**: https://consult.alshifalab.pk/admin/
- **WebSocket**: wss://consult.alshifalab.pk/ws/
- **Coolify Dashboard**: http://34.124.150.231:8000

## Troubleshooting

### If Deployment Fails

1. **Check Logs**: View application logs in Coolify dashboard
2. **Verify Git Access**: Ensure Coolify can access GitHub repository
3. **Check Resources**: Verify VPS has sufficient CPU/RAM
4. **Environment Variables**: Double-check all variables are set correctly

### If Domain Not Working

1. **DNS Check**: `nslookup consult.alshifalab.pk` (should return `34.124.150.231`)
2. **SSL Certificate**: Check SSL status in Coolify dashboard
3. **Ports**: Verify ports 80 and 443 are open
4. **Wait**: DNS and SSL setup can take 5-60 minutes

### If Services Not Healthy

1. **Database**: Check database container logs
2. **Backend**: Check backend container logs for errors
3. **Frontend**: Verify `VITE_API_URL` and `VITE_WS_URL` are correct
4. **Redis**: Check Redis container is running

## Quick Copy-Paste Commands

```bash
# View all environment variables
cat coolify-deploy.env

# Check DNS
nslookup consult.alshifalab.pk

# Test health endpoint
curl https://consult.alshifalab.pk/api/v1/health/

# Test via public IP
curl http://34.124.150.231/api/v1/health/
```

---

**Status**: Ready for manual deployment
**Project UUID**: `ewsc80ck8scc8sw8s4ksc08g`
**Project Name**: FMU

