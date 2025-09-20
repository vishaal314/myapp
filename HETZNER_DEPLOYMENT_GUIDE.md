# DataGuardian Pro - Hetzner Manual Deployment Guide

## 🚀 Complete Step-by-Step Deployment Script

This guide will help you deploy DataGuardian Pro on your Hetzner server using the automated deployment script.

## 📋 Prerequisites

Before running the deployment script, ensure you have:

- ✅ **Hetzner Cloud server** with Ubuntu 22.04 LTS
- ✅ **Root access** to the server
- ✅ **Domain name** pointing to your server IP
- ✅ **DataGuardian Pro source code** ready for upload
- ✅ **API keys** (OpenAI, Stripe, etc.)

## 🛠️ Server Requirements

**Recommended Hetzner Instance:**
- **CAX11**: 2 vCPUs, 4GB RAM, 40GB SSD
- **Cost**: €4.15/month
- **Location**: Falkenstein or Nuremberg (Germany/EU)

## 📝 Pre-Deployment Setup

### 1. Update Configuration

Edit the deployment script before running:

```bash
nano manual_hetzner_deploy.sh
```

**Update these variables:**
```bash
DOMAIN="your-actual-domain.com"     # Your domain name
EMAIL="admin@your-domain.com"       # Your email for SSL certificates
```

### 2. Upload Script to Server

Upload the deployment script to your Hetzner server:

```bash
scp manual_hetzner_deploy.sh root@YOUR_SERVER_IP:/root/
```

## 🚀 Deployment Process

### 1. Connect to Your Server

```bash
ssh root@YOUR_SERVER_IP
```

### 2. Make Script Executable

```bash
chmod +x manual_hetzner_deploy.sh
```

### 3. Run Deployment Script

```bash
./manual_hetzner_deploy.sh
```

The script will guide you through **14 steps**:

1. **System Updates** - Updates Ubuntu and installs dependencies
2. **Docker Installation** - Installs Docker and Docker Compose
3. **Firewall Configuration** - Sets up UFW security rules
4. **Application Directory** - Creates `/opt/dataguardian` structure
5. **Environment Configuration** - Generates secure `.env` file
6. **Docker Compose** - Creates production-ready container setup
7. **Nginx Configuration** - Reverse proxy with security headers
8. **Management Scripts** - Backup and monitoring tools
9. **Systemd Service** - Auto-start configuration
10. **Application Upload** - Upload your DataGuardian Pro source code
11. **Build & Start** - Builds containers and starts services
12. **SSL Certificates** - Let's Encrypt HTTPS setup
13. **Security Setup** - Fail2Ban, log rotation, automated backups
14. **Final Verification** - Tests all services

## 📁 Source Code Upload

During **Step 10**, you'll need to upload your DataGuardian Pro source code:

### Option 1: SCP Upload
```bash
# From your local machine
scp -r /path/to/dataguardian-pro/* root@YOUR_SERVER_IP:/opt/dataguardian/
```

### Option 2: Git Clone
```bash
# On the server
cd /opt/dataguardian
git clone https://github.com/your-repo/dataguardian-pro.git .
```

### Required Files:
- `app.py` - Main Streamlit application
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration
- All other source code files

## 🔧 Post-Deployment Configuration

After deployment completes:

### 1. Update API Keys

Edit the environment file:
```bash
nano /opt/dataguardian/.env
```

Update these keys:
```bash
OPENAI_API_KEY=your_actual_openai_key
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key
```

### 2. Restart Services

```bash
systemctl restart dataguardian
```

### 3. Verify Deployment

```bash
cd /opt/dataguardian
./status.sh
```

## 🌐 Access Your Application

- **HTTPS**: https://your-domain.com
- **Direct Access** (testing): http://YOUR_SERVER_IP:5000

## 📊 Management Commands

### Service Management
```bash
# Start/Stop services
systemctl start dataguardian
systemctl stop dataguardian
systemctl restart dataguardian

# Check service status
systemctl status dataguardian
```

