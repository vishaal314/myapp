# 🚀 CI/CD Pipeline Setup Guide

## Overview
This guide sets up automated deployment: **Replit → GitHub → Docker Hub → External Server**

---

## 📋 **STEP 1: GitHub Repository Setup**

### 1.1 Create/Configure Repository
- **Repository:** `vishaal314/myapp`
- **Branch:** `main`

### 1.2 Add GitHub Secrets
Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `DOCKERHUB_USERNAME` | `vishaalnoord7` |
| `DOCKERHUB_TOKEN` | `dckr_pat_Y4tYx9kjQy5k4MA-WMDQ6Rka3K8` |
| `SSH_HOST` | `45.81.35.202` |
| `SSH_USER` | `root` |
| `SSH_PRIVATE_KEY` | `9q54IQq0S4l3` |
| `APP_DIR` | `/opt/dataguardian` |

### 1.3 Configure Environment (Optional - for manual approval)
Go to your GitHub repo → **Settings** → **Environments** → **New environment**

- **Name:** `production`
- **Protection rules:** 
  - ✅ Required reviewers (add yourself)
  - This will require manual approval before deployment

---

## 📋 **STEP 2: Update GitHub Actions Workflow**

The workflow file `.github/workflows/deploy.yml` needs to be updated with your requirements.

Current status: File exists, needs update

---

## 📋 **STEP 3: Configure Replit Git Integration**

### 3.1 Initialize Git (if not done)
```bash
git config --global user.name "vishaal314"
git config --global user.email "your-email@example.com"
```

### 3.2 Connect to GitHub
```bash
# Add remote (if not already added)
git remote add origin https://github.com/vishaal314/myapp.git

# Or set remote
git remote set-url origin https://github.com/vishaal314/myapp.git
```

### 3.3 Create GitHub Personal Access Token
1. Go to GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **Generate new token (classic)**
3. Select scopes: `repo`, `workflow`
4. Copy the token

### 3.4 Add Token to Replit
Store in Replit Secrets (left sidebar → Secrets):
- **Key:** `GITHUB_TOKEN`
- **Value:** [your personal access token]

---

## 📋 **STEP 4: Workflow Structure**

### What Happens on `git push`:

```
1. TRIGGER: Push to main branch
   ↓
2. BUILD JOB (Automatic)
   ✅ Checkout code
   ✅ Build Docker image
   ✅ Push to Docker Hub as:
      - vishaalnoord7/myapp:latest
      - vishaalnoord7/myapp:<git-sha>
   ↓
3. DEPLOY JOB (Manual Approval)
   ⏸️  Waits for approval in GitHub Actions UI
   ↓
   ✅ SSH to 45.81.35.202
   ✅ Pull latest image
   ✅ Stop old container
   ✅ Run new container on port 80
   ✅ Verify deployment
```

---

## 📋 **STEP 5: Deployment from Replit**

### Push changes to trigger pipeline:

```bash
# Stage changes
git add .

# Commit
git commit -m "Deploy: Updated application"

# Push to GitHub (triggers workflow)
git push origin main
```

---

## 📋 **STEP 6: Monitor Deployment**

### 6.1 Check GitHub Actions
1. Go to your repo: `https://github.com/vishaal314/myapp`
2. Click **Actions** tab
3. See the running workflow

### 6.2 Approve Deployment
1. Click on the running workflow
2. Click **Review deployments**
3. Select **production**
4. Click **Approve and deploy**

### 6.3 Verify on Server
```bash
ssh root@45.81.35.202

# Check running containers
docker ps | grep myapp

# Check logs
docker logs myapp

# Test application
curl http://45.81.35.202
```

---

## 📋 **STEP 7: Container Configuration**

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

**Port Mapping:**
- External: Port 80
- Internal: Port 5000 (Streamlit default)

**Volume:**
- `/opt/dataguardian` on server → `/data` in container

**Auto-restart:**
- Container restarts automatically if it crashes

---

## ✅ **VERIFICATION CHECKLIST**

Before first deployment:

- [ ] GitHub repository created: `vishaal314/myapp`
- [ ] All GitHub secrets added (6 secrets)
- [ ] GitHub environment `production` created (optional)
- [ ] Replit git remote configured
- [ ] Dockerfile exists and is correct
- [ ] GitHub Actions workflow file created: `.github/workflows/deploy.yml`

---

## 🔧 **TROUBLESHOOTING**

### Build fails on GitHub Actions
- Check Dockerfile syntax
- Verify Docker Hub credentials in GitHub secrets

### Deployment fails
- Verify SSH credentials (`SSH_HOST`, `SSH_USER`, `SSH_PRIVATE_KEY`)
- Check server is accessible: `ssh root@45.81.35.202`
- Ensure Docker is installed on server

### Container not accessible
- Check port 80 is not used: `netstat -tlnp | grep :80`
- Verify firewall allows port 80
- Check container logs: `docker logs myapp`

---

## 📊 **WORKFLOW FEATURES**

✅ **Automatic Docker Build:** On every push to main  
✅ **Multi-tag Strategy:** Latest + Git SHA for rollback  
✅ **Manual Approval:** Production environment requires approval  
✅ **Health Check:** Verifies container started successfully  
✅ **Automatic Cleanup:** Removes old containers  
✅ **Auto-restart:** Container restarts on failure  

---

## 🎯 **QUICK DEPLOYMENT FLOW**

```bash
# On Replit:
git add .
git commit -m "Update application"
git push origin main

# On GitHub:
# → Actions tab → Approve deployment

# Result:
# → New version live at http://45.81.35.202
```

---

**Ready to set up? Start with Step 1: Add GitHub Secrets** 🚀
