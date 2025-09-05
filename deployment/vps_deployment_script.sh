#!/bin/bash
# DataGuardian Pro VPS Deployment Script for Retzor Server
# Server: vishaalnoord7.retzor.com (45.81.35.202)
# Date: September 5, 2025

set -e

echo "🚀 Starting DataGuardian Pro deployment on Retzor VPS..."

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

# Install Node.js for any frontend assets
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Create application user
echo "👤 Creating application user..."
useradd -m -s /bin/bash dataguardian
usermod -aG sudo dataguardian

# Setup application directory
echo "📁 Setting up application directory..."
mkdir -p /opt/dataguardian-pro
chown dataguardian:dataguardian /opt/dataguardian-pro

# Switch to application user
sudo -u dataguardian bash << 'EOF'
cd /opt/dataguardian-pro

# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install streamlit==1.28.1
pip install psycopg2-binary
pip install redis
pip install pandas
pip install numpy
pip install requests
pip install beautifulsoup4
pip install PyPDF2
pip install reportlab
pip install Pillow
pip install opencv-python-headless
pip install pytesseract
pip install bcrypt
pip install PyJWT
pip install python-jose
pip install stripe
pip install openai
pip install anthropic
pip install trafilatura
pip install tldextract
pip install textract
pip install pyyaml
pip install aiohttp
pip install cachetools
pip install cryptography
pip install dnspython
pip install flask
pip install memory-profiler
pip install plotly
pip install psutil
pip install py-spy
pip install pyinstaller
pip install python-whois
pip install svglib

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
    server_name vishaalnoord7.retzor.com;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
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
        
        # WebSocket support for Streamlit
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Increase timeouts for large file uploads
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        client_max_body_size 100M;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8501/health;
        access_log off;
    }
    
    # Static files (if any)
    location /static/ {
        alias /opt/dataguardian-pro/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
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
Environment=STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
Environment=REGION=Netherlands
Environment=GDPR_JURISDICTION=EU
Environment=DATA_RESIDENCY=Netherlands
ExecStart=/opt/dataguardian-pro/venv/bin/streamlit run app.py --server.port 8501 --server.address 127.0.0.1 --server.headless true
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/dataguardian-pro

[Install]
WantedBy=multi-user.target
EOF

# Configure firewall
echo "🔥 Configuring firewall..."
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable

# Create deployment script
cat > /opt/dataguardian-pro/deploy.sh << 'EOF'
#!/bin/bash
# DataGuardian Pro deployment helper

echo "🔄 Stopping application..."
sudo systemctl stop dataguardian-pro

echo "📥 Pulling latest changes..."
# Note: You'll need to set up git repository access
# git pull origin main

echo "📦 Installing/updating dependencies..."
source venv/bin/activate
pip install --upgrade -r requirements.txt

echo "🔄 Starting application..."
sudo systemctl start dataguardian-pro
sudo systemctl status dataguardian-pro

echo "✅ Deployment complete!"
echo "🌐 Application available at: http://vishaalnoord7.retzor.com"
EOF

chmod +x /opt/dataguardian-pro/deploy.sh
chown dataguardian:dataguardian /opt/dataguardian-pro/deploy.sh

# Start and enable services
echo "🚀 Starting services..."
systemctl daemon-reload
systemctl enable postgresql
systemctl enable nginx
systemctl enable dataguardian-pro

systemctl start postgresql
systemctl start nginx

echo "✅ DataGuardian Pro deployment completed!"
echo ""
echo "📋 DEPLOYMENT SUMMARY:"
echo "🌐 Domain: vishaalnoord7.retzor.com"
echo "🗄️ Database: PostgreSQL (dataguardian_pro)"
echo "👤 User: dataguardian"
echo "📁 Path: /opt/dataguardian-pro"
echo ""
echo "📝 NEXT STEPS:"
echo "1. Upload your application files to /opt/dataguardian-pro/"
echo "2. Run: sudo systemctl start dataguardian-pro"
echo "3. Setup SSL: sudo certbot --nginx -d vishaalnoord7.retzor.com"
echo "4. Check status: sudo systemctl status dataguardian-pro"
echo ""
echo "🔧 USEFUL COMMANDS:"
echo "- View logs: sudo journalctl -u dataguardian-pro -f"
echo "- Restart app: sudo systemctl restart dataguardian-pro"
echo "- Nginx status: sudo systemctl status nginx"
echo "- Database access: sudo -u postgres psql dataguardian_pro"