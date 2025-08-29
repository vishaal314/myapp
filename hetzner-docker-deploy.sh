#!/bin/bash
# DataGuardian Pro - Complete Hetzner + Docker Deployment Script
# Automated deployment to Hetzner Cloud with Docker setup

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

echo "🚀 DataGuardian Pro - Hetzner Docker Deployment"
echo "================================================"

# Update system and install dependencies
update_system() {
    print_step "Updating system packages..."
    apt update && apt upgrade -y
    apt install -y curl wget git unzip htop nano ufw
    print_status "System updated successfully."
}

# Install Docker and Docker Compose
install_docker() {
    print_step "Installing Docker..."
    
    if ! command -v docker &> /dev/null; then
        # Install Docker
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        
        # Add current user to docker group
        usermod -aG docker $USER
        
        # Start and enable Docker
        systemctl start docker
        systemctl enable docker
        
        print_status "Docker installed successfully."
    else
        print_status "Docker already installed."
    fi
    
    # Install Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
        print_status "Docker Compose installed successfully."
    else
        print_status "Docker Compose already installed."
    fi
    
    # Verify installation
    docker --version
    docker-compose --version
}

# Configure firewall
setup_firewall() {
    print_step "Configuring firewall..."
    
    # Allow SSH (22), HTTP (80), HTTPS (443), and custom ports
    ufw allow OpenSSH
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 5000/tcp  # DataGuardian Pro direct access
    
    # Enable firewall
    ufw --force enable
    
    print_status "Firewall configured successfully."
}

# Create application directory and setup
setup_application() {
    print_step "Setting up application directory..."
    
    # Create application directory
    mkdir -p /opt/dataguardian
    cd /opt/dataguardian
    
    # Create necessary subdirectories
    mkdir -p data logs reports config ssl nginx-logs backups
    
    # Set proper permissions
    chmod 755 data logs reports config
    chmod 700 ssl
    
    print_status "Application directory created: /opt/dataguardian"
}

# Generate environment configuration
create_env_config() {
    print_step "Creating environment configuration..."
    
    cat > .env << 'EOF'
# DataGuardian Pro - Hetzner Production Environment

# Application Settings
ENVIRONMENT=production
APP_NAME=DataGuardian Pro
APP_VERSION=1.0.0

# Database Configuration
DATABASE_URL=postgresql://dataguardian:DG_SecurePass_2024!@postgres:5432/dataguardian_prod
POSTGRES_DB=dataguardian_prod
POSTGRES_USER=dataguardian
POSTGRES_PASSWORD=DG_SecurePass_2024!

# Redis Configuration  
REDIS_URL=redis://:DG_RedisPass_2024!@redis:6379/0
REDIS_PASSWORD=DG_RedisPass_2024!

# Security Settings (Production Ready)
SAP_SSL_VERIFY=true
SALESFORCE_TIMEOUT=30
SAP_REQUEST_TIMEOUT=30
OIDC_TIMEOUT=30

# Stripe Configuration (Update with your keys)
STRIPE_PUBLISHABLE_KEY=pk_live_your_publishable_key_here
STRIPE_SECRET_KEY=sk_live_your_secret_key_here

# JWT and Encryption (Generate secure keys)
JWT_SECRET=your_secure_jwt_secret_minimum_32_characters_long_random_string
ENCRYPTION_KEY=your_32_character_encryption_key

# GDPR Compliance
DATA_RESIDENCY=EU
PRIVACY_POLICY_URL=https://yourdomain.com/privacy
TERMS_URL=https://yourdomain.com/terms

# Netherlands Specific
DEFAULT_COUNTRY=NL
DEFAULT_LANGUAGE=en
UAVG_COMPLIANCE=true

# Monitoring
LOG_LEVEL=INFO
ENABLE_DEBUG=false
HEALTH_CHECK_ENABLED=true

# Domain Configuration (Update with your domain)
DOMAIN_NAME=yourdomain.com
SSL_EMAIL=admin@yourdomain.com
EOF

    print_status "Environment configuration created. Please update with your actual values."
}

# Generate Docker Compose file for Hetzner
create_docker_compose() {
    print_step "Creating Docker Compose configuration..."
    
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
      - DATABASE_URL=postgresql://dataguardian:DG_SecurePass_2024!@postgres:5432/dataguardian_prod
      - REDIS_URL=redis://:DG_RedisPass_2024!@redis:6379/0
      - SAP_SSL_VERIFY=true
      - SALESFORCE_TIMEOUT=30
      - SAP_REQUEST_TIMEOUT=30
      - OIDC_TIMEOUT=30
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
    environment:
      POSTGRES_DB: dataguardian_prod
      POSTGRES_USER: dataguardian
      POSTGRES_PASSWORD: DG_SecurePass_2024!
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=C"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
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
    command: redis-server --appendonly yes --requirepass DG_RedisPass_2024!
    volumes:
      - redis_data:/data
    ports:
      - "127.0.0.1:6379:6379"  # Only bind to localhost
    restart: unless-stopped
    networks:
      - dataguardian-network
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "DG_RedisPass_2024!", "ping"]
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
    command: certonly --webroot --webroot-path=/var/www/certbot --email admin@yourdomain.com --agree-tos --no-eff-email -d yourdomain.com
    depends_on:
      - nginx

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

    print_status "Docker Compose configuration created."
}

