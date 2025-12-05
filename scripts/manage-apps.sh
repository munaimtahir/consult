#!/bin/bash
# Multi-App Management Script
# Provides commands to manage multiple apps in the deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Function to show usage
show_usage() {
    echo "Multi-App Management Script"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  list                    List all apps and their status"
    echo "  status [app_name]       Show status of specific app or all apps"
    echo "  start [app_name]        Start specific app or all apps"
    echo "  stop [app_name]         Stop specific app or all apps"
    echo "  restart [app_name]      Restart specific app or all apps"
    echo "  logs [app_name]         Show logs for specific app"
    echo "  health [app_name]       Check health of specific app"
    echo "  validate                Validate configuration"
    echo ""
    echo "Examples:"
    echo "  $0 list"
    echo "  $0 status backend"
    echo "  $0 start backend frontend"
    echo "  $0 health backend"
}

# Function to list all apps
list_apps() {
    print_info "Listing all apps..."
    echo ""
    
    # Get all services from docker-compose
    services=$(docker compose config --services 2>/dev/null || docker-compose config --services 2>/dev/null)
    
    if [ -z "$services" ]; then
        print_error "Could not read docker-compose.yml"
        exit 1
    fi
    
    echo "Available services:"
    for service in $services; do
        status=$(docker compose ps --format json $service 2>/dev/null | grep -o '"State":"[^"]*"' | cut -d'"' -f4 || echo "unknown")
        if [ "$status" = "running" ]; then
            echo -e "  ${GREEN}●${NC} $service (running)"
        elif [ "$status" = "exited" ]; then
            echo -e "  ${YELLOW}○${NC} $service (stopped)"
        else
            echo -e "  ${RED}○${NC} $service (not running)"
        fi
    done
}

# Function to show status
show_status() {
    local app_name=$1
    
    if [ -z "$app_name" ]; then
        print_info "Showing status of all apps..."
        docker compose ps
    else
        print_info "Showing status of $app_name..."
        docker compose ps $app_name
    fi
}

# Function to start app
start_app() {
    local app_name=$1
    
    if [ -z "$app_name" ]; then
        print_info "Starting all apps..."
        docker compose up -d
        print_success "All apps started"
    else
        print_info "Starting $app_name..."
        docker compose up -d $app_name
        print_success "$app_name started"
    fi
}

# Function to stop app
stop_app() {
    local app_name=$1
    
    if [ -z "$app_name" ]; then
        print_warning "Stopping all apps..."
        docker compose down
        print_success "All apps stopped"
    else
        print_info "Stopping $app_name..."
        docker compose stop $app_name
        print_success "$app_name stopped"
    fi
}

# Function to restart app
restart_app() {
    local app_name=$1
    
    if [ -z "$app_name" ]; then
        print_info "Restarting all apps..."
        docker compose restart
        print_success "All apps restarted"
    else
        print_info "Restarting $app_name..."
        docker compose restart $app_name
        print_success "$app_name restarted"
    fi
}

# Function to show logs
show_logs() {
    local app_name=$1
    
    if [ -z "$app_name" ]; then
        print_info "Showing logs for all apps..."
        docker compose logs -f
    else
        print_info "Showing logs for $app_name..."
        docker compose logs -f $app_name
    fi
}

# Function to check health
check_health() {
    local app_name=$1
    
    if [ -z "$app_name" ]; then
        print_info "Checking health of all apps..."
        
        # Check backend
        if docker compose ps backend | grep -q "running"; then
            echo ""
            print_info "Checking backend health..."
            response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/health/ || echo "000")
            if [ "$response" = "200" ]; then
                print_success "Backend is healthy"
            else
                print_error "Backend health check failed (HTTP $response)"
            fi
        fi
        
        # Check frontend
        if docker compose ps frontend | grep -q "running"; then
            echo ""
            print_info "Checking frontend health..."
            response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ || echo "000")
            if [ "$response" = "200" ]; then
                print_success "Frontend is healthy"
            else
                print_error "Frontend health check failed (HTTP $response)"
            fi
        fi
        
        # Check nginx
        if docker compose ps nginx-proxy | grep -q "running"; then
            echo ""
            print_info "Checking nginx health..."
            response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/health || echo "000")
            if [ "$response" = "200" ]; then
                print_success "Nginx is healthy"
            else
                print_error "Nginx health check failed (HTTP $response)"
            fi
        fi
    else
        print_info "Checking health of $app_name..."
        
        case $app_name in
            backend)
                response=$(curl -s http://localhost/api/health/ || echo "")
                if echo "$response" | grep -q "healthy"; then
                    print_success "$app_name is healthy"
                    echo "$response" | jq . 2>/dev/null || echo "$response"
                else
                    print_error "$app_name health check failed"
                fi
                ;;
            frontend)
                response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ || echo "000")
                if [ "$response" = "200" ]; then
                    print_success "$app_name is healthy"
                else
                    print_error "$app_name health check failed (HTTP $response)"
                fi
                ;;
            nginx-proxy|nginx)
                response=$(curl -s http://localhost/health || echo "")
                if [ "$response" = "healthy" ]; then
                    print_success "$app_name is healthy"
                else
                    print_error "$app_name health check failed"
                fi
                ;;
            *)
                print_warning "Health check not implemented for $app_name"
                docker compose ps $app_name
                ;;
        esac
    fi
}

# Function to validate configuration
validate_config() {
    print_info "Validating configuration..."
    
    # Check docker-compose.yml
    if [ -f "docker-compose.yml" ]; then
        if docker compose config > /dev/null 2>&1; then
            print_success "docker-compose.yml is valid"
        else
            print_error "docker-compose.yml has errors"
            docker compose config
            exit 1
        fi
    else
        print_error "docker-compose.yml not found"
        exit 1
    fi
    
    # Check nginx config
    if [ -f "nginx/default.conf" ]; then
        if docker compose exec -T nginx-proxy nginx -t > /dev/null 2>&1; then
            print_success "Nginx configuration is valid"
        else
            print_warning "Nginx configuration check skipped (nginx-proxy not running)"
        fi
    else
        print_error "nginx/default.conf not found"
        exit 1
    fi
    
    # Run environment validation if script exists
    if [ -f "scripts/validate-env.sh" ]; then
        echo ""
        bash scripts/validate-env.sh
    fi
}

# Main command handler
case "${1:-}" in
    list)
        list_apps
        ;;
    status)
        show_status "$2"
        ;;
    start)
        shift
        for app in "$@"; do
            start_app "$app"
        done
        if [ $# -eq 0 ]; then
            start_app
        fi
        ;;
    stop)
        shift
        for app in "$@"; do
            stop_app "$app"
        done
        if [ $# -eq 0 ]; then
            stop_app
        fi
        ;;
    restart)
        shift
        for app in "$@"; do
            restart_app "$app"
        done
        if [ $# -eq 0 ]; then
            restart_app
        fi
        ;;
    logs)
        show_logs "$2"
        ;;
    health)
        check_health "$2"
        ;;
    validate)
        validate_config
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
