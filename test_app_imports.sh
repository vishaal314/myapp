#!/bin/bash
# TEST APP.PY IMPORTS - Find which import is failing silently

echo "🔍 TEST APP.PY IMPORTS"
echo "===================="
echo ""

cd /opt/dataguardian

echo "Testing app.py imports one by one..."
echo ""

python3 << 'PYEOF'
import sys
sys.path.insert(0, '/opt/dataguardian')

print("Test 1: Import streamlit")
try:
    import streamlit as st
    print("✅ streamlit")
except Exception as e:
    print(f"❌ streamlit: {e}")
    sys.exit(1)

print("\nTest 2: Import utils.database_optimizer")
try:
    from utils.database_optimizer import get_optimized_db
    print("✅ utils.database_optimizer")
except Exception as e:
    print(f"❌ utils.database_optimizer: {e}")

print("\nTest 3: Import utils.redis_cache")
try:
    from utils.redis_cache import get_cache
    print("✅ utils.redis_cache")
except Exception as e:
    print(f"❌ utils.redis_cache: {e}")

print("\nTest 4: Import services.license_integration")
try:
    from services.license_integration import LicenseIntegration
    print("✅ services.license_integration")
except Exception as e:
    print(f"❌ services.license_integration: {e}")

print("\nTest 5: Import services.enterprise_auth_service")
try:
    from services.enterprise_auth_service import get_enterprise_auth_service
    print("✅ services.enterprise_auth_service")
except Exception as e:
    print(f"❌ services.enterprise_auth_service: {e}")

print("\nTest 6: Try to actually import app.py")
try:
    # This will run all imports in app.py
    print("Attempting full app.py import...")
    import app
    print("✅ app.py imported successfully!")
except Exception as e:
    print(f"❌ app.py import failed: {e}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()

PYEOF

echo ""
echo "✅ IMPORT TEST COMPLETE"
