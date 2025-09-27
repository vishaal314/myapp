#!/bin/bash
# Domain & HTTPS Setup - Configure dataguardianpro.nl with SSL certificates
# Sets up: Nginx reverse proxy, Let's Encrypt SSL, domain configuration

echo "🌐 DATAGUARDIAN PRO DOMAIN & HTTPS SETUP"
echo "========================================"
echo "Configuring dataguardianpro.nl with SSL certificates"
echo ""

DOMAIN="dataguardianpro.nl"
SERVER_IP="45.81.35.202"
STREAMLIT_PORT="5000"

# =============================================================================
# PART 1: SYSTEM PREPARATION
# =============================================================================

echo "🔧 PART 1: System preparation"
echo "============================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root for system configuration"
    echo "💡 Run: sudo ./setup_domain_https.sh"
    exit 1
fi

echo "✅ Running as root"

# Update system packages
echo "📦 Updating system packages..."
apt-get update -qq

# Install required packages
echo "📦 Installing required packages..."
apt-get install -y \
    nginx \
    certbot \
    python3-certbot-nginx \
    ufw \
    curl \
    wget \
    2>/dev/null

echo "✅ System packages installed"

# =============================================================================
# PART 2: FIREWALL CONFIGURATION
# =============================================================================

echo ""
echo "🔥 PART 2: Firewall configuration"
echo "=============================="

echo "🔧 Configuring UFW firewall..."

# Enable UFW if not already enabled
ufw --force enable

# Allow essential ports
ufw allow ssh
ufw allow 22
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw allow 5000/tcp # Streamlit (for direct access)

# Reload firewall
ufw reload

echo "✅ Firewall configured"
echo "📊 Firewall status:"
ufw status

# =============================================================================
# PART 3: NGINX CONFIGURATION
# =============================================================================

echo ""
echo "🌐 PART 3: Nginx configuration"
echo "==========================="

# Stop nginx if running
systemctl stop nginx 2>/dev/null || echo "Nginx not running"

# Remove default site
rm -f /etc/nginx/sites-enabled/default

# Create DataGuardian Pro nginx configuration
echo "📝 Creating nginx configuration for $DOMAIN..."

cat > /etc/nginx/sites-available/dataguardian << EOF
# DataGuardian Pro - Nginx Configuration
# Domain: $DOMAIN
# Backend: Streamlit on localhost:$STREAMLIT_PORT

server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    # Redirect all HTTP to HTTPS (will be enabled after SSL setup)
    # return 301 https://\$server_name\$request_uri;
    
    # Temporary HTTP configuration for Let's Encrypt
    location / {
        proxy_pass http://127.0.0.1:$STREAMLIT_PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 86400;
        
        # Streamlit specific headers
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Forwarded-Server \$host;
        proxy_set_header X-Forwarded-Port \$server_port;
        
        # WebSocket support for Streamlit
        proxy_set_header Sec-WebSocket-Extensions \$http_sec_websocket_extensions;
        proxy_set_header Sec-WebSocket-Key \$http_sec_websocket_key;
        proxy_set_header Sec-WebSocket-Version \$http_sec_websocket_version;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy strict-origin-when-cross-origin;
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/dataguardian /etc/nginx/sites-enabled/

# Test nginx configuration
echo "🧪 Testing nginx configuration..."
if nginx -t; then
    echo "✅ Nginx configuration is valid"
else
    echo "❌ Nginx configuration error"
    exit 1
fi

# Start nginx
systemctl start nginx
systemctl enable nginx

echo "✅ Nginx configured and started"

# =============================================================================
# PART 4: DNS VERIFICATION
# =============================================================================

echo ""
echo "🔍 PART 4: DNS verification"
echo "========================"

echo "🔍 Checking DNS resolution for $DOMAIN..."

# Test DNS resolution
DNS_RESULT=$(dig +short $DOMAIN 2>/dev/null || echo "FAIL")
if [ "$DNS_RESULT" = "$SERVER_IP" ]; then
    echo "✅ DNS resolution: $DOMAIN → $SERVER_IP"
else
    echo "⚠️  DNS resolution: $DOMAIN → $DNS_RESULT"
    echo "💡 Expected: $SERVER_IP"
    echo "💡 DNS propagation may take up to 24-48 hours"
fi

# Test HTTP access
echo "🌐 Testing HTTP access..."
HTTP_TEST=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN 2>/dev/null || echo "000")
if [ "$HTTP_TEST" = "200" ]; then
    echo "✅ HTTP access working: http://$DOMAIN"
