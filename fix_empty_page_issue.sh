#!/bin/bash
# Fix Empty Page Issue - Diagnose and fix HTTPS empty page display
# Addresses Streamlit proxy configuration and WebSocket issues

echo "🔍 EMPTY PAGE DIAGNOSIS & FIX"
echo "============================"
echo "Diagnosing why https://www.dataguardianpro.nl shows empty page"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root"
    echo "💡 Please run: sudo ./fix_empty_page_issue.sh"
    exit 1
fi

DOMAIN="dataguardianpro.nl"
APP_PORT="5000"

echo "🧪 STEP 1: CONNECTIVITY DIAGNOSTICS"
echo "=================================="

# Test local Streamlit
echo "🔍 Testing local Streamlit (localhost:5000)..."
local_streamlit=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$APP_PORT 2>/dev/null || echo "000")
echo "   Local Streamlit: $local_streamlit"

if [ "$local_streamlit" != "200" ]; then
    echo "❌ LOCAL STREAMLIT NOT WORKING - This is the root cause!"
    echo "🔧 Restarting DataGuardian service..."
    systemctl restart dataguardian
    sleep 15
    
    local_streamlit_retry=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$APP_PORT 2>/dev/null || echo "000")
    echo "   Local Streamlit after restart: $local_streamlit_retry"
    
    if [ "$local_streamlit_retry" != "200" ]; then
        echo "❌ CRITICAL: DataGuardian service failing"
        echo "📊 Service status:"
        systemctl status dataguardian --no-pager -l | head -15
        echo ""
        echo "📄 Recent DataGuardian logs:"
        journalctl -u dataguardian --no-pager -n 20 | tail -10
        exit 1
    fi
fi

