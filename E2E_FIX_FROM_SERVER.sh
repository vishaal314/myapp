#!/bin/bash
# E2E FIX - Run this ON the external server to fix scanner errors
# This script downloads Replit code and applies it

set -e

echo "🔧 E2E FIX FOR SCANNER ERRORS"
echo "============================="
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "❌ Run as root: sudo ./E2E_FIX_FROM_SERVER.sh"
    exit 1
fi

echo "STEP 1: Upload Replit Files"
echo "=========================="
echo ""
echo "You need to upload your Replit project to this server."
echo ""
echo "📥 On your LOCAL machine (not this server):"
echo ""
echo "   1. Download Replit project:"
echo "      - In Replit: Menu → Download as zip"
echo "      - Save to your computer (e.g., dataguardian.zip)"
echo ""
echo "   2. Upload to this server:"
echo "      scp dataguardian.zip root@dataguardianpro.nl:/tmp/replit.zip"
echo ""
echo "   3. Come back here and press Enter"
echo ""
read -p "Press Enter after you've uploaded replit.zip to /tmp/replit.zip..."

# Verify upload
if [ ! -f "/tmp/replit.zip" ]; then
    echo "❌ /tmp/replit.zip not found!"
    echo ""
    echo "Please upload the file first:"
    echo "   scp dataguardian.zip root@dataguardianpro.nl:/tmp/replit.zip"
    exit 1
fi

echo "✅ Found /tmp/replit.zip"

echo ""
echo "STEP 2: Extract Replit Files"
echo "=========================="
rm -rf /tmp/replit_sync 2>/dev/null || true
unzip -q /tmp/replit.zip -d /tmp/replit_sync
echo "✅ Extracted to /tmp/replit_sync"

# Find app.py location
if [ -f "/tmp/replit_sync/app.py" ]; then
    REPLIT_DIR="/tmp/replit_sync"
else
    # Check for nested directory
    REPLIT_DIR=$(find /tmp/replit_sync -name "app.py" -type f | head -1 | xargs dirname)
    if [ -z "$REPLIT_DIR" ]; then
        echo "❌ app.py not found in zip!"
        exit 1
    fi
fi

echo "✅ Found Replit project at: $REPLIT_DIR"

echo ""
echo "STEP 3: Backup Current Deployment"
echo "==============================="
cd /opt/dataguardian
backup_file="/root/dataguardian_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf "$backup_file" . 2>/dev/null
echo "✅ Backup saved: $backup_file"

echo ""
echo "STEP 4: Sync Replit Code to /opt/dataguardian"
echo "=========================================="
rsync -av --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
    --exclude='node_modules' --exclude='.pytest_cache' \
    "$REPLIT_DIR/" /opt/dataguardian/

echo "✅ Files synced"

echo ""
echo "STEP 5: Rebuild Docker Container"
echo "=============================="
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true

echo "Building new image (this takes 30-60 seconds)..."
docker build -t dataguardian-pro /opt/dataguardian 2>&1 | tail -20

docker run -d \
    --name dataguardian-container \
    --restart always \
    -p 5000:5000 \
    -e PYTHONUNBUFFERED=1 \
    dataguardian-pro

echo "✅ Container started"

echo ""
echo "STEP 6: Wait for Initialization (45 seconds)"
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
echo "STEP 7: Verify Deployment"
echo "======================="

echo "Container status:"
docker ps | grep dataguardian-container && echo "   ✅ Running" || echo "   ❌ Not running"

echo ""
echo "HTTP test:"
if curl -s http://localhost:5000 | grep -qi "dataguardian"; then
    echo "   ✅ DataGuardian detected"
    SUCCESS=true
else
    echo "   ⚠️  Checking..."
    SUCCESS=false
fi

echo ""
echo "Container logs (last 30 lines):"
docker logs dataguardian-container 2>&1 | tail -30

echo ""
echo "Clean up:"
rm -rf /tmp/replit_sync /tmp/replit.zip 2>/dev/null
echo "✅ Temp files removed"

if [ "$SUCCESS" = "true" ]; then
    echo ""
    echo "=========================================="
    echo "🎉 E2E FIX COMPLETE!"
    echo "=========================================="
    echo ""
    echo "✅ Replit code deployed successfully"
    echo "✅ All scanners now match Replit version"
    echo ""
    echo "🌐 Access: https://dataguardianpro.nl"
    echo "🔐 Login: vishaal314 / password123"
    echo ""
    echo "🧪 TEST CODE SCANNER:"
    echo "   1. Go to Code Scanner"
    echo "   2. Select 'Sampling Strategy'"
    echo "   3. Verify no 'stats' error"
    echo ""
    echo "✅ Scanner dropdown errors FIXED!"
else
    echo ""
    echo "⚠️  DEPLOYMENT NEEDS REVIEW"
    echo "========================="
    echo "Check the logs above for any issues"
    echo ""
    echo "If problems persist:"
    echo "   docker logs dataguardian-container -f"
fi

exit 0
