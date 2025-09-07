# DataGuardian Pro CI/CD Deployment Guide

This guide covers the complete setup of automated CI/CD deployment for DataGuardian Pro to your VPS server.

## 🚀 Quick Start

### 1. Server Details
- **Server IP**: 45.81.35.202
- **Domain**: vishaalnoord7.retzor.com
- **User**: root
- **Environment**: Production

### 2. GitHub Secrets Setup

Add these secrets to your GitHub repository (`Settings > Secrets and variables > Actions`):

```bash
SERVER_PASSWORD=9q54IQq0S4l3
OPENAI_API_KEY=your-openai-api-key
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret
```

### 3. Deployment Process

The CI/CD pipeline automatically:
- ✅ Runs tests on every push
- ✅ Builds Docker images
- ✅ Deploys to production server
- ✅ Sets up SSL certificates
- ✅ Configures reverse proxy
- ✅ Health checks

## 📋 Manual Server Setup (First Time)

```bash
# SSH into your server
ssh root@45.81.35.202

# Clone the repository
git clone https://github.com/your-username/dataguardian-pro.git
cd dataguardian-pro

# Make scripts executable
chmod +x deploy.sh backup.sh restore.sh

# Run initial deployment
./deploy.sh production
```

## 🔧 Configuration Files

### Docker Compose (`docker-compose.prod.yml`)
- Multi-container setup with PostgreSQL, Redis, Nginx
- SSL certificate automation
- Health checks and restart policies

### Nginx Configuration (`nginx.conf`)
- SSL/TLS termination
- Rate limiting
- WebSocket support for Streamlit
- Security headers

### Deployment Script (`deploy.sh`)
- Automated server setup
- Docker installation
- SSL certificate generation
- Firewall configuration
- Fail2ban security

## 🔐 Security Features

### SSL/TLS
- Automatic Let's Encrypt certificates
- A+ SSL rating configuration
- HSTS headers
- Perfect Forward Secrecy

### Firewall & Security
- UFW firewall (ports 22, 80, 443)
- Fail2ban intrusion detection
- Rate limiting (10 req/s)
- Security headers (XSS, CSRF protection)

### Application Security
- Non-root container user
- Environment variable isolation
- Secrets management via GitHub Actions
- Session security

## 📊 Monitoring & Maintenance

### Health Checks
```bash
# Check application status
curl -f https://vishaalnoord7.retzor.com/health

# View logs
docker-compose -f /opt/dataguardian-pro/docker-compose.prod.yml logs -f

# Check service status
docker-compose -f /opt/dataguardian-pro/docker-compose.prod.yml ps
```

### Backup System
```bash
# Manual backup
./backup.sh

# Restore from backup
./restore.sh list              # List available backups
./restore.sh                   # Interactive restore
```

### Log Management
- Automatic log rotation (30 days retention)
- Centralized logging in `/opt/dataguardian-pro/logs/`
- Application logs, Nginx logs, system logs

## 🔄 CI/CD Workflow

### Trigger Events
- Push to `main` branch → Production deployment
- Push to `develop` branch → Testing only
- Pull requests → Testing only

### Deployment Steps
1. **Test Stage**: Run Python tests and code quality checks
2. **Build Stage**: Create Docker image and save as artifact
3. **Deploy Stage**: 
   - SSH to production server
   - Stop existing services
   - Copy new files and Docker image
   - Load image and restart services
   - Health check verification
4. **Notify Stage**: Deployment status notification

## 🛠️ Troubleshooting

### Common Issues

**Services won't start:**
```bash
docker-compose -f /opt/dataguardian-pro/docker-compose.prod.yml logs
```

**SSL certificate issues:**
```bash
docker-compose -f /opt/dataguardian-pro/docker-compose.prod.yml restart certbot
```

**Database connection errors:**
```bash
docker exec dataguardian-postgres psql -U dataguardian_pro -d dataguardian_pro -c "SELECT 1;"
```

**Application not accessible:**
```bash
# Check firewall
ufw status
# Check Nginx
docker logs dataguardian-nginx
# Check application
curl -f http://localhost:5000
```

### Performance Tuning

**Database optimization:**
```sql
-- Check connections
SELECT count(*) FROM pg_stat_activity;

-- Optimize queries
EXPLAIN ANALYZE SELECT * FROM your_table;
```

**Redis monitoring:**
```bash
docker exec dataguardian-redis redis-cli INFO memory
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Load balancer setup
- Multiple application instances
- Shared PostgreSQL database
- Redis cluster

### Vertical Scaling
- Increase VPS resources
- Optimize Docker resource limits
- Database connection pooling

## 🔄 Updates & Maintenance

### Automatic Updates
- GitHub Actions handles deployments
- Zero-downtime deployments
- Automatic rollback on failure

### Manual Updates
```bash
# Pull latest changes
cd /opt/dataguardian-pro
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build
```

### Database Migrations
```bash
# Backup before migration
./backup.sh

# Run migrations (if needed)
docker exec dataguardian-pro python manage.py migrate
```

## 📞 Support

### Monitoring Endpoints
- **Health Check**: https://vishaalnoord7.retzor.com/health
- **Application**: https://vishaalnoord7.retzor.com
- **Metrics**: Available via container logs

### Log Locations
- Application: `/opt/dataguardian-pro/logs/`
- Nginx: `/var/log/nginx/`
- System: `/var/log/syslog`

---

## ✅ Deployment Checklist

- [ ] GitHub secrets configured
- [ ] Domain DNS pointing to server IP
- [ ] Server accessible via SSH
- [ ] First deployment completed
- [ ] SSL certificates generated
- [ ] Health checks passing
- [ ] Backup system tested
- [ ] Monitoring configured

**🎉 DataGuardian Pro is now deployed and ready for the Netherlands market!**