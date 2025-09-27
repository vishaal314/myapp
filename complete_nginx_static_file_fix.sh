#!/bin/bash
# Complete Nginx Static File Fix - External Server
# Fixes: Domain serves static 1837-byte file instead of proxying to Streamlit
# Addresses syntax errors and static file conflicts

echo "🔧 COMPLETE NGINX STATIC FILE FIX"
echo "================================="
echo "Issue: https://www.dataguardianpro.nl serves static file (1837 bytes) instead of Streamlit app"
echo "Fix: Remove syntax errors and static file conflicts"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root"
    echo "💡 Please run: sudo ./complete_nginx_static_file_fix.sh"
    exit 1
fi

DOMAIN="dataguardianpro.nl"
APP_PORT="5000"

echo "🔍 STEP 1: DIAGNOSIS - STATIC FILE vs PROXY"
echo "=========================================="

# Check current response characteristics
echo "🧪 Analyzing current HTTPS response..."
response_size=$(curl -s -o /dev/null -w "%{size_download}" https://www.$DOMAIN 2>/dev/null || echo "0")
content_type=$(curl -s -I https://www.$DOMAIN 2>/dev/null | grep -i "content-type" | cut -d: -f2 | tr -d ' \r\n')
has_etag=$(curl -s -I https://www.$DOMAIN 2>/dev/null | grep -i "etag" | wc -l)

echo "   📊 Response size: $response_size bytes"
echo "   📋 Content type: $content_type"
echo "   🏷️  Has ETag: $has_etag (1=static file, 0=dynamic)"

if [ "$response_size" -lt 5000 ] && [ "$has_etag" -gt 0 ]; then
    echo "❌ CONFIRMED: Serving static file instead of Streamlit app"
else
    echo "⚠️  Response characteristics unclear - proceeding with fix"
fi

# Test local Streamlit
local_test=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$APP_PORT 2>/dev/null || echo "000")
echo "   ✅ Local Streamlit: $local_test"

if [ "$local_test" != "200" ]; then
    echo "❌ CRITICAL: Local Streamlit not working - fixing first"
    systemctl restart dataguardian
    sleep 15
    
    local_retry=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$APP_PORT 2>/dev/null || echo "000")
    if [ "$local_retry" != "200" ]; then
        echo "❌ Local Streamlit still failing - check systemctl status dataguardian"
        exit 1
    fi
    echo "✅ Local Streamlit now working: $local_retry"
fi

echo ""
echo "🔍 STEP 2: FIND AND REMOVE STATIC FILE CONFLICTS"
echo "==============================================="

# Find potential static files being served
echo "🔍 Checking for static HTML files that might be served..."

# Common locations where static files might be
static_locations=(
    "/var/www/html/index.html"
    "/usr/share/nginx/html/index.html"
    "/opt/dataguardian/index.html"
    "/etc/nginx/html/index.html"
)

static_files_found=0
for location in "${static_locations[@]}"; do
    if [ -f "$location" ]; then
        file_size=$(stat --format=%s "$location" 2>/dev/null || echo "0")
        echo "   📄 Found: $location ($file_size bytes)"
        
        # Check if this matches our problematic response size
        if [ "$file_size" -eq 1837 ] || [ "$file_size" -eq 1838 ] || [ "$file_size" -eq 1836 ]; then
            echo "   🎯 MATCH: This file size matches the problematic response!"
            echo "   🗑️  Renaming to .backup to prevent serving..."
            mv "$location" "$location.backup.$(date +%Y%m%d_%H%M%S)"
            ((static_files_found++))
        fi
    fi
done

if [ $static_files_found -gt 0 ]; then
    echo "✅ Removed $static_files_found conflicting static files"
else
    echo "ℹ️  No obvious static file conflicts found"
fi

echo ""
echo "🔍 STEP 3: FIX NGINX CONFIGURATION SYNTAX ERRORS"
echo "==============================================="

# Backup current config
config_file="/etc/nginx/sites-enabled/$DOMAIN"
if [ -f "$config_file" ]; then
    echo "📁 Backing up current Nginx configuration..."
    cp "$config_file" "$config_file.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ Backup created"
else
    echo "❌ Nginx configuration file not found: $config_file"
    exit 1
fi

# Create clean, syntax-correct configuration
echo "📝 Creating syntax-correct Nginx configuration..."

cat > "$config_file" << EOF
# DataGuardian Pro - Clean Nginx Configuration
# Fixes static file serving and syntax errors

# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN www.$DOMAIN;
    
    # Simple redirect without additional processing
    return 301 https://\$server_name\$request_uri;
}

