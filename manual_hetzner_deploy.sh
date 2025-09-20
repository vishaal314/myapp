#!/bin/bash
# DataGuardian Pro - Manual Hetzner Deployment Script
# Complete step-by-step deployment for Netherlands hosting
# Run this script on your Hetzner server with Ubuntu 22.04 LTS

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration - UPDATE THESE BEFORE RUNNING
DOMAIN="your-domain.com"  # UPDATE: Your actual domain
EMAIL="admin@your-domain.com"  # UPDATE: Your email for SSL certificates
SERVER_NAME="dataguardian-pro"

print_step() { echo -e "${BLUE}[STEP $1]${NC} $2"; }
print_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

# Function to wait for user confirmation
wait_for_confirmation() {
    echo -e "\n${CYAN}Press Enter to continue or Ctrl+C to abort...${NC}"
    read -r
}

echo "🚀 DataGuardian Pro - Manual Hetzner Deployment"
echo "==============================================="
echo "This script will deploy DataGuardian Pro on your Hetzner server"
echo "Make sure you have updated the DOMAIN and EMAIL variables above!"
echo ""

print_warning "Before starting, ensure you have:"
echo "  ✓ Ubuntu 22.04 LTS server on Hetzner"
echo "  ✓ Root access to the server"
echo "  ✓ Domain DNS pointing to this server"
echo "  ✓ DataGuardian Pro source code ready"
echo ""
wait_for_confirmation

# =============================================================================
# STEP 1: System Updates and Dependencies
# =============================================================================
print_step "1" "System Updates and Dependencies Installation"
print_info "Updating system packages and installing required dependencies..."

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
    lsb-release

print_success "System updated and basic dependencies installed"
wait_for_confirmation

# =============================================================================
# STEP 2: Docker Installation
# =============================================================================
print_step "2" "Docker and Docker Compose Installation"
print_info "Installing Docker Engine and Docker Compose..."

# Remove old Docker versions
apt remove -y docker docker-engine docker.io containerd runc || true

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Add current user to docker group (if not root)
if [ "$USER" != "root" ]; then
    usermod -aG docker $USER
    print_warning "You may need to log out and back in for Docker group changes to take effect"
fi

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Start and enable Docker
systemctl start docker
systemctl enable docker

# Verify installation
docker --version
docker-compose --version

print_success "Docker and Docker Compose installed successfully"
wait_for_confirmation

# =============================================================================
# STEP 3: Firewall Configuration
# =============================================================================
print_step "3" "Firewall Configuration"
print_info "Configuring UFW firewall for security..."

# Reset firewall to defaults
ufw --force reset
ufw default deny incoming
ufw default allow outgoing

# Allow essential ports
ufw allow OpenSSH      # SSH access
ufw allow 80/tcp       # HTTP
ufw allow 443/tcp      # HTTPS
ufw allow 5000/tcp     # DataGuardian Pro (for testing)

# Enable firewall
ufw --force enable
ufw status

print_success "Firewall configured successfully"
wait_for_confirmation

# =============================================================================
# STEP 4: Application Directory Setup
# =============================================================================
print_step "4" "Application Directory Setup"
print_info "Creating application directory structure..."

# Create main application directory
mkdir -p /opt/dataguardian
cd /opt/dataguardian

# Create subdirectories
mkdir -p {data,logs,reports,config,ssl,backups,nginx-logs}

# Set proper permissions
chmod 755 data logs reports config nginx-logs backups
chmod 700 ssl

print_success "Application directory created: /opt/dataguardian"
print_info "Directory structure:"
tree /opt/dataguardian || ls -la /opt/dataguardian
wait_for_confirmation

# =============================================================================
# STEP 5: Environment Configuration
# =============================================================================
print_step "5" "Environment Configuration"
print_info "Creating production environment configuration..."

# Generate secure passwords
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
JWT_SECRET=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 16)

cat > .env << EOF
# DataGuardian Pro - Hetzner Production Environment
# Generated on: $(date)

# Application Settings
ENVIRONMENT=production
APP_NAME=DataGuardian Pro
APP_VERSION=1.0.0
SERVER_NAME=$SERVER_NAME

# Database Configuration
DATABASE_URL=postgresql://dataguardian:$DB_PASSWORD@postgres:5432/dataguardian_prod
POSTGRES_DB=dataguardian_prod
POSTGRES_USER=dataguardian
POSTGRES_PASSWORD=$DB_PASSWORD

# Redis Configuration  
REDIS_URL=redis://:$REDIS_PASSWORD@redis:6379/0
REDIS_PASSWORD=$REDIS_PASSWORD

