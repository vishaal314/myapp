#!/bin/bash
# SSL & HTTPS Failure Recovery Script
# Handles specific SSL certificate and HTTPS configuration failures
# Based on E2E test results showing SSL expansion and HTTPS access issues

echo "🚨 SSL & HTTPS FAILURE RECOVERY SCRIPT"
echo "====================================="
echo "Addressing SSL certificate and HTTPS configuration failures"
echo ""

# =============================================================================
# FAILURE CASE ANALYSIS AND FIXES
# =============================================================================

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root"
    echo "💡 Please run: sudo ./fix_ssl_https_failures.sh"
    exit 1
fi

echo "✅ Running as root"

# Define variables
DOMAIN="dataguardianpro.nl"
SERVER_IP="45.81.35.202"
APP_PORT="5000"

# Find DataGuardian installation
DATAGUARDIAN_DIR=""
if [ -d "/opt/dataguardian" ] && [ -f "/opt/dataguardian/app.py" ]; then
    DATAGUARDIAN_DIR="/opt/dataguardian"
elif [ -f "app.py" ]; then
    DATAGUARDIAN_DIR="$(pwd)"
else
    echo "❌ DataGuardian Pro installation not found"
    exit 1
fi

echo "✅ DataGuardian Pro found at: $DATAGUARDIAN_DIR"
cd "$DATAGUARDIAN_DIR"

# =============================================================================
# FAILURE CASE 1: SSL CERTIFICATE EXPANSION ISSUE
# =============================================================================

fix_ssl_certificate_expansion() {
    echo ""
    echo "🔐 FAILURE CASE 1: SSL CERTIFICATE EXPANSION"
    echo "==========================================="
    
    echo "🔍 Analyzing existing SSL certificates..."
    
    # Check for existing certificates
    if [ -f "/etc/letsencrypt/renewal/$DOMAIN.conf" ]; then
        echo "✅ Found existing certificate configuration"
        
        # Read current domains
        existing_domains=$(grep "^domains" /etc/letsencrypt/renewal/$DOMAIN.conf | cut -d'=' -f2 | tr ',' ' ')
        echo "📋 Current domains: $existing_domains"
        
        # Check if www is missing
        if echo "$existing_domains" | grep -q "www.$DOMAIN"; then
            echo "✅ WWW domain already included"
            return 0
        else
            echo "⚠️  WWW domain missing - expanding certificate"
            
            # Stop nginx for certificate expansion
            systemctl stop nginx
            
            echo "🔧 Expanding SSL certificate with --expand flag..."
            
            # Use expand flag to add www subdomain
            if certbot certonly \
                --standalone \
                --non-interactive \
                --agree-tos \
                --email admin@$DOMAIN \
                --expand \
                -d $DOMAIN \
                -d www.$DOMAIN; then
                
                echo "✅ SSL certificate expansion: SUCCESSFUL"
                return 0
            else
                echo "❌ SSL certificate expansion: FAILED"
                echo "🔍 Certbot error log:"
                tail -20 /var/log/letsencrypt/letsencrypt.log 2>/dev/null || echo "No log found"
                return 1
            fi
        fi
    else
        echo "⚠️  No existing certificate found - creating new one"
        
        # Stop nginx for new certificate
        systemctl stop nginx
        
        echo "🔧 Creating new SSL certificate..."
        
        if certbot certonly \
            --standalone \
            --non-interactive \
            --agree-tos \
            --email admin@$DOMAIN \
            -d $DOMAIN \
            -d www.$DOMAIN; then
            
            echo "✅ New SSL certificate: SUCCESSFUL"
            return 0
        else
            echo "❌ New SSL certificate: FAILED"
            return 1
        fi
    fi
}

# =============================================================================
# FAILURE CASE 2: HTTPS NGINX CONFIGURATION ISSUE
# =============================================================================

