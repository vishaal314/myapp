#!/bin/bash
# CLEAR ALL CACHES AND RESTART - Force complete reload
# Fixes persistent 'stats' error by clearing all caches

set -e

echo "🔄 CLEARING ALL CACHES AND RESTARTING"
echo "======================================"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "❌ Run as root: sudo ./CLEAR_CACHE_AND_RESTART.sh"
    exit 1
fi

echo "Step 1: Clear Python bytecode cache in container"
echo "=============================================="

docker exec dataguardian-container find /app -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
docker exec dataguardian-container find /app -type f -name "*.pyc" -delete 2>/dev/null || true
docker exec dataguardian-container find /app -type f -name "*.pyo" -delete 2>/dev/null || true

echo "✅ Cleared Python bytecode cache"

echo ""
echo "Step 2: Clear Streamlit cache"
echo "=========================="

docker exec dataguardian-container rm -rf /root/.streamlit/cache 2>/dev/null || true
docker exec dataguardian-container rm -rf ~/.streamlit/cache 2>/dev/null || true

echo "✅ Cleared Streamlit cache"

echo ""
echo "Step 3: Stop container and clear Docker cache"
echo "=========================================="

docker stop dataguardian-container
docker rm dataguardian-container

echo "✅ Container removed"

echo ""
echo "Step 4: Rebuild Docker image (fresh build)"
echo "======================================"

cd /opt/dataguardian

# Remove old image
docker rmi dataguardian-pro 2>/dev/null || true

# Build fresh
echo "Building fresh image (this takes 60-90 seconds)..."
docker build --no-cache -t dataguardian-pro . 2>&1 | tail -30

echo "✅ Fresh image built"

echo ""
echo "Step 5: Start container with environment variables"
echo "=============================================="

# Source environment file if it exists
if [ -f "/root/.dataguardian_env" ]; then
    echo "Using environment from /root/.dataguardian_env"
    docker run -d \
        --name dataguardian-container \
        --restart always \
        -p 5000:5000 \
        --env-file /root/.dataguardian_env \
        dataguardian-pro
else
    echo "⚠️  No environment file found, starting without custom env vars"
    docker run -d \
        --name dataguardian-container \
        --restart always \
        -p 5000:5000 \
        -e PYTHONUNBUFFERED=1 \
        dataguardian-pro
fi

echo "✅ Container started"

echo ""
echo "Step 6: Wait for full initialization (60 seconds)"
echo "============================================"

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
echo "Step 7: Verify application"
echo "======================="

# Check container
if docker ps | grep -q dataguardian-container; then
    echo "✅ Container running"
else
    echo "❌ Container not running!"
    docker logs dataguardian-container 2>&1 | tail -30
    exit 1
fi

# Check HTTP
sleep 5
if curl -s http://localhost:5000 | grep -qi "streamlit"; then
    echo "✅ HTTP responding"
fi

# Check for errors in logs
echo ""
echo "Checking for errors..."

if docker logs dataguardian-container 2>&1 | tail -100 | grep -qi "unboundlocalerror.*stats"; then
    echo "❌ 'stats' error STILL in logs"
    echo "Showing relevant logs:"
    docker logs dataguardian-container 2>&1 | grep -i "unboundlocalerror" | tail -10
else
    echo "✅ No 'stats' error in logs"
fi

if docker logs dataguardian-container 2>&1 | tail -100 | grep -qi "error"; then
    echo "⚠️  Some errors found in logs:"
    docker logs dataguardian-container 2>&1 | grep -i "error" | tail -10
fi

echo ""
echo "Recent logs:"
docker logs dataguardian-container 2>&1 | tail -25

echo ""
echo "=========================================="
echo "🎉 COMPLETE CACHE CLEAR & RESTART DONE!"
echo "=========================================="
echo ""
echo "✅ Python bytecode cache cleared"
echo "✅ Streamlit cache cleared"
echo "✅ Docker image rebuilt (no cache)"
echo "✅ Container restarted fresh"
echo ""
echo "🌐 IMPORTANT - CLEAR YOUR BROWSER CACHE:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "In your browser at https://dataguardianpro.nl:"
echo ""
echo "   Chrome/Edge:"
echo "   - Press Ctrl+Shift+Delete (Windows) or Cmd+Shift+Delete (Mac)"
echo "   - OR just press Ctrl+F5 for hard refresh"
echo ""
echo "   Firefox:"
echo "   - Press Ctrl+Shift+R for hard refresh"
echo ""
echo "   Safari:"
echo "   - Press Cmd+Option+R for hard refresh"
echo ""
echo "OR EASIEST: Use Incognito/Private window"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🧪 TEST CODE SCANNER:"
echo "   1. Open https://dataguardianpro.nl in INCOGNITO mode"
echo "   2. Login: vishaal314 / password123"
echo "   3. Go to Code Scanner"
echo "   4. Select: Scanning Strategy → Smart"
echo "   5. Enter repo URL"
echo "   6. Click Start Scan"
echo ""
echo "✅ Should work WITHOUT 'stats' error!"
echo ""
echo "📊 Monitor logs:"
echo "   docker logs dataguardian-container -f"

exit 0
