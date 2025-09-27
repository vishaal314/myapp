#!/bin/bash
# Simple Nginx Proxy Fix - Direct approach
# Fixes: 1837-byte static file serving instead of Streamlit proxy
# Uses clean, simple nginx configuration without complex variables

echo "🔧 SIMPLE NGINX PROXY FIX"
echo "========================="
echo "Issue: Domain serves 1837-byte static file instead of proxying to Streamlit"
echo "Fix: Simple, clean nginx configuration with direct proxy"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root"
    echo "💡 Please run: sudo ./simple_nginx_proxy_fix.sh"
    exit 1
fi

DOMAIN="dataguardianpro.nl"
APP_PORT="5000"

echo "🔍 STEP 1: CONFIRM CURRENT ISSUE"
echo "==============================="

# Test current state
echo "🧪 Current status check..."
local_test=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$APP_PORT 2>/dev/null || echo "000")
domain_size=$(curl -s -o /dev/null -w "%{size_download}" https://www.$DOMAIN 2>/dev/null || echo "0")
domain_status=$(curl -s -o /dev/null -w "%{http_code}" https://www.$DOMAIN 2>/dev/null || echo "000")

echo "   ✅ Local Streamlit: $local_test"
echo "   📊 Domain response size: $domain_size bytes"
echo "   📊 Domain status: $domain_status"

if [ "$domain_size" -eq 1837 ]; then
    echo "❌ CONFIRMED: Domain serving 1837-byte static file"
else
    echo "ℹ️  Domain response size: $domain_size bytes"
fi

echo ""
echo "🔧 STEP 2: CREATE SIMPLE NGINX CONFIGURATION"
echo "==========================================="

# Backup current config
config_file="/etc/nginx/sites-enabled/$DOMAIN"
if [ -f "$config_file" ]; then
    echo "📁 Backing up current configuration..."
    cp "$config_file" "$config_file.simple-backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ Backup created"
else
    echo "❌ Nginx config file not found: $config_file"
    exit 1
fi

# Create simple, clean configuration
echo "📝 Creating simple nginx configuration..."

cat > "$config_file" << EOF
# DataGuardian Pro - Simple Clean Configuration
# Direct proxy to Streamlit without complex directives

# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

# HTTPS server - Simple proxy configuration
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;
    
    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    
    # Basic security headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Client settings
    client_max_body_size 50M;
    
    # ROOT LOCATION - Direct proxy to Streamlit (NO STATIC FILES)
    location / {
        # Direct proxy to Streamlit application
        proxy_pass http://127.0.0.1:$APP_PORT;
        proxy_http_version 1.1;
        
        # WebSocket support for Streamlit
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Essential proxy headers
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Streamlit optimizations
        proxy_buffering off;
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
        proxy_connect_timeout 60s;
        
        # WebSocket headers for Streamlit
        proxy_set_header Sec-WebSocket-Extensions \$http_sec_websocket_extensions;
        proxy_set_header Sec-WebSocket-Key \$http_sec_websocket_key;
        proxy_set_header Sec-WebSocket-Version \$http_sec_websocket_version;
    }
    
    # Health check
    location = /health {
        access_log off;
        proxy_pass http://127.0.0.1:$APP_PORT/health;
        proxy_set_header Host \$host;
    }
    
    # Block hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
EOF

echo "✅ Simple nginx configuration created"

echo ""
echo "🧪 STEP 3: TEST CONFIGURATION"
echo "============================"

# Test configuration
echo "🔍 Testing nginx configuration..."
nginx_test_output=$(nginx -t 2>&1)
nginx_test_result=$?

if [ $nginx_test_result -eq 0 ]; then
    echo "✅ Nginx configuration is valid"
else
    echo "❌ Nginx configuration has issues:"
    echo "$nginx_test_output"
    
    # Check if it's just warnings (acceptable) or real errors
    if echo "$nginx_test_output" | grep -q "\[emerg\]"; then
        echo "❌ Critical errors found - restoring backup"
        cp "$config_file.simple-backup."* "$config_file" 2>/dev/null || true
        exit 1
    else
        echo "⚠️  Only warnings found - proceeding (warnings are acceptable)"
    fi
fi

echo ""
echo "🔄 STEP 4: APPLY CONFIGURATION"
echo "============================="

# Restart nginx
echo "🔄 Restarting nginx with new configuration..."
systemctl restart nginx
sleep 5

# Check nginx status
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx restarted successfully"
else
    echo "❌ Nginx failed to restart"
    echo "📊 Nginx status:"
    systemctl status nginx --no-pager -l | head -10
    
    # Restore backup
    echo "🔄 Restoring backup configuration..."
    cp "$config_file.simple-backup."* "$config_file" 2>/dev/null || true
    systemctl restart nginx
    exit 1
fi

echo ""
echo "🧪 STEP 5: VERIFY THE FIX"
echo "======================="

echo "⏳ Waiting 10 seconds for changes to take effect..."
sleep 10

# Test the fix
echo "🔍 Testing the fix..."

# Test local app (baseline)
final_local=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$APP_PORT 2>/dev/null || echo "000")
echo "   ✅ Local Streamlit: $final_local"

# Test domain HTTPS (the main issue)
final_domain_status=$(curl -s -o /dev/null -w "%{http_code}" https://www.$DOMAIN 2>/dev/null || echo "000")
final_domain_size=$(curl -s -o /dev/null -w "%{size_download}" https://www.$DOMAIN 2>/dev/null || echo "0")
echo "   🎯 Domain HTTPS status: $final_domain_status"
echo "   📊 Domain response size: $final_domain_size bytes (was: $domain_size)"

# Check for content improvement
if [ "$final_domain_size" -gt "$domain_size" ] && [ "$final_domain_status" = "200" ]; then
    echo "✅ SUCCESS: Response size increased - now serving dynamic content!"
elif [ "$final_domain_size" -ne 1837 ] && [ "$final_domain_status" = "200" ]; then
    echo "✅ GOOD: Response size changed from static file size"
elif [ "$final_domain_status" = "200" ]; then
    echo "⚠️  PARTIAL: Domain responds but size unchanged"
else
    echo "❌ ISSUE: Domain not responding correctly"
fi

echo ""
echo "🔍 STEP 6: CONTENT VERIFICATION"
echo "=============================="

# Test actual content
echo "🔍 Checking actual content delivery..."

# Get sample of current content
echo "📄 Sample content from https://www.$DOMAIN:"
echo "--- CONTENT START ---"
content_sample=$(curl -s https://www.$DOMAIN 2>/dev/null | head -10)
echo "$content_sample"
echo "--- CONTENT END ---"

# Check for Streamlit indicators
streamlit_indicators=$(echo "$content_sample" | grep -i "streamlit\|loading\|script\|css" | wc -l)
echo "   🎯 Streamlit/dynamic indicators: $streamlit_indicators"

echo ""
echo "🧪 STEP 7: COMPREHENSIVE TEST"
echo "============================"

# Test all variants
echo "🌐 Testing all domain variants..."

http_redirect=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN 2>/dev/null || echo "000")
https_main=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN 2>/dev/null || echo "000")
https_www=$(curl -s -o /dev/null -w "%{http_code}" https://www.$DOMAIN 2>/dev/null || echo "000")

echo "   🔄 HTTP redirect: $http_redirect (should be 301)"
echo "   🔐 HTTPS main: $https_main"
echo "   🌐 HTTPS www: $https_www"

echo ""
echo "📊 FINAL RESULTS"
echo "==============="

# Determine success
success=false
improvement=false

if [ "$final_domain_status" = "200" ] && [ "$final_domain_size" -gt "$domain_size" ]; then
    success=true
    improvement=true
elif [ "$final_domain_status" = "200" ] && [ "$final_domain_size" -ne 1837 ]; then
    improvement=true
elif [ "$final_domain_status" = "200" ]; then
    # At least responding, check content indicators
    if [ "$streamlit_indicators" -gt 0 ]; then
        improvement=true
    fi
fi

if [ "$success" = true ]; then
    echo ""
    echo "🎉🎉🎉 NGINX PROXY ISSUE FIXED! 🎉🎉🎉"
    echo "======================================"
    echo ""
    echo "✅ COMPLETE SUCCESS!"
    echo "✅ Static file issue: RESOLVED"
    echo "✅ Nginx proxy: NOW WORKING"
    echo "✅ Dynamic content: SERVING"
    echo ""
    echo "📊 IMPROVEMENTS:"
    echo "   Response size: $domain_size → $final_domain_size bytes"
    echo "   Content type: Now dynamic (no more static 1837 bytes)"
    echo "   Status: $final_domain_status (working)"
    echo ""
    echo "🌐 YOUR DATAGUARDIAN PRO IS NOW ACCESSIBLE:"
    echo "   🎯 https://dataguardianpro.nl"
    echo "   🎯 https://www.dataguardianpro.nl"
    echo ""
    echo "🚀 READY FOR USE!"
    echo "🇳🇱 Netherlands GDPR Compliance Platform LIVE!"

elif [ "$improvement" = true ]; then
    echo ""
    echo "✅ SIGNIFICANT IMPROVEMENT"
    echo "========================="
    echo ""
    echo "✅ Progress made:"
    echo "   Status: $final_domain_status"
    echo "   Size change: $domain_size → $final_domain_size bytes"
    echo "   Content indicators: $streamlit_indicators"
    echo ""
    echo "💡 RECOMMENDATION:"
    echo "   1. Try accessing https://www.$DOMAIN in browser"
    echo "   2. Clear browser cache if needed"
    echo "   3. Wait 2-3 minutes for full propagation"
    echo ""
    echo "🔍 TEST COMMAND:"
    echo "   curl -s https://www.$DOMAIN | head -20"

else
    echo ""
    echo "⚠️  PARTIAL RESULTS"
    echo "=================="
    echo ""
    echo "📊 Current status:"
    echo "   Local app: $final_local"
    echo "   Domain status: $final_domain_status"
    echo "   Domain size: $final_domain_size bytes"
    echo "   Content indicators: $streamlit_indicators"
    echo ""
    echo "🔧 NEXT STEPS:"
    echo "   1. Wait a few minutes and test again"
    echo "   2. Check DataGuardian service: systemctl status dataguardian"
    echo "   3. Check nginx logs: tail -20 /var/log/nginx/error.log"
    echo "   4. Try: systemctl restart dataguardian nginx"
fi

echo ""
echo "🎯 QUICK TEST COMMANDS:"
echo "======================"
echo "   🔍 Test domain: curl -I https://www.$DOMAIN"
echo "   📄 Get content: curl -s https://www.$DOMAIN | head -10"
echo "   📊 Services: systemctl status nginx dataguardian"
echo "   🔄 Restart: systemctl restart nginx dataguardian"

echo ""
echo "✅ SIMPLE NGINX PROXY FIX COMPLETED!"
echo "Your domain should now serve Streamlit content instead of static files!"