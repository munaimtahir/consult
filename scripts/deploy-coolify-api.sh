#!/bin/bash

# Coolify API Deployment Script
# This script deploys the consult application to Coolify using the API

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load configuration
CONFIG_FILE="$REPO_ROOT/coolify-api-config.env"
ENV_FILE="$REPO_ROOT/coolify-deploy.env"

if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}Error: Configuration file not found: $CONFIG_FILE${NC}"
    exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}Error: Environment file not found: $ENV_FILE${NC}"
    exit 1
fi

# Source configuration
source "$CONFIG_FILE"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Coolify API Deployment${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}Configuration:${NC}"
echo "  API URL: $COOLIFY_API_URL"
echo "  Server ID: $COOLIFY_SERVER_ID"
echo "  Project ID: $COOLIFY_PROJECT_ID"
echo "  Domain: $COOLIFY_DOMAIN"
echo "  Public IP: $COOLIFY_PUBLIC_IP"
echo ""

# Function to make API calls
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    local url="${COOLIFY_API_URL}${endpoint}"
    local headers=(
        -H "Authorization: Bearer $COOLIFY_API_TOKEN"
        -H "Content-Type: application/json"
        -H "Accept: application/json"
    )
    
    if [ "$method" = "GET" ]; then
        curl -s -X GET "${headers[@]}" "$url"
    elif [ "$method" = "POST" ]; then
        curl -s -X POST "${headers[@]}" -d "$data" "$url"
    elif [ "$method" = "PUT" ]; then
        curl -s -X PUT "${headers[@]}" -d "$data" "$url"
    elif [ "$method" = "PATCH" ]; then
        curl -s -X PATCH "${headers[@]}" -d "$data" "$url"
    fi
}

# Function to check API connectivity
check_api() {
    echo -e "${YELLOW}Checking API connectivity...${NC}"
    response=$(api_call "GET" "/servers" 2>&1)
    
    if echo "$response" | grep -q "error\|unauthorized\|401\|403"; then
        echo -e "${RED}Error: API authentication failed${NC}"
        echo "Response: $response"
        return 1
    fi
    
    echo -e "${GREEN}✓ API connection successful${NC}"
    return 0
}

# Function to get or create project
get_project() {
    echo -e "${YELLOW}Getting project: $COOLIFY_PROJECT_ID${NC}"
    response=$(api_call "GET" "/projects")
    
    # Try to find project by name/UUID
    project_id=$(echo "$response" | grep -o "\"uuid\":\"[^\"]*\"\|\"name\":\"$COOLIFY_PROJECT_ID\"" | head -1 | cut -d'"' -f4 || echo "")
    
    if [ -z "$project_id" ]; then
        echo -e "${YELLOW}Project not found, creating new project...${NC}"
        project_data="{\"name\":\"$COOLIFY_PROJECT_ID\"}"
        response=$(api_call "POST" "/projects" "$project_data")
        project_id=$(echo "$response" | grep -o "\"uuid\":\"[^\"]*\"" | head -1 | cut -d'"' -f4 || echo "$COOLIFY_PROJECT_ID")
    fi
    
    echo -e "${GREEN}✓ Project ID: $project_id${NC}"
    echo "$project_id"
}

# Function to check if application exists
check_application() {
    local project_id=$1
    local app_name="consult"
    
    echo -e "${YELLOW}Checking if application exists...${NC}"
    response=$(api_call "GET" "/projects/$project_id/applications")
    
    app_uuid=$(echo "$response" | grep -o "\"uuid\":\"[^\"]*\"\|\"name\":\"$app_name\"" | head -1 | cut -d'"' -f4 || echo "")
    
    if [ -n "$app_uuid" ]; then
        echo -e "${GREEN}✓ Application found: $app_uuid${NC}"
        echo "$app_uuid"
    else
        echo -e "${YELLOW}Application not found${NC}"
        echo ""
    fi
}

# Function to create application
create_application() {
    local project_id=$1
    
    echo -e "${YELLOW}Creating new Docker Compose application...${NC}"
    
    app_data=$(cat <<EOF
{
    "name": "consult",
    "description": "Hospital Consult System",
    "type": "dockercompose",
    "git_repository": "https://github.com/munaimtahir/consult",
    "git_branch": "main",
    "docker_compose_file": "docker-compose.coolify.yml",
    "server_id": "$COOLIFY_SERVER_ID"
}
EOF
)
    
    response=$(api_call "POST" "/projects/$project_id/applications" "$app_data")
    app_uuid=$(echo "$response" | grep -o "\"uuid\":\"[^\"]*\"" | head -1 | cut -d'"' -f4 || echo "")
    
    if [ -z "$app_uuid" ]; then
        echo -e "${RED}Error: Failed to create application${NC}"
        echo "Response: $response"
        return 1
    fi
    
    echo -e "${GREEN}✓ Application created: $app_uuid${NC}"
    echo "$app_uuid"
}