# Security Settings (Production Ready)
JWT_SECRET=$JWT_SECRET
ENCRYPTION_KEY=$ENCRYPTION_KEY
SAP_SSL_VERIFY=true
SALESFORCE_TIMEOUT=30
SAP_REQUEST_TIMEOUT=30
OIDC_TIMEOUT=30

# API Keys - MUST BE UPDATED WITH YOUR ACTUAL KEYS
OPENAI_API_KEY=your_openai_api_key_here
STRIPE_PUBLISHABLE_KEY=pk_live_your_publishable_key_here
STRIPE_SECRET_KEY=sk_live_your_secret_key_here

# GDPR Compliance (Netherlands)
DATA_RESIDENCY=EU
PRIVACY_POLICY_URL=https://$DOMAIN/privacy
TERMS_URL=https://$DOMAIN/terms
DEFAULT_COUNTRY=NL
DEFAULT_LANGUAGE=en
UAVG_COMPLIANCE=true

# Domain Configuration
DOMAIN_NAME=$DOMAIN
SSL_EMAIL=$EMAIL

# Monitoring and Logging
LOG_LEVEL=INFO
ENABLE_DEBUG=false
HEALTH_CHECK_ENABLED=true
EOF

# Secure the environment file
chmod 600 .env

print_success "Environment configuration created"
print_warning "IMPORTANT: Update .env file with your actual API keys!"
echo "  - OpenAI API Key"
echo "  - Stripe Keys"
echo "  - Any other required API keys"
wait_for_confirmation

# =============================================================================
# STEP 6: Docker Compose Configuration
# =============================================================================
print_step "6" "Docker Compose Configuration"
print_info "Creating Docker Compose configuration for production..."

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # DataGuardian Pro Application
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
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'

  # PostgreSQL Database
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
      - "127.0.0.1:5432:5432"  # Only bind to localhost
    restart: unless-stopped
    networks:
      - dataguardian-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dataguardian -d dataguardian_prod"]
      interval: 30s
      timeout: 10s
      retries: 5
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: dataguardian-redis
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "127.0.0.1:6379:6379"  # Only bind to localhost
    restart: unless-stopped
    networks:
      - dataguardian-network
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.25'

  # Nginx Reverse Proxy
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
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Certbot for SSL certificates
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
    driver: local
  redis_data:
    driver: local
  certbot_certs:
    driver: local
  certbot_www:
    driver: local

networks:
  dataguardian-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
EOF

