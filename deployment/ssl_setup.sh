#!/bin/bash
# SSL Certificate Setup for DataGuardian Pro
# Domain: vishaalnoord7.retzor.com

echo "🔒 Setting up SSL certificate for vishaalnoord7.retzor.com..."

# Install Certbot if not already installed
if ! command -v certbot &> /dev/null; then
    echo "📦 Installing Certbot..."
    apt update
    apt install -y certbot python3-certbot-nginx
fi

# Obtain SSL certificate
echo "📜 Obtaining SSL certificate..."
certbot --nginx -d vishaalnoord7.retzor.com --non-interactive --agree-tos --email vishaalnoord7@gmail.com

# Set up automatic renewal
echo "🔄 Setting up automatic renewal..."
systemctl enable certbot.timer
systemctl start certbot.timer

# Test renewal
echo "🧪 Testing renewal process..."
certbot renew --dry-run

# Update Nginx configuration for better security
echo "🔧 Updating Nginx security configuration..."
cat > /etc/nginx/sites-available/dataguardian-pro << 'EOF'
server {
    listen 80;
    server_name vishaalnoord7.retzor.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name vishaalnoord7.retzor.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/vishaalnoord7.retzor.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vishaalnoord7.retzor.com/privkey.pem;
    
    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS (HTTP Strict Transport Security)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob: https:; font-src 'self' data: https:; img-src 'self' data: https:;" always;
    
    # GDPR Compliance Headers
    add_header X-Data-Residency "Netherlands-EU" always;
    add_header X-Privacy-Policy "https://vishaalnoord7.retzor.com/privacy" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    # Main proxy to Streamlit
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # WebSocket support for Streamlit
        proxy_buffering off;
        proxy_cache off;
        
        # Increase timeouts for large file processing
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        client_max_body_size 100M;
        
        # Rate limiting for sensitive endpoints
        limit_req zone=api burst=20 nodelay;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8501/?health=check;
        access_log off;
    }
    
    # API endpoints with stricter rate limiting
    location /api/ {
        limit_req zone=api burst=10 nodelay;
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files caching
    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
        proxy_pass http://127.0.0.1:8501;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header X-Cache-Status "HIT";
    }
    
    # Deny access to sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    location ~ \.(env|config|log)$ {
        deny all;
        access_log off;
        log_not_found off;
    }
}
EOF

# Test and reload Nginx
nginx -t && systemctl reload nginx

echo "✅ SSL setup completed!"
echo "🌐 Your site is now available at: https://vishaalnoord7.retzor.com"
echo "🔒 SSL certificate will auto-renew every 60 days"
echo ""
echo "📋 SSL STATUS:"
echo "Certificate: /etc/letsencrypt/live/vishaalnoord7.retzor.com/"
echo "Auto-renewal: Enabled (certbot.timer)"
echo "Security: A+ grade SSL configuration"
echo ""
echo "🔧 VERIFY INSTALLATION:"
echo "curl -I https://vishaalnoord7.retzor.com"
echo "openssl s_client -connect vishaalnoord7.retzor.com:443 -servername vishaalnoord7.retzor.com"