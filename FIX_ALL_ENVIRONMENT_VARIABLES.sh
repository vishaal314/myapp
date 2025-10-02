#!/bin/bash
# FIX ALL ENVIRONMENT VARIABLES - Complete fix for external server
# Sets up all required secrets to match Replit environment

set -e

echo "🔧 FIXING ALL ENVIRONMENT VARIABLES"
echo "===================================="
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "❌ Run as root: sudo ./FIX_ALL_ENVIRONMENT_VARIABLES.sh"
    exit 1
fi

echo "Step 1: Generate missing secrets"
echo "=============================="

# Generate JWT_SECRET if not exists
if [ -z "$JWT_SECRET" ]; then
    JWT_SECRET=$(openssl rand -hex 32)
    echo "✅ Generated JWT_SECRET"
else
    echo "✅ Using existing JWT_SECRET"
fi

# Generate DATAGUARDIAN_MASTER_KEY if not exists
if [ -z "$DATAGUARDIAN_MASTER_KEY" ]; then
    DATAGUARDIAN_MASTER_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
    echo "✅ Generated DATAGUARDIAN_MASTER_KEY"
else
    echo "✅ Using existing DATAGUARDIAN_MASTER_KEY"
fi

echo ""
echo "Step 2: Load existing API keys from Replit secrets"
echo "=============================================="

# Check if we have existing secrets file
if [ -f "/root/.dataguardian_env" ]; then
    source /root/.dataguardian_env
    echo "✅ Loaded existing secrets from /root/.dataguardian_env"
fi

# Set defaults for optional keys (these can be empty for basic functionality)
OPENAI_API_KEY="${OPENAI_API_KEY:-}"
STRIPE_SECRET_KEY="${STRIPE_SECRET_KEY:-}"

if [ -n "$OPENAI_API_KEY" ]; then
    echo "✅ OPENAI_API_KEY is set"
else
    echo "⚠️  OPENAI_API_KEY not set (AI features will be limited)"
fi

if [ -n "$STRIPE_SECRET_KEY" ]; then
    echo "✅ STRIPE_SECRET_KEY is set"
else
    echo "⚠️  STRIPE_SECRET_KEY not set (payment features will be limited)"
fi

echo ""
echo "Step 3: Create environment file"
echo "============================="

# Create comprehensive environment file
cat > /root/.dataguardian_env << EOF
# DataGuardian Pro Environment Variables
# Generated: $(date)

# Authentication & Security (REQUIRED)
JWT_SECRET=$JWT_SECRET
DATAGUARDIAN_MASTER_KEY=$DATAGUARDIAN_MASTER_KEY

# API Keys (OPTIONAL - leave empty if not using)
OPENAI_API_KEY=$OPENAI_API_KEY
STRIPE_SECRET_KEY=$STRIPE_SECRET_KEY

# Database (automatically provided by container)
# DATABASE_URL will be set by container if PostgreSQL is available

# Runtime Configuration
PYTHONUNBUFFERED=1
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_PORT=5000
EOF

chmod 600 /root/.dataguardian_env
echo "✅ Created /root/.dataguardian_env (secure permissions)"

echo ""
echo "Step 4: Stop current container"
echo "==========================="
docker stop dataguardian-container 2>/dev/null && echo "✅ Container stopped" || echo "⚠️  No container running"
docker rm dataguardian-container 2>/dev/null && echo "✅ Container removed" || true

echo ""
echo "Step 5: Start container with ALL environment variables"
echo "===================================================="

docker run -d \
    --name dataguardian-container \
    --restart always \
    -p 5000:5000 \
    --env-file /root/.dataguardian_env \
    dataguardian-pro

echo "✅ Container started with complete environment"

echo ""
echo "Step 6: Wait for initialization (45 seconds)"
echo "========================================"
for i in {1..45}; do
    if [ $((i % 5)) -eq 0 ]; then
        echo -n " $i"
    else
        echo -n "."
    fi
    sleep 1
done
echo ""

echo ""
echo "Step 7: Verify environment variables"
echo "=================================="

# Check critical variables
VARS_OK=true

