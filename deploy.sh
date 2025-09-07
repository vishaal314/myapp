#!/bin/bash

# DataGuardian Pro Production Deployment Script
# Usage: ./deploy.sh [environment]

set -e

ENVIRONMENT=${1:-production}
PROJECT_DIR="/opt/dataguardian-pro"
BACKUP_DIR="/opt/dataguardian-pro/backups"
LOG_FILE="/opt/dataguardian-pro/logs/deployment.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    mkdir -p "$PROJECT_DIR"/{data,logs,cache,reports,backups,ssl}
    mkdir -p "$BACKUP_DIR/database"
    mkdir -p "$BACKUP_DIR/files"
}

# Install Docker if not present
install_docker() {
    if ! command -v docker &> /dev/null; then
        log "Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        systemctl enable docker
        systemctl start docker
        rm get-docker.sh
    else
        log "Docker already installed"
    fi

    if ! command -v docker-compose &> /dev/null; then
        log "Installing Docker Compose..."
        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    else
        log "Docker Compose already installed"
    fi
}

# Setup firewall
setup_firewall() {
    log "Configuring firewall..."
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw --force enable
}

# Create SSL certificates
setup_ssl() {
    log "Setting up SSL certificates..."
    
    # Create temporary nginx config for initial certificate
    cat > /tmp/nginx-ssl-setup.conf << 'EOF'
events {}
http {
    server {
        listen 80;
        server_name dataguardianpro.nl;
        
        location /.well-known/acme-challenge/ {
            root /var/www/html;
        }
        
        location / {
            return 301 https://$server_name$request_uri;
        }
    }
}
EOF

    # Start temporary nginx for certificate generation
    mkdir -p /var/www/html
    docker run -d --name temp-nginx -p 80:80 -v /tmp/nginx-ssl-setup.conf:/etc/nginx/nginx.conf -v /var/www/html:/var/www/html nginx:alpine

    # Generate certificates
    docker run --rm -v "$PROJECT_DIR/ssl":/etc/letsencrypt -v "$PROJECT_DIR/certbot-var":/var/lib/letsencrypt -v /var/www/html:/var/www/html certbot/certbot certonly --webroot --webroot-path=/var/www/html --email vishaal314@gmail.com --agree-tos --no-eff-email -d dataguardianpro.nl

    # Stop temporary nginx
    docker stop temp-nginx && docker rm temp-nginx
}

# Backup database
backup_database() {
    if docker ps -q -f name=dataguardian-postgres; then
        log "Creating database backup..."
        timestamp=$(date +%Y%m%d_%H%M%S)
        docker exec dataguardian-postgres pg_dump -U dataguardian_pro dataguardian_pro > "$BACKUP_DIR/database/backup_$timestamp.sql"
        
        # Keep only last 7 days of backups
        find "$BACKUP_DIR/database" -name "backup_*.sql" -mtime +7 -delete
    else
        warning "PostgreSQL container not running, skipping database backup"
    fi
}

# Load environment variables
create_env_file() {
    log "Creating production environment file..."
    
    cat > "$PROJECT_DIR/.env" << EOF
# Database Configuration
DATABASE_URL=postgresql://dataguardian_pro:dataguardian_secure_pass_2025@postgres:5432/dataguardian_pro
DB_USER=dataguardian_pro
DB_PASSWORD=dataguardian_secure_pass_2025

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Application Configuration
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=$(openssl rand -hex 32)

# Domain Configuration
DOMAIN=dataguardianpro.nl
ALLOWED_HOSTS=dataguardianpro.nl,localhost,127.0.0.1

# Performance Configuration
REDIS_CACHE_TTL=3600
SESSION_TIMEOUT=7200
MAX_UPLOAD_SIZE=100MB

# Security Configuration
SSL_ENABLED=true
FORCE_HTTPS=true
SESSION_SECURE=true
EOF
}

# Update system packages
update_system() {
    log "Updating system packages..."
    apt-get update
    apt-get upgrade -y
    apt-get install -y curl wget git htop nano ufw fail2ban openssl
}

# Configure fail2ban
setup_fail2ban() {
    log "Configuring fail2ban..."
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
}

# Main deployment function
deploy() {
    log "Starting DataGuardian Pro deployment..."
    
    cd "$PROJECT_DIR"
    
    # Backup before deployment
    backup_database
    
    # Create environment file
    create_env_file
    
    # Pull latest images and restart services
    log "Starting services..."
    docker-compose -f docker-compose.prod.yml up -d --build
    
    # Wait for services to be ready
    log "Waiting for services to start..."
    sleep 60
    
    # Health check
    log "Performing health check..."
    for i in {1..10}; do
        if curl -f http://localhost:5000 >/dev/null 2>&1; then
            log "✅ Application is healthy!"
            break
        fi
        log "Waiting for application to start... ($i/10)"
        sleep 10
    done
    
    # Setup log rotation
    cat > /etc/logrotate.d/dataguardian-pro << 'EOF'
/opt/dataguardian-pro/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 root root
    postrotate
        docker-compose -f /opt/dataguardian-pro/docker-compose.prod.yml restart dataguardian-pro
    endscript
}
EOF
    
    log "✅ DataGuardian Pro deployment completed successfully!"
    log "🌐 Application available at: https://dataguardianpro.nl"
}

# Main execution
main() {
    log "=== DataGuardian Pro Deployment Started ==="
    
    create_directories
    update_system
    install_docker
    setup_firewall
    setup_fail2ban
    
    if [ "$ENVIRONMENT" = "production" ]; then
        setup_ssl
    fi
    
    deploy
    
    log "=== Deployment Process Complete ==="
}

# Run main function
main "$@"