### Docker Management
```bash
cd /opt/dataguardian

# View running containers
docker-compose ps

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart dataguardian
docker-compose restart nginx

# Update application
docker-compose build
docker-compose up -d
```

### Monitoring & Maintenance
```bash
cd /opt/dataguardian

# Check system status
./status.sh

# Run backup
./backup.sh

# View recent logs
docker-compose logs --tail=50 dataguardian
```

## 🔐 Security Features

The deployment includes:

- ✅ **SSL/TLS** encryption with Let's Encrypt
- ✅ **UFW Firewall** with restricted ports
- ✅ **Fail2Ban** intrusion detection
- ✅ **Rate limiting** on Nginx
- ✅ **Security headers** (HSTS, XSS protection)
- ✅ **Automated backups** (daily at 2 AM)
- ✅ **Log rotation** (30-day retention)
- ✅ **Container isolation**

## 📈 Monitoring & Alerts

### Health Checks
```bash
# Application health
curl https://your-domain.com/health

# SSL certificate expiry
openssl s_client -connect your-domain.com:443 -servername your-domain.com </dev/null 2>/dev/null | openssl x509 -noout -dates
```

### Log Monitoring
```bash
# Application logs
tail -f /opt/dataguardian/logs/access.log

# Nginx logs  
tail -f /opt/dataguardian/nginx-logs/access.log

# System logs
journalctl -u dataguardian -f
```

## 💾 Backup & Recovery

### Automated Backups
- **Daily backups** at 2 AM (configured via cron)
- **30-day retention** for all backup files
- **Location**: `/opt/dataguardian/backups/`

### Manual Backup
```bash
cd /opt/dataguardian
./backup.sh
```

### Backup Contents
- PostgreSQL database dump
- Redis data snapshot
- Application data (reports, logs, config)
- SSL certificates

## 🚨 Troubleshooting

### Common Issues

**Application not starting:**
```bash
docker-compose logs dataguardian
# Check for missing environment variables or API keys
```

**SSL certificate issues:**
```bash
docker-compose logs certbot
# Ensure domain points to server IP
# Check firewall allows ports 80/443
```

**Database connection errors:**
```bash
docker-compose logs postgres
# Check database credentials in .env file
```

**High resource usage:**
```bash
docker stats
# Monitor container resource consumption
```

### Emergency Recovery
```bash
# Stop all services
systemctl stop dataguardian

# Remove all containers (data preserved in volumes)
docker-compose down

# Rebuild and restart
docker-compose build
systemctl start dataguardian
```

## 💰 Cost Optimization

### Hetzner Pricing (Monthly)
- **CAX11** (2 vCPUs, 4GB): €4.15
- **Backup Storage**: €0.60 (optional)
- **Domain**: ~€10/year
- **Total**: ~€5/month

### Cost Savings Tips
- Use Hetzner's snapshot feature for backups
- Monitor resource usage with `docker stats`
- Scale down during low-traffic periods
- Use CDN for static assets if needed

## 📞 Support

### Log Files Location
```bash
/opt/dataguardian/logs/           # Application logs
/opt/dataguardian/nginx-logs/     # Web server logs
/opt/dataguardian/backups/        # Backup files
/var/log/fail2ban.log            # Security logs
```

### Key Configuration Files
```bash
/opt/dataguardian/.env            # Environment variables
/opt/dataguardian/docker-compose.yml  # Container setup
/opt/dataguardian/nginx.conf      # Web server config
/etc/systemd/system/dataguardian.service  # Service definition
```

---

## 🎉 Deployment Complete!

Your DataGuardian Pro is now running securely on Hetzner with:

- 🔒 **End-to-end encryption**
- 🇳🇱 **Netherlands/EU data residency**
- 📊 **Enterprise-grade monitoring**
- 🚀 **Production-ready performance**
- 💰 **Cost-effective hosting** (~€5/month)

Visit **https://your-domain.com** to access your DataGuardian Pro installation!