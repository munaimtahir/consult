# Coolify Deployment Guide

This guide provides step-by-step instructions for deploying the Hospital Consult System on a VPS using Coolify PaaS.

## Prerequisites

1. **VPS Requirements:**
   - Ubuntu 20.04+ or Debian 11+ (recommended)
   - Minimum 2GB RAM, 2 CPU cores
   - 20GB+ disk space
   - Root or sudo access

2. **Coolify Installation:**
   - Coolify must be installed on your VPS
   - If not installed, follow: https://coolify.io/docs/installation

3. **Domain (Optional but Recommended):**
   - A domain name pointing to your VPS IP
   - Or use the VPS IP address directly

## Nginx Reverse Proxy Configuration

**Yes, we will use Nginx reverse proxy!** 

The deployment uses an **Nginx reverse proxy service** that handles:
- Routing API calls (`/api/`) to the backend
- Routing WebSocket connections (`/ws/`) to the backend
- Serving static files (`/static/`) and media files (`/media/`)
- Serving the React frontend (`/`)
- Health checks and error handling

**How it works with Coolify:**
- Coolify's Traefik reverse proxy routes external traffic to the Nginx service (port 80)
- Nginx handles all internal routing between frontend and backend
- This keeps the existing architecture and simplifies deployment

**Alternative:** If you prefer to use only Coolify's Traefik (without Nginx), you can configure path-based routing in Coolify, but the current setup with Nginx is recommended for simplicity.

## Deployment Steps

### Step 1: Prepare the Repository

1. **Ensure your repository is accessible:**
   - Repository should be in a Git hosting service (GitHub, GitLab, etc.)
   - Or have the code available on the VPS

2. **Verify required files exist:**
   - `docker-compose.yml` ✓
   - `backend/Dockerfile` ✓
   - `frontend/Dockerfile` ✓
   - `env.example` ✓

### Step 2: Create a New Resource in Coolify

1. **Login to Coolify Dashboard:**
   - Access your Coolify instance (usually at `http://your-vps-ip:8000`)

2. **Create a New Resource:**
   - Click "New Resource" or "+" button
   - Select "Docker Compose" as the resource type

3. **Configure the Resource:**
   - **Name:** `consult` or `hospital-consult-system`
   - **Source:** 
     - If using Git: Connect your Git repository
     - If using local files: Upload or provide path to the repository

### Step 3: Configure Environment Variables

In Coolify, navigate to your resource's environment variables section and add the following:

#### Required Environment Variables

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

# CORS Configuration (replace with your domain/IP)
CORS_ALLOWED_ORIGINS=https://your-domain.com,http://your-vps-ip,http://localhost:3000
CSRF_TRUSTED_ORIGINS=https://your-domain.com,http://your-vps-ip,http://localhost:3000

# Frontend Build Configuration (replace with your domain/IP)
VITE_API_URL=https://your-domain.com/api/v1
VITE_WS_URL=wss://your-domain.com/ws
```

#### Optional Environment Variables

```bash
# Email Configuration (if you want email notifications)
EMAIL_HOST_USER=consult@pmc.edu.pk
EMAIL_HOST_PASSWORD=your_email_password
EMAIL_DOMAIN=pmc.edu.pk

# Google OAuth (if you want SSO)
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret
DOMAIN=pmc.edu.pk

# Security Settings (for HTTPS)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

**Important Notes:**
- `SECRET_KEY` is already configured: `062ea43b72adeb8c8b73e691994e25bc18e488406bd50cf4b329134b92ea6c63`
- Replace `your-domain.com` and `your-vps-ip` with your actual values
- Use HTTPS URLs (`https://` and `wss://`) if you have SSL enabled
- Use HTTP URLs (`http://` and `ws://`) if SSL is not configured

### Step 4: Configure Docker Compose

Coolify will use the `docker-compose.yml` file (or `docker-compose.coolify.yml` if you prefer the optimized version). Ensure the following:

1. **Port Configuration:**
   - The nginx-proxy service exposes port 80
   - Coolify will handle port mapping automatically
   - If using a custom port, configure it in Coolify's port settings

2. **Volume Persistence:**
   - Database data: `postgres_data` volume (persistent)
   - Static files: `static_volume` (can be ephemeral)
   - Media files: `media_volume` (should be persistent)

3. **Network Configuration:**
   - Services use `consult_network` bridge network
   - Coolify will handle network isolation

### Step 5: Deploy the Application

1. **Review Configuration:**
   - Double-check all environment variables
   - Verify docker-compose.yml is correct

2. **Start Deployment:**
   - Click "Deploy" or "Start" in Coolify
   - Monitor the deployment logs

