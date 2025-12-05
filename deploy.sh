#!/bin/bash
# Deployment script for Hospital Consult System
# Public IP: 34.93.19.177
# Private IP: 18.220.252.164 (internal use only)

set -e

echo "========================================="
echo "Hospital Consult System - Deployment"
echo "Public IP: 34.93.19.177"
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
echo "Frontend: http://34.93.19.177"
echo "Backend API: http://34.93.19.177/api/v1/"
echo "Admin Panel: http://34.93.19.177/admin/"
echo ""
echo "To view logs: sudo docker compose logs -f"
echo "To stop: sudo docker compose down"
echo "========================================="
