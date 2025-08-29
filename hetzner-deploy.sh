#!/bin/bash
# DataGuardian Pro - Hetzner Deployment Script
# For Amsterdam datacenter deployment with GDPR compliance

echo "🚀 DataGuardian Pro - Hetzner Deployment"
echo "========================================="

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
echo "📋 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install PostgreSQL
echo "🗄️ Installing PostgreSQL..."
sudo apt install -y postgresql postgresql-contrib

# Install Redis
echo "🔄 Installing Redis..."
sudo apt install -y redis-server

# Configure PostgreSQL
echo "⚙️ Configuring PostgreSQL..."
sudo -u postgres createuser --createdb dataguardian
sudo -u postgres createdb dataguardian_prod
sudo -u postgres psql -c "ALTER USER dataguardian PASSWORD 'secure_password_2024';"

# Configure Redis
echo "🔧 Configuring Redis..."
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Create application directory
echo "📁 Setting up application directory..."
mkdir -p /opt/dataguardian
cd /opt/dataguardian

# Clone or prepare application
echo "📥 Preparing application files..."
# Note: Replace this with actual deployment method
echo "Copy your DataGuardian Pro files to /opt/dataguardian/"

# Create environment file
echo "🔒 Creating environment configuration..."
cat > .env << EOF
# Production Environment
ENVIRONMENT=production

# Database Configuration
DATABASE_URL=postgresql://dataguardian:secure_password_2024@localhost:5432/dataguardian_prod

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Security Settings
SAP_SSL_VERIFY=true
SALESFORCE_TIMEOUT=30
SAP_REQUEST_TIMEOUT=30
OIDC_TIMEOUT=30

# GDPR Compliance
DATA_RESIDENCY=EU
PRIVACY_POLICY_URL=https://dataguardian.nl/privacy
TERMS_URL=https://dataguardian.nl/terms

# Application Settings
LOG_LEVEL=INFO
DEBUG=false
EOF

# Create Docker Compose file
echo "🐳 Creating Docker Compose configuration..."
cat > docker-compose.yml << EOF
version: '3.8'

services:
  dataguardian:
    build: .
    ports:
      - "5000:5000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://dataguardian:secure_password_2024@host.docker.internal:5432/dataguardian_prod
      - REDIS_URL=redis://host.docker.internal:6379/0
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    depends_on:
      - postgres
      - redis
    extra_hosts:
      - "host.docker.internal:host-gateway"

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: dataguardian_prod
      POSTGRES_USER: dataguardian
      POSTGRES_PASSWORD: secure_password_2024
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - dataguardian
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
EOF

# Create Nginx configuration
echo "🌐 Creating Nginx configuration..."
cat > nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    upstream dataguardian {
        server dataguardian:5000;
    }

    server {
        listen 80;
        server_name _;
        return 301 https://\$server_name\$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name _;

        # SSL Configuration (add your certificates)
        # ssl_certificate /etc/nginx/ssl/cert.pem;
        # ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";

        location / {
            proxy_pass http://dataguardian;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            
            # WebSocket support for Streamlit
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
EOF

# Set up firewall
echo "🔥 Configuring firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Create systemd service
echo "⚙️ Creating systemd service..."
sudo cat > /etc/systemd/system/dataguardian.service << EOF
[Unit]
Description=DataGuardian Pro Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/dataguardian
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Deployment script completed!"
echo ""
echo "Next steps:"
echo "1. Copy your DataGuardian Pro code to /opt/dataguardian/"
echo "2. Build the Docker image: docker-compose build"
echo "3. Start services: sudo systemctl enable dataguardian && sudo systemctl start dataguardian"
echo "4. Configure domain and SSL certificates"
echo "5. Test at http://your-server-ip:5000"
echo ""
echo "💰 Monthly costs:"
echo "- Hetzner CAX11: €2.09"
echo "- Backup: €0.60 (optional)"
echo "- Domain: ~€10/year"
echo "- Total: €2.69/month + domain"