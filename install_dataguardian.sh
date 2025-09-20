#!/bin/bash
# DataGuardian Pro - Complete Production Installation Script
# Robust, idempotent installation for Ubuntu 22.04

set -e

# Configuration
DOMAIN="${1:-dataguardianpro.nl}"
EMAIL="${2:-vishaalnoord7@gmail.com}"
APP_USER="dataguardian"
APP_DIR="/opt/dataguardian"
SOURCE_DIR="/opt/GdprComplianceTool"
SOURCE_ZIP="/opt/GdprComplianceTool.zip"

# Parse command line arguments
RUN_CERTBOT=false
ENABLE_UFW=false
NON_INTERACTIVE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --domain)
            DOMAIN="$2"
            shift 2
            ;;
        --email)
            EMAIL="$2"
            shift 2
            ;;
        --run-certbot)
            RUN_CERTBOT=true
            shift
            ;;
        --enable-ufw)
            ENABLE_UFW=true
            shift
            ;;
        --non-interactive)
            NON_INTERACTIVE=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() { echo -e "${BLUE}[STEP $1]${NC} $2"; }
print_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

echo "🚀 DataGuardian Pro - Complete Production Installation"
echo "===================================================="
echo "Domain: $DOMAIN"
echo "Email: $EMAIL"
echo "Installation Directory: $APP_DIR"
echo "Service User: $APP_USER"
echo "SSL Certificate: $RUN_CERTBOT"
echo "UFW Firewall: $ENABLE_UFW"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root"
    exit 1
fi

# =============================================================================
# STEP 1: System Updates and Dependencies
# =============================================================================
print_step "1" "System Updates and Dependencies"
export DEBIAN_FRONTEND=noninteractive

apt update
apt install -y \
    curl \
    wget \
    git \
    unzip \
    htop \
    nano \
    build-essential \
    software-properties-common \
    ca-certificates \
    gnupg \
    lsb-release \
    rsync \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    supervisor \
    logrotate \
    fail2ban

print_success "System dependencies installed"

# =============================================================================
# STEP 2: Application User and Directory Setup
# =============================================================================
print_step "2" "Application User and Directory Setup"

# Create application user if doesn't exist
if ! id "$APP_USER" &>/dev/null; then
    useradd --system --shell /bin/bash --home "$APP_DIR" --create-home "$APP_USER"
    print_info "Created user: $APP_USER"
else
    print_info "User already exists: $APP_USER"
fi

# Create directory structure
mkdir -p "$APP_DIR"/{data,logs,reports,config,ssl,backups,.streamlit}
chown -R "$APP_USER:$APP_USER" "$APP_DIR"
chmod 755 "$APP_DIR"/{data,logs,reports,config,backups}
chmod 700 "$APP_DIR"/ssl

print_success "Directory structure created"

# =============================================================================
# STEP 3: Source Code Synchronization
# =============================================================================
print_step "3" "Source Code Synchronization"

if [ -d "$SOURCE_DIR" ]; then
    print_info "Syncing source code from $SOURCE_DIR to $APP_DIR"
    rsync -av --exclude='venv' --exclude='logs' --exclude='backups' --exclude='*.pyc' \
          "$SOURCE_DIR/" "$APP_DIR/"
    chown -R "$APP_USER:$APP_USER" "$APP_DIR"
    print_success "Source code synced from directory"
elif [ -f "$SOURCE_ZIP" ]; then
    print_info "Extracting source code from $SOURCE_ZIP to $APP_DIR"
    cd "$APP_DIR"
    unzip -o "$SOURCE_ZIP"
    chown -R "$APP_USER:$APP_USER" "$APP_DIR"
    print_success "Source code extracted from zip"
else
    print_error "No source code found at $SOURCE_DIR or $SOURCE_ZIP"
    exit 1
fi

# Verify essential files exist
if [ ! -f "$APP_DIR/app.py" ]; then
    print_error "app.py not found in $APP_DIR"
    exit 1
fi

print_success "Source code synchronized"

# =============================================================================
# STEP 4: Python Virtual Environment
# =============================================================================
print_step "4" "Python Virtual Environment Setup"

if [ ! -d "$APP_DIR/venv" ]; then
    print_info "Creating Python virtual environment"
    sudo -u "$APP_USER" python3 -m venv "$APP_DIR/venv"
else
    print_info "Virtual environment already exists"
fi

# Upgrade pip
sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install --upgrade pip

