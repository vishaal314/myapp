#!/bin/bash

# DataGuardian Pro - Quick Start Script for Hetzner
# Run this ONE command to deploy everything

echo "🚀 DataGuardian Pro - Hetzner Quick Deployment"
echo "=============================================="
echo "This will set up DataGuardian Pro in 15 minutes for €5/month"
echo ""

# Get server details
read -p "🌐 Enter your domain name (or press Enter to use IP): " DOMAIN_NAME
read -p "🔑 Enter your OpenAI API key: " OPENAI_KEY
read -p "💳 Enter your Stripe secret key (optional): " STRIPE_KEY

echo ""
echo "🔄 Starting automated deployment..."

# Update system and install dependencies
echo "📦 Installing system dependencies..."
apt update && apt upgrade -y
apt install -y docker.io docker-compose postgresql nginx certbot python3-certbot-nginx git curl ufw htop

# Start services
systemctl start docker postgresql nginx
systemctl enable docker postgresql nginx

# Configure firewall
ufw allow ssh && ufw allow http && ufw allow https && ufw --force enable

# Setup PostgreSQL
echo "🗄️ Setting up database..."
DB_PASSWORD=$(openssl rand -base64 32)
sudo -u postgres createuser --createdb dataguardian 2>/dev/null || true
sudo -u postgres createdb dataguardian_prod --owner=dataguardian 2>/dev/null || true
sudo -u postgres psql -c "ALTER USER dataguardian PASSWORD '$DB_PASSWORD';"

# Optimize PostgreSQL
cat >> /etc/postgresql/*/main/postgresql.conf << EOF
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
work_mem = 4MB
EOF
systemctl restart postgresql

# Create application directory
mkdir -p /opt/dataguardian && cd /opt/dataguardian

# Create Docker Compose file
cat > docker-compose.yml << EOF
version: '3.8'
services:
  dataguardian:
    build: .
    ports:
      - "127.0.0.1:5000:5000"
    environment:
      - DATABASE_URL=postgresql://dataguardian:$DB_PASSWORD@host.docker.internal:5432/dataguardian_prod
      - OPENAI_API_KEY=$OPENAI_KEY
      - STRIPE_SECRET_KEY=$STRIPE_KEY
      - DEFAULT_REGION=Netherlands
    restart: unless-stopped
    extra_hosts:
      - "host.docker.internal:host-gateway"
EOF

# Create Dockerfile
cat > Dockerfile << EOF
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc libpq-dev tesseract-ocr && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN mkdir -p logs reports temp
EXPOSE 5000
CMD ["streamlit", "run", "app.py", "--server.port=5000", "--server.address=0.0.0.0", "--server.headless=true"]
EOF

# Create requirements.txt
cat > requirements.txt << EOF
streamlit>=1.28.0
psycopg2-binary>=2.9.7
pandas>=2.0.3
plotly>=5.15.0
pillow>=10.0.0
beautifulsoup4>=4.12.2
requests>=2.31.0
openai>=1.3.0
stripe>=6.6.0
bcrypt>=4.0.1
pyjwt>=2.8.0
EOF

# Setup Nginx
cat > /etc/nginx/sites-available/dataguardian << EOF
server {
    listen 80;
    server_name ${DOMAIN_NAME:-_};
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

ln -sf /etc/nginx/sites-available/dataguardian /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

echo ""
echo "✅ Basic setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Copy your DataGuardian Pro source code to: /opt/dataguardian/"
echo "2. Run: cd /opt/dataguardian && docker-compose up -d"
if [ ! -z "$DOMAIN_NAME" ]; then
echo "3. Setup SSL: certbot --nginx -d $DOMAIN_NAME"
fi
echo ""
echo "💰 Cost: €4.90/month"
echo "🔐 Database password: $DB_PASSWORD"
echo "🌐 Access: http://$(curl -s ifconfig.me)"
echo ""
echo "📖 Full documentation: deployment/hetzner/DEPLOYMENT_GUIDE.md"