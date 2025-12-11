#!/bin/bash
# Script to add a new app to the multi-app deployment
# Usage: ./scripts/add-app.sh <app_name> <app_path> [backend_port] [frontend_port]

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
if [ $# -lt 2 ]; then
    echo "Usage: $0 <app_name> <app_path> [backend_port] [frontend_port]"
    echo ""
    echo "Arguments:"
    echo "  app_name      - Name of the app (e.g., app2, app3)"
    echo "  app_path      - Path prefix for the app (e.g., /app2, /app3)"
    echo "  backend_port  - Backend port (default: 8000)"
    echo "  frontend_port - Frontend port (default: 80)"
    echo ""
    echo "Example:"
    echo "  $0 app2 /app2 8000 80"
    exit 1
fi

APP_NAME=$1
APP_PATH=$2
BACKEND_PORT=${3:-8000}
FRONTEND_PORT=${4:-80}

# Validate app name (alphanumeric and underscores only)
if [[ ! $APP_NAME =~ ^[a-z0-9_]+$ ]]; then
    print_error "App name must be lowercase alphanumeric with underscores only"
    exit 1
fi

# Validate app path (must start with /)
if [[ ! $APP_PATH =~ ^/ ]]; then
    print_error "App path must start with /"
    exit 1
fi

print_info "Adding app: $APP_NAME"
print_info "App path: $APP_PATH"
print_info "Backend port: $BACKEND_PORT"
print_info "Frontend port: $FRONTEND_PORT"

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found"
    exit 1
fi

# Check if app already exists
if grep -q "${APP_NAME}_backend:" docker-compose.yml || grep -q "${APP_NAME}_frontend:" docker-compose.yml; then
    print_error "App $APP_NAME already exists in docker-compose.yml"
    exit 1
fi

# Check if nginx config exists
if [ ! -f "nginx/default.conf" ]; then
    print_error "nginx/default.conf not found"
    exit 1
fi

# Check if nginx config already has this app
if grep -q "location ${APP_PATH}" nginx/default.conf; then
    print_error "App path $APP_PATH already exists in nginx configuration"
    exit 1
fi

# Create backup
print_info "Creating backup..."
cp docker-compose.yml docker-compose.yml.backup.$(date +%Y%m%d_%H%M%S)
cp nginx/default.conf nginx/default.conf.backup.$(date +%Y%m%d_%H%M%S)

# Generate docker-compose service configuration
print_info "Generating docker-compose configuration..."

BACKEND_SERVICE=$(cat <<EOF
  # ${APP_NAME^} App - Backend Service
  ${APP_NAME}_backend:
    build: ./${APP_NAME}/backend
    expose:
      - "${BACKEND_PORT}"
    volumes:
      - ./${APP_NAME}/backend:/app
      - ${APP_NAME}_static_volume:/app/staticfiles
      - ${APP_NAME}_media_volume:/app/media
    environment:
      - DEBUG=0
      - SECRET_KEY=change_me_in_prod
      - ALLOWED_HOSTS=localhost,127.0.0.1,${APP_NAME}_backend,172.104.53.127
      - DATABASE=postgres
      - DB_NAME=consult_db
      - DB_USER=consult_user
      - DB_PASSWORD=consult_password
      - DB_HOST=db
      - DB_PORT=5432
      - REDIS_URL=redis://redis:6379/0
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - CORS_ALLOWED_ORIGINS=http://172.104.53.127,http://localhost:3000,http://localhost
      - CSRF_TRUSTED_ORIGINS=http://172.104.53.127,http://localhost:3000,http://localhost
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - consult_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:${BACKEND_PORT}/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M

  # ${APP_NAME^} App - Frontend Service
  ${APP_NAME}_frontend:
    build:
      context: ./${APP_NAME}/frontend
      args:
        - VITE_API_URL=http://172.104.53.127${APP_PATH}/api
    expose:
      - "${FRONTEND_PORT}"
    depends_on:
      ${APP_NAME}_backend:
        condition: service_healthy
    networks:
      - consult_network
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:${FRONTEND_PORT}/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M

EOF
)

# Add services to docker-compose.yml before nginx-proxy
print_info "Adding services to docker-compose.yml..."
sed -i "/^  # Nginx Reverse Proxy/i\\$BACKEND_SERVICE" docker-compose.yml

# Add volumes
print_info "Adding volumes to docker-compose.yml..."
VOLUMES_CONFIG=$(cat <<EOF
  ${APP_NAME}_static_volume:
    driver: local
  ${APP_NAME}_media_volume:
    driver: local
EOF
)

sed -i "/^volumes:/a\\$VOLUMES_CONFIG" docker-compose.yml

# Generate nginx configuration
print_info "Generating nginx configuration..."

NGINX_CONFIG=$(cat <<EOF

# ${APP_NAME^} App - Rate limiting zones
limit_req_zone \$binary_remote_addr zone=${APP_NAME}_api_limit:10m rate=100r/m;
limit_req_zone \$binary_remote_addr zone=${APP_NAME}_ws_limit:10m rate=10r/m;

# ${APP_NAME^} App - Upstream definitions
upstream ${APP_NAME}_backend {
    server ${APP_NAME}_backend:${BACKEND_PORT} max_fails=3 fail_timeout=30s;
}

upstream ${APP_NAME}_frontend {
    server ${APP_NAME}_frontend:${FRONTEND_PORT} max_fails=3 fail_timeout=30s;
}

# ${APP_NAME^} App - Health check endpoint
    location ${APP_PATH}/api/health/ {
        proxy_pass http://${APP_NAME}_backend;
        proxy_set_header Host \$host;
        access_log off;
    }

    # ${APP_NAME^} App - API endpoints
    location ${APP_PATH}/api/ {
        limit_req zone=${APP_NAME}_api_limit burst=20 nodelay;
        
        proxy_pass http://${APP_NAME}_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Forwarded-Port \$server_port;
        
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;
        proxy_next_upstream_tries 2;
        proxy_next_upstream_timeout 10s;
    }

    # ${APP_NAME^} App - WebSocket endpoints (if needed)
    location ${APP_PATH}/ws/ {
        limit_req zone=${APP_NAME}_ws_limit burst=5 nodelay;
        
        proxy_pass http://${APP_NAME}_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Forwarded-Port \$server_port;
        proxy_read_timeout 86400s;
        proxy_buffering off;
    }

    # ${APP_NAME^} App - Static files
    location ${APP_PATH}/static/ {
        alias /app/${APP_NAME}/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # ${APP_NAME^} App - Media files
    location ${APP_PATH}/media/ {
        alias /app/${APP_NAME}/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # ${APP_NAME^} App - Frontend
    location ${APP_PATH}/ {
        proxy_pass http://${APP_NAME}_frontend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Forwarded-Port \$server_port;
        
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;
        proxy_next_upstream_tries 2;
    }

EOF
)

# Add rate limiting zones at the top
sed -i "/^# Rate limiting zones/i\\$(echo "$NGINX_CONFIG" | head -n 3)" nginx/default.conf

# Add upstream definitions after consult app upstreams
sed -i "/^upstream consult_frontend/a\\$(echo "$NGINX_CONFIG" | sed -n '5,8p')" nginx/default.conf

# Add location blocks before the error pages section
sed -i "/^    # Error pages/i\\$(echo "$NGINX_CONFIG" | tail -n +9)" nginx/default.conf

# Update nginx-proxy depends_on
print_info "Updating nginx-proxy dependencies..."
sed -i "/nginx-proxy:/,/depends_on:/{ /depends_on:/a\\
      ${APP_NAME}_backend:\\
        condition: service_healthy\\
      ${APP_NAME}_frontend:\\
        condition: service_healthy
}" docker-compose.yml

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
fi

print_success "App $APP_NAME added successfully!"
echo ""
print_info "Next steps:"
echo "  1. Create app directory structure:"
echo "     mkdir -p ${APP_NAME}/{backend,frontend}"
echo "  2. Add your app code to ${APP_NAME}/backend and ${APP_NAME}/frontend"
echo "  3. Update environment variables in docker-compose.yml if needed"
echo "  4. Build and start the app:"
echo "     docker-compose build ${APP_NAME}_backend ${APP_NAME}_frontend"
echo "     docker-compose up -d ${APP_NAME}_backend ${APP_NAME}_frontend"
echo "  5. Restart nginx-proxy:"
echo "     docker-compose restart nginx-proxy"
echo ""
print_info "App will be accessible at: http://172.104.53.127${APP_PATH}"

