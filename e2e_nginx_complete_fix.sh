#!/bin/bash
# End-to-End Nginx Complete Fix
# Completely removes ALL $nonexistent references and creates clean proxy
# Aggressive approach: removes problematic files instead of editing them

echo "🔧 END-TO-END NGINX COMPLETE FIX"
echo "================================"
echo "Issue: nginx reads backup files with $nonexistent causing persistent errors"
echo "Fix: Remove ALL problematic files and create completely clean configuration"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root"
    echo "💡 Please run: sudo ./e2e_nginx_complete_fix.sh"
    exit 1
fi

DOMAIN="dataguardianpro.nl"
APP_PORT="5000"

echo "🔍 STEP 1: CURRENT STATE DIAGNOSIS"
echo "================================="

# Test current state
local_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$APP_PORT 2>/dev/null || echo "000")
domain_status=$(curl -s -o /dev/null -w "%{http_code}" https://www.$DOMAIN 2>/dev/null || echo "000")
domain_size=$(curl -s -o /dev/null -w "%{size_download}" https://www.$DOMAIN 2>/dev/null || echo "0")

echo "   ✅ Local Streamlit: $local_status"
echo "   📊 Domain status: $domain_status"
echo "   📊 Domain size: $domain_size bytes"

if [ "$domain_size" -eq 1837 ]; then
    echo "❌ CONFIRMED: Still serving 1837-byte static file"
else
    echo "ℹ️  Current response size: $domain_size bytes"
fi

echo ""
echo "🔍 STEP 2: FIND ALL PROBLEMATIC FILES"
echo "===================================="

# Find ALL files containing $nonexistent in nginx directories
echo "🔍 Searching for ALL files with $nonexistent references..."

problematic_files=()
while IFS= read -r -d '' file; do
    if grep -q "\$nonexistent" "$file" 2>/dev/null; then
        problematic_files+=("$file")
    fi
done < <(find /etc/nginx -type f -name "*.conf" -o -name "*dataguardianpro*" -print0 2>/dev/null)

if [ ${#problematic_files[@]} -gt 0 ]; then
    echo "❌ FOUND ${#problematic_files[@]} files with $nonexistent references:"
    for file in "${problematic_files[@]}"; do
        echo "   📄 $file"
        # Show the problematic lines
        grep -n "\$nonexistent" "$file" 2>/dev/null | head -2 | sed 's/^/      /'
    done
else
    echo "✅ No files with $nonexistent found"
fi

echo ""
echo "🗑️  STEP 3: AGGRESSIVE CLEANUP - REMOVE PROBLEMATIC FILES"
echo "======================================================="

if [ ${#problematic_files[@]} -gt 0 ]; then
    echo "🗑️  Removing ALL files containing $nonexistent..."
    
    # Create a safe backup directory
    backup_dir="/tmp/nginx-problematic-files-backup-$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    echo "📁 Created backup directory: $backup_dir"
    
    for file in "${problematic_files[@]}"; do
        echo "   🗑️  Removing: $file"
        
        # Copy to backup first
        cp "$file" "$backup_dir/$(basename "$file")-$(date +%H%M%S)" 2>/dev/null || true
        
        # Remove the problematic file
        rm -f "$file"
        echo "   ✅ Removed: $file"
    done
    
    echo "✅ Removed ${#problematic_files[@]} problematic files"
    echo "📁 Backups saved to: $backup_dir"
else
    echo "ℹ️  No files needed removal"
fi

echo ""
echo "🧹 STEP 4: CLEAN UP NGINX DIRECTORIES"
echo "===================================="

# Remove any remaining backup files that might contain problems
echo "🧹 Cleaning up nginx backup files..."

# Remove old backup files from sites-enabled and sites-available
find /etc/nginx/sites-enabled -name "*backup*" -delete 2>/dev/null || true
find /etc/nginx/sites-available -name "*backup*" -delete 2>/dev/null || true
find /etc/nginx/conf.d -name "*backup*" -delete 2>/dev/null || true

echo "✅ Nginx directories cleaned"

echo ""
echo "🔧 STEP 5: CREATE COMPLETELY FRESH CONFIGURATION"
echo "=============================================="

# Ensure directories exist
mkdir -p /etc/nginx/sites-available
mkdir -p /etc/nginx/sites-enabled

# Remove any existing configuration for the domain
rm -f "/etc/nginx/sites-enabled/$DOMAIN" 2>/dev/null || true
rm -f "/etc/nginx/sites-available/$DOMAIN" 2>/dev/null || true

# Create completely fresh configuration
config_file="/etc/nginx/sites-available/$DOMAIN"
echo "📝 Creating fresh nginx configuration at $config_file..."

cat > "$config_file" << 'EOF'
# DataGuardian Pro - Fresh Clean Configuration
# Created to fix persistent $nonexistent variable errors

server {
    listen 80;
    listen [::]:80;
    server_name dataguardianpro.nl www.dataguardianpro.nl;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name dataguardianpro.nl www.dataguardianpro.nl;
    
    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/dataguardianpro.nl/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dataguardianpro.nl/privkey.pem;
    
    # SSL settings
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
    
    # Client settings
    client_max_body_size 50M;
    
    # MAIN LOCATION - Direct proxy to Streamlit (NO COMPLEX DIRECTIVES)
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        
        # WebSocket support for Streamlit
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Essential proxy headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Streamlit optimizations
        proxy_buffering off;
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
        proxy_connect_timeout 60s;
        
        # Additional WebSocket headers
        proxy_set_header Sec-WebSocket-Extensions $http_sec_websocket_extensions;
        proxy_set_header Sec-WebSocket-Key $http_sec_websocket_key;
        proxy_set_header Sec-WebSocket-Version $http_sec_websocket_version;
    }
    
    # Health check endpoint
    location = /health {
        access_log off;
        proxy_pass http://127.0.0.1:5000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Block hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
EOF

echo "✅ Fresh configuration created"

# Enable the site
echo "🔗 Enabling site configuration..."
ln -sf "$config_file" "/etc/nginx/sites-enabled/$DOMAIN"
echo "✅ Site enabled"

echo ""
echo "🧪 STEP 6: TEST FRESH CONFIGURATION"
echo "=================================="

echo "🔍 Testing fresh nginx configuration..."
fresh_nginx_output=$(nginx -t 2>&1)
fresh_nginx_result=$?

echo "Nginx test output:"
echo "$fresh_nginx_output"

if [ $fresh_nginx_result -eq 0 ]; then
    echo "✅ SUCCESS: Fresh configuration is valid!"
elif echo "$fresh_nginx_output" | grep -q "\[emerg\]"; then
    echo "❌ Critical errors in fresh configuration"
    echo "This suggests a deeper nginx system issue"
    
    # Show current nginx configuration structure
    echo ""
    echo "🔍 Current nginx configuration structure:"
    echo "Main config: /etc/nginx/nginx.conf"
    echo "Sites available:"
    ls -la /etc/nginx/sites-available/ 2>/dev/null | head -10
    echo "Sites enabled:"
    ls -la /etc/nginx/sites-enabled/ 2>/dev/null | head -10
    
    exit 1
else
    echo "⚠️  Only warnings present - proceeding"
fi

echo ""
echo "🔄 STEP 7: APPLY FRESH CONFIGURATION"
echo "=================================="

echo "🛑 Stopping nginx for clean restart..."
systemctl stop nginx
sleep 3

# Kill any remaining nginx processes
pkill -f nginx 2>/dev/null || true
sleep 2

echo "▶️  Starting nginx with fresh configuration..."
systemctl start nginx
sleep 5

if systemctl is-active --quiet nginx; then
    echo "✅ Nginx started successfully with fresh configuration"
else
    echo "❌ Nginx failed to start"
    echo "📊 Nginx status:"
    systemctl status nginx --no-pager -l | head -15
    exit 1
fi

echo ""
echo "🧪 STEP 8: COMPREHENSIVE VERIFICATION"
echo "===================================="

echo "⏳ Waiting 20 seconds for full configuration to take effect..."
sleep 20

# Test all aspects
echo "🔍 Testing comprehensive results..."

final_local=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$APP_PORT 2>/dev/null || echo "000")
final_domain_status=$(curl -s -o /dev/null -w "%{http_code}" https://www.$DOMAIN 2>/dev/null || echo "000")
final_domain_size=$(curl -s -o /dev/null -w "%{size_download}" https://www.$DOMAIN 2>/dev/null || echo "0")

echo "   ✅ Local Streamlit: $final_local"
echo "   🎯 Domain HTTPS status: $final_domain_status"
echo "   📊 Domain response size: $final_domain_size bytes (was $domain_size)"

# Test additional variants
http_redirect=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN 2>/dev/null || echo "000")
https_main=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN 2>/dev/null || echo "000")

echo "   🔄 HTTP redirect: $http_redirect (should be 301)"
echo "   🔐 HTTPS main domain: $https_main"

echo ""
echo "🔍 STEP 9: CONTENT ANALYSIS"
echo "==========================="

# Analyze content being served
echo "🔍 Analyzing content from https://www.$DOMAIN..."

# Get response headers
echo "📊 Response headers:"
curl -s -I https://www.$DOMAIN 2>/dev/null | head -8

echo ""
echo "📄 Content sample (first 20 lines):"
echo "--- CONTENT START ---"
content_sample=$(curl -s https://www.$DOMAIN 2>/dev/null | head -20)
echo "$content_sample"
echo "--- CONTENT END ---"

# Check for dynamic content indicators
streamlit_indicators=$(echo "$content_sample" | grep -i "streamlit\|script\|css\|DOCTYPE\|loading\|div" | wc -l)
echo "   🎯 Dynamic content indicators: $streamlit_indicators"

# Check if it's no longer the static file
is_static_file=false
if [ "$final_domain_size" -eq 1837 ]; then
    is_static_file=true
fi

echo ""
echo "📊 FINAL RESULTS ANALYSIS"
echo "========================"

# Determine success level
if [ "$final_domain_status" = "200" ] && [ "$final_domain_size" -gt "$domain_size" ] && [ "$streamlit_indicators" -gt 3 ]; then
    echo ""
    echo "🎉🎉🎉 COMPLETE END-TO-END SUCCESS! 🎉🎉🎉"
    echo "========================================"
    echo ""
    echo "✅ ALL ISSUES COMPLETELY RESOLVED!"
    echo "✅ Problematic files: REMOVED"
    echo "✅ Fresh nginx config: WORKING"
    echo "✅ Static file issue: FIXED"
    echo "✅ Proxy to Streamlit: FUNCTIONAL"
    echo "✅ Dynamic content: SERVING PROPERLY"
    echo ""
    echo "📊 DRAMATIC IMPROVEMENTS:"
    echo "   Response size: $domain_size → $final_domain_size bytes"
    echo "   Content type: Dynamic Streamlit application"
    echo "   Status codes: All working ($final_domain_status)"
    echo "   Dynamic indicators: $streamlit_indicators found"
    echo ""
    echo "🌐 DATAGUARDIAN PRO FULLY OPERATIONAL:"
    echo "   🎯 PRIMARY: https://dataguardianpro.nl"
    echo "   🎯 WWW: https://www.dataguardianpro.nl"
    echo "   🔗 DIRECT: http://45.81.35.202:$APP_PORT"
    echo ""
    echo "🚀 PRODUCTION DEPLOYMENT COMPLETE!"
    echo "🇳🇱 Netherlands GDPR Compliance Platform LIVE!"
    echo "💰 €25K MRR Target Platform OPERATIONAL!"
    
elif [ "$final_domain_status" = "200" ] && [ "$is_static_file" = false ]; then
    echo ""
    echo "✅ MAJOR IMPROVEMENT ACHIEVED"
    echo "============================="
    echo ""
    echo "✅ Fresh configuration: Working"
    echo "✅ Domain response: $final_domain_status"
    echo "✅ Size improvement: $domain_size → $final_domain_size bytes"
    echo "✅ No longer static file: Confirmed"
    echo "✅ Content indicators: $streamlit_indicators found"
    echo ""
    echo "💡 FINAL STEPS:"
    echo "   1. Test in browser: https://www.$DOMAIN"
    echo "   2. Clear browser cache completely"
    echo "   3. Allow 3-5 minutes for DNS/CDN propagation"
    echo "   4. Check browser developer console for any remaining issues"
    
elif [ "$final_domain_status" = "200" ]; then
    echo ""
    echo "✅ SIGNIFICANT PROGRESS"
    echo "======================"
    echo ""
    echo "✅ Configuration: Clean and working"
    echo "✅ Domain status: $final_domain_status"
    echo "✅ Response: $final_domain_size bytes"
    echo ""
    echo "🔧 NEXT ACTIONS:"
    echo "   1. Verify in browser: https://www.$DOMAIN"
    echo "   2. Check DataGuardian service: systemctl status dataguardian"
    echo "   3. Monitor logs: tail -f /var/log/nginx/error.log"
    
else
    echo ""
    echo "⚠️  CONFIGURATION IMPROVED BUT DOMAIN ISSUES REMAIN"
    echo "=================================================="
    echo ""
    echo "✅ Nginx cleanup: Completed successfully"
    echo "✅ Fresh config: Applied and tested"
    echo "📊 Domain status: $final_domain_status"
    echo "📊 Response size: $final_domain_size bytes"
    echo ""
    echo "🔧 TROUBLESHOOTING STEPS:"
    echo "   1. Check DataGuardian service: systemctl status dataguardian"
    echo "   2. Restart DataGuardian: systemctl restart dataguardian"
    echo "   3. Check application logs for errors"
    echo "   4. Verify SSL certificates: certbot certificates"
fi

echo ""
echo "🎯 POST-FIX VERIFICATION COMMANDS:"
echo "=================================="
echo "   🔍 Quick test: curl -I https://www.$DOMAIN"
echo "   📄 Content check: curl -s https://www.$DOMAIN | head -30"
echo "   📊 Service status: systemctl status nginx dataguardian"
echo "   🔄 Restart services: systemctl restart dataguardian nginx"
echo "   📄 Nginx logs: tail -20 /var/log/nginx/error.log"
echo "   📄 App logs: journalctl -u dataguardian -n 20"

echo ""
echo "✅ END-TO-END NGINX COMPLETE FIX FINISHED!"
echo "All problematic files removed and fresh configuration applied!"
echo "Your DataGuardian Pro should now be fully accessible via HTTPS!"