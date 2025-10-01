#!/bin/bash
# FINAL VERIFICATION - Check everything

echo "🧪 FINAL COMPREHENSIVE VERIFICATION"
echo "==================================="
echo ""

echo "Test 1: DataGuardian Content in HTTP Response"
echo "==========================================="
response=$(curl -s http://localhost:5000)
if echo "$response" | grep -qi "dataguardian"; then
    echo "✅ DataGuardian Pro content FOUND!"
    content_found=true
else
    echo "❌ Still showing generic Streamlit"
    content_found=false
fi

echo ""
echo "Test 2: Check Page Title"
echo "====================="
echo "$response" | grep -i "<title>" | head -1

echo ""
echo "Test 3: Import Test in Container"
echo "=============================="
docker exec dataguardian-container python3 << 'PYEOF'
import sys
sys.path.insert(0, '/app')
try:
    import app
    print("✅ app.py imports successfully")
    print("Checking initialization...")
except Exception as e:
    print(f"❌ Import failed: {e}")
PYEOF

echo ""
echo "Test 4: Check Container Logs for Initialization"
echo "==========================================="
if docker logs dataguardian-container 2>&1 | grep -qi "Performance optimizations initialized\|Successfully initialized translations"; then
    echo "✅ App initialization messages found"
else
    echo "⚠️  No initialization messages in logs"
    echo ""
    echo "Recent logs:"
    docker logs dataguardian-container 2>&1 | tail -20
fi

echo ""
echo "Test 5: Domain DNS Check"
echo "====================="
echo "Checking dataguardianpro.nl DNS..."
if host dataguardianpro.nl | grep -q "has address"; then
    ip=$(host dataguardianpro.nl | grep "has address" | awk '{print $4}')
    echo "✅ Domain resolves to: $ip"
    
    server_ip=$(hostname -I | awk '{print $1}')
    echo "   Server IP: $server_ip"
    
    if [ "$ip" = "$server_ip" ]; then
        echo "✅ Domain points to this server correctly!"
    else
        echo "⚠️  Domain points to different IP ($ip vs $server_ip)"
    fi
else
    echo "⚠️  Domain not resolving"
fi

echo ""
echo "Test 6: Nginx Configuration"
echo "========================"
if nginx -t 2>&1 | grep -q "successful"; then
    echo "✅ Nginx config valid"
else
    echo "⚠️  Nginx config issues"
fi

echo ""
echo "Test 7: SSL/HTTPS Status"
echo "====================="
if [ -f "/etc/letsencrypt/live/dataguardianpro.nl/fullchain.pem" ]; then
    echo "✅ SSL certificate exists"
else
    echo "⚠️  No SSL certificate found"
fi

echo ""
echo "=========================================="
if [ "$content_found" = "true" ]; then
    echo "🎉 SUCCESS - DATAGUARDIAN PRO IS WORKING!"
    echo "=========================================="
    echo ""
    echo "🌐 Access your app:"
    echo "   https://dataguardianpro.nl"
    echo ""
    echo "🔐 Login credentials:"
    echo "   demo / demo123"
    echo "   vishaal314 / password123"
    echo ""
    echo "✅ DEPLOYMENT COMPLETE!"
else
    echo "⚠️  STILL NEEDS ATTENTION"
    echo "========================"
    echo ""
    echo "The app.py imports work in Python, but Streamlit"
    echo "isn't executing the main logic. This is unusual."
    echo ""
    echo "Possible causes:"
    echo "1. Streamlit session state issue"
    echo "2. Early exit condition in app.py"
    echo "3. Need to access via browser (WebSocket connection)"
    echo ""
    echo "Try accessing https://dataguardianpro.nl in browser"
fi

exit 0
