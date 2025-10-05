#!/bin/bash
################################################################################
# ULTIMATE FIX SCRIPT - DataGuardian Pro Server Deployment
# Fixes ALL issues: environment variables, code sync, Docker rebuild
# Run time: ~90 seconds
################################################################################

set -e  # Exit on any error

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 DataGuardian Pro - ULTIMATE FIX SCRIPT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Configuration
APP_DIR="/opt/dataguardian"
ENV_FILE="/root/.dataguardian_env"
CONTAINER_NAME="dataguardian-container"
IMAGE_NAME="dataguardian-pro"

# Step 1: Generate environment variables
echo "📝 Step 1/6: Generating environment variables..."
MASTER_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

cat > "$ENV_FILE" << EOF
# DataGuardian Pro Environment Configuration
# Generated: $(date)

# REQUIRED: Master encryption key (32-byte base64url)
DATAGUARDIAN_MASTER_KEY=$MASTER_KEY

# REQUIRED: JWT authentication secret
JWT_SECRET=$JWT_SECRET

# Database Configuration
DATABASE_URL=postgresql://dataguardian:changeme@localhost:5432/dataguardian

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Application Settings
ENVIRONMENT=production
LOG_LEVEL=INFO
EOF

chmod 600 "$ENV_FILE"
echo "✅ Environment file created: $ENV_FILE"
echo ""

# Step 2: Extract latest code
echo "📦 Step 2/6: Extracting latest code..."
cd "$APP_DIR"
if [ -f "/tmp/dataguardian_complete.tar.gz" ]; then
    tar -xzf /tmp/dataguardian_complete.tar.gz --overwrite
    echo "✅ Code extracted from /tmp/dataguardian_complete.tar.gz"
else
    echo "⚠️  Warning: /tmp/dataguardian_complete.tar.gz not found - using existing code"
fi
echo ""

# Step 3: Clean Python cache
echo "🧹 Step 3/6: Cleaning Python cache..."
find "$APP_DIR" -type f -name "*.pyc" -delete
find "$APP_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
echo "✅ Cache cleaned"
echo ""

# Step 4: Stop and remove old container
echo "🛑 Step 4/6: Stopping old container..."
docker stop "$CONTAINER_NAME" 2>/dev/null || true
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
echo "✅ Old container removed"
echo ""

# Step 5: Rebuild Docker image (no cache)
echo "🔨 Step 5/6: Rebuilding Docker image (this takes ~60 seconds)..."
cd "$APP_DIR"
docker build --no-cache -t "$IMAGE_NAME" . || {
    echo "❌ ERROR: Docker build failed!"
    exit 1
}
echo "✅ Docker image built successfully"
echo ""

# Step 6: Start new container
echo "🚀 Step 6/6: Starting new container..."
docker run -d \
    --name "$CONTAINER_NAME" \
    --restart always \
    --network host \
    --env-file "$ENV_FILE" \
    "$IMAGE_NAME" || {
    echo "❌ ERROR: Container failed to start!"
    exit 1
}
echo "✅ Container started"
echo ""

# Wait for app to initialize
echo "⏳ Waiting 30 seconds for application to initialize..."
sleep 30
echo ""

# Check container status
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 DEPLOYMENT STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if container is running
if docker ps | grep -q "$CONTAINER_NAME"; then
    echo "✅ Container Status: RUNNING"
else
    echo "❌ Container Status: FAILED"
    echo ""
    echo "Last 20 log lines:"
    docker logs "$CONTAINER_NAME" 2>&1 | tail -20
    exit 1
fi

# Check logs for success indicators
echo ""
echo "📋 Recent logs (last 30 lines):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker logs "$CONTAINER_NAME" 2>&1 | tail -30
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check for critical errors
if docker logs "$CONTAINER_NAME" 2>&1 | grep -q "DATAGUARDIAN_MASTER_KEY environment variable not set"; then
    echo "❌ ERROR: DATAGUARDIAN_MASTER_KEY still not set!"
    echo "   Check: docker exec $CONTAINER_NAME env | grep DATAGUARDIAN_MASTER_KEY"
    exit 1
fi

if docker logs "$CONTAINER_NAME" 2>&1 | grep -q "safe mode"; then
    echo "⚠️  WARNING: Application may still be in safe mode"
    echo "   Wait another 30 seconds and check logs again"
else
    echo "✅ No safe mode detected in logs"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 DEPLOYMENT COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Application URL: https://dataguardianpro.nl"
echo "👤 Login: vishaal314 / vishaal2024"
echo ""
echo "🧪 TESTING STEPS:"
echo "   1. Close ALL browser tabs"
echo "   2. Open NEW INCOGNITO window (Ctrl+Shift+N)"
echo "   3. Visit: https://dataguardianpro.nl"
echo "   4. Login with credentials above"
echo "   5. Click '🔍 New Scan' and test any scanner"
echo ""
echo "📊 Monitoring commands:"
echo "   • Live logs:    docker logs -f $CONTAINER_NAME"
echo "   • Status:       docker ps | grep $CONTAINER_NAME"
echo "   • Restart:      docker restart $CONTAINER_NAME"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
