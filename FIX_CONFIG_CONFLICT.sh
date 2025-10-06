#!/bin/bash
################################################################################
# FIX CONFIG CONFLICT - Remove conflicting config.py file
################################################################################

set -e

echo "🔧 Fixing config.py conflict..."

APP_DIR="/opt/dataguardian"
cd "$APP_DIR"

# Check for conflicting config.py file
if [ -f "config.py" ]; then
    echo "❌ Found conflicting config.py file (should be config/ directory)"
    echo "   Removing config.py..."
    rm -f config.py
    echo "✅ Removed config.py"
else
    echo "✅ No conflicting config.py found"
fi

# Verify config package exists
if [ -d "config" ] && [ -f "config/__init__.py" ]; then
    echo "✅ config/ package directory exists"
    ls -la config/
else
    echo "❌ ERROR: config/ package directory missing!"
    exit 1
fi

# Restart container
echo ""
echo "🔄 Restarting container..."
docker restart dataguardian-container

echo ""
echo "⏳ Waiting 20 seconds for startup..."
sleep 20

echo ""
echo "📋 Checking logs for errors..."
docker logs dataguardian-container 2>&1 | tail -30

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if docker logs dataguardian-container 2>&1 | grep -q "No module named 'config.pricing_config'"; then
    echo "❌ Config import still failing"
else
    echo "✅ Config import fixed!"
fi

if docker logs dataguardian-container 2>&1 | grep -q "You can now view your Streamlit app"; then
    echo "✅ Streamlit running"
fi

echo ""
echo "🌐 Test at: https://dataguardianpro.nl"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
