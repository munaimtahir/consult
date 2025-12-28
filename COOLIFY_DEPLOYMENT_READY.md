# Coolify Deployment Ready - consult.alshifalab.pk

## ✅ Configuration Complete

All files have been prepared for deployment to Coolify with domain `consult.alshifalab.pk`.

## Domain Status

- **Domain:** `consult.alshifalab.pk`
- **DNS:** ✅ Resolving to IP: `34.124.150.231`
- **SSL:** Will be auto-configured by Coolify

## Files Prepared

1. ✅ **COOLIFY_DEPLOY_INSTRUCTIONS.md** - Step-by-step deployment guide
2. ✅ **COOLIFY_ENV_VARIABLES.md** - Updated with domain
3. ✅ **.env.coolify** - Ready-to-use environment variables
4. ✅ **docker-compose.coolify.yml** - Optimized for Coolify
5. ✅ **deploy-coolify.sh** - Deployment helper script

## Quick Deployment Steps

### Option 1: Via Coolify Web UI (Recommended)

1. **Access Coolify:**
   - Open: `http://your-vps-ip:8000` (or your Coolify URL)
   - Login to Coolify dashboard

2. **Create New Resource:**
   - Click "New Resource" → "Docker Compose"
   - Name: `consult`
   - Source: 
     - Git: `https://github.com/munaimtahir/consult`
     - OR Local: `/home/munaim/repos/consult`
   - Compose File: `docker-compose.coolify.yml`

3. **Add Domain:**
   - Go to "Domains" section
   - Add: `consult.alshifalab.pk`
   - Coolify will auto-configure SSL

4. **Set Environment Variables:**
   - Copy all variables from `.env.coolify` file
   - Paste into Coolify's environment variables section

5. **Deploy:**
   - Click "Deploy" button
   - Monitor logs (2-5 minutes)

### Option 2: Via Coolify API (If Available)

If Coolify API is accessible, you can deploy programmatically. Check Coolify documentation for API endpoints.

## Environment Variables

All environment variables are configured in `.env.coolify`:

```bash
SECRET_KEY=062ea43b72adeb8c8b73e691994e25bc18e488406bd50cf4b329134b92ea6c63
ALLOWED_HOSTS=consult.alshifalab.pk,localhost,127.0.0.1,backend
CORS_ALLOWED_ORIGINS=https://consult.alshifalab.pk,http://consult.alshifalab.pk,http://localhost:3000
CSRF_TRUSTED_ORIGINS=https://consult.alshifalab.pk,http://consult.alshifalab.pk,http://localhost:3000
VITE_API_URL=https://consult.alshifalab.pk/api/v1
VITE_WS_URL=wss://consult.alshifalab.pk/ws
```

## Routing Configuration

Coolify's Traefik will handle routing. Configure:

- **Domain:** `consult.alshifalab.pk`
- **Target:** `nginx-proxy` service (port 80)
- **SSL:** Auto-configured by Coolify

If not using Nginx proxy:
- `/api/` → `backend:8000`
- `/ws/` → `backend:8000` (WebSocket)
- `/` → `frontend:80`

## Post-Deployment Verification

After deployment, test:

1. **Frontend:** https://consult.alshifalab.pk
2. **Backend Health:** https://consult.alshifalab.pk/api/v1/health/
3. **Django Admin:** https://consult.alshifalab.pk/admin/

Expected health response:
```json
{"status":"healthy","checks":{"database":"ok","cache":"ok"}}
```

## Default Login

- **Email:** admin@pmc.edu.pk
- **Password:** adminpassword123

⚠️ Change passwords in production!

## Troubleshooting

### Domain Not Working
- Verify DNS: `nslookup consult.alshifalab.pk`
- Check DNS propagation (may take up to 48 hours)
- Verify domain is added in Coolify

### SSL Certificate Issues
- Ensure DNS points to VPS
- Check ports 80 and 443 are open
- Review Coolify logs for Let's Encrypt errors

### Services Not Starting
- Check logs in Coolify dashboard
- Verify environment variables
- Check database/Redis connections

## Next Steps

1. ✅ Configuration files ready
2. ✅ Environment variables prepared
3. ✅ Domain DNS configured
4. ⏳ Deploy via Coolify UI
5. ⏳ Verify deployment
6. ⏳ Test all endpoints

---

**Status:** ✅ Ready for Coolify deployment
**Domain:** consult.alshifalab.pk
**See:** COOLIFY_DEPLOY_INSTRUCTIONS.md for detailed steps


