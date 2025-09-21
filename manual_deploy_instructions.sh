#!/bin/bash
# Manual Deploy Instructions - Run this on your production server

echo "🚀 DataGuardian Pro - Manual Production Deploy"
echo "============================================="
echo ""
echo "Copy this entire script and run it on your production server:"
echo ""

cat << 'PRODUCTION_SCRIPT'
#!/bin/bash
# Production Server Deployment Script

echo "🚀 Starting DataGuardian Pro deployment..."

# Stop service
echo "⏹️ Stopping DataGuardian service..."
systemctl stop dataguardian

# Create backup
echo "💾 Creating backup..."
cp /opt/dataguardian/app.py /opt/dataguardian/app.py.working_deploy_backup.$(date +%Y%m%d_%H%M%S)

# Create temporary file with working version
echo "📄 Creating working version of app.py..."
cat > /tmp/app_working.py << 'WORKING_APP_EOF'
WORKING_APP_EOF

# Move working version to production
echo "🔄 Installing working version..."
mv /tmp/app_working.py /opt/dataguardian/app.py

# Set permissions
echo "🔧 Setting permissions..."
chown dataguardian:dataguardian /opt/dataguardian/app.py

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
            echo "🎉🎉🎉 DEPLOYMENT SUCCESS! 🎉🎉🎉"
            echo "================================"
            echo "✅ Working version deployed"
            echo "✅ All syntax errors resolved"
            echo "✅ Service running properly"
            echo "✅ https://dataguardianpro.nl is operational"
            echo "================================"
        else
            echo "⚠️  Service running, HTTP response: $HTTP_CODE"
        fi
    else
        echo "❌ Service failed to start"
        journalctl -u dataguardian -n 10
    fi
else
    echo "❌ Syntax validation failed"
    sudo -u dataguardian /opt/dataguardian/venv/bin/python3 -m py_compile /opt/dataguardian/app.py
fi

PRODUCTION_SCRIPT

echo ""
echo "📋 Instructions:"
echo "1. Copy the script above"
echo "2. SSH to your production server: ssh root@45.81.35.202"
echo "3. Save as deploy.sh and run it"
echo ""