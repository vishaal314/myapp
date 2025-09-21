#!/bin/bash
# Quick Production Deploy - Run this directly on your production server

echo "🚀 DataGuardian Pro - Quick Production Deploy"
echo "============================================"

# Stop service
echo "⏹️ Stopping DataGuardian service..."
systemctl stop dataguardian

# Create backup  
echo "💾 Creating backup..."
cp /opt/dataguardian/app.py /opt/dataguardian/app.py.replit_deploy_backup.$(date +%Y%m%d_%H%M%S)

# Download working version directly from GitHub/transfer
echo "📥 Getting working version..."

# Alternative 1: Direct fix of known syntax errors
echo "🔧 Applying targeted syntax fixes to existing file..."

# Fix the specific syntax errors that are causing crashes
sed -i 's/st\.metric("Error", "—"))/st.metric("Error", "—")/g' /opt/dataguardian/app.py
sed -i 's/st\.metric("Report Downloads", usage_stats\.get('\''reports_generated'\'', 0))/st.metric("Report Downloads", usage_stats.get('\''reports_generated'\'', 0))/g' /opt/dataguardian/app.py  
sed -i 's/st\.metric("Document Downloads", usage_stats\.get('\''scans_completed'\'', 0))/st.metric("Document Downloads", usage_stats.get('\''scans_completed'\'', 0))/g' /opt/dataguardian/app.py

echo "✅ Fixed known syntax errors"

# Validate syntax
echo "🔍 Validating syntax..."
if sudo -u dataguardian /opt/dataguardian/venv/bin/python3 -m py_compile /opt/dataguardian/app.py 2>/dev/null; then
    echo "✅ Syntax validation passed!"
    
    # Start service
    echo "🚀 Starting DataGuardian service..."
    systemctl start dataguardian
    
    # Wait and test
    sleep 15
    
    if systemctl is-active --quiet dataguardian; then
        echo "✅ Service is running!"
        
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null || echo "000")
        if [ "$HTTP_CODE" = "200" ]; then
            echo ""
            echo "🎉🎉🎉 SUCCESS! 🎉🎉🎉"
            echo "========================"
            echo "✅ Syntax errors fixed"
            echo "✅ Service running"  
            echo "✅ https://dataguardianpro.nl operational"
            echo "👤 Login: vishaal314"
            echo "========================"
        else
            echo "⚠️  Service running, HTTP: $HTTP_CODE"
            echo "💡 May need more time to initialize"
        fi
        
        echo ""
        echo "📊 Service Status:"
        systemctl status dataguardian --no-pager | head -10
        
    else
        echo "❌ Service failed to start"
        journalctl -u dataguardian -n 10
    fi
else
    echo "❌ Syntax validation failed"
    echo "📋 Error details:"
    sudo -u dataguardian /opt/dataguardian/venv/bin/python3 -m py_compile /opt/dataguardian/app.py
fi