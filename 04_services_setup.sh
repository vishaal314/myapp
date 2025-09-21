#!/bin/bash
# DataGuardian Pro - Step 4: Services Setup
# Configures PostgreSQL, Redis, and system services

set -e  # Exit on any error

echo "⚙️ DataGuardian Pro - Services Setup (Step 4/5)"
echo "==============================================="
echo "Configuring PostgreSQL, Redis, and system services"
echo ""

# Function to log messages with timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root (use sudo)"
    exit 1
fi

log "Starting services setup..."

# Configure PostgreSQL
log "Configuring PostgreSQL database..."

# Start and enable PostgreSQL
systemctl start postgresql
systemctl enable postgresql

# Wait for PostgreSQL to be ready
sleep 5

# Create database and user
log "Creating DataGuardian database and user..."
sudo -u postgres psql << 'PSQL_SETUP_EOF'
-- Drop existing database and user if they exist
DROP DATABASE IF EXISTS dataguardian_pro;
DROP USER IF EXISTS dataguardian;

-- Create database
CREATE DATABASE dataguardian_pro;

-- Create user with secure password
CREATE USER dataguardian WITH ENCRYPTED PASSWORD 'DataGuardianSecure2025!';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE dataguardian_pro TO dataguardian;
ALTER USER dataguardian CREATEDB;

-- Set connection limit
ALTER USER dataguardian CONNECTION LIMIT 100;

\q
PSQL_SETUP_EOF

log "✅ PostgreSQL database configured"

# Configure Redis
log "Configuring Redis server..."

# Create Redis configuration
cat > /etc/redis/redis.conf.dataguardian << 'REDIS_CONFIG_EOF'
# DataGuardian Pro Redis Configuration
bind 127.0.0.1
port 6379
timeout 0
keepalive 300

# Memory management
maxmemory 256mb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000

# Security
protected-mode yes
requirepass DataGuardianRedis2025!

# Logging
loglevel notice
logfile /var/log/redis/redis-server.log

# Performance
tcp-backlog 511
databases 16
REDIS_CONFIG_EOF

# Backup original Redis config and use our config
cp /etc/redis/redis.conf /etc/redis/redis.conf.backup
cp /etc/redis/redis.conf.dataguardian /etc/redis/redis.conf

# Start and enable Redis
systemctl start redis-server
systemctl enable redis-server

# Wait for Redis to be ready
sleep 3

log "✅ Redis server configured"

# Create DataGuardian systemd service
log "Creating DataGuardian systemd service..."
cat > /etc/systemd/system/dataguardian.service << 'SYSTEMD_SERVICE_EOF'
[Unit]
Description=DataGuardian Pro - Enterprise Privacy Compliance Platform
Documentation=https://dataguardianpro.nl
After=network.target postgresql.service redis-server.service
Requires=postgresql.service redis-server.service
StartLimitIntervalSec=60
StartLimitBurst=3

[Service]
Type=simple
User=dataguardian
Group=dataguardian
WorkingDirectory=/opt/dataguardian
Environment=PATH=/opt/dataguardian/venv/bin
Environment=PYTHONPATH=/opt/dataguardian
Environment=PYTHONUNBUFFERED=1

# Environment variables
Environment=DATAGUARDIAN_MASTER_KEY=DataGuardianProSafeModeKey123456
Environment=DATABASE_URL=postgresql://dataguardian:DataGuardianSecure2025!@localhost/dataguardian_pro
Environment=REDIS_URL=redis://:DataGuardianRedis2025!@localhost:6379/0
Environment=ENVIRONMENT=production
Environment=SECRET_KEY=DataGuardianProSecretKey2025VerySecure
Environment=APP_NAME=DataGuardian Pro
Environment=APP_VERSION=1.0.0
Environment=APP_DOMAIN=dataguardianpro.nl

# Streamlit command
ExecStart=/opt/dataguardian/venv/bin/streamlit run app.py --server.port 5000 --server.address 0.0.0.0 --server.headless true
ExecReload=/bin/kill -HUP $MAINPID

# Restart configuration
Restart=always
RestartSec=10
KillMode=mixed
TimeoutStopSec=30

# Output to journal
StandardOutput=journal
StandardError=journal
SyslogIdentifier=dataguardian

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/dataguardian /var/log/dataguardian /tmp

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
SYSTEMD_SERVICE_EOF

log "✅ DataGuardian systemd service created"

# Configure Nginx
log "Configuring Nginx web server..."

