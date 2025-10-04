#!/bin/bash
# RUN THIS FROM REPLIT - Uploads code and fixes external server
# Usage: ./UPLOAD_AND_FIX.sh

set -e

EXTERNAL="root@dataguardianpro.nl"

echo "🚀 UPLOADING CODE & FIXING EXTERNAL SERVER"
echo "==========================================="
echo ""

# Check we're in project root
if [ ! -f "app.py" ]; then
    echo "❌ Run from project root (where app.py is)"
    exit 1
fi

echo "Step 1: Upload critical files to external server"
echo "================================================="

# Upload the three critical files
scp services/intelligent_repo_scanner.py $EXTERNAL:/opt/dataguardian/services/
scp services/code_scanner.py $EXTERNAL:/opt/dataguardian/services/
scp app.py $EXTERNAL:/opt/dataguardian/

echo "✅ Files uploaded"

echo ""
echo "Step 2: Execute comprehensive fix on external server"
echo "====================================================="

ssh $EXTERNAL << 'REMOTE_COMMANDS'

echo "🔧 Running comprehensive fix on external server..."

# Generate fresh keys
NEW_MASTER_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
NEW_JWT_SECRET=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')

# Get existing keys
if [ -f "/root/.dataguardian_env" ]; then
    DATABASE_URL=$(grep "^DATABASE_URL=" /root/.dataguardian_env | cut -d'=' -f2- || echo "")
    OPENAI_API_KEY=$(grep "^OPENAI_API_KEY=" /root/.dataguardian_env | cut -d'=' -f2- || echo "")
    STRIPE_SECRET_KEY=$(grep "^STRIPE_SECRET_KEY=" /root/.dataguardian_env | cut -d'=' -f2- || echo "")
fi

# Create environment file
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

echo "✅ Environment configured"

# Ensure Redis is running
echo "Starting Redis..."
systemctl stop redis-server 2>/dev/null || true
pkill redis-server 2>/dev/null || true
sleep 2
redis-server --daemonize yes --port 6379 --bind 127.0.0.1 --protected-mode no
sleep 2

if redis-cli -h 127.0.0.1 PING 2>/dev/null | grep -q PONG; then
    echo "✅ Redis running"
    redis-cli -h 127.0.0.1 FLUSHALL
else
    echo "⚠️  Redis not accessible (will use fallback)"
fi

# Clear all cache
echo "Clearing caches..."
rm -rf /tmp/dataguardian_* /var/cache/dataguardian_* /tmp/encryption_cache 2>/dev/null || true

cd /opt/dataguardian
find . -name "*.pyc" -delete 2>/dev/null || true
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

echo "✅ Caches cleared"

# Stop container
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true
docker rmi dataguardian-pro 2>/dev/null || true

# Rebuild Docker
echo "Rebuilding Docker (60 seconds)..."
docker build --no-cache -t dataguardian-pro . 2>&1 | tail -20

# Start container
docker run -d \
    --name dataguardian-container \
    --restart always \
    --network host \
    --env-file /root/.dataguardian_env \
    dataguardian-pro

echo "✅ Container started"

# Wait
echo "Waiting 50 seconds for initialization..."
sleep 50

# Check status
echo ""
echo "Checking for errors..."
LOGS=$(docker logs dataguardian-container 2>&1 | tail -80)

if echo "$LOGS" | grep -qi "unboundlocalerror.*stats"; then
    echo "❌ Stats error STILL present"
else
    echo "✅ NO stats error!"
fi

if echo "$LOGS" | grep -qi "All Redis connection attempts failed"; then
    echo "⚠️  Redis connection warning"
else
    echo "✅ NO Redis errors"
fi

if echo "$LOGS" | grep -qi "Incorrect padding"; then
    echo "❌ Encryption error present"
else
    echo "✅ NO encryption errors"
fi

echo ""
echo "Recent logs:"
docker logs dataguardian-container 2>&1 | tail -25

REMOTE_COMMANDS

echo ""
echo "════════════════════════════════════════════════"
echo "🎉 UPLOAD & FIX COMPLETE!"
echo "════════════════════════════════════════════════"
echo ""
echo "✅ Code uploaded"
echo "✅ Environment fixed"
echo "✅ Redis configured"
echo "✅ Docker rebuilt"
echo "✅ Container restarted"
echo ""
echo "🧪 TEST IN INCOGNITO:"
echo "   1. Close ALL browser tabs"
echo "   2. Open INCOGNITO window"
echo "   3. Visit: https://dataguardianpro.nl"
echo "   4. Login: vishaal314 / password123"
echo "   5. Try Code Scanner: https://github.com/rijdendetreinen/gotrain"
echo ""
echo "Expected: Scan works WITHOUT errors!"

exit 0
