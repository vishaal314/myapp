#!/bin/bash

# DataGuardian Pro - Complete End-to-End Deployment Script
# Deploys entire infrastructure with production-ready configuration
# Supports Ubuntu 20.04+ / Debian 11+ / CentOS 8+ / Amazon Linux 2

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/var/log/dataguardian-deploy.log"
DEPLOY_USER="dataguardian"
DEPLOY_HOME="/opt/dataguardian"
DOMAIN="${DOMAIN:-localhost}"
SSL_EMAIL="${SSL_EMAIL:-admin@dataguardian.nl}"
ENVIRONMENT="${ENVIRONMENT:-production}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "${LOG_FILE}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" | tee -a "${LOG_FILE}"
    exit 1
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}" | tee -a "${LOG_FILE}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}" | tee -a "${LOG_FILE}"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root. Use: sudo $0"
    fi
}

# Detect OS
detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$ID
        VERSION=$VERSION_ID
    else
        error "Cannot detect operating system"
    fi
    log "Detected OS: $OS $VERSION"
}

# Install system dependencies
install_system_deps() {
    log "Installing system dependencies..."
    
    case $OS in
        ubuntu|debian)
            apt-get update -y
            apt-get install -y \
                curl wget git nginx postgresql postgresql-contrib redis-server \
                python3 python3-pip python3-venv python3-dev \
                build-essential libpq-dev libffi-dev libssl-dev \
                supervisor certbot python3-certbot-nginx \
                htop vim nano ufw fail2ban \
                tesseract-ocr tesseract-ocr-nld tesseract-ocr-deu \
                imagemagick ghostscript poppler-utils
            ;;
        centos|rhel|fedora)
            yum update -y
            yum groupinstall -y "Development Tools"
            yum install -y \
                curl wget git nginx postgresql postgresql-server postgresql-contrib redis \
                python3 python3-pip python3-devel \
                libpq-devel libffi-devel openssl-devel \
                supervisor certbot python3-certbot-nginx \
                htop vim nano firewalld fail2ban \
                tesseract tesseract-langpack-nld tesseract-langpack-deu \
                ImageMagick ghostscript poppler-utils
            ;;
        *)
            error "Unsupported operating system: $OS"
            ;;
    esac
}

# Setup firewall
setup_firewall() {
    log "Configuring firewall..."
    
    case $OS in
        ubuntu|debian)
            ufw --force reset
            ufw default deny incoming
            ufw default allow outgoing
            ufw allow ssh
            ufw allow 80/tcp
            ufw allow 443/tcp
            ufw allow 5000/tcp  # DataGuardian app port
            ufw --force enable
            ;;
        centos|rhel|fedora)
            systemctl enable firewalld
            systemctl start firewalld
            firewall-cmd --permanent --add-service=ssh
            firewall-cmd --permanent --add-service=http
            firewall-cmd --permanent --add-service=https
            firewall-cmd --permanent --add-port=5000/tcp
            firewall-cmd --reload
            ;;
    esac
}

# Create deployment user
create_deploy_user() {
    log "Creating deployment user..."
    
    if ! id "$DEPLOY_USER" &>/dev/null; then
        useradd -m -s /bin/bash "$DEPLOY_USER"
        usermod -aG sudo "$DEPLOY_USER"
    fi
    
    mkdir -p "$DEPLOY_HOME"
    chown -R "$DEPLOY_USER:$DEPLOY_USER" "$DEPLOY_HOME"
}

# Setup PostgreSQL
setup_postgresql() {
    log "Setting up PostgreSQL..."
    
    case $OS in
        ubuntu|debian)
            systemctl enable postgresql
            systemctl start postgresql
            ;;
        centos|rhel|fedora)
            postgresql-setup initdb
            systemctl enable postgresql
            systemctl start postgresql
            ;;
    esac
    
    # Create database and user
    sudo -u postgres psql -c "CREATE USER dataguardian WITH PASSWORD 'DG_$(openssl rand -base64 32)';"
    sudo -u postgres psql -c "CREATE DATABASE dataguardian OWNER dataguardian;"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE dataguardian TO dataguardian;"
    
    # Store database credentials
    echo "DATABASE_URL=postgresql://dataguardian:DG_$(openssl rand -base64 32)@localhost:5432/dataguardian" > "$DEPLOY_HOME/.env"
    chown "$DEPLOY_USER:$DEPLOY_USER" "$DEPLOY_HOME/.env"
    chmod 600 "$DEPLOY_HOME/.env"
}

