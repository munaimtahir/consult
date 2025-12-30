#!/bin/bash
# Script to prepare and deploy consult.alshifalab.pk via Coolify

set -e

DOMAIN="consult.alshifalab.pk"
REPO_PATH="/home/munaim/repos/consult"

echo "========================================="
echo "Coolify Deployment Preparation"
echo "Domain: $DOMAIN"
echo "========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}✓${NC} Configuration files prepared"
echo -e "${GREEN}✓${NC} Environment variables configured for $DOMAIN"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Access Coolify Dashboard: http://localhost:8000"
echo "2. Create new Docker Compose resource"
echo "3. Add domain: $DOMAIN"
echo "4. Set environment variables from .env.coolify"
echo "5. Deploy"
echo ""
echo "See COOLIFY_DEPLOY_INSTRUCTIONS.md for detailed steps"
echo "========================================="


