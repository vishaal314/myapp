#!/bin/bash
# Check Dashboard Error Logs for DataGuardian Pro

echo "🔍 Checking DataGuardian Dashboard Error Logs..."
echo "=============================================="

echo "📊 Current Service Status:"
systemctl status dataguardian --no-pager -l

echo ""
echo "📋 Recent Error Logs (last 50 lines):"
journalctl -u dataguardian --no-pager -n 50

echo ""
echo "🔍 Checking for specific error patterns:"
echo "Looking for database connection errors..."
journalctl -u dataguardian --no-pager -n 100 | grep -i "database\|connection\|psycopg\|redis" || echo "No database connection errors found"

echo ""
echo "Looking for import/module errors..."
journalctl -u dataguardian --no-pager -n 100 | grep -i "import\|module\|traceback" || echo "No import errors found"

echo ""
echo "Looking for dashboard-specific errors..."
journalctl -u dataguardian --no-pager -n 100 | grep -i "dashboard\|temporarily\|unavailable" || echo "No dashboard-specific errors found"

echo ""
echo "🌐 Testing application endpoints:"
echo "Testing main page..."
MAIN_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null || echo "000")
echo "Main page response: $MAIN_CODE"

echo ""
echo "📁 Checking file permissions:"
ls -la /opt/dataguardian/ | head -10

echo ""
echo "🔑 Checking environment variables:"
sudo -u dataguardian /opt/dataguardian/venv/bin/python3 -c "
import os
print('DATABASE_URL present:', 'DATABASE_URL' in os.environ)
print('OPENAI_API_KEY present:', 'OPENAI_API_KEY' in os.environ)
print('STRIPE_SECRET_KEY present:', 'STRIPE_SECRET_KEY' in os.environ)
" 2>/dev/null || echo "Error checking environment variables"

echo ""
echo "📦 Testing critical imports:"
sudo -u dataguardian /opt/dataguardian/venv/bin/python3 -c "
try:
    import streamlit
    print('✅ streamlit OK')
except Exception as e:
    print('❌ streamlit ERROR:', e)

try:
    import psycopg2
    print('✅ psycopg2 OK')
except Exception as e:
    print('❌ psycopg2 ERROR:', e)

try:
    import redis
    print('✅ redis OK')
except Exception as e:
    print('❌ redis ERROR:', e)

try:
    import pandas
    print('✅ pandas OK')
except Exception as e:
    print('❌ pandas ERROR:', e)

try:
    import plotly
    print('✅ plotly OK')
except Exception as e:
    print('❌ plotly ERROR:', e)
"