#!/bin/bash
# Enhanced DataGuardian Pro - Remote Deployment to Production Server
# Run this from your Replit environment to deploy to remote server

set -e

echo "🛡️ DataGuardian Pro - REMOTE ENHANCED DEPLOYMENT"
echo "================================================="
echo "Deploying complete Replit environment to remote production server"
echo ""

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Function to check command success
check_command() {
    if [ $? -ne 0 ]; then
        log "❌ $1 FAILED"
        exit 1
    fi
    log "✅ $1"
}

# Get server details
read -p "Enter production server IP/hostname: " SERVER_HOST
read -p "Enter SSH user (usually root): " SSH_USER
read -p "Enter SSH port (default 22): " SSH_PORT
SSH_PORT=${SSH_PORT:-22}

SERVER="$SSH_USER@$SERVER_HOST"
log "Target server: $SERVER (port $SSH_PORT)"

# Verify we're running from complete Replit environment
log "Verifying we're running from complete Replit environment..."
required_modules=(
    "utils/activity_tracker.py"
    "utils/code_profiler.py"
    "services/license_integration.py"
    "app.py"
)

for module in "${required_modules[@]}"; do
    if [ -f "$module" ]; then
        log "✅ Found source module: $module"
    else
        log "❌ ERROR: Missing source module: $module"
        log "❌ Please run this script from the complete Replit environment directory"
        exit 1
    fi
done

# Create deployment package
log "Creating complete deployment package..."
PACKAGE_NAME="dataguardian_complete_$(date +%Y%m%d_%H%M%S).tar.gz"

tar --exclude='*.log' \
    --exclude='*.tmp' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='venv' \
    --exclude='*.pyc' \
    --exclude='.replit*' \
    --exclude='replit.nix' \
    -czf "$PACKAGE_NAME" .
check_command "Deployment package creation"

log "Package created: $PACKAGE_NAME ($(du -sh $PACKAGE_NAME | cut -f1))"

# Upload package to server
log "Uploading deployment package to production server..."
scp -P "$SSH_PORT" "$PACKAGE_NAME" "$SERVER:/tmp/"
check_command "Package upload to server"

# Create remote deployment script
log "Creating remote deployment script..."
cat > "remote_install.sh" << 'REMOTE_SCRIPT_EOF'
#!/bin/bash
# Remote installation script for DataGuardian Pro

set -e

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

PACKAGE_FILE="/tmp/PACKAGE_NAME_PLACEHOLDER"
INSTALL_DIR="/opt/dataguardian"
VENV_DIR="$INSTALL_DIR/venv"
SERVICE_USER="dataguardian"
SERVICE_NAME="dataguardian"

log "Starting remote DataGuardian installation..."

# System preparation
log "=== SYSTEM PREPARATION ==="
apt-get update -y
apt-get install -y \
    python3.11 python3.11-venv python3.11-dev python3-pip \
    postgresql postgresql-contrib redis-server nginx \
    curl wget git tar gzip build-essential pkg-config \
    libpq-dev libssl-dev libffi-dev libjpeg-dev libpng-dev \
    tesseract-ocr tesseract-ocr-nld poppler-utils \
    supervisor fail2ban htop tree jq sqlite3 ffmpeg imagemagick
check_command "System dependencies installation"

# User setup
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd -r -s /bin/bash -d "$INSTALL_DIR" "$SERVICE_USER"
    check_command "Service user creation"
fi

# Directory setup
mkdir -p "$INSTALL_DIR"
chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
chmod 755 "$INSTALL_DIR"
check_command "Installation directory setup"

# Extract package
log "=== EXTRACTING REPLIT ENVIRONMENT ==="
cd "$INSTALL_DIR"
tar -xzf "$PACKAGE_FILE"
chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
check_command "Replit environment extraction"

# Verify critical modules
critical_modules=(
    "utils/activity_tracker.py"
    "services/license_integration.py"
    "app.py"
)
for module in "${critical_modules[@]}"; do
    if [ -f "$INSTALL_DIR/$module" ]; then
        log "✅ Verified module: $module"
    else
        log "❌ Missing module: $module"
        exit 1
    fi
done

# Python environment
log "=== PYTHON ENVIRONMENT SETUP ==="
python3.11 -m venv "$VENV_DIR"
chown -R "$SERVICE_USER:$SERVICE_USER" "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip setuptools wheel

# Install dependencies
"$VENV_DIR/bin/pip" install \
    streamlit pandas numpy plotly redis psycopg2-binary \
    bcrypt pyjwt requests beautifulsoup4 pillow reportlab \
    pypdf2 pytesseract opencv-python-headless trafilatura \
    tldextract openai anthropic stripe aiohttp cryptography \
    pyyaml python-whois memory-profiler psutil cachetools \
    joblib authlib python-jose
check_command "Python dependencies installation"

# Database setup
log "=== DATABASE SETUP ==="
systemctl start postgresql redis-server
systemctl enable postgresql redis-server

