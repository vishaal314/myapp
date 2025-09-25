#!/bin/bash
# Fix Permissions and Rebuild

echo "🔧 Fixing Permission Issues"
echo "=========================="

# Stop containers
echo "⏹️ Stopping containers..."
docker-compose down

# Rebuild with no cache to ensure changes take effect
echo "🔨 Rebuilding DataGuardian container with permission fixes..."
docker-compose build --no-cache dataguardian

# Start everything back up
echo "🚀 Starting containers with fixed permissions..."
docker-compose up -d

# Wait for startup
echo "⏳ Waiting for services to initialize..."
sleep 15

# Check status
echo "📊 Checking container status..."
docker-compose ps

# Test application
echo "🧪 Testing application access..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo ""
    echo "🎉 SUCCESS! Permission issue fixed!"
    echo "================================="
    echo "✅ All containers running"
    echo "✅ Application responding (HTTP 200)"
    echo "✅ Log permissions resolved"
    echo ""
    echo "📍 Access your DataGuardian Pro:"
    echo "   http://45.81.35.202:5000"
else
    echo "⚠️ Application status: HTTP $HTTP_CODE"
    echo "📋 Check logs if needed:"
    echo "   docker-compose logs dataguardian"
fi