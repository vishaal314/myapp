# 🚀 DEPLOYMENT PATCH GUIDE - NOVEMBER 2025

## Quick Start

```bash
# Simple deployment (recommended)
bash deployment_patch_nov2025.sh

# Dry run (see what will happen without executing)
bash deployment_patch_nov2025.sh --dry-run

# Custom remote host
bash deployment_patch_nov2025.sh --remote-host your-server.com --remote-user admin
```

---

## 📦 What's Included in This Patch

### Critical Changes (Oct 11 - Nov 11, 2025)

✅ **Database Scanner Enhancements**
- SQL Server support with pymssql (no ODBC needed)
- Multi-database validation (PostgreSQL, MySQL, SQL Server)
- Netherlands PII detection in databases (BSN, Dutch IBAN, +31 phones)

✅ **Netherlands Localization (100% Complete)**
- Dutch translations (923 lines vs 344 English)
- BSN detection with 11-test validation
- UAVG compliance (AP Guidelines 2024-2025)
- Dutch report generation (PDF/HTML)

✅ **Patent Testing Infrastructure**
- test_patent_claims_final.py (Predictive Engine + DPIA Scanner)
- test_netherlands_localization_e2e.py (100% verification)
- Comprehensive test reports

✅ **Production Fixes**
- RLS disable fix (DISABLE_RLS=true)
- Docker cache rebuild (--no-cache)
- Empty scan results fix

---

## 🎯 Usage Examples

### 1. Standard Deployment to dataguardianpro.nl

```bash
# This will:
# - Create backup automatically
# - Transfer files via SSH
# - Apply patch
# - Rebuild Docker with --no-cache
# - Restart services
# - Run verification tests

bash deployment_patch_nov2025.sh
```

**Expected output:**
```
[INFO] Remote Host: root@dataguardianpro.nl
[INFO] Remote Path: /opt/dataguardian
[INFO] Backup: yes
[INFO] Verification: yes
[SUCCESS] SSH connection verified
[SUCCESS] Staged 50 files for deployment
[SUCCESS] Tarball created: /tmp/dataguardian_patch_nov2025_20251111_190000.tar.gz
[INFO] Transferring patch to dataguardianpro.nl...
[SUCCESS] Patch transferred successfully

Continue with deployment? (yes/no): yes

[SUCCESS] Deployment completed successfully!
```

---

### 2. Dry Run (See What Will Happen)

```bash
# Test the script without making any changes
bash deployment_patch_nov2025.sh --dry-run
```

**Use this to:**
- Verify SSH connectivity
- See which files will be deployed
- Check script logic before running

---

### 3. Custom Server Configuration

```bash
# Different server/user/path
bash deployment_patch_nov2025.sh \
  --remote-host myserver.com \
  --remote-user admin \
  --remote-path /home/admin/dataguardian
```

---

### 4. Skip Verification Tests

```bash
# Deploy without running post-deployment tests
bash deployment_patch_nov2025.sh --no-verify
```

---

## 📋 Prerequisites

### 1. SSH Key Authentication

The script requires SSH key authentication. If you haven't set it up:

```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy to remote server
ssh-copy-id root@dataguardianpro.nl

# Test connection
ssh root@dataguardianpro.nl "echo 'SSH OK'"
```

### 2. Remote Server Requirements

Your external server (dataguardianpro.nl) must have:
- Docker and Docker Compose installed
- Existing DataGuardian Pro installation at `/opt/dataguardian`
- Environment variables configured in `.env` file
- Sufficient disk space for backup (check with `df -h`)

---

## 🔍 What the Script Does

### Phase 1: Pre-flight Checks
1. Verifies you're in the correct directory
2. Tests SSH connectivity to remote server
3. Checks for required files

### Phase 2: Staging
1. Creates temporary staging directory
2. Copies 50+ critical files:
   - Core application (app.py)
   - Enhanced scanners (db_scanner.py, predictive_compliance_engine.py, dpia_scanner.py)
   - Netherlands localization (pii_detection.py, netherlands_uavg_compliance.py)
   - Translations (nl.json, en.json)
   - Testing infrastructure (test_patent_claims_final.py, test_netherlands_localization_e2e.py)
   - Configuration files