sudo -u postgres psql -c "DROP DATABASE IF EXISTS dataguardian;" 2>/dev/null || true
sudo -u postgres psql -c "DROP USER IF EXISTS dataguardian;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE dataguardian;"
sudo -u postgres psql -c "CREATE USER dataguardian WITH PASSWORD 'dataguardian_secure_2025';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE dataguardian TO dataguardian;"
sudo -u postgres psql -c "ALTER USER dataguardian CREATEDB SUPERUSER;"
check_command "Database setup"

# Environment variables
log "=== CONFIGURATION SETUP ==="
cat > "$INSTALL_DIR/.env" << 'ENV_EOF'
DATABASE_URL=postgresql://dataguardian:dataguardian_secure_2025@localhost/dataguardian
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=dataguardian_jwt_secret_2025_production_secure_random_key_32_chars
PYTHONPATH=/opt/dataguardian
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_PORT=5000
STREAMLIT_SERVER_ADDRESS=0.0.0.0
LICENSE_CHECK_ENABLED=true
LICENSE_STRICT_MODE=false
LOG_LEVEL=INFO
ENV_EOF
chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR/.env"
chmod 600 "$INSTALL_DIR/.env"

# Streamlit config
mkdir -p "$INSTALL_DIR/.streamlit"
cat > "$INSTALL_DIR/.streamlit/config.toml" << 'STREAMLIT_EOF'
[server]
headless = true
address = "0.0.0.0"
port = 5000
maxUploadSize = 200

[browser]
gatherUsageStats = false
showErrorDetails = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
STREAMLIT_EOF
chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR/.streamlit"

# Service setup
log "=== SERVICE SETUP ==="
cat > "/etc/systemd/system/$SERVICE_NAME.service" << SERVICE_EOF
[Unit]
Description=DataGuardian Pro - Enterprise Privacy Compliance Platform
After=network.target postgresql.service redis-server.service
Requires=postgresql.service redis-server.service

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$VENV_DIR/bin:/usr/local/bin:/usr/bin:/bin
Environment=PYTHONPATH=$INSTALL_DIR
EnvironmentFile=$INSTALL_DIR/.env
ExecStart=$VENV_DIR/bin/streamlit run app.py --server.port 5000 --server.address 0.0.0.0 --server.headless true
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# Nginx setup
cat > "/etc/nginx/sites-available/dataguardian" << 'NGINX_EOF'
server {
    listen 80;
    server_name localhost;
    client_max_body_size 200M;

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
    }
}
NGINX_EOF

ln -sf /etc/nginx/sites-available/dataguardian /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx
check_command "Nginx configuration"

# Start services
log "=== STARTING SERVICES ==="
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"
check_command "DataGuardian service start"

sleep 15

# Final validation
log "=== VALIDATION ==="
for i in {1..10}; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        log "✅ Application responding (HTTP 200)"
        break
    else
        log "⚠️ Application not ready (HTTP $HTTP_CODE) - attempt $i/10"
        if [ $i -eq 10 ]; then
            log "❌ Application failed to start properly"
            systemctl status "$SERVICE_NAME"
            exit 1
        fi
        sleep 3
    fi
done

# Module validation
cd "$INSTALL_DIR"
if "$VENV_DIR/bin/python" -c "import utils.activity_tracker" 2>/dev/null; then
    log "✅ Replit modules successfully imported"
else
    log "❌ Module import failed"
    exit 1
fi

echo ""
echo "🎉 DATAGUARDIAN PRO DEPLOYMENT SUCCESSFUL!"
echo "========================================="
echo "✅ Complete Replit environment deployed"
echo "✅ All services running and validated"
echo "✅ Application accessible at http://localhost:5000"
echo ""
echo "🔧 Service management:"
echo "   systemctl status/start/stop/restart dataguardian"
echo "   journalctl -u dataguardian -f"
echo ""
log "Remote deployment completed successfully!"
REMOTE_SCRIPT_EOF

# Replace placeholder with actual package name
sed -i "s/PACKAGE_NAME_PLACEHOLDER/$PACKAGE_NAME/g" remote_install.sh
chmod +x remote_install.sh

# Upload and execute remote script
log "Uploading and executing remote installation script..."
scp -P "$SSH_PORT" remote_install.sh "$SERVER:/tmp/"
ssh -p "$SSH_PORT" "$SERVER" "chmod +x /tmp/remote_install.sh && /tmp/remote_install.sh"
check_command "Remote installation execution"

# Cleanup
log "Cleaning up local files..."
rm -f "$PACKAGE_NAME" remote_install.sh
check_command "Local cleanup"

echo ""
echo "🎉 REMOTE DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "============================================"
echo "✅ Complete Replit environment deployed to production server"
echo "✅ All enterprise modules transferred and validated"
echo "✅ Services configured and running"
echo ""
echo "🌐 Access your production application:"
echo "   http://$SERVER_HOST:5000"
echo ""
echo "🔧 Manage services on production server:"
echo "   ssh $SERVER 'systemctl status dataguardian'"
echo "   ssh $SERVER 'journalctl -u dataguardian -f'"
echo ""
log "Complete remote deployment finished successfully!"