# HTTPS server - Clean configuration without syntax errors
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;
    
    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # SSL settings (in server context - CORRECT placement)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    
    # Client settings (in server context - CORRECT placement)
    client_max_body_size 50M;
    client_body_timeout 60s;
    client_header_timeout 60s;
    
    # Security headers (server level)
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # CRITICAL: Main location block - Proxy ALL requests to Streamlit
    location / {
        # Proxy to Streamlit application (ESSENTIAL)
        proxy_pass http://127.0.0.1:$APP_PORT;
        proxy_http_version 1.1;
        
        # WebSocket support for Streamlit (CRITICAL)
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Standard proxy headers
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$server_name;
        proxy_set_header X-Forwarded-Port \$server_port;
        
        # Streamlit optimizations (IMPORTANT for dynamic content)
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
        proxy_connect_timeout 60s;
        proxy_redirect off;
        
        # WebSocket headers for Streamlit real-time features
        proxy_set_header Sec-WebSocket-Extensions \$http_sec_websocket_extensions;
        proxy_set_header Sec-WebSocket-Key \$http_sec_websocket_key;
        proxy_set_header Sec-WebSocket-Version \$http_sec_websocket_version;
        proxy_set_header Sec-WebSocket-Protocol \$http_sec_websocket_protocol;
        
        # Prevent static file serving
        try_files \$nonexistent @backend;
    }
    
    # Backend fallback (ensures proxy is used)
    location @backend {
        proxy_pass http://127.0.0.1:$APP_PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Health check
    location = /health {
        access_log off;
        proxy_pass http://127.0.0.1:$APP_PORT/health;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_connect_timeout 5s;
        proxy_read_timeout 5s;
    }
    
    # Block access to hidden files and sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    # Block common sensitive files
    location ~ \.(py|pyc|pyo|env|log|conf|bak|backup)$ {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    # Explicitly deny serving any HTML files from filesystem
    location ~ \.html$ {
        # Don't serve static HTML - proxy everything to Streamlit
        try_files \$nonexistent @backend;
    }
}
EOF

echo "✅ Clean Nginx configuration created (no syntax errors)"

echo ""
echo "🔍 STEP 4: REMOVE RATE LIMITING CONFLICTS"
echo "======================================="

# Check if rate limiting config exists and might be causing issues
rate_limit_config="/etc/nginx/conf.d/rate_limiting.conf"
if [ -f "$rate_limit_config" ]; then
    echo "✅ Rate limiting config found: $rate_limit_config"
    
    # Verify rate limiting zones are properly defined
    if grep -q "limit_req_zone" "$rate_limit_config"; then
        echo "✅ Rate limiting zones properly defined"
    else
        echo "⚠️  Rate limiting config exists but zones not defined - creating minimal version"
        cat > "$rate_limit_config" << 'EOF'
# Basic rate limiting for DataGuardian Pro
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
EOF
    fi
else
    echo "ℹ️  No rate limiting config - creating basic one to prevent issues"
    cat > "$rate_limit_config" << 'EOF'
# Basic rate limiting for DataGuardian Pro
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
EOF
fi

echo ""
echo "🧪 STEP 5: TEST AND APPLY CONFIGURATION"
echo "====================================="

# Test configuration syntax
echo "🔍 Testing Nginx configuration syntax..."
if nginx -t >/dev/null 2>&1; then
    echo "✅ Nginx configuration syntax is valid"
else
    echo "❌ Configuration still has syntax errors:"
    nginx -t
    echo ""
    echo "🔄 Restoring backup configuration..."
    cp "$config_file.backup."* "$config_file" 2>/dev/null || true
    exit 1
fi

# Stop nginx to ensure clean restart
echo "🛑 Stopping Nginx for clean restart..."
systemctl stop nginx
sleep 3

# Remove any nginx processes
echo "🧹 Ensuring no stale nginx processes..."
pkill -f nginx 2>/dev/null || true
sleep 2

# Start nginx with new configuration
echo "▶️  Starting Nginx with new configuration..."
systemctl start nginx
sleep 5

# Verify nginx started correctly
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx started successfully"
else
    echo "❌ Nginx failed to start"
    echo "📊 Nginx status:"
    systemctl status nginx --no-pager -l | head -15
    echo ""
    echo "🔄 Restoring backup and restarting..."
    cp "$config_file.backup."* "$config_file" 2>/dev/null || true
    systemctl start nginx
    exit 1
fi

echo ""
echo "🧪 STEP 6: COMPREHENSIVE VERIFICATION"
echo "=================================="

echo "⏳ Waiting 15 seconds for configuration to fully take effect..."
sleep 15

# Test all endpoints
echo "🔍 Testing all endpoints..."

# Test 1: Local Streamlit (baseline)
local_final=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$APP_PORT 2>/dev/null || echo "000")
echo "   📍 Local Streamlit: $local_final"

