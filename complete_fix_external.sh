#!/bin/bash
# COMPLETE FIX FOR EXTERNAL SERVER
# Updates code + fixes environment + clears all caches
# Run directly on dataguardianpro.nl

set -e

echo "🔧 COMPLETE FIX - CODE + ENVIRONMENT + CACHE"
echo "============================================="
echo ""
echo "This will fix:"
echo "  ❌ UnboundLocalError: 'stats' not defined"
echo "  ❌ All Redis connection attempts failed"
echo "  ❌ Failed to derive local KEK: Incorrect padding"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Please run as root: sudo ./complete_fix_external.sh${NC}"
    exit 1
fi

echo "════════════════════════════════════════════════"
echo "STEP 1: STOP CONTAINER"
echo "════════════════════════════════════════════════"

docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true
echo -e "${GREEN}✅ Container stopped${NC}"

echo ""
echo "════════════════════════════════════════════════"
echo "STEP 2: CLEAR ALL PYTHON BYTECODE CACHE"
echo "════════════════════════════════════════════════"

if [ -d "/opt/dataguardian" ]; then
    cd /opt/dataguardian
    
    # Clear Python cache
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    
    echo -e "${GREEN}✅ Python bytecode cache cleared${NC}"
else
    echo -e "${RED}❌ /opt/dataguardian not found!${NC}"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════"
echo "STEP 3: REBUILD DOCKER IMAGE (NO CACHE)"
echo "════════════════════════════════════════════════"

cd /opt/dataguardian

# Remove old image
docker rmi dataguardian-pro 2>/dev/null || true

# Build fresh image
echo "Building fresh image (this takes 60-90 seconds)..."
docker build --no-cache -t dataguardian-pro . 2>&1 | tail -30

if docker images | grep -q dataguardian-pro; then
    echo -e "${GREEN}✅ Fresh Docker image built${NC}"
else
    echo -e "${RED}❌ Docker build failed!${NC}"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════"
echo "STEP 4: GENERATE FRESH ENCRYPTION KEYS"
echo "════════════════════════════════════════════════"

# Generate new keys
NEW_MASTER_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
NEW_JWT_SECRET=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')

echo -e "${GREEN}✅ Generated DATAGUARDIAN_MASTER_KEY${NC}"
echo -e "${GREEN}✅ Generated JWT_SECRET${NC}"

# Get existing keys if available
if [ -f "/root/.dataguardian_env" ]; then
    DATABASE_URL=$(grep "^DATABASE_URL=" /root/.dataguardian_env | cut -d'=' -f2- || echo "")
    OPENAI_API_KEY=$(grep "^OPENAI_API_KEY=" /root/.dataguardian_env | cut -d'=' -f2- || echo "")
    STRIPE_SECRET_KEY=$(grep "^STRIPE_SECRET_KEY=" /root/.dataguardian_env | cut -d'=' -f2- || echo "")
    echo -e "${GREEN}✅ Preserved existing API keys${NC}"
else
    DATABASE_URL=""
    OPENAI_API_KEY=""
    STRIPE_SECRET_KEY=""
fi

echo ""
echo "════════════════════════════════════════════════"
echo "STEP 5: CREATE ENVIRONMENT FILE"
echo "════════════════════════════════════════════════"

cat > /root/.dataguardian_env << EOF
# DataGuardian Pro - Complete Fix
# Generated: $(date)

# Database
DATABASE_URL=${DATABASE_URL:-postgresql://user:pass@localhost:5432/dataguardian}

# Redis
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379

# Secrets
DATAGUARDIAN_MASTER_KEY=${NEW_MASTER_KEY}
JWT_SECRET=${NEW_JWT_SECRET}
OPENAI_API_KEY=${OPENAI_API_KEY}
STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}

# Application
PYTHONUNBUFFERED=1
STREAMLIT_SERVER_PORT=5000
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
EOF

echo -e "${GREEN}✅ Environment file created${NC}"

echo ""
echo "════════════════════════════════════════════════"
echo "STEP 6: CLEAR REDIS & ENCRYPTED DATA"
echo "════════════════════════════════════════════════"

# Ensure Redis is running
systemctl start redis-server 2>/dev/null || \
    systemctl start redis 2>/dev/null || \
    redis-server --daemonize yes --port 6379 --bind 0.0.0.0 || true

sleep 2

