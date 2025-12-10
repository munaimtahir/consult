#!/bin/bash
# Deployment script for Hospital Consult System
# Server IP: 172.104.178.44

set -e

echo "========================================="
echo "Hospital Consult System - Deployment"
echo "Server IP: 172.104.178.44"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}→${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if Docker is running
if ! sudo docker ps > /dev/null 2>&1; then
    print_info "Starting Docker daemon..."
    sudo dockerd > /tmp/dockerd.log 2>&1 &
    sleep 5
    
    # Verify Docker started
    if ! sudo docker ps > /dev/null 2>&1; then
        print_error "Failed to start Docker daemon. Please check Docker installation."
        exit 1
    fi
fi

print_success "Docker is running"

# Stop any existing containers
echo ""
print_info "Stopping existing containers..."
sudo docker-compose down 2>/dev/null || true
print_success "Existing containers stopped"

# Build images
echo ""
print_info "Building Docker images..."
if sudo docker-compose build; then
    print_success "Docker images built successfully"
else
    print_error "Failed to build Docker images"
    exit 1
fi

# Start services
echo ""
print_info "Starting services..."
if sudo docker-compose up -d; then
    print_success "Services started"
else
    print_error "Failed to start services"
    exit 1
fi

# Wait for services to be ready
echo ""
print_info "Waiting for services to be healthy..."
max_wait=120
wait_time=0
all_healthy=false

while [ $wait_time -lt $max_wait ]; do
    # Check if backend is healthy
    if sudo docker-compose exec -T backend curl -f http://localhost:8000/api/v1/health/ > /dev/null 2>&1; then
        print_success "Backend is healthy"
        all_healthy=true
        break
    fi
    sleep 2
    wait_time=$((wait_time + 2))
    echo -n "."
done

if [ "$all_healthy" = false ]; then
    print_error "Backend did not become healthy within ${max_wait} seconds"
    echo ""
    print_info "Checking service logs..."
    sudo docker-compose logs --tail=50 backend
    exit 1
fi

# Wait a bit more for frontend and nginx
sleep 5

# Check service status
echo ""
print_info "Checking service status..."
sudo docker-compose ps

# Verify seed data was created
echo ""
print_info "Verifying seed data was created..."
sleep 3

# Check backend logs for seed data confirmation
if sudo docker-compose logs backend | grep -q "Database seeding completed successfully"; then
    print_success "Seed data creation confirmed in logs"
else
    print_error "Could not confirm seed data creation in logs"
    echo ""
    print_info "Backend logs (last 30 lines):"
    sudo docker-compose logs --tail=30 backend
fi

# Test health endpoints
echo ""
print_info "Testing health endpoints..."

# Test backend health
if curl -f http://localhost/api/v1/health/ > /dev/null 2>&1 || curl -f http://172.104.178.44/api/v1/health/ > /dev/null 2>&1; then
    print_success "Backend health endpoint is accessible"
else
    print_error "Backend health endpoint is not accessible"
fi

# Test nginx health
if curl -f http://localhost/health > /dev/null 2>&1 || curl -f http://172.104.178.44/health > /dev/null 2>&1; then
    print_success "Nginx health endpoint is accessible"
else
    print_error "Nginx health endpoint is not accessible"
fi

echo ""
echo "========================================="
print_success "Deployment Complete!"
echo "========================================="
echo ""
echo "Access Points:"
echo "  Frontend:    http://172.104.178.44"
echo "  Backend API: http://172.104.178.44/api/v1/"
echo "  Admin Panel: http://172.104.178.44/admin/"
echo ""
echo "Demo Credentials:"
echo "  Superuser: admin@pmc.edu.pk / adminpassword123"
echo "  Admin:     sysadmin@pmc.edu.pk / password123"
echo "  HOD:       [dept].hod@pmc.edu.pk / password123"
echo "  Doctor:    [dept].doc@pmc.edu.pk / password123"
echo ""
echo "Useful Commands:"
echo "  View logs:    sudo docker-compose logs -f [service]"
echo "  View all:     sudo docker-compose logs -f"
echo "  Stop:         sudo docker-compose down"
echo "  Restart:      sudo docker-compose restart [service]"
echo "========================================="