fix_https_nginx_configuration() {
    echo ""
    echo "🌐 FAILURE CASE 2: HTTPS NGINX CONFIGURATION"
    echo "=========================================="
    
    echo "🔍 Checking SSL certificate files..."
    
    if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ] || [ ! -f "/etc/letsencrypt/live/$DOMAIN/privkey.pem" ]; then
        echo "❌ SSL certificate files not found"
        return 1
    fi
    
    echo "✅ SSL certificate files found"
    
    echo "📝 Creating complete HTTPS Nginx configuration..."
    
    # Create comprehensive HTTPS configuration
    cat > /etc/nginx/sites-available/$DOMAIN << EOF
# DataGuardian Pro - Complete HTTPS Configuration for $DOMAIN
# Addresses HTTPS connectivity failures

# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN www.$DOMAIN;
    
    # Security headers even for redirects
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    
    # Redirect all HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

# HTTPS server with comprehensive configuration
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;
    
    # SSL certificate configuration
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/$DOMAIN/chain.pem;
    
    # Enhanced SSL security configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    
    # SSL session optimization
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;
    
    # OCSP stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;
    
    # Enhanced security headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self' wss: ws:;" always;
    
    # Client settings for large file uploads
    client_max_body_size 50M;
    client_body_timeout 60s;
    client_header_timeout 60s;
    client_body_buffer_size 1M;
    
    # Apply rate limiting (zones defined in conf.d/rate_limiting.conf)
    limit_req zone=general burst=20 nodelay;
    limit_conn conn_limit_per_ip 20;
    
    # Compression optimization
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        text/csv
        application/javascript
        application/json
        application/xml+rss
        application/xml
        application/pdf
        image/svg+xml;
    
    # Main application proxy to Streamlit
    location / {
        # Specific rate limiting for main app
        limit_req zone=general burst=10 nodelay;
        
        # Proxy to Streamlit application
        proxy_pass http://127.0.0.1:$APP_PORT;
        proxy_http_version 1.1;
        
        # WebSocket and HTTP upgrade headers
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Standard proxy headers
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$server_name;
        proxy_set_header X-Forwarded-Port \$server_port;
        
        # Streamlit specific optimizations
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
        
        # Custom headers for DataGuardian Pro
        proxy_set_header X-DataGuardian-Version "1.0";
        proxy_set_header X-Compliance-Platform "Netherlands-UAVG";
    }
    
    # Login endpoint with enhanced security
    location /login {
        limit_req zone=login burst=5 nodelay;
        
        # Additional security for login
        add_header X-Content-Type-Options nosniff always;
        add_header X-Frame-Options DENY always;
        
        proxy_pass http://127.0.0.1:$APP_PORT/login;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Login specific timeouts
        proxy_read_timeout 30s;
        proxy_send_timeout 30s;
    }
    
    # API endpoints with higher rate limits
    location /api/ {
        limit_req zone=api burst=50 nodelay;
        
        proxy_pass http://127.0.0.1:$APP_PORT/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # API specific settings
        proxy_read_timeout 120s;
        proxy_send_timeout 120s;
    }
    
    # Health check endpoint (minimal processing)
    location /health {
        access_log off;
        
        proxy_pass http://127.0.0.1:$APP_PORT/health;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_connect_timeout 5s;
        proxy_read_timeout 5s;
        proxy_send_timeout 5s;
    }
    
    # Static files with long-term caching
    location /static/ {
        alias $DATAGUARDIAN_DIR/static/;
        expires 30d;
        add_header Cache-Control "public, no-transform, immutable";
        add_header Vary "Accept-Encoding";
        access_log off;
        
        # Compression for static files
        gzip_static on;
        
        # Security for static files
        location ~* \.(js|css)$ {
            add_header Content-Security-Policy "default-src 'self'";
        }
    }
    
    # Favicon handling
    location /favicon.ico {
        alias $DATAGUARDIAN_DIR/static/favicon.ico;
        expires 30d;
        access_log off;
        log_not_found off;
    }
    
    # Robots.txt with proper content type
    location /robots.txt {
        access_log off;
        log_not_found off;
        add_header Content-Type text/plain;
        return 200 "User-agent: *\nDisallow: /admin/\nDisallow: /settings/\nDisallow: /api/\nAllow: /\n\nSitemap: https://$DOMAIN/sitemap.xml\n";
    }
    
    # Security: Block access to hidden files and sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    location ~ \.(py|pyc|pyo|env|log|conf)$ {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    # Error pages
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
    
    location = /404.html {
        root /var/www/html;
        internal;
    }
    
    location = /50x.html {
        root /var/www/html;
        internal;
    }
}
EOF

    echo "✅ HTTPS Nginx configuration created"
    
    # Test the configuration
    echo "🧪 Testing HTTPS Nginx configuration..."
    if nginx -t >/dev/null 2>&1; then
        echo "✅ HTTPS Nginx configuration: VALID"
        return 0
    else
        echo "❌ HTTPS Nginx configuration: INVALID"
        echo "🔍 Nginx test output:"
        nginx -t
        return 1
    fi
}

