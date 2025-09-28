#!/bin/bash
# QUICK UI FIX - Fast Streamlit configuration fix
# Addresses Streamlit serving generic HTML instead of DataGuardian Pro content
# Simplified version to avoid interruption

echo "⚡ QUICK UI FIX - STREAMLIT CONFIGURATION"
echo "========================================"
echo "Goal: Fix Streamlit to serve DataGuardian Pro content instead of generic HTML"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "❌ Run as root: sudo ./quick_ui_fix.sh"
    exit 1
fi

DOMAIN="dataguardianpro.nl"
APP_PORT="5000"
APP_DIR="/opt/dataguardian"

echo "🔧 STEP 1: CLEAR STREAMLIT CACHE QUICKLY"
echo "======================================"

cd "$APP_DIR"

# Clear Streamlit cache quickly
echo "🧹 Clearing Streamlit cache..."
rm -rf /root/.streamlit /tmp/streamlit* $HOME/.cache/streamlit 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

echo "   ✅ Cache cleared"

echo ""
echo "⚙️  STEP 2: CREATE STREAMLIT CONFIG"
echo "=============================="

mkdir -p "$APP_DIR/.streamlit"

cat > "$APP_DIR/.streamlit/config.toml" << 'EOF'
[server]
headless = true
address = "0.0.0.0"
port = 5000
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 200

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#0066CC"

[runner]
magicEnabled = true
fastReruns = true
EOF

echo "   ✅ Streamlit config created"

echo ""
echo "🔄 STEP 3: RESTART DATAGUARDIAN SERVICE"
echo "====================================="

echo "🔄 Restarting DataGuardian service..."
systemctl restart dataguardian
sleep 15

echo "⏳ Testing service startup..."
for i in {1..30}; do
    if systemctl is-active dataguardian >/dev/null 2>&1; then
        echo -n "✓"
    else
        echo -n "x"
    fi
    sleep 2
done
echo ""

service_status=$(systemctl is-active dataguardian)
echo "   📊 Service status: $service_status"

echo ""
echo "🧪 STEP 4: TEST CONTENT IMMEDIATELY" 
echo "==============================="

echo "🧪 Testing for DataGuardian Pro content..."

# Quick content test
for attempt in {1..5}; do
    echo "   Test $attempt:"
    
    # Local test
    local_response=$(curl -s http://localhost:$APP_PORT 2>/dev/null | head -c 2000)
    if echo "$local_response" | grep -qi "dataguardian pro"; then
        echo "     🎯 Local: DataGuardian Pro content detected!"
        local_success=true
    elif echo "$local_response" | grep -qi "scanner.*compliance\|enterprise.*privacy"; then
        echo "     ✅ Local: Privacy compliance content detected!"
        local_success=true
    elif echo "$local_response" | grep -q '<title>Streamlit</title>'; then
        echo "     ⚠️  Local: Generic Streamlit shell"
        local_success=false
    else
        echo "     ❓ Local: Unknown content"
        local_success=false
    fi
    
    # Domain test
    domain_response=$(curl -s https://www.$DOMAIN 2>/dev/null | head -c 2000)
    if echo "$domain_response" | grep -qi "dataguardian pro"; then
        echo "     🎯 Domain: DataGuardian Pro content detected!"
        domain_success=true
    elif echo "$domain_response" | grep -qi "scanner.*compliance\|enterprise.*privacy"; then
        echo "     ✅ Domain: Privacy compliance content detected!"
        domain_success=true
    elif echo "$domain_response" | grep -q '<title>Streamlit</title>'; then
        echo "     ⚠️  Domain: Generic Streamlit shell"
        domain_success=false
    else
        echo "     ❓ Domain: Unknown content"
        domain_success=false
    fi
    
    if [ "$local_success" = true ] && [ "$domain_success" = true ]; then
        echo "     🎉 SUCCESS: DataGuardian Pro content detected on both!"
        break
    fi
    
    sleep 10
done

echo ""
echo "📊 QUICK FIX RESULTS"
echo "=================="

if [ "$service_status" = "active" ]; then
    echo "✅ Service: RUNNING"
else
    echo "❌ Service: NOT RUNNING"
fi

if [ "$local_success" = true ]; then
    echo "✅ Local UI: DATAGUARDIAN CONTENT DETECTED"
else
    echo "⚠️  Local UI: STILL GENERIC STREAMLIT"
fi

if [ "$domain_success" = true ]; then
    echo "✅ Domain UI: DATAGUARDIAN CONTENT DETECTED"
else
    echo "⚠️  Domain UI: STILL GENERIC STREAMLIT"
fi

if [ "$local_success" = true ] && [ "$domain_success" = true ]; then
    echo ""
    echo "🎉 SUCCESS: DATAGUARDIAN PRO UI IS WORKING!"
    echo "========================================="
    echo ""
    echo "✅ Quick fix successful!"
    echo "✅ DataGuardian Pro content loading properly"
    echo "✅ No more generic Streamlit shell"
    echo ""
    echo "🌐 Your sites are operational:"
    echo "   🎯 https://dataguardianpro.nl"
    echo "   🎯 https://www.dataguardianpro.nl"
    echo ""
    echo "🇳🇱 Netherlands GDPR compliance platform is LIVE!"
    
elif [ "$local_success" = true ]; then
    echo ""
    echo "✅ PARTIAL SUCCESS - LOCAL WORKING"
    echo "==============================="
    echo ""
    echo "✅ Local DataGuardian content: WORKING"
    echo "⚠️  Domain: May need more time to update"
    echo ""
    echo "💡 Try again in 5-10 minutes for domain"
    
else
    echo ""
    echo "⚠️  NEEDS MORE WORK"
    echo "=================="
    echo ""
    echo "📊 Service running but still serving generic Streamlit"
    echo ""
    echo "🔧 Try these manual commands:"
    echo "   systemctl restart dataguardian"
    echo "   sleep 30"
    echo "   curl -s http://localhost:5000 | grep -i dataguardian"
fi

echo ""
echo "🎯 VERIFICATION:"
echo "==============="
echo "   Test content: curl -s https://www.$DOMAIN | head -50"
echo "   Check service: systemctl status dataguardian"
echo "   View logs: journalctl -u dataguardian -n 20"

echo ""
echo "✅ QUICK UI FIX COMPLETE!"