# Create Nginx site configuration
cat > /etc/nginx/sites-available/dataguardian << 'NGINX_CONFIG_EOF'
server {
    listen 80;
    listen [::]:80;
    server_name dataguardianpro.nl www.dataguardianpro.nl;

    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=dataguardian:10m rate=10r/s;
    limit_req zone=dataguardian burst=20 nodelay;

    # Client settings
    client_max_body_size 100M;
    client_body_timeout 60s;
    client_header_timeout 60s;

    # Main application
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;

        # WebSocket support for Streamlit
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffering
        proxy_buffering on;
        proxy_buffer_size 8k;
        proxy_buffers 8 8k;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:5000/?health=check;
        access_log off;
        
        # Quick health check timeouts
        proxy_connect_timeout 5s;
        proxy_send_timeout 5s;
        proxy_read_timeout 5s;
    }

    # Static files (if any)
    location /static/ {
        alias /opt/dataguardian/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Robots.txt
    location /robots.txt {
        add_header Content-Type text/plain;
        return 200 "User-agent: *\nDisallow: /\n";
    }

    # Security.txt
    location /.well-known/security.txt {
        add_header Content-Type text/plain;
        return 200 "Contact: security@dataguardianpro.nl\nExpires: 2025-12-31T23:59:59.000Z\n";
    }

    # Block sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    location ~ \.(env|git|svn|htaccess|htpasswd)$ {
        deny all;
        access_log off;
        log_not_found off;
    }
}

# SSL redirect (will be configured in final step)
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name dataguardianpro.nl www.dataguardianpro.nl;

    # SSL configuration will be added by certbot
    # ssl_certificate /etc/letsencrypt/live/dataguardianpro.nl/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/dataguardianpro.nl/privkey.pem;

    # Include SSL security settings
    include /etc/nginx/snippets/ssl-params.conf;

    # Same configuration as HTTP but with HTTPS headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    
    # All other directives same as HTTP block above
    # (Will be completed in final configuration step)
}
NGINX_CONFIG_EOF

# Create SSL security snippet
cat > /etc/nginx/snippets/ssl-params.conf << 'SSL_PARAMS_EOF'
# SSL Security Configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers on;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
ssl_ecdh_curve secp384r1;
ssl_session_timeout 10m;
ssl_session_cache shared:SSL:10m;
ssl_session_tickets off;
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;
SSL_PARAMS_EOF

# Enable site (disable default)
ln -sf /etc/nginx/sites-available/dataguardian /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Start and enable Nginx
systemctl enable nginx
systemctl start nginx

log "✅ Nginx web server configured"

# Configure logging
log "Configuring logging..."

# Create log directories
mkdir -p /var/log/dataguardian
chown dataguardian:dataguardian /var/log/dataguardian

# Create logrotate configuration
cat > /etc/logrotate.d/dataguardian << 'LOGROTATE_CONFIG_EOF'
/var/log/dataguardian/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 dataguardian dataguardian
    sharedscripts
    postrotate
        systemctl reload dataguardian
    endscript
}
LOGROTATE_CONFIG_EOF

log "✅ Logging configured"

# Create environment file
log "Creating environment configuration..."
cat > /opt/dataguardian/.env << 'ENV_CONFIG_EOF'
# DataGuardian Pro Environment Configuration
ENVIRONMENT=production
SECRET_KEY=DataGuardianProSecretKey2025VerySecure
DATAGUARDIAN_MASTER_KEY=DataGuardianProSafeModeKey123456
DATABASE_URL=postgresql://dataguardian:DataGuardianSecure2025!@localhost/dataguardian_pro
REDIS_URL=redis://:DataGuardianRedis2025!@localhost:6379/0

# Application Settings
APP_NAME=DataGuardian Pro
APP_VERSION=1.0.0
APP_DOMAIN=dataguardianpro.nl
APP_URL=https://dataguardianpro.nl

# Security Settings
SESSION_TIMEOUT=3600
BCRYPT_ROUNDS=12
JWT_EXPIRY=86400

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/dataguardian/app.log

# Feature Flags
ENABLE_ANALYTICS=true
ENABLE_NOTIFICATIONS=true
ENABLE_AUTO_BACKUP=true

# Netherlands Specific
LOCALE=nl_NL
TIMEZONE=Europe/Amsterdam
GDPR_CONTACT=dpo@dataguardianpro.nl
ENV_CONFIG_EOF

# Set proper permissions for environment file
chown dataguardian:dataguardian /opt/dataguardian/.env
chmod 600 /opt/dataguardian/.env

log "✅ Environment configuration created"

# Reload systemd and enable services
log "Enabling services..."
systemctl daemon-reload
systemctl enable dataguardian

log "✅ Services setup completed successfully!"
log ""
log "📋 Services configuration summary:"
log "   - PostgreSQL: Database 'dataguardian_pro' created"
log "   - Redis: Configured with authentication and persistence"
log "   - DataGuardian: Systemd service created and enabled"
log "   - Nginx: Web server configured with security headers"
log "   - Logging: Logrotate configured for log management"
log "   - Environment: Production configuration created"
log ""
log "🔥 Next step: Run 05_final_config.sh"
echo "==============================================="