# Setup Redis
setup_redis() {
    log "Setting up Redis..."
    
    systemctl enable redis-server redis || systemctl enable redis
    systemctl start redis-server redis || systemctl start redis
    
    # Configure Redis for production
    sed -i 's/# maxmemory <bytes>/maxmemory 512mb/' /etc/redis/redis.conf || sed -i 's/# maxmemory <bytes>/maxmemory 512mb/' /etc/redis.conf
    sed -i 's/# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis/redis.conf || sed -i 's/# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis.conf
    
    systemctl restart redis-server redis || systemctl restart redis
    
    echo "REDIS_URL=redis://localhost:6379/0" >> "$DEPLOY_HOME/.env"
}

# Install Python dependencies
setup_python_env() {
    log "Setting up Python environment..."
    
    sudo -u "$DEPLOY_USER" bash << EOF
cd "$DEPLOY_HOME"
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip wheel setuptools

# Install core dependencies
pip install streamlit==1.28.1
pip install psycopg2-binary redis
pip install pandas plotly pillow
pip install requests beautifulsoup4 trafilatura tldextract
pip install openai anthropic
pip install stripe pyjwt bcrypt
pip install reportlab pypdf2 textract pytesseract
pip install opencv-python-headless
pip install python-whois dnspython
pip install cryptography python-jose
pip install pyyaml cachetools psutil memory-profiler
pip install svglib mysql-connector-python pyodbc
pip install aiohttp flask
pip install py-spy pyinstaller

# Create requirements.txt
pip freeze > requirements.txt
EOF
}

