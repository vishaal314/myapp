#!/bin/bash

# DataGuardian Pro Production Deployment Script
# Usage: ./deploy.sh [environment] [domain] [email]
# Example: ./deploy.sh production mydomain.com admin@mydomain.com

set -e

ENVIRONMENT=${1:-production}
DOMAIN=${2:-""}
EMAIL=${3:-""}
PROJECT_DIR="/opt/dataguardian-pro"
BACKUP_DIR="/opt/dataguardian-pro/backups"
LOG_FILE="/opt/dataguardian-pro/logs/deployment.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    mkdir -p "$(dirname "$LOG_FILE")"
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    mkdir -p "$(dirname "$LOG_FILE")"
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    mkdir -p "$(dirname "$LOG_FILE")"
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    mkdir -p "$(dirname "$LOG_FILE")"
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root (use sudo)"
    fi
}

# Get user input if not provided
get_user_input() {
    if [[ -z "$DOMAIN" ]]; then
        echo -e "${YELLOW}Please enter your domain name (e.g., mydomain.com):${NC}"
        read -r DOMAIN
        if [[ -z "$DOMAIN" ]]; then
            error "Domain name is required"
        fi
    fi

    if [[ -z "$EMAIL" ]]; then
        echo -e "${YELLOW}Please enter your email address for SSL certificates:${NC}"
        read -r EMAIL
        if [[ -z "$EMAIL" ]]; then
            error "Email address is required"
        fi
    fi

    log "Deployment Configuration:"
    log "  Environment: $ENVIRONMENT"
    log "  Domain: $DOMAIN"
    log "  Email: $EMAIL"
    log "  Installation Directory: $PROJECT_DIR"
    echo ""
    
    read -p "Continue with deployment? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled."
        exit 1
    fi
}

