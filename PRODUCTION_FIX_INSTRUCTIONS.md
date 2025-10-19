# Production Fix Instructions - dataguardianpro.nl

## Issues Being Fixed

1. ❌ **Blob Scan still appearing** in payment dropdown (should be 16 scanners, not 17)
2. ❌ **STRIPE_SECRET_KEY environment variable not set** error on payment page

---

## Quick Fix (5 minutes)

### Step 1: Copy Script to Server

On your **local machine**, copy the fix script to the server:

```bash
scp COMPLETE_PRODUCTION_FIX.sh root@dataguardianpro.nl:/opt/dataguardian/
```

### Step 2: SSH to Server

```bash
ssh root@dataguardianpro.nl
```

### Step 3: Navigate to Directory

```bash
cd /opt/dataguardian
```

### Step 4: Make Script Executable

```bash
chmod +x COMPLETE_PRODUCTION_FIX.sh
```

### Step 5: Run the Fix Script

```bash
./COMPLETE_PRODUCTION_FIX.sh
```

---

## What the Script Does

### Phase 1: Environment Variable Check
- ✅ Verifies `/root/.dataguardian_env` exists
- ✅ Checks if `STRIPE_SECRET_KEY` is set
- ⚠️ **If missing, script will STOP and ask you to add it**

### Phase 2: Blob Scan Removal
- ✅ Updates `services/stripe_payment.py` to exactly 16 scanners
- ✅ Removes ALL blob references from `app.py`

### Phase 3: Verification
- ✅ Confirms exactly 16 scanners
- ✅ Confirms no blob references remain

### Phase 4: Docker Rebuild
- ✅ Stops containers
- ✅ Clears Docker build cache completely
- ✅ Rebuilds with `--no-cache` flag
- ✅ Restarts all containers

### Phase 5: Final Checks
- ✅ Verifies web server is responding
- ✅ Shows container status

---

## If Script Asks for API Keys

If the script stops and asks for `STRIPE_SECRET_KEY`:

### Edit Environment File:
```bash
nano /root/.dataguardian_env
```

### Add This Line:
```bash
STRIPE_SECRET_KEY=sk_test_YOUR_ACTUAL_KEY_HERE
```

**Get your Stripe key from:** https://dashboard.stripe.com/test/apikeys

### Save and Exit:
- Press `Ctrl+X`
- Press `Y`
- Press `Enter`

### Run Script Again:
```bash
./COMPLETE_PRODUCTION_FIX.sh
```

---

## Expected Output

```
==========================================
COMPLETE PRODUCTION FIX
dataguardianpro.nl
==========================================

📁 Working directory: /opt/dataguardian

==========================================
PHASE 1: Fix Environment Variables
==========================================

✅ STRIPE_SECRET_KEY found (sk_test_...)
✅ OPENAI_API_KEY found (sk-...)

==========================================
PHASE 2: Remove Blob Scan (16 scanners only)
==========================================

🔧 Fixing services/stripe_payment.py...
✅ stripe_payment.py: 16 scanners only
🔧 Removing ALL blob references from app.py...
✅ app.py: Removed 8 lines containing blob references

==========================================
PHASE 3: Verification
==========================================

📊 Scanners: 16 (expected: 16)
✅ All blob references removed
✅ Exactly 16 scanners

==========================================
PHASE 4: Docker Rebuild (with environment)
==========================================

📄 Using compose file: docker-compose.yml
🛑 Stopping containers...
🗑️  Clearing Docker build cache...
🔨 Rebuilding (no cache)...
🚀 Starting containers...
⏳ Waiting for services to start...

📊 Container status:
NAMES                   STATUS          PORTS
dataguardian-pro        Up 5 seconds    0.0.0.0:5000->5000/tcp
dataguardian-redis      Up 5 seconds    6379/tcp
dataguardian-postgres   Up 5 seconds    5432/tcp

==========================================
PHASE 5: Final Verification
==========================================

🌐 Testing web server...
✅ Web server responding (HTTP 200)

==========================================
✅ COMPLETE - ALL FIXES APPLIED
==========================================

Summary:
  ✅ STRIPE_SECRET_KEY configured
  ✅ 16 scanners (blob removed)
  ✅ Docker rebuilt with cache clear
  ✅ All containers restarted

Next Steps:

1. Test payment page:
   https://dataguardianpro.nl/payment_test_ideal

2. Hard refresh browser:
   Press Ctrl+Shift+R

3. Check logs if needed:
   docker logs dataguardian-pro
```

---

## Testing After Fix

### 1. Test Payment Page
Visit: https://dataguardianpro.nl/payment_test_ideal

**Expected Results:**
- ✅ NO error about `STRIPE_SECRET_KEY`
- ✅ Dropdown shows exactly **16 scanners** (no Blob Scan)
- ✅ Scanners with correct prices:
  - Code Scan - €23.00 + €4.83 VAT = €27.83
  - Image Scan - €28.00 + €5.88 VAT = €33.88
  - Database Scan - €46.00 + €9.66 VAT = €55.66
  - (NO Blob Scan €14.00)

### 2. Hard Refresh Browser
Press **Ctrl+Shift+R** to clear browser cache

### 3. Check Logs (if needed)
```bash
# View live logs
docker logs -f dataguardian-pro

# Check last 100 lines
docker logs --tail 100 dataguardian-pro

# Check for errors
docker logs dataguardian-pro 2>&1 | grep -i error
```

---

## Troubleshooting

### Issue: Script fails with "permission denied"
```bash
chmod +x COMPLETE_PRODUCTION_FIX.sh
```

### Issue: "STRIPE_SECRET_KEY not set"
1. Edit `/root/.dataguardian_env`
2. Add: `STRIPE_SECRET_KEY=sk_test_...`
3. Run script again

### Issue: Docker containers not starting
```bash
# Check container logs
docker logs dataguardian-pro

# Restart manually
docker-compose down
docker-compose up -d
```

### Issue: Still seeing Blob Scan after fix
1. Hard refresh browser: `Ctrl+Shift+R`
2. Clear browser cache completely
3. Try incognito/private browsing mode
4. Check logs: `docker logs dataguardian-pro`

---

## Manual Verification Commands

### Check scanners in stripe_payment.py:
```bash
grep -A 30 "SCAN_PRICES = {" services/stripe_payment.py | grep -c '":"'
# Should output: 16
```

### Check for blob references:
```bash
grep -i "blob" app.py | grep -i "scan\|document"
# Should output nothing
```

### Check environment variables:
```bash
cat /root/.dataguardian_env | grep STRIPE_SECRET_KEY
# Should show: STRIPE_SECRET_KEY=sk_test_...
```

---

## Success Criteria

✅ Payment page loads without STRIPE_SECRET_KEY error  
✅ Dropdown shows exactly 16 scanners  
✅ NO "Blob Scan" in the list  
✅ All prices calculated correctly with 21% VAT  
✅ Docker containers running stably  

---

## Support

If issues persist after running the script:

1. **Check Docker logs:**
   ```bash
   docker logs dataguardian-pro
   ```

2. **Verify environment file:**
   ```bash
   cat /root/.dataguardian_env
   ```

3. **Restart containers manually:**
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```