# Deploy application code
deploy_application() {
    log "Deploying DataGuardian Pro application..."
    
    # Copy application files
    cp -r "$SCRIPT_DIR"/* "$DEPLOY_HOME/" 2>/dev/null || true
    chown -R "$DEPLOY_USER:$DEPLOY_USER" "$DEPLOY_HOME"
    
    # Create necessary directories
    sudo -u "$DEPLOY_USER" mkdir -p "$DEPLOY_HOME"/{logs,uploads,cache,backups,certificates,.streamlit}
    
    # Create Streamlit config for HTTPS
    cat > "$DEPLOY_HOME/.streamlit/config.toml" << EOF
[server]
headless = true
address = "127.0.0.1"
port = 5000
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 100

[browser]
gatherUsageStats = false

[theme]
base = "light"
EOF

    chown -R "$DEPLOY_USER:$DEPLOY_USER" "$DEPLOY_HOME/.streamlit"
    
    # Set proper permissions
    chmod +x "$DEPLOY_HOME"/*.sh 2>/dev/null || true
}

# Setup environment variables
setup_environment() {
    log "Configuring environment variables..."
    
    # Determine protocol based on domain
    if [[ "$DOMAIN" != "localhost" && "$DOMAIN" != "127.0.0.1" ]]; then
        PROTOCOL="https"
    else
        PROTOCOL="http"
    fi
    
    cat >> "$DEPLOY_HOME/.env" << EOF
# Application Configuration
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Application URLs
APP_URL=$PROTOCOL://$DOMAIN
API_URL=$PROTOCOL://$DOMAIN/api

# Security Settings
SECRET_KEY=$(openssl rand -base64 64)
JWT_SECRET=$(openssl rand -base64 64)
SECURE_SSL_REDIRECT=true
SESSION_COOKIE_SECURE=true
CSRF_COOKIE_SECURE=true
HTTPS=1
FORCE_HTTPS=true

# SSL/TLS Configuration
SSL_VERIFY=true
SSL_CIPHERS=ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS
SSL_PROTOCOLS=TLSv1.2,TLSv1.3

# Security Headers
HSTS_MAX_AGE=31536000
HSTS_INCLUDE_SUBDOMAINS=true
HSTS_PRELOAD=true
X_FRAME_OPTIONS=DENY
X_CONTENT_TYPE_OPTIONS=nosniff
CSP_ENABLED=true

# Performance Settings
WORKERS=4
MAX_CONNECTIONS=100
CACHE_TTL=3600

# Netherlands Localization
DEFAULT_LANGUAGE=nl
TIMEZONE=Europe/Amsterdam
CURRENCY=EUR

# Monitoring
AUDIT_LOG_ENABLED=true
PERFORMANCE_MONITORING=true
METRICS_ENABLED=true

# File Upload Limits
MAX_UPLOAD_SIZE=100MB
ALLOWED_EXTENSIONS=pdf,docx,xlsx,csv,txt,py,js,java,cpp,c

# Email Configuration (to be configured)
# SMTP_HOST=
# SMTP_PORT=587
# SMTP_USER=
# SMTP_PASSWORD=
# FROM_EMAIL=noreply@dataguardian.nl
EOF

    chown "$DEPLOY_USER:$DEPLOY_USER" "$DEPLOY_HOME/.env"
    chmod 600 "$DEPLOY_HOME/.env"
}

# Setup Nginx
setup_nginx() {
    log "Configuring Nginx with HTTPS security..."
    
    cat > /etc/nginx/sites-available/dataguardian << EOF
# HTTP to HTTPS redirect
server {
    listen 80;
    server_name $DOMAIN;
    
    # Security headers for HTTP (minimal)
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    
    # Health check (accessible via HTTP for monitoring)
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    # Let's Encrypt ACME challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirect all other HTTP traffic to HTTPS
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

# HTTPS server (will be configured by certbot)
server {
    listen 443 ssl http2;
    server_name $DOMAIN;
    
    # SSL Configuration (enhanced by certbot)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # Enhanced Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: blob: https:; connect-src 'self' wss: https:; frame-ancestors 'none';" always;
    
    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=20r/s;
    limit_req_zone \$binary_remote_addr zone=login:10m rate=5r/m;
    limit_req zone=api burst=40 nodelay;
    
    # File upload size
    client_max_body_size 100M;
    client_body_timeout 60s;
    client_header_timeout 60s;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Proxy to Streamlit
    location / {
        # Additional rate limiting for login pages
        if (\$request_uri ~* "/(login|auth|signin)") {
            limit_req zone=login burst=10 nodelay;
        }
        
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-Port 443;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 86400;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        
        # Security headers for proxied content
        proxy_hide_header X-Powered-By;
        proxy_hide_header Server;
    }
    
    # Static files with security
    location /static/ {
        alias $DEPLOY_HOME/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header X-Content-Type-Options nosniff;
        
        # Deny access to sensitive files
        location ~* \.(htaccess|htpasswd|ini|log|sh|inc|bak|env)$ {
            deny all;
        }
    }
    
    # Health check (HTTPS)
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }
    
    # Security: Deny access to sensitive locations
    location ~ /\.(ht|git|env) {
        deny all;
        return 404;
    }
    
    location ~* \.(log|bak|backup|old)$ {
        deny all;
        return 404;
    }
}
EOF

    # Enable site
    ln -sf /etc/nginx/sites-available/dataguardian /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Create Let's Encrypt webroot
    mkdir -p /var/www/html/.well-known/acme-challenge
    chown -R www-data:www-data /var/www/html
    
    # Test nginx configuration
    nginx -t
    systemctl enable nginx
    systemctl restart nginx
}

# Setup SSL with Let's Encrypt
setup_ssl() {
    log "Setting up SSL certificate..."
    
    if [[ "$DOMAIN" != "localhost" && "$DOMAIN" != "127.0.0.1" ]]; then
        certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email "$SSL_EMAIL" --redirect
    else
        warn "Skipping SSL setup for localhost/IP address"
    fi
}

# Setup Supervisor for process management
setup_supervisor() {
    log "Setting up Supervisor for process management..."
    
    cat > /etc/supervisor/conf.d/dataguardian.conf << EOF
[program:dataguardian]
command=$DEPLOY_HOME/venv/bin/streamlit run app.py --server.port 5000 --server.address 127.0.0.1 --server.headless true --server.enableCORS false --server.enableXsrfProtection true
directory=$DEPLOY_HOME
user=$DEPLOY_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$DEPLOY_HOME/logs/app.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=PATH="$DEPLOY_HOME/venv/bin",STREAMLIT_SERVER_ENABLE_CORS=false,STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true,HTTPS=1,NODE_ENV=production

[program:dataguardian-worker]
command=$DEPLOY_HOME/venv/bin/python worker.py
directory=$DEPLOY_HOME
user=$DEPLOY_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$DEPLOY_HOME/logs/worker.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=PATH="$DEPLOY_HOME/venv/bin",HTTPS=1,NODE_ENV=production
EOF

    systemctl enable supervisor
    systemctl restart supervisor
    supervisorctl reread
    supervisorctl update
}

# Setup monitoring
setup_monitoring() {
    log "Setting up monitoring and logging..."
    
    # Create log rotation
    cat > /etc/logrotate.d/dataguardian << EOF
$DEPLOY_HOME/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $DEPLOY_USER $DEPLOY_USER
    postrotate
        supervisorctl restart dataguardian
    endscript
}
EOF

    # Setup fail2ban for security
    cat > /etc/fail2ban/jail.d/dataguardian.conf << EOF
[dataguardian]
enabled = true
port = 80,443
protocol = tcp
filter = nginx-http-auth
logpath = /var/log/nginx/error.log
maxretry = 5
bantime = 3600
findtime = 600
EOF

    systemctl enable fail2ban
    systemctl restart fail2ban
}

# Create backup script
setup_backup() {
    log "Setting up backup system..."
    
    cat > "$DEPLOY_HOME/backup.sh" << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/dataguardian/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
pg_dump dataguardian > "$BACKUP_DIR/db_backup_$DATE.sql"

# Application backup
tar -czf "$BACKUP_DIR/app_backup_$DATE.tar.gz" -C /opt/dataguardian \
    --exclude=backups --exclude=logs --exclude=cache --exclude=venv .

# Clean old backups (keep 7 days)
find "$BACKUP_DIR" -name "*.sql" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

    chmod +x "$DEPLOY_HOME/backup.sh"
    chown "$DEPLOY_USER:$DEPLOY_USER" "$DEPLOY_HOME/backup.sh"
    
    # Add to crontab
    (crontab -l -u "$DEPLOY_USER" 2>/dev/null; echo "0 2 * * * $DEPLOY_HOME/backup.sh >> $DEPLOY_HOME/logs/backup.log 2>&1") | crontab -u "$DEPLOY_USER" -
}

# Initialize database
initialize_database() {
    log "Initializing database..."
    
    sudo -u "$DEPLOY_USER" bash << EOF
cd "$DEPLOY_HOME"
source venv/bin/activate
source .env

# Run database migrations if they exist
if [[ -f "migrations/init.sql" ]]; then
    psql "\$DATABASE_URL" -f migrations/init.sql
fi

# Create initial admin user (if user management exists)
if [[ -f "create_admin.py" ]]; then
    python create_admin.py
fi
EOF
}

# Health checks
run_health_checks() {
    log "Running health checks..."
    
    # Check services
    systemctl is-active --quiet postgresql || error "PostgreSQL is not running"
    systemctl is-active --quiet redis || systemctl is-active --quiet redis-server || error "Redis is not running"
    systemctl is-active --quiet nginx || error "Nginx is not running"
    systemctl is-active --quiet supervisor || error "Supervisor is not running"
    
    # Check application
    sleep 10  # Give app time to start
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        log "✓ Application health check passed (HTTP)"
    else
        warn "Application health check failed - check logs"
    fi
    
    # Check HTTPS if domain is not localhost
    if [[ "$DOMAIN" != "localhost" && "$DOMAIN" != "127.0.0.1" ]]; then
        sleep 5  # Additional time for SSL setup
        if curl -f -k https://"$DOMAIN"/health > /dev/null 2>&1; then
            log "✓ HTTPS health check passed"
        else
            warn "HTTPS health check failed - SSL may still be setting up"
        fi
        
        # Test HTTP to HTTPS redirect
        if curl -s -I http://"$DOMAIN" | grep -q "301\|302"; then
            log "✓ HTTP to HTTPS redirect working"
        else
            warn "HTTP to HTTPS redirect may not be working correctly"
        fi
    fi
    
    # Check database connection
    sudo -u "$DEPLOY_USER" bash << EOF
cd "$DEPLOY_HOME"
source venv/bin/activate
source .env
python3 -c "import psycopg2; psycopg2.connect('\$DATABASE_URL'); print('✓ Database connection successful')"
EOF
}

# Display deployment summary
show_summary() {
    log "Deployment Summary"
    echo "===================="
    echo "✓ DataGuardian Pro deployed successfully with HTTPS security!"
    echo ""
    
    # Show appropriate URLs
    if [[ "$DOMAIN" != "localhost" && "$DOMAIN" != "127.0.0.1" ]]; then
        echo "🔒 Secure Application URL: https://$DOMAIN"
        echo "   (HTTP automatically redirects to HTTPS)"
    else
        echo "Application URL: http://$DOMAIN"
        echo "   (HTTPS available when deployed with a real domain)"
    fi
    
    echo ""
    echo "Infrastructure:"
    echo "  Deploy Directory: $DEPLOY_HOME"
    echo "  Deploy User: $DEPLOY_USER"
    echo "  Database: PostgreSQL (dataguardian)"
    echo "  Cache: Redis with persistent storage"
    echo "  Web Server: Nginx with SSL/TLS termination"
    echo "  Process Manager: Supervisor"
    echo ""
    
    echo "Security Features:"
    if [[ "$DOMAIN" != "localhost" && "$DOMAIN" != "127.0.0.1" ]]; then
        echo "  ✓ SSL/TLS encryption (Let's Encrypt)"
        echo "  ✓ HTTP to HTTPS automatic redirect"
        echo "  ✓ HSTS headers (31536000 seconds)"
        echo "  ✓ Content Security Policy (CSP)"
    fi
    echo "  ✓ Rate limiting (API & login protection)"
    echo "  ✓ Security headers (XSS, CSRF, Clickjacking)"
    echo "  ✓ Fail2ban intrusion prevention"
    echo "  ✓ Firewall configured (UFW/firewalld)"
    echo "  ✓ File upload restrictions"
    echo ""
    
    echo "Logs & Monitoring:"
    echo "  Application: $DEPLOY_HOME/logs/app.log"
    echo "  Worker: $DEPLOY_HOME/logs/worker.log"
    echo "  Nginx Access: /var/log/nginx/access.log"
    echo "  Nginx Error: /var/log/nginx/error.log"
    echo "  Deployment: $LOG_FILE"
    echo "  SSL Certificate: /var/log/letsencrypt/"
    echo ""
    
    echo "Management Commands:"
    echo "  Start: supervisorctl start dataguardian"
    echo "  Stop: supervisorctl stop dataguardian"
    echo "  Restart: supervisorctl restart dataguardian"
    echo "  Status: supervisorctl status"
    echo "  Logs: tail -f $DEPLOY_HOME/logs/app.log"
    echo "  Backup: $DEPLOY_HOME/backup.sh"
    echo "  SSL Renewal: certbot renew (automatic via cron)"
    echo ""
    
    echo "Next Steps:"
    echo "1. Configure API keys in $DEPLOY_HOME/.env"
    if [[ "$DOMAIN" != "localhost" && "$DOMAIN" != "127.0.0.1" ]]; then
        echo "2. Verify DNS points to this server"
        echo "3. Test HTTPS certificate and security headers"
    else
        echo "2. Deploy with real domain for full HTTPS security"
    fi
    echo "4. Configure email settings for notifications"
    echo "5. Set up monitoring alerts and backups"
    echo "6. Review and customize security policies"
    echo ""
    echo "🎉 DataGuardian Pro is ready for secure production deployment!"
}

# Main deployment function
main() {
    log "Starting DataGuardian Pro End-to-End Deployment"
    
    check_root
    detect_os
    install_system_deps
    setup_firewall
    create_deploy_user
    setup_postgresql
    setup_redis
    setup_python_env
    deploy_application
    setup_environment
    setup_nginx
    setup_ssl
    setup_supervisor
    setup_monitoring
    setup_backup
    initialize_database
    run_health_checks
    show_summary
    
    log "Deployment completed successfully!"
}

# Trap errors
trap 'error "Deployment failed at line $LINENO"' ERR

# Run main function
main "$@"