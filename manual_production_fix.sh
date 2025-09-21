#!/bin/bash
# Manual Production Fix - Line by Line

echo "🔧 Manual Production Syntax Fix"
echo "==============================="

# Stop service
echo "⏹️ Stopping service..."
systemctl stop dataguardian

# Create backup
echo "💾 Creating backup..."
cp /opt/dataguardian/app.py /opt/dataguardian/app.py.manual_backup.$(date +%Y%m%d_%H%M%S)

echo "🔧 Applying targeted fixes..."

# Fix the specific line 11124 syntax error
sed -i '11124s/st\.metric("Error", "—"))/st.metric("Error", "—")/' /opt/dataguardian/app.py

echo "✅ Fixed line 11124"

# Check if the fix worked
echo "🔍 Testing Python syntax..."
if sudo -u dataguardian /opt/dataguardian/venv/bin/python3 -m py_compile /opt/dataguardian/app.py 2>/dev/null; then
    echo "✅ Python syntax is now valid!"
    
    # Start service
    echo "🚀 Starting DataGuardian service..."
    systemctl start dataguardian
    
    # Wait and test
    sleep 10
    
    if systemctl is-active --quiet dataguardian; then
        echo "✅ Service is running!"
        
        # Test HTTP
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null || echo "000")
        if [ "$HTTP_CODE" = "200" ]; then
            echo ""
            echo "🎉 SUCCESS! DataGuardian Pro is operational!"
            echo "🔒 Access: https://dataguardianpro.nl"
            echo "👤 Login: vishaal314"
        else
            echo "⚠️  Service running but HTTP: $HTTP_CODE"
        fi
        
        # Show status
        echo ""
        echo "📊 Current Status:"
        systemctl status dataguardian --no-pager -l | head -10
        
    else
        echo "❌ Service failed to start"
        journalctl -u dataguardian -n 5 --no-pager
    fi
    
else
    echo "❌ Syntax still invalid"
    # Show the error
    sudo -u dataguardian /opt/dataguardian/venv/bin/python3 -m py_compile /opt/dataguardian/app.py
    echo "🔄 Check the error above and fix manually"
fi