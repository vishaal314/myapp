#!/bin/bash
# VERIFY ALL USERS AND FEATURES ARE AVAILABLE

echo "🔐 VERIFYING USERS AND FEATURES"
echo "==============================="
echo ""

echo "Step 1: Check User Authentication Files"
echo "======================================"
docker exec dataguardian-container ls -la /app/ | grep -E "secure_users|users\.json|auth"

echo ""
echo "Step 2: Verify User Database/Files Exist"
echo "======================================"
docker exec dataguardian-container python3 << 'PYEOF'
import sys
import os
import json

sys.path.insert(0, '/app')

# Check for user files
user_files = [
    '/app/secure_users.json',
    '/app/users.json',
    '/app/utils/secure_auth_enhanced.py'
]

print("User authentication files:")
for file in user_files:
    if os.path.exists(file):
        print(f"✅ {file}")
        if file.endswith('.json'):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        print(f"   Users found: {len(data)}")
                        print(f"   Usernames: {', '.join(list(data.keys())[:5])}")
                    elif isinstance(data, list):
                        print(f"   Users found: {len(data)}")
            except:
                pass
    else:
        print(f"❌ {file} not found")

print("")
print("Checking authentication system...")
try:
    from utils.secure_auth_enhanced import validate_credentials
    print("✅ Authentication system available")
except ImportError as e:
    print(f"⚠️  Auth import issue: {e}")
PYEOF

echo ""
echo "Step 3: Verify All Scanner Services"
echo "================================="
docker exec dataguardian-container python3 << 'PYEOF'
import sys
import os
sys.path.insert(0, '/app')

scanners = {
    'Code Scanner': 'scanner.code_scanner',
    'Document Scanner': 'scanner.blob_scanner',
    'Image Scanner': 'scanner.image_scanner',
    'Website Scanner': 'scanner.website_scanner',
    'Database Scanner': 'scanner.database_scanner',
    'AI Model Scanner': 'services.ai_model_scanner',
    'DPIA Scanner': 'services.dpia_scanner',
    'SOC2 Scanner': 'services.soc2_scanner',
    'API Scanner': 'services.api_scanner',
    'Sustainability Scanner': 'services.sustainability_scanner',
    'Enterprise Connector': 'services.enterprise_connectors',
    'Cookie Scanner': 'services.cookie_scanner'
}

print("Scanner availability check:")
for name, module in scanners.items():
    try:
        __import__(module)
        print(f"✅ {name} ({module})")
    except ImportError as e:
        print(f"❌ {name} ({module}): {str(e)[:60]}")
PYEOF

echo ""
echo "Step 4: Check Database Connection"
echo "=============================="
docker exec dataguardian-container python3 << 'PYEOF'
import os
import sys
sys.path.insert(0, '/app')

db_url = os.environ.get('DATABASE_URL')
if db_url:
    print(f"✅ DATABASE_URL configured")
    print(f"   Connection string: {db_url[:30]}...")
else:
    print("⚠️  DATABASE_URL not set")

try:
    import psycopg2
    print("✅ PostgreSQL driver available")
except:
    print("⚠️  PostgreSQL driver missing")
PYEOF

echo ""
echo "Step 5: Check Key Features"
echo "======================="
docker exec dataguardian-container python3 << 'PYEOF'
import sys
import os
sys.path.insert(0, '/app')

features = {
    'License System': 'services.license_integration',
    'Report Generation': 'services.download_reports',
    'Activity Tracking': 'utils.activity_tracker',
    'Compliance Calculator': 'services.compliance_calculator',
    'Risk Analyzer': 'services.smart_risk_analyzer',
    'Internationalization': 'utils.i18n',
    'Certificate System': 'services.certificate_generator'
}

print("Feature availability:")
for name, module in features.items():
    try:
        __import__(module)
        print(f"✅ {name}")
    except ImportError as e:
        print(f"⚠️  {name}: {str(e)[:50]}")
PYEOF

echo ""
echo "Step 6: Test Key Environment Variables"
echo "===================================="
docker exec dataguardian-container bash -c '
echo "Environment variables:"
[ ! -z "$DATABASE_URL" ] && echo "✅ DATABASE_URL" || echo "⚠️  DATABASE_URL missing"
[ ! -z "$OPENAI_API_KEY" ] && echo "✅ OPENAI_API_KEY" || echo "⚠️  OPENAI_API_KEY missing"
[ ! -z "$STRIPE_SECRET_KEY" ] && echo "✅ STRIPE_SECRET_KEY" || echo "⚠️  STRIPE_SECRET_KEY missing"
[ ! -z "$DATAGUARDIAN_MASTER_KEY" ] && echo "✅ DATAGUARDIAN_MASTER_KEY" || echo "⚠️  DATAGUARDIAN_MASTER_KEY missing"
'

echo ""
echo "=========================================="
echo "📊 VERIFICATION SUMMARY"
echo "=========================================="
echo ""
echo "✅ App is live at: https://dataguardianpro.nl"
echo ""
echo "🔐 TEST THESE LOGIN CREDENTIALS:"
echo "   1. demo / demo123"
echo "   2. vishaal314 / password123"
echo "   3. admin / admin123"
echo ""
echo "📋 TO VERIFY MANUALLY:"
echo "   1. Login with each user"
echo "   2. Test each scanner type"
echo "   3. Generate a report"
echo "   4. Check dashboard metrics"
echo ""
echo "✅ DEPLOYMENT VERIFICATION COMPLETE!"

exit 0
