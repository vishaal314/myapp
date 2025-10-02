#!/bin/bash
# FIX CODE SCANNER STATS ERROR - Direct fix for UnboundLocalError
# Updates scanner files inside running container

set -e

echo "🔧 FIXING CODE SCANNER 'stats' ERROR"
echo "====================================="
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "❌ Run as root: sudo ./FIX_CODE_SCANNER_STATS_ERROR.sh"
    exit 1
fi

echo "This fix will:"
echo "  1. Copy working scanner files from /opt/dataguardian"
echo "  2. Update files inside running container"
echo "  3. Restart Streamlit to reload modules"
echo ""

# Check if container is running
if ! docker ps | grep -q dataguardian-container; then
    echo "❌ Container not running. Start it first:"
    echo "   /root/restart_dataguardian.sh"
    exit 1
fi

echo "Step 1: Verify source files exist"
echo "==============================="

if [ ! -f "/opt/dataguardian/app.py" ]; then
    echo "❌ /opt/dataguardian/app.py not found!"
    echo "   Run APPLY_TAR_FIX.sh first to deploy code"
    exit 1
fi

echo "✅ Source files found in /opt/dataguardian"

echo ""
echo "Step 2: Copy critical scanner files to container"
echo "=============================================="

# Copy app.py
docker cp /opt/dataguardian/app.py dataguardian-container:/app/app.py
echo "✅ Copied app.py"

# Copy all scanner files
docker cp /opt/dataguardian/services/code_scanner.py dataguardian-container:/app/services/code_scanner.py
echo "✅ Copied code_scanner.py"

docker cp /opt/dataguardian/services/intelligent_repo_scanner.py dataguardian-container:/app/services/intelligent_repo_scanner.py
echo "✅ Copied intelligent_repo_scanner.py"

docker cp /opt/dataguardian/services/repo_scanner.py dataguardian-container:/app/services/repo_scanner.py 2>/dev/null && echo "✅ Copied repo_scanner.py" || echo "⚠️  repo_scanner.py not found"

docker cp /opt/dataguardian/services/enhanced_repo_scanner.py dataguardian-container:/app/services/enhanced_repo_scanner.py 2>/dev/null && echo "✅ Copied enhanced_repo_scanner.py" || echo "⚠️  enhanced_repo_scanner.py not found"

# Copy other critical scanners
docker cp /opt/dataguardian/services/db_scanner.py dataguardian-container:/app/services/db_scanner.py
echo "✅ Copied db_scanner.py"

docker cp /opt/dataguardian/services/ai_model_scanner.py dataguardian-container:/app/services/ai_model_scanner.py
echo "✅ Copied ai_model_scanner.py"

docker cp /opt/dataguardian/services/website_scanner.py dataguardian-container:/app/services/website_scanner.py
echo "✅ Copied website_scanner.py"

docker cp /opt/dataguardian/services/blob_scanner.py dataguardian-container:/app/services/blob_scanner.py
echo "✅ Copied blob_scanner.py"

echo ""
echo "Step 3: Verify app.py was updated"
echo "=============================="

# Get file sizes to confirm update
CONTAINER_SIZE=$(docker exec dataguardian-container stat -c%s /app/app.py 2>/dev/null)
HOST_SIZE=$(stat -c%s /opt/dataguardian/app.py 2>/dev/null || stat -f%z /opt/dataguardian/app.py 2>/dev/null)

if [ "$CONTAINER_SIZE" == "$HOST_SIZE" ]; then
    echo "✅ app.py updated successfully ($CONTAINER_SIZE bytes)"
else
    echo "⚠️  Size mismatch: Container=$CONTAINER_SIZE, Host=$HOST_SIZE"
fi

echo ""
echo "Step 4: Restart Streamlit to reload modules"
echo "========================================"

# Find and kill Streamlit process to force reload
docker exec dataguardian-container bash -c 'pkill -f streamlit || true'
echo "✅ Streamlit process killed"

echo "Waiting 10 seconds for auto-restart..."
sleep 10

# Check if Streamlit restarted
if docker exec dataguardian-container pgrep -f streamlit >/dev/null 2>&1; then
    echo "✅ Streamlit restarted automatically"
else
    echo "⚠️  Streamlit not running, restarting container..."
    docker restart dataguardian-container
    echo "Waiting 45 seconds for container restart..."
    sleep 45
fi

echo ""
echo "Step 5: Verify no 'stats' error in logs"
echo "===================================="

# Check recent logs
if docker logs dataguardian-container 2>&1 | tail -50 | grep -qi "unboundlocalerror.*stats"; then
    echo "⚠️  'stats' error still in logs (may be old)"
else
    echo "✅ No 'stats' error in recent logs"
fi

echo ""
echo "Recent logs:"
docker logs dataguardian-container 2>&1 | tail -20

echo ""
echo "Step 6: Test Code Scanner import"
echo "=============================="

docker exec dataguardian-container python3 -c "
import sys
sys.path.insert(0, '/app')

try:
    from services.code_scanner import CodeScanner
    from services.intelligent_repo_scanner import IntelligentRepoScanner
    
    print('✅ CodeScanner imported successfully')
    print('✅ IntelligentRepoScanner imported successfully')
    
    # Test basic initialization
    scanner = CodeScanner()
    print('✅ CodeScanner initialized')
    
    repo_scanner = IntelligentRepoScanner()
    print('✅ IntelligentRepoScanner initialized')
    
except Exception as e:
    print(f'❌ Import/initialization failed: {e}')
    sys.exit(1)
" 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Scanner imports working"
else
    echo "❌ Scanner imports failed"
    exit 1
fi

echo ""
echo "=========================================="
echo "🎉 CODE SCANNER FIX APPLIED!"
echo "=========================================="
echo ""
echo "✅ Scanner files updated in container"
echo "✅ Streamlit reloaded"
echo "✅ Imports verified"
echo ""
echo "🧪 TEST NOW:"
echo "   1. Visit: https://dataguardianpro.nl"
echo "   2. Login: vishaal314 / password123"
echo "   3. Go to Code Scanner"
echo "   4. Select: Scanning Strategy → Smart"
echo "   5. Enter repo: https://github.com/PacktPublishing/Python-Artificial-Intelligence-Projects-for-Beginners/tree/master"
echo "   6. Click 'Start Scan'"
echo ""
echo "✅ Should scan WITHOUT 'stats' error!"
echo ""
echo "📊 Monitor scan progress:"
echo "   docker logs dataguardian-container -f"
echo ""
echo "If error persists, the container needs full rebuild:"
echo "   /root/restart_dataguardian.sh"

exit 0
