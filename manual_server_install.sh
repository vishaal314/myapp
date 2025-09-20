#!/bin/bash
# DataGuardian Pro - Manual Server Installation Script
# Native installation without Docker

set -e

# Server Configuration
DOMAIN="dataguardianpro.nl"
EMAIL="vishaalnoord7@gmail.com"
SERVER_IP="45.81.35.202"
APP_USER="dataguardian"
APP_DIR="/opt/dataguardian"

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

echo "🚀 DataGuardian Pro - Manual Server Installation"
echo "==============================================="
echo "Domain: $DOMAIN"
echo "Installation Directory: $APP_DIR"
echo "Service User: $APP_USER"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root"
    exit 1
fi

# =============================================================================
# STEP 1: System Updates and Dependencies
# =============================================================================
print_step "1" "System Updates and Base Dependencies"
print_info "Updating system packages..."

export DEBIAN_FRONTEND=noninteractive
apt update && apt upgrade -y
apt install -y \
    curl \
    wget \
    git \
    unzip \
    htop \
    nano \
    ufw \
    fail2ban \
    build-essential \
    software-properties-common \
    ca-certificates \
    gnupg \
    lsb-release \
    tree \
    supervisor \
    logrotate

print_success "System updated successfully"

# =============================================================================
# STEP 2: Python 3.11 Installation
# =============================================================================
print_step "2" "Python 3.11 Installation"
print_info "Installing Python 3.11 and pip..."

add-apt-repository ppa:deadsnakes/ppa -y
apt update
apt install -y \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3.11-distutils \
    python3-pip

# Make Python 3.11 default
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

print_success "Python 3.11 installed successfully"

# =============================================================================
# STEP 3: PostgreSQL Installation
# =============================================================================
print_step "3" "PostgreSQL Installation"
print_info "Installing PostgreSQL 15..."

apt install -y postgresql postgresql-contrib postgresql-15

# Start and enable PostgreSQL
systemctl start postgresql
systemctl enable postgresql

# Create database and user
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
sudo -u postgres psql << EOF
CREATE USER dataguardian WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE dataguardian_prod OWNER dataguardian;
GRANT ALL PRIVILEGES ON DATABASE dataguardian_prod TO dataguardian;
ALTER USER dataguardian CREATEDB;
\q
EOF

print_success "PostgreSQL installed and configured"

# =============================================================================
# STEP 4: Redis Installation
# =============================================================================
print_step "4" "Redis Installation"
print_info "Installing Redis server..."

apt install -y redis-server

# Configure Redis
REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
sed -i "s/# requirepass foobared/requirepass $REDIS_PASSWORD/" /etc/redis/redis.conf
sed -i "s/bind 127.0.0.1/bind 127.0.0.1/" /etc/redis/redis.conf

systemctl restart redis-server
systemctl enable redis-server

print_success "Redis installed and configured"

# =============================================================================
# STEP 5: Nginx Installation
# =============================================================================
print_step "5" "Nginx Installation"
print_info "Installing Nginx web server..."

apt install -y nginx

# Stop default nginx for configuration
systemctl stop nginx

print_success "Nginx installed"

# =============================================================================
# STEP 6: Application User and Directory Setup
# =============================================================================
print_step "6" "Application Setup"
print_info "Creating application user and directory..."

# Create application user
useradd --system --shell /bin/bash --home $APP_DIR --create-home $APP_USER

# Create directory structure
mkdir -p $APP_DIR/{data,logs,reports,config,ssl,backups}
chown -R $APP_USER:$APP_USER $APP_DIR
chmod 755 $APP_DIR/{data,logs,reports,config,backups}
chmod 700 $APP_DIR/ssl

print_success "Application directory created: $APP_DIR"

# =============================================================================
# STEP 7: Environment Configuration
# =============================================================================
print_step "7" "Environment Configuration"
print_info "Creating application configuration..."

# Generate security keys
JWT_SECRET=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 16)

cat > $APP_DIR/.env << EOF
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
SAP_SSL_VERIFY=true
SALESFORCE_TIMEOUT=30
SAP_REQUEST_TIMEOUT=30
OIDC_TIMEOUT=30

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

chown $APP_USER:$APP_USER $APP_DIR/.env
chmod 600 $APP_DIR/.env

print_success "Environment configuration created"

# =============================================================================
# STEP 8: Python Virtual Environment
# =============================================================================
print_step "8" "Python Virtual Environment Setup"
print_info "Creating Python virtual environment..."

sudo -u $APP_USER python3.11 -m venv $APP_DIR/venv
sudo -u $APP_USER $APP_DIR/venv/bin/pip install --upgrade pip

# Install common dependencies
sudo -u $APP_USER $APP_DIR/venv/bin/pip install \
    streamlit \
    psycopg2-binary \
    redis \
    python-dotenv \
    requests \
    pandas \
    plotly

print_success "Virtual environment created"

# =============================================================================
# STEP 9: Systemd Service Configuration
# =============================================================================
print_step "9" "Systemd Service Configuration"
print_info "Creating DataGuardian Pro service..."

cat > /etc/systemd/system/dataguardian.service << EOF
[Unit]
Description=DataGuardian Pro - Privacy Compliance Platform
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

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
# STEP 10: Nginx Configuration
# =============================================================================
print_step "10" "Nginx Configuration"
print_info "Configuring Nginx reverse proxy..."

