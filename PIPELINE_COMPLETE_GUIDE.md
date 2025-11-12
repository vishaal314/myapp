# 🚀 Complete CI/CD Pipeline Setup - Start to Finish

## Pipeline Flow
```
Replit → GitHub → Docker Hub → Server (45.81.35.202) → Live at dataguardianpro.nl
```

---

## ✅ STEP 1: Add GitHub Secrets (5 minutes)

### 1.1 Go to GitHub Secrets Page
```
https://github.com/vishaal314/myapp/settings/secrets/actions
```

### 1.2 Click "New repository secret" and add each of these:

**Secret 1:**
- Name: `DOCKERHUB_USERNAME`
- Value: `vishaalnoord7`

**Secret 2:**
- Name: `DOCKERHUB_TOKEN`
- Value: `dckr_pat_Y4tYx9kjQy5k4MA-WMDQ6Rka3K8`

**Secret 3:**
- Name: `SSH_HOST`
- Value: `45.81.35.202`

**Secret 4:**
- Name: `SSH_USER`
- Value: `root`

**Secret 5:**
- Name: `SSH_PRIVATE_KEY`
- Value: `9q54IQq0S4l3`

**Secret 6:**
- Name: `APP_DIR`
- Value: `/opt/dataguardian`

### 1.3 Verify
You should see all 6 secrets listed on the secrets page.

---

## ✅ STEP 2: Configure Git in Replit (2 minutes)

### 2.1 Open Replit Shell and run:

```bash
# Set your identity
git config --global user.name "vishaal314"
git config --global user.email "your-email@example.com"

# Add GitHub remote
git remote add origin https://github.com/vishaal314/myapp.git
```

If remote already exists, update it:
```bash
git remote set-url origin https://github.com/vishaal314/myapp.git
```

### 2.2 Verify remote:
```bash
git remote -v
# Should show: origin https://github.com/vishaal314/myapp.git
```

---

## ✅ STEP 3: Push Code to Trigger Pipeline (30 seconds)

```bash
# Stage all files
git add .

# Commit
git commit -m "Initial deployment"

# Push to GitHub (this triggers the pipeline!)
git push origin main
```

**Note:** If prompted for password, use a GitHub Personal Access Token instead of password.

---

## ✅ STEP 4: Monitor GitHub Actions (5-10 minutes)

### 4.1 Go to GitHub Actions:
```
https://github.com/vishaal314/myapp/actions
```

### 4.2 Watch the workflow run:

**BUILD JOB** (3-5 minutes):
- ✅ Checkout code
- ✅ Build Docker image
- ✅ Push to Docker Hub: `vishaalnoord7/myapp:latest`

**DEPLOY JOB** (2-3 minutes):
- ⏸️ Waits for approval (if enabled) - Click "Review deployments" → "Approve"
- ✅ SSH to 45.81.35.202
- ✅ Pull image from Docker Hub
- ✅ Stop old container
- ✅ Start new container
- ✅ Verify deployment

### 4.3 Check completion:
Look for green checkmarks ✅ on all steps.

---

## ✅ STEP 5: Verify Deployment (1 minute)

### 5.1 Test via IP:
```
http://45.81.35.202
```
Should load your application!

### 5.2 SSH and check container:
```bash
ssh root@45.81.35.202

# Check container is running
docker ps | grep myapp

# Check logs
docker logs myapp --tail=50

# Exit
exit
```

---

## ✅ STEP 6: Configure Domain DNS (5 minutes + wait time)

### 6.1 Login to Namecheap:
```
https://www.namecheap.com
```

### 6.2 Configure DNS:
1. Go to **Domain List**
2. Click **Manage** next to dataguardianpro.nl
3. Click **Advanced DNS** tab
4. Add these A Records:

| Type | Host | Value | TTL |
|------|------|-------|-----|
| A Record | @ | 45.81.35.202 | Automatic |
| A Record | www | 45.81.35.202 | Automatic |

5. Delete any parking page or redirect records
6. Click **Save All Changes**

### 6.3 Wait for DNS propagation:
- Typical: 15-30 minutes
- Maximum: 24-48 hours

### 6.4 Test DNS:
```
https://dnschecker.org
Enter: dataguardianpro.nl
Should show: 45.81.35.202
```

