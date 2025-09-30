#!/bin/bash
# DIAGNOSE EXTERNAL SERVER - Find out why app.py isn't loading properly

echo "🔍 DIAGNOSE EXTERNAL SERVER - ROOT CAUSE ANALYSIS"
echo "==============================================="
echo ""

echo "📊 STEP 1: SERVICE STATUS"
echo "====================="
systemctl status dataguardian --no-pager | head -20

echo ""
echo "📄 STEP 2: LAST 100 LINES OF DATAGUARDIAN LOGS"
echo "==========================================="
journalctl -u dataguardian -n 100 --no-pager

echo ""
echo "🔍 STEP 3: CHECK FOR ERRORS IN LOGS"
echo "=============================="
echo "Python errors:"
journalctl -u dataguardian -n 200 --no-pager | grep -i "error\|exception\|traceback\|failed\|modulenotfound" | head -20

echo ""
echo "🔍 STEP 4: CHECK APP.PY IMPORTS"
echo "============================="
cd /opt/dataguardian
echo "First 50 import lines:"
grep "^import\|^from" app.py | head -50

echo ""
echo "🔍 STEP 5: TEST IMPORT MANUALLY"
echo "============================="
cd /opt/dataguardian
python3 -c "
import sys
sys.path.insert(0, '/opt/dataguardian')

print('Testing critical imports...')

try:
    import streamlit
    print('✅ streamlit')
except Exception as e:
    print(f'❌ streamlit: {e}')

try:
    from utils.database_optimizer import get_optimized_db
    print('✅ utils.database_optimizer')
except Exception as e:
    print(f'❌ utils.database_optimizer: {e}')

try:
    from services.license_integration import require_license_check
    print('✅ services.license_integration')
except Exception as e:
    print(f'❌ services.license_integration: {e}')

try:
    from utils.activity_tracker import track_scan_started
    print('✅ utils.activity_tracker')
except Exception as e:
    print(f'❌ utils.activity_tracker: {e}')
"

echo ""
echo "🔍 STEP 6: CHECK HTTP RESPONSE DETAILS"
echo "==================================="
echo "Full HTTP response:"
curl -s http://localhost:5000 | head -200

echo ""
echo "Search for DataGuardian:"
curl -s http://localhost:5000 | grep -i "dataguardian" || echo "❌ NO DATAGUARDIAN CONTENT FOUND"

echo ""
echo "Search for Streamlit title:"
curl -s http://localhost:5000 | grep -i "title" | head -5

echo ""
echo "🔍 STEP 7: CHECK MISSING DEPENDENCIES"
echo "==================================="
echo "Checking Python packages:"
pip3 list | grep -i "streamlit\|pandas\|plotly\|bcrypt\|redis\|jwt" || echo "Some packages missing"

echo ""
echo "✅ DIAGNOSIS COMPLETE!"
echo "===================="
echo ""
echo "Review the errors above to identify the issue."
echo ""
