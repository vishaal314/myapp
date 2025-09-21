#!/bin/bash
# Fix Production Syntax Error - DataGuardian Pro

echo "🔧 Fixing production syntax error..."

# Stop the service
echo "⏹️ Stopping DataGuardian service..."
systemctl stop dataguardian

# Create backup
echo "💾 Creating backup..."
cp /opt/dataguardian/app.py /opt/dataguardian/app.py.production_fix_backup.$(date +%Y%m%d_%H%M%S)

# Fix the specific syntax error at line 11124
echo "🔧 Fixing unmatched parenthesis at line 11124..."
sed -i '11124s/st\.metric("Error", "—"))/st.metric("Error", "—")/' /opt/dataguardian/app.py

# Also fix any other similar issues
echo "🔧 Fixing other potential syntax errors..."
sed -i 's/st\.metric(\([^)]*\)))/st.metric(\1)/g' /opt/dataguardian/app.py

# Verify the fix
echo "🔍 Checking Python syntax..."
if sudo -u dataguardian /opt/dataguardian/venv/bin/python3 -c "
import ast
with open('/opt/dataguardian/app.py', 'r') as f:
    ast.parse(f.read())
print('✅ Syntax is valid')
"; then
    echo "✅ Python syntax validation passed!"
else
    echo "❌ Syntax validation failed, restoring backup"
    cp /opt/dataguardian/app.py.production_fix_backup.* /opt/dataguardian/app.py 2>/dev/null
    exit 1
fi

# Start the service
echo "🚀 Starting DataGuardian service..."
systemctl start dataguardian

# Wait and check status
sleep 8
if systemctl is-active --quiet dataguardian; then
    echo "✅ SUCCESS! DataGuardian service is running!"
    
    # Test HTTP response
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ SUCCESS! Application responding properly!"
        echo ""
        echo "🎉 DataGuardian Pro is now operational!"
        echo "🔒 Access: https://dataguardianpro.nl"
        echo "👤 Login with: vishaal314"
    else
        echo "⚠️  Service running but HTTP response: $HTTP_CODE"
    fi
else
    echo "❌ Service failed to start"
    echo "📋 Check logs:"
    journalctl -u dataguardian -n 10
    exit 1
fi