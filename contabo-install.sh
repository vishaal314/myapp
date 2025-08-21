#!/bin/bash

# Contabo VPS Automated Setup Script for DataGuardian Pro
# Run this script on a fresh Contabo Ubuntu 22.04 VPS

set -e

echo "🚀 Starting DataGuardian Pro installation on Contabo VPS..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root (use sudo)"
    exit 1
fi

# Update system
print_status "Updating system packages..."
apt update && apt upgrade -y

# Install essential packages
print_status "Installing essential packages..."
apt install -y curl wget git nano htop unzip ufw fail2ban

# Create dataguardian user
print_status "Creating dataguardian user..."
if ! id "dataguardian" &>/dev/null; then
    adduser --disabled-password --gecos "" dataguardian
    usermod -aG sudo dataguardian
    print_status "User 'dataguardian' created successfully"
else
    print_warning "User 'dataguardian' already exists"
fi

# Setup SSH key for dataguardian user
if [ -f /root/.ssh/authorized_keys ]; then
    print_status "Setting up SSH keys for dataguardian user..."
    mkdir -p /home/dataguardian/.ssh
    cp /root/.ssh/authorized_keys /home/dataguardian/.ssh/
    chown -R dataguardian:dataguardian /home/dataguardian/.ssh
    chmod 700 /home/dataguardian/.ssh
    chmod 600 /home/dataguardian/.ssh/authorized_keys
fi

# Install Docker
print_status "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl enable docker
    systemctl start docker
    usermod -aG docker dataguardian
    rm get-docker.sh
    print_status "Docker installed successfully"
else
    print_warning "Docker already installed"
fi

# Install Docker Compose
print_status "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    print_status "Docker Compose installed successfully"
else
    print_warning "Docker Compose already installed"
fi

# Setup firewall
print_status "Configuring firewall..."
ufw --force enable
ufw allow ssh
ufw allow 80
ufw allow 443
ufw allow 8501

# Install Nginx
print_status "Installing Nginx..."
apt install -y nginx
systemctl enable nginx

# Install Certbot
print_status "Installing Certbot for SSL certificates..."
apt install -y certbot python3-certbot-nginx

# Create directory structure
print_status "Creating directory structure..."
mkdir -p /home/dataguardian/{backups,logs}
chown -R dataguardian:dataguardian /home/dataguardian

# Setup automatic backups
print_status "Setting up backup script..."
cat > /home/dataguardian/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/dataguardian/backups"
mkdir -p $BACKUP_DIR

# Backup database
cd /home/dataguardian/dataguardian-pro
docker-compose exec -T db pg_dump -U postgres dataguardian > $BACKUP_DIR/db_backup_$DATE.sql

# Backup application data
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz /home/dataguardian/dataguardian-pro --exclude=/home/dataguardian/dataguardian-pro/logs

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "$(date): Backup completed" >> /home/dataguardian/backup.log
EOF

chmod +x /home/dataguardian/backup.sh
chown dataguardian:dataguardian /home/dataguardian/backup.sh

# Setup monitoring script
print_status "Setting up monitoring script..."
cat > /home/dataguardian/monitor.sh << 'EOF'
#!/bin/bash
if ! curl -s http://localhost:8501/_stcore/health > /dev/null; then
    echo "$(date): DataGuardian Pro is down, restarting..." >> /home/dataguardian/monitor.log
    cd /home/dataguardian/dataguardian-pro
    docker-compose restart app
fi
EOF

chmod +x /home/dataguardian/monitor.sh
chown dataguardian:dataguardian /home/dataguardian/monitor.sh

# Create systemd service for monitoring
print_status "Creating monitoring service..."
cat > /etc/systemd/system/dataguardian-monitor.service << 'EOF'
[Unit]
Description=DataGuardian Pro Monitor
After=docker.service

[Service]
Type=oneshot
User=dataguardian
ExecStart=/home/dataguardian/monitor.sh
EOF

cat > /etc/systemd/system/dataguardian-monitor.timer << 'EOF'
[Unit]
Description=Run DataGuardian Pro Monitor every 5 minutes
Requires=dataguardian-monitor.service

[Timer]
OnCalendar=*:0/5
Persistent=true

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable dataguardian-monitor.timer
systemctl start dataguardian-monitor.timer

# Create sample environment file
print_status "Creating sample environment file..."
cat > /home/dataguardian/.env.sample << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://postgres:dataguardian_secure_2024@db:5432/dataguardian

# Stripe Configuration (Required)
STRIPE_PUBLISHABLE_KEY=pk_live_your_publishable_key_here
STRIPE_SECRET_KEY=sk_live_your_secret_key_here

