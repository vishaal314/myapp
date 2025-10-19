# Production Deployment Instructions - All 16 Scanners

**Date:** October 19, 2025  
**Script:** `deploy_all_16_scanners_to_production.sh`  
**Target:** dataguardianpro.nl

---

## 🎯 What This Deployment Does

1. ✅ **Removes Blob Scan** from all production files
2. ✅ **Adds all 16 scanners** to payment dropdowns
3. ✅ **Updates correct pricing** (21% Netherlands VAT)
4. ✅ **Rebuilds Docker containers** (no cache)
5. ✅ **Restarts all services**
6. ✅ **Creates automatic backup** before changes

---

## 📋 Files Updated on Production

1. `services/stripe_payment.py` - Scanner pricing backend
2. `app.py` - Main payment dropdown
3. `test_ideal_payment.py` - Test payment page
4. Docker containers rebuilt with --no-cache

---

## 🚀 How to Deploy

### Step 1: Set Environment Variables (Optional)

If your server setup is different, export these:

```bash
export SERVER_USER="root"              # Your SSH username
export SERVER_HOST="dataguardianpro.nl"  # Your server hostname/IP
export SERVER_PATH="/opt/dataguardian"   # Installation path
```

### Step 2: Run the Deployment Script

```bash
./deploy_all_16_scanners_to_production.sh
```

### Step 3: Monitor the Output

The script will:
- ✅ Test SSH connection
- ✅ Create backup
- ✅ Update all files
- ✅ Verify changes
- ✅ Rebuild Docker (no cache)
- ✅ Restart services

### Step 4: Verify Deployment

After completion, test:

```bash
# On your production server
curl https://dataguardianpro.nl/_stcore/health

# Should return: {"status": "ok"}
```

---

## 🔍 What Gets Updated

### services/stripe_payment.py

**Before:**
```python
SCAN_PRICES = {
    "Code Scan": 2300,
    "Blob Scan": 1400,  # ← REMOVED
    "Image Scan": 2800,
    # ... only 8 scanners
}
```

**After:**
```python
SCAN_PRICES = {
    "Manual Upload": 900,
    "API Scan": 1800,
    "Code Scan": 2300,
    "Website Scan": 2500,
    "Image Scan": 2800,
    "DPIA Scan": 3800,
    "Database Scan": 4600,
    "Sustainability Scan": 3200,
    "AI Model Scan": 4100,
    "SOC2 Scan": 5500,
    "Google Workspace Scan": 6800,
    "Microsoft 365 Scan": 7500,
    "Enterprise Scan": 8900,
    "Salesforce Scan": 9200,
    "Exact Online Scan": 12500,
    "SAP Integration Scan": 15000,
    # 16 scanners total ✅
}
```

### app.py & test_ideal_payment.py

**All 16 scanners added to dropdown:**
```python
scan_options = {
    # Basic (7)
    "Manual Upload": "€9.00 + €1.89 VAT = €10.89",
    "API Scan": "€18.00 + €3.78 VAT = €21.78",
    "Code Scan": "€23.00 + €4.83 VAT = €27.83",
    "Website Scan": "€25.00 + €5.25 VAT = €30.25",
    "Image Scan": "€28.00 + €5.88 VAT = €33.88",
    "DPIA Scan": "€38.00 + €7.98 VAT = €45.98",
    "Database Scan": "€46.00 + €9.66 VAT = €55.66",
    # Advanced (3)
    "Sustainability Scan": "€32.00 + €6.72 VAT = €38.72",
    "AI Model Scan": "€41.00 + €8.61 VAT = €49.61",
    "SOC2 Scan": "€55.00 + €11.55 VAT = €66.55",
    # Enterprise (6)
    "Google Workspace Scan": "€68.00 + €14.28 VAT = €82.28",
    "Microsoft 365 Scan": "€75.00 + €15.75 VAT = €90.75",
    "Enterprise Scan": "€89.00 + €18.69 VAT = €107.69",
    "Salesforce Scan": "€92.00 + €19.32 VAT = €111.32",
    "Exact Online Scan": "€125.00 + €26.25 VAT = €151.25",
    "SAP Integration Scan": "€150.00 + €31.50 VAT = €181.50"
}
```

