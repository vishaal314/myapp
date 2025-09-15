#!/bin/bash

# DataGuardian Pro Native Deployment Script (No Docker)
# For Ubuntu/Debian servers with direct Python installation

set -e

echo "🚀 DataGuardian Pro Native Deployment Starting..."
echo "======================================================="

# Configuration
DOMAIN="dataguardianpro.nl"
APP_DIR="/opt/dataguardian-pro"
APP_USER="dataguardian"
DB_NAME="dataguardian_pro"
DB_USER="dataguardian_user"
DB_PASS=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -hex 32)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: System Updates and Dependencies
log_info "Step 1: Updating system and installing dependencies..."
apt update && apt upgrade -y
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    certbot \
    python3-certbot-nginx \
    git \
    curl \
    wget \
    unzip \
    htop \
    nano \
    ufw \
    fail2ban \
    supervisor \
    build-essential \
    libpq-dev \
    pkg-config

# Step 2: Create application user
log_info "Step 2: Creating application user..."
if ! id "$APP_USER" &>/dev/null; then
    useradd -r -m -s /bin/bash "$APP_USER"
    log_info "User $APP_USER created"
else
    log_warn "User $APP_USER already exists"
fi

# Step 3: Create application directory
log_info "Step 3: Creating application directory..."
mkdir -p "$APP_DIR"
mkdir -p "$APP_DIR"/{logs,data,reports,backups,cache}
chown -R "$APP_USER":"$APP_USER" "$APP_DIR"

# Step 4: Configure PostgreSQL
log_info "Step 4: Configuring PostgreSQL..."
systemctl start postgresql
systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS $DB_NAME;
DROP USER IF EXISTS $DB_USER;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';
CREATE DATABASE $DB_NAME OWNER $DB_USER;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
ALTER USER $DB_USER CREATEDB;
\q
EOF

log_info "Database created: $DB_NAME with user: $DB_USER"

# Step 5: Configure Redis
log_info "Step 5: Configuring Redis..."
systemctl start redis-server
systemctl enable redis-server

# Configure Redis for production
cat > /etc/redis/redis.conf.backup << EOF
# Backup of original Redis config
$(cat /etc/redis/redis.conf)
EOF

# Update Redis configuration
sed -i 's/^# maxmemory <bytes>/maxmemory 512mb/' /etc/redis/redis.conf
sed -i 's/^# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis/redis.conf
systemctl restart redis-server

# Step 6: Setup Python environment
log_info "Step 6: Setting up Python virtual environment..."
cd "$APP_DIR"
sudo -u "$APP_USER" python3 -m venv venv
sudo -u "$APP_USER" bash -c "source venv/bin/activate && pip install --upgrade pip"

# Step 7: Extract and install application
log_info "Step 7: Application files should be uploaded to $APP_DIR"
log_warn "Please upload your DataGuardian Pro zip file to $APP_DIR before continuing"
log_warn "You can extract it using: unzip dataguardian-pro.zip -d $APP_DIR"

# Wait for user to upload files
echo -e "\n${YELLOW}Please upload your zip file and extract it, then press Enter to continue...${NC}"
read -r

# Install Python dependencies
if [ -f "$APP_DIR/requirements.txt" ] || [ -f "$APP_DIR/production_requirements.txt" ]; then
    log_info "Installing Python dependencies..."
    cd "$APP_DIR"
    if [ -f "production_requirements.txt" ]; then
        sudo -u "$APP_USER" bash -c "source venv/bin/activate && pip install -r production_requirements.txt"
    else
        sudo -u "$APP_USER" bash -c "source venv/bin/activate && pip install -r requirements.txt"
    fi
    
    # Install additional production dependencies
    sudo -u "$APP_USER" bash -c "source venv/bin/activate && pip install gunicorn psycopg2-binary"
else
    log_error "Requirements file not found! Please ensure requirements.txt or production_requirements.txt exists"
    exit 1
fi

# Step 8: Create environment configuration
log_info "Step 8: Creating environment configuration..."
cat > "$APP_DIR/.env" << EOF
# Production Configuration
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=$SECRET_KEY

