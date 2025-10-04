# 🚀 COMPLETE END-TO-END FIX FOR DATAGUARDIANPRO.NL

## Problem Summary
- External server at dataguardianpro.nl has outdated code
- Encryption errors due to old keys
- Login failing due to missing user_id field
- PostgreSQL may not be running

---

## ✅ COMPLETE MANUAL FIX STEPS

### STEP 1: Download Latest Package

From Replit Files panel:
- Download `dataguardian_complete.tar.gz` (1.1 MB)

---

### STEP 2: Upload to Server

From your local machine:

```bash
scp dataguardian_complete.tar.gz root@dataguardianpro.nl:/tmp/
```

---

### STEP 3: SSH into Server

```bash
ssh root@dataguardianpro.nl
```

---

### STEP 4: Stop Current Container

```bash
docker stop dataguardian-container
docker rm dataguardian-container
```

---

### STEP 5: Backup Old Code

```bash
mv /opt/dataguardian /opt/dataguardian.backup.$(date +%Y%m%d_%H%M%S)
```

---

### STEP 6: Extract New Code

```bash
mkdir -p /opt/dataguardian
cd /opt/dataguardian
tar -xzf /tmp/dataguardian_complete.tar.gz
```

Verify extraction:
```bash
ls -la | head -20
```

Should see: app.py, Dockerfile, services/, components/, etc.

---

### STEP 7: Generate Fresh Environment Keys

```bash
# Generate encryption key
NEW_MASTER_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')

# Generate JWT secret
NEW_JWT_SECRET=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')

echo "Keys generated successfully"
```

---

### STEP 8: Create Environment File

```bash
cat > /root/.dataguardian_env << 'EOF'
DATABASE_URL=postgresql://dataguardian:changeme@localhost:5432/dataguardian
REDIS_URL=redis://127.0.0.1:6379
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
PYTHONUNBUFFERED=1
STREAMLIT_SERVER_PORT=5000
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
EOF

# Add the generated keys
echo "DATAGUARDIAN_MASTER_KEY=$NEW_MASTER_KEY" >> /root/.dataguardian_env
echo "JWT_SECRET=$NEW_JWT_SECRET" >> /root/.dataguardian_env
```

**If you have API keys, add them:**
```bash
echo "OPENAI_API_KEY=your-openai-key" >> /root/.dataguardian_env
echo "STRIPE_SECRET_KEY=your-stripe-key" >> /root/.dataguardian_env
```

---

### STEP 9: Start PostgreSQL (if not running)

Check if running:
```bash
systemctl status postgresql
```

If not running:
```bash
systemctl start postgresql
systemctl enable postgresql
```

Create database and user:
```bash
sudo -u postgres psql << 'SQL'
CREATE USER dataguardian WITH PASSWORD 'changeme';
CREATE DATABASE dataguardian OWNER dataguardian;
GRANT ALL PRIVILEGES ON DATABASE dataguardian TO dataguardian;
SQL
```

---

### STEP 10: Start Redis

```bash
# Stop any existing Redis
pkill redis-server 2>/dev/null || true

# Start Redis
redis-server --daemonize yes --port 6379 --bind 127.0.0.1 --protected-mode no

# Verify
redis-cli -h 127.0.0.1 PING
```

Should return: `PONG`

---

### STEP 11: Clear Python Cache

```bash
cd /opt/dataguardian
find . -name "*.pyc" -delete
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
```

---

### STEP 12: Build Docker Image

```bash
cd /opt/dataguardian
docker build --no-cache -t dataguardian-pro .
```

**Wait 60-90 seconds for build to complete.**

Verify:
```bash
docker images | grep dataguardian-pro
```

---

### STEP 13: Start Container

```bash
docker run -d \
    --name dataguardian-container \
    --restart always \
    --network host \
    --env-file /root/.dataguardian_env \
    dataguardian-pro
```

---

### STEP 14: Wait for Initialization

