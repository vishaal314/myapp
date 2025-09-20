#!/bin/bash
# DataGuardian Pro - Retzor Server Deployment Script
# Customized for your specific server setup

set -e

# Server Configuration (Update these as needed)
DOMAIN="vm.retzor.com"  # Using your provided domain
EMAIL="vishaalnoord7@gmail.com"  # Using your email for SSL
SERVER_IP="45.81.35.202"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_step() { echo -e "${BLUE}[STEP $1]${NC} $2"; }
print_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

echo "🚀 DataGuardian Pro - Retzor Server Deployment"
echo "=============================================="
echo "Domain: $DOMAIN"
echo "Server IP: $SERVER_IP"
echo "SSL Email: $EMAIL"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root"
    exit 1
fi

# =============================================================================
# STEP 1: System Updates and Dependencies
# =============================================================================
print_step "1" "System Updates and Dependencies Installation"
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
    tree

print_success "System updated successfully"

# =============================================================================
# STEP 2: Docker Installation
# =============================================================================
print_step "2" "Docker Installation"
print_info "Installing Docker and Docker Compose..."

# Remove old versions
apt remove -y docker docker-engine docker.io containerd runc || true

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Start Docker
systemctl start docker
systemctl enable docker

# Verify installation
docker --version
docker-compose --version

print_success "Docker installed successfully"

# =============================================================================
# STEP 3: Firewall Configuration
# =============================================================================
print_step "3" "Firewall Configuration"
print_info "Configuring UFW firewall..."

ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 5000/tcp
ufw --force enable

print_success "Firewall configured"

# =============================================================================
# STEP 4: Application Setup
# =============================================================================
print_step "4" "Application Directory Setup"
print_info "Creating DataGuardian Pro directory structure..."

mkdir -p /opt/dataguardian
cd /opt/dataguardian
mkdir -p {data,logs,reports,config,ssl,backups,nginx-logs}
chmod 755 data logs reports config nginx-logs backups
chmod 700 ssl

print_success "Application directory created: /opt/dataguardian"

# =============================================================================
# STEP 5: Environment Configuration
# =============================================================================
print_step "5" "Environment Configuration"
print_info "Creating secure environment configuration..."

# Generate secure passwords and keys
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
JWT_SECRET=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 16)

cat > .env << EOF
# DataGuardian Pro - Retzor Production Environment
# Generated: $(date)

# Application Settings
ENVIRONMENT=production
APP_NAME=DataGuardian Pro
APP_VERSION=1.0.0

# Database Configuration
DATABASE_URL=postgresql://dataguardian:$DB_PASSWORD@postgres:5432/dataguardian_prod
POSTGRES_DB=dataguardian_prod
POSTGRES_USER=dataguardian
POSTGRES_PASSWORD=$DB_PASSWORD

# Redis Configuration
REDIS_URL=redis://:$REDIS_PASSWORD@redis:6379/0
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

chmod 600 .env
print_success "Environment configuration created"

# =============================================================================
# STEP 6: Docker Compose Configuration
# =============================================================================
print_step "6" "Docker Compose Configuration"
print_info "Creating production Docker Compose setup..."

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  dataguardian:
    build: .
    container_name: dataguardian-pro
    ports:
      - "5000:5000"
    environment:
      - ENVIRONMENT=production
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./reports:/app/reports
      - ./config:/app/config
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - dataguardian-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  postgres:
    image: postgres:15-alpine
    container_name: dataguardian-postgres
    env_file:
      - .env
    environment:
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=C"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "127.0.0.1:5432:5432"
    restart: unless-stopped
    networks:
      - dataguardian-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dataguardian -d dataguardian_prod"]
      interval: 30s
      timeout: 10s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: dataguardian-redis
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "127.0.0.1:6379:6379"
    restart: unless-stopped
    networks:
      - dataguardian-network
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: dataguardian-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - ./nginx-logs:/var/log/nginx
      - certbot_certs:/etc/letsencrypt:ro
      - certbot_www:/var/www/certbot:ro
    depends_on:
      - dataguardian
    restart: unless-stopped
    networks:
      - dataguardian-network

  certbot:
    image: certbot/certbot
    container_name: dataguardian-certbot
    volumes:
      - certbot_certs:/etc/letsencrypt
      - certbot_www:/var/www/certbot
    command: >
      sh -c "while :; do
        certbot renew --webroot --webroot-path=/var/www/certbot --email ${SSL_EMAIL} --agree-tos --no-eff-email;
        sleep 86400;
      done"

volumes:
  postgres_data:
  redis_data:
  certbot_certs:
  certbot_www:

networks:
  dataguardian-network:
    driver: bridge
EOF

print_success "Docker Compose configuration created"

# =============================================================================
# STEP 7: Nginx Configuration
# =============================================================================
print_step "7" "Nginx Configuration"
print_info "Creating Nginx reverse proxy configuration..."