# Database Configuration
DATABASE_URL=postgresql://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME
POSTGRES_USER=$DB_USER
POSTGRES_PASSWORD=$DB_PASS
POSTGRES_DB=$DB_NAME

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Domain Configuration
DOMAIN=$DOMAIN
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,localhost

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# API Keys (MUST BE CONFIGURED MANUALLY)
OPENAI_API_KEY=your_openai_api_key_here
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here

# Application Settings
MAX_UPLOAD_SIZE=100MB
SESSION_TIMEOUT=3600
LOG_LEVEL=INFO
EOF

chown "$APP_USER":"$APP_USER" "$APP_DIR/.env"
chmod 600 "$APP_DIR/.env"

log_warn "IMPORTANT: Edit $APP_DIR/.env to add your actual API keys"

# Step 9: Create application startup script
log_info "Step 9: Creating application startup script..."
cat > "$APP_DIR/start_app.sh" << 'EOF'
#!/bin/bash
cd /opt/dataguardian-pro
source venv/bin/activate
export $(cat .env | grep -v '^#' | xargs)

# Start Streamlit application
streamlit run app.py --server.port=5000 --server.address=0.0.0.0 --server.headless=true
EOF

chmod +x "$APP_DIR/start_app.sh"
chown "$APP_USER":"$APP_USER" "$APP_DIR/start_app.sh"

# Step 10: Configure Supervisor for process management
log_info "Step 10: Configuring Supervisor..."
cat > /etc/supervisor/conf.d/dataguardian.conf << EOF
[program:dataguardian-pro]
command=/opt/dataguardian-pro/start_app.sh
directory=/opt/dataguardian-pro
user=dataguardian
autostart=true
autorestart=true
stderr_logfile=/opt/dataguardian-pro/logs/error.log
stdout_logfile=/opt/dataguardian-pro/logs/access.log
environment=HOME="/home/dataguardian",USER="dataguardian"

[program:redis-server]
command=redis-server /etc/redis/redis.conf
autostart=true
autorestart=true
user=redis
EOF

