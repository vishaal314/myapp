# Railway Deployment Guide for DataGuardian Pro

## Prerequisites
- GitHub account
- Railway account (free at railway.app)
- Your code pushed to GitHub

## Step-by-Step Deployment

### 1. GitHub Repository Setup

Push your code to GitHub with these commands:
```bash
git init
git add .
git commit -m "Initial commit for Railway deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/dataguardian-pro.git
git push -u origin main
```

### 2. Railway Account Setup

1. Go to [railway.app](https://railway.app)
2. Click "Login with GitHub"
3. Authorize Railway to access your repositories

### 3. Create New Project

1. Click "New Project"
2. Choose "Deploy from GitHub repo"
3. Select your `dataguardian-pro` repository
4. Railway will automatically detect your Dockerfile

### 4. Add PostgreSQL Database

1. In your Railway project dashboard
2. Click "New Service"
3. Choose "Database" → "PostgreSQL"
4. Railway creates a managed PostgreSQL instance
5. Note the database connection details

### 5. Configure Environment Variables

In Railway dashboard, go to your app service and add these variables:

**Required Variables:**
```
DATABASE_URL=postgresql://user:pass@host:port/database
PGHOST=your-postgres-host
PGUSER=your-postgres-user  
PGPASSWORD=your-postgres-password
PGDATABASE=your-postgres-database
PGPORT=5432
PORT=5000
PYTHONUNBUFFERED=1
```

**Optional API Keys:**
```
OPENAI_API_KEY=your-openai-key
STRIPE_SECRET_KEY=sk_test_your-stripe-key
STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-key
ANTHROPIC_API_KEY=your-anthropic-key
```

### 6. Database Connection String

Railway provides the DATABASE_URL automatically:
1. Go to PostgreSQL service in Railway
2. Click "Connect" tab
3. Copy "Postgres Connection URL"
4. Paste it as DATABASE_URL in your app service

### 7. Deploy

1. Railway automatically builds and deploys when you push to GitHub
2. Monitor deployment in the "Deployments" tab
3. Check logs for any issues

### 8. Custom Domain (Optional)

1. In Railway dashboard, go to "Settings"
2. Add your custom domain
3. Update DNS records as instructed

## Expected Costs

**Railway Free Tier:**
- $5 free credits monthly
- No credit card required initially
- Sufficient for development/testing

**Typical Monthly Costs:**
- Small app: $0-10/month
- Medium traffic: $10-25/month
- Database included in app costs

## Troubleshooting

**Build Fails:**
- Check Dockerfile syntax
- Verify all dependencies in pyproject.toml
- Review build logs in Railway dashboard

**Database Connection Issues:**
- Verify DATABASE_URL format
- Check if database service is running
- Ensure firewall rules allow connections

**App Won't Start:**
- Check PORT environment variable (should be 5000)
- Verify Streamlit configuration
- Review application logs

## Monitoring

Railway provides:
- Real-time logs
- CPU/Memory usage metrics
- Deployment history
- Automatic SSL certificates
- Built-in monitoring

## Scaling

Railway automatically handles:
- Load balancing
- SSL termination
- Health checks
- Zero-downtime deployments