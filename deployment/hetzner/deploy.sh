#!/bin/bash

# DataGuardian Pro - Hetzner Cloud Deployment Script
# This script sets up DataGuardian Pro on a Hetzner CX21 server
# Cost: €5/month with Netherlands UAVG compliance

set -e

echo "🚀 Starting DataGuardian Pro deployment on Hetzner Cloud..."

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install required packages
echo "🔧 Installing Docker, PostgreSQL, and dependencies..."
apt install -y \
    docker.io \
    docker-compose \
    postgresql \
    postgresql-contrib \
    nginx \
    certbot \
    python3-certbot-nginx \
    git \
    curl \
    ufw

# Start and enable services
systemctl start docker
systemctl enable docker
systemctl start postgresql
systemctl enable postgresql
systemctl start nginx
systemctl enable nginx

# Configure firewall
echo "🔥 Configuring firewall..."
ufw allow ssh
ufw allow http
ufw allow https
ufw --force enable

# Setup PostgreSQL
echo "🗄️ Setting up PostgreSQL database..."
sudo -u postgres createuser --createdb dataguardian
sudo -u postgres createdb dataguardian_prod --owner=dataguardian

# Generate random password for PostgreSQL
DB_PASSWORD=$(openssl rand -base64 32)
sudo -u postgres psql -c "ALTER USER dataguardian PASSWORD '$DB_PASSWORD';"

# Configure PostgreSQL for production
echo "🔐 Configuring PostgreSQL for production..."
cat >> /etc/postgresql/*/main/postgresql.conf << EOF
# Performance optimizations for 8GB RAM
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB
EOF

# Configure PostgreSQL authentication
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/" /etc/postgresql/*/main/postgresql.conf
echo "host dataguardian_prod dataguardian 127.0.0.1/32 md5" >> /etc/postgresql/*/main/pg_hba.conf

systemctl restart postgresql

# Create application directory
echo "📁 Creating application directory..."
mkdir -p /opt/dataguardian
cd /opt/dataguardian

# Clone repository (replace with your actual repository)
echo "📥 Cloning DataGuardian Pro repository..."
# git clone https://github.com/yourusername/dataguardian-pro.git .
# For now, we'll create the necessary files

# Create environment file
echo "⚙️ Creating environment configuration..."
cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://dataguardian:$DB_PASSWORD@localhost:5432/dataguardian_prod
PGUSER=dataguardian
PGPASSWORD=$DB_PASSWORD
PGDATABASE=dataguardian_prod
PGHOST=localhost
PGPORT=5432

# Application Configuration
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_PORT=5000
STREAMLIT_SERVER_HEADLESS=true

# Security
JWT_SECRET=$(openssl rand -base64 64)
ENCRYPTION_KEY=$(openssl rand -base64 32)

# Netherlands Compliance
DEFAULT_REGION=Netherlands
DATA_RESIDENCY=EU
COMPLIANCE_MODE=UAVG

# External Services (add your API keys)
OPENAI_API_KEY=your_openai_key_here
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here
EOF

# Create Docker Compose file
echo "🐳 Creating Docker Compose configuration..."
cat > docker-compose.yml << EOF
version: '3.8'

services:
  dataguardian:
    build: .
    container_name: dataguardian_app
    ports:
      - "127.0.0.1:5000:5000"
    environment:
      - DATABASE_URL=postgresql://dataguardian:$DB_PASSWORD@host.docker.internal:5432/dataguardian_prod
    env_file:
      - .env
    restart: unless-stopped
    depends_on:
      - postgres-check
    extra_hosts:
      - "host.docker.internal:host-gateway"
    volumes:
      - ./logs:/app/logs
      - ./reports:/app/reports
      - ./temp:/app/temp

  postgres-check:
    image: postgres:16
    command: pg_isready -h host.docker.internal -p 5432 -U dataguardian
    extra_hosts:
      - "host.docker.internal:host-gateway"
    depends_on: []
EOF

# Create Dockerfile
echo "🔨 Creating Dockerfile..."
cat > Dockerfile << EOF
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    libpq-dev \\
    tesseract-ocr \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs reports temp static/uploads

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:5000 || exit 1

# Run application
CMD ["streamlit", "run", "app.py", "--server.port=5000", "--server.address=0.0.0.0", "--server.headless=true"]
EOF

# Create requirements.txt with all dependencies
echo "📋 Creating requirements.txt..."
cat > requirements.txt << EOF
streamlit>=1.28.0
psycopg2-binary>=2.9.7
pandas>=2.0.3
plotly>=5.15.0
pillow>=10.0.0
beautifulsoup4>=4.12.2
requests>=2.31.0
trafilatura>=1.6.2
tldextract>=3.4.4
pytesseract>=0.3.10
opencv-python-headless>=4.8.0
bcrypt>=4.0.1
pyjwt>=2.8.0
redis>=4.6.0
reportlab>=4.0.4
pypdf2>=3.0.1
textract>=1.6.5
openai>=1.3.0
anthropic>=0.5.0
stripe>=6.6.0
pyyaml>=6.0.1
cryptography>=41.0.4
cachetools>=5.3.1
python-jose>=3.3.0
aiohttp>=3.8.5
memory-profiler>=0.61.0
psutil>=5.9.5
svglib>=1.7.0
dnspython>=2.4.2
python-whois>=0.8.0
py-spy>=0.3.14
pyinstaller>=5.13.2
psycopg2-pool>=1.1
EOF

# Create Nginx configuration
echo "🌐 Configuring Nginx reverse proxy..."
cat > /etc/nginx/sites-available/dataguardian << EOF
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support for Streamlit
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Increase timeout for large file uploads
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
        
        # Increase client body size for file uploads
        client_max_body_size 100M;
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/dataguardian /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# Set proper permissions
chown -R www-data:www-data /opt/dataguardian
chmod -R 755 /opt/dataguardian

echo "✅ Base system setup complete!"
echo ""
echo "🔑 Database Password: $DB_PASSWORD"
echo "📁 Application Directory: /opt/dataguardian"
echo ""
echo "Next steps:"
echo "1. Copy your DataGuardian Pro source code to /opt/dataguardian/"
echo "2. Update .env file with your API keys"
echo "3. Run: cd /opt/dataguardian && docker-compose up -d"
echo "4. Setup SSL with: certbot --nginx -d yourdomain.com"
echo ""
echo "💰 Monthly cost: €4.90 (Hetzner CX21)"
echo "🌍 Compliance: EU/Netherlands UAVG ready"