print_success "Docker Compose configuration created"
wait_for_confirmation

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

    # Rate limiting for security
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
        server_name $DOMAIN www.$DOMAIN;
        
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
        server_name $DOMAIN www.$DOMAIN;

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

        # Rate limiting for auth endpoints
        location /auth {
            limit_req zone=login burst=5 nodelay;
            proxy_pass http://dataguardian;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

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
wait_for_confirmation

# =============================================================================
# STEP 8: Management Scripts
# =============================================================================
print_step "8" "Management Scripts Creation"
print_info "Creating management and monitoring scripts..."

# Backup script
cat > backup.sh << 'EOF'
#!/bin/bash
# DataGuardian Pro Backup Script for Hetzner

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
docker-compose exec -T redis redis-cli -a $REDIS_PASSWORD --rdb /data/dump_$DATE.rdb
docker cp dataguardian-redis:/data/dump_$DATE.rdb $BACKUP_DIR/

# Application data backup
echo "📁 Backing up application data..."
tar -czf $BACKUP_DIR/data_backup_$DATE.tar.gz data/ logs/ reports/ config/ --exclude='*.tmp'

# SSL certificates backup
echo "🔒 Backing up SSL certificates..."
docker run --rm -v certbot_certs:/source -v $BACKUP_DIR:/backup alpine tar -czf /backup/ssl_backup_$DATE.tar.gz -C /source .

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
# DataGuardian Pro Status Check

echo "🚀 DataGuardian Pro - System Status"
echo "==================================="

echo "📊 Container Status:"
docker-compose ps

echo ""
echo "💾 Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo ""
echo "🌐 Service Health:"
echo -n "Application: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/_stcore/health || echo "❌"
echo ""

echo -n "Nginx Proxy: "
curl -s -o /dev/null -w "%{http_code}" http://localhost/health || echo "❌"
echo ""

echo -n "Database: "
docker-compose exec -T postgres pg_isready -U dataguardian -d dataguardian_prod && echo "✅ Ready" || echo "❌ Not Ready"

echo -n "Redis: "
docker-compose exec -T redis redis-cli -a $REDIS_PASSWORD ping && echo "✅ PONG" || echo "❌ No Response"

echo ""
echo "💿 Disk Usage:"
df -h /opt/dataguardian

echo ""
echo "🔍 Recent Logs (Last 10 lines):"
docker-compose logs --tail=10 dataguardian
EOF

# Make scripts executable
chmod +x backup.sh status.sh

print_success "Management scripts created"
print_info "Available scripts:"
echo "  • backup.sh - Database and file backups"
echo "  • status.sh - System status check"
wait_for_confirmation

# =============================================================================
# STEP 9: Systemd Service
# =============================================================================
print_step "9" "Systemd Service Configuration"
print_info "Creating systemd service for auto-start..."

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

print_success "Systemd service created and enabled"
wait_for_confirmation

# =============================================================================
# STEP 10: Application Files Upload Instructions
# =============================================================================
print_step "10" "Application Files Upload"
print_warning "APPLICATION SOURCE CODE UPLOAD REQUIRED!"
echo ""
echo "You need to upload your DataGuardian Pro source code to this server."
echo "Current directory: /opt/dataguardian"
echo ""
echo "Upload methods:"
echo "1. SCP: scp -r /local/dataguardian-pro/* root@$DOMAIN:/opt/dataguardian/"
echo "2. Git clone: git clone your-repo-url /tmp/dataguardian && cp -r /tmp/dataguardian/* ."
echo "3. Upload via file manager/SFTP"
echo ""
print_warning "Required files in /opt/dataguardian:"
echo "  ✓ app.py (main Streamlit application)"
echo "  ✓ requirements.txt (Python dependencies)"
echo "  ✓ Dockerfile"
echo "  ✓ All application source code"
echo ""
print_info "After uploading files, ensure you have a Dockerfile like this:"
cat << 'EOD'

FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

EXPOSE 5000
CMD ["streamlit", "run", "app.py", "--server.port=5000", "--server.address=0.0.0.0", "--server.headless=true"]

EOD

echo ""
print_warning "Upload your source code now, then press Enter to continue..."
read -r

# Check if essential files exist
if [ ! -f "app.py" ]; then
    print_error "app.py not found! Please upload your application files."
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found! Please upload your application files."
    exit 1
fi

if [ ! -f "Dockerfile" ]; then
    print_warning "Dockerfile not found! Creating a basic one..."
    cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data logs reports config

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/_stcore/health || exit 1

# Run application
CMD ["streamlit", "run", "app.py", "--server.port=5000", "--server.address=0.0.0.0", "--server.headless=true"]
EOF
fi

print_success "Application files verified"
wait_for_confirmation

# =============================================================================
# STEP 11: Build and Start Application
# =============================================================================
print_step "11" "Build and Start Application"
print_info "Building Docker images and starting services..."

# Build the application
print_info "Building DataGuardian Pro Docker image..."
docker-compose build

# Start the services
print_info "Starting all services..."
docker-compose up -d

# Wait for services to be ready
print_info "Waiting for services to start..."
sleep 30

# Check status
docker-compose ps

print_success "Application services started"
wait_for_confirmation

# =============================================================================
# STEP 12: SSL Certificate Setup
# =============================================================================
print_step "12" "SSL Certificate Setup"
print_info "Setting up Let's Encrypt SSL certificates..."

# First, ensure domain is pointing to this server
print_warning "Before continuing, ensure your domain $DOMAIN points to this server!"
echo "Server IP: $(curl -s ifconfig.me)"
echo "Check with: nslookup $DOMAIN"
wait_for_confirmation

# Generate initial certificate
print_info "Generating initial SSL certificate..."
docker-compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

# Restart nginx to load certificates
docker-compose restart nginx

print_success "SSL certificates generated and installed"
wait_for_confirmation

# =============================================================================
# STEP 13: Security and Monitoring Setup
# =============================================================================
print_step "13" "Security and Monitoring Setup"
print_info "Setting up security features and monitoring..."

# Install and configure Fail2Ban
apt install -y fail2ban

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

# Setup log rotation
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
        docker-compose -f /opt/dataguardian/docker-compose.yml restart dataguardian
    endscript
}

/opt/dataguardian/nginx-logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker-compose -f /opt/dataguardian/docker-compose.yml restart nginx
    endscript
}
EOF

# Setup automated backups
crontab -l 2>/dev/null | { cat; echo "0 2 * * * /opt/dataguardian/backup.sh >> /opt/dataguardian/logs/backup.log 2>&1"; } | crontab -
crontab -l 2>/dev/null | { cat; echo "0 3 * * 0 /usr/local/bin/docker-compose -f /opt/dataguardian/docker-compose.yml restart certbot"; } | crontab -

print_success "Security and monitoring configured"
wait_for_confirmation

# =============================================================================
# STEP 14: Final Verification and Testing
# =============================================================================
print_step "14" "Final Verification and Testing"
print_info "Performing final system verification..."

