# ✅ CI/CD Pipeline - Complete Setup

## 🎯 Overview

Your automated deployment pipeline is now configured:

**Replit → GitHub → Docker Hub → External Server (45.81.35.202)**

---

## 📁 Files Created

✅ `.github/workflows/deploy.yml` - GitHub Actions workflow  
✅ `GITHUB_SECRETS_SETUP.md` - Secret configuration guide  
✅ `QUICK_START_DEPLOYMENT.md` - Quick deployment guide  
✅ `CI_CD_SETUP_INSTRUCTIONS.md` - Detailed instructions  

---

## 🚀 Setup in 3 Easy Steps

### **STEP 1: Add GitHub Secrets** (5 minutes)

Go to: `https://github.com/vishaal314/myapp/settings/secrets/actions`

Add these 6 secrets:

| Secret Name | Value |
|-------------|-------|
| `DOCKERHUB_USERNAME` | `vishaalnoord7` |
| `DOCKERHUB_TOKEN` | `dckr_pat_Y4tYx9kjQy5k4MA-WMDQ6Rka3K8` |
| `SSH_HOST` | `45.81.35.202` |
| `SSH_USER` | `root` |
| `SSH_PRIVATE_KEY` | `9q54IQq0S4l3` |
| `APP_DIR` | `/opt/dataguardian` |

---

### **STEP 2: Configure Git in Replit** (2 minutes)

```bash
# Set your git identity
git config --global user.name "vishaal314"
git config --global user.email "your-email@example.com"

# Add GitHub remote
git remote add origin https://github.com/vishaal314/myapp.git
```

---

### **STEP 3: Deploy!** (1 command)

```bash
git add .
git commit -m "Initial deployment"
git push origin main
```

**That's it!** The pipeline will automatically:
1. ✅ Build Docker image
2. ✅ Push to Docker Hub (`vishaalnoord7/myapp:latest`)
3. ✅ Wait for approval (if configured)
4. ✅ Deploy to 45.81.35.202
5. ✅ Start container on port 80

---

## 📊 How It Works

```
┌─────────────────┐
│   Replit        │
│                 │
│  1. Code        │
│  2. git push    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         GitHub Actions                  │
│                                         │
│  BUILD JOB (Automatic):                 │
│  ✅ Checkout code                        │
│  ✅ Build Docker image                   │
│  ✅ Push to Docker Hub                   │
│     → vishaalnoord7/myapp:latest        │
│     → vishaalnoord7/myapp:<git-sha>     │
│                                         │
│  DEPLOY JOB (Manual Approval):          │
│  ⏸️  Wait for approval                   │
│  ✅ SSH to 45.81.35.202                  │
│  ✅ Pull latest image from Docker Hub    │
│  ✅ Stop old container "myapp"           │
│  ✅ Run new container                    │
│  ✅ Verify deployment                    │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Live Server    │
│  45.81.35.202   │
│  Port: 80       │
│  Container: myapp│
└─────────────────┘
```

---

## 🎬 Your First Deployment

### 1. Push Code
```bash
git add .
git commit -m "Deploy application"
git push origin main
```

### 2. Monitor on GitHub
- Go to: `https://github.com/vishaal314/myapp/actions`
- Watch the workflow run
- See build progress in real-time

### 3. Approve Deployment (Optional)
If you configured manual approval:
- Click **Review deployments**
- Select **production**
- Click **Approve and deploy**

### 4. Verify
- Visit: `http://45.81.35.202`
- Your app is live! 🎉

---

## 🔧 Container Configuration

The deployment runs this command on your server:

```bash
docker run -d \
  --name myapp \
  --restart unless-stopped \
  -p 80:5000 \
  -v /opt/dataguardian:/data \
  -e ENVIRONMENT=production \
  vishaalnoord7/myapp:latest
```

**Key Points:**
- **Port:** External 80 → Internal 5000 (Streamlit)
- **Volume:** `/opt/dataguardian` → `/data` in container
- **Auto-restart:** Container restarts on crashes
- **Name:** `myapp` (easy to manage)

---

## ✅ Features Included

✅ **Automatic Docker Build** - On every push to main  
✅ **Multi-tag Strategy** - Latest + Git SHA for rollback  
✅ **Manual Approval** - Optional production gate  
✅ **Health Verification** - Confirms container started  
✅ **Auto Cleanup** - Removes old containers/images  
✅ **Detailed Logging** - See every deployment step  
✅ **Rollback Support** - Tagged images for easy rollback  

---

## 🛠️ Quick Commands

### Deploy
```bash
git push origin main
```

### Check Status
```bash
ssh root@45.81.35.202 "docker ps | grep myapp"
```

### View Logs
```bash
ssh root@45.81.35.202 "docker logs myapp --tail=100"
```

### Restart Container
```bash
ssh root@45.81.35.202 "docker restart myapp"
```

### Stop Container
```bash
ssh root@45.81.35.202 "docker stop myapp"
```

---

## 🔒 Optional: Enable Manual Approval

For production safety:

1. Go to: `https://github.com/vishaal314/myapp/settings/environments`
2. Click: **New environment**
3. Name: `production`
4. Enable: **Required reviewers**
5. Add yourself
6. Save

Now deployments wait for your approval! ⏸️

---

## 📚 Documentation

- **Quick Start:** See `QUICK_START_DEPLOYMENT.md`
- **Secrets Setup:** See `GITHUB_SECRETS_SETUP.md`
- **Full Guide:** See `CI_CD_SETUP_INSTRUCTIONS.md`

---

## 🎯 Next Steps

1. ✅ Add GitHub secrets → **Do this first!**
2. ✅ Configure git in Replit
3. ✅ Push code: `git push origin main`
4. ✅ Watch magic happen! 🚀

---

**Ready to deploy? Start with adding GitHub secrets!** 🔐