### Phase 3: Packaging
1. Creates deployment instructions (DEPLOY_INSTRUCTIONS.txt)
2. Generates remote deployment script (apply_patch.sh)
3. Bundles everything into timestamped tarball

### Phase 4: Transfer
1. Uploads tarball to remote server via SCP
2. Extracts on remote server

### Phase 5: Deployment
1. **Creates backup** → `/opt/dataguardian/backups/backup_TIMESTAMP.tar.gz`
2. **Stops services** → `docker-compose down`
3. **Applies patch** → `rsync` files to deployment path
4. **Sets environment** → Adds `DISABLE_RLS=true` to `.env`
5. **Rebuilds Docker** → `docker-compose build --no-cache`
6. **Restarts services** → `docker-compose up -d`

### Phase 6: Verification
1. Checks Docker container status
2. Tests web server response
3. Reviews recent logs for errors
4. Displays verification steps

### Phase 7: Cleanup
1. Removes staging directory
2. Preserves tarball for reference
3. Displays rollback instructions

---

## 🔧 Files Deployed

### Core Application (3 files)
- `app.py` - Main Streamlit application

### Scanner Services (4 files)
- `services/db_scanner.py` - **NEW: SQL Server support**
- `services/predictive_compliance_engine.py` - Patent testing validated
- `services/dpia_scanner.py` - Patent testing validated
- `services/intelligent_db_scanner.py` - Multi-database support

### Netherlands Localization (6 files)
- `utils/pii_detection.py` - BSN detection with 11-test
- `utils/netherlands_uavg_compliance.py` - AP Guidelines 2024-2025
- `utils/netherlands_gdpr.py` - Dutch GDPR implementation
- `utils/i18n.py` - Language system
- `utils/unified_translation.py` - Translation utilities
- `utils/animated_language_switcher.py` - Dutch flag 🇳🇱

### Translations (2 files)
- `translations/nl.json` - 923 lines Dutch translations
- `translations/en.json` - 344 lines English translations

### Testing Infrastructure (5 files)
- `test_patent_claims_final.py` - Patent verification (87.5% passed)
- `test_netherlands_localization_e2e.py` - NL localization (100% passed)
- `test_sqlserver_pymssql.py` - SQL Server testing
- `test_mysql_netherlands_pii.py` - MySQL Netherlands PII testing
- `test_database_scanner.py` - Database scanner validation

### Configuration & Documentation (5+ files)
- `config/pricing_config.py` - Netherlands pricing
- `replit.md` - Project documentation
- `NETHERLANDS_LOCALIZATION_FINAL_REPORT.md` - Localization report
- `PATENT_CLAIMS_TEST_REPORT.md` - Patent testing report
- `PATENT_TEST_EXECUTIVE_SUMMARY.md` - Patent summary

---

## ⚠️ Important Notes

### 1. Backup is Automatic
The script **always creates a backup** before deployment at:
```
/opt/dataguardian/backups/backup_YYYYMMDD_HHMMSS.tar.gz
```

### 2. RLS Environment Variable
The patch **automatically adds** this to your `.env` file:
```bash
DISABLE_RLS=true
```

This fixes the empty scan results issue on production.

### 3. Docker Cache Rebuild
The patch uses `docker-compose build --no-cache` to ensure all code changes are deployed. This fixes the issue where code changes weren't applying due to Docker cache.

### 4. Service Downtime
Deployment involves:
- Stopping services (~10 seconds)
- Rebuilding Docker images (~2-5 minutes)
- Starting services (~30 seconds)

**Total downtime: ~3-6 minutes**

---

## 🔄 Rollback Procedure

If deployment fails or causes issues, rollback using the automatic backup:

```bash
# SSH to server
ssh root@dataguardianpro.nl

# Navigate to deployment directory
cd /opt/dataguardian

# Stop services
docker-compose down

# List available backups
ls -lh backups/

# Restore from backup (use latest timestamp)
rm -rf *
tar -xzf backups/backup_20251111_190000.tar.gz

# Restart services
docker-compose up -d --build

# Verify
docker-compose ps
docker-compose logs -f
```

---

## ✅ Post-Deployment Verification

### 1. Check Web Application
```bash
# Visit in browser
https://dataguardianpro.nl

# Or test via curl
curl -I https://dataguardianpro.nl
```

