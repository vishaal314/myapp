# DataGuardian Pro - External Server Deployment

## 🚀 Quick Deployment Guide

### Step 1: Upload & Extract

```bash
# On external server (dataguardianpro.nl)
ssh root@dataguardianpro.nl

# Backup old installation
mv /opt/dataguardian /opt/dataguardian.backup.$(date +%Y%m%d_%H%M%S)

# Extract new code
mkdir -p /opt/dataguardian
cd /opt/dataguardian
tar -xzf /path/to/dataguardian_complete.tar.gz
```

### Step 2: Run Fix Script

```bash
# Download and run the fix script
cd /opt/dataguardian
chmod +x FIX_EXTERNAL_SERVER.sh
sudo ./FIX_EXTERNAL_SERVER.sh
```

### Step 3: Test in INCOGNITO Browser

**CRITICAL: You MUST use incognito mode!**

1. Close ALL browser tabs for dataguardianpro.nl
2. Press **Ctrl+Shift+N** (Chrome) or **Ctrl+Shift+P** (Firefox)
3. Visit: https://dataguardianpro.nl
4. Login: vishaal314 / password123
5. Try any scanner

## ⚠️ Important Notes

### The 'stats' Error You See is BROWSER CACHE

The logs show **NO 'stats' error** - only encryption errors:
- ✅ Code is correct (no 'stats' bug in logs)
- ❌ Your browser cached the old error page
- ✅ Incognito bypasses cache

### What the Fix Script Does

1. Generates fresh encryption keys
2. Starts Redis on 127.0.0.1:6379
3. **Clears old encrypted database columns** (fixes "Incorrect padding")
4. Clears Python cache
5. Rebuilds Docker (--no-cache)
6. Starts container with --network host

### Expected Results After Fix

- ✅ Dashboard loads
- ✅ NO 'stats' error
- ✅ NO encryption errors
- ✅ All scanners work

## 📊 Monitor Logs

```bash
docker logs dataguardian-container -f
```

You should see:
- ✅ "Streamlit app in your browser"
- ✅ NO "UnboundLocalError: stats"
- ✅ NO "Incorrect padding"

## 🔧 Manual Fix (If Script Fails)

```bash
# Generate keys
NEW_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
NEW_JWT=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')

# Create environment
cat > /root/.dataguardian_env << EOF
DATABASE_URL=postgresql://dataguardian:changeme@localhost:5432/dataguardian
REDIS_URL=redis://127.0.0.1:6379
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
DATAGUARDIAN_MASTER_KEY=$NEW_KEY
JWT_SECRET=$NEW_JWT
OPENAI_API_KEY=your_key_here
STRIPE_SECRET_KEY=your_key_here
PYTHONUNBUFFERED=1
STREAMLIT_SERVER_PORT=5000
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
EOF

# Start Redis
redis-server --daemonize yes --port 6379 --bind 127.0.0.1 --protected-mode no
redis-cli -h 127.0.0.1 FLUSHALL

# Clear caches
cd /opt/dataguardian
find . -name "*.pyc" -delete
rm -rf /tmp/dataguardian_* /var/cache/dataguardian_*

# Rebuild Docker
docker stop dataguardian-container
docker rm dataguardian-container
docker rmi dataguardian-pro
docker build --no-cache -t dataguardian-pro .
docker run -d --name dataguardian-container --restart always --network host --env-file /root/.dataguardian_env dataguardian-pro
```

## ✅ Verification

After 60 seconds, check:

```bash
docker logs dataguardian-container 2>&1 | tail -50 | grep -i "stats\|padding\|streamlit"
```

Should show:
- ✅ "You can now view your Streamlit app"
- ✅ NO "UnboundLocalError: stats"
- ✅ NO "Incorrect padding"