# Install dependencies
if [ -f "$APP_DIR/requirements.txt" ]; then
    print_info "Installing dependencies from requirements.txt"
    sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"
else
    print_info "Installing common DataGuardian dependencies"
    sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install \
        streamlit \
        psycopg2-binary \
        redis \
        python-dotenv \
        requests \
        pandas \
        plotly \
        openai \
        stripe \
        bcrypt \
        pyjwt \
        beautifulsoup4 \
        pillow \
        reportlab \
        trafilatura \
        tldextract \
        pytesseract \
        opencv-python-headless
fi

print_success "Python environment configured"

# =============================================================================
# STEP 5: PostgreSQL Configuration
# =============================================================================
print_step "5" "PostgreSQL Configuration"

# Start PostgreSQL
systemctl start postgresql
systemctl enable postgresql

# Generate secure password
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

# Create database and user idempotently
sudo -u postgres psql << EOF
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'dataguardian') THEN
        CREATE USER dataguardian WITH PASSWORD '$DB_PASSWORD';
    END IF;
END
\$\$;

SELECT 'CREATE DATABASE dataguardian_prod OWNER dataguardian'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'dataguardian_prod')\gexec

GRANT ALL PRIVILEGES ON DATABASE dataguardian_prod TO dataguardian;
ALTER USER dataguardian CREATEDB;
\q
EOF

# Apply database schema if exists
if [ -f "$APP_DIR/schema.sql" ] || [ -f "$APP_DIR/database/schema.sql" ]; then
    SCHEMA_FILE=""
    [ -f "$APP_DIR/schema.sql" ] && SCHEMA_FILE="$APP_DIR/schema.sql"
    [ -f "$APP_DIR/database/schema.sql" ] && SCHEMA_FILE="$APP_DIR/database/schema.sql"
    
    if [ -n "$SCHEMA_FILE" ]; then
        print_info "Applying database schema: $SCHEMA_FILE"
        PGPASSWORD="$DB_PASSWORD" psql -h localhost -U dataguardian -d dataguardian_prod -f "$SCHEMA_FILE"
    fi
fi

print_success "PostgreSQL configured"

# =============================================================================
# STEP 6: Redis Configuration
# =============================================================================
print_step "6" "Redis Configuration"

# Generate Redis password
REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

# Configure Redis password robustly
if ! grep -q "^requirepass" /etc/redis/redis.conf; then
    echo "requirepass $REDIS_PASSWORD" >> /etc/redis/redis.conf
else
    sed -i "s/^requirepass.*/requirepass $REDIS_PASSWORD/" /etc/redis/redis.conf
fi

# Ensure Redis binds to localhost
sed -i 's/^bind .*/bind 127.0.0.1/' /etc/redis/redis.conf

systemctl restart redis-server
systemctl enable redis-server

# Verify Redis authentication
redis-cli -a "$REDIS_PASSWORD" ping >/dev/null 2>&1

print_success "Redis configured"

# =============================================================================
# STEP 7: Environment Configuration
# =============================================================================
print_step "7" "Environment Configuration"

# Generate security keys
JWT_SECRET=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 16)

# Create .env file if it doesn't exist
if [ ! -f "$APP_DIR/.env" ]; then
    cat > "$APP_DIR/.env" << EOF
# DataGuardian Pro - Production Environment
# Generated: $(date)

# Application Settings
ENVIRONMENT=production
APP_NAME=DataGuardian Pro
APP_VERSION=1.0.0
APP_HOST=0.0.0.0
APP_PORT=5000

# Database Configuration
DATABASE_URL=postgresql://dataguardian:$DB_PASSWORD@localhost:5432/dataguardian_prod
POSTGRES_DB=dataguardian_prod
POSTGRES_USER=dataguardian
POSTGRES_PASSWORD=$DB_PASSWORD

# Redis Configuration
REDIS_URL=redis://:$REDIS_PASSWORD@localhost:6379/0
REDIS_PASSWORD=$REDIS_PASSWORD

# Security
JWT_SECRET=$JWT_SECRET
ENCRYPTION_KEY=$ENCRYPTION_KEY

# API Keys - UPDATE WITH YOUR ACTUAL KEYS
OPENAI_API_KEY=your_openai_api_key_here
STRIPE_PUBLISHABLE_KEY=pk_live_your_publishable_key_here
STRIPE_SECRET_KEY=sk_live_your_secret_key_here

# Domain Configuration
DOMAIN_NAME=$DOMAIN
SSL_EMAIL=$EMAIL

