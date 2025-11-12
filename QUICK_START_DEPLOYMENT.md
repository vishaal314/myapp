# 🚀 Quick Start - CI/CD Deployment

## ✅ Prerequisites Checklist

Before deploying, ensure:

- [ ] GitHub repository created: `vishaal314/myapp`
- [ ] All 6 GitHub secrets added (see `GITHUB_SECRETS_SETUP.md`)
- [ ] Dockerfile exists in repository
- [ ] GitHub Actions workflow exists: `.github/workflows/deploy.yml`
- [ ] Git configured in Replit

---

## 🎯 Deploy in 3 Steps

### Step 1: Configure Git in Replit

```bash
# Configure git user
git config --global user.name "vishaal314"
git config --global user.email "your-email@example.com"

# Add GitHub remote (if not already added)
git remote add origin https://github.com/vishaal314/myapp.git

# Or update existing remote
git remote set-url origin https://github.com/vishaal314/myapp.git
```

---

### Step 2: Push Your Code

```bash
# Stage all changes
git add .

# Commit with message
git commit -m "Deploy application"

# Push to GitHub (this triggers the pipeline!)
git push origin main
```

**Note:** You may need a GitHub Personal Access Token if prompted for password.

---

### Step 3: Monitor & Approve Deployment

1. **Go to GitHub Actions:**
   - Visit: `https://github.com/vishaal314/myapp/actions`
   - Click on the running workflow

2. **Watch Build Progress:**
   - Wait for "Build and Push to Docker Hub" to complete
   - Image will be pushed to: `vishaalnoord7/myapp:latest`

3. **Approve Deployment (if manual approval enabled):**
   - Click **Review deployments**
   - Select **production**
   - Click **Approve and deploy**

4. **Verify Deployment:**
   - Wait for "Deploy to External Server" to complete
   - Visit: `http://45.81.35.202`

---

## 🔍 Verify on Server

SSH into your server to verify:

```bash
ssh root@45.81.35.202

# Check container is running
docker ps | grep myapp

# Check logs
docker logs myapp

# Test application
curl http://localhost
```

---

## 📊 What Happens Automatically

```
┌──────────────┐
│  Replit Dev  │
│              │
│  git push    │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│         GitHub Actions               │
│                                      │
│  1. Checkout code                    │
│  2. Build Docker image               │
│  3. Push to Docker Hub               │
│     → vishaalnoord7/myapp:latest     │
│                                      │
│  4. [Wait for approval] ⏸️            │
│                                      │
│  5. SSH to 45.81.35.202              │
│  6. Pull latest image                │
│  7. Stop old container               │
│  8. Run new container                │
│  9. Verify deployment ✅             │
└──────────────────────────────────────┘
       │
       ▼
┌──────────────────┐
│  Live Server     │
│  45.81.35.202    │
│  Port 80         │
└──────────────────┘
```

---

## 🛠️ Troubleshooting

### Build Fails
- Check Dockerfile syntax
- Verify GitHub secrets are correct
- Check GitHub Actions logs

### Deployment Fails
- Verify server is accessible: `ssh root@45.81.35.202`
- Check Docker is installed on server: `docker --version`
- Verify port 80 is available: `netstat -tlnp | grep :80`

### Container Not Running
- Check logs: `docker logs myapp`
- Check if port 5000 is exposed in Dockerfile
- Verify environment variables

---

## 🔄 Rollback to Previous Version

If deployment fails, rollback:

```bash
ssh root@45.81.35.202

# Stop current container
docker stop myapp
docker rm myapp

# List available images
docker images | grep myapp

# Run previous version (use git SHA tag)
docker run -d --name myapp -p 80:5000 vishaalnoord7/myapp:<previous-git-sha>
```

---

## ⚡ Quick Commands

```bash
# Deploy
git add . && git commit -m "Update" && git push origin main

# Check deployment status
# → Go to https://github.com/vishaal314/myapp/actions

# Verify on server
ssh root@45.81.35.202 "docker ps | grep myapp"

# View logs
ssh root@45.81.35.202 "docker logs myapp --tail=50"

# Restart container
ssh root@45.81.35.202 "docker restart myapp"
```

---

**Ready to deploy? Just run:** `git push origin main` 🚀
