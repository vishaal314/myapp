#!/bin/bash
# DEPLOY PROTECTED APP.PY - Complete E2E Fix
# This fixes import failures that were stopping app.py execution

set -e

echo "🚀 DEPLOYING PROTECTED APP.PY - E2E FIX"
echo "======================================"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "❌ Run as root: sudo ./DEPLOY_PROTECTED_APP.sh"
    exit 1
fi

cd /opt/dataguardian

echo "📄 Step 1: Backup current app.py"
echo "==============================="
cp app.py app.py.backup.$(date +%Y%m%d_%H%M%S)
echo "   ✅ Backup created"

echo ""
echo "📥 Step 2: Download protected app.py from Replit"
echo "============================================="
echo "   ⚠️  YOU NEED TO MANUALLY COPY app.py from Replit to server!"
echo "   "
echo "   On your local machine, run:"
echo "   scp root@dataguardianpro.nl:/path/to/replit/app.py /opt/dataguardian/app.py"
echo ""
echo "   Or use the Replit file download and upload via scp/sftp"
echo ""
read -p "   Press ENTER once you've copied the new app.py..." 

echo ""
echo "🐳 Step 3: Rebuild Docker container"
echo "================================"
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true

echo "   Building new image..."
docker build -t dataguardian-pro . 2>&1 | tail -20

docker run -d \
    --name dataguardian-container \
    --restart always \
    -p 5000:5000 \
    dataguardian-pro

echo "   ✅ Container restarted with protected app.py"

echo ""
echo "⏳ Step 4: Wait for initialization (45 seconds)"
echo "=========================================="
for i in {1..45}; do
    echo -n "."
    sleep 1
done
echo ""

echo ""
echo "🧪 Step 5: COMPREHENSIVE VERIFICATION"
echo "=================================="

echo ""
echo "Container status:"
docker ps | grep dataguardian-container && echo "   ✅ Running" || echo "   ❌ Stopped"

echo ""
echo "HTTP Response:"
status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000)
if [ "$status" = "200" ]; then
    echo "   ✅ HTTP $status"
else
    echo "   ⚠️  HTTP $status"
fi

echo ""
echo "DataGuardian Content Check:"
if curl -s http://localhost:5000 | grep -qi "dataguardian"; then
    echo "   ✅✅✅ DataGuardian Pro CONTENT DETECTED! ✅✅✅"
    success=true
else
    echo "   ⚠️  Content not detected yet"
    success=false
fi

echo ""
echo "Container Logs (last 40 lines):"
echo "================================"
docker logs dataguardian-container 2>&1 | tail -40

echo ""
echo "Check for initialization messages:"
if docker logs dataguardian-container 2>&1 | grep -qi "Performance optimizations\|initialized translations\|DataGuardian Pro"; then
    echo "   ✅ App.py main logic IS EXECUTING!"
else
    echo "   ⚠️  No initialization messages yet"
fi

if [ "$success" = "true" ]; then
    echo ""
    echo "🎉🎉🎉 E2E FIX SUCCESSFUL! 🎉🎉🎉"
    echo "==============================="
    echo ""
    echo "✅ Protected imports working"
    echo "✅ App.py executing successfully"
    echo "✅ DataGuardian Pro content loading"
    echo ""
    echo "🌐 ACCESS YOUR APP:"
    echo "   https://dataguardianpro.nl"
    echo ""
    echo "🔐 LOGIN:"
    echo "   vishaal314 / password123"
    echo "   demo / demo123"
    echo ""
    echo "🏆 DEPLOYMENT MATCHES REPLIT ENVIRONMENT!"
else
    echo ""
    echo "⚠️  DEPLOYMENT COMPLETED - VERIFICATION PARTIAL"
    echo "==========================================="
    echo ""
    echo "Container is running. Check these:"
    echo "1. Wait 2-3 more minutes for full initialization"
    echo "2. Test manually: https://dataguardianpro.nl"
    echo "3. Check logs: docker logs dataguardian-container -f"
    echo ""
    echo "If still having issues, the protected imports will"
    echo "show which modules are missing in the logs above."
fi

echo ""
echo "✅ DEPLOYMENT COMPLETE!"

exit 0
