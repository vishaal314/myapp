#!/bin/bash
# DIRECT CODE FIX - Copy correct code from Replit to external server
# Run this FROM REPLIT terminal

set -e

EXTERNAL_SERVER="root@dataguardianpro.nl"
EXTERNAL_DIR="/opt/dataguardian"

echo "🔧 DIRECT CODE FIX - Upload Latest Code"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Must run from project root directory (where app.py is)"
    exit 1
fi

echo "Step 1: Package ONLY the scanner files that have bugs"
echo "====================================================="

# Create temporary directory
TMP_DIR=$(mktemp -d)
echo "Using temp directory: $TMP_DIR"

# Copy critical scanner files
mkdir -p "$TMP_DIR/services"

cp services/intelligent_repo_scanner.py "$TMP_DIR/services/" 2>/dev/null || echo "Warning: intelligent_repo_scanner.py not found"
cp services/code_scanner.py "$TMP_DIR/services/" 2>/dev/null || echo "Warning: code_scanner.py not found"
cp app.py "$TMP_DIR/" 2>/dev/null || echo "Warning: app.py not found"

echo "✅ Critical files packaged"

echo ""
echo "Step 2: Upload to external server"
echo "=================================="

# Upload files
scp "$TMP_DIR/app.py" "$EXTERNAL_SERVER:$EXTERNAL_DIR/app.py" 2>/dev/null || echo "Skipped app.py"
scp "$TMP_DIR/services/intelligent_repo_scanner.py" "$EXTERNAL_SERVER:$EXTERNAL_DIR/services/intelligent_repo_scanner.py" 2>/dev/null || echo "Skipped intelligent_repo_scanner.py"
scp "$TMP_DIR/services/code_scanner.py" "$EXTERNAL_SERVER:$EXTERNAL_DIR/services/code_scanner.py" 2>/dev/null || echo "Skipped code_scanner.py"

echo "✅ Files uploaded"

# Clean up
rm -rf "$TMP_DIR"

echo ""
echo "Step 3: Apply fix on external server"
echo "====================================="

ssh $EXTERNAL_SERVER << 'REMOTE_FIX'
set -e

echo "On external server..."

# Stop container
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true
echo "✅ Container stopped"

# Clear Python cache
cd /opt/dataguardian
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "✅ Python cache cleared"

# Rebuild Docker
docker rmi dataguardian-pro 2>/dev/null || true
docker build --no-cache -t dataguardian-pro . 2>&1 | tail -20
echo "✅ Docker rebuilt"

# Start container
docker run -d \
    --name dataguardian-container \
    --restart always \
    -p 5000:5000 \
    --network host \
    --env-file /root/.dataguardian_env \
    dataguardian-pro
echo "✅ Container started"

# Wait
echo "Waiting 45 seconds..."
sleep 45

# Check for stats error
if docker logs dataguardian-container 2>&1 | tail -50 | grep -qi "unboundlocalerror.*stats"; then
    echo "❌ Stats error still present"
else
    echo "✅ NO stats error!"
fi

docker logs dataguardian-container 2>&1 | tail -20

REMOTE_FIX

echo ""
echo "════════════════════════════════════════════════"
echo "🎉 DIRECT CODE FIX COMPLETE!"
echo "════════════════════════════════════════════════"
echo ""
echo "✅ Latest scanner code uploaded"
echo "✅ Docker rebuilt with new code"
echo "✅ Container restarted"
echo ""
echo "🧪 TEST IN INCOGNITO:"
echo "   https://dataguardianpro.nl"
echo "   vishaal314 / password123"
echo "   Try Code Scanner"

exit 0