# Create log files
touch "$APP_DIR/logs/error.log" "$APP_DIR/logs/access.log"
chown "$APP_USER":"$APP_USER" "$APP_DIR/logs"/*.log

systemctl enable supervisor
systemctl start supervisor
supervisorctl reread
supervisorctl update

# Step 11: Configure Nginx
log_info "Step 11: Configuring Nginx..."
cat > /etc/nginx/sites-available/dataguardian << EOF
# Rate limiting
limit_req_zone \$binary_remote_addr zone=app:10m rate=10r/s;

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    # SSL configuration will be added by certbot

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Application proxy
    location / {
        limit_req zone=app burst=20 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support for Streamlit
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }

    # Static files
    location /static/ {
        alias /opt/dataguardian-pro/static/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/dataguardian /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t
systemctl enable nginx
systemctl restart nginx

# Step 12: Configure SSL with Let's Encrypt
log_info "Step 12: Configuring SSL certificate..."
certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos --email "admin@$DOMAIN"

# Setup auto-renewal
systemctl enable certbot.timer
systemctl start certbot.timer

# Step 13: Configure Firewall
log_info "Step 13: Configuring firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Step 14: Configure Fail2Ban
log_info "Step 14: Configuring Fail2Ban..."
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

[nginx-noscript]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 6

[nginx-badbots]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 2
EOF

systemctl enable fail2ban
systemctl restart fail2ban

# Step 15: Create backup script
log_info "Step 15: Creating backup system..."
cat > "$APP_DIR/backup.sh" << 'EOF'
#!/bin/bash
# DataGuardian Pro Backup Script

BACKUP_DIR="/opt/dataguardian-pro/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_USER="dataguardian_user"
DB_NAME="dataguardian_pro"

# Database backup
pg_dump -U $DB_USER -h localhost $DB_NAME > "$BACKUP_DIR/db_backup_$TIMESTAMP.sql"

# Application files backup
tar -czf "$BACKUP_DIR/files_backup_$TIMESTAMP.tar.gz" \
    /opt/dataguardian-pro/data \
    /opt/dataguardian-pro/reports \
    /opt/dataguardian-pro/logs

# Cleanup old backups (keep 7 days)
find "$BACKUP_DIR" -name "db_backup_*.sql" -mtime +7 -delete
find "$BACKUP_DIR" -name "files_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: $TIMESTAMP"
EOF

chmod +x "$APP_DIR/backup.sh"
chown "$APP_USER":"$APP_USER" "$APP_DIR/backup.sh"

# Schedule daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * $APP_DIR/backup.sh") | crontab -

# Step 16: Start the application
log_info "Step 16: Starting DataGuardian Pro..."
supervisorctl start dataguardian-pro

# Step 17: Final verification
log_info "Step 17: Verifying installation..."
sleep 10

# Check services
systemctl is-active --quiet postgresql && log_info "✅ PostgreSQL: Running" || log_error "❌ PostgreSQL: Not running"
systemctl is-active --quiet redis-server && log_info "✅ Redis: Running" || log_error "❌ Redis: Not running"
systemctl is-active --quiet nginx && log_info "✅ Nginx: Running" || log_error "❌ Nginx: Not running"
supervisorctl status dataguardian-pro | grep -q RUNNING && log_info "✅ DataGuardian Pro: Running" || log_error "❌ DataGuardian Pro: Not running"

# Test application
if curl -f http://localhost:5000 > /dev/null 2>&1; then
    log_info "✅ Application responding on port 5000"
else
    log_warn "⚠️  Application not responding on port 5000"
fi

echo ""
echo "======================================================="
echo "🎉 DataGuardian Pro Deployment Complete!"
echo "======================================================="
echo ""
echo "📋 Deployment Summary:"
echo "• Application URL: https://$DOMAIN"
echo "• Application Directory: $APP_DIR"
echo "• Database: PostgreSQL ($DB_NAME)"
echo "• Cache: Redis"
echo "• Web Server: Nginx with SSL"
echo "• Process Manager: Supervisor"
echo ""
echo "🔧 Next Steps:"
echo "1. Edit $APP_DIR/.env to add your API keys"
echo "2. Restart application: supervisorctl restart dataguardian-pro"
echo "3. Visit https://$DOMAIN to access your application"
echo ""
echo "📊 Management Commands:"
echo "• View logs: tail -f $APP_DIR/logs/access.log"
echo "• Restart app: supervisorctl restart dataguardian-pro"
echo "• Check status: supervisorctl status"
echo "• Run backup: $APP_DIR/backup.sh"
echo ""
echo "🔐 Security Features Enabled:"
echo "✅ SSL/TLS encryption"
echo "✅ Firewall (UFW)"
echo "✅ Fail2Ban intrusion detection"
echo "✅ Rate limiting"
echo "✅ Security headers"
echo "✅ Automated backups"
echo ""

# Save credentials securely
cat > "$APP_DIR/deployment_info.txt" << EOF
DataGuardian Pro Deployment Information
======================================
Deployment Date: $(date)
Server IP: $(hostname -I | awk '{print $1}')
Domain: $DOMAIN

Database Information:
- Database Name: $DB_NAME
- Database User: $DB_USER  
- Database Password: $DB_PASS

Application Information:
- Directory: $APP_DIR
- User: $APP_USER
- Secret Key: $SECRET_KEY

Important Files:
- Environment: $APP_DIR/.env
- Logs: $APP_DIR/logs/
- Backups: $APP_DIR/backups/
- Startup: $APP_DIR/start_app.sh
EOF

chmod 600 "$APP_DIR/deployment_info.txt"
chown "$APP_USER":"$APP_USER" "$APP_DIR/deployment_info.txt"

log_info "Deployment information saved to: $APP_DIR/deployment_info.txt"
log_warn "IMPORTANT: Edit $APP_DIR/.env to configure your API keys before using the application!"

echo "🚀 Deployment script completed successfully!"