# Check for port conflicts
check_port_conflicts() {
    log "Checking for port conflicts..."
    
    local conflicting_services=()
    
    # Check port 80
    if netstat -tuln 2>/dev/null | grep -q ":80 " || ss -tuln 2>/dev/null | grep -q ":80 "; then
        conflicting_services+=("port 80 (HTTP)")
    fi
    
    # Check port 443
    if netstat -tuln 2>/dev/null | grep -q ":443 " || ss -tuln 2>/dev/null | grep -q ":443 "; then
        conflicting_services+=("port 443 (HTTPS)")
    fi
    
    if [[ ${#conflicting_services[@]} -gt 0 ]]; then
        warning "Detected services using required ports: ${conflicting_services[*]}"
        warning "You may need to stop existing web servers before continuing"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    mkdir -p "$PROJECT_DIR"/{data,logs,cache,reports,backups,ssl,certbot-var}
    mkdir -p "$BACKUP_DIR"/{database,files}
    
    # Ensure log file exists
    touch "$LOG_FILE"
    chmod 644 "$LOG_FILE"
}

# Install Docker if not present
install_docker() {
    if ! command -v docker &> /dev/null; then
        log "Installing Docker..."
        
        # Add Docker's official GPG key and repository
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # Install Docker
        apt-get update
        apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        
        systemctl enable docker
        systemctl start docker
        
        # Add user to docker group
        groupadd -f docker
        usermod -aG docker $SUDO_USER 2>/dev/null || true
    else
        log "Docker already installed"
    fi

    # Verify Docker installation
    docker --version || error "Docker installation failed"
    docker compose version || error "Docker Compose installation failed"
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
    log "Setting up SSL certificates with Let's Encrypt..."
    
    # Create webroot directory
    mkdir -p /var/www/html
    
    # Create temporary nginx config for initial certificate
    cat > /tmp/nginx-ssl-setup.conf << EOF
events {}
http {
    server {
        listen 80;
        server_name $DOMAIN;
        
        location /.well-known/acme-challenge/ {
            root /var/www/html;
        }
        
        location / {
            return 200 'DataGuardian Pro - Certificate Setup in Progress';
            add_header Content-Type text/plain;
        }
    }
}
EOF

    # Start temporary nginx for certificate generation
    docker run -d --name temp-nginx \
        -p 80:80 \
        -v /tmp/nginx-ssl-setup.conf:/etc/nginx/nginx.conf:ro \
        -v /var/www/html:/var/www/html \
        nginx:alpine

    sleep 5

    # Generate certificates
    log "Requesting SSL certificate from Let's Encrypt..."
    docker run --rm \
        -v "$PROJECT_DIR/ssl":/etc/letsencrypt \
        -v "$PROJECT_DIR/certbot-var":/var/lib/letsencrypt \
        -v /var/www/html:/var/www/html \
        certbot/certbot \
        certonly \
        --webroot \
        --webroot-path=/var/www/html \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        --domains "$DOMAIN"

    # Stop temporary nginx
    docker stop temp-nginx && docker rm temp-nginx
    rm -f /tmp/nginx-ssl-setup.conf

    log "SSL certificates generated successfully"
}

# Setup SSL certificate renewal automation
setup_ssl_renewal() {
    log "Setting up SSL certificate renewal automation..."
    
    cat > "$PROJECT_DIR/ssl-renew.sh" << 'EOF'
#!/bin/bash

PROJECT_DIR="/opt/dataguardian-pro"
LOG_FILE="$PROJECT_DIR/logs/ssl-renewal.log"

# Function to log messages
log_ssl() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Check if certificates need renewal (30 days before expiry)
log_ssl "Checking SSL certificate expiration..."

cd "$PROJECT_DIR"

# Run certbot renew using running container
if docker exec dataguardian-certbot certbot renew --quiet; then
    log_ssl "Certificate renewal check completed successfully"
    
    # Reload nginx to use new certificates
    if docker exec dataguardian-nginx nginx -s reload 2>/dev/null; then
        log_ssl "Nginx reloaded successfully"
    else
        log_ssl "Nginx reload failed, restarting nginx container"
        docker compose -f docker-compose.prod.yml restart nginx
    fi
    
    # Test HTTPS after renewal
    if curl -f --max-time 10 "https://$(grep DOMAIN .env | cut -d'=' -f2)" >/dev/null 2>&1; then
        log_ssl "HTTPS health check passed after renewal"
    else
        log_ssl "WARNING: HTTPS health check failed after renewal"
    fi
else
    log_ssl "ERROR: Certificate renewal failed"
fi
EOF

    chmod +x "$PROJECT_DIR/ssl-renew.sh"
    
    # Schedule SSL renewal twice daily (3:15 AM and 3:15 PM)
    (crontab -l 2>/dev/null; echo "15 3,15 * * * $PROJECT_DIR/ssl-renew.sh") | crontab -
    
    log "SSL certificate renewal automation configured"
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

# Generate secure passwords and keys
generate_secrets() {
    log "Generating secure passwords and API keys..."
    
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    SECRET_KEY=$(openssl rand -hex 32)
    
    log "Secure credentials generated"
}

# Create environment configuration
create_env_file() {
    log "Creating production environment file..."
    
    cat > "$PROJECT_DIR/.env" << EOF
# Production Environment Configuration
ENVIRONMENT=production
DEBUG=false

# Domain Configuration
DOMAIN=$DOMAIN
ALLOWED_HOSTS=$DOMAIN,localhost,127.0.0.1

# Database Configuration
DATABASE_URL=postgresql://dataguardian_pro:$DB_PASSWORD@postgres:5432/dataguardian_pro
DB_USER=dataguardian_pro
DB_PASSWORD=$DB_PASSWORD

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Security Configuration
SECRET_KEY=$SECRET_KEY
SSL_ENABLED=true
FORCE_HTTPS=true
SESSION_SECURE=true

# Performance Configuration
REDIS_CACHE_TTL=3600
SESSION_TIMEOUT=7200
MAX_UPLOAD_SIZE=100MB

# SSL Configuration
SSL_CERT_EMAIL=$EMAIL

# API Keys (Update these with your actual keys)
OPENAI_API_KEY=your_openai_api_key_here
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret_here

# Logging Configuration
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=30
EOF

    # Set secure permissions
    chmod 600 "$PROJECT_DIR/.env"
    
    log "Environment file created successfully"
}

# Update system packages
update_system() {
    log "Updating system packages..."
    export DEBIAN_FRONTEND=noninteractive
    apt-get update
    apt-get upgrade -y
    apt-get install -y \
        curl \
        wget \
        git \
        htop \
        nano \
        ufw \
        fail2ban \
        openssl \
        ca-certificates \
        gnupg \
        lsb-release \
        unzip \
        jq \
        net-tools
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
    
    log "Fail2ban configured successfully"
}

# Create docker-compose configuration
create_docker_compose() {
    log "Creating Docker Compose configuration..."
    
    cat > "$PROJECT_DIR/docker-compose.prod.yml" << 'EOF'
version: '3.8'

services:
  dataguardian-pro:
    image: dataguardian-pro:latest
    container_name: dataguardian-pro
    restart: unless-stopped
    pull_policy: never
    ports:
      - "127.0.0.1:5000:5000"
    environment:
      - ENVIRONMENT=${ENVIRONMENT}
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - SECRET_KEY=${SECRET_KEY}
      - DOMAIN=${DOMAIN}
      - SSL_ENABLED=${SSL_ENABLED}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./cache:/app/cache
      - ./reports:/app/reports
    networks:
      - dataguardian-network
    depends_on:
      - postgres
      - redis
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:5000/_stcore/health', timeout=5)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  postgres:
    image: postgres:16
    container_name: dataguardian-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: dataguardian_pro
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - dataguardian-network
    command: >
      postgres
      -c max_connections=200
      -c shared_buffers=256MB
      -c effective_cache_size=1GB
      -c maintenance_work_mem=64MB
      -c checkpoint_completion_target=0.9
      -c wal_buffers=16MB
      -c default_statistics_target=100
      -c random_page_cost=1.1

  redis:
    image: redis:7-alpine
    container_name: dataguardian-redis
    restart: unless-stopped
    command: >
      redis-server
      --appendonly yes
      --maxmemory 512mb
      --maxmemory-policy allkeys-lru
      --save 900 1
      --save 300 10
      --save 60 10000
    volumes:
      - redis_data:/data
    networks:
      - dataguardian-network

  nginx:
    image: nginx:alpine
    container_name: dataguardian-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/letsencrypt:ro
      - ./certbot-var:/var/lib/letsencrypt
      - /var/www/html:/var/www/html
      - nginx_logs:/var/log/nginx
    networks:
      - dataguardian-network
    depends_on:
      - dataguardian-pro

  certbot:
    image: certbot/certbot
    container_name: dataguardian-certbot
    volumes:
      - ./ssl:/etc/letsencrypt
      - ./certbot-var:/var/lib/letsencrypt
      - /var/www/html:/var/www/html
    command: echo "Certbot container ready for renewals"

volumes:
  postgres_data:
  redis_data:
  nginx_logs:

networks:
  dataguardian-network:
    driver: bridge
EOF

    log "Docker Compose configuration created successfully"
}

# Create nginx configuration
create_nginx_config() {
    log "Creating Nginx configuration..."
    
    cat > "$PROJECT_DIR/nginx.conf" << EOF
events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Logging
    log_format main '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                   '\$status \$body_bytes_sent "\$http_referer" '
                   '"\$http_user_agent" "\$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;
    
    # Performance optimizations
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    upstream dataguardian_backend {
        server dataguardian-pro:5000;
    }
    
    # HTTP redirect to HTTPS
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
    
    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name $DOMAIN www.$DOMAIN;
        
        ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
        
        # Modern SSL configuration
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 1h;
        ssl_session_tickets off;
        
        # OCSP stapling
        ssl_stapling on;
        ssl_stapling_verify on;
        
        location / {
            proxy_pass http://dataguardian_backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            
            # WebSocket support for Streamlit
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_read_timeout 86400;
            proxy_cache_bypass \$http_upgrade;
            
            # Security headers
            proxy_set_header X-Forwarded-Host \$server_name;
            proxy_set_header X-Forwarded-Server \$host;
        }
        
        # Static file caching
        location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
            proxy_pass http://dataguardian_backend;
            expires 1y;
            add_header Cache-Control "public, immutable";
            add_header X-Content-Type-Options nosniff;
        }
        
        # Health check endpoint
        location /health {
            proxy_pass http://dataguardian_backend/_stcore/health;
            access_log off;
        }
    }
}
EOF

    log "Nginx configuration created successfully"
}

# Create Dockerfile
create_dockerfile() {
    log "Creating Dockerfile..."
    
    cat > "$PROJECT_DIR/Dockerfile" << 'EOF'
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    postgresql-client \
    tesseract-ocr \
    tesseract-ocr-nld \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip cache purge

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs reports data temp cache

# Set environment variables
ENV ENVIRONMENT=production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=5000
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Create user for security
RUN useradd --create-home --shell /bin/bash dataguardian && \
    chown -R dataguardian:dataguardian /app
USER dataguardian

# Create Streamlit config
RUN mkdir -p ~/.streamlit && \
    echo '[server]\n\
headless = true\n\
address = "0.0.0.0"\n\
port = 5000\n\
enableCORS = false\n\
enableXsrfProtection = false\n\
maxUploadSize = 100\n\
\n\
[browser]\n\
gatherUsageStats = false\n\
\n\
[theme]\n\
base = "light"' > ~/.streamlit/config.toml

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/_stcore/health', timeout=5)" || exit 1

# Run application
CMD ["streamlit", "run", "app.py", "--server.port", "5000", "--server.address", "0.0.0.0", "--server.headless", "true"]
EOF

    log "Dockerfile created successfully"
}

# Create minimal application if files are missing
create_minimal_application() {
    log "Creating minimal application structure..."
    
    # Create basic app.py
    if [[ ! -f "app.py" ]]; then
        cat > app.py << 'EOF'
import streamlit as st
import os

st.set_page_config(
    page_title="DataGuardian Pro",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ DataGuardian Pro - Setup Required")
st.warning("This is a placeholder application. Please upload your complete DataGuardian Pro files.")

st.subheader("Environment Status")
env_vars = ["DATABASE_URL", "REDIS_URL", "ENVIRONMENT", "DOMAIN", "OPENAI_API_KEY", "STRIPE_SECRET_KEY"]
for var in env_vars:
    value = os.getenv(var)
    if value:
        st.success(f"✅ {var}: Configured")
    else:
        st.error(f"❌ {var}: Missing")

st.subheader("Next Steps")
st.info("""
1. Upload your complete DataGuardian Pro application files to: /opt/dataguardian-pro/
2. Update API keys in the .env file
3. Rebuild and restart the Docker containers
4. Access your application at: https://""" + os.getenv('DOMAIN', 'your-domain.com'))
EOF
    fi
    
    # Create basic requirements.txt
    if [[ ! -f "requirements.txt" ]] && [[ ! -f "production_requirements.txt" ]]; then
        cat > requirements.txt << 'EOF'
streamlit>=1.28.0
pandas>=1.5.0
psycopg2-binary>=2.9.0
redis>=4.5.0
openai>=1.0.0
stripe>=7.0.0
bcrypt>=4.0.0
cryptography>=41.0.0
pillow>=10.0.0
reportlab>=4.0.0
beautifulsoup4>=4.12.0
requests>=2.31.0
python-jose>=3.3.0
pyjwt>=2.8.0
opencv-python-headless>=4.8.0
plotly>=5.17.0
trafilatura>=1.6.0
tldextract>=5.1.0
pyyaml>=6.0.1
EOF
    fi
    
    # Create Docker configurations
    create_docker_compose
    create_nginx_config
    create_dockerfile
}

# Validate application code exists
validate_application_code() {
    log "Validating application code..."
    
    cd "$PROJECT_DIR"
    
    # Check for essential files
    local missing_files=()
    
    if [[ ! -f "app.py" ]]; then
        missing_files+=("app.py")
    fi
    
    if [[ ! -f "requirements.txt" ]] && [[ ! -f "production_requirements.txt" ]]; then
        missing_files+=("requirements.txt or production_requirements.txt")
    fi
    
    if [[ ! -f "docker-compose.prod.yml" ]]; then
        missing_files+=("docker-compose.prod.yml")
    fi
    
    if [[ ${#missing_files[@]} -gt 0 ]]; then
        warning "Missing essential application files: ${missing_files[*]}"
        
        # Try to create basic application structure
        create_minimal_application
        
        warning "Basic application structure created. You should upload your complete DataGuardian Pro files."
        warning "Required files: app.py, requirements.txt, and all Python modules"
    else
        log "✅ Application code validation passed"
    fi
}

# Build and deploy application
deploy() {
    log "Building and deploying DataGuardian Pro..."
    
    cd "$PROJECT_DIR"
    
    # Backup before deployment
    backup_database
    
    # Generate secrets and create environment file
    generate_secrets
    create_env_file
    
    # Validate application code exists
    validate_application_code
    
    # Build Docker image if Dockerfile exists
    if [[ -f "Dockerfile" ]]; then
        log "Building Docker image..."
        docker build -t dataguardian-pro:latest .
    else
        warning "Dockerfile not found. Using basic configuration."
    fi
    
    # Start services
    log "Starting application services..."
    docker compose -f docker-compose.prod.yml up -d
    
    # Wait for services to start
    log "Waiting for services to initialize..."
    sleep 60
    
    # Health check
    log "Performing health checks..."
    local retries=0
    local max_retries=12
    
    while [[ $retries -lt $max_retries ]]; do
        if curl -f http://localhost:5000/_stcore/health &>/dev/null || curl -f http://localhost:5000 &>/dev/null; then
            log "✅ Application is healthy and running!"
            break
        else
            retries=$((retries + 1))
            log "Health check $retries/$max_retries - waiting for application..."
            sleep 10
        fi
    done
    
    if [[ $retries -eq $max_retries ]]; then
        warning "Application health check failed. Check logs with: docker compose -f $PROJECT_DIR/docker-compose.prod.yml logs"
    fi
}

# Setup log rotation
setup_log_rotation() {
    log "Setting up log rotation..."
    
    cat > /etc/logrotate.d/dataguardian-pro << EOF
$PROJECT_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 root root
    postrotate
        docker compose -f $PROJECT_DIR/docker-compose.prod.yml restart dataguardian-pro >/dev/null 2>&1 || true
    endscript
}

/var/log/nginx/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    sharedscripts
    postrotate
        docker exec dataguardian-nginx nginx -s reload >/dev/null 2>&1 || true
    endscript
}
EOF

    log "Log rotation configured successfully"
}

# Setup monitoring and health checks
setup_monitoring() {
    log "Setting up system monitoring..."
    
    cat > "$PROJECT_DIR/monitor.sh" << 'EOF'
#!/bin/bash

PROJECT_DIR="/opt/dataguardian-pro"
LOG_FILE="$PROJECT_DIR/logs/monitor.log"
ALERT_LOG="$PROJECT_DIR/logs/alerts.log"

# Function to log monitoring messages
log_monitor() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Function to log alerts
log_alert() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ALERT: $1" >> "$ALERT_LOG"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ALERT: $1" >> "$LOG_FILE"
}

# Check Docker services
check_services() {
    local failed_services=()
    
    for service in dataguardian-pro dataguardian-postgres dataguardian-redis dataguardian-nginx; do
        if ! docker ps --format "table {{.Names}}" | grep -q "^$service$"; then
            failed_services+=("$service")
        fi
    done
    
    if [[ ${#failed_services[@]} -gt 0 ]]; then
        log_alert "Failed services detected: ${failed_services[*]}"
        cd "$PROJECT_DIR"
        docker compose -f docker-compose.prod.yml up -d "${failed_services[@]}"
        log_monitor "Attempted to restart failed services: ${failed_services[*]}"
    fi
}

# Check disk space
check_disk_space() {
    local usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [[ $usage -gt 85 ]]; then
        log_alert "High disk usage detected: ${usage}%"
    elif [[ $usage -gt 75 ]]; then
        log_monitor "Disk usage warning: ${usage}%"
    fi
}

# Check memory usage
check_memory() {
    local mem_usage=$(free | awk '/^Mem:/{printf "%.1f", $3/$2 * 100.0}')
    local mem_usage_int=${mem_usage%.*}
    if [[ $mem_usage_int -gt 90 ]]; then
        log_alert "High memory usage detected: ${mem_usage}%"
    fi
}

# Check application health
check_health() {
    local health_endpoints=(
        "http://localhost:5000/_stcore/health"
        "http://localhost:5000"
    )
    
    local failed_checks=0
    for endpoint in "${health_endpoints[@]}"; do
        if ! curl -f --max-time 10 "$endpoint" >/dev/null 2>&1; then
            ((failed_checks++))
        fi
    done
    
    if [[ $failed_checks -eq ${#health_endpoints[@]} ]]; then
        log_alert "All application health checks failed"
        cd "$PROJECT_DIR"
        docker compose -f docker-compose.prod.yml restart dataguardian-pro
        log_monitor "Restarted application due to health check failures"
    fi
}

# Check SSL certificate expiration
check_ssl_expiry() {
    if [[ -f "$PROJECT_DIR/ssl/live/$(grep DOMAIN $PROJECT_DIR/.env | cut -d'=' -f2)/fullchain.pem" ]]; then
        local domain=$(grep DOMAIN "$PROJECT_DIR/.env" | cut -d'=' -f2)
        local expiry_date=$(openssl x509 -enddate -noout -in "$PROJECT_DIR/ssl/live/$domain/fullchain.pem" | cut -d= -f2)
        local expiry_epoch=$(date -d "$expiry_date" +%s)
        local current_epoch=$(date +%s)
        local days_until_expiry=$(( (expiry_epoch - current_epoch) / 86400 ))
        
        if [[ $days_until_expiry -lt 30 ]]; then
            log_alert "SSL certificate expires in $days_until_expiry days"
        fi
    fi
}

# Main monitoring execution
log_monitor "Starting monitoring checks..."
check_services
check_disk_space
check_memory
check_health
check_ssl_expiry

# Cleanup old logs (keep 30 days)
find "$PROJECT_DIR/logs" -name "*.log" -mtime +30 -delete

log_monitor "Monitoring checks completed"
EOF

    chmod +x "$PROJECT_DIR/monitor.sh"
    
    # Schedule monitoring every 5 minutes
    (crontab -l 2>/dev/null; echo "*/5 * * * * $PROJECT_DIR/monitor.sh") | crontab -
    
    log "System monitoring configured successfully"
}

# Setup automated backups
setup_backups() {
    log "Setting up automated backup system..."
    
    cat > "$PROJECT_DIR/backup.sh" << 'EOF'
#!/bin/bash

PROJECT_DIR="/opt/dataguardian-pro"
BACKUP_DIR="$PROJECT_DIR/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$PROJECT_DIR/logs/backup.log"

# Function to log backup messages
log_backup() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log_backup "Starting backup process..."

# Database backup
if docker ps -q -f name=dataguardian-postgres; then
    log_backup "Creating database backup..."
    if docker exec dataguardian-postgres pg_dump -U dataguardian_pro dataguardian_pro | gzip > "$BACKUP_DIR/database/backup_${TIMESTAMP}.sql.gz"; then
        log_backup "Database backup completed successfully"
    else
        log_backup "ERROR: Database backup failed"
    fi
else
    log_backup "WARNING: PostgreSQL container not running, skipping database backup"
fi

# Application data backup
log_backup "Creating application data backup..."
if tar -czf "$BACKUP_DIR/files/data_backup_${TIMESTAMP}.tar.gz" -C "$PROJECT_DIR" data reports cache 2>/dev/null; then
    log_backup "Application data backup completed successfully"
else
    log_backup "WARNING: Application data backup failed or no data to backup"
fi

# Configuration backup
log_backup "Creating configuration backup..."
if tar -czf "$BACKUP_DIR/files/config_backup_${TIMESTAMP}.tar.gz" -C "$PROJECT_DIR" .env docker-compose.prod.yml 2>/dev/null; then
    log_backup "Configuration backup completed successfully"
else
    log_backup "WARNING: Configuration backup failed"
fi

# SSL certificates backup (if exists)
if [[ -d "$PROJECT_DIR/ssl/live" ]]; then
    log_backup "Creating SSL certificates backup..."
    if tar -czf "$BACKUP_DIR/files/ssl_backup_${TIMESTAMP}.tar.gz" -C "$PROJECT_DIR" ssl 2>/dev/null; then
        log_backup "SSL certificates backup completed successfully"
    else
        log_backup "WARNING: SSL certificates backup failed"
    fi
fi

# Cleanup old backups (keep 7 days)
find "$BACKUP_DIR/database" -name "backup_*.sql.gz" -mtime +7 -delete
find "$BACKUP_DIR/files" -name "*_backup_*.tar.gz" -mtime +7 -delete

log_backup "Backup process completed successfully"
EOF

    chmod +x "$PROJECT_DIR/backup.sh"
    
    # Schedule daily backups at 2 AM
    (crontab -l 2>/dev/null; echo "0 2 * * * $PROJECT_DIR/backup.sh >/dev/null 2>&1") | crontab -
    
    log "Automated backup system configured successfully"
}

# Show deployment summary
show_summary() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              DataGuardian Pro Deployment Complete           ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    echo -e "${BLUE}🌐 Application URLs:${NC}"
    echo "   Primary: https://$DOMAIN"
    echo "   Health Check: https://$DOMAIN/health"
    echo ""
    
    echo -e "${BLUE}📁 Important Paths:${NC}"
    echo "   Installation: $PROJECT_DIR"
    echo "   Logs: $PROJECT_DIR/logs/"
    echo "   Backups: $PROJECT_DIR/backups/"
    echo "   Configuration: $PROJECT_DIR/.env"
    echo ""
    
    echo -e "${BLUE}🐳 Docker Services:${NC}"
    docker compose -f "$PROJECT_DIR/docker-compose.prod.yml" ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "Services starting..."
    echo ""
    
    echo -e "${BLUE}🔐 Security Features:${NC}"
    echo "   ✅ SSL/TLS certificates (Let's Encrypt)"
    echo "   ✅ Firewall configured (UFW)"
    echo "   ✅ Intrusion detection (Fail2ban)"
    echo "   ✅ Secure database passwords"
    echo ""
    
    echo -e "${BLUE}⚙️ Management Commands:${NC}"
    echo "   View logs: docker compose -f $PROJECT_DIR/docker-compose.prod.yml logs -f"
    echo "   Restart services: docker compose -f $PROJECT_DIR/docker-compose.prod.yml restart"
    echo "   Update application: cd $PROJECT_DIR && docker compose -f docker-compose.prod.yml up -d --build"
    echo "   Manual backup: $PROJECT_DIR/backup.sh"
    echo ""
    
    echo -e "${YELLOW}⚠️  Next Steps:${NC}"
    echo "   1. Update API keys in $PROJECT_DIR/.env:"
    echo "      - OPENAI_API_KEY=your_actual_openai_key"
    echo "      - STRIPE_SECRET_KEY=your_actual_stripe_key"
    echo ""
    echo "   2. Restart services after updating API keys:"
    echo "      docker compose -f $PROJECT_DIR/docker-compose.prod.yml restart dataguardian-pro"
    echo ""
    echo "   3. Access your application at: https://$DOMAIN"
    echo ""
    
    echo -e "${GREEN}🎉 DataGuardian Pro is now running successfully!${NC}"
}

# Cleanup function
cleanup() {
    log "Performing cleanup..."
    
    # Stop any temporary containers
    docker stop temp-nginx 2>/dev/null || true
    docker rm temp-nginx 2>/dev/null || true
    
    # Clean up temporary files
    rm -f /tmp/nginx-ssl-setup.conf
    
    log "Cleanup completed"
}

# Signal handlers
trap cleanup EXIT
trap 'error "Deployment interrupted by user"' INT TERM

# Main execution
main() {
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                 DataGuardian Pro Deployment                 ║${NC}"
    echo -e "${BLUE}║              Netherlands UAVG Compliance Platform           ║${NC}"
    echo -e "${BLUE}║                      Version 2025.1                         ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    check_root
    get_user_input
    check_port_conflicts
    
    log "=== DataGuardian Pro Deployment Started ==="
    
    create_directories
    update_system
    install_docker
    setup_firewall
    setup_fail2ban
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        setup_ssl
        setup_ssl_renewal
    else
        warning "Skipping SSL setup for non-production environment"
    fi
    
    deploy
    setup_log_rotation
    setup_backups
    setup_monitoring
    
    log "=== DataGuardian Pro Deployment Completed Successfully ==="
    
    show_summary
}

# Run main function with all arguments
main "$@"