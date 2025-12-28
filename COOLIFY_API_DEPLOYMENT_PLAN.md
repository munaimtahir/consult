# Complete Coolify API Deployment Setup Plan

## Overview

This plan sets up a complete deployment system for the consult repository using Coolify API. All configurations use public IP addresses instead of localhost for external access.

## Public IP Configuration

**IMPORTANT**: The correct public VPS IP for this workspace is `34.124.150.231`. All references use this IP.

- **VPS Public IP**: `34.124.150.231` (correct public VPS IP)
- **Domain**: `consult.alshifalab.pk`
- **Coolify Dashboard**: `http://34.124.150.231:8000` (or configured port)
- **Coolify API**: `http://34.124.150.231:8000/api/v1` (or configured endpoint)

## Files to Create

### 1. Coolify API Configuration
**File**: `coolify-api-config.env`
- Configuration with actual values:
  - `COOLIFY_API_URL` - Public IP based API endpoint: `http://34.124.150.231:8000/api/v1`
  - `COOLIFY_API_TOKEN` - API token: `2|2cA2IeQjF9ndrIBVoLd2ZUagGKVl9R2Dvns8VglUefaccdfa`
  - `COOLIFY_SERVER_ID` - Server name: `localhost`
  - `COOLIFY_PROJECT_ID` - Project ID: `fmu`
  - `COOLIFY_PUBLIC_IP` - Public IP address: `34.124.150.231`
  - `COOLIFY_DOMAIN` - Domain name: `consult.alshifalab.pk`

### 2. Environment Variables for Deployment
**File**: `coolify-deploy.env`
- Complete environment variables with public IP:
  - Django config with `ALLOWED_HOSTS` including public IP
  - CORS/CSRF with public IP URLs
  - Frontend build args with public IP URLs
  - Database password (placeholder to be filled)
  - All other required variables

### 3. Bash Deployment Script
**File**: `scripts/deploy-coolify-api.sh`
- Complete script that:
  - Loads configuration from `coolify-api-config.env`
  - Validates API connectivity using public IP
  - Creates/updates Docker Compose resource
  - Sets all environment variables
  - Configures domain with SSL
  - Triggers deployment
  - Monitors deployment status
  - Validates deployment using public IP endpoints

### 4. Python Deployment Script
**File**: `scripts/deploy-coolify-api.py`
- Python alternative with:
  - Better error handling
  - Structured logging
  - Retry logic
  - JSON response parsing
  - Progress tracking
  - Uses public IP for all API calls

### 5. API Deployment Documentation
**File**: `COOLIFY_API_DEPLOYMENT.md`
- Complete guide including:
  - How to get API token from Coolify dashboard (using public IP)
  - Configuration setup
  - Running deployment scripts
  - Troubleshooting
  - API endpoint reference

### 6. Updated Environment Variables Reference
**File**: `COOLIFY_ENV_VARIABLES_PUBLIC_IP.md`
- Updated with public IP addresses:
  - `ALLOWED_HOSTS` includes public IP
  - `CORS_ALLOWED_ORIGINS` includes public IP URLs
  - `CSRF_TRUSTED_ORIGINS` includes public IP URLs
  - `VITE_API_URL` uses public IP or domain
  - `VITE_WS_URL` uses public IP or domain

## Environment Variables Configuration

### Required Variables (with Public IP)

```bash
# Django Configuration
SECRET_KEY=062ea43b72adeb8c8b73e691994e25bc18e488406bd50cf4b329134b92ea6c63
DEBUG=0
ALLOWED_HOSTS=consult.alshifalab.pk,34.124.150.231,localhost,127.0.0.1,backend
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

# CORS Configuration (with public IP)
CORS_ALLOWED_ORIGINS=https://consult.alshifalab.pk,http://consult.alshifalab.pk,http://34.124.150.231,http://34.124.150.231:3000
CSRF_TRUSTED_ORIGINS=https://consult.alshifalab.pk,http://consult.alshifalab.pk,http://34.124.150.231,http://34.124.150.231:3000

# Frontend Build Configuration (with public IP fallback)
VITE_API_URL=https://consult.alshifalab.pk/api/v1
VITE_WS_URL=wss://consult.alshifalab.pk/ws

# Security Settings (for HTTPS)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SITE_ID=1
```

