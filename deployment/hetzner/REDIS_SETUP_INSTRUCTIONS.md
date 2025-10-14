# Redis Setup Instructions for External Server

## Quick Setup (3 Easy Steps)

### Step 1: Copy Script to Server
```bash
scp deployment/hetzner/SETUP_REDIS_EXTERNAL.sh root@45.81.35.202:/opt/dataguardian/
```

### Step 2: SSH to Server
```bash
ssh root@45.81.35.202
cd /opt/dataguardian
```

### Step 3: Run Setup Script
```bash
chmod +x SETUP_REDIS_EXTERNAL.sh
./SETUP_REDIS_EXTERNAL.sh
```

---

## Alternative: One-Line Remote Execution

Run this from your local machine (no need to SSH):

```bash
scp deployment/hetzner/SETUP_REDIS_EXTERNAL.sh root@45.81.35.202:/opt/dataguardian/ && ssh root@45.81.35.202 "cd /opt/dataguardian && chmod +x SETUP_REDIS_EXTERNAL.sh && ./SETUP_REDIS_EXTERNAL.sh"
```

---

## What the Script Does

1. ✅ Stops existing containers safely
2. ✅ Starts Redis container (port 6379)
3. ✅ Tests Redis connection with PING
4. ✅ Updates .env file with Redis URL
5. ✅ Restarts main container with Redis link
6. ✅ Verifies all services are running
7. ✅ Performs read/write test
8. ✅ Shows application logs

---

## Expected Output

You should see:
```
════════════════════════════════════════════════════════════════
🔴 Redis Setup for DataGuardian Pro External Server
════════════════════════════════════════════════════════════════

1️⃣  Stopping existing containers...
   ✅ Existing containers stopped

2️⃣  Starting Redis container...
   ✅ Redis container started successfully

3️⃣  Waiting for Redis to initialize...

4️⃣  Testing Redis connection...
   ✅ Redis connection successful: PONG

5️⃣  Updating .env configuration...
   ✅ Updated existing REDIS_URL in .env

6️⃣  Starting main container with Redis connection...
   ✅ Main container started with Redis link

7️⃣  Waiting for application startup (20 seconds)...

8️⃣  Verification & Status Check:

   Redis Container Status:
   ✅ Redis: Up 25 seconds

   Main Container Status:
   ✅ DataGuardian: Up 20 seconds

   Redis Connection Tests:
   - PING test: PONG
   - Redis version: 7.2.4
   - Number of keys: (integer) 1
   - Memory usage: 1.23M

   Redis Read/Write Test:
   ✅ Read/Write test successful: DataGuardian_Pro_Working

════════════════════════════════════════════════════════════════
✅ Redis Setup Complete!
════════════════════════════════════════════════════════════════
```

---

## Troubleshooting

### If Redis fails to start:
```bash
docker logs dataguardian-redis
```

### If main container fails:
```bash
docker logs dataguardian-container --tail 50
```

### Check Redis is working:
```bash
docker exec dataguardian-redis redis-cli ping
```

### View all containers:
```bash
docker ps -a
```

---

## Useful Redis Commands

### Monitor Redis in real-time:
```bash
docker exec -it dataguardian-redis redis-cli monitor
```

### Check Redis memory:
```bash
docker exec dataguardian-redis redis-cli info memory | grep used_memory_human
```

### Count keys:
```bash
docker exec dataguardian-redis redis-cli dbsize
```

### Set/Get test:
```bash
docker exec dataguardian-redis redis-cli set mykey "test value"
docker exec dataguardian-redis redis-cli get mykey
```

### Restart everything:
```bash
docker restart dataguardian-redis dataguardian-container
```
