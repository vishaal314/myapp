# Secure Deployment Instructions

## 🔐 Security Notice
For security reasons, server credentials should not be shared in chat. Here's how to deploy securely:

## 🚀 Quick Deployment Steps

### Step 1: Connect to Your Server
```bash
ssh root@45.81.35.202
# Enter your password when prompted
```

### Step 2: Download Deployment Script
```bash
cd /opt
curl -O https://your-replit-url/QUICK_SERVER_DEPLOY.sh
chmod +x QUICK_SERVER_DEPLOY.sh
```

### Step 3: Run Setup
```bash
./QUICK_SERVER_DEPLOY.sh
```

### Step 4: Upload Your Application
**Option A: Direct Upload**
```bash
# From your local machine
scp -r /path/to/dataguardian/* root@45.81.35.202:/opt/dataguardian/
```

**Option B: Git Clone**
```bash
# On the server
cd /opt/dataguardian
git clone https://github.com/yourusername/dataguardian-pro.git .
```

### Step 5: Deploy with Docker
```bash
cd /opt/dataguardian
docker-compose up -d
```

## ✅ Verification
- **App URL:** http://45.81.35.202
- **Check logs:** `docker-compose logs -f dataguardian`
- **Status:** `docker-compose ps`

## 🛡️ Security Best Practices
1. Change default passwords in docker-compose.yml
2. Set up firewall (ufw enable)
3. Configure SSL certificate for HTTPS
4. Use environment variables for secrets

## 🔧 Management Commands
```bash
# View logs
docker-compose logs -f dataguardian

# Restart application
docker-compose restart dataguardian

# Update application
git pull origin main
docker-compose build
docker-compose up -d

# Backup database
docker-compose exec postgres pg_dump -U dataguardian dataguardian > backup.sql
```

**Total deployment time: ~10 minutes**