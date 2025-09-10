# DataGuardian Pro Deployment Manual

## 🚀 Manual Deployment Guide

### Prerequisites

**System Requirements:**
- Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- 4GB RAM minimum (8GB recommended)
- 20GB disk space minimum
- Root or sudo access
- Domain name pointing to your server

**Required Software:**
- Docker 20.10+
- Docker Compose 2.0+

---

## 📋 Method 1: Manual Step-by-Step Deployment

### Step 1: Server Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y curl wget git htop nano ufw fail2ban openssl

# Configure firewall
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

### Step 2: Install Docker & Docker Compose

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl enable docker
sudo systemctl start docker
rm get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add current user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Step 3: Prepare Application Directory

```bash
# Create application directory
sudo mkdir -p /opt/dataguardian-pro
sudo chown $USER:$USER /opt/dataguardian-pro
cd /opt/dataguardian-pro

# Create subdirectories
mkdir -p {data,logs,cache,reports,backups,ssl,certbot-var}
mkdir -p backups/{database,files}
```

### Step 4: Upload Application Files

```bash
# Option A: Git clone (if repository is accessible)
git clone https://github.com/yourusername/dataguardian-pro.git .

# Option B: Manual upload
# Upload these files to /opt/dataguardian-pro/:
# - app.py (main application)
# - docker-compose.prod.yml
# - Dockerfile
# - production_requirements.txt
# - All Python modules and assets
```

### Step 5: Configure Environment Variables

```bash
# Copy the production environment template
cp production.env.template .env

# Generate secure passwords and keys
DB_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -hex 32)

# Update .env with generated values
sed -i "s/generate_secure_password_here/$DB_PASSWORD/g" .env
sed -i "s/generate_32_char_secret_key_here/$SECRET_KEY/g" .env

# IMPORTANT: Edit .env file to configure your domain and API keys
nano .env

# Set these required values in .env:
# DOMAIN=your-actual-domain.com
# CERTBOT_EMAIL=your-email@domain.com  
# OPENAI_API_KEY=your_actual_openai_key
# STRIPE_SECRET_KEY=your_actual_stripe_key
```

**Required Configuration:**
Before proceeding, you **must** edit the `.env` file and set:
- `DOMAIN` - Your actual domain name 
- `CERTBOT_EMAIL` - Valid email for SSL certificates
- `OPENAI_API_KEY` - Your OpenAI API key
- `STRIPE_SECRET_KEY` - Your Stripe secret key

### Step 6: Prepare SSL Directory and Web Root

```bash
# Create SSL and web root directories for container mounting
mkdir -p ssl/live ssl/archive
mkdir -p /var/www/html
sudo chown -R $USER:$USER ssl

# Make web root accessible for Let's Encrypt challenges
sudo mkdir -p /var/www/html
sudo chown -R $USER:$USER /var/www/html
```

### Step 7: Build and Start Application

```bash
# Build Docker image
docker build -t dataguardian-pro:latest .

# Start services (nginx will handle SSL automatically)
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs to monitor SSL certificate generation
docker-compose -f docker-compose.prod.yml logs -f certbot
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### Step 8: Generate SSL Certificates (Container-based)

```bash
# Generate SSL certificate using the containerized certbot
# This will automatically use the domain from your .env file
docker-compose -f docker-compose.prod.yml run --rm certbot

# Check certificate generation
docker-compose -f docker-compose.prod.yml logs certbot

# Restart nginx to load certificates
docker-compose -f docker-compose.prod.yml restart nginx

# Set up automatic certificate renewal
echo "0 12 * * * cd /opt/dataguardian-pro && docker-compose -f docker-compose.prod.yml run --rm certbot renew" | crontab -
```

### Step 9: Configure Security

```bash
# Configure fail2ban
sudo tee /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
EOF

sudo systemctl enable fail2ban
sudo systemctl restart fail2ban
```

### Step 10: Setup Monitoring and Backups

```bash
# Setup log rotation
sudo tee /etc/logrotate.d/dataguardian-pro << 'EOF'
/opt/dataguardian-pro/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 root root
    postrotate
        docker-compose -f /opt/dataguardian-pro/docker-compose.prod.yml restart dataguardian-pro
    endscript
}
EOF

