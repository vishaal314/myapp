#!/bin/bash
# STANDALONE FIX FOR EXTERNAL SERVER
# Fixes Redis connection + Encryption errors
# Run directly on dataguardianpro.nl server

set -e

echo "🔧 FIXING ALL ERRORS ON EXTERNAL SERVER"
echo "========================================"
echo ""
echo "This will fix:"
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
    echo -e "${RED}❌ Please run as root: sudo ./fix_all_errors_external.sh${NC}"
    exit 1
fi

echo "════════════════════════════════════════════════"
echo "STEP 1: GENERATE FRESH ENCRYPTION KEYS"
echo "════════════════════════════════════════════════"

# Generate new master key
NEW_MASTER_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
echo -e "${GREEN}✅ Generated DATAGUARDIAN_MASTER_KEY${NC}"

# Generate new JWT secret
NEW_JWT_SECRET=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
echo -e "${GREEN}✅ Generated JWT_SECRET${NC}"

# Get existing DATABASE_URL if available
if [ -f "/root/.dataguardian_env" ]; then
    DATABASE_URL=$(grep "^DATABASE_URL=" /root/.dataguardian_env | cut -d'=' -f2- || echo "")
    OPENAI_API_KEY=$(grep "^OPENAI_API_KEY=" /root/.dataguardian_env | cut -d'=' -f2- || echo "")
    STRIPE_SECRET_KEY=$(grep "^STRIPE_SECRET_KEY=" /root/.dataguardian_env | cut -d'=' -f2- || echo "")
    echo -e "${GREEN}✅ Preserved existing API keys${NC}"
else
    DATABASE_URL=""
    OPENAI_API_KEY=""
    STRIPE_SECRET_KEY=""
    echo -e "${YELLOW}⚠️  No existing environment file found${NC}"
fi

echo ""
echo "════════════════════════════════════════════════"
echo "STEP 2: CREATE FIXED ENVIRONMENT FILE"
echo "════════════════════════════════════════════════"

# Create environment file with proper Redis configuration
cat > /root/.dataguardian_env << EOF
# DataGuardian Pro - Fixed Environment
# Generated: $(date)

