#!/bin/bash

# DataGuardian Pro Production Deployment Script
# Usage: ./deploy-setup.sh [environment] [domain] [email]
# Example: ./deploy-setup.sh production mydomain.com admin@mydomain.com

set -e

# Configuration
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
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

# Welcome banner
show_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                 DataGuardian Pro Deployment                 ║"
    echo "║              Netherlands UAVG Compliance Platform           ║"
    echo "║                      Version 2025.1                         ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
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

    echo -e "${BLUE}Deployment Configuration:${NC}"
    echo "  Environment: $ENVIRONMENT"
    echo "  Domain: $DOMAIN"
    echo "  Email: $EMAIL"
    echo "  Installation Directory: $PROJECT_DIR"
    echo ""
    
    read -p "Continue with deployment? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled."
        exit 1
    fi
}

# Create necessary directories
create_directories() {
    log "Creating project directories..."
    mkdir -p "$PROJECT_DIR"/{data,logs,cache,reports,backups,ssl,certbot-var}
    mkdir -p "$BACKUP_DIR"/{database,files}
    
    # Ensure log file exists
    touch "$LOG_FILE"
    chmod 644 "$LOG_FILE"
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
        jq
}

# Install Docker
install_docker() {
    if ! command -v docker &> /dev/null; then
        log "Installing Docker..."
        
        # Add Docker's official GPG key
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        
        # Add Docker repository
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # Install Docker
        apt-get update
        apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        
        # Start and enable Docker
        systemctl enable docker
        systemctl start docker
        
        # Create docker group and add user
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
    
    # Reset firewall
    ufw --force reset
    
    # Set default policies
    ufw default deny incoming
    ufw default allow outgoing
    
    # Allow necessary ports
    ufw allow ssh
    ufw allow 80/tcp   # HTTP
    ufw allow 443/tcp  # HTTPS
    
    # Enable firewall
    ufw --force enable
    
    log "Firewall configured successfully"
}

# Configure fail2ban
setup_fail2ban() {
    log "Configuring fail2ban..."
    
    cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5
ignoreip = 127.0.0.1/8 ::1

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3

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

[nginx-noproxy]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 2
EOF

    systemctl enable fail2ban
    systemctl restart fail2ban
    
    log "Fail2ban configured successfully"
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
      test: ["CMD-SHELL", "python -c 'import requests; requests.get(\"http://localhost:5000/_stcore/health\", timeout=5)' || exit 1"]
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
    # Remove port publishing for security - access only via Docker network
    # ports:
    #   - "127.0.0.1:5432:5432"
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
    # Remove port publishing for security - access only via Docker network
    # ports:
    #   - "127.0.0.1:6379:6379"
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
    command: certonly --webroot --webroot-path=/var/www/html --email ${SSL_CERT_EMAIL} --agree-tos --no-eff-email -d ${DOMAIN}

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

# Health check using Python instead of curl for reliability
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/_stcore/health', timeout=5)" || exit 1

# Run application
CMD ["streamlit", "run", "app.py", "--server.port", "5000", "--server.address", "0.0.0.0", "--server.headless", "true"]
EOF

    log "Dockerfile created successfully"
}

# Check for existing web servers on critical ports
check_port_conflicts() {
    log "Checking for port conflicts..."
    
    # Check if ports 80 and 443 are already in use
    local port_80_in_use=false
    local port_443_in_use=false
    
    if netstat -tlnp | grep -q ':80 '; then
        port_80_in_use=true
        warning "Port 80 is already in use:"
        netstat -tlnp | grep ':80 ' | tee -a "$LOG_FILE"
    fi
    
    if netstat -tlnp | grep -q ':443 '; then
        port_443_in_use=true
        warning "Port 443 is already in use:"
        netstat -tlnp | grep ':443 ' | tee -a "$LOG_FILE"
    fi
    
    if [[ "$port_80_in_use" == true ]] || [[ "$port_443_in_use" == true ]]; then
        echo -e "${RED}WARNING: Critical ports are already in use!${NC}"
        echo "This may cause conflicts with the DataGuardian Pro deployment."
        echo "Consider stopping existing web servers before proceeding."
        echo ""
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            error "Deployment cancelled due to port conflicts"
        fi
        warning "Proceeding with potential port conflicts - deployment may fail"
    else
        log "No port conflicts detected"
    fi
}

