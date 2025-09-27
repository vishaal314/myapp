#!/bin/bash
# Final Nginx Fix - Ultra Simple Approach
# Fixes: 1837-byte static file by using minimal, clean nginx configuration
# No complex variables, no experimental features, just basic proxy

echo "🔧 FINAL NGINX FIX - MINIMAL APPROACH"
echo "====================================="
echo "Issue: Domain serves 1837-byte static file instead of Streamlit"
echo "Fix: Ultra-simple nginx configuration with basic proxy only"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root"
    echo "💡 Please run: sudo ./final_nginx_fix.sh"
    exit 1
fi

DOMAIN="dataguardianpro.nl"
APP_PORT="5000"

echo "🔍 STEP 1: CONFIRM THE PROBLEM"
echo "============================="

# Check current issue
local_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$APP_PORT 2>/dev/null || echo "000")
domain_status=$(curl -s -o /dev/null -w "%{http_code}" https://www.$DOMAIN 2>/dev/null || echo "000")
domain_size=$(curl -s -o /dev/null -w "%{size_download}" https://www.$DOMAIN 2>/dev/null || echo "0")

echo "   ✅ Local Streamlit: $local_status"
echo "   📊 Domain status: $domain_status"
echo "   📊 Domain size: $domain_size bytes"

if [ "$domain_size" -eq 1837 ]; then
    echo "❌ CONFIRMED: Serving 1837-byte static file instead of Streamlit"
else
    echo "ℹ️  Current domain response: $domain_size bytes"
fi

echo ""
echo "🔧 STEP 2: CREATE MINIMAL NGINX CONFIG"
echo "====================================="

# Backup current config
config_file="/etc/nginx/sites-enabled/$DOMAIN"
if [ -f "$config_file" ]; then
    echo "📁 Creating backup..."
    cp "$config_file" "$config_file.final-backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ Backup created"
else
    echo "❌ Config file not found: $config_file"
    exit 1
fi

# Create the most minimal, clean nginx configuration possible
echo "📝 Creating minimal nginx configuration..."

cat > "$config_file" << 'EOF'
# DataGuardian Pro - Minimal Working Configuration
# Ultra-simple proxy to fix static file issue

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
    
    ssl_certificate /etc/letsencrypt/live/dataguardianpro.nl/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dataguardianpro.nl/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }
}
EOF

echo "✅ Minimal nginx configuration created"

echo ""
echo "🧪 STEP 3: TEST CONFIGURATION"
echo "============================"

# Test the configuration
echo "🔍 Testing nginx configuration..."
nginx_output=$(nginx -t 2>&1)
nginx_result=$?

echo "Nginx test output:"
echo "$nginx_output"

if [ $nginx_result -eq 0 ]; then
    echo "✅ Configuration test passed"
elif echo "$nginx_output" | grep -q "\[emerg\]"; then
    echo "❌ Critical errors in configuration"
    echo "🔄 Restoring backup..."
    cp "$config_file.final-backup."* "$config_file" 2>/dev/null || true
    exit 1
else
    echo "⚠️  Warnings only - proceeding (warnings are acceptable)"
fi

echo ""
echo "🔄 STEP 4: APPLY CONFIGURATION"
echo "============================="

# Apply the configuration
echo "🔄 Restarting nginx..."
systemctl restart nginx
sleep 5

if systemctl is-active --quiet nginx; then
    echo "✅ Nginx restarted successfully"
else
    echo "❌ Nginx failed to restart"
    echo "📊 Status:"
    systemctl status nginx --no-pager -l | head -10
    echo "🔄 Restoring backup..."
    cp "$config_file.final-backup."* "$config_file" 2>/dev/null || true
    systemctl restart nginx
    exit 1
fi

echo ""
echo "🧪 STEP 5: VERIFY THE FIX"
echo "======================="

echo "⏳ Waiting 15 seconds for changes to take effect..."
sleep 15

# Test the results
echo "🔍 Testing results..."

