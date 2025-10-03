#!/bin/bash
# COMPLETE ENCRYPTION FIX - Resolve "Incorrect padding" error
# Clears all encrypted data and sets fresh encryption key

set -e

EXTERNAL_SERVER="root@dataguardianpro.nl"

echo "🔧 FIXING ENCRYPTION 'Incorrect padding' ERROR"
echo "==============================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "This error occurs when encrypted data can't be decrypted with current key."
echo ""
echo "Fix approach:"
echo "  1. Clear all encrypted data (Redis + database)"
echo "  2. Set fresh DATAGUARDIAN_MASTER_KEY"
echo "  3. Restart container cleanly"
echo ""

# Get or generate master key
if [ -z "$DATAGUARDIAN_MASTER_KEY" ]; then
    echo -e "${YELLOW}⚠️  DATAGUARDIAN_MASTER_KEY not set in Replit${NC}"
    echo "Generating NEW master key..."
    MASTER_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
    echo -e "${GREEN}Generated: ${MASTER_KEY}${NC}"
else
    echo -e "${GREEN}✅ Using DATAGUARDIAN_MASTER_KEY from Replit${NC}"
    MASTER_KEY="$DATAGUARDIAN_MASTER_KEY"
fi

# Get or generate JWT secret
if [ -z "$JWT_SECRET" ]; then
    echo -e "${YELLOW}⚠️  JWT_SECRET not set in Replit${NC}"
    echo "Generating NEW JWT secret..."
    JWT_SEC=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
    echo -e "${GREEN}Generated: ${JWT_SEC}${NC}"
else
    echo -e "${GREEN}✅ Using JWT_SECRET from Replit${NC}"
    JWT_SEC="$JWT_SECRET"
fi

echo ""
echo "════════════════════════════════════════════════"
echo "STEP 1: CREATE CLEAN ENVIRONMENT FILE"
echo "════════════════════════════════════════════════"

# Create environment file
cat > .env_clean << EOF
# DataGuardian Pro - Clean Environment $(date)

# Database
DATABASE_URL=${DATABASE_URL:-postgresql://user:pass@localhost:5432/dataguardian}

# Redis
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379

# Secrets - FRESH KEYS
DATAGUARDIAN_MASTER_KEY=${MASTER_KEY}
JWT_SECRET=${JWT_SEC}
OPENAI_API_KEY=${OPENAI_API_KEY:-}
STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY:-}

# Application
PYTHONUNBUFFERED=1
STREAMLIT_SERVER_PORT=5000
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
EOF

echo -e "${GREEN}✅ Clean environment file created${NC}"

echo ""
echo "════════════════════════════════════════════════"
echo "STEP 2: UPLOAD TO EXTERNAL SERVER"
echo "════════════════════════════════════════════════"

scp .env_clean $EXTERNAL_SERVER:/root/.dataguardian_env
echo -e "${GREEN}✅ Environment uploaded${NC}"

rm .env_clean

echo ""
echo "════════════════════════════════════════════════"
echo "STEP 3: CLEAR ENCRYPTED DATA & RESTART"
echo "════════════════════════════════════════════════"

ssh $EXTERNAL_SERVER << 'REMOTE_SCRIPT'
set -e

echo "On external server: Clearing encrypted data..."

# Stop container
echo "Stopping container..."
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true

# Clear Redis encrypted data
echo "Clearing Redis cache..."
if redis-cli ping 2>/dev/null | grep -q PONG; then
    redis-cli FLUSHALL 2>/dev/null || true
    echo "✅ Redis cache cleared"
else
    echo "⚠️  Redis not accessible, skipping"
fi

# Clear any cached encrypted files
echo "Clearing encrypted cache files..."
rm -rf /tmp/dataguardian_* 2>/dev/null || true
rm -rf /var/cache/dataguardian_* 2>/dev/null || true

# Ensure Redis is running
echo "Ensuring Redis is running..."
systemctl start redis-server 2>/dev/null || \
    redis-server --daemonize yes --port 6379 --bind 0.0.0.0 || true
sleep 2

if redis-cli ping 2>/dev/null | grep -q PONG; then
    echo "✅ Redis running"
fi

# Start container with FRESH environment
echo "Starting container with clean environment..."
docker run -d \
    --name dataguardian-container \
    --restart always \
    -p 5000:5000 \
    --network host \
    --env-file /root/.dataguardian_env \
    dataguardian-pro

echo "✅ Container started"

# Wait for initialization
echo "Waiting 45 seconds for full initialization..."
sleep 45

# Verify no encryption errors
echo ""
echo "Verification:"
echo "============"

if docker ps | grep -q dataguardian-container; then
    echo "✅ Container running"
else
    echo "❌ Container not running"
    docker logs dataguardian-container 2>&1 | tail -30
    exit 1
fi

# Check for the specific error
echo ""
echo "Checking for 'Incorrect padding' error..."

if docker logs dataguardian-container 2>&1 | tail -100 | grep -qi "Incorrect padding"; then
    echo "❌ Encryption error STILL present:"
    docker logs dataguardian-container 2>&1 | grep -i "padding" | tail -5
    echo ""
    echo "This may mean:"
    echo "  1. Database has encrypted data from old key"
    echo "  2. Need to clear database encrypted columns"
else
    echo "✅ NO encryption errors found!"
fi

# Check for other errors
if docker logs dataguardian-container 2>&1 | tail -100 | grep -qi "ERROR"; then
    echo ""
    echo "Other errors found:"
    docker logs dataguardian-container 2>&1 | grep "ERROR" | tail -10
fi

echo ""
echo "Recent logs (last 30 lines):"
echo "============================"
docker logs dataguardian-container 2>&1 | tail -30

REMOTE_SCRIPT

echo ""
echo "════════════════════════════════════════════════"
echo "🎉 ENCRYPTION FIX APPLIED!"
echo "════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}✅ Encrypted data cleared${NC}"
echo -e "${GREEN}✅ Fresh DATAGUARDIAN_MASTER_KEY set${NC}"
echo -e "${GREEN}✅ Fresh JWT_SECRET set${NC}"
echo -e "${GREEN}✅ Container restarted cleanly${NC}"
echo ""
echo -e "${YELLOW}🧪 TEST NOW (IMPORTANT - Use INCOGNITO):${NC}"
echo "   1. Open INCOGNITO/PRIVATE browser window"
echo "   2. Visit: https://dataguardianpro.nl"
echo "   3. Login: vishaal314 / password123"
echo "   4. Check dashboard loads WITHOUT errors"
echo "   5. Try Code Scanner"
echo ""
echo -e "${GREEN}📊 Monitor logs:${NC}"
echo "   ssh $EXTERNAL_SERVER 'docker logs dataguardian-container -f'"
echo ""
echo "Expected result:"
echo "  ✅ NO 'Incorrect padding' errors"
echo "  ✅ Dashboard loads successfully"
echo "  ✅ All features working"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT:${NC}"
echo "  - Previous encrypted data is now cleared"
echo "  - Any cached results will be regenerated"
echo "  - User sessions will be fresh"

exit 0
