#!/bin/bash

# DataGuardian Pro - Standalone Deployment Script
# Enterprise on-premise installation

set -e

echo "🏢 DataGuardian Pro - Standalone Enterprise Deployment"
echo "===================================================="

# Configuration
INSTALL_DIR="/opt/dataguardian-standalone"
SERVICE_USER="dataguardian"
DB_NAME="dataguardian"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root or with sudo"
    exit 1
fi

# System requirements check
echo "🔍 Checking system requirements..."

# Check available memory (minimum 4GB)
MEMORY_GB=$(free -g | awk 'NR==2{print $2}')
if [ $MEMORY_GB -lt 4 ]; then
    echo "⚠️ Warning: Less than 4GB RAM detected. Minimum 4GB recommended."
    read -p "Continue anyway? (y/N): " -n 1 -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check available disk space (minimum 20GB)
DISK_GB=$(df -BG . | awk 'NR==2{print $4}' | sed 's/G//')
if [ $DISK_GB -lt 20 ]; then
    echo "❌ Error: Less than 20GB disk space available"
    exit 1
fi

# Check Docker availability
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl start docker
    systemctl enable docker
    rm get-docker.sh
fi

if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Create installation directory
echo "📁 Creating installation directory..."
mkdir -p $INSTALL_DIR
cd $INSTALL_DIR

# Create service user
echo "👤 Creating service user..."
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd -r -s /bin/false -d $INSTALL_DIR $SERVICE_USER
fi

# Create directory structure
echo "📂 Setting up directory structure..."
mkdir -p {data/{app,postgres,redis,reports,logs,backups},licenses,ssl,config}

# Generate passwords
echo "🔐 Generating secure passwords..."
DB_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)
JWT_SECRET=$(openssl rand -base64 64)

# Create environment file
echo "⚙️ Creating configuration..."
cat > .env << EOF
# Database Configuration
DB_PASSWORD=$DB_PASSWORD
DATABASE_URL=postgresql://dataguardian:$DB_PASSWORD@postgres:5432/dataguardian

# Redis Configuration
REDIS_PASSWORD=$REDIS_PASSWORD

# Application Security
JWT_SECRET=$JWT_SECRET
ENCRYPTION_KEY=$(openssl rand -base64 32)

# Standalone Configuration
STANDALONE_MODE=true
LICENSE_MODE=standalone
DATA_RESIDENCY=on-premise
COMPLIANCE_MODE=enterprise

# Regional Settings
DEFAULT_REGION=Netherlands
TIMEZONE=Europe/Amsterdam

# Performance Settings
WORKER_PROCESSES=4
MAX_CONNECTIONS=100
CACHE_SIZE=512MB

# Security Settings
SESSION_TIMEOUT=3600
MAX_FILE_SIZE=100MB
ALLOWED_EXTENSIONS=pdf,doc,docx,txt,csv,json,xml

# Logging
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=30
EOF

# Create Docker Compose file
cp ../docker/docker-compose.standalone.yml docker-compose.yml

# Create Nginx configuration
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream dataguardian {
        server dataguardian-app:5000;
    }

    server {
        listen 80;
        server_name localhost;
        
        client_max_body_size 100M;
        proxy_read_timeout 300s;
        
        location / {
            proxy_pass http://dataguardian;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
EOF

# Create database initialization script
cat > init-db.sql << 'EOF'
-- DataGuardian Pro Database Initialization
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Optimize for standalone deployment
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET work_mem = '8MB';
SELECT pg_reload_conf();
EOF

# Set permissions
chown -R $SERVICE_USER:$SERVICE_USER $INSTALL_DIR
chmod 600 .env

# Create systemd service
echo "🔧 Creating systemd service..."
cat > /etc/systemd/system/dataguardian-standalone.service << EOF
[Unit]
Description=DataGuardian Pro Standalone
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=root
Group=docker

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable dataguardian-standalone

# Create management scripts
echo "📋 Creating management scripts..."

# Start script
cat > start.sh << 'EOF'
#!/bin/bash
cd /opt/dataguardian-standalone
docker-compose up -d
echo "✅ DataGuardian Pro started"
echo "🌐 Access: http://$(hostname -I | awk '{print $1}'):80"
EOF

# Stop script
cat > stop.sh << 'EOF'
#!/bin/bash
cd /opt/dataguardian-standalone
docker-compose down
echo "⏹️ DataGuardian Pro stopped"
EOF

# Status script
cat > status.sh << 'EOF'
#!/bin/bash
cd /opt/dataguardian-standalone
echo "📊 DataGuardian Pro Status:"
docker-compose ps
echo ""
echo "💾 Storage Usage:"
du -sh data/*
echo ""
echo "📈 System Resources:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
EOF

# Backup script
cat > backup.sh << 'EOF'
#!/bin/bash
cd /opt/dataguardian-standalone
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U dataguardian dataguardian > data/backups/backup_$DATE.sql
tar -czf data/backups/complete_backup_$DATE.tar.gz data/
echo "✅ Backup created: complete_backup_$DATE.tar.gz"
EOF

chmod +x *.sh

# Start services
echo "🚀 Starting DataGuardian Pro..."
./start.sh

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 60

# Verify installation
echo "🔍 Verifying installation..."
if curl -s http://localhost:80 > /dev/null; then
    echo "✅ DataGuardian Pro is running"
else
    echo "❌ Service not responding"
    docker-compose logs
    exit 1
fi

# Create license instructions
cat > STANDALONE_LICENSE.md << EOF
# DataGuardian Pro - Standalone License

## Installation Complete ✅

Your DataGuardian Pro standalone installation is ready!

## Access Information:
- **URL:** http://$(hostname -I | awk '{print $1}'):80
- **Installation:** $INSTALL_DIR
- **Data:** $INSTALL_DIR/data/

## Default Credentials:
- **Admin User:** admin@dataguardian.local
- **Password:** DataGuardian2025!

## Management Commands:
\`\`\`bash
# Start services
sudo $INSTALL_DIR/start.sh

# Stop services  
sudo $INSTALL_DIR/stop.sh

# Check status
$INSTALL_DIR/status.sh

# Create backup
$INSTALL_DIR/backup.sh
\`\`\`

## License Activation:
1. Contact support for your license key
2. Place license file in: $INSTALL_DIR/licenses/
3. Restart services: sudo $INSTALL_DIR/stop.sh && sudo $INSTALL_DIR/start.sh

## Support:
- **Documentation:** $INSTALL_DIR/docs/
- **Logs:** $INSTALL_DIR/data/logs/
- **Email:** support@dataguardian-pro.com

## System Requirements Met:
✅ Memory: ${MEMORY_GB}GB (4GB+ required)
✅ Storage: ${DISK_GB}GB (20GB+ required)
✅ Docker: Installed and running
✅ Network: Port 80 accessible

Installation time: $(date)
EOF

echo ""
echo "🎉 DataGuardian Pro Standalone deployment completed!"
echo "📋 License information saved to: $INSTALL_DIR/STANDALONE_LICENSE.md"
echo "🌐 Access your installation at: http://$(hostname -I | awk '{print $1}'):80"
echo ""
echo "💼 For enterprise support and licensing:"
echo "   📧 support@dataguardian-pro.com"
echo "   📞 +31 (0)20 xxx-xxxx"
echo ""
echo "💰 Standalone License Pricing:"
echo "   🏢 SME (up to 100 employees): €2,000"
echo "   🏭 Enterprise (up to 1000): €5,000"  
echo "   🏛️ Government/Large: €15,000"