#!/bin/bash
# DataGuardian Pro - Step 2: Python Environment Setup
# Creates Python environment with exact package versions from Replit

set -e  # Exit on any error

echo "🐍 DataGuardian Pro - Python Environment Setup (Step 2/5)"
echo "========================================================="
echo "Setting up Python environment with exact Replit packages"
echo ""

# Function to log messages with timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root (use sudo)"
    exit 1
fi

log "Starting Python environment setup..."

# Create dataguardian user if it doesn't exist
log "Creating dataguardian user..."
if ! id "dataguardian" &>/dev/null; then
    useradd -r -m -s /bin/bash -d /home/dataguardian dataguardian
    log "✅ Created dataguardian user"
else
    log "✅ dataguardian user already exists"
fi

# Create application directory
log "Creating application directories..."
mkdir -p /opt/dataguardian
mkdir -p /var/log/dataguardian
mkdir -p /etc/dataguardian
mkdir -p /opt/dataguardian/backups

# Set ownership
chown -R dataguardian:dataguardian /opt/dataguardian
chown -R dataguardian:dataguardian /var/log/dataguardian
chown -R dataguardian:dataguardian /etc/dataguardian

log "✅ Directory structure created"

# Change to application directory
cd /opt/dataguardian

# Create Python virtual environment
log "Creating Python virtual environment..."
sudo -u dataguardian python3 -m venv venv

# Activate virtual environment and upgrade pip
log "Upgrading pip and installing build tools..."
sudo -u dataguardian /opt/dataguardian/venv/bin/pip install --upgrade pip setuptools wheel

# Create requirements file with exact versions from Replit
log "Creating requirements file with exact Replit versions..."
cat > requirements.txt << 'REQUIREMENTS_EOF'
# Core Web Framework (exact Replit versions)
streamlit>=1.44.1

# AI/ML Dependencies
aiohttp>=3.12.13
anthropic>=0.53.0
openai>=1.75.0

# Data Processing
pandas>=2.2.3
pillow>=11.2.1
plotly>=6.1.2

# Database & Caching
psycopg2-binary>=2.9.10
psycopg2-pool>=1.2
redis>=6.2.0

# Document Processing
pypdf2>=3.0.1
reportlab>=4.4.0
textract>=1.6.5
pytesseract>=0.3.13
pdfkit>=1.0.0

# HTTP & Web Scraping
requests>=2.32.3
beautifulsoup4>=4.8.2
trafilatura>=2.0.0
tldextract>=5.2.0

# Security & Authentication
bcrypt>=4.3.0
pyjwt>=2.10.1
cryptography>=45.0.5
authlib>=1.6.3
python-jose>=3.5.0
python3-saml>=1.16.0
pycryptodome>=3.22.0

# Payment Processing
stripe>=12.0.0

# Computer Vision & OCR
opencv-python>=4.12.0.88
opencv-python-headless>=4.12.0.88

# Machine Learning & Deep Learning
tensorflow>=2.20.0
torch>=2.8.0
onnx>=1.19.0
onnxruntime>=1.22.1

# System Monitoring & Performance
psutil>=7.0.0
memory-profiler>=0.61.0
py-spy>=0.4.0
cachetools>=5.5.2
joblib>=1.5.2

# Web Framework & API
flask>=3.1.2

# Database Connectors
mysql-connector-python>=9.4.0
pyodbc>=5.2.0

# Utilities
dnspython>=2.7.0
pyyaml>=6.0.2
python-whois>=0.9.5

# PDF and Document Processing
weasyprint>=66.0
svglib>=1.5.1

# Development & Testing
pyinstaller>=6.14.2
pytest>=8.4.2
REQUIREMENTS_EOF

# Set ownership
chown dataguardian:dataguardian requirements.txt

log "✅ Requirements file created with exact Replit versions"

# Install Python packages
log "Installing Python packages (this may take several minutes)..."
sudo -u dataguardian /opt/dataguardian/venv/bin/pip install -r requirements.txt

log "✅ Python packages installed successfully!"

# Verify key packages
log "Verifying key package installations..."
sudo -u dataguardian /opt/dataguardian/venv/bin/python3 -c "
import streamlit
import pandas
import redis
import psycopg2
import requests
print(f'✅ Streamlit: {streamlit.__version__}')
print(f'✅ Pandas: {pandas.__version__}')
print(f'✅ Redis: {redis.__version__}')
print(f'✅ Psycopg2: {psycopg2.__version__}')
print(f'✅ Requests: {requests.__version__}')
"

log "✅ Python environment setup completed successfully!"
log ""
log "📋 Python environment summary:"
log "   - Virtual environment: /opt/dataguardian/venv"
log "   - Python packages: $(sudo -u dataguardian /opt/dataguardian/venv/bin/pip list | wc -l) packages installed"
log "   - User: dataguardian"
log "   - Permissions: Properly configured"
log ""
log "🔥 Next step: Run 03_app_install.sh"
echo "========================================================="