#!/bin/bash
# SYNC REPLIT TO EXTERNAL SERVER - Complete E2E Script
# Run this from your Replit environment or after downloading Replit files

set -e

SERVER="root@dataguardianpro.nl"
SERVER_PATH="/opt/dataguardian"
EXCLUDE_PATTERNS="--exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='.pytest_cache' --exclude='node_modules' --exclude='.venv' --exclude='venv'"

echo "🔄 SYNC REPLIT TO EXTERNAL SERVER"
echo "================================="
echo ""

# Check if we have files to sync
if [ ! -f "app.py" ]; then
    echo "❌ app.py not found!"
    echo ""
    echo "Please run this script from your Replit project root,"
    echo "or download your Replit project first:"
    echo "  1. In Replit: Menu → Download as zip"
    echo "  2. Extract the zip"
    echo "  3. Run this script from extracted directory"
    exit 1
fi

echo "Step 1: Verify connection to external server"
echo "==========================================="
if ssh -o ConnectTimeout=5 $SERVER "echo '✅ Connected'" 2>/dev/null; then
    echo "✅ Server connection successful"
else
    echo "❌ Cannot connect to $SERVER"
    echo "   Make sure you can SSH to the server"
    exit 1
fi

echo ""
echo "Step 2: Backup current server files"
echo "================================="
ssh $SERVER "cd $SERVER_PATH && tar -czf /root/dataguardian_backup_\$(date +%Y%m%d_%H%M%S).tar.gz ." 2>/dev/null && echo "✅ Backup created" || echo "⚠️  Backup skipped"

echo ""
echo "Step 3: Sync files to external server"
echo "===================================="
echo "Syncing files (this may take 1-2 minutes)..."

# Use rsync for efficient sync
rsync -avz --progress \
    $EXCLUDE_PATTERNS \
    --exclude='*.log' \
    --exclude='*.sqlite' \
    --exclude='*.db' \
    --exclude='scan_checkpoint_*' \
    ./ $SERVER:$SERVER_PATH/

echo "✅ Files synced successfully"

echo ""
echo "Step 4: Rebuild Docker container on server"
echo "========================================"
ssh $SERVER << 'ENDSSH'
cd /opt/dataguardian

echo "Stopping current container..."
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true

echo "Building new image..."
docker build -t dataguardian-pro . 2>&1 | tail -20

echo "Starting new container..."
docker run -d \
    --name dataguardian-container \
    --restart always \
    -p 5000:5000 \
    -e PYTHONUNBUFFERED=1 \
    dataguardian-pro

echo "✅ Container restarted"
ENDSSH

echo ""
echo "Step 5: Wait for initialization (45 seconds)"
echo "========================================"
for i in {1..45}; do
    if [ $((i % 5)) -eq 0 ]; then
        echo -n " $i"
    else
        echo -n "."
    fi
    sleep 1
done
echo ""

echo ""
echo "Step 6: Verify deployment"
echo "======================="

# Test from server
ssh $SERVER << 'ENDTEST'
echo "Container status:"
docker ps | grep dataguardian-container && echo "   ✅ Running" || echo "   ❌ Not running"

echo ""
echo "HTTP test:"
if curl -s http://localhost:5000 | grep -qi "dataguardian"; then
    echo "   ✅ DataGuardian content detected"
else
    echo "   ⚠️  Generic Streamlit (checking logs...)"
    docker logs dataguardian-container 2>&1 | tail -20
fi

echo ""
echo "Recent container logs:"
docker logs dataguardian-container 2>&1 | tail -30
ENDTEST

echo ""
echo "=========================================="
echo "🎉 SYNC COMPLETE!"
echo "=========================================="
echo ""
echo "✅ Replit code synced to external server"
echo "✅ Docker container rebuilt"
echo "✅ Application restarted"
echo ""
echo "🌐 Test your app:"
echo "   https://dataguardianpro.nl"
echo ""
echo "🔐 Login credentials:"
echo "   vishaal314 / password123"
echo "   demo / demo123"
echo ""
echo "🧪 Test Code Scanner with sampling strategy"
echo "   to verify the 'stats' error is fixed"
echo ""
echo "📊 If any issues, check logs:"
echo "   ssh $SERVER"
echo "   docker logs dataguardian-container -f"

exit 0
