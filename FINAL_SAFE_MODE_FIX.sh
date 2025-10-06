#!/bin/bash
################################################################################
# FINAL SAFE MODE FIX - Fix JWT_SECRET and config functions
################################################################################

set -e

echo "🔧 Fixing safe mode issues..."

APP_DIR="/opt/dataguardian"
ENV_FILE="/root/.dataguardian_env"

cd "$APP_DIR"

# Step 1: Fix config/pricing_config.py with missing function
echo ""
echo "📦 Step 1/4: Fixing config/pricing_config.py..."
cat > config/pricing_config.py << 'EOFPYTHON'
"""Pricing configuration for DataGuardian Pro"""

PRICING_TIERS = {
    "starter": {
        "name": "Starter",
        "price_monthly": 25,
        "price_yearly": 250,
        "features": ["Basic PII scanning", "Up to 1,000 files/month", "PDF reports"],
        "scanner_limits": {"code": 1000, "website": 10, "database": 1}
    },
    "professional": {
        "name": "Professional", 
        "price_monthly": 99,
        "price_yearly": 990,
        "features": ["Advanced scanning", "Up to 10,000 files/month", "All report formats"],
        "scanner_limits": {"code": 10000, "website": 100, "database": 10}
    },
    "enterprise": {
        "name": "Enterprise",
        "price_monthly": 250,
        "price_yearly": 2500,
        "features": ["Unlimited scanning", "Priority support", "Custom integrations"],
        "scanner_limits": {"code": -1, "website": -1, "database": -1}
    }
}

CERTIFICATE_PRICE = 9.99

def get_tier_config(tier_name):
    """Get configuration for a specific tier"""
    return PRICING_TIERS.get(tier_name, PRICING_TIERS["professional"])

def get_pricing_config():
    """Get complete pricing configuration (required by license system)"""
    return {
        "tiers": PRICING_TIERS,
        "certificate_price": CERTIFICATE_PRICE,
        "currency": "EUR"
    }
EOFPYTHON
echo "✅ Fixed config/pricing_config.py"

# Step 2: Verify and update environment file
echo ""
echo "🔐 Step 2/4: Ensuring environment variables..."
if [ ! -f "$ENV_FILE" ]; then
    MASTER_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
else
    # Read existing or generate new
    source "$ENV_FILE" 2>/dev/null || true
    if [ -z "$DATAGUARDIAN_MASTER_KEY" ]; then
        MASTER_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    else
        MASTER_KEY="$DATAGUARDIAN_MASTER_KEY"
    fi
    if [ -z "$JWT_SECRET" ]; then
        JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    fi
fi

# Write complete environment file
cat > "$ENV_FILE" << EOF
DATAGUARDIAN_MASTER_KEY=$MASTER_KEY
JWT_SECRET=$JWT_SECRET
DATABASE_URL=postgresql://dataguardian:changeme@localhost:5432/dataguardian
PGHOST=localhost
PGPORT=5432
PGDATABASE=dataguardian
PGUSER=dataguardian
PGPASSWORD=changeme
REDIS_HOST=localhost
REDIS_PORT=6379
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=False
EOF
chmod 600 "$ENV_FILE"
echo "✅ Environment file created with JWT_SECRET"
echo "   JWT_SECRET=${JWT_SECRET:0:20}..." # Show first 20 chars

# Step 3: Rebuild Docker
echo ""
echo "🐳 Step 3/4: Rebuilding Docker..."
docker stop dataguardian-container 2>/dev/null || true
docker rm -f dataguardian-container 2>/dev/null || true

docker build --no-cache -t dataguardian-pro . || {
    echo "❌ Docker build failed!"
    exit 1
}
echo "✅ Docker rebuilt"

# Step 4: Start with environment file
echo ""
echo "🚀 Step 4/4: Starting container with environment..."
docker run -d \
    --name dataguardian-container \
    --restart always \
    --network host \
    --env-file "$ENV_FILE" \
    dataguardian-pro

sleep 25

# Verification
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 VERIFICATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check container running
if docker ps | grep -q dataguardian-container; then
    echo "✅ Container: RUNNING"
else
    echo "❌ Container: FAILED"
    exit 1
fi

# Check for JWT_SECRET error
if docker logs dataguardian-container 2>&1 | grep -q "JWT_SECRET environment variable is required"; then
    echo "❌ JWT_SECRET: STILL MISSING"
    echo "   Checking environment in container..."
    docker exec dataguardian-container printenv | grep JWT_SECRET || echo "   JWT_SECRET not in container!"
else
    echo "✅ JWT_SECRET: LOADED"
fi

# Check for config errors
if docker logs dataguardian-container 2>&1 | grep -q "cannot import name 'get_pricing_config'"; then
    echo "❌ Config: get_pricing_config missing"
else
    echo "✅ Config: get_pricing_config exists"
fi

# Check for safe mode
if docker logs dataguardian-container 2>&1 | grep -qi "safe mode"; then
    echo "⚠️  App: STILL IN SAFE MODE"
else
    echo "✅ App: NORMAL MODE"
fi

echo ""
echo "📋 Recent logs (last 25 lines):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker logs dataguardian-container 2>&1 | tail -25
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Final status
ERRORS=$(docker logs dataguardian-container 2>&1 | grep -c "JWT_SECRET\|cannot import name 'get_pricing_config'" || true)
if [ "$ERRORS" -eq 0 ]; then
    echo ""
    echo "🎉 SUCCESS! No safe mode errors!"
    echo ""
    echo "🌐 Application: https://dataguardianpro.nl"
    echo "👤 Login: vishaal314 / vishaal2024"
    echo ""
    echo "🧪 TEST (IMPORTANT - use INCOGNITO):"
    echo "   1. Close ALL browser tabs"
    echo "   2. Open INCOGNITO window (Ctrl+Shift+N)"
    echo "   3. Visit https://dataguardianpro.nl"
    echo "   4. Login and test scanners"
    echo ""
else
    echo ""
    echo "⚠️  WARNING: $ERRORS errors still detected"
    echo "Manual check needed:"
    echo "   docker logs dataguardian-container | grep -E 'JWT_SECRET|get_pricing_config|safe mode'"
fi
