#!/bin/bash
# Production DataGuardian Pro Deployment
# Runs on production server with uploaded files

set -e

echo "🏭 DataGuardian Pro - PRODUCTION DEPLOYMENT"
echo "==========================================="
echo "Deploying DataGuardian Pro on production server"
echo ""

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

check_command() {
    if [ $? -ne 0 ]; then
        log "❌ $1 FAILED"
        exit 1
    fi
    log "✅ $1"
}

INSTALL_DIR="/opt/dataguardian"
VENV_DIR="$INSTALL_DIR/venv"
SERVICE_USER="dataguardian"
SERVICE_NAME="dataguardian"

log "Starting production deployment..."

# Check if we have an uploaded package to extract
if [ -f "/opt/GdprComplianceTool.zip" ]; then
    log "Found GdprComplianceTool.zip in /opt, extracting..."
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    # Extract with verbose output to understand structure
    log "Extracting ZIP contents..."
    unzip -q -o /opt/GdprComplianceTool.zip
    
    # Debug: Show what was extracted
    log "Extracted files structure:"
    find "$INSTALL_DIR" -name "*.py" -type f | head -5
    
    chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
    rm -f /opt/GdprComplianceTool.zip
    check_command "ZIP package extraction"
elif [ -f "/opt/dataguardian_complete.zip" ]; then
    log "Found ZIP package in /opt, extracting..."
    cd "$INSTALL_DIR"
    unzip -q -o /opt/dataguardian_complete.zip
    chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
    rm -f /opt/dataguardian_complete.zip
    check_command "ZIP package extraction"
elif [ -f "/tmp/dataguardian_complete.zip" ]; then
    log "Found ZIP package in /tmp, extracting..."
    cd "$INSTALL_DIR"
    unzip -q -o /tmp/dataguardian_complete.zip
    chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
    rm -f /tmp/dataguardian_complete.zip
    check_command "ZIP package extraction"
elif [ -f "/opt/dataguardian_complete.tar.gz" ]; then
    log "Found TAR package in /opt, extracting..."
    cd "$INSTALL_DIR"
    tar -xzf /opt/dataguardian_complete.tar.gz
    chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
    rm -f /opt/dataguardian_complete.tar.gz
    check_command "TAR package extraction"
elif [ -f "/tmp/dataguardian_complete.tar.gz" ]; then
    log "Found TAR package in /tmp, extracting..."
    cd "$INSTALL_DIR"
    tar -xzf /tmp/dataguardian_complete.tar.gz
    chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
    rm -f /tmp/dataguardian_complete.tar.gz
    check_command "TAR package extraction"
elif [ -f "$INSTALL_DIR/app.py" ]; then
    log "Found existing app.py, proceeding with current files..."
else
    log "❌ No DataGuardian source files found!"
    log "Please upload the source files first:"
    echo ""
    echo "🎯 RECOMMENDED: Use Replit's ZIP export feature:"
    echo "   1. In your Replit workspace, go to the file menu (3 dots)"
    echo "   2. Select 'Download as zip'"
    echo "   3. Save as 'dataguardian_complete.zip'"
    echo ""
    echo "📤 Then place it in /opt:"
    echo "   scp dataguardian_complete.zip root@vishaalnoord7:/opt/"
    echo ""
    echo "🔧 Alternative (manual tar):"
    echo "   tar --exclude='attached_assets' --exclude='reports' --exclude='marketing*' \\"
    echo "       --exclude='logs' --exclude='*.log' --exclude='__pycache__' \\"
    echo "       --exclude='.git' --exclude='*.pyc' \\"
    echo "       -czf dataguardian_complete.tar.gz ."
    echo "   scp dataguardian_complete.tar.gz root@vishaalnoord7:/opt/"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# 1. SYSTEM SETUP
log "=== SYSTEM SETUP ==="
apt-get update -y >/dev/null 2>&1
apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip \
    postgresql postgresql-contrib redis-server nginx curl wget git \
    build-essential libpq-dev tesseract-ocr poppler-utils \
    libssl-dev libffi-dev libjpeg-dev libpng-dev zlib1g-dev \
    libxml2-dev libxslt1-dev supervisor fail2ban >/dev/null 2>&1
