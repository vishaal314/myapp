#!/bin/bash
# DataGuardian Pro - Quick Server Deployment
# Run this script directly on your server

set -e

echo "🚀 DataGuardian Pro - Quick Server Deployment"
echo "============================================="

# Configuration
INSTALL_DIR="/opt/dataguardian"
SERVICE_USER="dataguardian"
DOMAIN_OR_IP="45.81.35.202"  # Update if needed

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

log "Starting deployment..."

# 1. SYSTEM SETUP
log "=== Installing system packages ==="
apt-get update -y >/dev/null 2>&1
apt-get install -y python3.11 python3.11-venv python3-pip git curl \
    postgresql postgresql-contrib redis-server nginx docker.io \
    docker-compose unzip >/dev/null 2>&1
check_command "System packages"

# 2. DOCKER SETUP (Simple approach)
log "=== Setting up Docker ==="
systemctl start docker
systemctl enable docker
usermod -aG docker root
check_command "Docker setup"

# 3. CREATE DEPLOYMENT DIRECTORY
log "=== Setting up directories ==="
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# 4. CREATE DOCKER COMPOSE FILE
log "=== Creating Docker Compose configuration ==="
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  dataguardian:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://dataguardian:dataguardian_secure@postgres:5432/dataguardian
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET=dataguardian_jwt_secret_2025_production
      - DATAGUARDIAN_MASTER_KEY=gQJ6WV5FxDgGWj-vQqRzHqS4CIUOGFaXRqsGXNLJHbU=
      - ENVIRONMENT=production
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_SERVER_PORT=5000
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=dataguardian
      - POSTGRES_USER=dataguardian
      - POSTGRES_PASSWORD=dataguardian_secure
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    ports:
      - "6379:6379"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - dataguardian
    restart: unless-stopped

volumes:
  postgres_data:
EOF

# 5. CREATE NGINX CONFIG
log "=== Creating Nginx configuration ==="
cat > nginx.conf << 'EOF'
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
        client_max_body_size 200M;

        location / {
            proxy_pass http://dataguardian;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
            proxy_read_timeout 86400;
        }
    }
}
EOF

check_command "Configuration files"

log "=== Setup complete! ==="
echo ""
echo "📋 NEXT STEPS:"
echo "1. Upload your DataGuardian Pro source code to: $INSTALL_DIR"
echo "2. Ensure you have these files:"
echo "   - app.py (main application)"
echo "   - Dockerfile"
echo "   - requirements.txt"
echo "   - All utils/, services/, components/ directories"
echo ""
echo "3. Run deployment:"
echo "   cd $INSTALL_DIR"
echo "   docker-compose up -d"
echo ""
echo "🌐 Your app will be available at: http://$DOMAIN_OR_IP"
echo ""
echo "🔧 Management commands:"
echo "   docker-compose logs -f dataguardian  # View logs"
echo "   docker-compose restart dataguardian  # Restart app"
echo "   docker-compose down                  # Stop all services"
echo "   docker-compose up -d                 # Start all services"

log "Quick setup completed successfully!"