3. **Monitor Initialization:**
   - Backend will:
     - Wait for PostgreSQL and Redis
     - Run database migrations
     - Seed demo data
     - Collect static files
   - This may take 2-5 minutes on first deployment

### Step 6: Configure Domain and SSL (Optional)

1. **Add Domain in Coolify:**
   - Navigate to your resource settings
   - Add your domain name
   - Coolify will automatically configure SSL using Let's Encrypt

2. **Update Environment Variables:**
   - After SSL is configured, update:
     - `CORS_ALLOWED_ORIGINS` to include `https://your-domain.com`
     - `CSRF_TRUSTED_ORIGINS` to include `https://your-domain.com`
     - `VITE_API_URL` to `https://your-domain.com/api/v1`
     - `VITE_WS_URL` to `wss://your-domain.com/ws`
   - Redeploy after updating environment variables

### Step 7: Verify Deployment

1. **Check Service Health:**
   ```bash
   # In Coolify dashboard, check service status
   # All services should show as "Healthy"
   ```

2. **Test Endpoints:**
   - Frontend: `http://your-domain.com` or `http://your-vps-ip`
   - Backend API: `http://your-domain.com/api/v1/health/`
   - Django Admin: `http://your-domain.com/admin/`

3. **Test Login:**
   - Use demo credentials from README.md
   - Example: `admin@pmc.edu.pk` / `adminpassword123`

## Post-Deployment Configuration

### 1. Database Backup

Configure automatic backups in Coolify:
- Navigate to your resource → Backups
- Enable automatic backups for the `postgres_data` volume
- Set backup frequency (daily recommended)

### 2. Monitoring

- **Logs:** Access logs in Coolify dashboard
- **Health Checks:** Coolify monitors health endpoints automatically
- **Resource Usage:** Monitor CPU, RAM, and disk usage in dashboard

### 3. Updates and Maintenance

**Updating the Application:**
1. Push changes to your Git repository
2. In Coolify, click "Redeploy" or enable auto-deploy
3. Coolify will pull latest changes and rebuild containers

**Database Migrations:**
- Migrations run automatically on container startup
- Check logs if migrations fail

**Static Files:**
- Static files are collected automatically on startup
- If static files don't update, restart the backend service

## Troubleshooting

### Services Not Starting

1. **Check Logs:**
   - View logs in Coolify dashboard
   - Look for error messages

2. **Common Issues:**
   - **Database connection failed:** Check `DB_HOST`, `DB_USER`, `DB_PASSWORD`
   - **Redis connection failed:** Check `REDIS_URL`
   - **Port conflicts:** Ensure port 80 is available
   - **Insufficient resources:** Check VPS CPU/RAM usage

### Frontend Not Loading

1. **Check Environment Variables:**
   - Verify `VITE_API_URL` and `VITE_WS_URL` are correct
   - Ensure they match your domain/IP

2. **Check Backend Health:**
   - Test: `curl http://your-domain.com/api/v1/health/`
   - Should return: `{"status": "ok"}`

### WebSocket Not Working

1. **Check WebSocket URL:**
   - Verify `VITE_WS_URL` uses correct protocol (`ws://` or `wss://`)
   - Ensure it matches your domain/IP

2. **Check Nginx Configuration:**
   - WebSocket proxy settings are in `nginx/default.conf`
   - Verify `/ws/` location block is correct

### Database Issues

1. **Reset Database (Development Only):**
   ```bash
   # In Coolify, access backend container shell
   python manage.py flush --noinput
   python manage.py migrate
   python manage.py seed_data
   ```

2. **Backup Database:**
   ```bash
   # In Coolify, access db container shell
   pg_dump -U consult_user consult_db > backup.sql
   ```

## Default Login Credentials

After deployment, you can use these demo credentials:

| Role | Email | Password |
|------|-------|----------|
| **Superuser** | admin@pmc.edu.pk | adminpassword123 |
| **System Admin** | sysadmin@pmc.edu.pk | password123 |
| **Cardiology HOD** | cardio.hod@pmc.edu.pk | password123 |
| **Cardiology Doctor** | cardio.doc@pmc.edu.pk | password123 |
| **Neurology HOD** | neuro.hod@pmc.edu.pk | password123 |
| **Neurology Doctor** | neuro.doc@pmc.edu.pk | password123 |

**⚠️ Security Note:** Change default passwords in production!

## Support and Resources

- **Coolify Documentation:** https://coolify.io/docs
- **Project README:** [README.md](./README.md)
- **Deployment Guide:** [DEPLOYMENT.md](./DEPLOYMENT.md)
- **Troubleshooting:** Check logs in Coolify dashboard

---

**Deployment Complete!** 🎉

Your Hospital Consult System should now be running on your VPS via Coolify.

