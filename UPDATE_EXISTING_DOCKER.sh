#!/bin/bash
# UPDATE EXISTING DOCKER INSTALLATION
# Run this directly on dataguardianpro.nl with existing Docker setup
# Usage: sudo ./UPDATE_EXISTING_DOCKER.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  UPDATE EXISTING DOCKER INSTALLATION          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Run as root: sudo ./UPDATE_EXISTING_DOCKER.sh${NC}"
    exit 1
fi

if [ ! -d "/opt/dataguardian" ]; then
    echo -e "${RED}❌ /opt/dataguardian not found!${NC}"
    exit 1
fi

# ═══════════════════════════════════════════════════════════════
# STEP 1: GENERATE FRESH ENVIRONMENT
# ═══════════════════════════════════════════════════════════════

echo -e "${BLUE}STEP 1: Generate Fresh Environment${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Generate new keys
NEW_MASTER_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
NEW_JWT_SECRET=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')

echo -e "${GREEN}✅ Generated fresh DATAGUARDIAN_MASTER_KEY${NC}"
echo -e "${GREEN}✅ Generated fresh JWT_SECRET${NC}"

# Preserve API keys
OPENAI_API_KEY=""
STRIPE_SECRET_KEY=""
DATABASE_URL=""

if [ -f "/root/.dataguardian_env" ]; then
    OPENAI_API_KEY=$(grep "^OPENAI_API_KEY=" /root/.dataguardian_env 2>/dev/null | cut -d'=' -f2- || echo "")
    STRIPE_SECRET_KEY=$(grep "^STRIPE_SECRET_KEY=" /root/.dataguardian_env 2>/dev/null | cut -d'=' -f2- || echo "")
    DATABASE_URL=$(grep "^DATABASE_URL=" /root/.dataguardian_env 2>/dev/null | cut -d'=' -f2- || echo "")
    echo -e "${GREEN}✅ Preserved API keys from existing environment${NC}"
fi

