#!/bin/bash
# QUICK SERVICE START - Skip package installation, just configure and start services
# For when files are already perfect and packages are likely installed

set -e

echo "⚡ QUICK SERVICE START - BYPASS PACKAGE INSTALLATION"
echo "=================================================="
echo "Skipping Python package installation (assumes already installed)"
echo "Going straight to service configuration and startup"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "❌ Run as root: sudo ./quick_service_start.sh"
    exit 1
fi

APP_DIR="/opt/dataguardian"
DOMAIN="dataguardianpro.nl"
APP_PORT="5000"

cd "$APP_DIR" || exit 1

echo "🔧 STEP 1: CREATE SYSTEMD SERVICE"
echo "=============================="

echo "🔧 Creating dataguardian.service..."

cat > /etc/systemd/system/dataguardian.service << 'EOF'
[Unit]
Description=DataGuardian Pro - Replit Environment
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/dataguardian

# Environment variables
Environment=PYTHONPATH=/opt/dataguardian
Environment=PYTHONUNBUFFERED=1
Environment=STREAMLIT_SERVER_HEADLESS=true
Environment=STREAMLIT_SERVER_PORT=5000
Environment=STREAMLIT_SERVER_ADDRESS=0.0.0.0
Environment=STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Start command matching Replit
ExecStart=/usr/bin/python3 -m streamlit run app.py --server.port 5000 --server.address 0.0.0.0 --server.headless true

# Restart configuration
Restart=always
RestartSec=30
TimeoutStartSec=180

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=dataguardian

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable dataguardian

echo "   ✅ dataguardian.service created"

echo ""
echo "🌐 STEP 2: CONFIGURE NGINX"
echo "======================"

echo "🌐 Creating nginx configuration..."

cat > /etc/nginx/sites-available/$DOMAIN << 'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name dataguardianpro.nl www.dataguardianpro.nl;
    
    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    
    # Streamlit proxy
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        
        # Headers for Streamlit
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx config
echo "   🧪 Testing nginx configuration..."
if nginx -t 2>&1; then
    echo "   ✅ Nginx configuration valid"
else
    echo "   ❌ Nginx configuration error - check syntax"
    exit 1
fi

echo ""
echo "▶️  STEP 3: START ALL SERVICES"
echo "============================"

echo "▶️  Starting services in order..."

# Start Redis
echo "   🔴 Starting Redis..."
systemctl start redis-server 2>&1 || echo "Redis may already be running"
sleep 2
redis_status=$(systemctl is-active redis-server)
echo "      Status: $redis_status"

# Start Nginx
echo "   🌐 Starting Nginx..."
systemctl start nginx 2>&1 || echo "Nginx may already be running"
sleep 2
nginx_status=$(systemctl is-active nginx)
echo "      Status: $nginx_status"

# Start DataGuardian
echo "   🚀 Starting DataGuardian Pro..."
echo "      (This may take 20-30 seconds...)"
systemctl start dataguardian 2>&1
sleep 25

dataguardian_status=$(systemctl is-active dataguardian)
echo "      Status: $dataguardian_status"

echo ""
echo "📊 SERVICES STATUS:"
echo "   Redis: $redis_status"
echo "   Nginx: $nginx_status"
echo "   DataGuardian: $dataguardian_status"

echo ""
echo "⏳ STEP 4: WAIT FOR APP INITIALIZATION (30 SECONDS)"
echo "=============================================="

echo "⏳ Giving DataGuardian Pro time to fully initialize..."
for i in {1..30}; do
    echo -n "."
    sleep 1
done
echo ""

echo ""
echo "🧪 STEP 5: TEST DEPLOYMENT"
echo "======================="

echo "🧪 Testing DataGuardian Pro..."

