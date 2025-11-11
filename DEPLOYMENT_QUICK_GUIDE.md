# 🚀 DEPLOYMENT QUICK GUIDE (NO BACKUP)

## 3-Step Deployment Process

### STEP 1: Create Patch (on Replit)
```bash
bash deploy_patch_nov2025.sh create
```

**Output:** `dataguardian_patch_nov2025_TIMESTAMP.tar.gz` (244K)

---

### STEP 2: Transfer to Server
```bash
# Choose your preferred method:

# Option A - rsync
rsync -avz dataguardian_patch_*.tar.gz root@dataguardianpro.nl:/tmp/

# Option B - scp
scp dataguardian_patch_*.tar.gz root@dataguardianpro.nl:/tmp/

# Option C - Manual FTP/SFTP upload to /tmp/
```

---

### STEP 3: Apply Patch (on server)
```bash
ssh root@dataguardianpro.nl
cd /tmp
tar -xzf dataguardian_patch_*.tar.gz
cd dataguardian_patch_*/
bash deploy_patch_nov2025.sh apply /opt/dataguardian
```

---

## What the Script Does

**Deployment Steps (No Backup):**

1. ✅ **Stop services** → `docker-compose down`
2. ✅ **Apply patch** → Rsync files to deployment path
3. ✅ **Set environment** → Add `DISABLE_RLS=true` to .env
4. ✅ **Rebuild Docker** → `docker-compose build --no-cache`
5. ✅ **Start services** → `docker-compose up -d`
6. ✅ **Verify** → Check container status and logs

**Downtime:** ~3-6 minutes

---

## What Gets Fixed

✅ **Empty Scan Results** → DISABLE_RLS=true  
✅ **Code Not Deploying** → Docker --no-cache rebuild  
✅ **SQL Server Support** → pymssql integration  
✅ **Netherlands Localization** → 100% complete (923 lines Dutch)  

---

## Files Included

**Total:** 22 files

- Core application (app.py)
- Scanner services (4 files) - DB, DPIA, Predictive, Intelligent
- Netherlands utils (6 files) - PII, UAVG, GDPR, i18n
- Translations (2 files) - Dutch 923 lines, English 344 lines
- Test scripts (5 files) - Patent claims, NL localization, SQL Server
- Configuration & docs (4+ files)

---

## Verification After Deployment

1. **Web App:** https://dataguardianpro.nl
2. **Database Scanner:** Test PostgreSQL, MySQL, SQL Server
3. **Dutch Language:** Switch to 🇳🇱 Nederlands
4. **Scan Activity:** Dashboard should show history
5. **Logs:** `docker-compose logs -f` (check for errors)

---

## Notes

⚠️ **No backup is created** - Make sure you have your own backup if needed  
✅ **Fast deployment** - No backup overhead  
✅ **Idempotent** - Can run multiple times safely  
✅ **No SCP** - Transfer files your preferred way  

---

**Version:** 1.0 (No Backup)  
**Date:** November 11, 2025  
**Status:** ✅ Ready to Deploy
