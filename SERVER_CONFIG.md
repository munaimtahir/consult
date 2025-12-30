# Server Configuration - Single Source of Truth

**⚠️ IMPORTANT:** This file is the authoritative source for server IP addresses.  
When updating server configuration, update this file first, then update all other files that reference these values.

## Server IP Addresses

### Public IP (Internet Access)
- **IP Address**: `172.104.53.127`
- **Usage**: This is the IP address used to access the application from the internet
- **Used in**: 
  - `docker-compose.yml` (ALLOWED_HOSTS, CORS, CSRF, VITE_API_URL, VITE_WS_URL)
  - `nginx/default.conf` (server_name)
  - All documentation files
  - Deployment scripts

### Private IP (Internal Use Only)
- **IP Address**: `18.220.252.164`
- **Usage**: Internal/private IP address of the cloud server (not accessible from internet)
- **Note**: Do NOT use this IP in configuration files for external access

## Application URLs

All URLs use the **Public IP** (`172.104.53.127`):

- **Frontend**: http://172.104.53.127
- **Backend API**: http://172.104.53.127/api/v1/
- **Admin Panel**: http://172.104.53.127/admin/
- **WebSocket**: ws://172.104.53.127/ws

## Files That Reference Server IP

When updating the server IP, ensure these files are updated:

### Configuration Files (Runtime)
- `docker-compose.yml` - Environment variables and build args
- `nginx/default.conf` - Nginx server_name directive

### Documentation Files
- `DEPLOYMENT_COMPLETE.md` - Application access URLs
- `DEPLOYMENT_STATUS.md` - Deployment status and URLs
- `DEPLOYMENT.md` - Deployment guide
- `README.md` - Main project documentation (if contains deployment info)

### Scripts
- `deploy.sh` - Deployment script output messages

## How to Update Server IP

If the server IP changes, follow these steps:

1. **Update this file** (`SERVER_CONFIG.md`) with the new IP addresses
2. **Update configuration files**:
   ```bash
   # Update docker-compose.yml
   sed -i 's/172.104.53.127/NEW_PUBLIC_IP/g' docker-compose.yml
   
   # Update nginx/default.conf
   sed -i 's/172.104.53.127/NEW_PUBLIC_IP/g' nginx/default.conf
   ```
3. **Update documentation files**:
   ```bash
   find . -name "*.md" -type f -exec sed -i 's/172.104.53.127/NEW_PUBLIC_IP/g' {} \;
   ```
4. **Update scripts**:
   ```bash
   find . -name "*.sh" -type f -exec sed -i 's/172.104.53.127/NEW_PUBLIC_IP/g' {} \;
   ```
5. **Verify changes**:
   ```bash
   grep -r "172.104.53.127" . --include="*.yml" --include="*.conf" --include="*.md" --include="*.sh"
   ```
6. **Rebuild and redeploy**:
   ```bash
   ./deploy.sh
   ```

## Last Updated
- **Date**: 2024-12-05
- **Updated By**: Repository cleanup and configuration standardization
