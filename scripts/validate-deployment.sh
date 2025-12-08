#!/bin/bash

# Deployment Validation Script
# This script validates that all services are running correctly after deployment

set -e

echo "=========================================="
echo "Docker Compose Deployment Validation"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if docker compose is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}ERROR: Docker is not installed or not in PATH${NC}"
    exit 1
fi

# Function to check service status
check_service() {
    local service=$1
    if docker compose ps | grep -q "$service.*Up"; then
        echo -e "${GREEN}✓${NC} $service is running"
        return 0
    else
        echo -e "${RED}✗${NC} $service is not running"
        return 1
    fi
}

# Function to check HTTP endpoint
check_endpoint() {
    local url=$1
    local expected_status=${2:-200}
    local description=$3
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✓${NC} $description (HTTP $response)"
        return 0
    else
        echo -e "${RED}✗${NC} $description (HTTP $response)"
        return 1
    fi
}

# Function to check service health
check_health() {
    local service=$1
    local health_status=$(docker compose ps --format json | jq -r ".[] | select(.Service==\"$service\") | .Health" 2>/dev/null || echo "unknown")
    if [ "$health_status" = "healthy" ]; then
        echo -e "${GREEN}✓${NC} $service health check: healthy"
        return 0
    elif [ "$health_status" = "starting" ]; then
        echo -e "${YELLOW}⚠${NC} $service health check: starting (may need more time)"
        return 0
    else
        echo -e "${RED}✗${NC} $service health check: $health_status"
        return 1
    fi
}

echo "1. Checking service status..."
echo "----------------------------------------"
services=("db" "redis" "backend" "frontend" "nginx-proxy")
all_services_up=true

for service in "${services[@]}"; do
    if ! check_service "$service"; then
        all_services_up=false
    fi
done

echo ""
echo "2. Checking service health..."
echo "----------------------------------------"
services_with_health=("db" "redis" "backend" "frontend" "nginx-proxy")
all_services_healthy=true

for service in "${services_with_health[@]}"; do
    if ! check_health "$service"; then
        all_services_healthy=false
    fi
done

echo ""
echo "3. Checking HTTP endpoints..."
echo "----------------------------------------"
all_endpoints_ok=true

# Wait a bit for services to be ready
sleep 2

if ! check_endpoint "http://localhost/health" "200" "Nginx health endpoint"; then
    all_endpoints_ok=false
fi

if ! check_endpoint "http://localhost/api/v1/health/" "200" "Backend health endpoint"; then
    all_endpoints_ok=false
fi

if ! check_endpoint "http://localhost/" "200" "Frontend homepage"; then
    all_endpoints_ok=false
fi

if ! check_endpoint "http://localhost/admin/" "200" "Admin panel"; then
    all_endpoints_ok=false
fi

echo ""
echo "4. Checking database connectivity..."
echo "----------------------------------------"
if docker compose exec -T db pg_isready -U consult_user -d consult_db > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Database is ready and accepting connections"
else
    echo -e "${RED}✗${NC} Database is not ready"
    all_endpoints_ok=false
fi

echo ""
echo "5. Checking Redis connectivity..."
echo "----------------------------------------"
if docker compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Redis is ready and accepting connections"
else
    echo -e "${RED}✗${NC} Redis is not ready"
    all_endpoints_ok=false
fi

echo ""
echo "6. Checking backend logs for errors..."
echo "----------------------------------------"
backend_errors=$(docker compose logs backend 2>&1 | grep -i "error\|exception\|traceback" | tail -5 || true)
if [ -z "$backend_errors" ]; then
    echo -e "${GREEN}✓${NC} No recent errors in backend logs"
else
    echo -e "${YELLOW}⚠${NC} Found potential errors in backend logs:"
    echo "$backend_errors"
fi

echo ""
echo "=========================================="
echo "Validation Summary"
echo "=========================================="

if [ "$all_services_up" = true ] && [ "$all_endpoints_ok" = true ]; then
    echo -e "${GREEN}✓ DEPLOYMENT SUCCESSFUL${NC}"
    echo ""
    echo "All services are running and endpoints are accessible."
    echo ""
    echo "Access the application at:"
    echo "  - Frontend: http://localhost"
    echo "  - API: http://localhost/api/v1/"
    echo "  - Admin: http://localhost/admin/"
    echo ""
    exit 0
else
    echo -e "${RED}✗ DEPLOYMENT ISSUES DETECTED${NC}"
    echo ""
    echo "Please check the errors above and review service logs:"
    echo "  docker compose logs [service_name]"
    echo ""
    exit 1
fi

