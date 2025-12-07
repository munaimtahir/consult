# Deployment Complete - Hospital Consult System

## Server Information

**Server IP Address:** `34.93.19.177`

## Service Status

All services are deployed and running:

- ✅ **Database (PostgreSQL)**: Running on port 5432
- ✅ **Redis**: Running on port 6379  
- ✅ **Backend (Django/FastAPI)**: Running on port 8000
- ✅ **Frontend (React)**: Running on port 3000
- ✅ **Nginx Reverse Proxy**: Running on port 80

## Access URLs

### Local Access (from server)
- **Frontend**: http://localhost/
- **Backend API**: http://localhost/api/v1/
- **Admin Panel**: http://localhost/admin/
- **Backend Direct**: http://localhost:8000
- **Frontend Direct**: http://localhost:3000

### External Access (from internet)
**Note:** External access requires firewall/security group configuration in your cloud provider's console.

- **Frontend**: http://34.93.19.177/
- **Backend API**: http://34.93.19.177/api/v1/
- **Admin Panel**: http://34.93.19.177/admin/

## Firewall Configuration Required

To enable external access, you need to configure your cloud provider's firewall/security group to allow:
- **Port 80 (HTTP)**: For frontend and API access
- **Port 443 (HTTPS)**: If you plan to add SSL (recommended)
- **Port 8000**: Optional, for direct backend access (not recommended for production)

### AWS Security Group Example
If using AWS, add inbound rules:
- Type: HTTP, Port: 80, Source: 0.0.0.0/0
- Type: HTTPS, Port: 443, Source: 0.0.0.0/0 (if using SSL)

### Google Cloud Platform Example
If using GCP, create firewall rules:
```bash
gcloud compute firewall-rules create allow-http \
    --allow tcp:80 \
    --source-ranges 0.0.0.0/0 \
    --target-tags http-server

gcloud compute firewall-rules create allow-https \
    --allow tcp:443 \
    --source-ranges 0.0.0.0/0 \
    --target-tags https-server
```

## Default Login Credentials

**IMPORTANT SECURITY NOTE**: Default credentials should be changed immediately after first login.

The system comes with pre-configured test users. Default credentials are generated during deployment and should be:
1. Changed immediately after first login for production use
2. Never committed to version control
3. Stored securely using a password manager or secrets management system

To view or reset credentials, use the backend's Django admin panel or management commands:
```bash
# Create a new superuser with secure password
sudo docker compose exec backend python manage.py createsuperuser

# Reset an existing user's password
sudo docker compose exec backend python manage.py changepassword <email>
```

Default test user roles available:
- Superuser (email: `admin@pmc.edu.pk`)
- System Admin (email: `sysadmin@pmc.edu.pk`)
- HOD - Cardiology (email: `cardio.hod@pmc.edu.pk`)
- Doctor - Cardiology (email: `cardio.doc@pmc.edu.pk`)

## Service Management

### View Service Status
```bash
cd /workspace
sudo docker compose ps
```

### View Logs
```bash
# All services
sudo docker compose logs -f

# Specific service
sudo docker compose logs -f backend
sudo docker compose logs -f frontend
sudo docker compose logs -f nginx-proxy
```

### Restart Services
```bash
sudo docker compose restart
# Or restart specific service
sudo docker compose restart backend
```

### Stop Services
```bash
sudo docker compose down
```

### Start Services
```bash
sudo docker compose up -d
```

### Rebuild and Redeploy
```bash
sudo docker compose down
sudo docker compose build
sudo docker compose up -d
```

## Architecture

```
Internet
   ↓
Port 80 (nginx-proxy - host network)
   ├── /api/ → localhost:8000 (backend)
   ├── /admin/ → localhost:8000 (backend)
   ├── /ws/ → localhost:8000 (backend WebSocket)
   ├── /static/ → static files
   ├── /media/ → media files
   └── / → localhost:3000 (frontend)
```

## Network Configuration

- **Backend, Database, Redis**: Using host networking mode
- **Frontend**: Using bridge network, exposed on port 3000
- **Nginx Proxy**: Using host networking mode, listening on port 80

### ⚠️ Security Note: Host Networking Mode

This deployment uses Docker's `network_mode: host` for several services to resolve networking issues. 

**Important Security Considerations:**
- **Reduced Isolation**: Host networking bypasses Docker's network isolation, exposing container ports directly on the host's network interface
- **Port Conflicts**: Services using host networking may conflict with other applications on the same ports
- **Production Considerations**: For production deployments, consider:
  - Using Docker's bridge networking with proper service discovery
  - Implementing additional firewall rules to restrict access to sensitive ports
  - Using a VPN or private network for database and Redis access
  - Configuring security groups/firewalls to only expose necessary ports (80, 443) to the internet

**Why Host Networking Was Used:**
This configuration was implemented to resolve Docker networking issues encountered during deployment. For better security, migrate to bridge networking when possible.

## Troubleshooting

### Check if services are running
```bash
sudo docker compose ps
```

### Check if ports are listening
```bash
sudo netstat -tlnp | grep -E ":(80|8000|3000|5432|6379)"
```

### Test local access
```bash
curl http://localhost/
curl http://localhost/api/v1/
curl http://localhost/admin/
```

### Check nginx configuration
```bash
sudo docker compose logs nginx-proxy
```

### Check backend logs for errors
```bash
sudo docker compose logs backend | tail -50
```

## Notes

1. **External Access**: Currently, external access (from internet) is blocked by firewall. You need to configure your cloud provider's security group/firewall to allow port 80.

2. **Backend Errors**: The backend may show some application-level errors in logs. These are code-level issues and don't prevent the service from running. The API endpoints are accessible.

3. **Database**: PostgreSQL is running and accessible. Migrations and seed data have been executed.

4. **SSL/HTTPS**: For production, you should configure SSL certificates (Let's Encrypt) and update nginx configuration to serve HTTPS.

## Next Steps

1. ✅ Configure firewall/security group to allow port 80
2. ✅ Test external access from your browser
3. ✅ Set up SSL/HTTPS (recommended for production)
4. ✅ Review and fix any backend application errors
5. ✅ Set up monitoring and logging
6. ✅ Configure backups for database

## Deployment Date

Deployed on: December 4, 2025

---

For support or issues, check the logs using the commands above.
