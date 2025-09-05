#!/bin/bash
# Quick deployment script for VPS setup
# This script can be copy-pasted directly into your VPS terminal

echo "🚀 DataGuardian Pro Quick VPS Setup"
echo "Server: $(hostname -I | awk '{print $1}')"
echo "Starting automated setup..."

# System Update
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install Python 3.11 and dependencies
echo "🐍 Installing Python 3.11 and dependencies..."
apt install -y python3.11 python3.11-venv python3-pip
apt install -y postgresql postgresql-contrib
apt install -y nginx
apt install -y git curl wget htop nano
apt install -y certbot python3-certbot-nginx

# Create application user
echo "👤 Creating application user..."
useradd -m -s /bin/bash dataguardian || echo "User already exists"
usermod -aG sudo dataguardian

# Setup application directory
echo "📁 Setting up application directory..."
mkdir -p /opt/dataguardian-pro
chown dataguardian:dataguardian /opt/dataguardian-pro

# Switch to application user and setup Python environment
echo "🔧 Setting up Python environment..."
sudo -u dataguardian bash << 'EOF'
cd /opt/dataguardian-pro

# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install streamlit==1.28.1
pip install psycopg2-binary redis pandas numpy requests beautifulsoup4
pip install PyPDF2 reportlab Pillow opencv-python-headless pytesseract
pip install bcrypt PyJWT python-jose stripe openai anthropic
pip install trafilatura tldextract textract pyyaml aiohttp
pip install cachetools cryptography dnspython flask memory-profiler
pip install plotly psutil py-spy pyinstaller python-whois svglib

echo "✅ Python environment setup complete"
EOF

# Configure PostgreSQL
echo "🗄️ Configuring PostgreSQL..."
sudo -u postgres psql << 'EOF'
CREATE DATABASE dataguardian_pro;
CREATE USER dataguardian_user WITH ENCRYPTED PASSWORD 'SecureDbPassword2025!';
GRANT ALL PRIVILEGES ON DATABASE dataguardian_pro TO dataguardian_user;
ALTER USER dataguardian_user CREATEDB;
\q
EOF

# Configure Nginx
echo "🌐 Configuring Nginx..."
cat > /etc/nginx/sites-available/dataguardian-pro << 'EOF'
server {
    listen 80;
    server_name dataguardianpro.nl www.dataguardianpro.nl _;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # Proxy to Streamlit
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts for large uploads
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        client_max_body_size 100M;
    }
    
    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8501/?health=check;
        access_log off;
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/dataguardian-pro /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# Create systemd service
echo "⚙️ Creating systemd service..."
cat > /etc/systemd/system/dataguardian-pro.service << 'EOF'
[Unit]
Description=DataGuardian Pro Streamlit Application
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=exec
User=dataguardian
Group=dataguardian
WorkingDirectory=/opt/dataguardian-pro
Environment=PATH=/opt/dataguardian-pro/venv/bin
Environment=DATABASE_URL=postgresql://dataguardian_user:SecureDbPassword2025!@localhost:5432/dataguardian_pro
Environment=STREAMLIT_SERVER_PORT=8501
Environment=STREAMLIT_SERVER_ADDRESS=127.0.0.1
Environment=STREAMLIT_SERVER_HEADLESS=true
Environment=REGION=Netherlands
ExecStart=/opt/dataguardian-pro/venv/bin/streamlit run app.py --server.port 8501 --server.address 127.0.0.1 --server.headless true
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Configure firewall
echo "🔥 Configuring firewall..."
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable

# Start services
echo "🚀 Starting services..."
systemctl daemon-reload
systemctl enable postgresql nginx dataguardian-pro
systemctl start postgresql nginx

echo ""
echo "✅ VPS Setup Complete!"
echo "📋 NEXT STEPS:"
echo "1. Upload your DataGuardian Pro files to: /opt/dataguardian-pro/"
echo "2. Start application: sudo systemctl start dataguardian-pro"
echo "3. Check logs: sudo journalctl -u dataguardian-pro -f"
echo "4. Access at: http://$(curl -s ifconfig.me)/"
echo ""
echo "📁 Ready for file upload at: /opt/dataguardian-pro/"