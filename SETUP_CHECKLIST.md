# ✅ CI/CD Pipeline Setup - Simple Checklist

Follow these steps in order. Check each box as you complete it.

---

## 🔐 PART 1: GitHub Secrets (5 minutes)

### Step 1: Open GitHub Secrets Page
```
https://github.com/vishaal314/myapp/settings/secrets/actions
```

### Step 2: Add Secrets (Click "New repository secret" for each)

- [ ] **Secret 1:** Name: `DOCKERHUB_USERNAME` → Value: `vishaalnoord7`
- [ ] **Secret 2:** Name: `DOCKERHUB_TOKEN` → Value: `dckr_pat_Y4tYx9kjQy5k4MA-WMDQ6Rka3K8`
- [ ] **Secret 3:** Name: `SSH_HOST` → Value: `45.81.35.202`
- [ ] **Secret 4:** Name: `SSH_USER` → Value: `root`
- [ ] **Secret 5:** Name: `SSH_PRIVATE_KEY` → Value: `9q54IQq0S4l3`
- [ ] **Secret 6:** Name: `APP_DIR` → Value: `/opt/dataguardian`

✅ You should see all 6 secrets listed on the page.

---

## 💻 PART 2: Configure Git (2 minutes)

### Step 3: Open Replit Shell

Copy and paste this (replace your-email):

```bash
git config --global user.name "vishaal314"
git config --global user.email "your-email@example.com"
git remote add origin https://github.com/vishaal314/myapp.git
```

- [ ] Commands executed without errors

If you see "remote origin already exists", run this instead:
```bash
git remote set-url origin https://github.com/vishaal314/myapp.git
```

---

## 🚀 PART 3: First Deployment (30 seconds)

### Step 4: Push Code

Copy and paste:

```bash
git add .
git commit -m "Initial deployment"
git push origin main
```

- [ ] Code pushed successfully

---

## 👀 PART 4: Watch Deployment (5-10 minutes)

### Step 5: Open GitHub Actions
```
https://github.com/vishaal314/myapp/actions
```

### Step 6: Watch Progress

You'll see:
- [ ] ✅ "Build and Push to Docker Hub" - Wait for green checkmark (3-5 min)
- [ ] ✅ "Deploy to External Server" - Wait for green checkmark (2-3 min)

**If deployment asks for approval:**
- Click "Review deployments"
- Click "production"
- Click "Approve and deploy"

---

## 🎉 PART 5: Verify It Works (1 minute)

### Step 7: Test Your App

Open in browser:
```
http://45.81.35.202
```

- [ ] App loads successfully! 🎉

---

## 🌐 PART 6: Setup Domain (5 minutes + wait)

### Step 8: Login to Namecheap
```
https://www.namecheap.com
```

### Step 9: Configure DNS

1. Click "Domain List"
2. Click "Manage" next to dataguardianpro.nl
3. Click "Advanced DNS" tab
4. Add these 2 records:

- [ ] **Record 1:** Type: `A Record` | Host: `@` | Value: `45.81.35.202` | TTL: `Automatic`
- [ ] **Record 2:** Type: `A Record` | Host: `www` | Value: `45.81.35.202` | TTL: `Automatic`

5. Delete any parking page or redirect records
6. Click "Save All Changes"

### Step 10: Wait for DNS

- [ ] Wait 15-30 minutes (grab coffee ☕)

### Step 11: Test Domain

Check DNS propagation:
```
https://dnschecker.org
Enter: dataguardianpro.nl
Should show: 45.81.35.202
```

- [ ] DNS shows correct IP

Open in browser:
```
http://dataguardianpro.nl
```

- [ ] Domain works! 🚀

---

## 🎯 DONE! You're Live!

Your pipeline is now complete:

✅ Push code → Auto build → Auto deploy → Live instantly

---

## 🔄 FUTURE UPDATES (After Initial Setup)

Every time you want to update:

```bash
git add .
git commit -m "Your update message"
git push origin main
```

Then:
1. Wait 5-10 minutes
2. Your changes are live at http://dataguardianpro.nl

**That's it!** 🎉

---

## 📞 Need Help?

If stuck on:
- **Secrets:** Make sure all 6 are added correctly
- **Git push:** You may need a GitHub Personal Access Token
- **Deployment:** Check https://github.com/vishaal314/myapp/actions for errors
- **Domain:** Wait longer (can take up to 24 hours)

---

**Start with Part 1: Add GitHub Secrets** 👆