```bash
sleep 30
```

Check container is running:
```bash
docker ps | grep dataguardian
```

---

### STEP 15: Check Logs for Errors

```bash
docker logs dataguardian-container 2>&1 | tail -50
```

Look for:
- ✅ "You can now view your Streamlit app"
- ❌ NO "Incorrect padding" errors
- ❌ NO "user_id" errors

---

### STEP 16: Fix User File in Container

The secure_users.json in the package has the correct format. Verify it's in the container:

```bash
docker exec dataguardian-container cat /app/secure_users.json
```

Should show vishaal314 with user_id, username, password_hash, etc.

If missing or wrong, copy the correct one:
```bash
docker cp /opt/dataguardian/secure_users.json dataguardian-container:/app/secure_users.json
docker restart dataguardian-container
sleep 30
```

---

### STEP 17: Final Verification

```bash
# Check container status
docker ps | grep dataguardian

# Check for errors
docker logs dataguardian-container 2>&1 | grep -i "error\|keyerror\|padding" | tail -20

# If no output = good!
```

---

## 🧪 TEST LOGIN

### 1. Close ALL Browser Tabs
Close every tab for dataguardianpro.nl

### 2. Open Incognito Mode
- Chrome/Edge: Press **Ctrl+Shift+N**
- Firefox: Press **Ctrl+Shift+P**

### 3. Visit Website
```
https://dataguardianpro.nl
```

### 4. Login
- Username: **vishaal314**
- Password: **vishaal2024**

### 5. Expected Result
✅ Login successful
✅ Dashboard loads
✅ NO "safe mode" error
✅ NO "user_id" error
✅ All scanners available

---

## 🔧 TROUBLESHOOTING

### Issue: Container won't start

Check logs:
```bash
docker logs dataguardian-container
```

### Issue: "Incorrect padding" error

Environment key problem:
```bash
# Check environment
cat /root/.dataguardian_env | grep DATAGUARDIAN_MASTER_KEY

# Should be 43-44 characters
```

### Issue: "user_id" KeyError

secure_users.json missing field:
```bash
docker exec dataguardian-container python3 << 'PYTHON'
import json
with open('/app/secure_users.json') as f:
    users = json.load(f)
    print(json.dumps(users, indent=2))
PYTHON
```

Should show user_id field. If not, recopy the file.

### Issue: Can't connect to PostgreSQL

```bash
systemctl status postgresql
PGPASSWORD='changeme' psql -h localhost -U dataguardian -d dataguardian -c "SELECT 1;"
```

### Issue: Redis not responding

```bash
redis-cli -h 127.0.0.1 PING
# Should return PONG
```

---

## 📊 EXPECTED FINAL STATE

✅ PostgreSQL running on localhost:5432
✅ Redis running on 127.0.0.1:6379  
✅ Docker container running
✅ Environment variables set
✅ secure_users.json with complete user structure
✅ No encryption errors
✅ Login working
✅ All scanners available

---

## 🎯 QUICK HEALTH CHECK

```bash
# All should return OK
echo "1. Container:" && docker ps | grep dataguardian && echo "OK" || echo "FAIL"
echo "2. PostgreSQL:" && systemctl is-active postgresql && echo "OK" || echo "FAIL"  
echo "3. Redis:" && redis-cli -h 127.0.0.1 PING && echo "OK" || echo "FAIL"
echo "4. App:" && curl -s http://localhost:5000 | grep -q "streamlit" && echo "OK" || echo "FAIL"
```

All should show "OK"

---

## 📝 SUMMARY

1. Upload package → `/tmp/dataguardian_complete.tar.gz`
2. Extract → `/opt/dataguardian`
3. Create environment → `/root/.dataguardian_env`
4. Start services → PostgreSQL, Redis
5. Build Docker → `docker build`
6. Run container → `docker run`
7. Verify user file → `secure_users.json`
8. Test login → Incognito browser

**Total time: 5-10 minutes**
