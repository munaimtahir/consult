# Coolify API Deployment Guide

Complete guide for deploying the consult repository to Coolify using the API.

## Prerequisites

- Coolify instance running at `http://34.124.150.231:8000`
- API token with deployment permissions
- DNS A record configured: `consult.alshifalab.pk` → `34.124.150.231`
- Ports 80, 443, and 8000 open on firewall
- GitHub repository accessible: `https://github.com/munaimtahir/consult`

## Configuration

### 1. API Configuration

The configuration is stored in `coolify-api-config.env`:

```bash
COOLIFY_API_URL=http://34.124.150.231:8000/api/v1
COOLIFY_API_TOKEN=2|2cA2IeQjF9ndrIBVoLd2ZUagGKVl9R2Dvns8VglUefaccdfa
COOLIFY_SERVER_ID=localhost
COOLIFY_PROJECT_ID=fmu
COOLIFY_PUBLIC_IP=34.124.150.231
COOLIFY_DOMAIN=consult.alshifalab.pk
```

### 2. Environment Variables

All environment variables are in `coolify-deploy.env` including:
- Django configuration
- Database credentials
- Redis configuration
- CORS/CSRF settings
- Frontend build configuration

## Deployment Methods

### Method 1: Bash Script (Recommended)

```bash
cd /home/munaim/repos/consult
./scripts/deploy-coolify-api.sh
```

The script will:
1. Check API connectivity
2. Get or create project
3. Check if application exists
4. Create application if needed
5. Set environment variables
6. Configure domain
7. Trigger deployment
8. Validate deployment

### Method 2: Python Script

```bash
cd /home/munaim/repos/consult
python3 scripts/deploy-coolify-api.py
```

Requires Python 3 and `requests` library:
```bash
pip3 install requests
```

### Method 3: Manual via Coolify Dashboard

1. Access Coolify: `http://34.124.150.231:8000`
2. Navigate to project `fmu`
3. Click "New Resource" → "Docker Compose"
4. Configure:
   - Name: `consult`
   - Git Repository: `https://github.com/munaimtahir/consult`
   - Branch: `main`
   - Compose File: `docker-compose.coolify.yml`
5. Add environment variables from `coolify-deploy.env`
6. Add domain: `consult.alshifalab.pk`
7. Click "Deploy"

## API Endpoints Used

The scripts interact with these Coolify API endpoints:

- `GET /api/v1/servers` - List servers
- `GET /api/v1/projects` - List projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects/{id}/applications` - List applications
- `POST /api/v1/projects/{id}/applications` - Create application
- `POST /api/v1/applications/{id}/environment-variables` - Set env vars
- `POST /api/v1/applications/{id}/domains` - Add domain
- `POST /api/v1/applications/{id}/deploy` - Trigger deployment

## Verification

### 1. DNS Check

```bash
nslookup consult.alshifalab.pk
# Should return: 34.124.150.231
```

### 2. API Connectivity

```bash
curl -H "Authorization: Bearer 2|2cA2IeQjF9ndrIBVoLd2ZUagGKVl9R2Dvns8VglUefaccdfa" \
     http://34.124.150.231:8000/api/v1/servers
```

### 3. Health Endpoints

After deployment:

```bash
# Domain (HTTPS)
curl https://consult.alshifalab.pk/api/v1/health/

# Public IP (HTTP)
curl http://34.124.150.231/api/v1/health/

# Expected response:
# {"status":"healthy","checks":{"database":"ok","cache":"ok"}}
```

## Troubleshooting

### API Authentication Failed

- Verify API token is correct
- Check token has `write`, `deploy`, and `read:sensitive` permissions
- Verify Coolify API is enabled in settings

### Application Creation Failed

- Check if project `fmu` exists in Coolify
- Verify server `localhost` exists
- Check GitHub repository is accessible
- Verify `docker-compose.coolify.yml` exists in repository

### Environment Variables Not Set

- Some API endpoints may vary by Coolify version
- Set environment variables manually in Coolify dashboard if needed
- Check `coolify-deploy.env` file format

### Domain Not Working

- Verify DNS has propagated: `nslookup consult.alshifalab.pk`
- Check SSL certificate is being issued (may take a few minutes)
- Verify ports 80 and 443 are open
- Check Coolify logs for Let's Encrypt errors

### Deployment Not Starting

- Check application logs in Coolify dashboard
- Verify Docker Compose file is valid
- Check if GitHub repository is accessible
- Verify build resources are sufficient

### Services Not Healthy

- Check individual service logs in Coolify
- Verify database and Redis are starting correctly
- Check environment variables are set correctly
- Verify health check endpoints are responding

## Post-Deployment

### Access Points

- **Frontend**: https://consult.alshifalab.pk
- **Backend API**: https://consult.alshifalab.pk/api/v1/
- **Django Admin**: https://consult.alshifalab.pk/admin/
- **WebSocket**: wss://consult.alshifalab.pk/ws/
- **Coolify Dashboard**: http://34.124.150.231:8000

### Default Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Superuser | admin@pmc.edu.pk | adminpassword123 |
| System Admin | sysadmin@pmc.edu.pk | password123 |

⚠️ **Change default passwords in production!**

### Monitoring

- Monitor deployment logs in Coolify dashboard
- Check service health status
- Monitor resource usage (CPU, RAM, disk)
- Set up automatic backups for database

### Updates

To update the application:

1. Push changes to GitHub repository
2. In Coolify dashboard, click "Redeploy"
3. Or use API: `POST /api/v1/applications/{id}/deploy`

## Support

- **Coolify Documentation**: https://coolify.io/docs
- **Coolify API Docs**: https://coolify.io/docs/api
- **Project Repository**: https://github.com/munaimtahir/consult

---

**Status**: Ready for deployment
**Last Updated**: 2024-12-28

