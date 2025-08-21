# DataGuardian Pro - Railway Quick Start (5 Minutes)

## 🚀 Super Fast Railway Deployment

### Step 1: One-Click Deploy (2 minutes)
1. **Go to Railway**: [railway.app](https://railway.app)
2. **Sign up** with GitHub
3. **Click "New Project"** → **"Deploy from GitHub repo"**
4. **Select** your DataGuardian Pro repository
5. **Click Deploy** (Railway will auto-detect Python/Streamlit)

### Step 2: Add Database (1 minute)
1. In your Railway project dashboard
2. **Click "New"** → **"Database"** → **"PostgreSQL"** 
3. Railway automatically connects it to your app

### Step 3: Environment Variables (2 minutes)
In Railway dashboard, go to **Variables** tab and add:

```bash
# Stripe (required for payments)
STRIPE_PUBLISHABLE_KEY=pk_live_your_key_here
STRIPE_SECRET_KEY=sk_live_your_key_here

# Security (generate these)
JWT_SECRET=your_32_character_secret_here
ENCRYPTION_KEY=your_32_character_key_here

# Optional optimizations
ENVIRONMENT=production
STREAMLIT_SERVER_HEADLESS=true
```

### Step 4: Custom Domain (Optional)
1. **Settings** → **Domains** → **Custom Domain**
2. Add: `dataguardian.yourcompany.com`
3. Update DNS: `CNAME dataguardian → your-app.railway.app`

## ✅ That's It!

Your app will be live at:
- **Railway URL**: `https://your-app.railway.app`
- **Custom Domain**: `https://dataguardian.yourcompany.com`

## 💰 Cost: $10/month
- Railway Hobby: $5/month
- PostgreSQL: $5/month
- **Total**: $10/month for full SaaS platform

## 📊 What You Get
- ✅ Automatic HTTPS/SSL
- ✅ EU data residency available
- ✅ Auto-scaling (1-3 instances)
- ✅ Managed PostgreSQL
- ✅ 99.9% uptime SLA
- ✅ Automatic deployments from GitHub
- ✅ Built-in monitoring

## 🔧 Files Needed
Make sure these files are in your repository:

**railway.json** (already created)
**nixpacks.toml** (already created)  
**Procfile** (already created)
**requirements.txt** (copy from railway-requirements.txt)

## 🚨 Important Notes
1. **Copy `railway-requirements.txt` to `requirements.txt`** before deploying
2. **Get Stripe keys** from your Stripe dashboard
3. **Generate secure secrets**: Use online generator for JWT_SECRET and ENCRYPTION_KEY
4. **Test payments** in Stripe test mode first

## 📞 Support
- Railway Discord: discord.gg/railway
- Railway Docs: docs.railway.app

**Your DataGuardian Pro SaaS will be live in 5 minutes!** 🎉