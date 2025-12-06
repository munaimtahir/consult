# Deployment Configuration Guide

This guide explains how to configure the application for deployment using environment variables.

## Quick Start

1. **Create a `.env` file** from the template:
   ```bash
   cp .env.example .env
   ```

2. **Update the environment variables** in `.env`:
   - Set `PUBLIC_IP` to your server's public IP address
   - Update `CONSULT_ALLOWED_HOSTS` to include your server's IP addresses
   - Update `CONSULT_CORS_ALLOWED_ORIGINS` and `CONSULT_CSRF_TRUSTED_ORIGINS`
   - Update `CONSULT_VITE_API_URL` and `CONSULT_VITE_WS_URL` to use your public IP
   - **Important**: Change `CONSULT_SECRET_KEY` to a strong, random value for production

3. **Deploy** using the deploy script:
   ```bash
   ./deploy.sh
   ```

## Environment Variables Reference

### Server Configuration
- `PUBLIC_IP`: Your server's public IP address (used by deploy script)
- `PRIVATE_IP`: Your server's private IP address (if applicable)

### Backend Configuration
- `CONSULT_DEBUG`: Set to `0` for production, `1` for development
- `CONSULT_SECRET_KEY`: **CRITICAL** - Must be changed for production
- `CONSULT_ALLOWED_HOSTS`: Comma-separated list of hostnames/IPs that can access the backend
- `CONSULT_CORS_ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins
- `CONSULT_CSRF_TRUSTED_ORIGINS`: Comma-separated list of trusted CSRF origins

### Database Configuration
- `DB_HOST`: Database host (default: `localhost` for host networking)
- `DB_PORT`: Database port (default: `5432`)
- `DB_NAME`: Database name
- `DB_USER`: Database user
- `DB_PASSWORD`: Database password

### Redis Configuration
- `REDIS_HOST`: Redis host (default: `localhost` for host networking)
- `REDIS_PORT`: Redis port (default: `6379`)
- `REDIS_URL`: Redis connection URL

### Frontend Configuration
- `CONSULT_VITE_API_URL`: Backend API URL (e.g., `http://YOUR_IP/api/v1`)
- `CONSULT_VITE_WS_URL`: WebSocket URL (e.g., `ws://YOUR_IP/ws`)

## Example Configuration for a New Server

If your server's public IP is `1.2.3.4`, your `.env` file should look like:

```env
PUBLIC_IP=1.2.3.4

CONSULT_ALLOWED_HOSTS=localhost,127.0.0.1,backend,1.2.3.4
CONSULT_CORS_ALLOWED_ORIGINS=http://1.2.3.4,http://localhost:3000,http://localhost
CONSULT_CSRF_TRUSTED_ORIGINS=http://1.2.3.4,http://localhost:3000,http://localhost

CONSULT_VITE_API_URL=http://1.2.3.4/api/v1
CONSULT_VITE_WS_URL=ws://1.2.3.4/ws

CONSULT_SECRET_KEY=your-very-long-random-secret-key-here
```

## Security Best Practices

### 1. Never Commit Credentials
- The `.env` file should **never** be committed to version control
- It's already included in `.gitignore`
- Use `.env.example` as a template

### 2. Generate Strong Secret Keys
Generate a strong secret key for production:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 3. Change Default Passwords
After deployment, immediately change all default passwords:
```bash
# Create a new superuser with secure password
sudo docker compose exec backend python manage.py createsuperuser

# Reset existing user passwords
sudo docker compose exec backend python manage.py changepassword <email>
```

### 4. Restrict Access
- Configure firewall rules to only allow necessary ports (80, 443)
- Block direct access to database (5432) and Redis (6379) from the internet
- Use security groups/firewall rules in your cloud provider

### 5. Enable HTTPS
For production, configure SSL/TLS certificates:
- Use Let's Encrypt for free SSL certificates
- Update nginx configuration to redirect HTTP to HTTPS
- Update environment variables to use `https://` and `wss://` URLs

## Troubleshooting

### Services Can't Connect
If services can't connect to each other:
1. Verify `DB_HOST` and `REDIS_HOST` are set correctly (use `localhost` for host networking)
2. Check that all services are running: `sudo docker compose ps`
3. Check logs for connection errors: `sudo docker compose logs backend`

### CORS Errors
If you see CORS errors in the browser console:
1. Verify `CONSULT_CORS_ALLOWED_ORIGINS` includes your server's IP/domain
2. Verify `CONSULT_CSRF_TRUSTED_ORIGINS` includes your server's IP/domain
3. Restart backend after changing these: `sudo docker compose restart backend`

### Frontend Can't Connect to Backend
If the frontend can't reach the API:
1. Verify `CONSULT_VITE_API_URL` is set to your server's public IP
2. Rebuild the frontend: `sudo docker compose build frontend`
3. Restart services: `sudo docker compose up -d`

## Additional Resources

- [Docker Compose Environment Variables](https://docs.docker.com/compose/environment-variables/)
- [Django Settings Best Practices](https://docs.djangoproject.com/en/stable/topics/settings/)
- [Nginx Configuration Guide](https://nginx.org/en/docs/)