# GDPR Compliance (Netherlands)
DATA_RESIDENCY=EU
PRIVACY_POLICY_URL=https://$DOMAIN/privacy
TERMS_URL=https://$DOMAIN/terms
DEFAULT_COUNTRY=NL
DEFAULT_LANGUAGE=en
UAVG_COMPLIANCE=true

# Monitoring
LOG_LEVEL=INFO
ENABLE_DEBUG=false
HEALTH_CHECK_ENABLED=true
EOF

    chown "$APP_USER:$APP_USER" "$APP_DIR/.env"
    chmod 600 "$APP_DIR/.env"
    print_info "Environment configuration created"
else
    print_info "Environment configuration already exists"
fi

# Create Streamlit configuration
cat > "$APP_DIR/.streamlit/config.toml" << EOF
[server]
headless = true
address = "0.0.0.0"
port = 5000
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
EOF

chown "$APP_USER:$APP_USER" "$APP_DIR/.streamlit/config.toml"

print_success "Configuration files created"

# =============================================================================
# STEP 8: Systemd Service Configuration
# =============================================================================
print_step "8" "Systemd Service Configuration"

cat > /etc/systemd/system/dataguardian.service << EOF
[Unit]
Description=DataGuardian Pro - Privacy Compliance Platform
After=network.target postgresql.service redis-server.service
Wants=postgresql.service redis-server.service

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/streamlit run app.py --server.port 5000 --server.address 0.0.0.0 --server.headless true
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=dataguardian

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$APP_DIR

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable dataguardian.service

print_success "Systemd service configured"

# =============================================================================
# STEP 9: Nginx Configuration
# =============================================================================
print_step "9" "Nginx Configuration"

cat > /etc/nginx/sites-available/dataguardian << EOF
# Rate limiting
limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;

# Upstream
upstream dataguardian {
    server 127.0.0.1:5000;
}