# Create backup script
tee /opt/dataguardian-pro/backup.sh << 'EOF'
#!/bin/bash
timestamp=$(date +%Y%m%d_%H%M%S)
backup_dir="/opt/dataguardian-pro/backups"

# Database backup
docker exec dataguardian-postgres pg_dump -U dataguardian_pro dataguardian_pro > "$backup_dir/database/backup_$timestamp.sql"

# Files backup
tar -czf "$backup_dir/files/files_backup_$timestamp.tar.gz" -C /opt/dataguardian-pro data reports

# Cleanup old backups (keep 7 days)
find "$backup_dir/database" -name "backup_*.sql" -mtime +7 -delete
find "$backup_dir/files" -name "files_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: $timestamp"
EOF

chmod +x /opt/dataguardian-pro/backup.sh

# Schedule daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/dataguardian-pro/backup.sh") | crontab -
```

---

## 🐳 Method 2: Docker Deployment (Alternative)

### Quick Docker Setup

```bash
# 1. Create project directory
mkdir ~/dataguardian-pro && cd ~/dataguardian-pro

# 2. Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://postgres:password@db:5432/dataguardian_pro
    depends_on:
      - db
      - redis
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: dataguardian_pro
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes

volumes:
  postgres_data:
EOF

# 3. Upload application files or clone repository

# 4. Build and run
docker-compose up -d

# 5. Check logs
docker-compose logs -f
```

### Docker Single Container Deployment

```bash
# Build image
docker build -t dataguardian-pro .

# Run with external database
docker run -d \
  --name dataguardian-pro \
  -p 5000:5000 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
  -e REDIS_URL="redis://redis-host:6379" \
  -e OPENAI_API_KEY="your-key" \
  -v $(pwd)/data:/app/data \
  dataguardian-pro:latest
```

---

## 🔧 Post-Deployment Steps

### Verify Installation

```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# Test application
curl -f http://localhost:5000

# Test SSL (if configured)
curl -f https://your-domain.com

# Check database connectivity
docker exec -it dataguardian-postgres psql -U dataguardian_pro -d dataguardian_pro -c "SELECT version();"
```

### Application Setup

1. **Access Application**: Visit `https://your-domain.com`
2. **Create Admin User**: Follow first-time setup wizard
3. **Configure API Keys**: Add OpenAI and Stripe keys in Settings
4. **Test Scanners**: Run a test scan to verify functionality
5. **Configure Backup**: Verify automated backups are working

### Troubleshooting

```bash
# View application logs
docker-compose -f docker-compose.prod.yml logs dataguardian-pro

# View database logs
docker-compose -f docker-compose.prod.yml logs postgres

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Rebuild application
docker-compose -f docker-compose.prod.yml build --no-cache dataguardian-pro
docker-compose -f docker-compose.prod.yml up -d
```

### Maintenance Commands

```bash
# Update application
git pull origin main
docker-compose -f docker-compose.prod.yml build dataguardian-pro
docker-compose -f docker-compose.prod.yml up -d

# Database maintenance
docker exec dataguardian-postgres vacuumdb -U dataguardian_pro -d dataguardian_pro --analyze

# View system resources
docker stats
```

---

## 🌐 Alternative Cloud Deployments

### Deploy on Replit (Recommended)
1. Use Replit's "Publish" button
2. Choose "Autoscale Deployment" for production
3. Configure environment variables in Replit Secrets
4. Deploy with custom domain support

### Deploy on Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway deploy
```

### Deploy on DigitalOcean App Platform
1. Connect GitHub repository
2. Configure build settings
3. Add environment variables
4. Deploy with automatic SSL

---

## 📞 Support

For deployment issues:
- Check logs: `/opt/dataguardian-pro/logs/`
- Review configuration: `/opt/dataguardian-pro/.env`
- Monitor resources: `htop`, `docker stats`
- Contact: support@dataguardianpro.nl

---

**Total Deployment Time:** 30-60 minutes
**Recommended for:** Production environments with custom domains
**Alternative:** Use automated `deploy.sh` script for faster deployment