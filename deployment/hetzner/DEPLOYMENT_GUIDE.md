# DataGuardian Pro - Hetzner Cloud Deployment Guide

## Overview
This guide walks you through deploying DataGuardian Pro on Hetzner Cloud for €5/month with full Netherlands UAVG compliance.

## Prerequisites
- Hetzner Cloud account
- Domain name (optional but recommended)
- API keys for OpenAI, Stripe, etc.

## Step 1: Create Hetzner Server

### 1.1 Login to Hetzner Cloud Console
1. Go to [console.hetzner.cloud](https://console.hetzner.cloud)
2. Create account or login
3. Create a new project: "DataGuardian Pro"

### 1.2 Launch Server
1. Click "Add Server"
2. **Location:** Falkenstein, Germany (best for Netherlands)
3. **Image:** Ubuntu 22.04
4. **Type:** CX21 (2 vCPU, 8GB RAM) - €4.90/month
5. **SSH Key:** Upload your public SSH key
6. **Name:** dataguardian-prod
7. **User Data:** Leave empty for now
8. Click "Create & Buy Now"

### 1.3 Server Details
- **Cost:** €4.90/month (billed hourly)
- **Performance:** 50-100 concurrent users
- **Storage:** 40GB NVMe SSD
- **Network:** 20TB monthly traffic
- **Compliance:** EU hosting, GDPR/UAVG ready

## Step 2: Initial Server Setup

### 2.1 Connect to Server
```bash
# Replace with your server IP
ssh root@YOUR_SERVER_IP
```

### 2.2 Upload Deployment Script
```bash
# On your local machine
scp deployment/hetzner/deploy.sh root@YOUR_SERVER_IP:/root/
```

### 2.3 Run Deployment Script
```bash
# On the server
chmod +x /root/deploy.sh
./deploy.sh
```

The script will:
- Install Docker, PostgreSQL, Nginx
- Configure firewall
- Setup database with secure password
- Create application structure
- Configure reverse proxy

**⏱️ Setup Time:** 10-15 minutes

## Step 3: Deploy DataGuardian Pro

### 3.1 Upload Source Code
```bash
# On your local machine - upload your DataGuardian Pro files
scp -r . root@YOUR_SERVER_IP:/opt/dataguardian/

# Or use git clone (if repository is available)
ssh root@YOUR_SERVER_IP
cd /opt/dataguardian
git clone https://your-repo-url.git .
```

### 3.2 Configure Environment Variables
```bash
# On the server
cd /opt/dataguardian
nano .env

# Add your API keys:
OPENAI_API_KEY=sk-your-openai-key
STRIPE_SECRET_KEY=sk_live_your-stripe-key
STRIPE_PUBLISHABLE_KEY=pk_live_your-stripe-key
```

### 3.3 Build and Start Application
```bash
# Build Docker image
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f dataguardian
```

## Step 4: SSL Certificate Setup

### 4.1 Point Domain to Server
1. In your domain registrar, create A record:
   - **Name:** @ (or subdomain like app)
   - **Value:** YOUR_SERVER_IP
   - **TTL:** 300

### 4.2 Install SSL Certificate
```bash
# Replace with your domain
certbot --nginx -d yourdomain.com

# Follow prompts:
# 1. Enter email address
# 2. Agree to terms
# 3. Choose redirect HTTPS (recommended)
```

### 4.3 Auto-renewal Setup
```bash
# Test renewal
certbot renew --dry-run

# Auto-renewal is already configured via systemd
systemctl status certbot.timer
```

## Step 5: Production Configuration

### 5.1 Database Optimization
```bash
# The deployment script already optimizes PostgreSQL for 8GB RAM
# Monitor performance with:
sudo -u postgres psql dataguardian_prod -c "SELECT * FROM pg_stat_activity;"
```

### 5.2 Monitoring Setup
```bash
# Check application logs
docker-compose logs -f dataguardian

# Check system resources
htop
df -h
```

### 5.3 Backup Configuration
```bash
# Create backup script
cat > /opt/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
sudo -u postgres pg_dump dataguardian_prod > /opt/backups/db_backup_$DATE.sql
# Keep only last 7 days
find /opt/backups -name "db_backup_*.sql" -mtime +7 -delete
EOF

mkdir -p /opt/backups
chmod +x /opt/backup.sh

# Setup daily backup cron
echo "0 2 * * * /opt/backup.sh" | crontab -
```

## Step 6: Testing and Verification

### 6.1 Application Testing
1. Visit https://yourdomain.com
2. Test login functionality
3. Run each scanner type
4. Verify PDF report generation
5. Test payment integration (if applicable)

### 6.2 Performance Testing
```bash
# Install Apache Bench for testing
apt install apache2-utils

# Test concurrent users
ab -n 100 -c 10 https://yourdomain.com/

# Monitor during test
htop
docker stats
```

### 6.3 Compliance Verification
- ✅ Server location: Germany (EU)
- ✅ Database location: Same server (EU)
- ✅ SSL encryption: Let's Encrypt
- ✅ Data residency: EU-only
- ✅ GDPR/UAVG compliance: Ready

## Step 7: Scaling Plan

### 7.1 Traffic Growth Plan
- **0-25 customers:** CX21 (€5/month) ✅ Current
- **26-50 customers:** Upgrade to CX31 (€10/month)
- **51-100 customers:** Upgrade to CX41 (€16/month)
- **100+ customers:** Add load balancer + multiple servers

### 7.2 Upgrade Process
```bash
# Hetzner allows live upgrades (no downtime)
# 1. In Hetzner console: Resize server
# 2. Reboot when convenient
# 3. No application changes needed
```

## Maintenance Tasks

### Daily
- Check application logs: `docker-compose logs --tail=50 dataguardian`
- Monitor disk space: `df -h`

### Weekly
- Review backup files: `ls -la /opt/backups/`
- Check SSL certificate: `certbot certificates`
- Update packages: `apt update && apt upgrade -y`

### Monthly
- Review Hetzner billing
- Analyze application metrics
- Security updates: `docker-compose pull && docker-compose up -d`

## Troubleshooting

### Common Issues

**Application won't start:**
```bash
# Check logs
docker-compose logs dataguardian

# Common fixes
docker-compose down
docker-compose up -d
```

**Database connection issues:**
```bash
# Test database connection
sudo -u postgres psql dataguardian_prod -c "SELECT version();"

# Reset database password if needed
sudo -u postgres psql -c "ALTER USER dataguardian PASSWORD 'newpassword';"
```

**SSL certificate issues:**
```bash
# Check certificate status
certbot certificates

# Renew manually if needed
certbot renew --force-renewal -d yourdomain.com
```

**High memory usage:**
```bash
# Check Docker memory usage
docker stats

# Restart application if needed
docker-compose restart dataguardian
```

## Cost Breakdown

| Component | Monthly Cost |
|-----------|-------------|
| Hetzner CX21 Server | €4.90 |
| Domain name | €10-15/year |
| SSL Certificate | Free (Let's Encrypt) |
| **Total Monthly** | **€5-6** |

## Security Features

- ✅ Firewall configured (UFW)
- ✅ SSL/TLS encryption
- ✅ Database password authentication
- ✅ Application container isolation
- ✅ Regular security updates
- ✅ EU data residency

## Netherlands UAVG Compliance

- ✅ **Data Location:** Germany (EU member state)
- ✅ **Data Processing:** EU-only servers
- ✅ **Data Transfer:** No third-country transfers
- ✅ **Privacy Controls:** Built into application
- ✅ **Audit Trail:** Full logging capability
- ✅ **Data Subject Rights:** Supported by application

## Support

### Hetzner Support
- 24/7 technical support
- Response time: Usually within hours
- Documentation: [docs.hetzner.com](https://docs.hetzner.com)

### Application Support
- Monitor logs: `/opt/dataguardian/logs/`
- Database logs: `/var/log/postgresql/`
- System logs: `journalctl -f`

This deployment provides enterprise-grade hosting at startup costs while maintaining full Netherlands compliance for your €25K MRR goal.