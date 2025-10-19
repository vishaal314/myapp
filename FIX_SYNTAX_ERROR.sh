#!/bin/bash
#
# Fix Syntax Error - Copy fixed app.py to server and rebuild
# Run this script from your LOCAL machine (where you have Replit files)
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=========================================="
echo "Fix Syntax Error & Rebuild"
echo "=========================================="
echo ""

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo -e "${RED}❌ app.py not found in current directory${NC}"
    echo "Please run this script from your Replit project directory"
    exit 1
fi

echo -e "${GREEN}✅ app.py found${NC}"
echo ""

# Copy fixed app.py to server
echo "📤 Copying fixed app.py to server..."
scp app.py root@dataguardianpro.nl:/opt/dataguardian/

echo -e "${GREEN}✅ File copied${NC}"
echo ""

# SSH to server and rebuild
echo "🔨 Rebuilding container on server..."
ssh root@dataguardianpro.nl << 'ENDSSH'
set -e

echo "📁 Navigating to /opt/dataguardian..."
cd /opt/dataguardian

echo "🛑 Stopping old container..."
docker stop dataguardian-container || true
docker rm dataguardian-container || true

echo "🗑️  Clearing Docker cache..."
docker builder prune -f

echo "🔨 Rebuilding image (no cache)..."
docker build --no-cache -t dataguardian:latest .

echo "🚀 Starting new container..."
docker run -d \
  --name dataguardian-container \
  --env-file /root/.dataguardian_env \
  -p 5000:5000 \
  --health-cmd="curl -f http://localhost:5000 || exit 1" \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  dataguardian:latest

echo "⏳ Waiting 30 seconds for startup..."
sleep 30

echo ""
echo "📊 Container Status:"
docker ps | grep dataguardian

echo ""
echo "📜 Recent Logs:"
docker logs --tail 20 dataguardian-container

ENDSSH

echo ""
echo -e "${GREEN}=========================================="
echo "✅ COMPLETE"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Visit: https://dataguardianpro.nl/payment_test_ideal"
echo "2. Hard refresh: Ctrl+Shift+R"
echo "3. Verify: 16 scanners (NO Blob Scan)"
echo -e "${NC}"