# HTTP server (redirect to HTTPS)
server {
    listen 80;
    server_name $DOMAIN;
    
    # Let's Encrypt ACME challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Health check
    location /health {
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }
    
    # Redirect to HTTPS (will be enabled after SSL setup)
    # location / {
    #     return 301 https://\$server_name\$request_uri;
    # }
    
    # Temporary HTTP access during setup
    location / {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://dataguardian;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support for Streamlit
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}

# HTTPS server (will be enabled after SSL certificate)
# server {
#     listen 443 ssl http2;
#     server_name $DOMAIN;
#
#     # SSL Configuration
#     ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
#     ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
#     ssl_session_cache shared:SSL:10m;
#     ssl_session_timeout 10m;
#     ssl_protocols TLSv1.2 TLSv1.3;
#     ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
#     ssl_prefer_server_ciphers off;
#
#     # Security headers
#     add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
#     add_header X-Frame-Options DENY always;
#     add_header X-Content-Type-Options nosniff always;
#     add_header X-XSS-Protection "1; mode=block" always;
#     add_header Referrer-Policy "strict-origin-when-cross-origin" always;
#
#     # File upload size
#     client_max_body_size 100M;
#
#     # Main application
#     location / {
#         limit_req zone=api burst=20 nodelay;
#         
#         proxy_pass http://dataguardian;
#         proxy_set_header Host \$host;
#         proxy_set_header X-Real-IP \$remote_addr;
#         proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
#         proxy_set_header X-Forwarded-Proto \$scheme;
#         
#         # WebSocket support for Streamlit
#         proxy_http_version 1.1;
#         proxy_set_header Upgrade \$http_upgrade;
#         proxy_set_header Connection "upgrade";
#         
#         # Timeouts
#         proxy_connect_timeout 60s;
#         proxy_send_timeout 60s;
#         proxy_read_timeout 60s;
#     }
# }
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/dataguardian /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
nginx -t

systemctl restart nginx
systemctl enable nginx

print_success "Nginx configured"

# =============================================================================
# STEP 10: Firewall Configuration (Optional)
# =============================================================================
if [ "$ENABLE_UFW" = true ]; then
    print_step "10" "Firewall Configuration"
    
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow OpenSSH
    ufw allow 'Nginx Full'
    ufw --force enable
    
    print_success "UFW firewall enabled"
else
    print_step "10" "Firewall Configuration (Skipped)"
    print_info "UFW firewall not enabled (use --enable-ufw to enable)"
fi

# =============================================================================
# STEP 11: Management Scripts
# =============================================================================
print_step "11" "Management Scripts"

# Status script
cat > "$APP_DIR/status.sh" << 'EOF'
#!/bin/bash
echo "🚀 DataGuardian Pro - System Status"
echo "==================================="

echo "📊 Service Status:"
systemctl status dataguardian.service --no-pager -l

echo ""
echo "🌐 Service Health:"
echo -n "Application: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/_stcore/health 2>/dev/null && echo "✅ Ready" || echo "❌ Not Ready"

echo -n "Nginx Health: "
curl -s -o /dev/null -w "%{http_code}" http://localhost/health 2>/dev/null && echo "✅ Ready" || echo "❌ Not Ready"

echo -n "Database: "
pg_isready -h localhost -p 5432 -U dataguardian 2>/dev/null && echo "✅ Ready" || echo "❌ Not Ready"

echo -n "Redis: "
redis-cli ping 2>/dev/null >/dev/null && echo "✅ Ready" || echo "❌ Not Ready"

echo ""
echo "💿 Disk Usage:"
df -h /opt/dataguardian

echo ""
echo "📊 Memory Usage:"
free -h

echo ""
echo "🔄 Recent Logs:"
journalctl -u dataguardian.service --no-pager -n 5
EOF

# Backup script
cat > "$APP_DIR/backup.sh" << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/dataguardian/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

mkdir -p $BACKUP_DIR
echo "🔄 Starting backup process..."

# Load environment
source /opt/dataguardian/.env

# Database backup
echo "📊 Backing up PostgreSQL database..."
PGPASSWORD="$POSTGRES_PASSWORD" pg_dump -h localhost -U dataguardian dataguardian_prod | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Redis backup
echo "🔄 Backing up Redis data..."
redis-cli -a "$REDIS_PASSWORD" --rdb $BACKUP_DIR/redis_backup_$DATE.rdb >/dev/null 2>&1

# Application data backup
echo "📁 Backing up application data..."
tar -czf $BACKUP_DIR/data_backup_$DATE.tar.gz -C /opt/dataguardian data/ logs/ reports/ config/ --exclude='*.tmp' 2>/dev/null

# Clean up old backups
echo "🧹 Cleaning up old backups..."
find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.rdb" -mtime +$RETENTION_DAYS -delete

echo "✅ Backup completed: $BACKUP_DIR"
EOF

chmod +x "$APP_DIR/status.sh" "$APP_DIR/backup.sh"
chown "$APP_USER:$APP_USER" "$APP_DIR/status.sh" "$APP_DIR/backup.sh"

print_success "Management scripts created"

# =============================================================================
# STEP 12: SSL Certificate (Optional)
# =============================================================================
if [ "$RUN_CERTBOT" = true ]; then
    print_step "12" "SSL Certificate Generation"
    
    # Install certbot if not present
    if ! command -v certbot &> /dev/null; then
        apt install -y certbot python3-certbot-nginx
    fi
    
    # Check if domain resolves to this server
    DOMAIN_IP=$(dig +short "$DOMAIN" | tail -n1)
    SERVER_IP=$(curl -s https://ipinfo.io/ip 2>/dev/null || curl -s https://api.ipify.org 2>/dev/null)
    
    if [ "$DOMAIN_IP" = "$SERVER_IP" ]; then
        print_info "Domain resolves correctly, generating SSL certificate..."
        certbot --nginx --agree-tos --no-eff-email --email "$EMAIL" -d "$DOMAIN" --redirect --non-interactive
        print_success "SSL certificate generated"
    else
        print_warning "Domain $DOMAIN doesn't resolve to this server ($SERVER_IP). Please update DNS first."
        print_info "You can run 'certbot --nginx -d $DOMAIN' manually after DNS propagation"
    fi
else
    print_step "12" "SSL Certificate (Skipped)"
    print_info "SSL certificate not generated (use --run-certbot to enable)"
fi

# =============================================================================
# STEP 13: Security Configuration
# =============================================================================
print_step "13" "Security Configuration"

# Fail2Ban configuration
if [ ! -f /etc/fail2ban/jail.local ]; then
    cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
EOF

    systemctl enable fail2ban
    systemctl restart fail2ban
fi

# Log rotation
cat > /etc/logrotate.d/dataguardian << 'EOF'
/opt/dataguardian/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 dataguardian dataguardian
    postrotate
        systemctl reload dataguardian.service 2>/dev/null || true
    endscript
}
EOF

# Automated backups
if ! crontab -l 2>/dev/null | grep -q "backup.sh"; then
    (crontab -l 2>/dev/null; echo "0 2 * * * /opt/dataguardian/backup.sh >> /opt/dataguardian/logs/backup.log 2>&1") | crontab -
fi

print_success "Security configured"

# =============================================================================
# STEP 14: Start Services
# =============================================================================
print_step "14" "Starting Services"

# Start DataGuardian service
systemctl start dataguardian

# Wait for service to start
sleep 10

# Check service status
if systemctl is-active --quiet dataguardian; then
    print_success "DataGuardian service started successfully"
else
    print_warning "DataGuardian service failed to start, checking logs..."
    journalctl -u dataguardian.service --no-pager -n 10
fi

print_success "Services started"

# =============================================================================
# STEP 15: Deployment Verification
# =============================================================================
print_step "15" "Deployment Verification"

print_info "Waiting for application to fully initialize..."
sleep 15

# Test application health
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/_stcore/health | grep -q "200"; then
    print_success "✅ Application health check passed"
else
    print_warning "⚠️ Application health check failed"
fi

# Test nginx health
if curl -s -o /dev/null -w "%{http_code}" http://localhost/health | grep -q "200"; then
    print_success "✅ Nginx health check passed"
else
    print_warning "⚠️ Nginx health check failed"
fi

# Test database connection
if pg_isready -h localhost -p 5432 -U dataguardian >/dev/null 2>&1; then
    print_success "✅ Database connection successful"
else
    print_warning "⚠️ Database connection failed"
fi

# Test Redis connection
if redis-cli ping >/dev/null 2>&1; then
    print_success "✅ Redis connection successful"
else
    print_warning "⚠️ Redis connection failed"
fi

print_success "Deployment verification completed"

# =============================================================================
# FINAL SUMMARY
# =============================================================================
cat > "$APP_DIR/deployment_info.txt" << EOF
DataGuardian Pro Production Deployment
=====================================
Date: $(date)
Domain: $DOMAIN
Email: $EMAIL
Installation Directory: $APP_DIR
Service User: $APP_USER

Database Password: $DB_PASSWORD
Redis Password: $REDIS_PASSWORD
JWT Secret: $JWT_SECRET
Encryption Key: $ENCRYPTION_KEY

Services:
- Application: systemctl start/stop/restart dataguardian
- PostgreSQL: systemctl start/stop/restart postgresql
- Redis: systemctl start/stop/restart redis-server
- Nginx: systemctl start/stop/restart nginx

Management:
- Status: $APP_DIR/status.sh
- Backup: $APP_DIR/backup.sh
- Logs: journalctl -u dataguardian.service -f

Access:
- HTTP: http://$DOMAIN
- HTTPS: https://$DOMAIN (if SSL enabled)
- Health: http://$DOMAIN/health

Next Steps:
1. Update API keys in $APP_DIR/.env
2. Run: systemctl restart dataguardian
3. Generate SSL: certbot --nginx -d $DOMAIN (if not done)
4. Test: https://$DOMAIN
EOF

chown "$APP_USER:$APP_USER" "$APP_DIR/deployment_info.txt"
chmod 600 "$APP_DIR/deployment_info.txt"

echo ""
echo "🎉 DataGuardian Pro Installation Complete!"
echo "==========================================="
echo ""
echo "✅ **Installation Summary:**"
echo "• Domain: $DOMAIN"
echo "• Installation: $APP_DIR"
echo "• Service User: $APP_USER"
echo "• Database: PostgreSQL (localhost:5432)"
echo "• Cache: Redis (localhost:6379)"
echo "• Web Server: Nginx (ports 80/443)"
echo ""
echo "🔧 **Next Steps:**"
echo "1. Update API keys: nano $APP_DIR/.env"
echo "2. Restart service: systemctl restart dataguardian"
if [ "$RUN_CERTBOT" != true ]; then
echo "3. Generate SSL: certbot --nginx -d $DOMAIN"
fi
echo ""
echo "📊 **Management Commands:**"
echo "• Status: $APP_DIR/status.sh"
echo "• Backup: $APP_DIR/backup.sh"
echo "• Logs: journalctl -u dataguardian.service -f"
echo "• Service: systemctl start/stop/restart dataguardian"
echo ""
echo "🌐 **Access Your Application:**"
echo "• HTTP: http://$DOMAIN"
if [ "$RUN_CERTBOT" = true ]; then
echo "• HTTPS: https://$DOMAIN"
fi
echo "• Health: http://$DOMAIN/health"
echo ""
echo "🇳🇱 **DataGuardian Pro is ready for enterprise privacy compliance!**"