#!/bin/bash
# Check DataGuardian Application Status

echo "🔍 Checking DataGuardian Application Status..."
echo "=============================================="

echo "📊 Service Status:"
systemctl status dataguardian --no-pager -l

echo ""
echo "📋 Recent Application Logs:"
journalctl -u dataguardian --no-pager -n 30

echo ""
echo "🌐 Testing Application Response:"
echo "Testing HTTPS..."
HTTPS_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://dataguardianpro.nl 2>/dev/null || echo "000")
echo "HTTPS Response: $HTTPS_CODE"

echo "Testing HTTP backup..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://dataguardianpro.nl:5000 2>/dev/null || echo "000")
echo "HTTP Response: $HTTP_CODE"

echo ""
echo "🔍 Testing Python Dependencies:"
echo "Testing psutil import..."
if sudo -u dataguardian /opt/dataguardian/venv/bin/python3 -c "import psutil; print('✅ psutil working')" 2>/dev/null; then
    echo "✅ psutil is available"
else
    echo "❌ psutil is MISSING - This is the problem!"
fi

echo ""
echo "📁 Virtual Environment Status:"
ls -la /opt/dataguardian/venv/bin/ | grep python
echo ""
echo "Installed packages:"
sudo -u dataguardian /opt/dataguardian/venv/bin/pip list | grep -E "(psutil|streamlit|pandas|openai|stripe)" || echo "❌ Critical packages missing"