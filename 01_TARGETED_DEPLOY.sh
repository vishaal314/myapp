#!/bin/bash
# Targeted DataGuardian Pro Deployment - Essential Files Only
# Copies only the essential working files, not massive data directories

set -e

echo "🎯 DataGuardian Pro - TARGETED DEPLOYMENT"
echo "========================================="
echo "Deploying essential Replit files only (avoiding massive data directories)"
echo ""

# Function to log messages
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

# Variables
INSTALL_DIR="/opt/dataguardian"
VENV_DIR="$INSTALL_DIR/venv"
SERVICE_USER="dataguardian"
SERVICE_NAME="dataguardian"
CURRENT_DIR="$(pwd)"

# Verify we're in Replit environment
log "Verifying Replit environment..."
required_files=(
    "utils/activity_tracker.py"
    "services/license_integration.py"
    "app.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        log "✅ Found: $file"
    else
        log "❌ Missing: $file"
        exit 1
    fi
done

# 1. SYSTEM SETUP
log "=== SYSTEM SETUP ==="
apt-get update -y >/dev/null 2>&1
apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip \
    postgresql postgresql-contrib redis-server nginx curl wget git \
    build-essential libpq-dev tesseract-ocr poppler-utils >/dev/null 2>&1
check_command "System packages installation"

# 2. USER SETUP
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd -r -s /bin/bash -d "$INSTALL_DIR" "$SERVICE_USER"
    check_command "Service user creation"
fi

mkdir -p "$INSTALL_DIR"
chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
chmod 755 "$INSTALL_DIR"
check_command "Directory setup"

# 3. TARGETED FILE COPY (Essential directories only)
log "=== TARGETED FILE COPY ==="

# Define essential directories and files to copy
essential_items=(
    "app.py"
    "utils/"
    "services/"
    "components/"
    "config/"
    "translations/"
    "static/"
    ".streamlit/"
    "database/"
    "data/"
)

log "Copying essential application files..."
cd "$CURRENT_DIR"

# Create targeted package with only essential files
tar -czf /tmp/dataguardian_essential.tar.gz \
    --exclude='attached_assets/' \
    --exclude='reports/' \
    --exclude='logs/' \
    --exclude='marketing*/' \
    --exclude='docs/' \
    --exclude='examples/' \
    --exclude='terraform/' \
    --exclude='test*/' \
    --exclude='patent_proofs/' \
    --exclude='DataGuardian-Pro-Standalone-Source/' \
    --exclude='*.log' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='*.pyc' \
    "${essential_items[@]}" 2>/dev/null
check_command "Essential files packaging"

# Extract to production
log "Extracting essential files to production..."
cd "$INSTALL_DIR"
tar -xzf /tmp/dataguardian_essential.tar.gz
chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
rm -f /tmp/dataguardian_essential.tar.gz
check_command "Essential files extraction"

# Verify extraction
log "Verifying essential files..."
for file in "${required_files[@]}"; do
    if [ -f "$INSTALL_DIR/$file" ]; then
        log "✅ Production: $file"
    else
        log "❌ Missing in production: $file"
        exit 1
    fi
done

# 4. PYTHON ENVIRONMENT
log "=== PYTHON ENVIRONMENT ==="
cd "$INSTALL_DIR"
python3.11 -m venv "$VENV_DIR"
chown -R "$SERVICE_USER:$SERVICE_USER" "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip setuptools wheel >/dev/null 2>&1
check_command "Python virtual environment"

log "Installing essential Python packages..."
"$VENV_DIR/bin/pip" install \
    streamlit pandas numpy plotly redis psycopg2-binary \
    bcrypt pyjwt requests beautifulsoup4 pillow reportlab \
    pypdf2 pytesseract opencv-python-headless trafilatura \
    tldextract openai anthropic stripe aiohttp cryptography \
    pyyaml python-whois memory-profiler psutil cachetools \
    joblib authlib python-jose >/dev/null 2>&1
check_command "Python dependencies installation"

# 5. DATABASE SETUP
log "=== DATABASE SETUP ==="
systemctl start postgresql redis-server >/dev/null 2>&1
systemctl enable postgresql redis-server >/dev/null 2>&1

# Database setup
sudo -u postgres psql -c "DROP DATABASE IF EXISTS dataguardian;" >/dev/null 2>&1 || true
sudo -u postgres psql -c "DROP USER IF EXISTS dataguardian;" >/dev/null 2>&1 || true
sudo -u postgres psql -c "CREATE DATABASE dataguardian;" >/dev/null 2>&1
sudo -u postgres psql -c "CREATE USER dataguardian WITH PASSWORD 'dataguardian_secure_2025';" >/dev/null 2>&1
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE dataguardian TO dataguardian;" >/dev/null 2>&1
sudo -u postgres psql -c "ALTER USER dataguardian CREATEDB SUPERUSER;" >/dev/null 2>&1
check_command "Database setup"

# 6. CONFIGURATION
log "=== CONFIGURATION SETUP ==="

# Environment variables
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
check_command "Configuration setup"

# 7. SERVICES SETUP
log "=== SERVICES SETUP ==="

# Systemd service
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
nginx -t >/dev/null 2>&1 && systemctl restart nginx >/dev/null 2>&1
check_command "Nginx configuration"

# 8. START SERVICES
log "=== STARTING SERVICES ==="
systemctl daemon-reload
systemctl enable "$SERVICE_NAME" >/dev/null 2>&1
systemctl start "$SERVICE_NAME"
check_command "Service startup"

# Wait for initialization
log "Waiting for service initialization..."
sleep 20

# 9. VALIDATION
log "=== VALIDATION ==="

# HTTP validation
for i in {1..12}; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        log "✅ Application responding (HTTP 200)"
        break
    else
        log "⚠️ Application not ready (HTTP $HTTP_CODE) - attempt $i/12"
        if [ $i -eq 12 ]; then
            log "❌ Application failed to respond"
            systemctl status "$SERVICE_NAME" --no-pager -l
            exit 1
        fi
        sleep 5
    fi
done

# Module import validation
cd "$INSTALL_DIR"
if "$VENV_DIR/bin/python" -c "import utils.activity_tracker; import services.license_integration" 2>/dev/null; then
    log "✅ Essential modules successfully imported"
else
    log "❌ Module import failed"
    exit 1
fi

echo ""
echo "🎉 TARGETED DEPLOYMENT SUCCESSFUL!"
echo "================================="
echo "✅ Essential Replit application files deployed"
echo "✅ All services running and validated"
echo "✅ Application accessible at http://localhost:5000"
echo ""
echo "📊 Deployment Summary:"
echo "   ✅ Core application files (app.py, utils/, services/)"
echo "   ✅ Configuration and translations"
echo "   ✅ Database and caching services"
echo "   ✅ Web server and reverse proxy"
echo "   ✅ Module imports working correctly"
echo ""
echo "🔧 Service management:"
echo "   systemctl status/start/stop/restart $SERVICE_NAME"
echo "   journalctl -u $SERVICE_NAME -f"
echo ""
log "Targeted deployment completed successfully!"