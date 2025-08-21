# DataGuardian Pro - Railway Deployment Guide

## Overview
Railway is an excellent platform for deploying DataGuardian Pro with automatic scaling, built-in PostgreSQL, and simple configuration. This guide provides step-by-step instructions for production deployment.

## Prerequisites
- Railway account (free tier available)
- GitHub repository with DataGuardian Pro code
- Stripe account for payment processing
- 15-20 minutes deployment time

## Step 1: Railway Account Setup

### 1.1 Create Railway Account
1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub (recommended for seamless integration)
3. Verify your email address
4. Complete account setup

### 1.2 Install Railway CLI (Optional but Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login
```

## Step 2: Project Preparation

### 2.1 Create Railway Configuration Files

Create `railway.json` in your project root:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true"
  }
}
```

Create `nixpacks.toml` for Python environment:
```toml
[phases.setup]
nixPkgs = ["python311", "postgresql"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[phases.build]
cmds = ["echo 'Build completed'"]

[start]
cmd = "streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true"
```

### 2.2 Update Streamlit Configuration
Ensure `.streamlit/config.toml` is configured for production:
```toml
[server]
headless = true
address = "0.0.0.0"
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
showErrorDetails = false

[theme]
base = "light"
```

## Step 3: Database Setup

### 3.1 Add PostgreSQL Service
1. In Railway dashboard, click "New Project"
2. Select "Provision PostgreSQL"
3. Name your database (e.g., "dataguardian-db")
4. Note down the connection details

### 3.2 Database Configuration
Railway automatically provides these environment variables:
- `DATABASE_URL`
- `PGHOST`
- `PGPORT`
- `PGDATABASE`
- `PGUSER`
- `PGPASSWORD`

## Step 4: Application Deployment

### 4.1 Deploy from GitHub
1. In Railway dashboard, click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your DataGuardian Pro repository
4. Select main branch
5. Click "Deploy"

### 4.2 Environment Variables Setup
In Railway dashboard, go to Variables tab and add:

```bash
# Database (automatically provided by Railway PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/database

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_live_your_publishable_key
STRIPE_SECRET_KEY=sk_live_your_secret_key

# Application Settings
ENVIRONMENT=production
JWT_SECRET=your_secure_jwt_secret_32_chars_long
ENCRYPTION_KEY=your_encryption_key_32_chars_long

# Optional: Redis URL (if using Redis service)
REDIS_URL=redis://user:password@host:port

# Application Configuration
PYTHONPATH=/app
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_ENABLE_CORS=false
```

### 4.3 Custom Domain (Optional)
1. In Railway dashboard, go to Settings
2. Click "Generate Domain" for railway.app subdomain
3. Or add custom domain in "Custom Domain" section
4. Configure DNS records as instructed

## Step 5: Production Optimizations

### 5.1 Update requirements.txt for Production
Ensure these packages are in `requirements.txt`:
```txt
streamlit>=1.28.0
psycopg2-binary
gunicorn
redis
stripe
bcrypt
pyjwt
requests
pandas
plotly
pillow
reportlab
beautifulsoup4
trafilatura
pytesseract
opencv-python-headless
```

### 5.2 Create Health Check Endpoint
Add to your `app.py`:
```python
import streamlit as st

# Health check for Railway
if st.query_params.get("health") == "check":
    st.write("OK")
    st.stop()
```

## Step 6: Monitoring and Logs

### 6.1 Access Logs
```bash
# Using Railway CLI
railway logs

# Or in Railway dashboard
# Go to your service > View Logs
```

### 6.2 Performance Monitoring
1. Enable Railway metrics in dashboard
2. Monitor CPU, memory, and request metrics
3. Set up alerts for high usage

## Step 7: Scaling Configuration

### 7.1 Auto-scaling Setup
```bash
# In Railway dashboard, go to Settings
# Configure:
- Memory: 1GB (recommended minimum)
- CPU: 1 vCPU (scales automatically)
- Replicas: 1-3 (based on traffic)
```