check_command "System packages"

# 2. USER SETUP
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd -r -s /bin/bash -d "$INSTALL_DIR" "$SERVICE_USER"
    check_command "Service user creation"
fi

mkdir -p "$INSTALL_DIR"
chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
chmod 755 "$INSTALL_DIR"
check_command "Directory setup"

# 3. VERIFY AND ORGANIZE APPLICATION FILES
log "=== VERIFYING APPLICATION FILES ==="

# Find app.py files after extraction - could be in subdirectories
APP_PY_LOCATION=$(find "$INSTALL_DIR" -name "app.py" -type f | head -1)

if [ -n "$APP_PY_LOCATION" ]; then
    APP_SOURCE_DIR=$(dirname "$APP_PY_LOCATION")
    log "✅ Found app.py at: $APP_SOURCE_DIR"
    
    # If app.py is in a subdirectory, move all files to the root
    if [ "$APP_SOURCE_DIR" != "$INSTALL_DIR" ]; then
        log "Moving application files from $APP_SOURCE_DIR to $INSTALL_DIR"
        
        # Create temporary directory for reorganization
        TEMP_DIR="/tmp/dataguardian_reorg_$$"
        mkdir -p "$TEMP_DIR"
        
        # Copy all files from source directory to temp directory
        if [ -d "$APP_SOURCE_DIR" ]; then
            cp -r "$APP_SOURCE_DIR"/* "$TEMP_DIR/" 2>/dev/null || true
            # Copy hidden files too (like .streamlit)
            find "$APP_SOURCE_DIR" -name ".*" -type f -exec cp {} "$TEMP_DIR/" \; 2>/dev/null || true
            find "$APP_SOURCE_DIR" -name ".*" -type d -exec cp -r {} "$TEMP_DIR/" \; 2>/dev/null || true
        fi
        
        # Verify app.py was copied to temp directory
        if [ -f "$TEMP_DIR/app.py" ]; then
            # Clear the install directory and move files from temp
            rm -rf "$INSTALL_DIR"/*
            cp -r "$TEMP_DIR"/* "$INSTALL_DIR/" 2>/dev/null || true
            
            # Copy hidden files and directories
            find "$TEMP_DIR" -name ".*" -type f -exec cp {} "$INSTALL_DIR/" \; 2>/dev/null || true
            find "$TEMP_DIR" -name ".*" -type d -exec cp -r {} "$INSTALL_DIR/" \; 2>/dev/null || true
            
            # Clean up temp directory
            rm -rf "$TEMP_DIR"
            
            # Final verification
            if [ -f "$INSTALL_DIR/app.py" ]; then
                log "✅ Application files reorganized successfully"
            else
                log "❌ Failed to reorganize files - app.py missing after move"
                exit 1
            fi
        else
            log "❌ Failed to copy files to temporary directory"
            rm -rf "$TEMP_DIR"
            exit 1
        fi
    fi
else
    log "❌ Missing app.py - application files not properly transferred"
    log "Checking extraction contents..."
    find "$INSTALL_DIR" -name "*.py" -type f | head -10
    exit 1
fi

# Final verification
if [ ! -f "$INSTALL_DIR/app.py" ]; then
    log "❌ app.py still not found after reorganization"
    exit 1
fi

# Create minimal required directories if they don't exist
mkdir -p "$INSTALL_DIR/utils" "$INSTALL_DIR/services" "$INSTALL_DIR/components" \
         "$INSTALL_DIR/config" "$INSTALL_DIR/.streamlit" "$INSTALL_DIR/data" \
         "$INSTALL_DIR/translations" "$INSTALL_DIR/static"

# 4. PYTHON ENVIRONMENT
log "=== PYTHON ENVIRONMENT ==="
cd "$INSTALL_DIR"
python3.11 -m venv "$VENV_DIR"
chown -R "$SERVICE_USER:$SERVICE_USER" "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip setuptools wheel >/dev/null 2>&1
check_command "Python virtual environment"

log "Installing Python packages..."
"$VENV_DIR/bin/pip" install \
    streamlit==1.44.0 pandas numpy plotly redis psycopg2-binary \
    bcrypt pyjwt requests beautifulsoup4 pillow reportlab \
    pypdf2 pytesseract opencv-python-headless trafilatura \
    tldextract openai anthropic stripe aiohttp cryptography \
    pyyaml python-whois memory-profiler psutil cachetools \
    joblib authlib python-jose python3-saml dnspython \
    mysql-connector-python textract pdfkit svglib weasyprint \
    flask >/dev/null 2>&1
check_command "Python packages installation"

# 5. DATABASE SETUP
log "=== DATABASE SETUP ==="
systemctl start postgresql redis-server >/dev/null 2>&1
systemctl enable postgresql redis-server >/dev/null 2>&1

# Database configuration
sudo -u postgres psql -c "DROP DATABASE IF EXISTS dataguardian;" >/dev/null 2>&1 || true
sudo -u postgres psql -c "DROP USER IF EXISTS dataguardian;" >/dev/null 2>&1 || true
sudo -u postgres psql -c "CREATE DATABASE dataguardian;" >/dev/null 2>&1
sudo -u postgres psql -c "CREATE USER dataguardian WITH PASSWORD 'dataguardian_secure_2025';" >/dev/null 2>&1
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE dataguardian TO dataguardian;" >/dev/null 2>&1
sudo -u postgres psql -c "ALTER USER dataguardian CREATEDB SUPERUSER;" >/dev/null 2>&1

# Create basic database schema
sudo -u postgres psql -d dataguardian -c "
CREATE TABLE IF NOT EXISTS scan_results (
    id SERIAL PRIMARY KEY,
    scan_id VARCHAR(255) UNIQUE,
    username VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scan_type VARCHAR(100),
    region VARCHAR(50),
    file_count INTEGER DEFAULT 0,
    total_pii_found INTEGER DEFAULT 0,
    high_risk_count INTEGER DEFAULT 0,
    result JSONB
);
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE,
    email VARCHAR(255),
    password_hash VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS license_data (
    id SERIAL PRIMARY KEY,
    license_key VARCHAR(255) UNIQUE,
    user_id INTEGER REFERENCES users(id),
    plan VARCHAR(100),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
" >/dev/null 2>&1

# Redis memory setting
echo 'vm.overcommit_memory = 1' >> /etc/sysctl.conf
sysctl vm.overcommit_memory=1 >/dev/null 2>&1

check_command "Database setup"

# 6. CONFIGURATION
log "=== CONFIGURATION ==="

# Environment variables
cat > "$INSTALL_DIR/.env" << 'ENV_EOF'
DATABASE_URL=postgresql://dataguardian:dataguardian_secure_2025@localhost/dataguardian
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=dataguardian
POSTGRES_USER=dataguardian
POSTGRES_PASSWORD=dataguardian_secure_2025
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
JWT_SECRET=dataguardian_jwt_secret_2025_production_secure_random_key_32_chars
DATAGUARDIAN_MASTER_KEY=gQJ6WV5FxDgGWj-vQqRzHqS4CIUOGFaXRqsGXNLJHbU=
ENCRYPTION_KEY=dataguardian_encryption_key_2025_secure
PYTHONPATH=/opt/dataguardian
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_PORT=5000
STREAMLIT_SERVER_ADDRESS=0.0.0.0
OPENAI_API_KEY=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
STRIPE_SECRET_KEY=sk_test_51RArxBFSlkdgMbJE03jAVsOp0Cp3KabXxuqlWtpKQgD82MPBRFJGhM7ghzPFYpNnzjlEoPqSC6uY7mzlWUY7RICb00Avj3sJx7
LICENSE_CHECK_ENABLED=true
LICENSE_STRICT_MODE=false
LOG_LEVEL=INFO
ENV_EOF
chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR/.env"
chmod 600 "$INSTALL_DIR/.env"

# Streamlit configuration
cat > "$INSTALL_DIR/.streamlit/config.toml" << 'STREAMLIT_EOF'
[server]
headless = true
address = "0.0.0.0"
port = 5000
folderWatchBlacklist = [".*", "*/reports/*", "*/temp_*/*"]

[browser]
gatherUsageStats = false
serverAddress = "localhost"

[theme]
primaryColor = "#4267B2"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F5"
textColor = "#1E293B"
font = "sans serif"

[ui]
hideTopBar = true

[client]
showErrorDetails = false
toolbarMode = "minimal"

[global]
developmentMode = false

[runner]
fastReruns = true

[logger]
level = "error"
STREAMLIT_EOF
chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR/.streamlit"
check_command "Configuration files"

# 7. SERVICE SETUP
log "=== SERVICE SETUP ==="

# Systemd service
cat > "/etc/systemd/system/$SERVICE_NAME.service" << SERVICE_EOF
[Unit]
Description=DataGuardian Pro - Enterprise Privacy Compliance Platform
After=network.target postgresql.service redis-server.service
Wants=postgresql.service redis-server.service
Requires=postgresql.service redis-server.service

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$VENV_DIR/bin:/usr/local/bin:/usr/bin:/bin
Environment=PYTHONPATH=$INSTALL_DIR
EnvironmentFile=$INSTALL_DIR/.env
ExecStartPre=/bin/sleep 5
ExecStart=$VENV_DIR/bin/streamlit run app.py --server.port 5000 --server.address 0.0.0.0 --server.headless true
Restart=always
RestartSec=10
TimeoutStartSec=60
StandardOutput=journal
StandardError=journal
KillMode=mixed

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# Nginx configuration
cat > "/etc/nginx/sites-available/dataguardian" << 'NGINX_EOF'
server {
    listen 80;
    server_name localhost;
    client_max_body_size 200M;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
        proxy_connect_timeout 60;
    }
}
NGINX_EOF

ln -sf /etc/nginx/sites-available/dataguardian /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t >/dev/null 2>&1 && systemctl restart nginx >/dev/null 2>&1
check_command "Web server setup"

# Set file permissions
chmod 750 "$INSTALL_DIR"
find "$INSTALL_DIR" -name "*.py" -exec chmod 644 {} \;
find "$INSTALL_DIR" -type d -exec chmod 755 {} \;
chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"

# 8. START SERVICES
log "=== STARTING SERVICES ==="
systemctl daemon-reload
systemctl enable "$SERVICE_NAME" >/dev/null 2>&1
systemctl start "$SERVICE_NAME"
check_command "Service startup"

# Wait for initialization
log "Waiting for application to start..."
sleep 25

# 9. VALIDATION
log "=== VALIDATION ==="

# Check service status
if systemctl is-active --quiet "$SERVICE_NAME"; then
    log "✅ DataGuardian service is running"
else
    log "❌ DataGuardian service failed to start"
    systemctl status "$SERVICE_NAME" --no-pager -l
    journalctl -u "$SERVICE_NAME" --no-pager -l | tail -20
    exit 1
fi

# HTTP validation
for i in {1..15}; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        log "✅ Application responding (HTTP 200)"
        break
    else
        log "⚠️ Application not ready (HTTP $HTTP_CODE) - attempt $i/15"
        if [ $i -eq 15 ]; then
            log "❌ Application failed to respond properly"
            echo ""
            echo "🔧 Troubleshooting:"
            echo "   systemctl status $SERVICE_NAME"
            echo "   journalctl -u $SERVICE_NAME -f"
            echo "   curl -v http://localhost:5000"
            exit 1
        fi
        sleep 4
    fi
done

echo ""
echo "🎉 PRODUCTION DEPLOYMENT SUCCESSFUL!"
echo "===================================="
echo "✅ DataGuardian Pro deployed on production server"
echo "✅ All services configured and running"
echo "✅ Application responding correctly"
echo ""
echo "🌐 Access your application:"
echo "   http://localhost:5000"
echo ""
echo "🔧 Service management:"
echo "   systemctl status/start/stop/restart $SERVICE_NAME"
echo "   journalctl -u $SERVICE_NAME -f"
echo ""
echo "📁 Installation directory: $INSTALL_DIR"
echo ""
log "Production deployment completed successfully!"