# Server Update Instructions

## Issue
The server is using old IP addresses (`3.233.180.130`) instead of the new public IP (`172.104.53.127`).

## Quick Fix - Update deploy.sh on Server

SSH into your server and run:

```bash
cd /home/munaim/apps/consult

# Update deploy.sh
cat > deploy.sh << 'EOF'
#!/bin/bash
# Deployment script for Hospital Consult System
# Server IP: 172.104.53.127

set -e

echo "========================================="
echo "Hospital Consult System - Deployment"
echo "Server IP: 172.104.53.127"
echo "========================================="

# Check if Docker is running
if ! sudo docker ps > /dev/null 2>&1; then
    echo "Starting Docker daemon..."
    sudo dockerd > /tmp/dockerd.log 2>&1 &
    sleep 5
fi

# Stop any existing containers
echo "Stopping existing containers..."
sudo docker compose down 2>/dev/null || true

# Build images
echo "Building Docker images..."
sudo docker compose build

# Start services
echo "Starting services..."
sudo docker compose up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Check service status
echo "Checking service status..."
sudo docker compose ps

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo "Frontend: http://172.104.53.127"
echo "Backend API: http://172.104.53.127/api/v1/"
echo "Admin Panel: http://172.104.53.127/admin/"
echo ""
echo "To view logs: sudo docker compose logs -f"
echo "To stop: sudo docker compose down"
echo "========================================="
EOF

chmod +x deploy.sh
```

## Also Update docker-compose.yml

The docker-compose.yml on the server also needs to be updated. Run this on the server:

```bash
cd /home/munaim/apps/consult

# Update docker-compose.yml to use correct IP
sed -i 's/3\.233\.180\.130/172.104.53.127/g' docker-compose.yml
sed -i 's/18\.220\.252\.164/172.104.53.127/g' docker-compose.yml

# Verify the changes
grep "172.104.53.127" docker-compose.yml
```

## Update nginx/default.conf

```bash
cd /home/munaim/apps/consult

# Update nginx config
sed -i 's/3\.233\.180\.130/172.104.53.127/g' nginx/default.conf
sed -i 's/18\.220\.252\.164/172.104.53.127/g' nginx/default.conf

# Verify the changes
grep "172.104.53.127" nginx/default.conf
```

## After Updates - Redeploy

After updating all files, redeploy:

```bash
cd /home/munaim/apps/consult
./deploy.sh
```

## Verify Configuration

After deployment, verify the configuration is correct:

```bash
# Check docker-compose environment variables
sudo docker compose config | grep -E "(VITE_API_URL|VITE_WS_URL|ALLOWED_HOSTS|CORS_ALLOWED_ORIGINS)"

# Should show:
# - VITE_API_URL=http://172.104.53.127/api/v1
# - VITE_WS_URL=ws://172.104.53.127/ws
# - ALLOWED_HOSTS should include 172.104.53.127
# - CORS_ALLOWED_ORIGINS should include http://172.104.53.127
```