### 6.5 Access via domain:
```
http://dataguardianpro.nl
```
Your app is now live! 🎉

---

## 🔄 FUTURE DEPLOYMENTS (After Initial Setup)

Every time you want to deploy updates:

```bash
# 1. Make your code changes in Replit

# 2. Push to GitHub
git add .
git commit -m "Update: describe your changes"
git push origin main

# 3. Monitor at https://github.com/vishaal314/myapp/actions

# 4. Approve deployment if manual approval is enabled

# 5. Done! Live at http://dataguardianpro.nl
```

---

## 📊 What Happens Automatically

```
You: git push origin main
  ↓
GitHub Actions (Automatic):
  ├─ Build Docker image
  ├─ Push to Docker Hub: vishaalnoord7/myapp:latest
  ├─ [Wait for approval - optional]
  ├─ SSH to 45.81.35.202
  ├─ Pull latest image
  ├─ Stop old container "myapp"
  ├─ Start new container on port 80
  └─ Verify deployment ✅
  ↓
Live: http://dataguardianpro.nl
```

---

## 🎯 Quick Commands Reference

### Deploy:
```bash
git add . && git commit -m "Update" && git push origin main
```

### Check deployment status:
```
https://github.com/vishaal314/myapp/actions
```

### SSH to server:
```bash
ssh root@45.81.35.202
```

### Check container:
```bash
docker ps | grep myapp
docker logs myapp --tail=100
```

### Restart container:
```bash
docker restart myapp
```

### Stop deployment:
```bash
docker stop myapp
docker rm myapp
```

---

## ✅ Complete Checklist

**Initial Setup:**
- [ ] GitHub repository created: vishaal314/myapp
- [ ] All 6 GitHub secrets added
- [ ] Git configured in Replit
- [ ] Workflow file exists: .github/workflows/deploy.yml
- [ ] Dockerfile exists

**First Deployment:**
- [ ] Code pushed to main branch
- [ ] Build job completed (green ✅)
- [ ] Deploy job completed (green ✅)
- [ ] App accessible at http://45.81.35.202

**Domain Setup:**
- [ ] A Record @ → 45.81.35.202 added in Namecheap
- [ ] A Record www → 45.81.35.202 added in Namecheap
- [ ] DNS propagated (test with dnschecker.org)
- [ ] App accessible at http://dataguardianpro.nl

**Optional Enhancements:**
- [ ] Manual approval environment configured
- [ ] SSL certificate installed (HTTPS)
- [ ] Monitoring/alerts configured

---

## 🚨 Troubleshooting

### Build fails:
- Check Dockerfile syntax
- Verify GitHub secrets are correct
- Check GitHub Actions logs

### Deployment fails:
- Verify server is accessible: `ssh root@45.81.35.202`
- Check Docker is installed: `ssh root@45.81.35.202 "docker --version"`
- Verify secrets are correct

### Domain not working:
- Wait longer (DNS can take 24-48 hours)
- Verify A Records in Namecheap
- Clear DNS cache on your computer
- Test with dnschecker.org

### Container not running:
- SSH to server and check logs: `docker logs myapp`
- Verify port 5000 is exposed in Dockerfile
- Check if port 80 is available: `netstat -tlnp | grep :80`

---

## 🎉 Success Criteria

After completing all steps:

✅ Code pushed to GitHub automatically triggers build  
✅ Docker image pushed to Docker Hub: vishaalnoord7/myapp:latest  
✅ Container deployed to 45.81.35.202  
✅ App accessible at http://45.81.35.202  
✅ DNS configured (dataguardianpro.nl → 45.81.35.202)  
✅ App accessible at http://dataguardianpro.nl  

**Total setup time:** ~20-30 minutes (excluding DNS propagation)

---

## 📞 Support Files

- `CI_CD_COMPLETE_SETUP.md` - Overview and features
- `GITHUB_SECRETS_SETUP.md` - Secret configuration details
- `NAMECHEAP_STEP_BY_STEP.md` - DNS configuration guide
- `QUICK_START_DEPLOYMENT.md` - Quick deployment reference

---

**Start with Step 1: Add GitHub Secrets!** 🚀