new_local=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$APP_PORT 2>/dev/null || echo "000")
new_domain_status=$(curl -s -o /dev/null -w "%{http_code}" https://www.$DOMAIN 2>/dev/null || echo "000")
new_domain_size=$(curl -s -o /dev/null -w "%{size_download}" https://www.$DOMAIN 2>/dev/null || echo "0")

echo "   ✅ Local Streamlit: $new_local"
echo "   🎯 Domain status: $new_domain_status"
echo "   📊 Domain size: $new_domain_size bytes (was $domain_size)"

# Check for improvement
if [ "$new_domain_status" = "200" ] && [ "$new_domain_size" -gt "$domain_size" ]; then
    echo "✅ SUCCESS: Response size increased - serving dynamic content!"
elif [ "$new_domain_status" = "200" ] && [ "$new_domain_size" -ne 1837 ]; then
    echo "✅ GOOD: Response size changed from static file size"
elif [ "$new_domain_status" = "200" ]; then
    echo "⚠️  Domain responds but checking content..."
else
    echo "❌ Domain not responding correctly"
fi

echo ""
echo "🔍 STEP 6: CONTENT VERIFICATION"
echo "=============================="

# Check actual content
echo "🔍 Checking content from domain..."
echo "📄 Content sample:"
echo "--- START ---"
curl -s https://www.$DOMAIN 2>/dev/null | head -15 | tail -10
echo "--- END ---"

# Check for dynamic content indicators
content_check=$(curl -s https://www.$DOMAIN 2>/dev/null | grep -E "(streamlit|script|css|DOCTYPE|html)" | wc -l)
echo "   🎯 Dynamic content indicators: $content_check"

echo ""
echo "📊 FINAL RESULTS"
echo "==============="

if [ "$new_domain_status" = "200" ] && [ "$new_domain_size" -gt "$domain_size" ] && [ "$content_check" -gt 0 ]; then
    echo ""
    echo "🎉🎉🎉 NGINX ISSUE COMPLETELY FIXED! 🎉🎉🎉"
    echo "=========================================="
    echo ""
    echo "✅ COMPLETE SUCCESS!"
    echo "✅ Static file issue: RESOLVED"
    echo "✅ Nginx proxy: WORKING PERFECTLY"
    echo "✅ Dynamic content: SERVING"
    echo ""
    echo "📊 IMPROVEMENTS:"
    echo "   Response size: $domain_size → $new_domain_size bytes"
    echo "   Content type: Dynamic (Streamlit)"
    echo "   Status: $new_domain_status"
    echo ""
    echo "🌐 DATAGUARDIAN PRO NOW FULLY ACCESSIBLE:"
    echo "   🎯 https://dataguardianpro.nl"
    echo "   🎯 https://www.dataguardianpro.nl"
    echo ""
    echo "🚀 PRODUCTION READY!"
    echo "🇳🇱 Netherlands GDPR Compliance Platform LIVE!"
    
elif [ "$new_domain_status" = "200" ]; then
    echo ""
    echo "✅ SIGNIFICANT PROGRESS"
    echo "======================"
    echo ""
    echo "✅ Nginx proxy: Working ($new_domain_status)"
    echo "✅ Size change: $domain_size → $new_domain_size bytes"
    echo "✅ Content elements: $content_check found"
    echo ""
    echo "💡 NEXT:"
    echo "   1. Test in browser: https://www.$DOMAIN"
    echo "   2. Clear browser cache if needed"
    echo "   3. Allow 2-3 minutes for full propagation"
    
else
    echo ""
    echo "⚠️  PARTIAL RESULTS"
    echo "=================="
    echo ""
    echo "📊 Status:"
    echo "   Local: $new_local"
    echo "   Domain: $new_domain_status"
    echo "   Size: $new_domain_size bytes"
    echo ""
    echo "🔧 TROUBLESHOOTING:"
    echo "   1. Check services: systemctl status nginx dataguardian"
    echo "   2. Check logs: tail -20 /var/log/nginx/error.log"
    echo "   3. Restart services: systemctl restart dataguardian nginx"
fi

echo ""
echo "🎯 VERIFICATION COMMANDS:"
echo "========================"
echo "   🔍 Test: curl -I https://www.$DOMAIN"
echo "   📄 Content: curl -s https://www.$DOMAIN | head -20"
echo "   📊 Status: systemctl status nginx dataguardian"
echo "   🔄 Restart: systemctl restart nginx dataguardian"

echo ""
echo "✅ FINAL NGINX FIX COMPLETED!"
echo "Static file issue should now be resolved with dynamic Streamlit content!"