# Security Keys (Generate 32-character random strings)
JWT_SECRET=your_32_character_jwt_secret_here
ENCRYPTION_KEY=your_32_character_encryption_key_here

# Application Settings
ENVIRONMENT=production
STREAMLIT_SERVER_HEADLESS=true
PYTHONPATH=/app
REDIS_URL=redis://redis:6379

# Optional: Email notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EOF

chown dataguardian:dataguardian /home/dataguardian/.env.sample

# Set up log rotation
print_status "Setting up log rotation..."
cat > /etc/logrotate.d/dataguardian << 'EOF'
/home/dataguardian/dataguardian-pro/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    copytruncate
    su dataguardian dataguardian
}

/home/dataguardian/*.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    copytruncate
    su dataguardian dataguardian
}
EOF

# Create deployment script
print_status "Creating deployment script..."
cat > /home/dataguardian/deploy.sh << 'EOF'
#!/bin/bash

echo "🚀 Deploying DataGuardian Pro..."

# Check if repository exists
if [ ! -d "/home/dataguardian/dataguardian-pro" ]; then
    echo "Please clone your DataGuardian Pro repository first:"
    echo "git clone https://github.com/yourusername/dataguardian-pro.git"
    exit 1
fi

cd /home/dataguardian/dataguardian-pro

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Please create .env file first:"
    echo "cp /home/dataguardian/.env.sample /home/dataguardian/dataguardian-pro/.env"
    echo "Then edit .env with your actual configuration"
    exit 1
fi

# Pull latest changes
git pull

# Build and start services
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Wait for services to start
sleep 30

# Test if application is running
if curl -s http://localhost:8501/_stcore/health > /dev/null; then
    echo "✅ DataGuardian Pro deployed successfully!"
    echo "🌐 Access your application at: http://$(curl -s ifconfig.me):8501"
else
    echo "❌ Deployment failed. Check logs:"
    echo "docker-compose logs app"
fi
EOF

chmod +x /home/dataguardian/deploy.sh
chown dataguardian:dataguardian /home/dataguardian/deploy.sh

# Security hardening
print_status "Applying security hardening..."

# Configure fail2ban
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
EOF

systemctl restart fail2ban

# Secure shared memory
echo "tmpfs /run/shm tmpfs defaults,noexec,nosuid 0 0" >> /etc/fstab

# Print completion message
print_status "Installation completed successfully!"
echo ""
echo "🎉 Contabo VPS setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Switch to dataguardian user: su - dataguardian"
echo "2. Clone your repository: git clone https://github.com/yourusername/dataguardian-pro.git"
echo "3. Copy environment file: cp .env.sample dataguardian-pro/.env"
echo "4. Edit environment file: nano dataguardian-pro/.env"
echo "5. Deploy application: ./deploy.sh"
echo ""
echo "🔧 Useful commands:"
echo "- Check application: docker-compose ps"
echo "- View logs: docker-compose logs app"
echo "- Restart services: docker-compose restart"
echo "- System monitoring: htop"
echo ""
echo "🌐 Your server IP: $(curl -s ifconfig.me)"
echo ""
echo "💡 Remember to:"
echo "- Configure your domain DNS to point to this IP"
echo "- Setup SSL certificate: sudo certbot --nginx -d yourdomain.com"
echo "- Configure Stripe keys in .env file"
echo ""

# Create a summary file
cat > /home/dataguardian/SETUP_SUMMARY.txt << EOF
DataGuardian Pro - Contabo VPS Setup Summary
============================================

Server IP: $(curl -s ifconfig.me)
Setup Date: $(date)
VPS Specs: 4 vCPU, 8GB RAM, 200GB SSD
Cost: €4.99/month

Installed Services:
- Docker & Docker Compose
- Nginx (web server)
- Certbot (SSL certificates)
- UFW Firewall
- Fail2ban (security)
- Automatic backups (daily)
- Health monitoring (every 5 minutes)

File Locations:
- Application: /home/dataguardian/dataguardian-pro/
- Backups: /home/dataguardian/backups/
- Logs: /home/dataguardian/dataguardian-pro/logs/
- Environment: /home/dataguardian/dataguardian-pro/.env

Scripts:
- Deploy: /home/dataguardian/deploy.sh
- Backup: /home/dataguardian/backup.sh
- Monitor: /home/dataguardian/monitor.sh

Next Steps:
1. Clone your DataGuardian Pro repository
2. Configure .env file with your settings
3. Run deploy.sh to start the application
4. Setup domain and SSL certificate

Support:
- Contabo: my.contabo.com
- Documentation: This file and setup guides
EOF

chown dataguardian:dataguardian /home/dataguardian/SETUP_SUMMARY.txt

print_status "Setup summary saved to /home/dataguardian/SETUP_SUMMARY.txt"