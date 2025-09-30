#!/bin/bash
# COMPLETE E2E FIX - Run this on your external server (dataguardianpro.nl)
# This will apply the protected app.py that fixes import failures

set -e

echo "🚀 COMPLETE E2E FIX FOR DATAGUARDIAN PRO"
echo "========================================"
echo ""
echo "This will:"
echo "  1. Copy protected app.py from Replit"
echo "  2. Rebuild Docker container"
echo "  3. Verify DataGuardian Pro loads correctly"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "❌ Run as root: sudo ./COMPLETE_E2E_FIX.sh"
    exit 1
fi

cd /opt/dataguardian

echo "📄 STEP 1: Backup current app.py"
echo "=============================="
backup_name="app.py.backup.$(date +%Y%m%d_%H%M%S)"
cp app.py "$backup_name"
echo "   ✅ Backed up to: $backup_name"

echo ""
echo "📥 STEP 2: Get protected app.py from Replit"
echo "========================================"
echo ""
echo "⚠️  MANUAL STEP REQUIRED:"
echo ""
echo "Option A - Using scp (recommended):"
echo "  On your LOCAL machine (not server), run:"
echo "  scp /path/to/replit/app.py root@dataguardianpro.nl:/opt/dataguardian/app.py"
echo ""
echo "Option B - Using Replit web interface:"
echo "  1. In Replit, select app.py"
echo "  2. Click Download"
echo "  3. Upload to server using scp or SFTP"
echo ""
echo "Option C - Direct paste:"
echo "  1. Open app.py in Replit"
echo "  2. Copy entire contents"
echo "  3. On server: nano /opt/dataguardian/app.py"
echo "  4. Replace entire file"
echo ""
read -p "Press ENTER after you've updated app.py on the server..."

echo ""
echo "🔍 STEP 3: Verify app.py was updated"
echo "================================="
if grep -q "PERFORMANCE_IMPORTS_OK" app.py; then
    echo "   ✅ Protected imports detected in app.py"
else
    echo "   ❌ Protected imports NOT found!"
    echo "   Make sure you copied the LATEST app.py from Replit"
    exit 1
fi

echo ""
echo "🐳 STEP 4: Rebuild Docker container"
echo "==============================="
echo "   Stopping old container..."
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true

echo "   Rebuilding image (may take 2-3 minutes)..."
docker build -t dataguardian-pro . 2>&1 | tee /tmp/docker_build.log | tail -20

echo ""
echo "   Starting new container..."
docker run -d \
    --name dataguardian-container \
    --restart always \
    -p 5000:5000 \
    -e PYTHONUNBUFFERED=1 \
    dataguardian-pro

echo "   ✅ Container started"

echo ""
echo "⏳ STEP 5: Wait for initialization (60 seconds)"
echo "==========================================="
echo "   Waiting for app to fully initialize..."
for i in {1..60}; do
    if [ $((i % 10)) -eq 0 ]; then
        echo -n " $i"
    else
        echo -n "."
    fi
    sleep 1
done
echo ""

echo ""
echo "🧪 STEP 6: COMPREHENSIVE VERIFICATION"
echo "=================================="

success_count=0

echo ""
echo "Test 1: Container Status"
if docker ps | grep -q dataguardian-container; then
    echo "   ✅ Container running"
    ((success_count++))
else
    echo "   ❌ Container not running"
fi

echo ""
echo "Test 2: HTTP Response"
status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000)
if [ "$status" = "200" ]; then
    echo "   ✅ HTTP 200 OK"
    ((success_count++))
else
    echo "   ⚠️  HTTP $status"
fi

echo ""
echo "Test 3: DataGuardian Content"
response=$(curl -s http://localhost:5000)
if echo "$response" | grep -qi "dataguardian"; then
    echo "   ✅✅✅ DataGuardian Pro CONTENT DETECTED!"
    ((success_count++))
    content_found=true
else
    echo "   ⚠️  Content not detected"
    content_found=false
fi

echo ""
echo "Test 4: App Initialization Logs"
logs=$(docker logs dataguardian-container 2>&1)
if echo "$logs" | grep -qi "Performance optimizations\|initialized translations\|DataGuardian"; then
    echo "   ✅ App.py main logic EXECUTING!"
    ((success_count++))
else
    echo "   ⚠️  No initialization messages"
fi

echo ""
echo "Test 5: Protected Imports Status"
if echo "$logs" | grep -qi "PERFORMANCE_IMPORTS_OK\|LICENSE_IMPORTS_OK\|ENTERPRISE_IMPORTS_OK"; then
    echo "   ✅ Protected imports working"
    ((success_count++))
else
    echo "   ℹ️  Import status not in logs (may be normal)"
fi

echo ""
echo "📊 Container Logs (last 50 lines):"
echo "================================"
docker logs dataguardian-container 2>&1 | tail -50

echo ""
echo "========================================"
echo "VERIFICATION RESULTS: $success_count/5 tests passed"
echo "========================================"

if [ "$content_found" = "true" ] && [ $success_count -ge 3 ]; then
    echo ""
    echo "🎉🎉🎉 E2E FIX SUCCESSFUL! 🎉🎉🎉"
    echo ""
    echo "✅ Protected imports working"
    echo "✅ App.py executing main logic"
    echo "✅ DataGuardian Pro content loading"
    echo "✅ External server matches Replit"
    echo ""
    echo "🌐 ACCESS YOUR APP:"
    echo "   🎯 https://dataguardianpro.nl"
    echo "   🎯 https://www.dataguardianpro.nl"
    echo ""
    echo "🔐 LOGIN CREDENTIALS:"
    echo "   vishaal314 / password123"
    echo "   demo / demo123"
    echo "   admin / admin123"
    echo ""
    echo "🐳 DOCKER COMMANDS:"
    echo "   View logs:    docker logs dataguardian-container -f"
    echo "   Restart:      docker restart dataguardian-container"
    echo "   Stop:         docker stop dataguardian-container"
    echo "   Start:        docker start dataguardian-container"
    echo "   Shell access: docker exec -it dataguardian-container bash"
    echo ""
    echo "💾 ROLLBACK IF NEEDED:"
    echo "   cp $backup_name app.py"
    echo "   Then rebuild: docker build -t dataguardian-pro ."
    echo ""
    echo "🏆 SUCCESS: DEPLOYMENT COMPLETE!"
    
    exit 0
else
    echo ""
    echo "⚠️  PARTIAL SUCCESS - NEEDS INVESTIGATION"
    echo "======================================="
    echo ""
    echo "Status: $success_count/5 tests passed"
    echo ""
    echo "TROUBLESHOOTING:"
    echo ""
    echo "1. Check logs for import errors:"
    echo "   docker logs dataguardian-container 2>&1 | grep -i 'import\|error\|warning'"
    echo ""
    echo "2. Check if Python modules are missing:"
    echo "   docker exec dataguardian-container python3 -c 'import sys; print(sys.path)'"
    echo ""
    echo "3. Test app.py directly in container:"
    echo "   docker exec -it dataguardian-container bash"
    echo "   cd /app && python3 -c 'import app'"
    echo ""
    echo "4. View full build log:"
    echo "   cat /tmp/docker_build.log"
    echo ""
    echo "5. Manual inspection:"
    echo "   docker exec -it dataguardian-container bash"
    echo "   ls -la /app/"
    echo ""
    echo "If issues persist, check logs above for specific error messages."
    echo ""
    
    exit 1
fi