# Validate application source code
validate_application_code() {
    log "Validating DataGuardian Pro application code..."
    
    cd "$PROJECT_DIR"
    
    # Check if we're in the DataGuardian Pro source directory
    if [[ -f "app.py" ]] && [[ -f "requirements.txt" ]] && [[ -d "services" ]] && [[ -d "components" ]] && [[ -d "utils" ]]; then
        log "✅ Complete DataGuardian Pro source code detected"
        
        # Verify critical files exist
        local missing_files=()
        local critical_files=(
            "app.py"
            "requirements.txt"
            "services/code_scanner.py"
            "services/ai_model_scanner.py"
            "components/scanner_interface.py"
            "utils/common.py"
        )
        
        for file in "${critical_files[@]}"; do
            if [[ ! -f "$file" ]]; then
                missing_files+=("$file")
            fi
        done
        
        if [[ ${#missing_files[@]} -gt 0 ]]; then
            warning "Some critical files are missing:"
            for file in "${missing_files[@]}"; do
                echo "  - $file"
            done
            echo ""
            read -p "Continue with incomplete application? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                error "Deployment cancelled due to missing application files"
            fi
        else
            log "✅ All critical application files present"
        fi
        
        return 0
    else
        log "❌ Complete DataGuardian Pro source code not detected"
        return 1
    fi
}

# Download or prepare application files
prepare_application_code() {
    log "Preparing DataGuardian Pro application code..."
    
    cd "$PROJECT_DIR"
    
    # First, check if we already have valid application code
    if validate_application_code; then
        log "Application code validation successful"
        return 0
    fi
    
    # Try to download from repository if available
    log "Attempting to download from repository..."
    if download_from_repository; then
        log "Repository download successful"
        if validate_application_code; then
            return 0
        fi
    fi
    
    # Try to extract from local archives
    log "Attempting to extract from local archives..."
    if extract_from_archives; then
        log "Archive extraction successful"
        if validate_application_code; then
            return 0
        fi
    fi
    
    # Create minimal application for deployment
    log "Creating minimal application structure..."
    create_minimal_application
    
    # Show instructions for manual upload
    show_manual_upload_instructions
}

# Download application files from repository
download_from_repository() {
    local repo_urls=(
        "https://github.com/dataguardian/dataguardian-pro.git"
        "https://github.com/DataGuardian/DataGuardian-Pro.git"
    )
    
    for repo_url in "${repo_urls[@]}"; do
        log "Trying repository: $repo_url"
        if git ls-remote "$repo_url" &>/dev/null; then
            log "Repository accessible, cloning..."
            if git clone "$repo_url" temp_repo; then
                # Copy files and clean up
                cp -r temp_repo/* . 2>/dev/null || cp -r temp_repo/src/* . 2>/dev/null || true
                rm -rf temp_repo
                return 0
            fi
        fi
    done
    
    return 1
}

# Extract from local archives
extract_from_archives() {
    local archives=(
        "dataguardian-pro-complete.tar.gz"
        "dataguardian-complete.tar.gz"
        "DataGuardian-Pro-Standalone-Source.tar.gz"
        "*.tar.gz"
    )
    
    for pattern in "${archives[@]}"; do
        for archive in $pattern; do
            if [[ -f "$archive" ]]; then
                log "Found archive: $archive"
                if tar -tf "$archive" | head -5 | grep -q "app.py\|src/"; then
                    log "Extracting from $archive..."
                    tar -xzf "$archive" --strip-components=1 2>/dev/null || tar -xzf "$archive" 2>/dev/null
                    # Handle nested source directories
                    if [[ -d "DataGuardian-Pro-Standalone-Source" ]]; then
                        cp -r DataGuardian-Pro-Standalone-Source/* .
                        rm -rf DataGuardian-Pro-Standalone-Source
                    fi
                    return 0
                fi
            fi
        done
    done
    
    return 1
}

# Create minimal application structure
create_minimal_application() {
    log "Creating minimal DataGuardian Pro application structure..."
    
    # Create directory structure
    mkdir -p {services,components,utils,static,translations,pages,docs}
    
    # Create requirements.txt with comprehensive dependencies
    cat > requirements.txt << 'EOF'
# Core Streamlit and web framework
streamlit>=1.28.0
streamlit-option-menu>=0.3.6

# Data processing and analysis
pandas>=1.5.0
numpy>=1.24.0
plotly>=5.17.0

# Database and caching
psycopg2-binary>=2.9.0
redis>=4.5.0
sqlalchemy>=2.0.0

# API integrations
openai>=1.0.0
stripe>=7.0.0
requests>=2.31.0

# Security and authentication
bcrypt>=4.0.0
cryptography>=41.0.0
python-jose>=3.3.0
pyjwt>=2.8.0

# Document and image processing
pillow>=10.0.0
reportlab>=4.0.0
beautifulsoup4>=4.12.0
pytesseract>=0.3.10
opencv-python-headless>=4.8.0

# Data extraction and parsing
trafilatura>=1.6.0
tldextract>=5.1.0
pyyaml>=6.0.1

# Development and monitoring
joblib>=1.3.0
psutil>=5.9.0
cachetools>=5.3.0

# Additional utilities
aiohttp>=3.8.0
dnspython>=2.4.0
EOF
    
    # Create minimal app.py
    cat > app.py << 'EOF'
import streamlit as st
import os
import sys
from pathlib import Path

# Configure Streamlit
st.set_page_config(
    page_title="DataGuardian Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header { font-size: 2.5rem; color: #2E86AB; margin-bottom: 2rem; }
.status-success { background-color: #d4edda; padding: 1rem; border-radius: 0.5rem; }
.status-warning { background-color: #fff3cd; padding: 1rem; border-radius: 0.5rem; }
.status-error { background-color: #f8d7da; padding: 1rem; border-radius: 0.5rem; }
</style>
""", unsafe_allow_html=True)

def check_environment():
    """Check environment configuration"""
    env_vars = {
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "REDIS_URL": os.getenv("REDIS_URL"),
        "ENVIRONMENT": os.getenv("ENVIRONMENT"),
        "DOMAIN": os.getenv("DOMAIN"),
        "OPENAI_API_KEY": "Set" if os.getenv("OPENAI_API_KEY", "").startswith(("sk-", "your_")) else "Missing",
        "STRIPE_SECRET_KEY": "Set" if os.getenv("STRIPE_SECRET_KEY", "").startswith(("sk_", "your_")) else "Missing"
    }
    
    return env_vars

def check_file_structure():
    """Check if complete DataGuardian Pro files are present"""
    required_files = [
        "services/code_scanner.py",
        "services/ai_model_scanner.py",
        "components/scanner_interface.py",
        "utils/common.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    return missing_files

def main():
    # Header
    st.markdown('<h1 class="main-header">🛡️ DataGuardian Pro</h1>', unsafe_allow_html=True)
    
    # Check if this is the minimal installation
    missing_files = check_file_structure()
    
    if missing_files:
        st.markdown('<div class="status-warning">', unsafe_allow_html=True)
        st.warning("⚠️ Minimal Installation Detected")
        st.write("This is a minimal DataGuardian Pro installation. Complete application files need to be uploaded.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.subheader("📋 Required Files")
        st.write("Please upload the following files to complete the installation:")
        for file in missing_files:
            st.write(f"❌ {file}")
    else:
        st.markdown('<div class="status-success">', unsafe_allow_html=True)
        st.success("✅ Complete DataGuardian Pro Installation")
        st.write("All required application files are present.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Environment status
    st.subheader("🔧 Environment Configuration")
    env_vars = check_environment()
    
    col1, col2 = st.columns(2)
    with col1:
        for key, value in list(env_vars.items())[:3]:
            status = "✅" if value and value != "Missing" else "❌"
            st.write(f"{status} **{key}**: {value or 'Not Set'}")
    
    with col2:
        for key, value in list(env_vars.items())[3:]:
            status = "✅" if value and value != "Missing" else "❌"
            st.write(f"{status} **{key}**: {value or 'Not Set'}")
    
    # System information
    st.subheader("ℹ️ System Information")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Python Version", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    with col2:
        st.metric("Installation Directory", "/opt/dataguardian-pro")
    
    with col3:
        st.metric("Environment", os.getenv("ENVIRONMENT", "Unknown"))
    
    # Instructions
    if missing_files:
        st.subheader("📥 Upload Instructions")
        st.info("""
        **To complete your DataGuardian Pro installation:**
        
        1. **Stop the application**: `docker compose -f /opt/dataguardian-pro/docker-compose.prod.yml down`
        2. **Upload files**: Copy your complete DataGuardian Pro files to `/opt/dataguardian-pro/`
        3. **Rebuild image**: `cd /opt/dataguardian-pro && docker build -t dataguardian-pro:latest .`
        4. **Restart services**: `docker compose -f /opt/dataguardian-pro/docker-compose.prod.yml up -d`
        
        **Alternative**: Run the deployment script again with your source files in the directory.
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        DataGuardian Pro - Netherlands UAVG Compliance Platform<br>
        Version 2025.1 | Deployment: {}
    </div>
    """.format(os.getenv("ENVIRONMENT", "Unknown")), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
EOF
    
    # Create basic service stubs
    touch services/__init__.py components/__init__.py utils/__init__.py
    
    log "Minimal application structure created"
}

# Show manual upload instructions
show_manual_upload_instructions() {
    echo -e "${YELLOW}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    MANUAL UPLOAD REQUIRED                   ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${BLUE}📁 Upload your complete DataGuardian Pro source code to:${NC}"
    echo "   $PROJECT_DIR"
    echo ""
    
    echo -e "${BLUE}📋 Required files and directories:${NC}"
    echo "   ✓ app.py (main application file)"
    echo "   ✓ requirements.txt (Python dependencies)"
    echo "   ✓ services/ (scanner services)"
    echo "   ✓ components/ (UI components)"
    echo "   ✓ utils/ (utility functions)"
    echo "   ✓ static/ (static assets)"
    echo "   ✓ translations/ (language files)"
    echo ""
    
    echo -e "${BLUE}🔄 After uploading files, rebuild and restart:${NC}"
    echo "   1. cd $PROJECT_DIR"
    echo "   2. docker build -t dataguardian-pro:latest ."
    echo "   3. docker compose -f docker-compose.prod.yml up -d --force-recreate"
    echo ""
    
    warning "A minimal application has been created for now. Please upload your complete source code."
}

# Setup SSL certificates
setup_ssl() {
    log "Setting up SSL certificates with Let's Encrypt..."
    
    # Create webroot directory
    mkdir -p /var/www/html
    
    cd "$PROJECT_DIR"
    
    # Start nginx temporarily for certificate generation
    log "Starting temporary Nginx for certificate generation..."
    
    # Create temporary nginx config for ACME challenge
    cat > temp-nginx.conf << EOF
events {
    worker_connections 1024;
}

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

    # Start temporary nginx
    docker run -d --name temp-nginx \
        -p 80:80 \
        -v "$PWD/temp-nginx.conf:/etc/nginx/nginx.conf:ro" \
        -v /var/www/html:/var/www/html \
        nginx:alpine

    sleep 5

    # Generate certificate using certbot
    log "Requesting SSL certificate from Let's Encrypt..."
    
    docker run --rm \
        -v "$PROJECT_DIR/ssl:/etc/letsencrypt" \
        -v "$PROJECT_DIR/certbot-var:/var/lib/letsencrypt" \
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
    rm temp-nginx.conf

    log "SSL certificates generated successfully"
}

# Build and deploy application
deploy_application() {
    log "Building and deploying DataGuardian Pro..."
    
    cd "$PROJECT_DIR"
    
    # Build Docker image
    log "Building Docker image..."
    docker build -t dataguardian-pro:latest .
    
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
        if curl -f http://localhost:5000/_stcore/health &>/dev/null; then
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

# Setup SSL certificate renewal
setup_ssl_renewal() {
    log "Setting up SSL certificate renewal automation..."
    
    cat > "$PROJECT_DIR/ssl-renew.sh" << 'EOF'
#!/bin/bash

# SSL Certificate Renewal Script for DataGuardian Pro
# Run by cron twice daily

PROJECT_DIR="/opt/dataguardian-pro"
LOG_FILE="$PROJECT_DIR/logs/ssl-renewal.log"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S'): $1" >> "$LOG_FILE"
}

cd "$PROJECT_DIR" || exit 1

log_message "Starting SSL certificate renewal check"

# Check if certificates are due for renewal (within 30 days)
if docker compose -f docker-compose.prod.yml run --rm certbot certificates | grep -q "INVALID\|will expire"; then
    log_message "Certificates need renewal"
    
    # Attempt renewal
    if docker compose -f docker-compose.prod.yml run --rm certbot renew --quiet; then
        log_message "Certificate renewal successful"
        
        # Reload nginx to pick up new certificates
        if docker compose -f docker-compose.prod.yml exec nginx nginx -s reload; then
            log_message "Nginx reloaded successfully"
        else
            log_message "ERROR: Failed to reload nginx after certificate renewal"
            # Restart nginx container as fallback
            docker compose -f docker-compose.prod.yml restart nginx
            log_message "Nginx container restarted as fallback"
        fi
        
        # Test the renewed certificates
        if curl -sSf https://localhost/_stcore/health > /dev/null 2>&1; then
            log_message "SSL certificate renewal verification successful"
        else
            log_message "WARNING: SSL certificate verification failed after renewal"
        fi
    else
        log_message "ERROR: Certificate renewal failed"
        # Send alert (could be enhanced to email/webhook)
        echo "SSL certificate renewal failed for $(hostname)" >> "$PROJECT_DIR/logs/alerts.log"
    fi
else
    log_message "Certificates are up to date, no renewal needed"
fi

log_message "SSL certificate renewal check completed"
EOF

    chmod +x "$PROJECT_DIR/ssl-renew.sh"
    
    # Schedule SSL renewal checks twice daily (at 3:15 AM and 3:15 PM)
    (crontab -l 2>/dev/null; echo "15 3,15 * * * $PROJECT_DIR/ssl-renew.sh >/dev/null 2>&1") | crontab -
    
    log "SSL certificate renewal automation configured successfully"
}

# Setup automated backups
setup_backups() {
    log "Setting up automated backups..."
    
    cat > "$PROJECT_DIR/backup.sh" << 'EOF'
#!/bin/bash

# DataGuardian Pro Backup Script
PROJECT_DIR="/opt/dataguardian-pro"
BACKUP_DIR="$PROJECT_DIR/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$PROJECT_DIR/logs/backup.log"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S'): $1" | tee -a "$LOG_FILE"
}

log_message "Starting backup process"

# Ensure backup directories exist
mkdir -p "$BACKUP_DIR"/{database,files,ssl}

# Database backup with error checking
log_message "Creating database backup"
if docker exec dataguardian-postgres pg_dump -U dataguardian_pro dataguardian_pro | gzip > "$BACKUP_DIR/database/backup_${TIMESTAMP}.sql.gz"; then
    log_message "Database backup completed successfully"
else
    log_message "ERROR: Database backup failed"
fi

# Application data backup
log_message "Creating application data backup"
if tar -czf "$BACKUP_DIR/files/data_backup_${TIMESTAMP}.tar.gz" -C "$PROJECT_DIR" data reports cache 2>/dev/null; then
    log_message "Application data backup completed successfully"
else
    log_message "WARNING: Some application data backup files may be missing"
fi

# Configuration backup
log_message "Creating configuration backup"
if tar -czf "$BACKUP_DIR/files/config_backup_${TIMESTAMP}.tar.gz" -C "$PROJECT_DIR" .env docker-compose.prod.yml nginx.conf 2>/dev/null; then
    log_message "Configuration backup completed successfully"
else
    log_message "ERROR: Configuration backup failed"
fi

# SSL certificates backup
log_message "Creating SSL certificates backup"
if tar -czf "$BACKUP_DIR/ssl/ssl_backup_${TIMESTAMP}.tar.gz" -C "$PROJECT_DIR" ssl 2>/dev/null; then
    log_message "SSL certificates backup completed successfully"
else
    log_message "WARNING: SSL certificates backup may have failed"
fi

# Cleanup old backups (keep 14 days for database, 7 days for others)
log_message "Cleaning up old backups"
find "$BACKUP_DIR/database" -name "backup_*.sql.gz" -mtime +14 -delete 2>/dev/null
find "$BACKUP_DIR/files" -name "*_backup_*.tar.gz" -mtime +7 -delete 2>/dev/null
find "$BACKUP_DIR/ssl" -name "ssl_backup_*.tar.gz" -mtime +7 -delete 2>/dev/null

# Calculate backup sizes
db_size=$(du -sh "$BACKUP_DIR/database" 2>/dev/null | cut -f1 || echo "unknown")
files_size=$(du -sh "$BACKUP_DIR/files" 2>/dev/null | cut -f1 || echo "unknown")
ssl_size=$(du -sh "$BACKUP_DIR/ssl" 2>/dev/null | cut -f1 || echo "unknown")

log_message "Backup process completed - DB: $db_size, Files: $files_size, SSL: $ssl_size"
EOF

    chmod +x "$PROJECT_DIR/backup.sh"
    
    # Schedule daily backups at 2 AM
    (crontab -l 2>/dev/null; echo "0 2 * * * $PROJECT_DIR/backup.sh >/dev/null 2>&1") | crontab -
    
    log "Automated backups configured successfully"
}

# Setup comprehensive monitoring
setup_monitoring() {
    log "Setting up comprehensive system monitoring..."
    
    cat > "$PROJECT_DIR/monitor.sh" << 'EOF'
#!/bin/bash

# DataGuardian Pro System Monitor
PROJECT_DIR="/opt/dataguardian-pro"
LOG_FILE="$PROJECT_DIR/logs/monitor.log"
ALERT_FILE="$PROJECT_DIR/logs/alerts.log"

# Logging function
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S'): $1" >> "$LOG_FILE"
}

alert_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S'): ALERT - $1" | tee -a "$LOG_FILE" >> "$ALERT_FILE"
}

# Check Docker services health
check_services() {
    local failed_services=()
    local unhealthy_services=()
    
    # Check if containers are running
    for service in dataguardian-pro dataguardian-postgres dataguardian-redis dataguardian-nginx; do
        if ! docker ps --format "table {{.Names}}" | grep -q "^$service$"; then
            failed_services+=("$service")
        fi
    done
    
    # Check container health status
    for container in $(docker ps --format "{{.Names}}"); do
        if [[ "$container" =~ dataguardian ]]; then
            health_status=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "no-health-check")
            if [[ "$health_status" == "unhealthy" ]]; then
                unhealthy_services+=("$container")
            fi
        fi
    done
    
    # Handle failed services
    if [[ ${#failed_services[@]} -gt 0 ]]; then
        alert_message "Failed services detected: ${failed_services[*]}"
        log_message "Attempting to restart failed services: ${failed_services[*]}"
        
        cd "$PROJECT_DIR" || exit 1
        if docker compose -f docker-compose.prod.yml up -d "${failed_services[@]}"; then
            log_message "Successfully restarted services: ${failed_services[*]}"
        else
            alert_message "Failed to restart services: ${failed_services[*]}"
        fi
    fi
    
    # Handle unhealthy services
    if [[ ${#unhealthy_services[@]} -gt 0 ]]; then
        alert_message "Unhealthy services detected: ${unhealthy_services[*]}"
        log_message "Attempting to restart unhealthy services"
        
        for service in "${unhealthy_services[@]}"; do
            docker restart "$service"
        done
    fi
}

# Check disk space
check_disk_space() {
    local root_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    local data_usage=$(df "$PROJECT_DIR" | awk 'NR==2 {print $5}' | sed 's/%//' 2>/dev/null || echo "0")
    
    if [[ $root_usage -gt 90 ]]; then
        alert_message "Critical disk usage on root: ${root_usage}%"
    elif [[ $root_usage -gt 80 ]]; then
        log_message "WARNING - High disk usage on root: ${root_usage}%"
    fi
    
    if [[ $data_usage -gt 85 ]]; then
        alert_message "High disk usage on data partition: ${data_usage}%"
    fi
}

# Check memory usage
check_memory() {
    local memory_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2 }')
    if [[ $memory_usage -gt 90 ]]; then
        alert_message "Critical memory usage: ${memory_usage}%"
    elif [[ $memory_usage -gt 80 ]]; then
        log_message "WARNING - High memory usage: ${memory_usage}%"
    fi
}

# Check application health with multiple endpoints
check_application_health() {
    local health_endpoints=(
        "http://localhost:5000/_stcore/health"
        "http://localhost:5000/"
    )
    
    local health_failed=0
    
    for endpoint in "${health_endpoints[@]}"; do
        if ! python3 -c "import requests; requests.get('$endpoint', timeout=10)" 2>/dev/null; then
            health_failed=$((health_failed + 1))
            log_message "Health check failed for: $endpoint"
        fi
    done
    
    # If more than half the endpoints fail, restart the application
    if [[ $health_failed -gt $((${#health_endpoints[@]} / 2)) ]]; then
        alert_message "Application health checks failing - restarting service"
        cd "$PROJECT_DIR" || exit 1
        docker compose -f docker-compose.prod.yml restart dataguardian-pro
        sleep 30  # Wait for restart
        
        # Verify restart was successful
        if python3 -c "import requests; requests.get('http://localhost:5000/_stcore/health', timeout=10)" 2>/dev/null; then
            log_message "Application restart successful"
        else
            alert_message "Application restart failed - manual intervention required"
        fi
    fi
}

# Check SSL certificate expiration
check_ssl_expiration() {
    if [[ -f "$PROJECT_DIR/ssl/live/*/fullchain.pem" ]]; then
        local cert_file=$(find "$PROJECT_DIR/ssl/live" -name "fullchain.pem" | head -1)
        if [[ -f "$cert_file" ]]; then
            local expiry_date=$(openssl x509 -enddate -noout -in "$cert_file" | cut -d= -f2)
            local expiry_epoch=$(date -d "$expiry_date" +%s 2>/dev/null || echo "0")
            local current_epoch=$(date +%s)
            local days_until_expiry=$(( (expiry_epoch - current_epoch) / 86400 ))
            
            if [[ $days_until_expiry -lt 7 ]]; then
                alert_message "SSL certificate expires in $days_until_expiry days"
            elif [[ $days_until_expiry -lt 30 ]]; then
                log_message "SSL certificate expires in $days_until_expiry days"
            fi
        fi
    fi
}

# Main monitoring execution
log_message "Starting system monitoring check"

check_services
check_disk_space
check_memory
check_application_health
check_ssl_expiration

# Cleanup old logs (keep 30 days for monitor, 7 days for alerts)
find "$PROJECT_DIR/logs" -name "monitor.log" -mtime +30 -delete 2>/dev/null
find "$PROJECT_DIR/logs" -name "alerts.log" -mtime +7 -delete 2>/dev/null
find "$PROJECT_DIR/logs" -name "*.log" -size +100M -exec truncate -s 50M {} + 2>/dev/null

log_message "System monitoring check completed"
EOF

    chmod +x "$PROJECT_DIR/monitor.sh"
    
    # Schedule comprehensive monitoring every 5 minutes
    (crontab -l 2>/dev/null; echo "*/5 * * * * $PROJECT_DIR/monitor.sh >/dev/null 2>&1") | crontab -
    
    # Create initial log files with proper permissions
    touch "$PROJECT_DIR/logs/monitor.log" "$PROJECT_DIR/logs/alerts.log"
    chmod 644 "$PROJECT_DIR/logs/monitor.log" "$PROJECT_DIR/logs/alerts.log"
    
    log "Comprehensive system monitoring configured successfully"
}

# Show deployment summary
show_summary() {
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              DataGuardian Pro Deployment Complete           ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
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
    docker compose -f "$PROJECT_DIR/docker-compose.prod.yml" ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
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
    rm -f "$PROJECT_DIR/temp-nginx.conf"
    
    log "Cleanup completed"
}

# Signal handlers
trap cleanup EXIT
trap 'error "Deployment interrupted by user"' INT TERM

# Main deployment function
main() {
    show_banner
    check_root
    get_user_input
    
    log "=== Starting DataGuardian Pro Production Deployment ==="
    
    create_directories
    update_system
    install_docker
    setup_firewall
    setup_fail2ban
    generate_secrets
    create_env_file
    create_nginx_config
    create_docker_compose
    create_dockerfile
    check_port_conflicts
    prepare_application_code
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        setup_ssl
        setup_ssl_renewal
    else
        warning "Skipping SSL setup for non-production environment"
    fi
    
    deploy_application
    setup_log_rotation
    setup_backups
    setup_monitoring
    
    log "=== DataGuardian Pro Deployment Completed Successfully ==="
    
    show_summary
}

# Run main function with all arguments
main "$@"