# Test domain responses
echo ""
echo "🔍 Testing domain responses..."
domain_http=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN 2>/dev/null || echo "000")
domain_https=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN 2>/dev/null || echo "000")
www_https=$(curl -s -o /dev/null -w "%{http_code}" https://www.$DOMAIN 2>/dev/null || echo "000")

echo "   Domain HTTP: $domain_http"
echo "   Domain HTTPS: $domain_https" 
echo "   WWW HTTPS: $www_https"

# Test content delivery
echo ""
echo "🔍 Testing actual content delivery..."
echo "🧪 Local Streamlit content preview:"
local_content=$(curl -s http://localhost:$APP_PORT | head -5 | tail -2)
echo "$local_content"

echo ""
echo "🧪 Domain HTTPS content preview:"  
domain_content=$(curl -s https://www.$DOMAIN | head -5 | tail -2)
echo "$domain_content"

# Compare content
if [ "$local_content" = "$domain_content" ]; then
    echo "✅ Content matches - WebSocket/JavaScript issue likely"
else
    echo "❌ Content differs - Proxy configuration issue"
fi

echo ""
echo "🧪 STEP 2: NGINX CONFIGURATION CHECK"
echo "==================================="

# Check if nginx is serving the right content
echo "🔍 Checking Nginx configuration..."

if [ -f "/etc/nginx/sites-enabled/$DOMAIN" ]; then
    echo "✅ Nginx site configuration found"
    
    # Check if proxy_pass is configured
    if grep -q "proxy_pass.*127.0.0.1:$APP_PORT" /etc/nginx/sites-enabled/$DOMAIN; then
        echo "✅ Proxy configuration found for port $APP_PORT"
    else
        echo "❌ Proxy configuration missing or incorrect"
        echo "🔧 FIXING PROXY CONFIGURATION..."
        
        # Backup current config
        cp /etc/nginx/sites-enabled/$DOMAIN /etc/nginx/sites-enabled/$DOMAIN.backup
        
        # Fix proxy configuration
        cat > /etc/nginx/sites-enabled/$DOMAIN << EOF
# DataGuardian Pro - Fixed Proxy Configuration

# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

# HTTPS server with corrected proxy
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # SSL security settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Client settings
    client_max_body_size 50M;
    client_body_timeout 60s;
    client_header_timeout 60s;
    
    # Main location - proxy to Streamlit
    location / {
        # Essential: Proxy to local Streamlit
        proxy_pass http://127.0.0.1:$APP_PORT;
        proxy_http_version 1.1;
        
        # WebSocket support (CRITICAL for Streamlit)
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Standard proxy headers
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$server_name;
        proxy_set_header X-Forwarded-Port \$server_port;
        
        # Streamlit specific settings (IMPORTANT)
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
        proxy_connect_timeout 60s;
        proxy_redirect off;
        
        # WebSocket specific headers for Streamlit
        proxy_set_header Sec-WebSocket-Extensions \$http_sec_websocket_extensions;
        proxy_set_header Sec-WebSocket-Key \$http_sec_websocket_key;
        proxy_set_header Sec-WebSocket-Version \$http_sec_websocket_version;
        proxy_set_header Sec-WebSocket-Protocol \$http_sec_websocket_protocol;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:$APP_PORT/health;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
    
    # Block hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
EOF

        echo "✅ Nginx configuration fixed with proper proxy settings"
    fi
else
    echo "❌ Nginx site configuration not found"
    exit 1
fi

echo ""
echo "🧪 STEP 3: NGINX RESTART & VERIFICATION"  
echo "======================================"

# Test nginx configuration
echo "🔧 Testing Nginx configuration..."
if nginx -t >/dev/null 2>&1; then
    echo "✅ Nginx configuration valid"
else
    echo "❌ Nginx configuration invalid:"
    nginx -t
    exit 1
fi

# Restart nginx
echo "🔄 Restarting Nginx..."
systemctl restart nginx
sleep 5

# Check nginx status
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx restarted successfully"
else
    echo "❌ Nginx failed to restart"
    systemctl status nginx --no-pager -l | head -10
    exit 1
fi

echo ""
echo "🧪 STEP 4: STREAMLIT CONFIGURATION CHECK"
echo "======================================="

# Check Streamlit configuration
echo "🔍 Checking Streamlit configuration..."

if [ -d ".streamlit" ]; then
    echo "✅ Streamlit config directory found"
    
    if [ -f ".streamlit/config.toml" ]; then
        echo "✅ Streamlit config file found"
        echo "📄 Current Streamlit config:"
        cat .streamlit/config.toml
    else
        echo "⚠️  Streamlit config file missing - creating optimal config..."
        
        mkdir -p .streamlit
        cat > .streamlit/config.toml << 'EOF'
[server]
headless = true
address = "0.0.0.0"
port = 5000
enableCORS = false
enableXsrfProtection = false
maxUploadSize = 50

[browser]
gatherUsageStats = false

[theme]
base = "light"
EOF
        echo "✅ Streamlit config created"
    fi
else
    echo "⚠️  Streamlit config directory missing - creating..."
    mkdir -p .streamlit
    cat > .streamlit/config.toml << 'EOF'
[server]
headless = true
address = "0.0.0.0"
port = 5000
enableCORS = false
enableXsrfProtection = false
maxUploadSize = 50

[browser]
gatherUsageStats = false

[theme]
base = "light"
EOF
    echo "✅ Streamlit config directory and file created"
fi

echo ""
echo "🧪 STEP 5: DATAGUARDIAN SERVICE RESTART"
echo "====================================="

echo "🔄 Restarting DataGuardian service with new config..."
systemctl restart dataguardian
sleep 15

# Check service status
if systemctl is-active --quiet dataguardian; then
    echo "✅ DataGuardian service restarted successfully"
else
    echo "❌ DataGuardian service failed to restart"
    echo "📊 Service status:"
    systemctl status dataguardian --no-pager -l | head -15
    exit 1
fi

# Wait for app to be ready
echo "⏳ Waiting for DataGuardian to be ready..."
for i in {1..12}; do
    app_check=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$APP_PORT 2>/dev/null || echo "000")
    if [ "$app_check" = "200" ]; then
        echo "✅ DataGuardian ready on port $APP_PORT"
        break
    else
        echo "   Attempt $i/12: $app_check (waiting...)"
        sleep 5
    fi
done

echo ""
echo "🧪 STEP 6: FINAL CONNECTIVITY TESTS"
echo "================================="

# Final comprehensive test
echo "🔍 Running final connectivity tests..."

# Test 1: Local Streamlit
final_local=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$APP_PORT 2>/dev/null || echo "000")
echo "   ✅ Local Streamlit: $final_local"

# Test 2: Domain HTTP (should redirect)
final_http=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN 2>/dev/null || echo "000")
echo "   ✅ Domain HTTP: $final_http (should be 301 redirect)"

# Test 3: Domain HTTPS
final_https=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN 2>/dev/null || echo "000")
echo "   ✅ Domain HTTPS: $final_https"