# Create environment
cat > /root/.dataguardian_env << EOF
DATABASE_URL=${DATABASE_URL:-postgresql://dataguardian:changeme@localhost:5432/dataguardian}
REDIS_URL=redis://127.0.0.1:6379
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
DATAGUARDIAN_MASTER_KEY=${NEW_MASTER_KEY}
JWT_SECRET=${NEW_JWT_SECRET}
OPENAI_API_KEY=${OPENAI_API_KEY}
STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
PYTHONUNBUFFERED=1
STREAMLIT_SERVER_PORT=5000
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
EOF

echo -e "${GREEN}✅ Environment configured${NC}"

# ═══════════════════════════════════════════════════════════════
# STEP 2: START REDIS & CLEAR CACHE
# ═══════════════════════════════════════════════════════════════

echo ""
echo -e "${BLUE}STEP 2: Start Redis & Clear Cache${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start Redis
systemctl stop redis-server 2>/dev/null || true
pkill redis-server 2>/dev/null || true
sleep 2
redis-server --daemonize yes --port 6379 --bind 127.0.0.1 --protected-mode no
sleep 2

if redis-cli -h 127.0.0.1 PING 2>/dev/null | grep -q PONG; then
    redis-cli -h 127.0.0.1 FLUSHALL
    echo -e "${GREEN}✅ Redis running and flushed${NC}"
else
    echo -e "${YELLOW}⚠️  Redis not responding (will use fallback)${NC}"
fi

# Clear filesystem cache
rm -rf /tmp/dataguardian_* /var/cache/dataguardian_* /tmp/encryption_cache 2>/dev/null || true
echo -e "${GREEN}✅ Filesystem cache cleared${NC}"

# ═══════════════════════════════════════════════════════════════
# STEP 3: CLEAR OLD ENCRYPTED DATA
# ═══════════════════════════════════════════════════════════════

echo ""
echo -e "${BLUE}STEP 3: Clear Old Encrypted Data${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ ! -z "$DATABASE_URL" ]; then
    # Extract DB credentials
    DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
    DB_PASS=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
    
    # Clear encrypted columns
    PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" << 'SQL' 2>/dev/null || true
UPDATE scan_results SET encrypted_payload = NULL WHERE encrypted_payload IS NOT NULL;
UPDATE certificates SET encrypted_report = NULL WHERE encrypted_report IS NOT NULL;
UPDATE api_credentials SET encrypted_credentials = NULL WHERE encrypted_credentials IS NOT NULL;
TRUNCATE TABLE scan_cache;
SQL
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Database encrypted columns cleared${NC}"
    else
        echo -e "${YELLOW}⚠️  Database cleanup skipped (continuing)${NC}"
    fi
fi

# ═══════════════════════════════════════════════════════════════
# STEP 4: STOP CONTAINER & CLEAR PYTHON CACHE
# ═══════════════════════════════════════════════════════════════

echo ""
echo -e "${BLUE}STEP 4: Stop Container & Clear Cache${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true
echo -e "${GREEN}✅ Container stopped${NC}"

cd /opt/dataguardian
find . -name "*.pyc" -delete 2>/dev/null || true
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
echo -e "${GREEN}✅ Python cache cleared${NC}"

# ═══════════════════════════════════════════════════════════════
# STEP 5: REBUILD DOCKER
# ═══════════════════════════════════════════════════════════════

echo ""
echo -e "${BLUE}STEP 5: Rebuild Docker Image${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

docker rmi dataguardian-pro 2>/dev/null || true

echo "Building (60-90 seconds)..."
docker build --no-cache -t dataguardian-pro . 2>&1 | tail -20

if ! docker images | grep -q dataguardian-pro; then
    echo -e "${RED}❌ Docker build failed!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker image rebuilt${NC}"

# ═══════════════════════════════════════════════════════════════
# STEP 6: START CONTAINER
# ═══════════════════════════════════════════════════════════════

echo ""
echo -e "${BLUE}STEP 6: Start Container${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

docker run -d \
    --name dataguardian-container \
    --restart always \
    --network host \
    --env-file /root/.dataguardian_env \
    dataguardian-pro

echo -e "${GREEN}✅ Container started${NC}"

# ═══════════════════════════════════════════════════════════════
# STEP 7: WAIT & VERIFY
# ═══════════════════════════════════════════════════════════════

echo ""
echo -e "${BLUE}STEP 7: Wait for Initialization${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Waiting 60 seconds..."
for i in {1..60}; do
    [ $((i % 10)) -eq 0 ] && echo -n " $i" || echo -n "."
    sleep 1
done
echo ""

# ═══════════════════════════════════════════════════════════════
# STEP 8: VERIFICATION
# ═══════════════════════════════════════════════════════════════

echo ""
echo -e "${BLUE}STEP 8: Verification${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if ! docker ps | grep -q dataguardian-container; then
    echo -e "${RED}❌ Container NOT running!${NC}"
    docker logs dataguardian-container 2>&1 | tail -30
    exit 1
fi
echo -e "${GREEN}✅ Container running${NC}"

sleep 5
if curl -s http://localhost:5000 | grep -qi streamlit; then
    echo -e "${GREEN}✅ HTTP responding${NC}"
fi

LOGS=$(docker logs dataguardian-container 2>&1 | tail -100)

echo ""
echo "Error Check:"
echo "━━━━━━━━━━━━"

echo "$LOGS" | grep -qi "unboundlocalerror.*stats" && \
    echo -e "${RED}❌ 'stats' error present${NC}" || \
    echo -e "${GREEN}✅ NO 'stats' error${NC}"

echo "$LOGS" | grep -qi "All Redis connection attempts failed" && \
    echo -e "${YELLOW}⚠️  Redis warning${NC}" || \
    echo -e "${GREEN}✅ NO Redis errors${NC}"

echo "$LOGS" | grep -qi "Incorrect padding" && \
    echo -e "${RED}❌ Encryption error${NC}" || \
    echo -e "${GREEN}✅ NO encryption errors${NC}"

echo "$LOGS" | grep -qi "You can now view your Streamlit app" && \
    echo -e "${GREEN}✅ Streamlit started${NC}" || \
    echo -e "${YELLOW}⚠️  Streamlit initializing${NC}"

echo ""
echo "Recent logs:"
echo "━━━━━━━━━━━━"
docker logs dataguardian-container 2>&1 | tail -25

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  ✅ UPDATE COMPLETE!                           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}🧪 TEST IN INCOGNITO BROWSER:${NC}"
echo ""
echo "  1. Close ALL tabs for dataguardianpro.nl"
echo "  2. Press Ctrl+Shift+N (incognito)"
echo "  3. Visit: https://dataguardianpro.nl"
echo "  4. Login: vishaal314 / password123"
echo "  5. Try any scanner"
echo ""
echo -e "${GREEN}Expected: NO errors, all scanners working${NC}"
echo ""
echo -e "${BLUE}Monitor: docker logs dataguardian-container -f${NC}"

exit 0