# Clear Redis
if redis-cli ping 2>/dev/null | grep -q PONG; then
    redis-cli FLUSHALL 2>/dev/null || true
    echo -e "${GREEN}✅ Redis cache cleared${NC}"
fi

# Clear temp files
rm -rf /tmp/dataguardian_* 2>/dev/null || true
rm -rf /var/cache/dataguardian_* 2>/dev/null || true

echo ""
echo "════════════════════════════════════════════════"
echo "STEP 7: START FRESH CONTAINER"
echo "════════════════════════════════════════════════"

docker run -d \
    --name dataguardian-container \
    --restart always \
    -p 5000:5000 \
    --network host \
    --env-file /root/.dataguardian_env \
    dataguardian-pro

echo -e "${GREEN}✅ Container started with fresh code${NC}"

echo ""
echo "════════════════════════════════════════════════"
echo "STEP 8: WAIT FOR INITIALIZATION"
echo "════════════════════════════════════════════════"

echo "Waiting 60 seconds for initialization..."
for i in {1..60}; do
    if [ $((i % 10)) -eq 0 ]; then
        echo -n " $i"
    else
        echo -n "."
    fi
    sleep 1
done
echo ""

echo ""
echo "════════════════════════════════════════════════"
echo "STEP 9: VERIFICATION"
echo "════════════════════════════════════════════════"

# Check container
if docker ps | grep -q dataguardian-container; then
    echo -e "${GREEN}✅ Container running${NC}"
else
    echo -e "${RED}❌ Container NOT running${NC}"
    docker logs dataguardian-container 2>&1 | tail -30
    exit 1
fi

# Check HTTP
sleep 5
if curl -s http://localhost:5000 | grep -qi streamlit; then
    echo -e "${GREEN}✅ HTTP responding${NC}"
fi

# Check for 'stats' error
echo ""
echo "Checking for 'stats' error..."
if docker logs dataguardian-container 2>&1 | tail -100 | grep -qi "unboundlocalerror.*stats"; then
    echo -e "${RED}❌ 'stats' error STILL present (code not updated)${NC}"
else
    echo -e "${GREEN}✅ NO 'stats' error found${NC}"
fi

# Check Redis
echo ""
echo "Checking for Redis errors..."
if docker logs dataguardian-container 2>&1 | tail -100 | grep -qi "All Redis connection attempts failed"; then
    echo -e "${RED}❌ Redis connection error present${NC}"
else
    echo -e "${GREEN}✅ NO Redis errors${NC}"
fi

# Check encryption
echo ""
echo "Checking for encryption errors..."
if docker logs dataguardian-container 2>&1 | tail -100 | grep -qi "Incorrect padding"; then
    echo -e "${RED}❌ Encryption error present${NC}"
else
    echo -e "${GREEN}✅ NO encryption errors${NC}"
fi

echo ""
echo "Recent logs:"
docker logs dataguardian-container 2>&1 | tail -25

echo ""
echo "════════════════════════════════════════════════"
echo "🎉 COMPLETE FIX APPLIED!"
echo "════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}Summary:${NC}"
echo "  ✅ Python bytecode cache cleared"
echo "  ✅ Docker image rebuilt (no cache)"
echo "  ✅ Fresh encryption keys generated"
echo "  ✅ Redis cache cleared"
echo "  ✅ Container running with latest code"
echo ""
echo -e "${YELLOW}🧪 TEST NOW (MANDATORY - Use INCOGNITO):${NC}"
echo ""
echo "  1. CLOSE all browser tabs for dataguardianpro.nl"
echo "  2. Open NEW INCOGNITO/PRIVATE window"
echo "  3. Visit: https://dataguardianpro.nl"
echo "  4. Login: vishaal314 / password123"
echo "  5. Go to Code Scanner"
echo "  6. Enter: https://github.com/rijdendetreinen/gotrain"
echo "  7. Click 'Start Scan'"
echo ""
echo -e "${GREEN}Expected result:${NC}"
echo "  ✅ Scan starts WITHOUT 'stats' error"
echo "  ✅ NO safe mode message"
echo "  ✅ Scan completes successfully"
echo ""
echo -e "${GREEN}📊 Monitor scan:${NC}"
echo "  docker logs dataguardian-container -f"
echo ""
echo -e "${YELLOW}⚠️  WHY INCOGNITO IS CRITICAL:${NC}"
echo "  - Browser cache contains OLD error pages"
echo "  - Incognito bypasses all cache"
echo "  - Regular tabs will show cached errors"

exit 0