# Function to set environment variables
set_environment_variables() {
    local app_uuid=$1
    
    echo -e "${YELLOW}Setting environment variables...${NC}"
    
    # Read environment variables from file
    env_vars="{}"
    while IFS='=' read -r key value || [ -n "$key" ]; do
        # Skip comments and empty lines
        [[ "$key" =~ ^#.*$ ]] && continue
        [[ -z "$key" ]] && continue
        
        # Remove quotes from value if present
        value=$(echo "$value" | sed 's/^"\(.*\)"$/\1/')
        
        # Add to JSON object
        if [ "$env_vars" = "{}" ]; then
            env_vars="{\"$key\":\"$value\"}"
        else
            env_vars=$(echo "$env_vars" | jq ". + {\"$key\":\"$value\"}" 2>/dev/null || echo "$env_vars")
        fi
    done < "$ENV_FILE"
    
    # Set environment variables via API
    env_data="{\"environment_variables\":$env_vars}"
    response=$(api_call "POST" "/applications/$app_uuid/environment-variables" "$env_data" 2>&1)
    
    if echo "$response" | grep -q "error\|failed"; then
        echo -e "${YELLOW}Warning: May need to set environment variables manually in Coolify dashboard${NC}"
        echo "Response: $response"
    else
        echo -e "${GREEN}✓ Environment variables set${NC}"
    fi
}

# Function to configure domain
configure_domain() {
    local app_uuid=$1
    
    echo -e "${YELLOW}Configuring domain: $COOLIFY_DOMAIN${NC}"
    
    domain_data=$(cat <<EOF
{
    "domain": "$COOLIFY_DOMAIN",
    "enable_ssl": true,
    "force_https": true
}
EOF
)
    
    response=$(api_call "POST" "/applications/$app_uuid/domains" "$domain_data" 2>&1)
    
    if echo "$response" | grep -q "error\|already exists"; then
        echo -e "${YELLOW}Domain may already be configured or needs manual setup${NC}"
    else
        echo -e "${GREEN}✓ Domain configured${NC}"
    fi
}

# Function to trigger deployment
trigger_deployment() {
    local app_uuid=$1
    
    echo -e "${YELLOW}Triggering deployment...${NC}"
    
    deploy_data="{\"force_rebuild\":false}"
    response=$(api_call "POST" "/applications/$app_uuid/deploy" "$deploy_data" 2>&1)
    
    if echo "$response" | grep -q "error\|failed"; then
        echo -e "${RED}Error: Deployment trigger failed${NC}"
        echo "Response: $response"
        return 1
    fi
    
    echo -e "${GREEN}✓ Deployment triggered${NC}"
    echo ""
    echo -e "${BLUE}Deployment started. Monitor progress in Coolify dashboard:${NC}"
    echo "  http://$COOLIFY_PUBLIC_IP:8000"
    echo ""
}

# Function to validate deployment
validate_deployment() {
    echo -e "${YELLOW}Waiting for deployment to initialize (30 seconds)...${NC}"
    sleep 30
    
    echo -e "${YELLOW}Validating deployment...${NC}"
    
    # Check domain
    if curl -s -o /dev/null -w "%{http_code}" "https://$COOLIFY_DOMAIN/api/v1/health/" | grep -q "200\|301\|302"; then
        echo -e "${GREEN}✓ Domain is accessible${NC}"
    else
        echo -e "${YELLOW}⚠ Domain may not be ready yet (DNS propagation or SSL setup)${NC}"
    fi
    
    # Check public IP
    if curl -s -o /dev/null -w "%{http_code}" "http://$COOLIFY_PUBLIC_IP/api/v1/health/" | grep -q "200"; then
        echo -e "${GREEN}✓ Public IP is accessible${NC}"
    else
        echo -e "${YELLOW}⚠ Public IP endpoint not ready yet${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}Access points:${NC}"
    echo "  Domain: https://$COOLIFY_DOMAIN"
    echo "  Public IP: http://$COOLIFY_PUBLIC_IP"
    echo "  Dashboard: http://$COOLIFY_PUBLIC_IP:8000"
}

# Main deployment flow
main() {
    echo -e "${BLUE}Starting deployment process...${NC}"
    echo ""
    
    # Check API connectivity
    if ! check_api; then
        exit 1
    fi
    
    # Get or create project
    project_id=$(get_project)
    if [ -z "$project_id" ]; then
        echo -e "${RED}Error: Could not get/create project${NC}"
        exit 1
    fi
    
    # Check if application exists
    app_uuid=$(check_application "$project_id")
    
    # Create application if it doesn't exist
    if [ -z "$app_uuid" ]; then
        app_uuid=$(create_application "$project_id")
        if [ -z "$app_uuid" ]; then
            echo -e "${RED}Error: Could not create application${NC}"
            exit 1
        fi
    fi
    
    # Set environment variables
    set_environment_variables "$app_uuid"
    
    # Configure domain
    configure_domain "$app_uuid"
    
    # Trigger deployment
    if ! trigger_deployment "$app_uuid"; then
        echo -e "${YELLOW}Note: You may need to trigger deployment manually from Coolify dashboard${NC}"
    fi
    
    # Validate deployment
    validate_deployment
    
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Deployment process completed!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Monitor deployment in Coolify dashboard"
    echo "2. Check logs if any issues occur"
    echo "3. Verify DNS has propagated: nslookup $COOLIFY_DOMAIN"
    echo "4. Test endpoints after deployment completes"
}

# Run main function
main

