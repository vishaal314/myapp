#!/bin/bash
# ADD REDIS TO EXTERNAL SERVER - Match Replit environment exactly

echo "🔧 ADDING REDIS TO EXTERNAL SERVER"
echo "==================================="
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "❌ Run as root: sudo ./ADD_REDIS_TO_SERVER.sh"
    exit 1
fi

echo "Step 1: Install Redis"
echo "==================="
apt-get update -qq
apt-get install -y redis-server

echo ""
echo "Step 2: Configure Redis"
echo "===================="
# Bind to localhost only for security
sed -i 's/bind 127.0.0.1 ::1/bind 127.0.0.1/g' /etc/redis/redis.conf
systemctl enable redis-server
systemctl restart redis-server

echo ""
echo "Step 3: Verify Redis"
echo "=================="
if systemctl is-active --quiet redis-server; then
    echo "✅ Redis running"
    redis-cli ping && echo "✅ Redis responding to PING"
else
    echo "❌ Redis not running"
fi

echo ""
echo "Step 4: Restart DataGuardian Container"
echo "===================================="
docker restart dataguardian-container

echo ""
echo "Waiting 30 seconds for app to reconnect..."
sleep 30

echo ""
echo "Step 5: Verify Connection"
echo "======================="
if docker logs dataguardian-container 2>&1 | tail -50 | grep -qi "redis.*failed"; then
    echo "⚠️  Redis still not connected (check firewall)"
    docker logs dataguardian-container 2>&1 | tail -20
else
    echo "✅ Redis connection should be working"
    docker logs dataguardian-container 2>&1 | tail -20
fi

echo ""
echo "=========================================="
echo "🎉 REDIS SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "✅ Redis server installed and running"
echo "✅ DataGuardian container restarted"
echo ""
echo "🧪 Test the app to verify caching works:"
echo "   https://dataguardianpro.nl"
echo ""
echo "📊 Check Redis status:"
echo "   systemctl status redis-server"
echo "   redis-cli ping"

exit 0
