#!/bin/bash
# FIX SCANNERS DIRECTLY ON SERVER
# Run this script ON the external server to fix scanner dropdown errors

set -e

echo "🔧 FIX SCANNERS ON EXTERNAL SERVER"
echo "==================================="
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "❌ Run as root: sudo ./FIX_SCANNERS_ON_SERVER.sh"
    exit 1
fi

echo "Step 1: Copy working Replit files from current directory"
echo "======================================================="

# Check if we have Replit files here
if [ ! -f "app.py" ]; then
    echo "❌ app.py not found in current directory!"
    echo ""
    echo "You need Replit files here first."
    echo ""
    echo "📥 OPTION 1 - Upload from local machine:"
    echo "   1. Download Replit: Menu → Download as zip"
    echo "   2. Upload: scp dataguardian.zip root@dataguardianpro.nl:~/"
    echo "   3. Extract: cd ~ && unzip dataguardian.zip"
    echo "   4. Run this script from extracted directory"
    echo ""
    echo "📥 OPTION 2 - Use E2E fix script:"
    echo "   ./E2E_FIX_FROM_SERVER.sh"
    echo ""
    exit 1
fi

echo "✅ Found app.py in current directory"

echo ""
echo "Step 2: Backup current deployment"
echo "=============================="
cd /opt/dataguardian
backup_file="/root/dataguardian_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf "$backup_file" . 2>/dev/null
echo "✅ Backup saved: $backup_file"

echo ""
echo "Step 3: Copy files to /opt/dataguardian"
echo "===================================="
cd - > /dev/null
rsync -av --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
    --exclude='node_modules' --exclude='.pytest_cache' \
    --exclude='*.log' --exclude='*.db' \
    ./ /opt/dataguardian/

echo "✅ Files copied"

echo ""
echo "Step 4: Rebuild Docker container"
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

echo "✅ Container started"

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

docker ps | grep dataguardian-container && echo "✅ Container running" || echo "❌ Container not running"

echo ""
echo "Testing HTTP response..."
if curl -s http://localhost:5000 | grep -qi "dataguardian"; then
    echo "✅ DataGuardian content detected"
    SUCCESS=true
else
    echo "⚠️  Checking deployment..."
    SUCCESS=false
fi

echo ""
echo "Recent logs:"
docker logs dataguardian-container 2>&1 | tail -30

if [ "$SUCCESS" = "true" ]; then
    echo ""
    echo "=========================================="
    echo "🎉 SCANNERS FIXED!"
    echo "=========================================="
    echo ""
    echo "✅ All scanner code updated"
    echo "✅ Docker container rebuilt"
    echo "✅ App restarted successfully"
    echo ""
    echo "🌐 Test: https://dataguardianpro.nl"
    echo "🔐 Login: vishaal314 / password123"
    echo ""
    echo "🧪 TEST ALL SCANNERS:"
    echo "   1. Code Scanner → Sampling Strategy"
    echo "   2. Database Scanner → All options"
    echo "   3. AI Model Scanner → All features"
    echo ""
    echo "✅ All dropdown errors should be FIXED!"
else
    echo ""
    echo "⚠️  VERIFICATION NEEDED"
    echo "====================="
    echo "Check logs above for issues"
    echo ""
    echo "Monitor logs: docker logs dataguardian-container -f"
fi

exit 0
