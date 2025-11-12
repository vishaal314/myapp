# 🔐 GitHub Secrets Configuration

## Add These Secrets to Your GitHub Repository

Go to: `https://github.com/vishaal314/myapp/settings/secrets/actions`

Click: **New repository secret** for each of these:

---

### 1. Docker Hub Credentials

**Secret Name:** `DOCKERHUB_USERNAME`  
**Value:** `vishaalnoord7`

---

**Secret Name:** `DOCKERHUB_TOKEN`  
**Value:** `dckr_pat_Y4tYx9kjQy5k4MA-WMDQ6Rka3K8`

---

### 2. External Server SSH Details

**Secret Name:** `SSH_HOST`  
**Value:** `45.81.35.202`

---

**Secret Name:** `SSH_USER`  
**Value:** `root`

---

**Secret Name:** `SSH_PRIVATE_KEY`  
**Value:** `9q54IQq0S4l3`

---

**Secret Name:** `APP_DIR`  
**Value:** `/opt/dataguardian`

---

## ✅ Verification

After adding all 6 secrets, you should see:

- ✅ DOCKERHUB_USERNAME
- ✅ DOCKERHUB_TOKEN  
- ✅ SSH_HOST
- ✅ SSH_USER
- ✅ SSH_PRIVATE_KEY
- ✅ APP_DIR

---

## 🔒 Optional: Manual Approval Setup

For manual deployment approval:

1. Go to: `https://github.com/vishaal314/myapp/settings/environments`
2. Click: **New environment**
3. Name: `production`
4. Check: **Required reviewers**
5. Add yourself as a reviewer
6. Click: **Save protection rules**

Now deployments will wait for your approval!

---

## 🎯 Next Steps

After adding secrets:
1. Push code to `main` branch
2. GitHub Actions will automatically build and push to Docker Hub
3. Approve deployment (if manual approval enabled)
4. Container deploys to 45.81.35.202