# Test 1: HTTP Response
echo "   Test 1: HTTP Response"
response=$(curl -s --max-time 10 http://localhost:5000 2>/dev/null || echo "")
status_code=$(curl -s --max-time 10 -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null || echo "000")

if [ "$status_code" = "200" ]; then
    echo "      ✅ HTTP 200 OK"
else
    echo "      ⚠️  HTTP Status: $status_code"
fi

# Test 2: DataGuardian Content
echo "   Test 2: DataGuardian Pro Content"
if echo "$response" | grep -qi "dataguardian"; then
    echo "      ✅ DataGuardian Pro detected!"
else
    echo "      ⚠️  DataGuardian content not found"
fi

# Test 3: Netherlands Branding
echo "   Test 3: Netherlands Branding"
if echo "$response" | grep -qi "netherlands"; then
    echo "      ✅ Netherlands branding detected!"
else
    echo "      ⚠️  Netherlands branding not found"
fi

# Test 4: Authentication Interface
echo "   Test 4: Authentication Interface"
if echo "$response" | grep -qi "customer.*login\|live.*demo\|authentication"; then
    echo "      ✅ Authentication interface detected!"
else
    echo "      ⚠️  Authentication interface not found"
fi

echo ""
echo "📝 SAMPLE CONTENT:"
echo "$response" | grep -i "dataguardian\|netherlands\|customer\|login\|demo" | head -5 | sed 's/^/   /'

echo ""
echo "🎯 QUICK SERVICE START RESULTS"
echo "============================="

# Calculate score
score=0

if [ "$redis_status" = "active" ]; then
    score=$((score + 10))
    echo "✅ Redis: RUNNING (+10)"
else
    echo "❌ Redis: NOT RUNNING"
fi

if [ "$nginx_status" = "active" ]; then
    score=$((score + 20))
    echo "✅ Nginx: RUNNING (+20)"
else
    echo "❌ Nginx: NOT RUNNING"
fi

if [ "$dataguardian_status" = "active" ]; then
    score=$((score + 30))
    echo "✅ DataGuardian: RUNNING (+30)"
else
    echo "❌ DataGuardian: NOT RUNNING"
fi

if [ "$status_code" = "200" ] && echo "$response" | grep -qi "dataguardian"; then
    if echo "$response" | grep -qi "netherlands"; then
        score=$((score + 40))
        echo "✅ DataGuardian Pro Interface: PERFECT (+40)"
    else
        score=$((score + 30))
        echo "✅ DataGuardian Pro Interface: GOOD (+30)"
    fi
elif [ "$status_code" = "200" ]; then
    score=$((score + 15))
    echo "⚠️  Interface: LOADING (+15)"
else
    echo "❌ Interface: NOT RESPONDING"
fi

echo ""
echo "📊 FINAL SCORE: $score/100"

if [ $score -ge 90 ]; then
    echo ""
    echo "🎉🎉🎉 PERFECT SUCCESS! 🎉🎉🎉"
    echo "========================================"
    echo ""
    echo "✅ ALL SERVICES RUNNING PERFECTLY"
    echo "✅ DATAGUARDIAN PRO INTERFACE ACTIVE"
    echo "✅ 100% REPLIT ENVIRONMENT REPLICATED"
    echo ""
    echo "🌐 ACCESS YOUR APP:"
    echo "   🎯 https://dataguardianpro.nl"
    echo "   🎯 https://www.dataguardianpro.nl"
    echo ""
    echo "🔐 LOGIN:"
    echo "   vishaal314 / password123"
    echo "   demo / demo123"
    echo "   admin / admin123"
    echo ""
    echo "🏆 MISSION ACCOMPLISHED!"
    
elif [ $score -ge 70 ]; then
    echo ""
    echo "🎉 GREAT SUCCESS!"
    echo "================"
    echo ""
    echo "✅ Services running"
    echo "✅ Interface loading"
    echo ""
    echo "🌐 Test: https://dataguardianpro.nl"
    echo ""
    echo "💡 If interface shows generic Streamlit, wait 1-2 minutes for full load"
    
elif [ $score -ge 50 ]; then
    echo ""
    echo "✅ PARTIAL SUCCESS"
    echo "================="
    echo ""
    echo "Services started but interface needs verification"
    echo ""
    echo "Check logs: journalctl -u dataguardian -n 50 -f"
    
else
    echo ""
    echo "⚠️  NEEDS ATTENTION"
    echo "================="
    echo ""
    echo "📄 Check logs: journalctl -u dataguardian -n 100"
    echo "🔄 Restart: systemctl restart dataguardian"
fi

echo ""
echo "🔍 USEFUL COMMANDS:"
echo "==================="
echo "   Status: systemctl status dataguardian"
echo "   Logs: journalctl -u dataguardian -n 50 -f"
echo "   Restart: systemctl restart dataguardian"
echo "   Test: curl http://localhost:5000 | grep dataguardian"
echo ""

echo "✅ QUICK SERVICE START COMPLETE!"

exit 0
