#!/bin/bash
# QUICK UPDATE FOR DATAGUARDIANPRO.NL
# Fixes license check errors and enables all scanners

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════${NC}"
echo -e "${BLUE}   QUICK UPDATE - DataGuardian Pro  ${NC}"
echo -e "${BLUE}═══════════════════════════════════${NC}"
echo ""

# Check if running on server
if [ ! -d "/opt/dataguardian" ]; then
    echo "Error: /opt/dataguardian not found!"
    echo "Run this script on the dataguardianpro.nl server"
    exit 1
fi

cd /opt/dataguardian

echo "1. Extracting updated code..."
tar -xzf /tmp/dataguardian_complete.tar.gz --overwrite app.py

echo -e "${GREEN}✅ Code updated${NC}"

echo ""
echo "2. Clearing Python cache..."
find . -name "*.pyc" -delete 2>/dev/null || true
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

echo -e "${GREEN}✅ Cache cleared${NC}"

echo ""
echo "3. Rebuilding Docker image..."
docker build --no-cache -t dataguardian-pro . > /tmp/docker_build.log 2>&1

echo -e "${GREEN}✅ Image rebuilt${NC}"

echo ""
echo "4. Restarting container..."
docker rm -f dataguardian-container 2>/dev/null || true

docker run -d \
    --name dataguardian-container \
    --restart always \
    --network host \
    --env-file /root/.dataguardian_env \
    dataguardian-pro

echo -e "${GREEN}✅ Container restarted${NC}"

echo ""
echo "5. Waiting for startup (30 seconds)..."
sleep 30

echo ""
echo "6. Checking logs for errors..."
ERROR_COUNT=$(docker logs dataguardian-container 2>&1 | grep -ic "error\|exception\|traceback" || true)

if [ "$ERROR_COUNT" -gt 5 ]; then
    echo -e "${BLUE}⚠️  Found some errors in logs${NC}"
    echo "Showing last 30 lines:"
    docker logs dataguardian-container 2>&1 | tail -30
else
    echo -e "${GREEN}✅ No critical errors found${NC}"
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════${NC}"
echo -e "${GREEN}   ✅ UPDATE COMPLETE!              ${NC}"
echo -e "${GREEN}═══════════════════════════════════${NC}"
echo ""
echo "Test at: https://dataguardianpro.nl"
echo "Login: vishaal314 / vishaal2024"
echo ""
echo -e "${BLUE}Remember: Use INCOGNITO browser (Ctrl+Shift+N)${NC}"
