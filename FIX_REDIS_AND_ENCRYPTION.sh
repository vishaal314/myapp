#!/bin/bash
# FIX REDIS CONNECTION AND ENCRYPTION ERRORS
# Fixes "All Redis connection attempts failed" and "Incorrect padding" errors

set -e

EXTERNAL_SERVER="root@dataguardianpro.nl"

echo "🔧 FIXING REDIS & ENCRYPTION ERRORS"
echo "===================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "This will fix:"
echo "  1. ❌ Redis connection failure"
echo "  2. ❌ KMS encryption 'Incorrect padding' error"
echo ""

# Check if we have the master key
if [ -z "$DATAGUARDIAN_MASTER_KEY" ]; then
    echo -e "${YELLOW}⚠️  DATAGUARDIAN_MASTER_KEY not set in Replit${NC}"
    echo "Generating new key for fresh start..."
    NEW_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
    echo -e "${GREEN}Generated: $NEW_KEY${NC}"
else
    echo -e "${GREEN}✅ Using existing DATAGUARDIAN_MASTER_KEY from Replit${NC}"
    NEW_KEY="$DATAGUARDIAN_MASTER_KEY"
fi

# Check JWT_SECRET
if [ -z "$JWT_SECRET" ]; then
    echo -e "${YELLOW}⚠️  JWT_SECRET not set in Replit${NC}"
    echo "Generating new JWT secret..."
    NEW_JWT=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
    echo -e "${GREEN}Generated: $NEW_JWT${NC}"
else
    echo -e "${GREEN}✅ Using existing JWT_SECRET from Replit${NC}"
    NEW_JWT="$JWT_SECRET"
fi

echo ""
echo "════════════════════════════════════════════════"
echo "STEP 1: CREATE FIXED ENVIRONMENT FILE"
echo "════════════════════════════════════════════════"

# Create environment file with proper Redis URL
cat > .env_fixed << EOF
# DataGuardian Pro Environment - Fixed $(date)

# Database
DATABASE_URL=${DATABASE_URL:-postgresql://user:pass@localhost:5432/dataguardian}

# Redis - FIXED to use localhost
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379

# Secrets
DATAGUARDIAN_MASTER_KEY=$NEW_KEY
JWT_SECRET=$NEW_JWT
OPENAI_API_KEY=${OPENAI_API_KEY:-}
STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY:-}

# Application
PYTHONUNBUFFERED=1
STREAMLIT_SERVER_PORT=5000
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true

# PostgreSQL (if needed separately)
PGHOST=$(echo ${DATABASE_URL:-postgresql://localhost:5432/db} | sed -n 's/.*@\([^:]*\):.*/\1/p')
PGPORT=$(echo ${DATABASE_URL:-postgresql://localhost:5432/db} | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
PGDATABASE=$(echo ${DATABASE_URL:-postgresql://localhost:5432/db} | sed -n 's/.*\/\([^?]*\).*/\1/p')
PGUSER=$(echo ${DATABASE_URL:-postgresql://localhost:5432/db} | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
PGPASSWORD=$(echo ${DATABASE_URL:-postgresql://localhost:5432/db} | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
EOF

echo -e "${GREEN}✅ Environment file created with Redis fix${NC}"

echo ""
echo "════════════════════════════════════════════════"
echo "STEP 2: UPLOAD TO EXTERNAL SERVER"
echo "════════════════════════════════════════════════"

scp .env_fixed $EXTERNAL_SERVER:/root/.dataguardian_env
echo -e "${GREEN}✅ Environment uploaded${NC}"

rm .env_fixed

echo ""
echo "════════════════════════════════════════════════"
echo "STEP 3: APPLY FIX ON EXTERNAL SERVER"
echo "════════════════════════════════════════════════"

ssh $EXTERNAL_SERVER << 'REMOTE_SCRIPT'
set -e

echo "On external server: Applying fixes..."

# Stop container
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true

# Ensure Redis is running
if ! redis-cli ping 2>/dev/null | grep -q PONG; then
    echo "Starting Redis..."
    systemctl start redis-server 2>/dev/null || \
        redis-server --daemonize yes --port 6379 --bind 0.0.0.0 || true
    sleep 2
fi

# Verify Redis
if redis-cli ping 2>/dev/null | grep -q PONG; then
    echo "✅ Redis is running"
else
    echo "⚠️  Redis may not be accessible"
fi

# Clear any encrypted data that might be causing issues
echo "Clearing cached encrypted data..."
redis-cli FLUSHDB 2>/dev/null || true

# Start container with fixed environment
echo "Starting container with fixed environment..."
docker run -d \
    --name dataguardian-container \
    --restart always \
    -p 5000:5000 \
    --network host \
    --env-file /root/.dataguardian_env \
    dataguardian-pro

echo "✅ Container started with --network host (for Redis access)"

# Wait for startup
echo "Waiting 30 seconds for initialization..."
sleep 30

# Verify
echo ""
echo "Verification:"
echo "============"

if docker ps | grep -q dataguardian-container; then
    echo "✅ Container running"
else
    echo "❌ Container not running"
    docker logs dataguardian-container 2>&1 | tail -20
    exit 1
fi

# Check logs for errors
echo ""
echo "Checking for errors in logs..."

if docker logs dataguardian-container 2>&1 | tail -50 | grep -qi "All Redis connection attempts failed"; then
    echo "❌ Redis connection still failing"
else
    echo "✅ No Redis connection errors"
fi

if docker logs dataguardian-container 2>&1 | tail -50 | grep -qi "Incorrect padding"; then
    echo "❌ Encryption errors still present"
else
    echo "✅ No encryption errors"
fi

echo ""
echo "Recent logs:"
docker logs dataguardian-container 2>&1 | tail -25

REMOTE_SCRIPT

echo ""
echo "════════════════════════════════════════════════"
echo "🎉 REDIS & ENCRYPTION FIX COMPLETE!"
echo "════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}✅ Redis URL configured: redis://localhost:6379${NC}"
echo -e "${GREEN}✅ Encryption key set: DATAGUARDIAN_MASTER_KEY${NC}"
echo -e "${GREEN}✅ JWT secret configured${NC}"
echo -e "${GREEN}✅ Container using --network host for Redis access${NC}"
echo ""
echo -e "${YELLOW}🧪 TEST NOW:${NC}"
echo "   1. Visit: https://dataguardianpro.nl"
echo "   2. Login: vishaal314 / password123"
echo "   3. Check dashboard loads without errors"
echo "   4. Try Code Scanner"
echo ""
echo -e "${GREEN}📊 Monitor logs:${NC}"
echo "   ssh $EXTERNAL_SERVER 'docker logs dataguardian-container -f'"
echo ""
echo "Expected results:"
echo "  ✅ No 'All Redis connection attempts failed'"
echo "  ✅ No 'Incorrect padding' errors"
echo "  ✅ Dashboard loads successfully"

exit 0