## Coolify API Endpoints (using Public IP)

All API calls will use: `http://34.124.150.231:8000/api/v1` (or configured endpoint)

- `GET /servers` - List servers
- `GET /projects` - List projects  
- `POST /projects/{id}/applications` - Create Docker Compose application
- `PUT /applications/{id}` - Update application
- `POST /applications/{id}/environment-variables` - Set environment variables
- `POST /applications/{id}/domains` - Add domain
- `POST /applications/{id}/deploy` - Trigger deployment
- `GET /applications/{id}/status` - Check deployment status

## Deployment Flow

1. **Load Configuration**
   - Read `coolify-api-config.env` (user must create from template)
   - Validate API URL is accessible (using public IP)
   - Load environment variables from `coolify-deploy.env`

2. **Authenticate**
   - Test API token with public IP endpoint
   - Verify permissions

3. **Create/Update Resource**
   - Check if application exists
   - Create new Docker Compose resource if needed
   - Use GitHub repository: `https://github.com/munaimtahir/consult`
   - Use compose file: `docker-compose.coolify.yml`
   - Set build pack to Docker Compose

4. **Configure Environment Variables**
   - Set all variables from `coolify-deploy.env`
   - Replace placeholders with actual values
   - Include public IP in all relevant variables

5. **Configure Domain**
   - Add domain: `consult.alshifalab.pk`
   - Enable SSL/HTTPS (Let's Encrypt)
   - Configure routing

6. **Deploy**
   - Trigger deployment via API
   - Monitor logs
   - Wait for services to be healthy
   - Check deployment status

7. **Validate**
   - Test: `https://consult.alshifalab.pk/api/v1/health/`
   - Test: `https://consult.alshifalab.pk/`
   - Test: `http://34.124.150.231/api/v1/health/` (fallback)
   - Verify all services are running

## Validation Endpoints (using Public IP/Domain)

After deployment, validate using:
- Frontend: `https://consult.alshifalab.pk` or `http://34.124.150.231`
- Backend API: `https://consult.alshifalab.pk/api/v1/health/` or `http://34.124.150.231/api/v1/health/`
- Django Admin: `https://consult.alshifalab.pk/admin/` or `http://34.124.150.231/admin/`
- WebSocket: `wss://consult.alshifalab.pk/ws/` or `ws://34.124.150.231/ws/`

## Configuration Values

**Coolify API Configuration:**
- **Coolify API Token**: `2|2cA2IeQjF9ndrIBVoLd2ZUagGKVl9R2Dvns8VglUefaccdfa`
- **Coolify Server ID**: `localhost` (server name - this is the server identifier in Coolify)
- **Coolify Project ID**: `fmu`

**Configuration Files Created:**
- `coolify-api-config.env` - Contains actual API configuration with token and IDs
- `coolify-deploy.env` - Contains all environment variables for deployment

**Other Placeholders:**
- **Email Password** (optional) - For email notifications
- **Google OAuth Credentials** (optional) - If using OAuth

Note: Database password is set to `consult_password` as per documentation. Change it in production for security.

## Success Criteria

- ✅ Script authenticates with Coolify API using public IP
- ✅ Resource created/updated successfully
- ✅ All environment variables set with public IP addresses
- ✅ Domain configured with SSL
- ✅ Deployment completed successfully
- ✅ All services healthy
- ✅ Application accessible via domain and public IP
- ✅ Health endpoints responding correctly

## Notes

- Health checks inside containers still use `localhost` (correct for internal checks)
- External access uses public IP or domain
- SSL/HTTPS preferred, HTTP as fallback
- All API calls use public IP for Coolify API endpoint
- Environment variables include both domain and public IP for flexibility

 