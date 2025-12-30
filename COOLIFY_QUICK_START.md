# Coolify Quick Start Guide

Quick reference for deploying the Hospital Consult System on Coolify.

## Pre-Deployment Checklist

- [ ] Coolify installed on VPS
- [ ] Repository accessible (Git or local)
- [ ] Domain configured (optional)
- [ ] Environment variables prepared

## Deployment Steps

### 1. Create Resource in Coolify
- Resource Type: **Docker Compose**
- Name: `consult` or `hospital-consult-system`
- Source: Connect Git repository or upload files

### 2. Set Environment Variables
Copy variables from `COOLIFY_ENV_VARIABLES.md` and replace:
- `your-domain.com` → Your domain
- `your-vps-ip` → Your VPS IP
- `your-secure-db-password-here` → Strong password
- `SECRET_KEY` → `062ea43b72adeb8c8b73e691994e25bc18e488406bd50cf4b329134b92ea6c63` (already configured)

### 3. Deploy
- Click "Deploy" in Coolify
- Monitor logs for initialization (2-5 minutes)

### 4. Configure SSL (Optional)
- Add domain in Coolify settings
- SSL will be auto-configured
- Update environment variables with HTTPS URLs
- Redeploy

## Quick Commands

### Generate Secret Key
```bash
openssl rand -hex 32
```

### Test Health Endpoint
```bash
curl http://your-domain.com/api/v1/health/
```

### Access Points
- Frontend: `http://your-domain.com`
- API: `http://your-domain.com/api/v1/`
- Admin: `http://your-domain.com/admin/`

## Default Login

- Email: `admin@pmc.edu.pk`
- Password: `adminpassword123`

## Troubleshooting

1. **Services not starting:** Check logs in Coolify dashboard
2. **Database errors:** Verify `DB_PASSWORD` and `DB_HOST`
3. **Frontend not loading:** Check `VITE_API_URL` and `VITE_WS_URL`
4. **WebSocket issues:** Verify `VITE_WS_URL` uses correct protocol

## Full Documentation

- **Detailed Guide:** [COOLIFY_DEPLOYMENT.md](./COOLIFY_DEPLOYMENT.md)
- **Environment Variables:** [COOLIFY_ENV_VARIABLES.md](./COOLIFY_ENV_VARIABLES.md)
- **Main README:** [README.md](./README.md)

