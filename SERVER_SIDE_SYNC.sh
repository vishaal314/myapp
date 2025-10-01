#!/bin/bash
# SERVER-SIDE SYNC - Run this ON the external server
# Use this if you've already uploaded Replit files to /tmp/replit_sync

set -e

echo "🔄 SERVER-SIDE SYNC FROM REPLIT FILES"
echo "====================================="
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "❌ Run as root: sudo ./SERVER_SIDE_SYNC.sh"
    exit 1
fi

# Check for uploaded Replit files
SYNC_DIR="/tmp/replit_sync"
if [ ! -d "$SYNC_DIR" ] || [ ! -f "$SYNC_DIR/app.py" ]; then
    echo "❌ Replit files not found at $SYNC_DIR"
    echo ""
    echo "📥 Please upload Replit files first:"
    echo "   1. Download Replit as zip"
    echo "   2. scp replit.zip root@dataguardianpro.nl:/tmp/"
    echo "   3. ssh root@dataguardianpro.nl"
    echo "   4. unzip /tmp/replit.zip -d /tmp/replit_sync"
    echo "   5. Run this script"
    exit 1
fi

echo "✅ Found Replit files at $SYNC_DIR"

echo ""
echo "Step 1: Backup current deployment"
echo "==============================="
cd /opt/dataguardian
backup_file="/root/dataguardian_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf "$backup_file" . 2>/dev/null
echo "✅ Backup saved to: $backup_file"

echo ""
echo "Step 2: Sync Replit files to /opt/dataguardian"
echo "==========================================="
rsync -av --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
    --exclude='node_modules' --exclude='.pytest_cache' \
    "$SYNC_DIR/" /opt/dataguardian/

echo "✅ Files synced"

echo ""
echo "Step 3: Rebuild Docker container"
echo "=============================="
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true

echo "Building new image..."
docker build -t dataguardian-pro /opt/dataguardian 2>&1 | tail -20

docker run -d \
    --name dataguardian-container \
    --restart always \
    -p 5000:5000 \
    -e PYTHONUNBUFFERED=1 \
    dataguardian-pro

echo "✅ Container restarted"

echo ""
echo "Step 4: Wait for initialization (45 seconds)"
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
echo "Step 5: Verify deployment"
echo "======================="

echo "Container status:"
docker ps | grep dataguardian-container && echo "   ✅ Running" || echo "   ❌ Not running"

echo ""
echo "HTTP test:"
if curl -s http://localhost:5000 | grep -qi "dataguardian"; then
    echo "   ✅ DataGuardian content detected"
    success=true
else
    echo "   ⚠️  Testing..."
    success=false
fi

echo ""
echo "Container logs (last 30 lines):"
docker logs dataguardian-container 2>&1 | tail -30

echo ""
echo "Clean up temp files:"
rm -rf "$SYNC_DIR"
echo "✅ Cleaned up /tmp/replit_sync"

if [ "$success" = "true" ]; then
    echo ""
    echo "=========================================="
    echo "🎉 SYNC SUCCESSFUL!"
    echo "=========================================="
    echo ""
    echo "✅ Replit code deployed successfully"
    echo "✅ All scanners should now match Replit"
    echo ""
    echo "🌐 Access: https://dataguardianpro.nl"
    echo "🔐 Login: vishaal314 / password123"
    echo ""
    echo "🧪 Test Code Scanner with sampling strategy"
else
    echo ""
    echo "⚠️  DEPLOYMENT NEEDS VERIFICATION"
    echo "================================"
    echo "Check logs above for any errors"
fi

exit 0