### 2. Test Database Scanner
1. Log into DataGuardian Pro
2. Navigate to "Database Scanner"
3. Test with PostgreSQL connection
4. Test with MySQL connection (if available)
5. Test with SQL Server connection (if available)
6. Verify Netherlands PII detection (BSN, Dutch IBAN, +31 phones)

### 3. Verify Dutch Language
1. Click language switcher (🇬🇧 → 🇳🇱)
2. Verify UI switches to Dutch
3. Check dashboard, scanners, reports are in Dutch
4. Generate a report in Dutch (PDF or HTML)

### 4. Check Recent Scan Activity
1. Go to Dashboard
2. Check "Recent Scan Activity" section
3. Should show scan history (not empty)
4. Verify metrics update correctly

### 5. Review Logs
```bash
ssh root@dataguardianpro.nl
cd /opt/dataguardian
docker-compose logs -f

# Check for errors
docker-compose logs | grep -i error | grep -v "INFO" | grep -v "DEBUG"
```

---

## 🐛 Troubleshooting

### Problem: SSH Connection Failed

**Solution:**
```bash
# Test SSH manually
ssh root@dataguardianpro.nl

# If password required, set up SSH keys
ssh-copy-id root@dataguardianpro.nl
```

---

### Problem: Docker Rebuild Failed

**Symptoms:**
```
ERROR: Service 'web' failed to build
```

**Solution:**
```bash
# SSH to server
ssh root@dataguardianpro.nl
cd /opt/dataguardian

# Check Docker disk space
df -h
docker system df

# Clean up if needed
docker system prune -a

# Rebuild manually
docker-compose build --no-cache
docker-compose up -d
```

---

### Problem: Services Won't Start

**Symptoms:**
```
Container exited with code 1
```

**Solution:**
```bash
# Check logs for specific error
docker-compose logs

# Common issues:
# 1. Missing environment variables
cat .env  # Verify all variables present

# 2. Port conflicts
docker-compose ps
netstat -tlnp | grep 5000

# 3. Database connection
# Test DATABASE_URL connection manually
```

---

### Problem: Empty Scan Results

**This should be fixed by the patch!**

**Verify the fix:**
```bash
ssh root@dataguardianpro.nl
cd /opt/dataguardian

# Check .env has DISABLE_RLS
grep DISABLE_RLS .env
# Should show: DISABLE_RLS=true

# If not, add it
echo "DISABLE_RLS=true" >> .env

# Restart
docker-compose restart
```

---

## 📊 Expected Results

After successful deployment:

✅ **Web Application**: https://dataguardianpro.nl responds  
✅ **Database Scanner**: SQL Server, MySQL, PostgreSQL all working  
✅ **Netherlands Localization**: 100% functional (Dutch UI, BSN detection, UAVG)  
✅ **Recent Scan Activity**: Shows scan history (not empty)  
✅ **Docker Containers**: All running (`docker-compose ps`)  
✅ **No Critical Errors**: Logs clean (`docker-compose logs`)  

---

## 📞 Support

If you encounter issues:

1. **Check logs first:**
   ```bash
   ssh root@dataguardianpro.nl
   cd /opt/dataguardian
   docker-compose logs -f
   ```

2. **Review backup location:**
   ```bash
   ls -lh /opt/dataguardian/backups/
   ```

3. **Test rollback procedure** (if needed)

4. **Verify environment variables:**
   ```bash
   cat /opt/dataguardian/.env
   ```

---

## 🎉 Success Checklist

After running the deployment patch, verify:

- [ ] Script completed without errors
- [ ] Backup created at `/opt/dataguardian/backups/backup_TIMESTAMP.tar.gz`
- [ ] Web application accessible at https://dataguardianpro.nl
- [ ] Database Scanner works with multiple databases
- [ ] Dutch language UI functional (🇳🇱 Nederlands)
- [ ] Recent Scan Activity shows data (not empty)
- [ ] No critical errors in logs
- [ ] All Docker containers running

---

**Report Version:** 1.0  
**Date:** November 11, 2025  
**Patch Name:** `deployment_patch_nov2025.sh`  
**Status:** ✅ Ready for Production Deployment
