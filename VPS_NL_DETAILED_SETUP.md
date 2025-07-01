# Complete VPS.nl Deployment Guide for DataGuardian Pro
## Step-by-Step Netherlands Hosting Setup

VPS.nl is a 100% Dutch company providing Netherlands-only hosting, perfect for GDPR compliance and data sovereignty.

## 📋 Prerequisites
- Valid email address
- Payment method (credit card or iDEAL)
- GitHub repository with your DataGuardian Pro code
- 2-3 hours for complete setup

## 🔰 Phase 1: VPS.nl Account and Server Setup

### Step 1: Create VPS.nl Account

1. **Visit VPS.nl**
   - Go to [vps.nl](https://vps.nl)
   - Click "Bestellen" (Order) in top menu

2. **Choose VPS Plan**
   - Select "Linux VPS"
   - Choose "VPS Basic" (€2.99/month) or "VPS Standard" (€5.99/month)
   - Recommended: VPS Standard for better performance

**VPS Plans Comparison:**
```
VPS Basic (€2.99/month):
- 1 vCPU
- 1GB RAM
- 25GB SSD
- 1TB traffic

VPS Standard (€5.99/month):
- 2 vCPU
- 2GB RAM
- 50GB SSD
- 2TB traffic
- Recommended for production
```

3. **Configuration Options**
   - Operating System: Ubuntu 22.04 LTS
   - Datacenter: Keep default (Netherlands)
   - Backup: Add "Backup Service" (+€1/month) - recommended
   - Monitoring: Add "Monitoring" (+€1/month) - optional

4. **Account Registration**
   - Fill in personal/business details
   - Use Netherlands address if possible (for compliance)
   - Choose payment method (iDEAL for Dutch payments)

5. **Complete Order**
   - Review configuration
   - Accept terms and conditions
   - Complete payment
   - Wait for email confirmation (usually 15-30 minutes)

### Step 2: Access Your VPS

1. **Receive Access Details**
   - Check email for VPS credentials
   - Note: IP address, root password, SSH port (usually 22)

2. **Initial SSH Connection**
   ```bash
   # Replace with your actual IP address
   ssh root@YOUR_VPS_IP_ADDRESS
   
   # Enter the password from email
   # Accept fingerprint when prompted
   ```

3. **Change Root Password (Security)**
   ```bash
   # Change to secure password
   passwd
   
   # Enter new strong password twice
   # Use combination of letters, numbers, symbols
   ```

4. **Update System**
   ```bash
   # Update package lists
   apt update
   
   # Upgrade installed packages
   apt upgrade -y
   
   # Install essential tools
   apt install -y curl wget unzip git htop nano
   ```

## 🐳 Phase 2: Docker Installation and Setup

### Step 3: Install Docker

```bash
# Remove any old Docker installations
apt remove -y docker docker-engine docker.io containerd runc

# Install dependencies
apt install -y apt-transport-https ca-certificates gnupg lsb-release

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package list
apt update

# Install Docker
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start and enable Docker
systemctl start docker
systemctl enable docker

# Verify installation
docker --version
docker compose version
```

### Step 4: Configure Docker for Production

```bash
# Create Docker daemon configuration
cat > /etc/docker/daemon.json << EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2"
}
EOF

# Restart Docker to apply configuration
systemctl restart docker
```

## 📁 Phase 3: Application Deployment

### Step 5: Prepare Application Code

```bash
# Create application directory
mkdir -p /opt/dataguardian
cd /opt/dataguardian

# Clone your repository (replace with your GitHub URL)
git clone https://github.com/YOUR_USERNAME/dataguardian-pro.git .

# Verify files are present
ls -la
```

### Step 6: Database Setup

**Option A: PostgreSQL in Docker (Recommended)**
```bash
# Create PostgreSQL data directory
mkdir -p /opt/dataguardian/postgres_data

# Create docker-compose.yml for database
cat > docker-compose.db.yml << EOF
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: dataguardian-db
    environment:
      POSTGRES_PASSWORD: $(openssl rand -base64 32)
      POSTGRES_USER: dataguardian
      POSTGRES_DB: dataguardian_db
    volumes:
      - ./postgres_data:/var/lib/postgresql/data
      - ./database/postgres-init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped
    networks:
      - dataguardian_network

networks:
  dataguardian_network:
    driver: bridge
EOF

# Start database
docker compose -f docker-compose.db.yml up -d

# Check database status
docker compose -f docker-compose.db.yml logs postgres
```

**Option B: SQLite (Budget Option)**
```bash
# Create data directory for SQLite
mkdir -p /opt/dataguardian/data

# SQLite requires no separate container
echo "Using SQLite - no additional database setup needed"
```

### Step 7: Configure Environment Variables

```bash
# Create environment file
cat > .env << EOF
# Database Configuration (choose one)
# For PostgreSQL:
DATABASE_URL=postgresql://dataguardian:YOUR_POSTGRES_PASSWORD@localhost:5432/dataguardian_db
PGHOST=localhost
PGUSER=dataguardian
PGPASSWORD=YOUR_POSTGRES_PASSWORD
PGDATABASE=dataguardian_db
PGPORT=5432

# For SQLite (alternative):
# DATABASE_URL=sqlite:///app/data/dataguardian.db

# Application Configuration
PORT=5000
PYTHONUNBUFFERED=1
DATA_RESIDENCY=Netherlands
HOSTING_PROVIDER=VPS.nl
GDPR_COMPLIANT=true

# Optional API Keys (add if you have them)
# OPENAI_API_KEY=your_openai_key_here
# STRIPE_SECRET_KEY=sk_test_your_stripe_key
# STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key
# ANTHROPIC_API_KEY=your_anthropic_key_here
EOF

# Secure the environment file
chmod 600 .env
```

### Step 8: Application Deployment

```bash
# Build the application
docker build -t dataguardian-pro .

# For PostgreSQL setup:
cat > docker-compose.yml << EOF
version: '3.8'

services:
  app:
    build: .
    container_name: dataguardian-app
    ports:
      - "5000:5000"
    env_file:
      - .env
    volumes:
      - ./reports:/app/reports
      - ./uploads:/app/uploads
      - ./data:/app/data
    restart: unless-stopped
    networks:
      - dataguardian_network
    depends_on:
      - postgres

  postgres:
    image: postgres:15-alpine
    container_name: dataguardian-db
    environment:
      POSTGRES_PASSWORD: YOUR_POSTGRES_PASSWORD
      POSTGRES_USER: dataguardian
      POSTGRES_DB: dataguardian_db
    volumes:
      - ./postgres_data:/var/lib/postgresql/data
      - ./database/postgres-init.sql:/docker-entrypoint-initdb.d/init.sql
    expose:
      - "5432"
    restart: unless-stopped
    networks:
      - dataguardian_network

networks:
  dataguardian_network:
    driver: bridge

volumes:
  postgres_data:
EOF

# Deploy the application
docker compose up -d

# Check deployment status
docker compose ps
docker compose logs app
```

## 🌐 Phase 4: Web Server and SSL Setup

### Step 9: Install and Configure Nginx

```bash
# Install Nginx
apt install -y nginx

# Create Nginx configuration for DataGuardian Pro
cat > /etc/nginx/sites-available/dataguardian << EOF
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    location / {
        proxy_pass http://localhost:5000;
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
EOF

# Enable the site
ln -s /etc/nginx/sites-available/dataguardian /etc/nginx/sites-enabled/

# Remove default site
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Start Nginx
systemctl enable nginx
systemctl start nginx
```

### Step 10: SSL Certificate with Let's Encrypt

```bash
# Install Certbot
apt install -y certbot python3-certbot-nginx

# If you have a domain name:
certbot --nginx -d yourdomain.com

# If using IP only (self-signed certificate):
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/dataguardian.key \
    -out /etc/ssl/certs/dataguardian.crt \
    -subj "/C=NL/ST=Netherlands/L=Amsterdam/O=DataGuardian/OU=IT/CN=dataguardian"

# Update Nginx for SSL
cat > /etc/nginx/sites-available/dataguardian << EOF
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name YOUR_DOMAIN_OR_IP;

    ssl_certificate /etc/ssl/certs/dataguardian.crt;
    ssl_certificate_key /etc/ssl/private/dataguardian.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# Reload Nginx
systemctl reload nginx
```

## 🔒 Phase 5: Security and Monitoring

### Step 11: Firewall Configuration

```bash
# Install UFW firewall
apt install -y ufw

# Set default policies
ufw default deny incoming
ufw default allow outgoing

# Allow SSH
ufw allow ssh

# Allow HTTP and HTTPS
ufw allow 80
ufw allow 443

# Enable firewall
ufw --force enable

# Check status
ufw status
```

### Step 12: Monitoring Setup

```bash
# Create monitoring script
cat > /opt/dataguardian/monitor.sh << 'EOF'
#!/bin/bash
# DataGuardian Pro monitoring script

echo "=== DataGuardian Pro Status Check ==="
echo "Date: $(date)"
echo ""

# Check Docker containers
echo "Docker containers:"
docker compose ps

echo ""
echo "Application logs (last 10 lines):"
docker compose logs --tail=10 app

echo ""
echo "Database status:"
docker compose logs --tail=5 postgres

echo ""
echo "Nginx status:"
systemctl status nginx --no-pager -l

echo ""
echo "Disk usage:"
df -h

echo ""
echo "Memory usage:"
free -h

echo ""
echo "=== End Status Check ==="
EOF

# Make executable
chmod +x /opt/dataguardian/monitor.sh

# Test monitoring
/opt/dataguardian/monitor.sh
```

### Step 13: Backup Configuration

```bash
# Create backup script
cat > /opt/dataguardian/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/dataguardian/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
docker compose exec -T postgres pg_dump -U dataguardian dataguardian_db > $BACKUP_DIR/db_backup_$DATE.sql

# Backup application data
tar -czf $BACKUP_DIR/app_data_$DATE.tar.gz /opt/dataguardian/data /opt/dataguardian/reports

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

# Make executable
chmod +x /opt/dataguardian/backup.sh

# Add to crontab for daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/dataguardian/backup.sh") | crontab -
```

## ✅ Phase 6: Testing and Verification

### Step 14: Verify Deployment

```bash
# Check all services
docker compose ps

# Test application access
curl -I http://localhost:5000

# Check logs for errors
docker compose logs app | grep -i error

# Test database connection
docker compose exec postgres psql -U dataguardian -d dataguardian_db -c "\dt"

# Test external access (replace with your IP)
curl -I http://YOUR_VPS_IP
```

### Step 15: Access Your Application

1. **Open browser and navigate to:**
   - HTTP: `http://YOUR_VPS_IP`
   - HTTPS: `https://YOUR_VPS_IP` (if SSL configured)

2. **Test login with default accounts:**
   - Username: `admin`, Password: `password`
   - Username: `analyst`, Password: `password`

3. **Verify DPIA functionality:**
   - Click "Simple DPIA"
   - Fill out a test assessment
   - Generate and download report

## 🔧 Maintenance Commands

```bash
# View application logs
docker compose logs -f app

# Restart application
docker compose restart app

# Update application
cd /opt/dataguardian
git pull
docker compose build app
docker compose up -d

# Manual backup
/opt/dataguardian/backup.sh

# System monitoring
/opt/dataguardian/monitor.sh
```

## 📊 Cost Summary

**Monthly Costs:**
- VPS Standard: €5.99
- Backup Service: €1.00
- Domain (optional): €1.00/month
- **Total: €7.99/month**

**Annual Cost: €95.88**

## 🎯 Success Checklist

- ✅ VPS.nl account created and VPS provisioned
- ✅ Docker and Docker Compose installed
- ✅ PostgreSQL database running
- ✅ DataGuardian Pro application deployed
- ✅ Nginx reverse proxy configured
- ✅ SSL certificate installed
- ✅ Firewall configured
- ✅ Monitoring and backup scripts setup
- ✅ Application accessible via web browser
- ✅ DPIA functionality tested

Your DataGuardian Pro application is now running on 100% Netherlands infrastructure with full GDPR compliance!