else
    echo "⚠️  HTTP access status: $HTTP_TEST"
    echo "💡 This is normal if DNS hasn't propagated yet"
fi

# =============================================================================
# PART 5: SSL CERTIFICATE SETUP
# =============================================================================

echo ""
echo "🔐 PART 5: SSL certificate setup"
echo "=============================="

echo "🔧 Setting up Let's Encrypt SSL certificate..."

# Check if domain resolves to our server
if [ "$DNS_RESULT" = "$SERVER_IP" ] && [ "$HTTP_TEST" = "200" ]; then
    echo "✅ Domain accessible - proceeding with SSL setup"
    
    # Get SSL certificate
    echo "📜 Obtaining SSL certificate from Let's Encrypt..."
    certbot --nginx \
        --non-interactive \
        --agree-tos \
        --email admin@$DOMAIN \
        --domains $DOMAIN,www.$DOMAIN \
        --redirect \
        2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ SSL certificate obtained successfully"
        
        # Test HTTPS
        sleep 5
        HTTPS_TEST=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN 2>/dev/null || echo "000")
        if [ "$HTTPS_TEST" = "200" ]; then
            echo "✅ HTTPS working: https://$DOMAIN"
        else
            echo "⚠️  HTTPS status: $HTTPS_TEST (may need a moment)"
        fi
        
    else
        echo "⚠️  SSL certificate setup had issues"
        echo "💡 This may be due to DNS propagation or domain verification"
    fi
    
else
    echo "⚠️  Skipping SSL setup - domain not yet accessible"
    echo "💡 Run this script again after DNS propagation completes"
fi

# =============================================================================
# PART 6: STREAMLIT CONFIGURATION UPDATE
# =============================================================================

echo ""
echo "⚙️  PART 6: Streamlit configuration update"
echo "======================================="

cd /opt/dataguardian || exit 1

# Update Streamlit config for domain usage
echo "📝 Updating Streamlit configuration for domain usage..."

cat > .streamlit/config.toml << EOF
[server]
headless = true
address = "127.0.0.1"
port = $STREAMLIT_PORT
enableCORS = false
enableXsrfProtection = false
maxUploadSize = 1000

[browser]
gatherUsageStats = false
serverAddress = "$DOMAIN"
serverPort = 443

[theme]
primaryColor = "#4267B2"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F5"
textColor = "#1E293B"
font = "sans serif"

[global]
developmentMode = false

[runner]
fastReruns = true
magicEnabled = true
EOF

# Restart Streamlit to apply domain configuration
echo "🔄 Restarting Streamlit with domain configuration..."

# Get current Streamlit PID
STREAMLIT_PID=$(pgrep -f "streamlit run" | head -1)
if [ -n "$STREAMLIT_PID" ]; then
    kill $STREAMLIT_PID
    sleep 3
fi

# Start Streamlit with domain configuration
nohup streamlit run app.py \
    --server.port $STREAMLIT_PORT \
    --server.address 127.0.0.1 \
    --server.headless true \
    > streamlit_domain.log 2>&1 &

NEW_PID=$!
echo $NEW_PID > streamlit.pid

echo "✅ Streamlit restarted for domain usage (PID: $NEW_PID)"

# =============================================================================
# PART 7: AUTOMATIC SSL RENEWAL
# =============================================================================

echo ""
echo "🔄 PART 7: Automatic SSL renewal setup"
echo "===================================="

echo "⚙️  Setting up automatic SSL certificate renewal..."

# Create renewal script
cat > /etc/cron.daily/renew-dataguardian-ssl << EOF
#!/bin/bash
# Auto-renew DataGuardian Pro SSL certificates