# =============================================================================
# FAILURE CASE 3: PORT 443 NOT LISTENING ISSUE
# =============================================================================

fix_port_443_listening() {
    echo ""
    echo "🔌 FAILURE CASE 3: PORT 443 NOT LISTENING"
    echo "========================================"
    
    echo "🔍 Checking port 443 status..."
    
    if netstat -tlnp | grep :443 >/dev/null 2>&1; then
        echo "✅ Port 443 already listening"
        return 0
    fi
    
    echo "⚠️  Port 443 not listening - fixing..."
    
    # Check if nginx is running
    if ! systemctl is-active --quiet nginx; then
        echo "🔧 Starting Nginx service..."
        systemctl start nginx
        sleep 5
    fi
    
    # Check if SSL configuration is loaded
    if nginx -T 2>/dev/null | grep -q "listen.*443.*ssl"; then
        echo "✅ SSL configuration detected in Nginx"
    else
        echo "❌ No SSL configuration found in Nginx"
        return 1
    fi
    
    # Restart nginx to ensure SSL binding
    echo "🔄 Restarting Nginx to bind SSL port..."
    systemctl restart nginx
    sleep 10
    
    # Check port 443 again
    if netstat -tlnp | grep :443 >/dev/null 2>&1; then
        echo "✅ Port 443 now listening"
        return 0
    else
        echo "❌ Port 443 still not listening"
        echo "🔍 Nginx error log:"
        tail -20 /var/log/nginx/error.log 2>/dev/null || echo "No error log found"
        return 1
    fi
}

# =============================================================================
# FAILURE CASE 4: HTTPS RESPONSE CODE 000 ISSUE
# =============================================================================

fix_https_response_000() {
    echo ""
    echo "🌐 FAILURE CASE 4: HTTPS RESPONSE CODE 000"
    echo "========================================"
    
    echo "🧪 Testing HTTPS connectivity..."
    
    # Test local HTTPS first
    local_https=$(curl -s -o /dev/null -w "%{http_code}" -k https://localhost 2>/dev/null || echo "000")
    echo "📊 Local HTTPS (localhost): $local_https"
    
    # Test domain HTTPS
    domain_https=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN 2>/dev/null || echo "000")
    echo "📊 Domain HTTPS ($DOMAIN): $domain_https"
    
    if [ "$domain_https" = "000" ]; then
        echo "⚠️  HTTPS returning 000 - diagnosing issue..."
        
        # Check if it's a DNS issue
        if ! nslookup $DOMAIN >/dev/null 2>&1; then
            echo "❌ DNS resolution failed"
            return 1
        fi
        
        # Check if it's a firewall issue
        if command -v ufw >/dev/null 2>&1; then
            if ufw status | grep -q "443"; then
                echo "✅ Firewall allows port 443"
            else
                echo "🔧 Opening port 443 in firewall..."
                ufw allow 443/tcp >/dev/null 2>&1
                ufw reload >/dev/null 2>&1
            fi
        fi
        
        # Check SSL certificate validity
        echo "🔍 Checking SSL certificate validity..."
        if openssl x509 -in /etc/letsencrypt/live/$DOMAIN/cert.pem -text -noout | grep -q "$DOMAIN"; then
            echo "✅ SSL certificate valid for domain"
        else
            echo "❌ SSL certificate invalid"
            return 1
        fi
        
        # Test with verbose curl for debugging
        echo "🔍 Detailed HTTPS test:"
        timeout 10 curl -v https://$DOMAIN 2>&1 | head -10 || echo "Connection timeout"
        
        return 1
    else
        echo "✅ HTTPS responding with code: $domain_https"
        return 0
    fi
}

