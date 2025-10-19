# Quick Start: Deploy to Production Server

**🚀 Deploy all 16 scanners to dataguardianpro.nl in 3 steps**

---

## Step 1: Run Deployment Script

```bash
./deploy_all_16_scanners_to_production.sh
```

**What it does:**
- ✅ Removes Blob Scan from all locations
- ✅ Adds all 16 scanners with correct pricing
- ✅ Rebuilds Docker containers (no cache)
- ✅ Restarts all services
- ℹ️  No backup (use Git for rollback)

**Time:** ~3-5 minutes

---

## Step 2: Verify Deployment

```bash
./verify_production_deployment.sh
```

**What it checks:**
- ✅ Scanner count (should be 16)
- ✅ Blob Scan removed
- ✅ Docker containers running
- ✅ Streamlit healthy

---

## Step 3: Test in Browser

1. Open: https://dataguardianpro.nl/payment_test_ideal
2. Hard refresh: **Ctrl+Shift+R** (Windows) or **Cmd+Shift+R** (Mac)
3. Check dropdown shows **16 scanners**
4. Verify **Blob Scan is NOT present**

---

## 📊 Expected Result

### Dropdown should show:

**Basic (7):**
1. Manual Upload - €10.89
2. API Scan - €21.78
3. Code Scan - €27.83
4. Website Scan - €30.25
5. Image Scan - €33.88
6. DPIA Scan - €45.98
7. Database Scan - €55.66

**Advanced (3):**
8. Sustainability Scan - €38.72
9. AI Model Scan - €49.61
10. SOC2 Scan - €66.55

**Enterprise (6):**
11. Google Workspace Scan - €82.28
12. Microsoft 365 Scan - €90.75
13. Enterprise Scan - €107.69
14. Salesforce Scan - €111.32
15. Exact Online Scan - €151.25
16. SAP Integration Scan - €181.50

**Total: 16 scanners ✅**

---

## 🔧 If Something Goes Wrong

### Rollback (using Git):
```bash
ssh root@dataguardianpro.nl
cd /opt/dataguardian
git reset --hard HEAD~1
docker-compose down && docker-compose build --no-cache && docker-compose up -d
```

---

## 📞 Configuration

Default settings:
```bash
SERVER_USER=root
SERVER_HOST=dataguardianpro.nl
SERVER_PATH=/opt/dataguardian
```

To customize:
```bash
export SERVER_USER="your_username"
export SERVER_HOST="your_server_ip"
./deploy_all_16_scanners_to_production.sh
```

---

**That's it! Your production server will have all 16 scanners.** 🎉