# Test application
print_info "Testing application endpoints..."

sleep 10

# Test local application
if curl -f http://localhost:5000 > /dev/null 2>&1; then
    print_success "✅ Application responding on port 5000"
else
    print_error "❌ Application not responding on port 5000"
fi

# Test nginx health
if curl -f http://localhost/health > /dev/null 2>&1; then
    print_success "✅ Nginx health check passing"
else
    print_error "❌ Nginx health check failing"
fi

# Test HTTPS
if curl -f https://$DOMAIN/health > /dev/null 2>&1; then
    print_success "✅ HTTPS endpoint working"
else
    print_warning "⚠️  HTTPS endpoint not working (may need time for SSL to propagate)"
fi

# Show container status
echo ""
print_info "Final container status:"
docker-compose ps

print_success "System verification completed"
wait_for_confirmation

# =============================================================================
# DEPLOYMENT COMPLETE
# =============================================================================

echo ""
echo "🎉 DataGuardian Pro Hetzner Deployment Complete!"
echo "==============================================="
echo ""
echo "📋 Deployment Summary:"
echo "• Server: Hetzner Cloud with Ubuntu 22.04"
echo "• Application URL: https://$DOMAIN"
echo "• Application Directory: /opt/dataguardian"
echo "• Database: PostgreSQL (containerized)"
echo "• Cache: Redis (containerized)"
echo "• Web Server: Nginx with SSL/TLS"
echo "• SSL Certificates: Let's Encrypt"
echo ""
echo "🔧 Next Steps:"
echo "1. Update /opt/dataguardian/.env with your actual API keys:"
echo "   - OPENAI_API_KEY"
echo "   - STRIPE_SECRET_KEY"
echo "   - STRIPE_PUBLISHABLE_KEY"
echo "2. Restart application: systemctl restart dataguardian"
echo "3. Visit https://$DOMAIN to access DataGuardian Pro"
echo ""
echo "📊 Management Commands:"
echo "• Check status: cd /opt/dataguardian && ./status.sh"
echo "• View logs: cd /opt/dataguardian && docker-compose logs -f"
echo "• Restart services: systemctl restart dataguardian"
echo "• Run backup: cd /opt/dataguardian && ./backup.sh"
echo "• Update application: cd /opt/dataguardian && docker-compose build && systemctl restart dataguardian"
echo ""
echo "🌐 Access Points:"
echo "• HTTPS: https://$DOMAIN"
echo "• Direct access: http://$(curl -s ifconfig.me):5000 (for testing only)"
echo ""
echo "🔐 Security Features Enabled:"
echo "✅ SSL/TLS encryption with Let's Encrypt"
echo "✅ UFW firewall configured"
echo "✅ Fail2Ban intrusion detection"
echo "✅ Rate limiting"
echo "✅ Security headers"
echo "✅ Automated backups (daily at 2 AM)"
echo "✅ Log rotation"
echo "✅ Container security"
echo ""
echo "💰 Estimated Monthly Costs (Hetzner):"
echo "• CAX11 (2 vCPUs, 4GB RAM): €4.15/month"
echo "• Backup storage: €0.60/month (optional)"
echo "• Domain: ~€10/year"
echo "• Total: ~€5/month + domain"
echo ""

# Save deployment information
cat > deployment_info.txt << EOF
DataGuardian Pro Hetzner Deployment Information
==============================================
Deployment Date: $(date)
Server IP: $(curl -s ifconfig.me)
Domain: $DOMAIN
SSL Email: $EMAIL

Database Credentials:
- Database: dataguardian_prod
- Username: dataguardian
- Password: $DB_PASSWORD

Redis Password: $REDIS_PASSWORD
JWT Secret: $JWT_SECRET
Encryption Key: $ENCRYPTION_KEY

Important Directories:
- Application: /opt/dataguardian
- Logs: /opt/dataguardian/logs
- Backups: /opt/dataguardian/backups
- SSL Certificates: Docker volume (certbot_certs)

Service Management:
- Start/Stop: systemctl start/stop dataguardian
- Status: systemctl status dataguardian
- Logs: docker-compose logs -f
- Backup: ./backup.sh
- Status Check: ./status.sh

Next Steps:
1. Update .env with real API keys
2. Test all functionality
3. Configure monitoring
4. Setup off-site backups
EOF

chmod 600 deployment_info.txt

print_success "🚀 DataGuardian Pro deployment completed successfully!"
print_info "Deployment information saved to: /opt/dataguardian/deployment_info.txt"
print_warning "IMPORTANT: Update your API keys in .env before going live!"

echo ""
echo "Happy hosting with DataGuardian Pro on Hetzner! 🇳🇱"