cat > nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=login:10m rate=5r/m;

    # Logging
    log_format main '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                    '\$status \$body_bytes_sent "\$http_referer" '
                    '"\$http_user_agent" "\$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    upstream dataguardian {
        server dataguardian:5000;
    }

    # HTTP server (redirect to HTTPS)
    server {
        listen 80;
        server_name $DOMAIN;
        
        # Let's Encrypt ACME challenge
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
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

        # SSL Configuration
        ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

        # File upload size
        client_max_body_size 100M;

        # Main application
        location / {
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
}
EOF

print_success "Nginx configuration created"

# =============================================================================
# STEP 8: Management Scripts
# =============================================================================
print_step "8" "Management Scripts"
print_info "Creating backup and status scripts..."

# Backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/dataguardian/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

mkdir -p $BACKUP_DIR
echo "🔄 Starting backup process..."

# Database backup
echo "📊 Backing up PostgreSQL database..."
docker-compose exec -T postgres pg_dump -U dataguardian dataguardian_prod | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Redis backup
echo "🔄 Backing up Redis data..."
docker-compose exec -T redis redis-cli -a $REDIS_PASSWORD --rdb /data/dump_$DATE.rdb 2>/dev/null
docker cp dataguardian-redis:/data/dump_$DATE.rdb $BACKUP_DIR/ 2>/dev/null || true

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
cat > status.sh << 'EOF'
#!/bin/bash
echo "🚀 DataGuardian Pro - System Status"
echo "==================================="

echo "📊 Container Status:"
docker-compose ps

echo ""
echo "💾 Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null

echo ""
echo "🌐 Service Health:"
echo -n "Application: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/_stcore/health 2>/dev/null || echo "❌"
echo ""

echo -n "Nginx Proxy: "
curl -s -o /dev/null -w "%{http_code}" http://localhost/health 2>/dev/null || echo "❌"
echo ""

echo -n "Database: "
docker-compose exec -T postgres pg_isready -U dataguardian -d dataguardian_prod 2>/dev/null && echo "✅ Ready" || echo "❌ Not Ready"

echo ""
echo "💿 Disk Usage:"
df -h /opt/dataguardian
EOF

chmod +x backup.sh status.sh
print_success "Management scripts created"

# =============================================================================
# STEP 9: Systemd Service
# =============================================================================
print_step "9" "Systemd Service Configuration"
print_info "Creating auto-start service..."

cat > /etc/systemd/system/dataguardian.service << 'EOF'
[Unit]
Description=DataGuardian Pro Service
Requires=docker.service
After=docker.service
StartLimitIntervalSec=0

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/dataguardian
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
ExecReload=/usr/local/bin/docker-compose restart
TimeoutStartSec=300
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable dataguardian.service
print_success "Systemd service configured"

# =============================================================================
# STEP 10: Security Setup
# =============================================================================
print_step "10" "Security Configuration"
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
logpath = /opt/dataguardian/nginx-logs/error.log

[nginx-dos]
enabled = true
port = http,https
logpath = /opt/dataguardian/nginx-logs/access.log
maxretry = 300
findtime = 300
bantime = 600
EOF

systemctl enable fail2ban
systemctl restart fail2ban

# Log rotation
cat > /etc/logrotate.d/dataguardian << 'EOF'
/opt/dataguardian/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker-compose -f /opt/dataguardian/docker-compose.yml restart dataguardian 2>/dev/null || true
    endscript
}
EOF

# Automated backups
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/dataguardian/backup.sh >> /opt/dataguardian/logs/backup.log 2>&1") | crontab -

print_success "Security configured"

print_info "🎉 DataGuardian Pro Retzor Deployment Complete!"
echo ""
echo "📋 Summary:"
echo "• Server: $SERVER_IP ($DOMAIN)"
echo "• Application Directory: /opt/dataguardian"
echo "• SSL Email: $EMAIL"
echo ""
echo "🔧 Next Steps:"
echo "1. Upload your DataGuardian Pro source code to /opt/dataguardian/"
echo "2. Update .env with your actual API keys"
echo "3. Build and start: docker-compose build && docker-compose up -d"
echo "4. Generate SSL: docker-compose run --rm certbot certonly --webroot --webroot-path=/var/www/certbot --email $EMAIL --agree-tos --no-eff-email -d $DOMAIN"
echo "5. Start service: systemctl start dataguardian"
echo ""
echo "📊 Management:"
echo "• Status: ./status.sh"
echo "• Backup: ./backup.sh"
echo "• Logs: docker-compose logs -f"
echo ""
echo "🌐 Access: https://$DOMAIN"

# Save deployment info securely
cat > deployment_info.txt << EOF
DataGuardian Pro Retzor Deployment
=================================
Date: $(date)
Server IP: $SERVER_IP
Domain: $DOMAIN
SSL Email: $EMAIL

Database Password: $DB_PASSWORD
Redis Password: $REDIS_PASSWORD
JWT Secret: $JWT_SECRET
Encryption Key: $ENCRYPTION_KEY

Management:
- Directory: /opt/dataguardian
- Service: systemctl start/stop/restart dataguardian
- Status: ./status.sh
- Backup: ./backup.sh
EOF

chmod 600 deployment_info.txt
print_success "🚀 Ready for source code upload and final configuration!"