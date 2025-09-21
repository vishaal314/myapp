#!/bin/bash
# DataGuardian Pro - Step 1: System Preparation
# Installs all system dependencies matching Replit environment

set -e  # Exit on any error

echo "🚀 DataGuardian Pro - System Preparation (Step 1/5)"
echo "=================================================="
echo "Installing system dependencies (matches replit.nix)"
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

log "Starting system preparation..."

# Update system packages
log "Updating system packages..."
apt update -y
apt upgrade -y

# Install system dependencies (matching replit.nix exactly)
log "Installing core system dependencies..."
apt install -y \
    build-essential \
    gcc \
    g++ \
    pkg-config \
    curl \
    wget \
    git \
    vim \
    nano \
    htop \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# Install language and development tools
log "Installing language and development tools..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-setuptools \
    python3-wheel

# Install system libraries (matching replit.nix)
log "Installing system libraries..."
apt install -y \
    libc6-dev \
    libstdc++6 \
    libglib2.0-dev \
    libgtk-3-dev \
    libgobject-introspection1.0-dev \
    tk-dev \
    tcl-dev \
    libcairo2-dev \
    libgirepository1.0-dev \
    libfreetype6-dev \
    ghostscript \
    ffmpeg \
    locales \
    locales-all

# Install Redis server
log "Installing Redis server..."
apt install -y redis-server

# Install PostgreSQL
log "Installing PostgreSQL..."
apt install -y postgresql postgresql-contrib postgresql-client

# Install Nginx
log "Installing Nginx web server..."
apt install -y nginx

# Install additional tools for document processing
log "Installing document processing tools..."
apt install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-nld \
    poppler-utils \
    wkhtmltopdf \
    pandoc

# Install monitoring and security tools
log "Installing monitoring and security tools..."
apt install -y \
    supervisor \
    fail2ban \
    ufw \
    logrotate \
    rsyslog

# Install SSL certificate tools
log "Installing SSL certificate tools..."
apt install -y certbot python3-certbot-nginx

# Configure locales
log "Configuring locales..."
locale-gen en_US.UTF-8
locale-gen nl_NL.UTF-8
update-locale LANG=en_US.UTF-8

# Set timezone to Amsterdam (Netherlands)
log "Setting timezone to Europe/Amsterdam..."
timedatectl set-timezone Europe/Amsterdam

# Configure firewall
log "Configuring firewall..."
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp

# Allow local connections for services
ufw allow from 127.0.0.1 to any port 5000  # Streamlit
ufw allow from 127.0.0.1 to any port 5432  # PostgreSQL
ufw allow from 127.0.0.1 to any port 6379  # Redis

log "✅ System preparation completed successfully!"
log ""
log "📋 Installed components:"
log "   - Build tools and compilers"
log "   - Python 3 with development headers"
log "   - Redis server"
log "   - PostgreSQL database"
log "   - Nginx web server"
log "   - Document processing tools"
log "   - Security and monitoring tools"
log "   - SSL certificate management"
log ""
log "🔥 Next step: Run 02_python_setup.sh"
echo "=================================================="