# Contabo VPS Setup Guide - €4.99/month

## Why Contabo for DataGuardian Pro?

- **Cheapest EU Option:** €4.99/month total cost
- **Excellent Value:** 4 vCPU, 8GB RAM, 200GB SSD
- **EU Compliance:** German datacenter for GDPR
- **Self-Managed:** Full control over your infrastructure
- **Scalable:** Easy upgrades available

## Step-by-Step Setup (30 minutes)

### 1. Create Contabo Account (5 minutes)

1. Go to [contabo.com](https://contabo.com)
2. Click "VPS" → "VPS S SSD"
3. **Configuration:**
   - **Plan:** VPS S (4 vCPU, 8GB RAM, 200GB SSD) - €4.99/month
   - **Region:** Germany (Nuremberg) for EU compliance
   - **OS:** Ubuntu 22.04 LTS
   - **Contract:** 12 months (cheaper than monthly)
4. **Add-ons:**
   - Skip backup service (we'll handle this ourselves)
   - Skip management service
5. **Complete order and payment**
6. **Wait for setup email** (usually 15-30 minutes)

### 2. Initial Server Setup (10 minutes)

Connect via SSH:
```bash
ssh root@YOUR_SERVER_IP
```

Update system:
```bash
apt update && apt upgrade -y
```

Install essential packages:
```bash
apt install -y curl wget git nano htop unzip
```

Create non-root user:
```bash
adduser dataguardian
usermod -aG sudo dataguardian
```

Setup SSH key authentication:
```bash
mkdir -p /home/dataguardian/.ssh
cp ~/.ssh/authorized_keys /home/dataguardian/.ssh/
chown -R dataguardian:dataguardian /home/dataguardian/.ssh
chmod 700 /home/dataguardian/.ssh
chmod 600 /home/dataguardian/.ssh/authorized_keys
```

### 3. Install Docker and Docker Compose (5 minutes)

Install Docker:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl enable docker
systemctl start docker
```

Add user to docker group:
```bash
usermod -aG docker dataguardian
```

Install Docker Compose:
```bash
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

Test installation:
```bash
docker --version
docker-compose --version
```

### 4. Setup Firewall (2 minutes)

Configure UFW firewall:
```bash
ufw enable
ufw allow ssh
ufw allow 80
ufw allow 443
ufw allow 8501
ufw status
```

### 5. Deploy DataGuardian Pro (8 minutes)

Switch to dataguardian user:
```bash
su - dataguardian
```

Clone repository:
```bash
git clone https://github.com/yourusername/dataguardian-pro.git
cd dataguardian-pro
```

Create environment file:
```bash
nano .env
```

Add configuration:
```bash
# Database (using local PostgreSQL container)
DATABASE_URL=postgresql://postgres:dataguardian_secure_2024@db:5432/dataguardian

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_live_your_publishable_key
STRIPE_SECRET_KEY=sk_live_your_secret_key

# Security Keys (generate 32-character random strings)
JWT_SECRET=your_32_character_jwt_secret_here
ENCRYPTION_KEY=your_32_character_encryption_key

# Application Settings
ENVIRONMENT=production
STREAMLIT_SERVER_HEADLESS=true
PYTHONPATH=/app

# Optional: External database (if using managed service later)
# DATABASE_URL=postgresql://user:pass@external-host:5432/dbname
```

Start the application:
```bash
docker-compose up -d
```

Check if services are running:
```bash
docker-compose ps
docker-compose logs app
```

Test the application:
```bash
curl http://localhost:8501
```

## 6. Setup Nginx Reverse Proxy (Optional - 5 minutes)

Install Nginx:
```bash
sudo apt install nginx -y
```

Create Nginx configuration:
```bash
sudo nano /etc/nginx/sites-available/dataguardian
```

Add configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_buffering off;
        proxy_read_timeout 86400;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/dataguardian /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 7. Setup SSL Certificate (Optional - 3 minutes)

Install Certbot:
```bash
sudo apt install certbot python3-certbot-nginx -y
```

Get SSL certificate:
```bash
sudo certbot --nginx -d your-domain.com
```

Auto-renewal:
```bash
sudo crontab -e
# Add line:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

## 8. Setup Monitoring and Backup (5 minutes)

Create backup script:
```bash
nano ~/backup.sh
```

Add backup script:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/dataguardian/backups"
mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec -T db pg_dump -U postgres dataguardian > $BACKUP_DIR/db_backup_$DATE.sql

# Backup application data
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz /home/dataguardian/dataguardian-pro

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

Make executable and schedule:
```bash
chmod +x ~/backup.sh

# Add to crontab
crontab -e
# Add line for daily backup at 2 AM:
# 0 2 * * * /home/dataguardian/backup.sh >> /home/dataguardian/backup.log 2>&1
```

Create monitoring script:
```bash
nano ~/monitor.sh
```

Add monitoring:
```bash
#!/bin/bash
# Check if DataGuardian Pro is running
if ! curl -s http://localhost:8501 > /dev/null; then
    echo "DataGuardian Pro is down, restarting..."
    cd /home/dataguardian/dataguardian-pro
    docker-compose restart app
    
    # Send email notification (optional)
    # echo "DataGuardian Pro restarted at $(date)" | mail -s "DataGuardian Alert" your-email@domain.com
fi
```

Make executable and schedule:
```bash
chmod +x ~/monitor.sh

# Add to crontab for every 5 minutes
crontab -e
# Add line:
# */5 * * * * /home/dataguardian/monitor.sh
```

## ✅ You're Live!

Your DataGuardian Pro is now running at:
- **Direct IP:** http://YOUR_SERVER_IP:8501
- **With Domain:** https://your-domain.com (if configured)

## 📊 Server Specifications

**Contabo VPS S:**
- **CPU:** 4 vCores
- **RAM:** 8GB
- **Storage:** 200GB SSD
- **Bandwidth:** Unlimited
- **Location:** Germany (EU)
- **Cost:** €4.99/month

## 🔧 Management Commands

Check application status:
```bash
cd /home/dataguardian/dataguardian-pro
docker-compose ps
docker-compose logs app
```

Update application:
```bash
git pull
docker-compose build --no-cache
docker-compose up -d
```

View system resources:
```bash
htop
df -h
docker stats
```

Check database:
```bash
docker-compose exec db psql -U postgres -d dataguardian
```

Restart services:
```bash
docker-compose restart
sudo systemctl restart nginx
```

## 📈 Performance Optimization

**For high traffic, consider:**

1. **Enable Redis caching:**
```bash
# Redis is already included in docker-compose.yml
# Just uncomment the REDIS_URL in .env
echo "REDIS_URL=redis://redis:6379" >> .env
docker-compose up -d
```

2. **Optimize PostgreSQL:**
```bash
# Edit PostgreSQL config
docker-compose exec db nano /var/lib/postgresql/data/postgresql.conf
# Add these optimizations:
# shared_buffers = 256MB
# effective_cache_size = 2GB
# max_connections = 100
```

3. **Setup log rotation:**
```bash
sudo nano /etc/logrotate.d/dataguardian
```

Add:
```
/home/dataguardian/dataguardian-pro/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    copytruncate
}
```

## 🛡️ Security Hardening

Change SSH port:
```bash
sudo nano /etc/ssh/sshd_config
# Change Port 22 to Port 2222
sudo systemctl restart ssh
sudo ufw allow 2222
sudo ufw delete allow ssh
```

Disable root login:
```bash
sudo nano /etc/ssh/sshd_config
# Set PermitRootLogin no
sudo systemctl restart ssh
```

Install fail2ban:
```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
```

## 🆘 Troubleshooting

**Application won't start:**
```bash
docker-compose logs app
docker-compose down && docker-compose up -d
```

**Database issues:**
```bash
docker-compose logs db
docker-compose exec db psql -U postgres -l
```

**Nginx issues:**
```bash
sudo nginx -t
sudo systemctl status nginx
sudo tail -f /var/log/nginx/error.log
```

**Disk space full:**
```bash
df -h
docker system prune -a
sudo apt autoremove
```

**Memory issues:**
```bash
free -h
docker stats
# Consider upgrading to VPS M (€8.99/month, 16GB RAM)
```

## 💰 Cost Breakdown

**Monthly Costs:**
- **VPS S:** €4.99/month
- **Domain:** €10-15/year (~€1/month)
- **Total:** ~€6/month

**Annual Costs:**
- **VPS S:** €59.88/year (with 12-month contract)
- **Domain:** €10-15/year
- **Total:** ~€70-75/year

## 🔄 Upgrade Path

When you need more resources:
- **VPS M:** €8.99/month (6 vCPU, 16GB RAM)
- **VPS L:** €14.99/month (8 vCPU, 30GB RAM)
- **VPS XL:** €26.99/month (10 vCPU, 60GB RAM)

## 📞 Contabo Support

- **Support Portal:** [my.contabo.com](https://my.contabo.com)
- **Documentation:** [docs.contabo.com](https://docs.contabo.com)
- **Community:** [forum.contabo.com](https://forum.contabo.com)

**Your €4.99/month EU-compliant DataGuardian Pro SaaS is ready!**

This setup gives you:
- Full control over your infrastructure
- Maximum cost efficiency
- EU data residency for GDPR compliance
- Professional-grade deployment
- Easy scaling options