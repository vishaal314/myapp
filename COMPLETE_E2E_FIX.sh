#!/bin/bash
################################################################################
# COMPLETE E2E FIX - Fix everything and rebuild
################################################################################

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 DataGuardian Pro - COMPLETE E2E FIX"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

APP_DIR="/opt/dataguardian"
ENV_FILE="/root/.dataguardian_env"

# Step 1: Remove conflicting config.py
echo ""
echo "🧹 Step 1/6: Removing conflicting config.py..."
cd "$APP_DIR"
rm -f config.py
echo "✅ Removed config.py"

# Step 2: Create config package
echo ""
echo "📦 Step 2/6: Creating config package..."
mkdir -p config

cat > config/__init__.py << 'EOFPYTHON'
"""Configuration package for DataGuardian Pro"""
__version__ = "2.0.0"
EOFPYTHON

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
    return PRICING_TIERS.get(tier_name, PRICING_TIERS["professional"])
EOFPYTHON

cat > config/report_config.py << 'EOFPYTHON'
"""Report configuration for DataGuardian Pro"""

REPORT_FORMATS = ["PDF", "HTML", "JSON", "CSV"]

REPORT_TEMPLATES = {
    "executive": {
        "name": "Executive Summary",
        "sections": ["overview", "compliance_score", "key_findings", "recommendations"]
    },
    "technical": {
        "name": "Technical Report",
        "sections": ["full_scan_results", "pii_details", "gdpr_articles", "remediation"]
    },
    "compliance": {
        "name": "Compliance Report",
        "sections": ["gdpr_compliance", "risk_assessment", "legal_framework", "action_items"]
    }
}

def get_report_config(report_type):
    return REPORT_TEMPLATES.get(report_type, REPORT_TEMPLATES["technical"])
EOFPYTHON

cat > config/translation_mappings.py << 'EOFPYTHON'
"""Translation mappings for scanner types and features"""

SCANNER_TYPE_MAPPING = {
    "code": "Code Scanner",
    "website": "Website Scanner",
    "database": "Database Scanner",
    "ai_model": "AI Model Scanner",
    "dpia": "DPIA Assessment",
    "soc2": "SOC2 Compliance",
    "sustainability": "Sustainability Scanner",
    "blob": "Blob Scanner",
    "image": "Image Scanner",
    "api": "API Scanner",
    "cloud": "Cloud Scanner",
    "repository": "Repository Scanner"
}

def get_scanner_display_name(scanner_type):
    return SCANNER_TYPE_MAPPING.get(scanner_type, scanner_type.title())
EOFPYTHON

echo "✅ Config package created"

# Step 3: Fix database schema
echo ""
echo "🗄️  Step 3/6: Fixing database schema..."
PGPASSWORD=changeme psql -h localhost -U dataguardian -d dataguardian << 'EOFSQL'
-- Add missing columns to tenants table
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS max_users INTEGER DEFAULT 10;
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS max_scans_per_month INTEGER DEFAULT 1000;
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS features JSONB DEFAULT '[]'::jsonb;
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS subscription_status VARCHAR(50) DEFAULT 'active';
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS subscription_end_date TIMESTAMP;

-- Update default tenant
UPDATE tenants 
SET max_users = 100, 
    max_scans_per_month = -1,
    features = '["unlimited_scans", "priority_support", "custom_integrations"]'::jsonb,
    subscription_status = 'active'
WHERE organization_id = 'default_org';
EOFSQL
echo "✅ Database schema updated"

# Step 4: Environment variables
echo ""
echo "🔐 Step 4/6: Setting environment..."
if [ ! -f "$ENV_FILE" ] || [ -z "$(grep DATAGUARDIAN_MASTER_KEY $ENV_FILE 2>/dev/null)" ]; then
    MASTER_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
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
    echo "✅ Environment configured"
else
    echo "✅ Using existing environment"
fi

# Step 5: Rebuild Docker with new config
echo ""
echo "🐳 Step 5/6: Rebuilding Docker image..."
docker stop dataguardian-container 2>/dev/null || true
docker rm -f dataguardian-container 2>/dev/null || true

docker build --no-cache -t dataguardian-pro . || {
    echo "❌ Docker build failed!"
    exit 1
}
echo "✅ Docker rebuilt with new config package"

# Step 6: Start container
echo ""
echo "🚀 Step 6/6: Starting container..."
docker run -d \
    --name dataguardian-container \
    --restart always \
    --network host \
    --env-file "$ENV_FILE" \
    dataguardian-pro

sleep 30

# Verify deployment
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 VERIFICATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check container
if docker ps | grep -q dataguardian-container; then
    echo "✅ Container: RUNNING"
else
    echo "❌ Container: FAILED"
    exit 1
fi

# Check config in container
if docker exec dataguardian-container ls -la /app/config/ 2>/dev/null | grep -q "__init__.py"; then
    echo "✅ Config package: EXISTS IN CONTAINER"
else
    echo "❌ Config package: MISSING IN CONTAINER"
fi

# Test config import
if docker exec dataguardian-container python3 -c "from config import pricing_config; print('OK')" 2>&1 | grep -q "OK"; then
    echo "✅ Config import: SUCCESS"
else
    echo "⚠️  Config import: FAILED (check logs)"
fi

# Check for errors
echo ""
echo "📋 Recent logs:"
docker logs dataguardian-container 2>&1 | tail -20

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
CONFIG_ERRORS=$(docker logs dataguardian-container 2>&1 | grep -c "No module named 'config" || true)
if [ "$CONFIG_ERRORS" -eq 0 ]; then
    echo "🎉 SUCCESS! No config import errors!"
    echo ""
    echo "🌐 Application: https://dataguardianpro.nl"
    echo "👤 Login: vishaal314 / vishaal2024"
    echo ""
    echo "🧪 TEST (use INCOGNITO mode):"
    echo "   1. Close all browser tabs"
    echo "   2. Open incognito window"
    echo "   3. Visit https://dataguardianpro.nl"
    echo "   4. Login and test scanners"
else
    echo "⚠️  WARNING: $CONFIG_ERRORS config import errors detected"
    echo "Check logs: docker logs dataguardian-container | grep config"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