# Generate Nginx configuration for Hetzner
create_nginx_config() {
    print_step "Creating Nginx configuration..."
    
    cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

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
        server_name yourdomain.com www.yourdomain.com;
        
        # Let's Encrypt ACME challenge
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
        
        # Health check
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
        
        # Redirect to HTTPS
        location / {
            return 301 https://$server_name$request_uri;
        }
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL Configuration
        ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
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
            include /etc/nginx/proxy_params;
        }

        # Main application
        location / {
            proxy_pass http://dataguardian;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
    }
}
EOF

    print_status "Nginx configuration created."
}

# Generate backup script
create_backup_script() {
    print_step "Creating backup script..."
    
    cat > backup.sh << 'EOF'
#!/bin/bash
# DataGuardian Pro Backup Script for Hetzner

BACKUP_DIR="/opt/dataguardian/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

echo "🔄 Starting backup process..."

# Backup database
echo "📊 Backing up PostgreSQL database..."
docker-compose exec -T postgres pg_dump -U dataguardian dataguardian_prod | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Backup Redis data
echo "🔄 Backing up Redis data..."
docker-compose exec -T redis redis-cli -a DG_RedisPass_2024! --rdb /data/dump_$DATE.rdb
docker cp dataguardian-redis:/data/dump_$DATE.rdb $BACKUP_DIR/

# Backup application data
echo "📁 Backing up application data..."
tar -czf $BACKUP_DIR/data_backup_$DATE.tar.gz data/ logs/ reports/ config/ --exclude='*.tmp'

# Backup SSL certificates
echo "🔒 Backing up SSL certificates..."
tar -czf $BACKUP_DIR/ssl_backup_$DATE.tar.gz ssl/ -C /etc/letsencrypt .

# Upload to external storage (optional - configure with your provider)
# rsync -av $BACKUP_DIR/ user@backup-server:/backups/dataguardian/

# Clean up old backups
echo "🧹 Cleaning up old backups..."
find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.rdb" -mtime +$RETENTION_DAYS -delete

echo "✅ Backup completed: $BACKUP_DIR"
echo "📊 Backup size: $(du -sh $BACKUP_DIR | cut -f1)"
EOF

    chmod +x backup.sh
    print_status "Backup script created: backup.sh"
}

# Setup SSL certificates with Let's Encrypt
setup_ssl() {
    print_step "Setting up SSL certificates..."
    
    print_warning "Please update nginx.conf and docker-compose.yml with your actual domain name before running this."
    print_warning "Run: docker-compose run --rm certbot to generate SSL certificates after updating domain."
    
    # Create directory for certbot
    mkdir -p ssl
    
    print_status "SSL setup prepared. Configure your domain and run certbot."
}

# Create systemd service for auto-start
create_systemd_service() {
    print_step "Creating systemd service..."
    
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

    # Enable and start service
    systemctl daemon-reload
    systemctl enable dataguardian.service
    
    print_status "Systemd service created and enabled."
}

# Setup monitoring and log rotation
setup_monitoring() {
    print_step "Setting up monitoring and log rotation..."
    
    # Install log rotation
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

    # Setup automated backup cron job
    echo "0 2 * * * /opt/dataguardian/backup.sh >> /opt/dataguardian/logs/backup.log 2>&1" | crontab -
    
    print_status "Monitoring and log rotation configured."
}

# Create deployment status check script
create_status_script() {
    print_step "Creating status check script..."
    
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
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/_stcore/health
echo ""

echo -n "Nginx Proxy: "
curl -s -o /dev/null -w "%{http_code}" http://localhost/health
echo ""

echo -n "Database: "
docker-compose exec -T postgres pg_isready -U dataguardian -d dataguardian_prod && echo "✅ Ready" || echo "❌ Not Ready"

echo -n "Redis: "
docker-compose exec -T redis redis-cli -a DG_RedisPass_2024! ping && echo "✅ PONG" || echo "❌ No Response"

echo ""
echo "💿 Disk Usage:"
df -h /opt/dataguardian

echo ""
echo "🔍 Recent Logs (Last 10 lines):"
docker-compose logs --tail=10 dataguardian
EOF

    chmod +x status.sh
    print_status "Status check script created: status.sh"
}

# Main deployment function
main() {
    print_status "Starting DataGuardian Pro deployment on Hetzner..."
    
    update_system
    install_docker
    setup_firewall
    setup_application
    create_env_config
    create_docker_compose
    create_nginx_config
    create_backup_script
    setup_ssl
    create_systemd_service
    setup_monitoring
    create_status_script
    
    echo ""
    echo "🎉 DataGuardian Pro Hetzner Deployment Complete!"
    echo "================================================="
    echo ""
    echo "📋 Next Steps:"
    echo "1. Update .env file with your actual API keys and settings"
    echo "2. Update docker-compose.yml and nginx.conf with your domain name"
    echo "3. Copy your DataGuardian Pro source code to /opt/dataguardian/"
    echo "4. Build and start: docker-compose build && docker-compose up -d"
    echo "5. Generate SSL certificates: docker-compose run --rm certbot"
    echo "6. Start service: systemctl start dataguardian"
    echo ""
    echo "📊 Management Commands:"
    echo "• Check status: ./status.sh"
    echo "• View logs: docker-compose logs -f"
    echo "• Backup: ./backup.sh"
    echo "• Restart: systemctl restart dataguardian"
    echo ""
    echo "🌐 Access Points:"
    echo "• Application: http://YOUR_SERVER_IP:5000"
    echo "• Proxy: http://YOUR_SERVER_IP"
    echo "• HTTPS: https://yourdomain.com (after SSL setup)"
    echo ""
    print_status "Deployment completed successfully! 🚀"
}

# Run main function
main "$@"