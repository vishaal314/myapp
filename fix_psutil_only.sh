#!/bin/bash
# Focused Fix for psutil - DataGuardian Pro Critical Dependency

echo "🎯 Installing psutil only - focused fix for DataGuardian Pro..."

# Stop the service first
echo "⏹️ Stopping DataGuardian service..."
systemctl stop dataguardian

# Clear any pip cache that might be causing issues
echo "🧹 Clearing pip cache..."
sudo -u dataguardian /opt/dataguardian/venv/bin/pip cache purge

# Install psutil with force and no cache
echo "📦 Installing psutil (force reinstall)..."
sudo -u dataguardian /opt/dataguardian/venv/bin/pip install --no-cache-dir --force-reinstall psutil

# Verify psutil is working
echo "🔍 Testing psutil import..."
if sudo -u dataguardian /opt/dataguardian/venv/bin/python3 -c "import psutil; print(f'✅ psutil version: {psutil.__version__}')"; then
    echo "✅ psutil is working correctly!"
    
    # Also install a few other critical missing packages (skip textract for now)
    echo "📦 Installing other critical packages..."
    sudo -u dataguardian /opt/dataguardian/venv/bin/pip install --no-cache-dir \
        anthropic \
        pypdf2 \
        memory-profiler \
        py-spy \
        cachetools \
        joblib \
        opencv-python-headless \
        pytesseract \
        pyyaml \
        aiohttp \
        authlib \
        python-jose \
        python3-saml \
        dnspython \
        python-whois \
        mysql-connector-python \
        svglib

    echo "✅ Critical packages installed!"
    
    # Start the service
    echo "🚀 Starting DataGuardian service..."
    systemctl start dataguardian
    
    # Wait for startup
    sleep 5
    
    # Test the service
    echo "📊 Testing service status..."
    if systemctl is-active --quiet dataguardian; then
        echo "✅ DataGuardian service is running!"
        
        # Test application response
        echo "🌐 Testing application response..."
        sleep 3
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null || echo "000")
        
        if [ "$HTTP_CODE" = "200" ]; then
            echo "✅ SUCCESS! Application is working!"
            echo ""
            echo "🎉 DataGuardian Pro is now operational!"
            echo "🔒 Access: https://dataguardianpro.nl"
            echo "🔓 Backup: http://dataguardianpro.nl:5000"
            echo "👤 Login with: vishaal314"
        else
            echo "⚠️  HTTP Response: $HTTP_CODE"
            echo "🔧 Checking recent logs..."
            journalctl -u dataguardian --no-pager -n 10
        fi
    else
        echo "❌ Service failed to start"
        systemctl status dataguardian --no-pager -l
    fi
    
else
    echo "❌ psutil installation still failed!"
    echo "🔧 Trying alternative installation method..."
    
    # Try installing with system pip and copying
    echo "📦 Installing psutil with system pip..."
    pip3 install psutil
    
    # Copy from system to virtual environment
    PSUTIL_PATH=$(python3 -c "import psutil; print(psutil.__file__)" 2>/dev/null | sed 's/__init__.py//')
    if [ -n "$PSUTIL_PATH" ]; then
        echo "📋 Found system psutil at: $PSUTIL_PATH"
        cp -r "$PSUTIL_PATH"* /opt/dataguardian/venv/lib/python3.11/site-packages/
        chown -R dataguardian:dataguardian /opt/dataguardian/venv/lib/python3.11/site-packages/psutil*
        
        # Test again
        if sudo -u dataguardian /opt/dataguardian/venv/bin/python3 -c "import psutil; print('✅ psutil copied successfully')"; then
            echo "✅ psutil is now working!"
            systemctl start dataguardian
        else
            echo "❌ psutil copy method also failed"
        fi
    fi
fi