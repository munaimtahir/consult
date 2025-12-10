#!/bin/bash
# Script to update server IP addresses on the deployment server
# Run this script on the server: bash update-server-ip.sh

set -e

NEW_IP="172.104.178.44"
OLD_IPS=("3.233.180.130" "18.220.252.164" "34.93.19.177")

echo "========================================="
echo "Updating Server IP Configuration"
echo "New IP: $NEW_IP"
echo "========================================="

# Update deploy.sh
echo "Updating deploy.sh..."
sed -i "s/3\.233\.180\.130/$NEW_IP/g" deploy.sh
sed -i "s/18\.220\.252\.164/$NEW_IP/g" deploy.sh
sed -i "s/34\.93\.19\.177/$NEW_IP/g" deploy.sh
echo "✅ deploy.sh updated"

# Update docker-compose.yml
echo "Updating docker-compose.yml..."
sed -i "s/3\.233\.180\.130/$NEW_IP/g" docker-compose.yml
sed -i "s/18\.220\.252\.164/$NEW_IP/g" docker-compose.yml
sed -i "s/34\.93\.19\.177/$NEW_IP/g" docker-compose.yml
echo "✅ docker-compose.yml updated"

# Update nginx/default.conf
echo "Updating nginx/default.conf..."
sed -i "s/3\.233\.180\.130/$NEW_IP/g" nginx/default.conf
sed -i "s/18\.220\.252\.164/$NEW_IP/g" nginx/default.conf
sed -i "s/34\.93\.19\.177/$NEW_IP/g" nginx/default.conf
echo "✅ nginx/default.conf updated"

echo ""
echo "========================================="
echo "Verification"
echo "========================================="

echo "Checking deploy.sh:"
grep -n "$NEW_IP" deploy.sh | head -3 || echo "⚠️  No matches found"

echo ""
echo "Checking docker-compose.yml:"
grep -n "$NEW_IP" docker-compose.yml | head -3 || echo "⚠️  No matches found"

echo ""
echo "Checking nginx/default.conf:"
grep -n "$NEW_IP" nginx/default.conf | head -3 || echo "⚠️  No matches found"

echo ""
echo "========================================="
echo "Update Complete!"
echo "========================================="
echo "Now run: ./deploy.sh"
echo "========================================="