---

## ✅ Verification Steps

After deployment completes:

### 1. Check Scanner Count
```bash
ssh root@dataguardianpro.nl "cd /opt/dataguardian && python3 -c 'from services.stripe_payment import SCAN_PRICES; print(len(SCAN_PRICES))'"
# Should output: 16
```

### 2. Verify Blob Scan Removed
```bash
ssh root@dataguardianpro.nl "cd /opt/dataguardian && grep -c 'Blob Scan' services/stripe_payment.py || echo '0'"
# Should output: 0
```

### 3. Check Docker Containers
```bash
ssh root@dataguardianpro.nl "docker-compose ps"
# All containers should show "Up"
```

### 4. Test Website
Open in browser:
- https://dataguardianpro.nl
- Navigate to payment test page
- Verify dropdown shows 16 scanners
- Confirm Blob Scan is NOT present

---

## 🔄 Rollback Instructions

If something goes wrong:

```bash
# Connect to server
ssh root@dataguardianpro.nl

# Find backup directory (created automatically)
BACKUP_DIR=$(ls -td /opt/dataguardian_backups/* | head -1)
echo "Using backup: $BACKUP_DIR"

# Restore files
cd /opt/dataguardian
cp ${BACKUP_DIR}/app.py.backup app.py
cp ${BACKUP_DIR}/stripe_payment.py.backup services/stripe_payment.py
cp ${BACKUP_DIR}/test_ideal_payment.py.backup test_ideal_payment.py

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 📊 Expected Results

### Before Deployment:
- Blob Scan: ✗ Present in dropdown
- Total scanners: 8-10 scanners
- Dropdown: Incomplete

### After Deployment:
- Blob Scan: ✅ Removed completely
- Total scanners: ✅ 16 scanners
- Dropdown: ✅ All scanners with correct pricing

---

## 🔧 Troubleshooting

### Issue: "Cannot connect to server"
**Solution:**
```bash
# Test SSH connection
ssh root@dataguardianpro.nl "echo 'Connected'"

# If fails, check SSH config or provide different credentials
export SERVER_USER="your_username"
export SERVER_HOST="your_ip_address"
```

### Issue: "Docker containers not starting"
**Solution:**
```bash
ssh root@dataguardianpro.nl
cd /opt/dataguardian
docker-compose logs
# Check logs for errors
```

### Issue: "Changes not visible in browser"
**Solution:**
```bash
# Clear browser cache
# Windows/Linux: Ctrl + Shift + R
# Mac: Cmd + Shift + R
# Or use incognito mode
```

---

## 📝 Deployment Checklist

Pre-Deployment:
- [ ] SSH access to dataguardianpro.nl working
- [ ] Script is executable (`chmod +x deploy_all_16_scanners_to_production.sh`)
- [ ] Server has enough disk space for backup

During Deployment:
- [ ] Script completes without errors
- [ ] Backup created successfully
- [ ] Files updated and verified
- [ ] Docker containers rebuilt
- [ ] Services restarted

Post-Deployment:
- [ ] Website accessible at https://dataguardianpro.nl
- [ ] Payment page loads correctly
- [ ] Dropdown shows 16 scanners
- [ ] Blob Scan NOT present
- [ ] Test payment flow works

---

## 🎉 Success Indicators

You'll know deployment succeeded when you see:

```
==========================================
✅ DEPLOYMENT COMPLETE
==========================================

📊 Summary:
   ✅ Blob Scan removed from all files
   ✅ All 16 scanners added to dropdowns
   ✅ services/stripe_payment.py updated
   ✅ app.py updated
   ✅ test_ideal_payment.py updated
   ✅ Docker containers rebuilt (no cache)
   ✅ Services restarted

🌐 Production URL: https://dataguardianpro.nl

🎉 All 16 scanners are now live on production!
```

---

## 📞 Support

If you encounter issues:

1. Check the backup directory: `/opt/dataguardian_backups/`
2. Review Docker logs: `docker-compose logs`
3. Verify file contents manually
4. Use rollback instructions if needed

---

**Deployment Script:** `deploy_all_16_scanners_to_production.sh`  
**Ready to deploy!** 🚀