# =============================================================================
# FAILURE CASE 5: COMPREHENSIVE SSL/HTTPS RESTART
# =============================================================================

comprehensive_ssl_restart() {
    echo ""
    echo "🔄 FAILURE CASE 5: COMPREHENSIVE SSL/HTTPS RESTART"
    echo "==============================================="
    
    echo "🛑 Stopping all services for complete restart..."
    
    # Stop services
    systemctl stop nginx
    systemctl stop dataguardian
    
    # Clear any nginx processes
    pkill -f nginx || true
    sleep 5
    
    # Start services in correct order
    echo "▶️  Starting DataGuardian service..."
    systemctl start dataguardian
    sleep 10
    
    # Verify DataGuardian is responding
    local_app_check=0
    for i in {1..6}; do
        if curl -s http://localhost:$APP_PORT >/dev/null 2>&1; then
            echo "✅ DataGuardian responding on port $APP_PORT"
            local_app_check=1
            break
        else
            echo "⏳ Waiting for DataGuardian... (attempt $i/6)"
            sleep 10
        fi
    done
    
    if [ $local_app_check -eq 0 ]; then
        echo "❌ DataGuardian failed to start properly"
        return 1
    fi
    
    echo "▶️  Starting Nginx with SSL configuration..."
    systemctl start nginx
    sleep 10
    
    # Check if nginx started successfully
    if systemctl is-active --quiet nginx; then
        echo "✅ Nginx started successfully"
    else
        echo "❌ Nginx failed to start"
        echo "🔍 Nginx status:"
        systemctl status nginx --no-pager -l | head -10
        return 1
    fi
    
    # Verify both HTTP and HTTPS
    sleep 5
    
    http_check=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN 2>/dev/null || echo "000")
    https_check=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN 2>/dev/null || echo "000")
    
    echo "📊 Final connectivity check:"
    echo "   HTTP: $http_check"
    echo "   HTTPS: $https_check"
    
    if [ "$https_check" = "200" ]; then
        echo "✅ HTTPS fully operational"
        return 0
    else
        echo "⚠️  HTTPS still not fully operational"
        return 1
    fi
}

# =============================================================================
# MAIN EXECUTION FLOW FOR FAILURE RECOVERY
# =============================================================================

echo "🔍 ANALYZING FAILURE PATTERNS..."
echo "=============================="

# Run failure case fixes in order
failure_count=0
success_count=0

echo ""
echo "🔧 EXECUTING FAILURE CASE FIXES..."
echo "================================="

# Fix 1: SSL Certificate Expansion
echo ""
echo "🔧 FIX 1: SSL Certificate Expansion..."
if fix_ssl_certificate_expansion; then
    echo "✅ FIX 1: SUCCESS"
    ((success_count++))
else
    echo "❌ FIX 1: FAILED"
    ((failure_count++))
fi

# Fix 2: HTTPS Nginx Configuration
echo ""
echo "🔧 FIX 2: HTTPS Nginx Configuration..."
if fix_https_nginx_configuration; then
    echo "✅ FIX 2: SUCCESS"
    ((success_count++))
else
    echo "❌ FIX 2: FAILED"
    ((failure_count++))
fi

# Fix 3: Port 443 Listening
echo ""
echo "🔧 FIX 3: Port 443 Listening..."
if fix_port_443_listening; then
    echo "✅ FIX 3: SUCCESS"
    ((success_count++))
else
    echo "❌ FIX 3: FAILED"
    ((failure_count++))
fi

# Fix 4: HTTPS Response 000
echo ""
echo "🔧 FIX 4: HTTPS Response Code..."
if fix_https_response_000; then
    echo "✅ FIX 4: SUCCESS"
    ((success_count++))
else
    echo "❌ FIX 4: FAILED"
    ((failure_count++))
fi