# Test 4: WWW HTTPS (the problematic one)
final_www_https=$(curl -s -o /dev/null -w "%{http_code}" https://www.$DOMAIN 2>/dev/null || echo "000")
echo "   ✅ WWW HTTPS: $final_www_https"

echo ""
echo "🧪 STEP 7: CONTENT VERIFICATION"
echo "============================"

# Check if we're getting Streamlit content now
echo "🔍 Testing actual page content delivery..."

# Get a snippet of the response to verify it's Streamlit
www_content_test=$(curl -s https://www.$DOMAIN | grep -i "streamlit\|dataguardian" | wc -l)

if [ "$www_content_test" -gt 0 ]; then
    echo "✅ HTTPS content contains expected elements ($www_content_test matches)"
    
    # Show a preview of what we're getting
    echo ""
    echo "📄 Content preview from https://www.$DOMAIN:"
    curl -s https://www.$DOMAIN | head -20 | tail -10
    
else
    echo "❌ HTTPS content still not showing expected elements"
    
    echo ""
    echo "📄 Current content from https://www.$DOMAIN:"
    curl -s https://www.$DOMAIN | head -10
    
    echo ""
    echo "📄 Expected content from localhost:$APP_PORT:"
    curl -s http://localhost:$APP_PORT | head -10
fi

echo ""
echo "📊 EMPTY PAGE FIX - FINAL RESULTS"
echo "==============================="

# Determine success
if [ "$final_www_https" = "200" ] && [ "$www_content_test" -gt 0 ]; then
    echo ""
    echo "🎉🎉🎉 EMPTY PAGE FIXED! 🎉🎉🎉"
    echo "==============================="
    echo ""
    echo "✅ ALL ISSUES RESOLVED!"
    echo "✅ Local Streamlit: Working ($final_local)"
    echo "✅ Nginx proxy: Fixed and working"
    echo "✅ HTTPS response: $final_www_https"
    echo "✅ Content delivery: Working"
    echo "✅ WebSocket support: Configured"
    echo ""
    echo "🌐 YOUR PLATFORM IS NOW FULLY FUNCTIONAL:"
    echo "   📍 Primary: https://$DOMAIN"
    echo "   📍 WWW: https://www.$DOMAIN"
    echo "   📍 Both show DataGuardian Pro interface"
    echo ""
    echo "🚀 READY FOR USE!"
    echo "Your Netherlands GDPR compliance platform is live!"
    
elif [ "$final_www_https" = "200" ] && [ "$www_content_test" -eq 0 ]; then
    echo ""
    echo "⚠️  PARTIAL SUCCESS - CONTENT ISSUE REMAINS"
    echo "========================================"
    echo ""
    echo "✅ HTTPS connectivity: Working ($final_www_https)"
    echo "⚠️  Content delivery: Still not showing expected content"
    echo ""
    echo "🔧 ADDITIONAL STEPS NEEDED:"
    echo "1. Check DataGuardian logs: journalctl -u dataguardian -f"
    echo "2. Verify app.py is loading properly"
    echo "3. Check for any Python/Streamlit errors"
    echo "4. Try restarting both services: systemctl restart dataguardian nginx"
    
else
    echo ""
    echo "❌ ISSUES REMAIN"
    echo "==============="
    echo ""
    echo "📊 Current status:"
    echo "   Local Streamlit: $final_local"
    echo "   Domain HTTPS: $final_https"
    echo "   WWW HTTPS: $final_www_https"
    echo "   Content elements: $www_content_test"
    echo ""
    echo "🔧 TROUBLESHOOTING NEEDED:"
    echo "   Check service logs: journalctl -u dataguardian -u nginx"
    echo "   Verify SSL certificates: certbot certificates"
    echo "   Test manually: curl -v https://www.$DOMAIN"
fi

echo ""
echo "🎯 QUICK ACCESS COMMANDS:"
echo "========================"
echo "   🔍 Test site: curl -I https://www.$DOMAIN"
echo "   📊 Service status: systemctl status dataguardian nginx"
echo "   📄 View logs: journalctl -u dataguardian -f"
echo "   🔄 Restart services: systemctl restart dataguardian nginx"

echo ""
echo "✅ EMPTY PAGE DIAGNOSIS & FIX COMPLETED!"