cat > /etc/nginx/sites-available/dataguardian << EOF
# Rate limiting
limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone \$binary_remote_addr zone=login:10m rate=5r/m;

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
    
    # Redirect to HTTPS
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name $DOMAIN;

    # SSL Configuration (will be configured after Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # File upload size
    client_max_body_size 100M;

    # Main application
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
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/dataguardian /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
nginx -t

print_success "Nginx configured"

# =============================================================================
# STEP 11: SSL Certificate Setup
# =============================================================================
print_step "11" "SSL Certificate Setup"
print_info "Installing Certbot for SSL certificates..."

apt install -y certbot python3-certbot-nginx

print_success "Certbot installed"

# =============================================================================
# STEP 12: Firewall Configuration
# =============================================================================
print_step "12" "Firewall Configuration"
print_info "Configuring UFW firewall..."

ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

print_success "Firewall configured"

# =============================================================================
# STEP 13: Management Scripts
# =============================================================================
print_step "13" "Management Scripts"
print_info "Creating backup and status scripts..."

# Backup script
cat > $APP_DIR/backup.sh << 'EOF'
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
pg_dump postgresql://dataguardian:$POSTGRES_PASSWORD@localhost:5432/dataguardian_prod | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Redis backup
echo "🔄 Backing up Redis data..."
redis-cli -a $REDIS_PASSWORD --rdb $BACKUP_DIR/redis_backup_$DATE.rdb

# Application data backup
echo "📁 Backing up application data..."
tar -czf $BACKUP_DIR/data_backup_$DATE.tar.gz data/ logs/ reports/ config/ --exclude='*.tmp' 2>/dev/null

# Clean up old backups
echo "🧹 Cleaning up old backups..."
find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.rdb" -mtime +$RETENTION_DAYS -delete

echo "✅ Backup completed: $BACKUP_DIR"
echo "📊 Backup size: $(du -sh $BACKUP_DIR | cut -f1)"
EOF

# Status script
cat > $APP_DIR/status.sh << 'EOF'
#!/bin/bash
echo "🚀 DataGuardian Pro - System Status"
echo "==================================="

echo "📊 Service Status:"
systemctl status dataguardian.service --no-pager -l
echo ""

echo "🌐 Service Health:"
echo -n "Application: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/_stcore/health 2>/dev/null || echo "❌"
echo ""

echo -n "Nginx Proxy: "
curl -s -o /dev/null -w "%{http_code}" http://localhost/health 2>/dev/null || echo "❌"
echo ""

echo -n "Database: "
pg_isready -h localhost -p 5432 -U dataguardian 2>/dev/null && echo "✅ Ready" || echo "❌ Not Ready"

echo -n "Redis: "
redis-cli ping 2>/dev/null && echo "✅ Ready" || echo "❌ Not Ready"

echo ""
echo "💿 Disk Usage:"
df -h /opt/dataguardian

echo ""
echo "📊 Memory Usage:"
free -h

echo ""
echo "🔄 Recent Logs:"
journalctl -u dataguardian.service --no-pager -n 10
EOF

chmod +x $APP_DIR/backup.sh $APP_DIR/status.sh
chown $APP_USER:$APP_USER $APP_DIR/backup.sh $APP_DIR/status.sh

print_success "Management scripts created"

# =============================================================================
# STEP 14: Security Setup
# =============================================================================
print_step "14" "Security Configuration"
print_info "Setting up Fail2Ban and security..."

# Fail2Ban configuration
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

[nginx-dos]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 300
findtime = 300
bantime = 600
EOF

systemctl enable fail2ban
systemctl start fail2ban

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
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/dataguardian/backup.sh >> /opt/dataguardian/logs/backup.log 2>&1") | crontab -

print_success "Security configured"

# =============================================================================
# STEP 15: Final Configuration
# =============================================================================
print_step "15" "Final Configuration"
print_info "Completing installation..."

# Start Nginx
systemctl start nginx
systemctl enable nginx

# Save deployment info
cat > $APP_DIR/deployment_info.txt << EOF
DataGuardian Pro Manual Installation
===================================
Date: $(date)
Server IP: $SERVER_IP
Domain: $DOMAIN
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
EOF

chown $APP_USER:$APP_USER $APP_DIR/deployment_info.txt
chmod 600 $APP_DIR/deployment_info.txt

print_success "✅ DataGuardian Pro Manual Installation Complete!"
echo ""
echo "📋 Summary:"
echo "• Domain: $DOMAIN"
echo "• Installation: $APP_DIR"
echo "• Service User: $APP_USER"
echo "• Database: PostgreSQL (localhost:5432)"
echo "• Cache: Redis (localhost:6379)"
echo "• Web Server: Nginx (ports 80/443)"
echo ""
echo "🔧 Next Steps:"
echo "1. Upload your DataGuardian Pro source code to $APP_DIR/"
echo "2. Install Python dependencies: sudo -u $APP_USER $APP_DIR/venv/bin/pip install -r requirements.txt"
echo "3. Update $APP_DIR/.env with your actual API keys"
echo "4. Generate SSL certificate: certbot --nginx -d $DOMAIN"
echo "5. Start application: systemctl start dataguardian"
echo ""
echo "📊 Management Commands:"
echo "• Status: $APP_DIR/status.sh"
echo "• Backup: $APP_DIR/backup.sh"
echo "• Logs: journalctl -u dataguardian.service -f"
echo "• Service: systemctl start/stop/restart dataguardian"
echo ""
echo "🌐 Access: https://$DOMAIN (after SSL setup)"