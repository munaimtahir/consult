#!/bin/bash
# Script to remove an app from the multi-app deployment
# Usage: ./scripts/remove-app.sh <app_name>

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <app_name>"
    echo ""
    echo "Arguments:"
    echo "  app_name - Name of the app to remove (e.g., app2, app3)"
    echo ""
    echo "Example:"
    echo "  $0 app2"
    exit 1
fi

APP_NAME=$1

print_warning "Removing app: $APP_NAME"
print_warning "This will remove the app from docker-compose.yml and nginx configuration"
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    print_info "Cancelled."
    exit 0
fi

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found"
    exit 1
fi

# Check if app exists
if ! grep -q "${APP_NAME}_backend:" docker-compose.yml; then
    print_error "App $APP_NAME not found in docker-compose.yml"
    exit 1
fi

# Stop and remove containers
print_info "Stopping and removing containers..."
docker-compose stop ${APP_NAME}_backend ${APP_NAME}_frontend 2>/dev/null || true
docker-compose rm -f ${APP_NAME}_backend ${APP_NAME}_frontend 2>/dev/null || true

# Create backup
print_info "Creating backup..."
cp docker-compose.yml docker-compose.yml.backup.$(date +%Y%m%d_%H%M%S)
cp nginx/default.conf nginx/default.conf.backup.$(date +%Y%m%d_%H%M%S)

# Remove from docker-compose.yml
print_info "Removing from docker-compose.yml..."

# Remove backend service
sed -i "/^  # ${APP_NAME^} App - Backend Service/,/^$/d" docker-compose.yml

# Remove frontend service
sed -i "/^  # ${APP_NAME^} App - Frontend Service/,/^$/d" docker-compose.yml

# Remove volumes
sed -i "/^  ${APP_NAME}_static_volume:/,/^$/d" docker-compose.yml
sed -i "/^  ${APP_NAME}_media_volume:/,/^$/d" docker-compose.yml

# Remove from nginx-proxy depends_on
sed -i "/${APP_NAME}_backend:/,/condition: service_healthy/d" docker-compose.yml
sed -i "/${APP_NAME}_frontend:/,/condition: service_healthy/d" docker-compose.yml

# Remove from nginx configuration
print_info "Removing from nginx configuration..."

# Remove rate limiting zones
sed -i "/# ${APP_NAME^} App - Rate limiting zones/,/limit_req_zone.*${APP_NAME}_ws_limit/d" nginx/default.conf

# Remove upstream definitions
sed -i "/upstream ${APP_NAME}_backend/,/^}/d" nginx/default.conf
sed -i "/upstream ${APP_NAME}_frontend/,/^}/d" nginx/default.conf

# Remove location blocks
sed -i "/# ${APP_NAME^} App - Health check endpoint/,/^    }$/d" nginx/default.conf
sed -i "/# ${APP_NAME^} App - API endpoints/,/^    }$/d" nginx/default.conf
sed -i "/# ${APP_NAME^} App - WebSocket endpoints/,/^    }$/d" nginx/default.conf
sed -i "/# ${APP_NAME^} App - Static files/,/^    }$/d" nginx/default.conf
sed -i "/# ${APP_NAME^} App - Media files/,/^    }$/d" nginx/default.conf
sed -i "/# ${APP_NAME^} App - Frontend/,/^    }$/d" nginx/default.conf

# Validate configurations
print_info "Validating configurations..."

if ! docker-compose config > /dev/null 2>&1; then
    print_error "docker-compose.yml has errors. Restoring backup..."
    mv docker-compose.yml.backup.* docker-compose.yml 2>/dev/null || true
    mv nginx/default.conf.backup.* nginx/default.conf 2>/dev/null || true
    exit 1
fi

# Test nginx config (if nginx is running)
if docker-compose ps nginx-proxy 2>/dev/null | grep -q "running"; then
    if ! docker-compose exec -T nginx-proxy nginx -t > /dev/null 2>&1; then
        print_error "Nginx configuration has errors. Restoring backup..."
        mv docker-compose.yml.backup.* docker-compose.yml 2>/dev/null || true
        mv nginx/default.conf.backup.* nginx/default.conf 2>/dev/null || true
        exit 1
    fi
    print_info "Restarting nginx-proxy..."
    docker-compose restart nginx-proxy
fi

print_success "App $APP_NAME removed successfully!"
print_info "Note: App directories and volumes were not removed. Remove them manually if needed."

