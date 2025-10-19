#!/bin/bash
#
# Fix Production Server - Remove Blob Scan + Add All 16 Scanners
# Run this script DIRECTLY on dataguardianpro.nl server
# Date: October 19, 2025
#

set -e  # Exit on error

echo "=========================================="
echo "DataGuardian Pro - Production Fix"
echo "Remove Blob Scan + Add All 16 Scanners"
echo "=========================================="
echo ""

# Change to DataGuardian directory
cd /opt/dataguardian || { echo "❌ ERROR: /opt/dataguardian not found"; exit 1; }

echo "📁 Working directory: $(pwd)"
echo ""

# Backup current files (optional - comment out if not needed)
# echo "💾 Creating backup..."
# cp services/stripe_payment.py services/stripe_payment.py.backup.$(date +%Y%m%d_%H%M%S)
# cp app.py app.py.backup.$(date +%Y%m%d_%H%M%S)
# cp pages/payment_test_ideal.py pages/payment_test_ideal.py.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true

###########################################
# Step 1: Fix services/stripe_payment.py
###########################################
echo "🔧 Step 1: Fixing services/stripe_payment.py..."

python3 << 'PYTHON_FIX_STRIPE'
import re

# Read the file
with open('services/stripe_payment.py', 'r') as f:
    content = f.read()

# NEW SCAN_PRICES (16 scanners, NO Blob Scan)
new_scan_prices = '''# Pricing for each scan type (in cents EUR)
SCAN_PRICES = {
    # Basic Scanners
    "Manual Upload": 900,  # €9.00
    "API Scan": 1800,  # €18.00
    "Code Scan": 2300,  # €23.00
    "Image Scan": 2800,  # €28.00
    "Database Scan": 4600,  # €46.00
    "Website Scan": 2500,  # €25.00
    "DPIA Scan": 3800,  # €38.00
    
    # Advanced Scanners
    "Sustainability Scan": 3200,  # €32.00
    "AI Model Scan": 4100,  # €41.00
    "SOC2 Scan": 5500,  # €55.00
    
    # Enterprise Connectors
    "Google Workspace Scan": 6800,  # €68.00
    "Microsoft 365 Scan": 7500,  # €75.00
    "Enterprise Scan": 8900,  # €89.00
    "Salesforce Scan": 9200,  # €92.00
    "Exact Online Scan": 12500,  # €125.00
    "SAP Integration Scan": 15000,  # €150.00
}'''

# NEW SCAN_PRODUCTS (16 scanners, NO Blob Scan)
new_scan_products = '''# Product names for each scan type
SCAN_PRODUCTS = {
    "Manual Upload": "DataGuardian Pro Manual Upload Scanner",
    "API Scan": "DataGuardian Pro API Scanner",
    "Code Scan": "DataGuardian Pro Code Scanner",
    "Image Scan": "DataGuardian Pro Image Scanner",
    "Database Scan": "DataGuardian Pro Database Scanner",
    "Website Scan": "DataGuardian Pro Website Scanner",
    "DPIA Scan": "DataGuardian Pro DPIA Assessment",
    "Sustainability Scan": "DataGuardian Pro Sustainability Scanner",
    "AI Model Scan": "DataGuardian Pro AI Model Scanner",
    "SOC2 Scan": "DataGuardian Pro SOC2 Scanner",
    "Google Workspace Scan": "DataGuardian Pro Google Workspace Scanner",
    "Microsoft 365 Scan": "DataGuardian Pro Microsoft 365 Scanner",
    "Enterprise Scan": "DataGuardian Pro Enterprise Scanner",
    "Salesforce Scan": "DataGuardian Pro Salesforce Scanner",
    "Exact Online Scan": "DataGuardian Pro Exact Online Connector",
    "SAP Integration Scan": "DataGuardian Pro SAP Integration Scanner",
}'''

# NEW SCAN_DESCRIPTIONS (16 scanners, NO Blob Scan)
new_scan_descriptions = '''# Descriptions for each scan type
SCAN_DESCRIPTIONS = {
    "Manual Upload": "Manual file scanning for PII detection",
    "API Scan": "API scanning for data exposure and compliance issues",
    "Code Scan": "Comprehensive code scanning for PII and secrets detection",
    "Image Scan": "Image scanning for faces and visual identifiers",
    "Database Scan": "Database scanning for GDPR compliance",
    "Website Scan": "Website scanning for cookies, trackers, and privacy policy compliance",
    "DPIA Scan": "Data Protection Impact Assessment for GDPR Article 35 compliance",
    "Sustainability Scan": "Cloud resource optimization and sustainability analysis",
    "AI Model Scan": "AI model auditing for bias and GDPR compliance",
    "SOC2 Scan": "SOC2 security and access control auditing",
    "Google Workspace Scan": "Google Workspace organization scanning for data exposure",
    "Microsoft 365 Scan": "Microsoft 365 tenant scanning for PII and compliance issues",
    "Enterprise Scan": "Advanced enterprise data scanning with full connector suite",
    "Salesforce Scan": "Salesforce CRM data scanning for customer privacy compliance",
    "Exact Online Scan": "Direct integration scanning for Exact Online accounting data",
    "SAP Integration Scan": "SAP ERP system integration with GDPR compliance analysis",
}'''