if docker exec dataguardian-container printenv JWT_SECRET &>/dev/null; then
    echo "✅ JWT_SECRET is set"
else
    echo "❌ JWT_SECRET missing"
    VARS_OK=false
fi

if docker exec dataguardian-container printenv DATAGUARDIAN_MASTER_KEY &>/dev/null; then
    echo "✅ DATAGUARDIAN_MASTER_KEY is set"
else
    echo "❌ DATAGUARDIAN_MASTER_KEY missing"
    VARS_OK=false
fi

echo ""
echo "Step 8: Check application logs"
echo "============================"

# Check for common errors
if docker logs dataguardian-container 2>&1 | tail -50 | grep -qi "jwt_secret.*required"; then
    echo "❌ JWT_SECRET error still in logs"
    VARS_OK=false
elif docker logs dataguardian-container 2>&1 | tail -50 | grep -qi "master_key.*not set"; then
    echo "❌ MASTER_KEY error still in logs"
    VARS_OK=false
else
    echo "✅ No environment variable errors in logs"
fi

echo ""
echo "Recent logs:"
docker logs dataguardian-container 2>&1 | tail -25

echo ""
echo "Step 9: Test HTTP response"
echo "======================="

sleep 5
if curl -s http://localhost:5000 | grep -qi "streamlit"; then
    echo "✅ App responding on port 5000"
else
    echo "⚠️  App may still be loading, check logs above"
fi

# Test HTTPS
if curl -s -k https://localhost | grep -qi "streamlit"; then
    echo "✅ HTTPS/Nginx proxy working"
fi

echo ""
echo "Step 10: Create restart script for future use"
echo "=========================================="

cat > /root/restart_dataguardian.sh << 'RESTART_SCRIPT'
#!/bin/bash
# Restart DataGuardian with all environment variables

echo "🔄 Restarting DataGuardian Pro..."

docker stop dataguardian-container 2>/dev/null
docker rm dataguardian-container 2>/dev/null

docker run -d \
    --name dataguardian-container \
    --restart always \
    -p 5000:5000 \
    --env-file /root/.dataguardian_env \
    dataguardian-pro

echo "✅ DataGuardian Pro restarted"
echo "🌐 Access: https://dataguardianpro.nl"

docker logs dataguardian-container 2>&1 | tail -20
RESTART_SCRIPT

chmod +x /root/restart_dataguardian.sh
echo "✅ Created /root/restart_dataguardian.sh for future restarts"

if [ "$VARS_OK" = true ]; then
    echo ""
    echo "=========================================="
    echo "🎉 ALL ENVIRONMENT VARIABLES FIXED!"
    echo "=========================================="
    echo ""
    echo "✅ JWT_SECRET configured"
    echo "✅ DATAGUARDIAN_MASTER_KEY configured"
    echo "✅ Container running with all secrets"
    echo "✅ Environment saved for persistence"
    echo ""
    echo "🌐 TEST YOUR APPLICATION:"
    echo "   https://dataguardianpro.nl"
    echo ""
    echo "🔐 LOGIN CREDENTIALS:"
    echo "   vishaal314 / password123"
    echo "   demo / demo123"
    echo "   admin / admin123"
    echo ""
    echo "✅ SHOULD NOW SEE:"
    echo "   • Full dashboard (no errors)"
    echo "   • All 12 scanners available"
    echo "   • Predictive Compliance working"
    echo "   • All features matching Replit"
    echo ""
    echo "🔄 TO RESTART IN FUTURE:"
    echo "   /root/restart_dataguardian.sh"
    echo ""
    echo "📊 MONITOR LOGS:"
    echo "   docker logs dataguardian-container -f"
    echo ""
    echo "🎯 External server now matches Replit environment!"
    exit 0
else
    echo ""
    echo "⚠️  SOME ISSUES DETECTED"
    echo "======================"
    echo ""
    echo "Please check the logs above for any remaining errors."
    echo "The container is running but may need additional debugging."
    echo ""
    echo "Check full logs with:"
    echo "   docker logs dataguardian-container -f"
    exit 1
fi
