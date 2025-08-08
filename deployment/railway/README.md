# DataGuardian Pro - Railway Deployment

## Quick Deploy to Railway

This guide helps you deploy DataGuardian Pro to Railway in 30 minutes for €5-20/month with automatic scaling.

## Prerequisites

- GitHub account
- Railway account (free at railway.app)
- API keys (OpenAI, Stripe, etc.)

## Step-by-Step Deployment

### 1. Prepare Code for GitHub (5 minutes)

Your code is already Railway-ready with:
- ✅ `Dockerfile` configured
- ✅ `railway.toml` added
- ✅ `.gitignore` created
- ✅ Environment variables documented

### 2. Upload to GitHub (5 minutes)

1. Go to [github.com](https://github.com) and create new repository
2. Name it: `dataguardian-pro`
3. Upload all files from this Replit
4. Commit changes

### 3. Deploy to Railway (10 minutes)

1. Go to [railway.app](https://railway.app)
2. Login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `dataguardian-pro` repository
5. Railway auto-detects Dockerfile and starts building

### 4. Add PostgreSQL Database (3 minutes)

1. In Railway dashboard, click "New Service"
2. Choose "Database" → "PostgreSQL"
3. Wait for provisioning (2-3 minutes)

### 5. Configure Environment Variables (5 minutes)

Click on your app service → "Variables" tab:

**Database Variables (copy from PostgreSQL service):**
```
DATABASE_URL=postgresql://postgres:password@host:port/railway
PGHOST=host
PGUSER=postgres
PGPASSWORD=password
PGDATABASE=railway
PGPORT=5432
```

**Application Variables:**
```
PORT=5000
PYTHONUNBUFFERED=1
DEFAULT_REGION=Netherlands
DATA_RESIDENCY=EU
COMPLIANCE_MODE=UAVG
```

**API Keys (add your own):**
```
OPENAI_API_KEY=your-key-here
STRIPE_SECRET_KEY=sk_test_your-key
STRIPE_PUBLISHABLE_KEY=pk_test_your-key
```

### 6. Access Your Live App (2 minutes)

1. Wait for deployment to complete
2. Click on your app service
3. Find the public URL (looks like: `https://dataguardian-pro-production.up.railway.app`)
4. Your app is live!

## Cost Structure

- **Development**: $0-5/month (free tier)
- **Production**: $10-25/month (auto-scales)
- **Enterprise**: $25-100/month (high traffic)

## Features Included

- ✅ Automatic SSL certificates
- ✅ Global CDN
- ✅ Auto-scaling
- ✅ Zero-downtime deployments
- ✅ Real-time monitoring
- ✅ Automatic backups
- ✅ EU hosting available

## Monitoring

Railway provides:
- CPU/Memory usage
- Request analytics
- Error tracking
- Performance metrics
- Real-time logs

## Updates

Push to GitHub main branch → Railway auto-deploys

## Support

- Railway Discord: discord.gg/railway
- Documentation: docs.railway.app