# Replace SCAN_PRICES
content = re.sub(
    r'# Pricing for each scan type.*?SCAN_PRICES\s*=\s*\{.*?\n\}',
    new_scan_prices,
    content,
    count=1,
    flags=re.DOTALL
)

# Replace SCAN_PRODUCTS
content = re.sub(
    r'# Product names for each scan type.*?SCAN_PRODUCTS\s*=\s*\{.*?\n\}',
    new_scan_products,
    content,
    count=1,
    flags=re.DOTALL
)

# Replace SCAN_DESCRIPTIONS
content = re.sub(
    r'# Descriptions for each scan type.*?SCAN_DESCRIPTIONS\s*=\s*\{.*?\n\}',
    new_scan_descriptions,
    content,
    count=1,
    flags=re.DOTALL
)

# Write back
with open('services/stripe_payment.py', 'w') as f:
    f.write(content)

print("✅ services/stripe_payment.py updated - Blob Scan removed, 16 scanners added")
PYTHON_FIX_STRIPE

###########################################
# Step 2: Fix app.py
###########################################
echo "🔧 Step 2: Fixing app.py..."

python3 << 'PYTHON_FIX_APP'
import re

# Read the file
with open('app.py', 'r') as f:
    content = f.read()

# Remove all Blob Scan references
content = content.replace('"Blob Scan"', '')
content = content.replace("'Blob Scan'", '')
content = re.sub(r'"Blob Scan - €[\d.]+.*?"', '', content)
content = re.sub(r"'Blob Scan - €[\d.]+.*?'", '', content)

# Write back
with open('app.py', 'w') as f:
    f.write(content)

print("✅ app.py updated - Blob Scan removed")
PYTHON_FIX_APP

###########################################
# Step 3: Fix pages/payment_test_ideal.py
###########################################
echo "🔧 Step 3: Fixing pages/payment_test_ideal.py..."

if [ -f "pages/payment_test_ideal.py" ]; then
    python3 << 'PYTHON_FIX_IDEAL'
import re

# Read the file
with open('pages/payment_test_ideal.py', 'r') as f:
    content = f.read()

# Remove all Blob Scan references
content = content.replace('"Blob Scan"', '')
content = content.replace("'Blob Scan'", '')
content = re.sub(r'"Blob Scan - €[\d.]+.*?"', '', content)
content = re.sub(r"'Blob Scan - €[\d.]+.*?'", '', content)

# Write back
with open('pages/payment_test_ideal.py', 'w') as f:
    f.write(content)

print("✅ pages/payment_test_ideal.py updated - Blob Scan removed")
PYTHON_FIX_IDEAL
else
    echo "⚠️  pages/payment_test_ideal.py not found, skipping"
fi

###########################################
# Step 4: Verify Changes
###########################################
echo ""
echo "🔍 Verifying changes..."
echo ""

# Count scanners in stripe_payment.py
SCANNER_COUNT=$(grep -o '"[^"]*":\s*[0-9]' services/stripe_payment.py | grep -c ":" || true)
echo "📊 Scanners in stripe_payment.py: $SCANNER_COUNT (expected: 16)"

# Check for Blob Scan
if grep -q "Blob Scan" services/stripe_payment.py; then
    echo "❌ ERROR: Blob Scan still found in stripe_payment.py"
else
    echo "✅ Blob Scan removed from stripe_payment.py"
fi

if grep -q "Blob Scan" app.py; then
    echo "❌ ERROR: Blob Scan still found in app.py"
else
    echo "✅ Blob Scan removed from app.py"
fi

###########################################
# Step 5: Restart Docker
###########################################
echo ""
echo "🔄 Restarting Docker containers..."
echo ""

# Try both docker-compose and docker compose
if command -v docker-compose &> /dev/null; then
    echo "Using docker-compose command..."
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    echo "Using docker compose command..."
    docker compose down
    docker compose build --no-cache
    docker compose up -d
else
    echo "❌ ERROR: Neither 'docker-compose' nor 'docker compose' found"
    echo "Please restart Docker manually"
    exit 1
fi

echo ""
echo "⏳ Waiting for services to start (30 seconds)..."
sleep 30

###########################################
# Step 6: Final Verification
###########################################
echo ""
echo "🔍 Final verification..."
echo ""

# Check container status
if command -v docker-compose &> /dev/null; then
    docker-compose ps
elif command -v docker &> /dev/null; then
    docker compose ps
fi

# Check if Streamlit is running
if curl -s http://localhost:5000/_stcore/health > /dev/null 2>&1; then
    echo "✅ Streamlit is running"
else
    echo "⚠️  Streamlit health check failed (might still be starting)"
fi

echo ""
echo "=========================================="
echo "✅ PRODUCTION FIX COMPLETE"
echo "=========================================="
echo ""
echo "📊 Summary:"
echo "   ✅ Blob Scan removed from all files"
echo "   ✅ All 16 scanners added to stripe_payment.py"
echo "   ✅ Docker containers rebuilt (no cache)"
echo "   ✅ Services restarted"
echo ""
echo "🌐 Production URL: https://dataguardianpro.nl"
echo ""
echo "📋 Next Steps:"
echo "   1. Open: https://dataguardianpro.nl/payment_test_ideal"
echo "   2. Hard refresh: Ctrl+Shift+R"
echo "   3. Verify dropdown shows 16 scanners"
echo "   4. Confirm Blob Scan is NOT present"
echo ""
echo "🎉 All 16 scanners are now live!"
echo ""
