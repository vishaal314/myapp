#!/bin/bash
# Fix Missing Python Dependencies for DataGuardian Pro

echo "🔧 Fixing missing Python dependencies for DataGuardian Pro..."

# Stop the service first
echo "⏹️ Stopping DataGuardian service..."
systemctl stop dataguardian

# Install missing Python dependencies in the virtual environment
echo "📦 Installing missing dependencies..."
sudo -u dataguardian /opt/dataguardian/venv/bin/pip install --upgrade pip

# Install the specific missing modules
echo "📥 Installing psutil and other required dependencies..."
sudo -u dataguardian /opt/dataguardian/venv/bin/pip install \
    psutil \
    streamlit \
    psycopg2-binary \
    redis \
    python-dotenv \
    requests \
    pandas \
    plotly \
    bcrypt \
    cryptography \
    pyjwt \
    pillow \
    beautifulsoup4 \
    openai \
    anthropic \
    stripe \
    reportlab \
    pypdf2 \
    textract \
    pdfkit \
    trafilatura \
    tldextract \
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
    svglib \
    weasyprint

echo "✅ Dependencies installed successfully!"

# Verify psutil is properly installed
echo "🔍 Verifying psutil installation..."
if sudo -u dataguardian /opt/dataguardian/venv/bin/python3 -c "import psutil; print(f'psutil version: {psutil.__version__}')"; then
    echo "✅ psutil is working correctly"
else
    echo "❌ psutil installation failed"
    exit 1
fi

# Verify other critical imports
echo "🔍 Testing other critical imports..."
if sudo -u dataguardian /opt/dataguardian/venv/bin/python3 -c "
import streamlit
import psycopg2
import redis
import requests
import pandas
import plotly
import bcrypt
import jwt
import openai
import stripe
print('✅ All critical modules imported successfully')
"; then
    echo "✅ All dependencies are working"
else
    echo "❌ Some dependencies are still missing"
    exit 1
fi

# Start the service
echo "🚀 Starting DataGuardian service..."
systemctl start dataguardian

# Wait a moment for startup
sleep 5

# Check service status
echo "📊 Checking service status..."
if systemctl is-active --quiet dataguardian; then
    echo "✅ DataGuardian service is running!"
    
    # Test HTTP response
    echo "🌐 Testing application response..."
    sleep 3
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ Application is responding correctly (HTTP 200)"
        echo ""
        echo "🎉 DataGuardian Pro is now working perfectly!"
        echo "🌐 Access your app at: https://dataguardianpro.nl"
        echo "🔓 Backup access: http://dataguardianpro.nl:5000"
    else
        echo "⚠️  Application responding with HTTP code: $HTTP_CODE"
        echo "🔧 Checking service logs..."
        journalctl -u dataguardian --no-pager -n 10
    fi
else
    echo "❌ Service failed to start. Checking logs..."
    systemctl status dataguardian --no-pager -l
    echo ""
    echo "Recent logs:"
    journalctl -u dataguardian --no-pager -n 20
fi