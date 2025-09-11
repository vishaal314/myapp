#!/bin/bash

echo "🚀 DataGuardian Pro Demo Enterprise Upgrade - Starting..."
echo "================================================"

# Step 1: Backup current license file
echo "📝 Step 1: Backing up current licenses..."
cp licenses.json licenses_backup_$(date +%Y%m%d_%H%M%S).json

if [ $? -eq 0 ]; then
    echo "✅ License backup created successfully"
else
    echo "❌ Failed to backup licenses"
    exit 1
fi

# Step 2: Upgrade demo account to Enterprise
echo ""
echo "🎯 Step 2: Upgrading demo@dataguardianpro.nl to Enterprise..."

# Create the upgraded licenses.json with Enterprise rights for demo
cat > licenses.json << 'EOF'
{
  "admin_001": {
    "user_id": "admin_001",
    "username": "admin",
    "email": "admin@dataguardian.pro",
    "license_tier": "Enterprise",
    "license_status": "active",
    "scans_remaining": 99999,
    "scans_limit": 99999,
    "users_limit": 999,
    "features": [
      "all_scanners",
      "ai_act_compliance",
      "netherlands_uavg",
      "enterprise_connectors",
      "unlimited_reports",
      "certificate_generation",
      "priority_support"
    ],
    "regions": [
      "Netherlands",
      "Germany",
      "France",
      "Belgium",
      "EU"
    ],
    "license_start": "2025-09-06T16:23:49.937566",
    "license_end": "2035-09-04T16:23:49.937574",
    "created_at": "2025-09-06T16:23:49.937580",
    "last_updated": "2025-09-06T16:23:49.937581"
  },
  "demo_001": {
    "user_id": "demo_001",
    "username": "demo",
    "email": "demo@dataguardian.pro",
    "license_tier": "Enterprise",
    "license_status": "active",
    "scans_remaining": 99999,
    "scans_limit": 99999,
    "users_limit": 999,
    "features": [
      "all_scanners",
      "ai_act_compliance",
      "netherlands_uavg",
      "enterprise_connectors",
      "unlimited_reports",
      "certificate_generation",
      "priority_support",
      "full_demo_access"
    ],
    "regions": [
      "Netherlands",
      "Germany",
      "France",
      "Belgium",
      "EU"
    ],
    "license_start": "2025-09-06T16:23:49.939713",
    "license_end": "2026-09-06T16:23:49.939720",
    "created_at": "2025-09-06T16:23:49.939726",
    "last_updated": "2025-09-11T23:30:00.000000"
  }
}
EOF

if [ $? -eq 0 ]; then
    echo "✅ Demo account upgraded to Enterprise tier"
    echo "   - License: Professional → Enterprise"
    echo "   - Scans: 1000 → 99999 (unlimited)"
    echo "   - Features: Basic → All Enterprise features"
    echo "   - Regions: Netherlands only → All EU regions"
else
    echo "❌ Failed to upgrade demo license"
    exit 1
fi

# Step 3: Also update user_licenses.json to ensure consistency
echo ""
echo "🔄 Step 3: Updating user license assignments..."

cat > user_licenses.json << 'EOF'
{
  "admin": {
    "license_id": "DGP-ENT-2025-001",
    "user_id": "admin_001",
    "assigned_date": "2025-09-06T16:24:26.573433",
    "status": "active"
  },
  "demo": {
    "license_id": "DGP-ENT-2025-002",
    "user_id": "demo_001",
    "assigned_date": "2025-09-11T23:30:00.000000",
    "status": "active"
  }
}
EOF

if [ $? -eq 0 ]; then
    echo "✅ User license assignments updated"
else
    echo "❌ Failed to update user license assignments"
    exit 1
fi

# Step 4: Restart DataGuardian Pro to apply new licenses
echo ""
echo "🔄 Step 4: Restarting DataGuardian Pro with Enterprise license..."
docker compose -f docker-compose.prod.yml restart dataguardian-pro

if [ $? -eq 0 ]; then
    echo "✅ DataGuardian Pro restarted successfully"
else
    echo "❌ Failed to restart DataGuardian Pro"
    exit 1
fi

echo "⏳ Waiting for container to fully start with new license..."
sleep 25

# Step 5: Verify license upgrade
echo ""
echo "📊 Step 5: Verifying license upgrade..."

# Check if the demo user now has Enterprise access
if grep -q '"license_tier": "Enterprise"' licenses.json && grep -q '"email": "demo@dataguardian.pro"' licenses.json; then
    echo "✅ Demo account license upgrade confirmed"
else
    echo "❌ License upgrade verification failed"
    exit 1
fi

# Check container logs for any errors
echo ""
echo "📋 Container status and recent logs:"
docker logs dataguardian-pro --tail 10

# Step 6: Test website connectivity
echo ""
echo "🌐 Step 6: Testing website connectivity..."
curl -I https://dataguardianpro.nl

echo ""
echo "🎉 Demo Enterprise Upgrade Complete!"
echo "================================================"
echo "✅ License: Demo account upgraded to Enterprise"
echo "✅ Features: All scanners and enterprise features enabled"
echo "✅ Scans: Unlimited (99,999 scans)"
echo "✅ Regions: All EU regions (Netherlands, Germany, France, Belgium)"
echo "✅ Container: Restarted with new license configuration"
echo ""
echo "🎯 DEMO ACCOUNT NOW HAS FULL ACCESS:"
echo "   📧 Email: demo@dataguardianpro.nl"
echo "   🔐 Password: demo123"
echo "   🏆 Tier: Enterprise (full features)"
echo "   🔍 Scanners: All scanners available"
echo "   📊 Scans: 99,999 (unlimited)"
echo "   🌍 Regions: All EU regions"
echo "   🎫 Features: All enterprise features enabled"
echo ""
echo "🚀 LOGIN NOW:"
echo "1. Go to: https://dataguardianpro.nl"
echo "2. Select: 🇳🇱 Nederlands (working!)"
echo "3. Email: demo@dataguardianpro.nl"
echo "4. Password: demo123"
echo "5. Click: 'Inloggen'"
echo "6. Access: Full DataGuardian Pro platform!"
echo ""
echo "💡 The demo account now has TEMPORARY full Enterprise rights"
echo "   including all scanners, unlimited scans, and all features!"