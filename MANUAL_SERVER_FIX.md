# Manual Fix for Syntax Error

## Issue Found

**Syntax Error in app.py line 2158:**
```python
'blob': ,  # ❌ BROKEN - value removed but key remains
```

This was caused by the blob removal script leaving incomplete dictionary entries.

---

## ✅ Fixed in Replit

I've already fixed the syntax errors in the Replit version of app.py:
- ✅ Removed `'blob': 'Blob Scanner',` from line 2159
- ✅ Removed `'blob': '📄 Blob Scanner',` from line 2325

---

## 🔧 Apply Fix to Server (3 Options)

### **Option 1: Automated Script (Recommended)**

Run this from your **local machine** (where you have Replit files):

```bash
chmod +x FIX_SYNTAX_ERROR.sh
./FIX_SYNTAX_ERROR.sh
```

This will automatically:
1. Copy fixed app.py to server
2. Rebuild Docker container
3. Start with updated code

---

### **Option 2: Manual SCP + Rebuild**

**Step 1: Copy fixed app.py to server**
```bash
# From local machine (in Replit directory)
scp app.py root@dataguardianpro.nl:/opt/dataguardian/
```

**Step 2: SSH to server and rebuild**
```bash
ssh root@dataguardianpro.nl

cd /opt/dataguardian

# Stop old container
docker stop dataguardian-container
docker rm dataguardian-container

# Rebuild with no cache
docker build --no-cache -t dataguardian:latest .

# Start new container
docker run -d \
  --name dataguardian-container \
  --env-file /root/.dataguardian_env \
  -p 5000:5000 \
  --health-cmd="curl -f http://localhost:5000 || exit 1" \
  --health-interval=30s \
  dataguardian:latest

# Wait and check
sleep 30
docker ps
docker logs --tail 50 dataguardian-container
```

---

### **Option 3: Direct Edit on Server**

**SSH to server:**
```bash
ssh root@dataguardianpro.nl
cd /opt/dataguardian
```

**Edit app.py:**
```bash
nano app.py
```

**Find line 2159 (Ctrl+_  then type 2159):**
Remove this line:
```python
'blob': 'Blob Scanner',  # ❌ DELETE THIS ENTIRE LINE
```

**Find line 2325:**
Remove this line:
```python
'blob': '📄 Blob Scanner',  # ❌ DELETE THIS ENTIRE LINE
```

**Save:** Ctrl+X, then Y, then Enter

**Rebuild container:**
```bash
docker stop dataguardian-container
docker rm dataguardian-container
docker build --no-cache -t dataguardian:latest .
docker run -d --name dataguardian-container --env-file /root/.dataguardian_env -p 5000:5000 dataguardian:latest
```

---

## ✅ Verification

After rebuild:

**1. Check container logs:**
```bash
docker logs dataguardian-container
```

**Should see:**
```
You can now view your Streamlit app in your browser.
URL: http://0.0.0.0:5000
```

**Should NOT see:**
```
SyntaxError: expression expected after dictionary key and ':'
```

**2. Test payment page:**
Visit: https://dataguardianpro.nl/payment_test_ideal

**3. Hard refresh:**
Press Ctrl+Shift+R

**4. Expected results:**
- ✅ NO syntax errors
- ✅ 16 scanners in dropdown
- ✅ NO "Blob Scan - €14.00"
- ✅ NO STRIPE_SECRET_KEY error

---

## Summary

**Root Cause:**
The STANDALONE_FIX.sh script removed blob values but left dictionary keys, creating invalid Python syntax.

**Solution:**
Fixed app.py in Replit (removed blob entries completely). Now need to copy fixed file to server and rebuild container.

**Fastest Method:**
Use Option 1 (automated script) or Option 2 (manual SCP + rebuild).
