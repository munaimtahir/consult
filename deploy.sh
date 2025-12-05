#!/bin/bash
# Deployment script for Hospital Consult System (Multi-App Support)
# Public IP: 34.93.19.177
# Private IP: 18.220.252.164 (internal use only)

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================="
echo "Hospital Consult System - Multi-App Deployment"
echo "Public IP: 34.93.19.177"
echo "========================================="

# Validate configuration
if [ -f "scripts/validate-env.sh" ]; then
    echo -e "${BLUE}Validating environment variables...${NC}"
    bash scripts/validate-env.sh || {
        echo -e "${YELLOW}Warning: Environment validation failed, but continuing...${NC}"
    }
fi

# Check if Docker is running
if ! sudo docker ps > /dev/null 2>&1; then
    echo "Starting Docker daemon..."
    sudo dockerd > /tmp/dockerd.log 2>&1 &
    sleep 5
fi

# Validate docker-compose configuration
echo -e "${BLUE}Validating docker-compose configuration...${NC}"
if ! sudo docker compose config > /dev/null 2>&1; then
    echo "Error: docker-compose.yml has configuration errors"
    sudo docker compose config
    exit 1
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
sleep 15

# Check service status
echo ""
echo "Service Status:"
sudo docker compose ps

# Wait for health checks
echo ""
echo -e "${BLUE}Waiting for health checks...${NC}"
sleep 10

# Check health of key services
echo ""
echo "Health Checks:"
if [ -f "scripts/manage-apps.sh" ]; then
    bash scripts/manage-apps.sh health
else
    echo "Health check script not found, skipping health checks"
fi

echo ""
echo "========================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "========================================="
echo "Access URLs:"
echo "  Frontend: http://34.93.19.177"
echo "  Backend API: http://34.93.19.177/api/v1/"
echo "  Admin Panel: http://34.93.19.177/admin/"
echo "  Health Check: http://34.93.19.177/api/health/"
echo ""
echo "Management Commands:"
echo "  View logs: sudo docker compose logs -f"
echo "  Stop all: sudo docker compose down"
echo "  Manage apps: bash scripts/manage-apps.sh list"
echo "========================================="
