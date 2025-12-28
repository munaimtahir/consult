# 🚀 Deploy Now - consult.alshifalab.pk

## ✅ Everything is Ready!

Your Hospital Consult System is configured and ready to deploy via Coolify with domain `consult.alshifalab.pk`.

## Quick Start (5 Steps)

### 1. Access Coolify Dashboard
```
http://your-vps-ip:8000
```
Login to your Coolify instance.

### 2. Create New Resource
- Click **"New Resource"** → **"Docker Compose"**
- **Name:** `consult`
- **Source:** 
  - Git: `https://github.com/munaimtahir/consult`
  - OR Local Path: `/home/munaim/repos/consult`
- **Compose File:** `docker-compose.coolify.yml`

### 3. Add Domain
- Go to **"Domains"** section
- Add: `consult.alshifalab.pk`
- Coolify will auto-configure SSL certificate

### 4. Set Environment Variables
Copy and paste ALL variables from `.env.coolify`:

```bash
SECRET_KEY=062ea43b72adeb8c8b73e691994e25bc18e488406bd50cf4b329134b92ea6c63
DEBUG=0
ALLOWED_HOSTS=consult.alshifalab.pk,localhost,127.0.0.1,backend
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
CORS_ALLOWED_ORIGINS=https://consult.alshifalab.pk,http://consult.alshifalab.pk,http://localhost:3000
CSRF_TRUSTED_ORIGINS=https://consult.alshifalab.pk,http://consult.alshifalab.pk,http://localhost:3000
VITE_API_URL=https://consult.alshifalab.pk/api/v1
VITE_WS_URL=wss://consult.alshifalab.pk/ws
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SITE_ID=1
```

### 5. Deploy
- Click **"Deploy"** button
- Wait 2-5 minutes for initialization
- Monitor logs in Coolify dashboard

## Verify Deployment

After deployment completes:

1. **Frontend:** https://consult.alshifalab.pk
2. **Backend Health:** https://consult.alshifalab.pk/api/v1/health/
3. **Admin Panel:** https://consult.alshifalab.pk/admin/

Expected health response:
```json
{"status":"healthy","checks":{"database":"ok","cache":"ok"}}
```

## Default Login

- **Email:** admin@pmc.edu.pk
- **Password:** adminpassword123

⚠️ **Change passwords in production!**

## What's Configured

✅ Domain: `consult.alshifalab.pk`  
✅ DNS: Resolving correctly  
✅ Secret Key: Configured  
✅ Environment Variables: Ready  
✅ Docker Compose: Optimized for Coolify  
✅ SSL: Will be auto-configured by Coolify  

## Files Reference

- **Quick Guide:** `COOLIFY_DEPLOY_INSTRUCTIONS.md`
- **Environment Variables:** `.env.coolify`
- **Detailed Guide:** `COOLIFY_DEPLOYMENT.md`

## Troubleshooting

**Domain not working?**
- Check DNS: `nslookup consult.alshifalab.pk`
- Verify domain added in Coolify

**Services not starting?**
- Check logs in Coolify dashboard
- Verify environment variables are set

**SSL issues?**
- Ensure DNS points to VPS
- Check ports 80/443 are open
- Review Coolify logs

---

**Ready to deploy!** 🎉

Follow the 5 steps above to deploy via Coolify UI.


