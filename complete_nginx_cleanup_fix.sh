#!/bin/bash
# Complete Nginx Cleanup Fix
# Systematically finds and removes ALL $nonexistent variable references
# Then creates clean proxy configuration for DataGuardian Pro

echo "🔧 COMPLETE NGINX CLEANUP & FIX"
echo "==============================="
echo "Issue: nginx test fails with 'unknown nonexistent variable' from previous scripts"
echo "Fix: Find and remove ALL references, then create clean proxy configuration"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root"
    echo "💡 Please run: sudo ./complete_nginx_cleanup_fix.sh"
    exit 1
fi

DOMAIN="dataguardianpro.nl"
APP_PORT="5000"

echo "🔍 STEP 1: DIAGNOSE CURRENT ISSUE"
echo "==============================="

# Test current state
local_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$APP_PORT 2>/dev/null || echo "000")
domain_status=$(curl -s -o /dev/null -w "%{http_code}" https://www.$DOMAIN 2>/dev/null || echo "000")
domain_size=$(curl -s -o /dev/null -w "%{size_download}" https://www.$DOMAIN 2>/dev/null || echo "0")

echo "   ✅ Local Streamlit: $local_status"
echo "   📊 Domain status: $domain_status"  
echo "   📊 Domain size: $domain_size bytes"

# Test nginx configuration
echo ""
echo "🔍 Testing current nginx configuration..."
nginx_test_output=$(nginx -t 2>&1)
nginx_test_result=$?

if [ $nginx_test_result -eq 0 ]; then
    echo "✅ Nginx configuration is currently valid"
else
    echo "❌ Nginx configuration has errors:"
    echo "$nginx_test_output"
fi

echo ""
echo "🔍 STEP 2: FIND ALL $nonexistent REFERENCES"
echo "=========================================="

# Search for the problematic variable in all nginx configs
echo "🔍 Searching for all '$nonexistent' references in nginx configuration..."

nonexistent_files=()
search_result=$(grep -r "\$nonexistent" /etc/nginx 2>/dev/null || true)

if [ -n "$search_result" ]; then
    echo "❌ FOUND problematic references:"
    echo "$search_result"
    
    # Extract unique files with the problematic variable
    while IFS= read -r line; do
        if [ -n "$line" ]; then
            file_path=$(echo "$line" | cut -d: -f1)
            nonexistent_files+=("$file_path")
        fi
    done <<< "$search_result"
    
    # Remove duplicates
    nonexistent_files=($(printf "%s\n" "${nonexistent_files[@]}" | sort -u))
    
    echo ""
    echo "📁 Files containing '$nonexistent' variable:"
    for file in "${nonexistent_files[@]}"; do
        echo "   📄 $file"
    done
else
    echo "✅ No '$nonexistent' references found in /etc/nginx"
fi

echo ""
echo "🧹 STEP 3: CLEAN UP PROBLEMATIC REFERENCES"
echo "========================================"

if [ ${#nonexistent_files[@]} -gt 0 ]; then
    echo "🧹 Cleaning up $nonexistent references..."
    
    for file in "${nonexistent_files[@]}"; do
        echo "   📄 Processing: $file"
        
        # Create backup
        cp "$file" "$file.cleanup-backup.$(date +%Y%m%d_%H%M%S)"
        echo "   📁 Backup created: $file.cleanup-backup.*"
        
        # Remove lines containing $nonexistent
        sed -i '/\$nonexistent/d' "$file"
        echo "   ✅ Removed $nonexistent references from $file"
    done
    
    echo "✅ Cleanup completed for ${#nonexistent_files[@]} files"
else
    echo "ℹ️  No files needed cleanup"
fi

echo ""
echo "🔧 STEP 4: CREATE CLEAN NGINX CONFIGURATION"
echo "=========================================="

# Main site configuration
config_file="/etc/nginx/sites-enabled/$DOMAIN"

# Backup current config if it exists
if [ -f "$config_file" ]; then
    echo "📁 Backing up main site configuration..."
    cp "$config_file" "$config_file.clean-backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ Backup created"
fi

# Create completely clean configuration
echo "📝 Creating clean nginx configuration for $DOMAIN..."

cat > "$config_file" << 'EOF'
# DataGuardian Pro - Clean Proxy Configuration
# No experimental features, just basic proxy to Streamlit

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
    
    # Basic security headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Main location - Direct proxy to Streamlit
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        
        # WebSocket support for Streamlit
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Standard proxy headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Streamlit optimizations
        proxy_buffering off;
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
        proxy_connect_timeout 60s;
    }
    
    # Health check
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

echo "✅ Clean nginx configuration created"

echo ""
echo "🧪 STEP 5: TEST CLEANED CONFIGURATION"
echo "===================================="

echo "🔍 Testing nginx configuration after cleanup..."
cleaned_nginx_output=$(nginx -t 2>&1)
cleaned_nginx_result=$?

echo "Nginx test result:"
echo "$cleaned_nginx_output"

if [ $cleaned_nginx_result -eq 0 ]; then
    echo "✅ SUCCESS: Nginx configuration is now valid!"
elif echo "$cleaned_nginx_output" | grep -q "\[emerg\]"; then
    echo "❌ Critical errors still remain"
    
    # If still failing, show more diagnostic info
    echo ""
    echo "🔍 Additional diagnostics..."
    echo "Checking for any remaining problematic references:"
    remaining_issues=$(grep -r "\$nonexistent" /etc/nginx 2>/dev/null || echo "None found")
    echo "$remaining_issues"
    
    exit 1
else
    echo "⚠️  Only warnings - proceeding"
fi

echo ""
echo "🔄 STEP 6: APPLY CONFIGURATION"
echo "============================="

echo "🔄 Reloading nginx with cleaned configuration..."
systemctl reload nginx
sleep 5

if systemctl is-active --quiet nginx; then
    echo "✅ Nginx reloaded successfully"
else
    echo "❌ Nginx failed to reload"
    echo "📊 Nginx status:"
    systemctl status nginx --no-pager -l | head -10
    exit 1
fi

echo ""
echo "🧪 STEP 7: VERIFY THE FIX"
echo "======================="

echo "⏳ Waiting 15 seconds for configuration to take effect..."
sleep 15

# Test results
echo "🔍 Testing final results..."

final_local=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$APP_PORT 2>/dev/null || echo "000")
final_domain_status=$(curl -s -o /dev/null -w "%{http_code}" https://www.$DOMAIN 2>/dev/null || echo "000")
final_domain_size=$(curl -s -o /dev/null -w "%{size_download}" https://www.$DOMAIN 2>/dev/null || echo "0")

echo "   ✅ Local Streamlit: $final_local"
echo "   🎯 Domain status: $final_domain_status"
echo "   📊 Domain size: $final_domain_size bytes (was $domain_size)"

# Check for improvement
if [ "$final_domain_status" = "200" ] && [ "$final_domain_size" -gt "$domain_size" ]; then
    echo "✅ SUCCESS: Response size increased - now serving dynamic content!"
elif [ "$final_domain_status" = "200" ] && [ "$final_domain_size" -ne 1837 ]; then
    echo "✅ GOOD: Response size changed from static file"
elif [ "$final_domain_status" = "200" ]; then
    echo "⚠️  Domain responds - checking content..."
else
    echo "❌ Domain not responding correctly"
fi

echo ""
echo "🔍 STEP 8: CONTENT VERIFICATION"
echo "=============================="

# Check actual content being served
echo "🔍 Checking content from https://www.$DOMAIN..."

# Get headers
echo "📊 Response headers:"
curl -s -I https://www.$DOMAIN 2>/dev/null | head -10

echo ""
echo "📄 Content sample:"
echo "--- CONTENT START ---"
curl -s https://www.$DOMAIN 2>/dev/null | head -20 | tail -10
echo "--- CONTENT END ---"

# Check for Streamlit content
streamlit_content=$(curl -s https://www.$DOMAIN 2>/dev/null | grep -i "streamlit\|script\|css\|loading" | wc -l)
echo "   🎯 Dynamic content indicators: $streamlit_content"

echo ""
echo "📊 FINAL RESULTS"
echo "==============="

if [ "$final_domain_status" = "200" ] && [ "$final_domain_size" -gt "$domain_size" ] && [ "$streamlit_content" -gt 0 ]; then
    echo ""
    echo "🎉🎉🎉 COMPLETE SUCCESS! 🎉🎉🎉"
    echo "==============================="
    echo ""
    echo "✅ ALL ISSUES RESOLVED!"
    echo "✅ $nonexistent references: REMOVED"
    echo "✅ Nginx configuration: VALID"
    echo "✅ Static file issue: FIXED"
    echo "✅ Proxy to Streamlit: WORKING"
    echo "✅ Dynamic content: SERVING"
    echo ""
    echo "📊 IMPROVEMENTS:"
    echo "   Response size: $domain_size → $final_domain_size bytes"
    echo "   Content: Dynamic Streamlit application"
    echo "   Status: $final_domain_status (working)"
    echo ""
    echo "🌐 DATAGUARDIAN PRO NOW FULLY ACCESSIBLE:"
    echo "   🎯 https://dataguardianpro.nl"
    echo "   🎯 https://www.dataguardianpro.nl"
    echo ""
    echo "🚀 PRODUCTION READY!"
    echo "🇳🇱 Netherlands GDPR Compliance Platform LIVE!"
    
elif [ "$final_domain_status" = "200" ]; then
    echo ""
    echo "✅ SIGNIFICANT IMPROVEMENT"
    echo "========================="
    echo ""
    echo "✅ Nginx configuration: Working"
    echo "✅ Domain response: $final_domain_status"
    echo "✅ Size change: $domain_size → $final_domain_size bytes"
    echo "✅ Content elements: $streamlit_content found"
    echo ""
    echo "💡 NEXT STEPS:"
    echo "   1. Test in browser: https://www.$DOMAIN"
    echo "   2. Clear browser cache"
    echo "   3. Allow full propagation (2-3 minutes)"
    
else
    echo ""
    echo "⚠️  PARTIAL SUCCESS"
    echo "=================="
    echo ""
    echo "✅ Configuration cleanup: Completed"
    echo "✅ Nginx test: Passing"
    echo "📊 Domain status: $final_domain_status"
    echo "📊 Response size: $final_domain_size bytes"
    echo ""
    echo "🔧 TROUBLESHOOTING:"
    echo "   1. Check services: systemctl status nginx dataguardian"
    echo "   2. Check logs: tail -20 /var/log/nginx/error.log"
    echo "   3. Restart DataGuardian: systemctl restart dataguardian"
fi

echo ""
echo "🎯 VERIFICATION COMMANDS:"
echo "========================"
echo "   🔍 Test domain: curl -I https://www.$DOMAIN"
echo "   📄 Get content: curl -s https://www.$DOMAIN | head -20"
echo "   📊 Check services: systemctl status nginx dataguardian"
echo "   🔄 Restart all: systemctl restart nginx dataguardian"

echo ""
echo "✅ COMPLETE NGINX CLEANUP & FIX COMPLETED!"
echo "All $nonexistent references removed and clean proxy configuration applied!"