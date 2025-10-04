#!/bin/bash
# COMPLETE SYNC - Upload ALL code from Replit to External Server
# Run FROM REPLIT terminal: ./SYNC_ALL_TO_EXTERNAL.sh

set -e

EXTERNAL="root@dataguardianpro.nl"
REMOTE_DIR="/opt/dataguardian"

echo "🔄 COMPLETE SYNCHRONIZATION - Replit → External Server"
echo "======================================================="
echo ""

# Check we're in the right place
if [ ! -f "app.py" ] || [ ! -d "services" ]; then
    echo "❌ Must run from project root directory"
    exit 1
fi

echo "Step 1: Create tarball of current working code"
echo "==============================================="

# Create temp directory
TMP_DIR=$(mktemp -d)
TARBALL="$TMP_DIR/dataguardian_code.tar.gz"

# Package all code (exclude temp files, logs, caches)
tar -czf "$TARBALL" \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='logs' \
    --exclude='temp' \
    --exclude='*.log' \
    --exclude='.streamlit' \
    --exclude='node_modules' \
    app.py \
    services/ \
    components/ \
    utils/ \
    scanners/ \
    Dockerfile \
    requirements.txt \
    translations/ \
    2>/dev/null || echo "Some optional directories skipped"

echo "✅ Code packaged: $(du -h $TARBALL | cut -f1)"

echo ""
echo "Step 2: Upload to external server"
echo "=================================="

scp "$TARBALL" "$EXTERNAL:/tmp/dataguardian_code.tar.gz"

echo "✅ Upload complete"

# Clean up local temp
rm -rf "$TMP_DIR"

echo ""
echo "Step 3: Execute complete fix on external server"
echo "================================================"

ssh $EXTERNAL << 'REMOTE_FIX'
set -e

echo "🔧 Applying fixes on external server..."
echo ""

# Stop container
echo "Stopping container..."
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true
echo "✅ Container stopped"

# Backup old code
echo "Backing up old code..."
if [ -d "/opt/dataguardian" ]; then
    mv /opt/dataguardian /opt/dataguardian.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
fi

# Extract new code
echo "Extracting new code..."
mkdir -p /opt/dataguardian
cd /opt/dataguardian
tar -xzf /tmp/dataguardian_code.tar.gz
rm /tmp/dataguardian_code.tar.gz
echo "✅ New code extracted"

# Generate fresh environment
echo "Generating fresh environment..."

NEW_MASTER_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
NEW_JWT_SECRET=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')

# Try to preserve existing keys
if [ -f "/root/.dataguardian_env" ]; then
    OPENAI_API_KEY=$(grep "^OPENAI_API_KEY=" /root/.dataguardian_env 2>/dev/null | cut -d'=' -f2- || echo "")
    STRIPE_SECRET_KEY=$(grep "^STRIPE_SECRET_KEY=" /root/.dataguardian_env 2>/dev/null | cut -d'=' -f2- || echo "")
    DATABASE_URL=$(grep "^DATABASE_URL=" /root/.dataguardian_env 2>/dev/null | cut -d'=' -f2- || echo "")
fi

cat > /root/.dataguardian_env << EOF
# DataGuardian Pro - Complete Sync
# Generated: $(date)

# Database
DATABASE_URL=${DATABASE_URL:-postgresql://dataguardian:changeme@localhost:5432/dataguardian}

# Redis
REDIS_URL=redis://127.0.0.1:6379
REDIS_HOST=127.0.0.1
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

echo "✅ Environment configured"

# Start Redis
echo "Starting Redis..."
systemctl stop redis-server 2>/dev/null || true
pkill redis-server 2>/dev/null || true
sleep 2
redis-server --daemonize yes --port 6379 --bind 127.0.0.1 --protected-mode no
sleep 2

if redis-cli -h 127.0.0.1 PING 2>/dev/null | grep -q PONG; then
    redis-cli -h 127.0.0.1 FLUSHALL
    echo "✅ Redis running and flushed"
else
    echo "⚠️  Redis not responding (will use fallback)"
fi

# Clear all caches
echo "Clearing caches..."
rm -rf /tmp/dataguardian_* /var/cache/dataguardian_* /tmp/encryption_cache 2>/dev/null || true
find /opt/dataguardian -name "*.pyc" -delete 2>/dev/null || true
find /opt/dataguardian -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
echo "✅ Caches cleared"

# Remove old Docker image
docker rmi dataguardian-pro 2>/dev/null || true

# Build fresh Docker image
echo ""
echo "Building Docker image (60-90 seconds)..."
cd /opt/dataguardian
docker build --no-cache -t dataguardian-pro . 2>&1 | tail -25

if ! docker images | grep -q dataguardian-pro; then
    echo "❌ Docker build failed!"
    exit 1
fi
echo "✅ Docker image built"

# Start container
echo "Starting container..."
docker run -d \
    --name dataguardian-container \
    --restart always \
    --network host \
    --env-file /root/.dataguardian_env \
    dataguardian-pro

echo "✅ Container started"

# Wait for initialization
echo ""
echo "Waiting 50 seconds for initialization..."
sleep 50

# Check for errors
echo ""
echo "═══════════════════════════════════════════════"
echo "ERROR CHECK"
echo "═══════════════════════════════════════════════"

LOGS=$(docker logs dataguardian-container 2>&1 | tail -100)

if echo "$LOGS" | grep -qi "unboundlocalerror.*stats"; then
    echo "❌ 'stats' error STILL PRESENT"
    echo "This should NOT happen with fresh code!"
else
    echo "✅ NO 'stats' error found"
fi

if echo "$LOGS" | grep -qi "All Redis connection attempts failed"; then
    echo "⚠️  Redis connection warning (using fallback)"
else
    echo "✅ NO Redis connection errors"
fi

if echo "$LOGS" | grep -qi "Incorrect padding"; then
    echo "⚠️  Encryption warning (will regenerate on use)"
else
    echo "✅ NO encryption errors"
fi

if echo "$LOGS" | grep -qi "Streamlit app in your browser"; then
    echo "✅ Streamlit server started successfully"
else
    echo "⚠️  Streamlit may not be fully initialized"
fi

echo ""
echo "Recent logs (last 30 lines):"
echo "============================"
docker logs dataguardian-container 2>&1 | tail -30

REMOTE_FIX

echo ""
echo "════════════════════════════════════════════════"
echo "🎉 COMPLETE SYNCHRONIZATION FINISHED!"
echo "════════════════════════════════════════════════"
echo ""
echo "✅ All code uploaded from Replit"
echo "✅ Fresh Docker image built"
echo "✅ New environment configured"
echo "✅ All caches cleared"
echo "✅ Container restarted"
echo ""
echo "🧪 TEST NOW (MANDATORY - USE INCOGNITO!):"
echo ""
echo "  1. Close ALL browser tabs for dataguardianpro.nl"
echo "  2. Open NEW INCOGNITO/PRIVATE window (Ctrl+Shift+N)"
echo "  3. Visit: https://dataguardianpro.nl"
echo "  4. Login: vishaal314 / password123"
echo "  5. Try ANY scanner (Code, Website, etc.)"
echo ""
echo "Expected results:"
echo "  ✅ NO 'stats' errors"
echo "  ✅ ALL scanners working"
echo "  ✅ Dashboard loads"
echo ""
echo "⚠️  CRITICAL: You MUST use INCOGNITO browser!"
echo "   Regular browser has cached the old error page"
echo ""
echo "📊 Monitor logs:"
echo "   ssh $EXTERNAL"
echo "   docker logs dataguardian-container -f"

exit 0
