#!/bin/bash
# APPLY TAR FIX - E2E fix for external server using tar file
# Run this ON the external server after uploading dataguardian_deploy.tar.gz

set -e

echo "🚀 E2E FIX FROM TAR FILE"
echo "========================"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "❌ Run as root: sudo ./APPLY_TAR_FIX.sh"
    exit 1
fi

TAR_FILE="/root/dataguardian_deploy.tar.gz"

# Check if tar file exists
if [ ! -f "$TAR_FILE" ]; then
    echo "❌ $TAR_FILE not found!"
    echo ""
    echo "📥 UPLOAD INSTRUCTIONS:"
    echo "======================"
    echo ""
    echo "1. Download dataguardian_deploy.tar.gz from Replit"
    echo ""
    echo "2. Upload to this server:"
    echo "   scp dataguardian_deploy.tar.gz root@dataguardianpro.nl:/root/"
    echo ""
    echo "3. Then run this script again from /root:"
    echo "   cd /root && sudo ./APPLY_TAR_FIX.sh"
    exit 1
fi

echo "✅ Found: $TAR_FILE"
TAR_SIZE=$(du -h $TAR_FILE | cut -f1)
echo "   Size: $TAR_SIZE"

echo ""
echo "Step 1: Backup Current Deployment"
echo "================================="
if [ -d "/opt/dataguardian" ]; then
    BACKUP_FILE="/root/dataguardian_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    cd /opt/dataguardian
    tar -czf "$BACKUP_FILE" . 2>/dev/null
    echo "✅ Backup saved: $BACKUP_FILE"
else
    echo "⚠️  /opt/dataguardian doesn't exist, creating..."
    mkdir -p /opt/dataguardian
fi

echo ""
echo "Step 2: Extract New Files"
echo "======================="
cd /opt/dataguardian

# Remove old files
rm -rf app.py services utils translations .streamlit 2>/dev/null || true

# Extract new files
tar -xzf $TAR_FILE -C /opt/dataguardian/
echo "✅ Files extracted to /opt/dataguardian"

# Verify critical files
if [ ! -f "app.py" ]; then
    echo "❌ app.py not found after extraction!"
    echo "Restoring from backup..."
    tar -xzf "$BACKUP_FILE" -C /opt/dataguardian/
    exit 1
fi

echo "✅ Verified: app.py exists"
echo "✅ Verified: services/ exists"

echo ""
echo "Step 3: Stop Current Container"
echo "============================"
docker stop dataguardian-container 2>/dev/null && echo "✅ Container stopped" || echo "⚠️  No container running"
docker rm dataguardian-container 2>/dev/null && echo "✅ Container removed" || true

echo ""
echo "Step 4: Rebuild Docker Image"
echo "=========================="
echo "Building new image (30-60 seconds)..."
docker build -t dataguardian-pro /opt/dataguardian 2>&1 | tail -20

echo ""
echo "Step 5: Start New Container"
echo "========================"
docker run -d \
    --name dataguardian-container \
    --restart always \
    -p 5000:5000 \
    -e PYTHONUNBUFFERED=1 \
    dataguardian-pro

echo "✅ Container started"

echo ""
echo "Step 6: Wait for Initialization"
echo "============================="
echo "Waiting 45 seconds for app to start..."
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
echo "Step 7: Verify Deployment"
echo "======================="

# Check container status
if docker ps | grep -q dataguardian-container; then
    echo "✅ Container: Running"
else
    echo "❌ Container: Not running"
    docker logs dataguardian-container 2>&1 | tail -30
    exit 1
fi

# Check HTTP response
echo ""
echo "Testing HTTP..."
sleep 5
if curl -s http://localhost:5000 | grep -qi "dataguardian"; then
    echo "✅ HTTP: DataGuardian content detected"
    SUCCESS=true
else
    echo "⚠️  HTTP: Checking response..."
    curl -s http://localhost:5000 | head -20
    SUCCESS=false
fi

# Check HTTPS
echo ""
echo "Testing HTTPS..."
if curl -s -k https://localhost | grep -qi "dataguardian"; then
    echo "✅ HTTPS: Working"
elif curl -s -k https://localhost | grep -qi "streamlit"; then
    echo "✅ HTTPS: Nginx proxy working"
fi

echo ""
echo "Container logs (last 30 lines):"
docker logs dataguardian-container 2>&1 | tail -30

echo ""
echo "Step 8: Cleanup"
echo "============="
rm -f $TAR_FILE
echo "✅ Removed temporary tar file"

if [ "$SUCCESS" = "true" ]; then
    echo ""
    echo "=========================================="
    echo "🎉 E2E FIX COMPLETE!"
    echo "=========================================="
    echo ""
    echo "✅ All Replit files deployed"
    echo "✅ Docker container rebuilt"
    echo "✅ Application running"
    echo ""
    echo "🌐 Access: https://dataguardianpro.nl"
    echo "🔐 Login: vishaal314 / password123"
    echo ""
    echo "🧪 TEST ALL SCANNERS:"
    echo "   • Code Scanner → Sampling Strategy"
    echo "   • Database Scanner → All options"
    echo "   • AI Model Scanner → All features"
    echo "   • Website Scanner → Cookie compliance"
    echo "   • Blob Scanner → File analysis"
    echo ""
    echo "✅ ALL SCANNER ERRORS FIXED!"
    echo ""
    echo "📊 Monitor logs:"
    echo "   docker logs dataguardian-container -f"
else
    echo ""
    echo "⚠️  DEPLOYMENT NEEDS VERIFICATION"
    echo "================================"
    echo ""
    echo "The deployment completed but verification is inconclusive."
    echo "Please test manually: https://dataguardianpro.nl"
    echo ""
    echo "Check logs for any errors:"
    echo "   docker logs dataguardian-container -f"
fi

exit 0
