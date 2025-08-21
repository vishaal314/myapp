# Hetzner Cloud Setup Guide - €13.29/month

## Why Hetzner for DataGuardian Pro?

- **EU Compliance:** German servers perfect for Netherlands GDPR
- **Cheap:** €13.29/month total (€3.29 server + €10 database)
- **Fast:** Excellent European performance
- **Reliable:** 99.9% uptime guarantee
- **Scalable:** Easy upgrades as you grow

## Step-by-Step Setup (15 minutes)

### 1. Create Hetzner Account (2 minutes)
1. Go to [console.hetzner.cloud](https://console.hetzner.cloud)
2. Click "Sign Up"
3. Verify email and add payment method
4. Create new project: "DataGuardian Pro"

### 2. Create Server (3 minutes)
1. **Click "Add Server"**
2. **Location:** Nuremberg (Germany) or Helsinki (Finland)
3. **Image:** Ubuntu 22.04
4. **Type:** CX11 (1 vCPU, 2GB RAM) - €3.29/month
5. **SSH Key:** Add your public key or use password
6. **Name:** dataguardian-server
7. **Click "Create & Buy now"**

### 3. Setup Database (2 minutes)
1. **Go to "Databases" tab**
2. **Click "Create Database"**
3. **Type:** PostgreSQL 15
4. **Size:** DB-cx11 (€10/month)
5. **Location:** Same as server
6. **Name:** dataguardian-db
7. **Note the connection string**

### 4. Connect and Deploy (8 minutes)

SSH into your server:
```bash
ssh root@YOUR_SERVER_IP
```

Install Docker:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl enable docker
systemctl start docker
```

Install Docker Compose:
```bash
apt update
apt install docker-compose -y
```

Clone and setup DataGuardian Pro:
```bash
git clone https://github.com/yourusername/dataguardian-pro.git
cd dataguardian-pro

# Create environment file
nano .env
```

Add to `.env`:
```bash
# Database (from Hetzner Database connection string)
DATABASE_URL=postgresql://username:password@host:port/database

# Stripe
STRIPE_PUBLISHABLE_KEY=pk_live_your_key
STRIPE_SECRET_KEY=sk_live_your_key

# Security (generate 32-character strings)
JWT_SECRET=your_32_character_secret
ENCRYPTION_KEY=your_32_character_encryption_key

# Settings
ENVIRONMENT=production
STREAMLIT_SERVER_HEADLESS=true
```

Start the application:
```bash
docker-compose up -d
```

Check if running:
```bash
docker-compose ps
curl http://localhost:8501
```

### 5. Setup Domain and SSL (Optional)

Install Nginx and Certbot:
```bash
apt install nginx certbot python3-certbot-nginx -y
```

Create Nginx config:
```bash
nano /etc/nginx/sites-available/dataguardian
```

Add configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

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
    }
}
```

Enable site:
```bash
ln -s /etc/nginx/sites-available/dataguardian /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

Get SSL certificate:
```bash
certbot --nginx -d yourdomain.com
```

## ✅ You're Live!

Your DataGuardian Pro is now running at:
- **IP:** http://YOUR_SERVER_IP:8501
- **Domain:** https://yourdomain.com (if configured)

## 💰 Monthly Costs
- **Server CX11:** €3.29/month
- **PostgreSQL:** €10/month
- **Total:** €13.29/month (~$14.50/month)

## 🔧 Management Commands

Check application status:
```bash
docker-compose ps
docker-compose logs app
```

Update application:
```bash
git pull
docker-compose build
docker-compose up -d
```

Backup database:
```bash
docker-compose exec db pg_dump -U postgres dataguardian > backup.sql
```

Monitor resources:
```bash
htop
df -h
```

## 📊 Performance Optimization

For high traffic, upgrade to:
- **CX21:** €5.83/month (2 vCPU, 4GB RAM)
- **CX31:** €10.67/month (2 vCPU, 8GB RAM)

## 🆘 Troubleshooting

**App won't start:**
```bash
docker-compose logs app
```

**Database connection issues:**
```bash
docker-compose logs db
```

**Check firewall:**
```bash
ufw status
ufw allow 80
ufw allow 443
```

**Your €13.29/month EU-compliant DataGuardian Pro SaaS is ready!**