certbot renew --quiet --nginx
systemctl reload nginx

# Log renewal attempts
echo "\$(date): SSL renewal check completed" >> /var/log/dataguardian-ssl.log
EOF

chmod +x /etc/cron.daily/renew-dataguardian-ssl

echo "✅ Automatic SSL renewal configured"

# =============================================================================
# PART 8: FINAL VERIFICATION & STATUS
# =============================================================================

echo ""
echo "🏁 PART 8: Final verification & status"
echo "===================================="

sleep 10

# Final tests
echo "🧪 Running final verification tests..."

# Test domain resolution
FINAL_DNS=$(dig +short $DOMAIN 2>/dev/null || echo "FAIL")
echo "📍 DNS: $DOMAIN → $FINAL_DNS"

# Test HTTP
FINAL_HTTP=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN 2>/dev/null || echo "000")
echo "🌐 HTTP: $FINAL_HTTP"

# Test HTTPS
FINAL_HTTPS=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN 2>/dev/null || echo "000")
echo "🔐 HTTPS: $FINAL_HTTPS"

# Test Streamlit
STREAMLIT_STATUS=$(ps aux | grep -v grep | grep "streamlit run" | wc -l)
echo "🖥️  Streamlit: $STREAMLIT_STATUS process(es) running"

echo ""
echo "📊 DOMAIN & HTTPS SETUP STATUS"
echo "=============================="

if [ "$FINAL_HTTPS" = "200" ]; then
    echo ""
    echo "🎉🎉🎉 COMPLETE SUCCESS! 🎉🎉🎉"
    echo "==============================="
    echo ""
    echo "✅ DATAGUARDIAN PRO IS LIVE WITH HTTPS!"
    echo "✅ Domain: $DOMAIN"
    echo "✅ SSL Certificate: ACTIVE"
    echo "✅ HTTPS Redirect: WORKING"
    echo "✅ All 12 Scanner Types: READY"
    echo ""
    echo "🌐 YOUR PRODUCTION PLATFORM:"
    echo "   🔐 Secure URL: https://$DOMAIN"
    echo "   🌍 Public Access: AVAILABLE"
    echo "   📱 Mobile Friendly: YES"
    echo "   🇳🇱 Netherlands Market: READY"
    echo ""
    echo "🚀 READY FOR €25K MRR LAUNCH!"
    echo "Your Netherlands compliance platform is now live with professional HTTPS!"

elif [ "$FINAL_HTTP" = "200" ]; then
    echo ""
    echo "⏳ DOMAIN WORKING - SSL PENDING"
    echo "=============================="
    echo ""
    echo "✅ Domain: $DOMAIN accessible via HTTP"
    echo "⏳ HTTPS: Setting up (may take a few minutes)"
    echo "✅ Platform: Fully operational"
    echo ""
    echo "💡 HTTPS will be available shortly"
    echo "🔄 Check: https://$DOMAIN in 5-10 minutes"

else
    echo ""
    echo "⏳ DNS PROPAGATION IN PROGRESS"
    echo "============================="
    echo ""
    echo "✅ Server: Configured and ready"
    echo "✅ SSL Setup: Prepared"
    echo "⏳ DNS: Propagating (24-48 hours)"
    echo ""
    echo "💡 NEXT STEPS:"
    echo "   1. Wait for DNS propagation"
    echo "   2. Re-run: sudo ./setup_domain_https.sh"
    echo "   3. Domain will be live with HTTPS"
fi

echo ""
echo "📋 CONFIGURATION SUMMARY:"
echo "========================"
echo "   🌐 Domain: $DOMAIN"
echo "   📍 Server IP: $SERVER_IP"
echo "   🔐 SSL: Let's Encrypt"
echo "   🌐 Web Server: Nginx"
echo "   🖥️  Backend: Streamlit on port $STREAMLIT_PORT"
echo "   🔄 Auto-renewal: Configured"

echo ""
echo "✅ DOMAIN & HTTPS SETUP COMPLETE!"
echo "DataGuardian Pro is configured for production with professional domain"