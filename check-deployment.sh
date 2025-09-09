#!/bin/bash

# DataGuardian Pro Deployment Health Check Script
# Use this to verify your deployment is working correctly

echo "🔍 DataGuardian Pro Deployment Health Check"
echo "=========================================="

cd /opt/dataguardian-pro || {
    echo "❌ DataGuardian directory not found!"
    exit 1
}

# Check Docker services
echo "📋 Docker Services Status:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "🐳 Docker Images:"
docker images | grep -E "(dataguardian|postgres|redis|nginx|certbot)"

echo ""
echo "💾 Disk Usage:"
df -h /

echo ""
echo "📁 Application Directories:"
ls -la /opt/dataguardian-pro/

echo ""
echo "🌐 Network Connectivity Test:"
if curl -s -f http://localhost:5000 >/dev/null 2>&1; then
    echo "✅ Application responding on port 5000"
else
    echo "❌ Application not responding on port 5000"
    echo "📋 Application logs (last 10 lines):"
    docker logs dataguardian-pro --tail=10 2>/dev/null || echo "No logs available"
fi

echo ""
echo "🔒 SSL Certificate Status:"
if [ -d "/opt/dataguardian-pro/ssl/live" ]; then
    echo "✅ SSL certificates found"
    ls -la /opt/dataguardian-pro/ssl/live/
else
    echo "⚠️  SSL certificates not found"
fi

echo ""
echo "📊 Database Connection Test:"
if docker exec dataguardian-postgres pg_isready -U dataguardian_pro >/dev/null 2>&1; then
    echo "✅ Database is ready"
else
    echo "❌ Database connection failed"
fi

echo ""
echo "⚡ Redis Connection Test:"
if docker exec dataguardian-redis redis-cli ping >/dev/null 2>&1; then
    echo "✅ Redis is responding"
else
    echo "❌ Redis connection failed"  
fi

echo ""
echo "🔧 Environment Variables Check:"
if [ -f "/opt/dataguardian-pro/.env" ]; then
    echo "✅ Environment file exists"
    echo "Variables set:"
    grep -E "^[A-Z]" /opt/dataguardian-pro/.env | grep -v "PASSWORD\|KEY\|SECRET" || echo "No safe variables to display"
else
    echo "❌ Environment file missing"
fi

echo ""
echo "=========================================="
echo "Health check completed!"