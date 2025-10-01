#!/bin/bash
# ADD SSL CONFIGURATION TO NGINX

set -e

echo "🔒 ADDING SSL/HTTPS CONFIGURATION"
echo "================================="
echo ""

# Backup current config
cp /etc/nginx/sites-available/dataguardianpro.nl /etc/nginx/sites-available/dataguardianpro.nl.backup

# Create new config with SSL
cat > /etc/nginx/sites-available/dataguardianpro.nl << 'NGINXEOF'
map $http_upgrade $connection_upgrade {
    default upgrade;
    '' close;
}

# HTTP server - redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name dataguardianpro.nl www.dataguardianpro.nl;
    
    # Redirect all HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name dataguardianpro.nl www.dataguardianpro.nl;
    
    # SSL Certificate
    ssl_certificate /etc/letsencrypt/live/dataguardianpro.nl/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dataguardianpro.nl/privkey.pem;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    
    # Proxy to Streamlit
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_read_timeout 300s;
    }
}
NGINXEOF

echo "✅ SSL configuration created"

echo ""
echo "Testing nginx configuration..."
if nginx -t; then
    echo "✅ Nginx config valid"
else
    echo "❌ Config error - restoring backup"
    cp /etc/nginx/sites-available/dataguardianpro.nl.backup /etc/nginx/sites-available/dataguardianpro.nl
    exit 1
fi

echo ""
echo "Reloading nginx..."
systemctl reload nginx

echo ""
echo "Waiting 5 seconds..."
sleep 5

echo ""
echo "🧪 TESTING HTTPS"
echo "==============="

echo ""
echo "Test 1: Nginx listening on 443?"
netstat -tlnp | grep ":443" && echo "✅ Port 443 active" || echo "❌ Port 443 not listening"

echo ""
echo "Test 2: HTTPS connection test"
if curl -k -I https://dataguardianpro.nl 2>&1 | grep -q "200 OK"; then
    echo "✅ HTTPS works!"
else
    echo "⚠️  Testing..."
    curl -k -I https://dataguardianpro.nl 2>&1 | head -5
fi

echo ""
echo "Test 3: HTTP redirect test"
if curl -I http://dataguardianpro.nl 2>&1 | grep -q "301"; then
    echo "✅ HTTP→HTTPS redirect working"
else
    echo "Testing redirect..."
    curl -I http://dataguardianpro.nl 2>&1 | head -3
fi

echo ""
echo "=========================================="
echo "🎉 SSL/HTTPS CONFIGURATION COMPLETE!"
echo "=========================================="
echo ""
echo "🌐 Access your app:"
echo "   https://dataguardianpro.nl"
echo ""
echo "🔐 Login:"
echo "   demo / demo123"
echo ""
echo "✅ Browser should now connect successfully!"

exit 0
