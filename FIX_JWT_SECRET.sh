#!/bin/bash
# FIX JWT_SECRET - Add missing JWT secret to external server

set -e

echo "🔧 FIXING JWT_SECRET ENVIRONMENT VARIABLE"
echo "========================================="
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "❌ Run as root: sudo ./FIX_JWT_SECRET.sh"
    exit 1
fi

echo "Step 1: Generate secure JWT_SECRET"
echo "================================="

# Generate a secure 64-character random secret
JWT_SECRET=$(openssl rand -hex 32)
echo "✅ Generated secure JWT_SECRET: ${JWT_SECRET:0:16}... (truncated for security)"

echo ""
echo "Step 2: Stop current container"
echo "==========================="
docker stop dataguardian-container 2>/dev/null && echo "✅ Container stopped" || echo "⚠️  Container not running"
docker rm dataguardian-container 2>/dev/null && echo "✅ Container removed" || true

echo ""
echo "Step 3: Start container with JWT_SECRET"
echo "===================================="

# Start container with all required environment variables
docker run -d \
    --name dataguardian-container \
    --restart always \
    -p 5000:5000 \
    -e PYTHONUNBUFFERED=1 \
    -e JWT_SECRET="$JWT_SECRET" \
    -e DATAGUARDIAN_MASTER_KEY="${DATAGUARDIAN_MASTER_KEY:-}" \
    -e OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
    -e STRIPE_SECRET_KEY="${STRIPE_SECRET_KEY:-}" \
    dataguardian-pro

echo "✅ Container started with JWT_SECRET"

echo ""
echo "Step 4: Save JWT_SECRET for persistence"
echo "===================================="

# Save to environment file for future container restarts
cat > /root/.dataguardian_env << EOF
JWT_SECRET=$JWT_SECRET
DATAGUARDIAN_MASTER_KEY=${DATAGUARDIAN_MASTER_KEY:-}
OPENAI_API_KEY=${OPENAI_API_KEY:-}
STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY:-}
EOF

chmod 600 /root/.dataguardian_env
echo "✅ Saved to /root/.dataguardian_env (secure)"

echo ""
echo "Step 5: Wait for initialization (30 seconds)"
echo "========================================"
for i in {1..30}; do
    if [ $((i % 5)) -eq 0 ]; then
        echo -n " $i"
    else
        echo -n "."
    fi
    sleep 1
done
echo ""

echo ""
echo "Step 6: Verify JWT_SECRET is loaded"
echo "================================="

# Check if JWT_SECRET is in container
if docker exec dataguardian-container printenv JWT_SECRET &>/dev/null; then
    echo "✅ JWT_SECRET is set in container"
else
    echo "❌ JWT_SECRET not found in container"
    exit 1
fi

echo ""
echo "Step 7: Test application"
echo "======================"

# Check logs for JWT error
if docker logs dataguardian-container 2>&1 | tail -30 | grep -qi "jwt_secret.*required"; then
    echo "❌ JWT_SECRET error still present in logs"
    docker logs dataguardian-container 2>&1 | tail -20
    exit 1
else
    echo "✅ No JWT_SECRET errors in logs"
fi

# Check HTTP response
sleep 5
if curl -s http://localhost:5000 | grep -qi "streamlit"; then
    echo "✅ App responding on port 5000"
else
    echo "⚠️  App may still be loading..."
fi

echo ""
echo "Container logs (last 20 lines):"
docker logs dataguardian-container 2>&1 | tail -20

echo ""
echo "=========================================="
echo "🎉 JWT_SECRET FIX COMPLETE!"
echo "=========================================="
echo ""
echo "✅ JWT_SECRET generated and configured"
echo "✅ Container restarted with environment variables"
echo "✅ Secret saved to /root/.dataguardian_env"
echo ""
echo "🌐 Test login now:"
echo "   1. Visit: https://dataguardianpro.nl"
echo "   2. Login: vishaal314 / password123"
echo "   3. Should see full dashboard (no safe mode)"
echo ""
echo "🔄 For future container restarts, use:"
echo "   docker run -d --name dataguardian-container --restart always -p 5000:5000 --env-file /root/.dataguardian_env dataguardian-pro"
echo ""
echo "✅ Login should now work without errors!"

exit 0