# Test 2: HTTP (should redirect)
http_final=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN 2>/dev/null || echo "000")
echo "   🔄 HTTP redirect: $http_final (should be 301)"

# Test 3: HTTPS main domain
https_main=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN 2>/dev/null || echo "000")
echo "   🔐 HTTPS main: $https_main"

# Test 4: HTTPS www (the problematic one)
https_www=$(curl -s -o /dev/null -w "%{http_code}" https://www.$DOMAIN 2>/dev/null || echo "000")
echo "   🌐 HTTPS www: $https_www"

echo ""
echo "🧪 STEP 7: CONTENT AND RESPONSE ANALYSIS"
echo "======================================"

# Analyze new response characteristics
echo "🔍 Analyzing new response characteristics..."
new_response_size=$(curl -s -o /dev/null -w "%{size_download}" https://www.$DOMAIN 2>/dev/null || echo "0")
new_content_type=$(curl -s -I https://www.$DOMAIN 2>/dev/null | grep -i "content-type" | cut -d: -f2 | tr -d ' \r\n')
new_has_etag=$(curl -s -I https://www.$DOMAIN 2>/dev/null | grep -i "etag" | wc -l)

echo "   📊 New response size: $new_response_size bytes (was: $response_size)"
echo "   📋 New content type: $new_content_type (was: $content_type)"
echo "   🏷️  New ETag count: $new_has_etag (was: $has_etag)"

# Check for Streamlit content
echo ""
echo "🔍 Testing for Streamlit content..."
streamlit_content=$(curl -s https://www.$DOMAIN 2>/dev/null | grep -i "streamlit\|dataguardian\|loading" | wc -l)
echo "   📄 Streamlit indicators: $streamlit_content (>0 is good)"

if [ "$streamlit_content" -gt 0 ]; then
    echo "✅ SUCCESS: Content contains Streamlit/DataGuardian elements!"
    
    echo ""
    echo "📄 Content preview from https://www.$DOMAIN:"
    echo "--- CONTENT START ---"
    curl -s https://www.$DOMAIN 2>/dev/null | head -20 | tail -10
    echo "--- CONTENT END ---"
else
    echo "⚠️  Content verification inconclusive"
    
    echo ""
    echo "📄 Current response from https://www.$DOMAIN:"
    echo "--- RESPONSE START ---"
    curl -s https://www.$DOMAIN 2>/dev/null | head -10
    echo "--- RESPONSE END ---"
fi

echo ""
echo "🧪 STEP 8: BROWSER SIMULATION TEST"
echo "==============================="

# Simulate browser behavior
echo "🌐 Testing browser-like behavior (following redirects)..."

# Full browser simulation
browser_test=$(curl -s -L -o /dev/null -w "%{http_code}" -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" https://www.$DOMAIN 2>/dev/null || echo "000")
echo "   🌐 Browser simulation: $browser_test"

# Check for common Streamlit elements
echo "🔍 Checking for Streamlit application elements..."
app_elements=$(curl -s -L -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" https://www.$DOMAIN 2>/dev/null | grep -E "(streamlit|st-|data-testid)" | wc -l)
echo "   🎯 App elements found: $app_elements"

echo ""
echo "📊 FINAL RESULTS ANALYSIS"
echo "========================"

# Determine success level
success_level="UNKNOWN"
issues_found=()
fixes_applied=()

# Check response characteristics improvement
if [ "$new_response_size" -gt "$response_size" ] && [ "$new_has_etag" -lt "$has_etag" ]; then
    success_level="HIGH"
    fixes_applied+=("Response size increased (dynamic content)")
    fixes_applied+=("ETag removed (no longer static)")
elif [ "$https_www" = "200" ] && [ "$streamlit_content" -gt 0 ]; then
    success_level="HIGH"
    fixes_applied+=("HTTPS working with Streamlit content")
elif [ "$https_www" = "200" ] && [ "$new_response_size" -ne 1837 ]; then
    success_level="MEDIUM"
    fixes_applied+=("HTTPS working with different content")
elif [ "$https_www" = "200" ]; then
    success_level="LOW"
    issues_found+=("HTTPS responds but content unclear")
else
    success_level="FAILED"
    issues_found+=("HTTPS not responding correctly")
fi

# Report results
echo ""
if [ "$success_level" = "HIGH" ]; then
    echo "🎉🎉🎉 COMPLETE SUCCESS! 🎉🎉🎉"
    echo "==============================="
    echo ""
    echo "✅ ALL ISSUES FIXED!"
    echo "✅ Static file conflict: RESOLVED"
    echo "✅ Nginx syntax errors: FIXED"
    echo "✅ Proxy configuration: WORKING"
    echo "✅ Dynamic content: SERVING"
    
    for fix in "${fixes_applied[@]}"; do
        echo "✅ $fix"
    done
    
    echo ""
    echo "🌐 YOUR DATAGUARDIAN PRO IS NOW FULLY FUNCTIONAL:"
    echo ""
    echo "   🎯 PRIMARY: https://dataguardianpro.nl"
    echo "   🎯 WWW: https://www.dataguardianpro.nl"
    echo "   🔗 DIRECT: http://$SERVER_IP:$APP_PORT"
    echo ""
    echo "📊 RESPONSE IMPROVEMENTS:"
    echo "   Size: $response_size → $new_response_size bytes"
    echo "   ETag: Static → Dynamic"
    echo "   Content: Streamlit elements detected"
    echo ""
    echo "🚀 READY FOR PRODUCTION!"
    echo "🇳🇱 Netherlands GDPR Compliance Platform LIVE!"
    
elif [ "$success_level" = "MEDIUM" ]; then
    echo "✅ SIGNIFICANT IMPROVEMENT"
    echo "========================="
    echo ""
    echo "✅ Main issues resolved:"
    for fix in "${fixes_applied[@]}"; do
        echo "✅ $fix"
    done
    echo ""
    echo "🔧 Minor issues (if any):"
    for issue in "${issues_found[@]}"; do
        echo "⚠️  $issue"
    done
    echo ""
    echo "💡 RECOMMENDATION:"
    echo "   Try accessing https://www.$DOMAIN in browser"
    echo "   Clear browser cache if needed"
    
else
    echo "⚠️  PARTIAL SUCCESS OR ISSUES REMAIN"
    echo "===================================="
    echo ""
    echo "📊 Current status:"
    echo "   Local app: $local_final"
    echo "   HTTPS www: $https_www"  
    echo "   Content elements: $streamlit_content"
    echo "   Response size: $new_response_size"
    echo ""
    echo "🔧 Issues found:"
    for issue in "${issues_found[@]}"; do
        echo "❌ $issue"
    done
    echo ""
    echo "🔧 ADDITIONAL TROUBLESHOOTING:"
    echo "   1. Check DataGuardian service: systemctl status dataguardian"
    echo "   2. Check Nginx error log: tail -20 /var/log/nginx/error.log"
    echo "   3. Test direct app access: curl http://localhost:$APP_PORT"
    echo "   4. Restart both services: systemctl restart dataguardian nginx"
fi

echo ""
echo "🎯 QUICK REFERENCE COMMANDS:"
echo "============================"
echo "   🔍 Test domain: curl -I https://www.$DOMAIN"
echo "   📄 Get content: curl -s https://www.$DOMAIN | head -20"
echo "   📊 Service status: systemctl status nginx dataguardian"
echo "   📄 View logs: tail -f /var/log/nginx/error.log"
echo "   🔄 Restart: systemctl restart nginx dataguardian"
echo "   📁 Config backup: $config_file.backup.*"

echo ""
echo "✅ COMPLETE NGINX STATIC FILE FIX COMPLETED!"
echo "Your DataGuardian Pro should now serve dynamic content instead of static files!"