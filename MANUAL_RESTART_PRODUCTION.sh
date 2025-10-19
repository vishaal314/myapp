#!/bin/bash
#
# MANUAL RESTART - For when docker-compose.yml is missing
# Run this on: root@dataguardianpro.nl
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=========================================="
echo "Manual Docker Container Restart"
echo "dataguardianpro.nl"
echo -e "==========================================${NC}"
echo ""

# Load environment if exists
if [ -f "/root/.dataguardian_env" ]; then
    source /root/.dataguardian_env
    echo -e "${GREEN}✅ Environment loaded${NC}"
else
    echo -e "${YELLOW}⚠️  No environment file found${NC}"
fi

echo ""

# Find DataGuardian containers
echo "🔍 Finding DataGuardian containers..."
CONTAINERS=$(docker ps -a --filter "name=dataguardian" --format "{{.Names}}" | head -10)

if [ -z "$CONTAINERS" ]; then
    echo -e "${RED}❌ No DataGuardian containers found${NC}"
    echo ""
    echo "Available containers:"
    docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
    exit 1
fi

echo -e "${GREEN}Found containers:${NC}"
echo "$CONTAINERS" | while read container; do
    echo "  • $container"
done
echo ""

# Stop containers
echo "🛑 Stopping containers..."
echo "$CONTAINERS" | while read container; do
    docker stop "$container" 2>/dev/null || echo "  Already stopped: $container"
done

# Remove containers
echo "🗑️  Removing old containers..."
echo "$CONTAINERS" | while read container; do
    docker rm "$container" 2>/dev/null || echo "  Already removed: $container"
done

# Clear build cache
echo "🗑️  Clearing Docker cache..."
docker builder prune -f || true

echo ""
echo -e "${YELLOW}=========================================="
echo "⚠️  MANUAL ACTION REQUIRED"
echo -e "==========================================${NC}"
echo ""
echo "Containers stopped. To complete the restart:"
echo ""
echo "1️⃣  If you have docker-compose.yml:"
echo "   ${CYAN}cd /opt/dataguardian${NC}"
echo "   ${CYAN}docker-compose up -d${NC}"
echo ""
echo "2️⃣  If you DON'T have docker-compose.yml:"
echo "   You need to copy it from Replit:"
echo ""
echo "   ${YELLOW}On your local machine:${NC}"
echo "   ${CYAN}scp docker-compose.yml root@dataguardianpro.nl:/opt/dataguardian/${NC}"
echo ""
echo "   ${YELLOW}Then on server:${NC}"
echo "   ${CYAN}cd /opt/dataguardian${NC}"
echo "   ${CYAN}docker-compose up -d${NC}"
echo ""
echo "3️⃣  Check status:"
echo "   ${CYAN}docker ps${NC}"
echo ""