# Fix 5: Comprehensive Restart (if previous fixes didn't work)
if [ $failure_count -gt 0 ]; then
    echo ""
    echo "🔧 FIX 5: Comprehensive SSL/HTTPS Restart..."
    if comprehensive_ssl_restart; then
        echo "✅ FIX 5: SUCCESS"
        ((success_count++))
    else
        echo "❌ FIX 5: FAILED"
        ((failure_count++))
    fi
fi

# =============================================================================
# FINAL VERIFICATION AND REPORTING
# =============================================================================

echo ""
echo "🧪 FINAL VERIFICATION TESTS"
echo "=========================="

# Test all connectivity types
echo "🔍 Running post-fix verification..."

http_final=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN 2>/dev/null || echo "000")
https_final=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN 2>/dev/null || echo "000")
www_https_final=$(curl -s -o /dev/null -w "%{http_code}" https://www.$DOMAIN 2>/dev/null || echo "000")
port_443_status="CLOSED"

if netstat -tlnp | grep :443 >/dev/null 2>&1; then
    port_443_status="LISTENING"
fi

echo ""
echo "📊 FINAL TEST RESULTS:"
echo "====================="
echo "   HTTP ($DOMAIN): $http_final"
echo "   HTTPS ($DOMAIN): $https_final"
echo "   HTTPS (www.$DOMAIN): $www_https_final"
echo "   Port 443: $port_443_status"

# Determine overall success
overall_success=false

if [ "$https_final" = "200" ] && [ "$www_https_final" = "200" ] && [ "$port_443_status" = "LISTENING" ]; then
    overall_success=true
fi

echo ""
echo "📋 FAILURE RECOVERY SUMMARY"
echo "=========================="
echo "   Fixes attempted: $((success_count + failure_count))"
echo "   Fixes successful: $success_count"
echo "   Fixes failed: $failure_count"

if [ "$overall_success" = true ]; then
    echo ""
    echo "🎉🎉🎉 FAILURE RECOVERY: COMPLETE SUCCESS! 🎉🎉🎉"
    echo "==============================================="
    echo ""
    echo "✅ ALL SSL/HTTPS ISSUES RESOLVED!"
    echo "✅ Certificate expansion: Working"
    echo "✅ HTTPS configuration: Working"
    echo "✅ Port 443: Listening"
    echo "✅ HTTPS connectivity: Working"
    echo ""
    echo "🌐 YOUR PLATFORM IS NOW FULLY OPERATIONAL:"
    echo "   📍 HTTPS: https://$DOMAIN"
    echo "   📍 HTTPS WWW: https://www.$DOMAIN"
    echo "   📍 HTTP: Redirects to HTTPS"
    echo ""
    echo "🚀 DataGuardian Pro is ready for production!"
    echo "Your €25K MRR Netherlands compliance platform is LIVE with HTTPS!"
else
    echo ""
    echo "⚠️  FAILURE RECOVERY: PARTIAL SUCCESS"
    echo "==================================="
    echo ""
    echo "✅ Some issues were resolved"
    echo "⚠️  HTTPS may still need manual intervention"
    echo ""
    echo "🔧 MANUAL STEPS TO TRY:"
    echo "   1. Check certbot status: certbot certificates"
    echo "   2. Manual certificate renewal: certbot renew --force-renewal"
    echo "   3. Nginx configuration test: nginx -t"
    echo "   4. Service restart: systemctl restart nginx dataguardian"
    echo "   5. Firewall check: ufw status"
    echo ""
    echo "📞 IF STILL FAILING:"
    echo "   1. Check DNS propagation globally"
    echo "   2. Verify domain registrar settings"
    echo "   3. Consider using Cloudflare SSL proxy"
fi

echo ""
echo "🎯 QUICK ACCESS COMMANDS:"
echo "========================"
echo "   🔍 Test HTTPS: curl -I https://$DOMAIN"
echo "   📊 Check services: systemctl status nginx dataguardian"
echo "   📄 View logs: journalctl -u nginx -f"
echo "   🔄 Restart all: systemctl restart nginx dataguardian"

echo ""
echo "✅ SSL/HTTPS FAILURE RECOVERY COMPLETED!"
echo "Check the results above and test your platform access"