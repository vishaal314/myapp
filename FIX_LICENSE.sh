#!/bin/bash
################################################################################
# FIX LICENSE - Add enterprise license to server
################################################################################

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎫 FIXING LICENSE - Adding enterprise license"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

APP_DIR="/opt/dataguardian"
cd "$APP_DIR"

# Create enterprise license for vishaal314
echo ""
echo "📝 Creating enterprise license for vishaal314..."
cat > license.json << 'EOFLICENSE'
{
  "license_id": "DGP-ENT-2025-PROD-001",
  "license_type": "enterprise",
  "customer_id": "vishaal314",
  "customer_name": "Vishaal",
  "company_name": "DataGuardian Pro Production",
  "email": "vishaal314@dataguardian.pro",
  "issued_date": "2025-10-06T00:00:00.000000",
  "expiry_date": "2035-10-06T23:59:59.999999",
  "usage_limits": [
    {
      "limit_type": "scans_per_month",
      "limit_value": 99999,
      "current_usage": 0,
      "reset_period": "monthly",
      "last_reset": "2025-10-06T00:00:00.000000"
    },
    {
      "limit_type": "concurrent_users",
      "limit_value": 999,
      "current_usage": 0,
      "reset_period": "daily",
      "last_reset": "2025-10-06T00:00:00.000000"
    }
  ],
  "allowed_features": [
    "all_scanners",
    "unlimited_scanners",
    "code_scanner",
    "blob_scanner",
    "website_scanner",
    "database_scanner",
    "api_scanner",
    "ai_model_scanner",
    "dpia_scanner",
    "soc2_scanner",
    "sustainability_scanner",
    "image_scanner",
    "enterprise_connector_scanner",
    "ai_act_compliance",
    "netherlands_uavg",
    "enterprise_connectors",
    "unlimited_reports",
    "certificate_generation",
    "api_access",
    "compliance_dashboard",
    "reporting",
    "white_label",
    "priority_support",
    "custom_integration",
    "admin_access",
    "full_access"
  ],
  "allowed_scanners": [
    "code_scanner",
    "code",
    "blob_scanner",
    "blob",
    "website_scanner",
    "website",
    "database_scanner",
    "database",
    "api_scanner",
    "api",
    "ai_model_scanner",
    "ai_model",
    "ai model",
    "dpia_scanner",
    "dpia",
    "soc2_scanner",
    "soc2",
    "sustainability_scanner",
    "sustainability",
    "image_scanner",
    "image",
    "enterprise_connector_scanner",
    "enterprise_connector",
    "enterprise",
    "document_scanner",
    "document",
    "all_scanners",
    "unlimited"
  ],
  "allowed_regions": [
    "Netherlands",
    "Germany",
    "France",
    "Belgium",
    "EU",
    "Global"
  ],
  "max_concurrent_users": 999,
  "is_active": true,
  "metadata": {
    "plan_name": "Enterprise",
    "subscription_status": "active",
    "auto_renewal": true,
    "billing_cycle": "annual",
    "created_by": "system",
    "support_level": "premium",
    "sla_hours": 1,
    "deployment": "production"
  }
}
EOFLICENSE

echo "✅ License created: DGP-ENT-2025-PROD-001"

# Verify license file
if [ -f license.json ]; then
    echo "✅ License file exists ($(stat -c%s license.json) bytes)"
else
    echo "❌ License file creation failed!"
    exit 1
fi

# Rebuild Docker with license
echo ""
echo "🐳 Rebuilding Docker with license..."
docker stop dataguardian-container 2>/dev/null || true
docker rm -f dataguardian-container 2>/dev/null || true

docker build --no-cache -t dataguardian-pro . || {
    echo "❌ Docker build failed!"
    exit 1
}
echo "✅ Docker rebuilt with license included"

# Start container
echo ""
echo "🚀 Starting container..."
ENV_FILE="/root/.dataguardian_env"
docker run -d \
    --name dataguardian-container \
    --restart always \
    --network host \
    --env-file "$ENV_FILE" \
    dataguardian-pro

sleep 30

# Verification
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

# Check for license errors
if docker logs dataguardian-container 2>&1 | grep -qi "License Error"; then
    echo "⚠️  License errors detected"
    docker logs dataguardian-container 2>&1 | grep -i "license" | tail -5
else
    echo "✅ No license errors"
fi

# Check Streamlit started
if docker logs dataguardian-container 2>&1 | grep -q "You can now view your Streamlit app"; then
    echo "✅ Streamlit: STARTED"
else
    echo "⚠️  Streamlit: CHECK LOGS"
fi

# Verify license in container
echo ""
echo "🔍 Verifying license inside container..."
if docker exec dataguardian-container test -f /app/license.json; then
    LICENSE_SIZE=$(docker exec dataguardian-container stat -c%s /app/license.json)
    echo "✅ License file in container: ${LICENSE_SIZE} bytes"
    
    LICENSE_TYPE=$(docker exec dataguardian-container cat /app/license.json | grep -o '"license_type": "[^"]*"' | head -1)
    echo "✅ License type: ${LICENSE_TYPE}"
else
    echo "❌ License file NOT in container!"
    exit 1
fi

echo ""
echo "📋 Recent logs:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker logs dataguardian-container 2>&1 | tail -30
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 LICENSE INSTALLED! ENTERPRISE ACCESS GRANTED!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 License Details:"
echo "   License ID: DGP-ENT-2025-PROD-001"
echo "   Type: Enterprise"
echo "   User: vishaal314"
echo "   Scans: 99,999/month"
echo "   Features: ALL (12 scanners)"
echo "   Regions: Global"
echo "   Valid Until: 2035-10-06"
echo ""
echo "🌐 Application: https://dataguardianpro.nl"
echo "👤 Login: vishaal314 / vishaal2024"
echo ""
echo "🧪 FINAL TEST:"
echo "   1. Close ALL browser tabs"
echo "   2. Open INCOGNITO window (Ctrl+Shift+N)"
echo "   3. Visit https://dataguardianpro.nl"
echo "   4. Login - Should go directly to Dashboard"
echo "   5. Test ALL 12 scanners - ALL should work!"
echo ""
echo "✅ Full enterprise access activated!"
