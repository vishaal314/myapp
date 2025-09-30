#!/bin/bash
# DIAGNOSE IMPORTS - Find exactly which import is failing

echo "🔍 DEEP IMPORT DIAGNOSIS"
echo "======================="
echo ""

echo "Test 1: Check if protected imports are in container"
echo "================================================="
docker exec dataguardian-container grep -c "PERFORMANCE_IMPORTS_OK" /app/app.py

echo ""
echo "Test 2: Try to import app.py and capture ALL errors"
echo "================================================="
docker exec dataguardian-container python3 -c "
import sys
import traceback
sys.path.insert(0, '/app')

print('Starting import test...')
print('')

try:
    import app
    print('✅ SUCCESS: app.py imported without errors!')
except Exception as e:
    print('❌ IMPORT FAILED!')
    print('')
    print('Error type:', type(e).__name__)
    print('Error message:', str(e))
    print('')
    print('Full traceback:')
    traceback.print_exc()
" 2>&1

echo ""
echo "Test 3: Check for Python syntax errors"
echo "===================================="
docker exec dataguardian-container python3 -m py_compile /app/app.py 2>&1 && echo "✅ No syntax errors" || echo "❌ Syntax errors found"

echo ""
echo "Test 4: Check which modules are available"
echo "======================================"
docker exec dataguardian-container python3 -c "
import sys
sys.path.insert(0, '/app')

modules_to_test = [
    'utils.database_optimizer',
    'utils.redis_cache',
    'services.license_integration',
    'services.enterprise_auth_service',
    'components.pricing_display',
    'config.pricing_config'
]

for module in modules_to_test:
    try:
        __import__(module)
        print(f'✅ {module}')
    except Exception as e:
        print(f'❌ {module}: {str(e)[:80]}')
"

echo ""
echo "Test 5: Check file structure in container"
echo "======================================"
docker exec dataguardian-container ls -la /app/ | head -20

echo ""
echo "Test 6: Check if utils/ services/ exist"
echo "===================================="
docker exec dataguardian-container bash -c "
echo 'utils/: ' && ls /app/utils/ 2>&1 | head -5
echo ''
echo 'services/: ' && ls /app/services/ 2>&1 | head -5
echo ''
echo 'components/: ' && ls /app/components/ 2>&1 | head -5
"

echo ""
echo "Test 7: Try importing Streamlit in container"
echo "========================================="
docker exec dataguardian-container python3 -c "import streamlit as st; print('✅ Streamlit imports OK')" 2>&1

echo ""
echo "✅ DIAGNOSIS COMPLETE"
echo "===================="
echo ""
echo "Look for the FIRST import error above - that's what's breaking app.py"