### 7.2 Resource Limits
```json
{
  "resources": {
    "memory": "1GB",
    "cpu": "1000m"
  },
  "scaling": {
    "minReplicas": 1,
    "maxReplicas": 3
  }
}
```

## Step 8: Security Configuration

### 8.1 HTTPS Setup
- Railway provides automatic HTTPS
- SSL certificates are managed automatically
- Force HTTPS redirects are enabled by default

### 8.2 Environment Security
```bash
# Set secure environment variables
JWT_SECRET=$(openssl rand -base64 32)
ENCRYPTION_KEY=$(openssl rand -base64 32)
```

## Step 9: Backup Strategy

### 9.1 Database Backups
Railway PostgreSQL includes automatic backups:
- Daily backups retained for 7 days
- Point-in-time recovery available
- Manual backups can be triggered

### 9.2 Code Backups
- GitHub repository serves as code backup
- Use Railway CLI to download deployments if needed

## Step 10: Domain and SSL

### 10.1 Custom Domain Setup
1. In Railway dashboard, go to your service
2. Click "Settings" > "Domains"
3. Click "Custom Domain"
4. Enter your domain (e.g., dataguardian.yourcompany.com)
5. Configure DNS records:
   ```
   Type: CNAME
   Name: dataguardian (or subdomain)
   Value: your-app.railway.app
   ```

### 10.2 SSL Certificate
- Railway automatically provisions SSL certificates
- Certificates auto-renew
- HTTPS is enforced by default

## Step 11: Cost Optimization

### 11.1 Railway Pricing
- **Hobby Plan**: $5/month (perfect for SaaS launch)
  - 512MB RAM, 1 vCPU
  - $5/month PostgreSQL
  - Custom domains included
  - Automatic scaling

### 11.2 Resource Monitoring
```bash
# Monitor usage
railway usage

# Check billing
railway billing
```

## Step 12: Launch Checklist

### Pre-Launch
- [ ] Environment variables configured
- [ ] Database connected and migrated
- [ ] Stripe payments tested
- [ ] Custom domain configured
- [ ] SSL certificate active
- [ ] Health checks passing
- [ ] Logs monitoring setup

### Post-Launch
- [ ] Monitor application performance
- [ ] Check error rates
- [ ] Verify payment processing
- [ ] Test all scanner functions
- [ ] Monitor resource usage
- [ ] Set up alerts

## Step 13: Troubleshooting

### Common Issues

**1. Port Configuration**
```bash
# Ensure your app uses Railway's PORT environment variable
PORT=${PORT:-8501}
streamlit run app.py --server.port $PORT
```

**2. Database Connection**
```python
# Test database connection
import psycopg2
import os

try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    print("Database connected successfully")
except Exception as e:
    print(f"Database connection failed: {e}")
```

**3. Memory Issues**
- Increase memory allocation in Railway settings
- Optimize large file processing
- Implement caching strategies

### Support Resources
- Railway Discord: [discord.gg/railway](https://discord.gg/railway)
- Railway Docs: [docs.railway.app](https://docs.railway.app)
- Railway Status: [status.railway.app](https://status.railway.app)

## Expected Deployment Time
- **Initial Setup**: 5 minutes
- **Environment Configuration**: 5 minutes
- **Database Setup**: 3 minutes
- **Application Deployment**: 2-5 minutes
- **Custom Domain Setup**: 5 minutes
- **Total**: 15-25 minutes

## Monthly Costs (Netherlands/EU)
- **Railway Hobby**: $5/month (app hosting)
- **PostgreSQL**: $5/month (managed database)
- **Total**: $10/month (perfect for SaaS launch)

This Railway deployment provides:
- **Automatic HTTPS** and SSL certificates
- **Managed PostgreSQL** database
- **Auto-scaling** based on traffic
- **EU data residency** (Railway has EU regions)
- **99.9% uptime** SLA
- **Simple pricing** model

Your DataGuardian Pro will be live at `https://your-app.railway.app` within 20 minutes!