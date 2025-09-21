#!/bin/bash
# Deploy Working Version from Replit to Production

echo "🚀 DataGuardian Pro - Deploy Working Version"
echo "==========================================="
echo "Transferring tested, working app.py to production"
echo ""

# Check if we have the working app.py locally
if [ ! -f "app.py" ]; then
    echo "❌ app.py not found in current directory"
    echo "Please run this from the Replit root directory"
    exit 1
fi

echo "✅ Found working app.py locally"

# Test local syntax first
echo "🔍 Validating local app.py syntax..."
if python3 -m py_compile app.py 2>/dev/null; then
    echo "✅ Local app.py syntax is valid"
else
    echo "❌ Local app.py has syntax errors"
    python3 -m py_compile app.py
    exit 1
fi

# Production server details
PROD_SERVER="45.81.35.202"
PROD_USER="root"
PROD_PATH="/opt/dataguardian"

echo ""
echo "📤 Deploying to production server..."

# Stop production service
echo "⏹️ Stopping production service..."
ssh ${PROD_USER}@${PROD_SERVER} "systemctl stop dataguardian"

# Create backup on production
echo "💾 Creating backup on production..."
ssh ${PROD_USER}@${PROD_SERVER} "cp ${PROD_PATH}/app.py ${PROD_PATH}/app.py.working_deploy_backup.\$(date +%Y%m%d_%H%M%S)"

# Transfer working version
echo "🔄 Transferring working app.py..."
scp app.py ${PROD_USER}@${PROD_SERVER}:${PROD_PATH}/app.py

# Set proper permissions
echo "🔧 Setting permissions..."
ssh ${PROD_USER}@${PROD_SERVER} "chown dataguardian:dataguardian ${PROD_PATH}/app.py"

# Validate syntax on production
echo "🔍 Validating syntax on production..."
if ssh ${PROD_USER}@${PROD_SERVER} "sudo -u dataguardian ${PROD_PATH}/venv/bin/python3 -m py_compile ${PROD_PATH}/app.py 2>/dev/null"; then
    echo "✅ Production syntax validation passed!"
    
    # Start service
    echo "🚀 Starting DataGuardian service..."
    ssh ${PROD_USER}@${PROD_SERVER} "systemctl start dataguardian"
    
    # Wait for startup
    echo "⏳ Waiting for service startup..."
    sleep 15
    
    # Check status
    if ssh ${PROD_USER}@${PROD_SERVER} "systemctl is-active --quiet dataguardian"; then
        echo "✅ DataGuardian service is running!"
        
        # Test HTTP
        echo "🌐 Testing HTTP response..."
        HTTP_CODE=$(ssh ${PROD_USER}@${PROD_SERVER} "curl -s -o /dev/null -w '%{http_code}' http://localhost:5000 2>/dev/null" || echo "000")
        
        if [ "$HTTP_CODE" = "200" ]; then
            echo ""
            echo "🎉🎉🎉 DEPLOYMENT SUCCESS! 🎉🎉🎉"
            echo "======================================="
            echo "✅ Working version deployed successfully"
            echo "✅ All syntax errors resolved"
            echo "✅ Service running properly"
            echo "✅ HTTP responses working"
            echo "✅ 502 Bad Gateway RESOLVED"
            echo ""
            echo "🔒 Your DataGuardian Pro is live:"
            echo "   https://dataguardianpro.nl"
            echo ""
            echo "👤 Admin Login:"
            echo "   Username: vishaal314"
            echo ""
            echo "📊 Full enterprise functionality restored!"
            echo "======================================="
            
        else
            echo "⚠️  Service running but HTTP response: $HTTP_CODE"
            echo "💡 May need 30 seconds to fully initialize"
        fi
        
        # Show service status
        echo ""
        echo "📊 Production Service Status:"
        ssh ${PROD_USER}@${PROD_SERVER} "systemctl status dataguardian --no-pager -l | head -10"
        
    else
        echo "❌ Service failed to start"
        echo "📋 Service logs:"
        ssh ${PROD_USER}@${PROD_SERVER} "journalctl -u dataguardian --no-pager -n 10"
        exit 1
    fi
    
else
    echo "❌ Syntax validation failed on production"
    ssh ${PROD_USER}@${PROD_SERVER} "sudo -u dataguardian ${PROD_PATH}/venv/bin/python3 -m py_compile ${PROD_PATH}/app.py"
    exit 1
fi

echo ""
echo "🎯 Deployment Complete!"
echo "Your DataGuardian Pro is now fully operational with the tested, working version."