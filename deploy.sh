#!/bin/bash
# Deployment script for Hospital Consult System
# Server IP: 172.104.178.44

set -e

echo "========================================="
echo "Hospital Consult System - Deployment"
echo "Server IP: 172.104.178.44"
echo "========================================="

# Check if Docker is running
if ! sudo docker ps > /dev/null 2>&1; then
    echo "Starting Docker daemon..."
    sudo dockerd > /tmp/dockerd.log 2>&1 &
    sleep 5
fi

# Stop any existing containers
echo "Stopping existing containers..."
sudo docker-compose down 2>/dev/null || true

# Build images
echo "Building Docker images..."
sudo docker-compose build

# Start services
echo "Starting services..."
sudo docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Check service status
echo "Checking service status..."
sudo docker-compose ps

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo "Frontend: http://172.104.178.44"
echo "Backend API: http://172.104.178.44/api/v1/"
echo "Admin Panel: http://172.104.178.44/admin/"
echo ""
echo "To view logs: sudo docker-compose logs -f"
echo "To stop: sudo docker-compose down"
echo "========================================="
