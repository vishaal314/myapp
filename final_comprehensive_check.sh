#!/bin/bash
# FINAL COMPREHENSIVE CHECK - Check everything after WebSocket fix

echo "🔍 FINAL COMPREHENSIVE CHECK"
echo "==========================="
echo ""

echo "📊 STEP 1: SERVICE STATUS"
echo "====================="
systemctl is-active nginx && echo "✅ Nginx: RUNNING" || echo "❌ Nginx: STOPPED"
systemctl is-active dataguardian && echo "✅ DataGuardian: RUNNING" || echo "❌ DataGuardian: STOPPED"
systemctl is-active redis-server && echo "✅ Redis: RUNNING" || echo "❌ Redis: STOPPED"

echo ""
echo "📄 STEP 2: LATEST DATAGUARDIAN LOGS (LAST 30 LINES)"
echo "=============================================="
journalctl -u dataguardian -n 30 --no-pager

echo ""
echo "🔍 STEP 3: CHECK FOR INITIALIZATION MESSAGES"
echo "======================================="
echo "Recent initialization patterns:"
journalctl -u dataguardian --since "5 minutes ago" --no-pager | grep -E "Performance|translation|System monitoring|DataGuardian" | tail -10 || echo "No initialization messages found"

echo ""
echo "🌐 STEP 4: TEST HTTP RESPONSE"
echo "========================="
echo "HTTP Status Code:"
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:5000

echo ""
echo "Response content (first 100 chars):"
curl -s http://localhost:5000 | head -c 100

echo ""
echo ""
echo "Search for 'DataGuardian':"
curl -s http://localhost:5000 | grep -i "dataguardian" | head -5 || echo "❌ NOT FOUND"

echo ""
echo "Search for page title:"
curl -s http://localhost:5000 | grep -i "<title>" | head -3

echo ""
echo "🔍 STEP 5: CHECK NGINX CONFIGURATION"
echo "==============================="
echo "Current nginx config for dataguardianpro.nl:"
grep -A 5 "location /" /etc/nginx/sites-available/dataguardianpro.nl | head -10

echo ""
echo "WebSocket upgrade configuration:"
grep -i "upgrade" /etc/nginx/sites-available/dataguardianpro.nl | head -5

echo ""
echo "🔍 STEP 6: CHECK PYTHON PROCESS"
echo "============================="
echo "DataGuardian Python processes:"
ps aux | grep "[p]ython.*streamlit.*app.py"

echo ""
echo "🔍 STEP 7: CHECK PORT 5000"
echo "======================"
echo "What's listening on port 5000:"
netstat -tlnp | grep ":5000"

echo ""
echo "🔍 STEP 8: TEST DIRECT STREAMLIT (BYPASS NGINX)"
echo "==========================================="
echo "Testing http://localhost:5000 directly:"
curl -s --max-time 5 http://127.0.0.1:5000 | grep -E "<title>|DataGuardian" | head -5 || echo "No DataGuardian content found"

echo ""
echo "🔍 STEP 9: CHECK APP.PY FILE"
echo "========================"
cd /opt/dataguardian
echo "App.py exists:"
ls -lh app.py 2>&1 | head -1
echo ""
echo "App.py first import line:"
head -100 app.py | grep "import streamlit" | head -1
echo ""
echo "App.py DataGuardian references:"
grep -c "DataGuardian" app.py

echo ""
echo "🔍 STEP 10: CHECK STREAMLIT CACHE"
echo "=============================="
echo "Streamlit cache directory:"
ls -la ~/.streamlit/cache 2>&1 || echo "No cache directory"

echo ""
echo "✅ COMPREHENSIVE CHECK COMPLETE!"
echo "=============================="