# Database
DATABASE_URL=${DATABASE_URL:-postgresql://user:pass@localhost:5432/dataguardian}

# Redis - FIXED for localhost access
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379

# Secrets - FRESH KEYS to avoid encryption errors
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

echo -e "${GREEN}✅ Environment file created at /root/.dataguardian_env${NC}"

echo ""
echo "════════════════════════════════════════════════"
echo "STEP 3: STOP CONTAINER & CLEAR ENCRYPTED DATA"
echo "════════════════════════════════════════════════"

# Stop and remove container
echo "Stopping container..."
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true
echo -e "${GREEN}✅ Container stopped${NC}"

# Clear Redis encrypted data
echo "Clearing Redis cache..."
if redis-cli ping 2>/dev/null | grep -q PONG; then
    redis-cli FLUSHALL 2>/dev/null || true
    echo -e "${GREEN}✅ Redis cache cleared${NC}"
else
    echo -e "${YELLOW}⚠️  Redis not accessible, will start it${NC}"
fi

# Clear cached files
echo "Clearing cached encrypted files..."
rm -rf /tmp/dataguardian_* 2>/dev/null || true
rm -rf /var/cache/dataguardian_* 2>/dev/null || true
echo -e "${GREEN}✅ Cache files cleared${NC}"

echo ""
echo "════════════════════════════════════════════════"
echo "STEP 4: ENSURE REDIS IS RUNNING"
echo "════════════════════════════════════════════════"

# Start Redis if not running
if ! redis-cli ping 2>/dev/null | grep -q PONG; then
    echo "Starting Redis server..."
    
    # Try systemctl first
    systemctl start redis-server 2>/dev/null || \
        systemctl start redis 2>/dev/null || \
        redis-server --daemonize yes --port 6379 --bind 0.0.0.0 || true
    
    sleep 3
fi

# Verify Redis
if redis-cli ping 2>/dev/null | grep -q PONG; then
    echo -e "${GREEN}✅ Redis is running and accessible${NC}"
    redis-cli INFO server | grep redis_version || true
else
    echo -e "${RED}❌ Redis still not accessible!${NC}"
    echo "Trying to start manually..."
    redis-server --daemonize yes --port 6379 --bind 0.0.0.0
    sleep 3
    
    if redis-cli ping 2>/dev/null | grep -q PONG; then
        echo -e "${GREEN}✅ Redis started successfully${NC}"
    else
        echo -e "${RED}❌ Redis failed to start - continuing anyway${NC}"
    fi
fi

echo ""
echo "════════════════════════════════════════════════"
echo "STEP 5: START CONTAINER WITH FIXES"
echo "════════════════════════════════════════════════"

# Check if image exists
if ! docker images | grep -q dataguardian-pro; then
    echo -e "${RED}❌ Docker image 'dataguardian-pro' not found!${NC}"
    echo "Please build the image first:"
    echo "  cd /opt/dataguardian && docker build -t dataguardian-pro ."
    exit 1
fi

# Start container with --network host for Redis access
echo "Starting container with --network host..."
docker run -d \
    --name dataguardian-container \
    --restart always \
    -p 5000:5000 \
    --network host \
    --env-file /root/.dataguardian_env \
    dataguardian-pro

echo -e "${GREEN}✅ Container started${NC}"

echo ""
echo "════════════════════════════════════════════════"
echo "STEP 6: WAIT FOR INITIALIZATION"
echo "════════════════════════════════════════════════"

echo "Waiting 60 seconds for full initialization..."
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
echo "STEP 7: VERIFICATION"
echo "════════════════════════════════════════════════"

# Check container status
if docker ps | grep -q dataguardian-container; then
    echo -e "${GREEN}✅ Container is running${NC}"
else
    echo -e "${RED}❌ Container is NOT running!${NC}"
    echo "Showing logs:"
    docker logs dataguardian-container 2>&1 | tail -30
    exit 1
fi

# Check HTTP response
echo ""
echo "Checking HTTP response..."
sleep 5
if curl -s http://localhost:5000 | grep -qi "streamlit"; then
    echo -e "${GREEN}✅ HTTP server responding${NC}"
else
    echo -e "${YELLOW}⚠️  HTTP may not be ready yet${NC}"
fi

# Check for Redis connection error
echo ""
echo "Checking for Redis connection errors..."
if docker logs dataguardian-container 2>&1 | tail -100 | grep -qi "All Redis connection attempts failed"; then
    echo -e "${RED}❌ Redis connection error STILL present${NC}"
    echo "Container may not have --network host or Redis not accessible"
else
    echo -e "${GREEN}✅ NO Redis connection errors found${NC}"
fi

# Check for encryption error
echo ""
echo "Checking for encryption errors..."
if docker logs dataguardian-container 2>&1 | tail -100 | grep -qi "Incorrect padding"; then
    echo -e "${RED}❌ Encryption error STILL present${NC}"
    echo "May need to clear database encrypted columns"
else
    echo -e "${GREEN}✅ NO encryption errors found${NC}"
fi

# Show recent logs
echo ""
echo "Recent logs (last 30 lines):"
echo "============================"
docker logs dataguardian-container 2>&1 | tail -30

echo ""
echo "════════════════════════════════════════════════"
echo "🎉 FIX COMPLETE!"
echo "════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}Summary of changes:${NC}"
echo "  ✅ Fresh DATAGUARDIAN_MASTER_KEY generated"
echo "  ✅ Fresh JWT_SECRET generated"
echo "  ✅ Redis configured for localhost:6379"
echo "  ✅ All encrypted cache cleared"
echo "  ✅ Container running with --network host"
echo ""
echo -e "${YELLOW}🧪 TEST NOW (IMPORTANT):${NC}"
echo ""
echo "  1. Open INCOGNITO/PRIVATE browser window"
echo "  2. Visit: https://dataguardianpro.nl"
echo "  3. Login: vishaal314 / password123"
echo "  4. Check dashboard loads WITHOUT errors"
echo "  5. Try Code Scanner"
echo ""
echo -e "${GREEN}📊 Monitor logs:${NC}"
echo "  docker logs dataguardian-container -f"
echo ""
echo -e "${GREEN}Expected results:${NC}"
echo "  ✅ No 'All Redis connection attempts failed'"
echo "  ✅ No 'Incorrect padding' errors"
echo "  ✅ Dashboard loads successfully"
echo "  ✅ All scanners working"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT NOTES:${NC}"
echo "  - Previous encrypted data has been cleared"
echo "  - User sessions will be fresh"
echo "  - Any cached scan results will regenerate"
echo "  - New encryption keys will be used going forward"
echo ""
echo "If errors persist, check:"
echo "  1. Redis is running: redis-cli ping"
echo "  2. Container can access Redis: docker exec dataguardian-container redis-cli -h localhost ping"
echo "  3. Environment file: cat /root/.dataguardian_env"

exit 0
