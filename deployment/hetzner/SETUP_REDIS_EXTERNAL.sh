#!/bin/bash
# SETUP_REDIS_EXTERNAL.sh
# Redis Setup Script for External Server (dataguardianpro.nl)
# 
# Usage: 
#   1. Copy this file to your external server: scp SETUP_REDIS_EXTERNAL.sh root@45.81.35.202:/opt/dataguardian/
#   2. SSH to server: ssh root@45.81.35.202
#   3. Run: cd /opt/dataguardian && chmod +x SETUP_REDIS_EXTERNAL.sh && ./SETUP_REDIS_EXTERNAL.sh

set -e  # Exit on error

echo "════════════════════════════════════════════════════════════════"
echo "🔴 Redis Setup for DataGuardian Pro External Server"
echo "   Server: dataguardianpro.nl (45.81.35.202)"
echo "   Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "════════════════════════════════════════════════════════════════"

# Change to application directory
cd /opt/dataguardian || { echo "❌ Error: /opt/dataguardian directory not found"; exit 1; }

# 1. Stop existing containers
echo ""
echo "1️⃣  Stopping existing containers..."
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true
docker stop dataguardian-redis 2>/dev/null || true
docker rm dataguardian-redis 2>/dev/null || true
echo "   ✅ Existing containers stopped"

# 2. Start Redis container
echo ""
echo "2️⃣  Starting Redis container..."
docker run -d \
  --name dataguardian-redis \
  --restart unless-stopped \
  -p 6379:6379 \
  redis:7-alpine redis-server --appendonly yes --bind 0.0.0.0

if [ $? -eq 0 ]; then
    echo "   ✅ Redis container started successfully"
else
    echo "   ❌ Error: Failed to start Redis container"
    exit 1
fi

# 3. Wait for Redis to be ready
echo ""
echo "3️⃣  Waiting for Redis to initialize..."
sleep 5

# 4. Test Redis connection
echo ""
echo "4️⃣  Testing Redis connection..."
REDIS_PING=$(docker exec dataguardian-redis redis-cli ping 2>/dev/null)
if [ "$REDIS_PING" == "PONG" ]; then
    echo "   ✅ Redis connection successful: $REDIS_PING"
else
    echo "   ❌ Error: Redis connection failed"
    exit 1
fi

# 5. Update .env file with Redis URL
echo ""
echo "5️⃣  Updating .env configuration..."
if [ -f .env ]; then
    if grep -q "^REDIS_URL=" .env; then
        sed -i 's|^REDIS_URL=.*|REDIS_URL=redis://dataguardian-redis:6379/0|' .env
        echo "   ✅ Updated existing REDIS_URL in .env"
    else
        echo "REDIS_URL=redis://dataguardian-redis:6379/0" >> .env
        echo "   ✅ Added REDIS_URL to .env"
    fi
else
    echo "   ⚠️  Warning: .env file not found, skipping Redis URL configuration"
fi

# 6. Restart main container with Redis link
echo ""
echo "6️⃣  Starting main container with Redis connection..."
docker run -d \
  --name dataguardian-container \
  --env-file .env \
  -p 5000:5000 \
  --cpus="1.5" \
  --memory="2g" \
  --link dataguardian-redis:redis \
  --restart unless-stopped \
  dataguardian:latest

if [ $? -eq 0 ]; then
    echo "   ✅ Main container started with Redis link"
else
    echo "   ❌ Error: Failed to start main container"
    exit 1
fi

# 7. Wait for application startup
echo ""
echo "7️⃣  Waiting for application startup (20 seconds)..."
sleep 20

# 8. Comprehensive verification
echo ""
echo "8️⃣  Verification & Status Check:"
echo ""
echo "   Redis Container Status:"
REDIS_STATUS=$(docker ps --filter "name=dataguardian-redis" --format "{{.Status}}" 2>/dev/null)
if [ -n "$REDIS_STATUS" ]; then
    echo "   ✅ Redis: $REDIS_STATUS"
else
    echo "   ❌ Redis: Not running"
fi

echo ""
echo "   Main Container Status:"
MAIN_STATUS=$(docker ps --filter "name=dataguardian-container" --format "{{.Status}}" 2>/dev/null)
if [ -n "$MAIN_STATUS" ]; then
    echo "   ✅ DataGuardian: $MAIN_STATUS"
else
    echo "   ❌ DataGuardian: Not running"
fi

echo ""
echo "   Redis Connection Tests:"
echo -n "   - PING test: "
docker exec dataguardian-redis redis-cli ping 2>/dev/null

echo -n "   - Redis version: "
docker exec dataguardian-redis redis-cli info server 2>/dev/null | grep redis_version | cut -d: -f2

echo -n "   - Number of keys: "
docker exec dataguardian-redis redis-cli dbsize 2>/dev/null

echo -n "   - Memory usage: "
docker exec dataguardian-redis redis-cli info memory 2>/dev/null | grep used_memory_human | cut -d: -f2

# 9. Quick read/write test
echo ""
echo "   Redis Read/Write Test:"
docker exec dataguardian-redis redis-cli set test_key "DataGuardian_Pro_Working" EX 60 > /dev/null 2>&1
TEST_VALUE=$(docker exec dataguardian-redis redis-cli get test_key 2>/dev/null)
if [ "$TEST_VALUE" == "DataGuardian_Pro_Working" ]; then
    echo "   ✅ Read/Write test successful: $TEST_VALUE"
else
    echo "   ❌ Read/Write test failed"
fi

# 10. Show recent application logs
echo ""
echo "   Recent Application Logs (last 10 lines):"
echo "   ────────────────────────────────────────"
docker logs dataguardian-container --tail 10 2>/dev/null | sed 's/^/   /'

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ Redis Setup Complete!"
echo ""
echo "📊 Summary:"
echo "   - Redis container: dataguardian-redis (port 6379)"
echo "   - Main container: dataguardian-container (port 5000)"
echo "   - Application URL: https://dataguardianpro.nl"
echo ""
echo "🔍 Useful Commands:"
echo "   - Check Redis: docker exec dataguardian-redis redis-cli ping"
echo "   - Monitor Redis: docker exec -it dataguardian-redis redis-cli monitor"
echo "   - View logs: docker logs dataguardian-container --tail 50"
echo "   - Restart all: docker restart dataguardian-redis dataguardian-container"
echo "════════════════════════════════════════════════════════════════"
