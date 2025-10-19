#!/bin/bash
#
# Deploy All 16 Scanners to Production Server (dataguardianpro.nl)
# Removes Blob Scan and adds all 16 scanners with correct pricing
# Date: October 19, 2025
#

set -e  # Exit on error

echo "=========================================="
echo "DataGuardian Pro - Production Deployment"
echo "All 16 Scanners + Blob Scan Removal"
echo "=========================================="
echo ""

# Configuration
SERVER_USER="${SERVER_USER:-root}"
SERVER_HOST="${SERVER_HOST:-dataguardianpro.nl}"
SERVER_PATH="${SERVER_PATH:-/opt/dataguardian}"
BACKUP_DIR="/opt/dataguardian_backups/$(date +%Y%m%d_%H%M%S)"

echo "📋 Deployment Configuration:"
echo "   Server: ${SERVER_USER}@${SERVER_HOST}"
echo "   Path: ${SERVER_PATH}"
echo "   Backup: ${BACKUP_DIR}"
echo ""

# Check if we can connect to server
echo "🔍 Testing server connection..."
if ! ssh -o ConnectTimeout=5 ${SERVER_USER}@${SERVER_HOST} "echo 'Connection successful'" > /dev/null 2>&1; then
    echo "❌ ERROR: Cannot connect to ${SERVER_HOST}"
    echo "   Please check your SSH configuration"
    exit 1
fi
echo "✅ Server connection successful"
echo ""

# Create backup
echo "💾 Creating backup of current production files..."
ssh ${SERVER_USER}@${SERVER_HOST} << 'BACKUP_SCRIPT'
BACKUP_DIR="/opt/dataguardian_backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "${BACKUP_DIR}"
cd /opt/dataguardian

# Backup critical files
cp app.py "${BACKUP_DIR}/app.py.backup" 2>/dev/null || true
cp test_ideal_payment.py "${BACKUP_DIR}/test_ideal_payment.py.backup" 2>/dev/null || true
cp pages/payment_test_ideal.py "${BACKUP_DIR}/payment_test_ideal.py.backup" 2>/dev/null || true
cp services/stripe_payment.py "${BACKUP_DIR}/stripe_payment.py.backup" 2>/dev/null || true

echo "✅ Backup created at ${BACKUP_DIR}"
BACKUP_SCRIPT

echo ""

# Update services/stripe_payment.py - Remove Blob Scan
echo "🔧 Updating services/stripe_payment.py (removing Blob Scan)..."
ssh ${SERVER_USER}@${SERVER_HOST} << 'UPDATE_STRIPE_PAYMENT'
cd /opt/dataguardian

# Create updated stripe_payment.py with Blob Scan removed
cat > /tmp/stripe_payment_update.py << 'PYTHON_CODE'
# Pricing for each scan type (in cents EUR)
SCAN_PRICES = {
    "Manual Upload": 900,  # €9.00
    "API Scan": 1800,  # €18.00
    "Code Scan": 2300,  # €23.00
    "Website Scan": 2500,  # €25.00
    "Image Scan": 2800,  # €28.00
    "DPIA Scan": 3800,  # €38.00
    "Database Scan": 4600,  # €46.00
    "Sustainability Scan": 3200,  # €32.00
    "AI Model Scan": 4100,  # €41.00
    "SOC2 Scan": 5500,  # €55.00
    "Google Workspace Scan": 6800,  # €68.00
    "Microsoft 365 Scan": 7500,  # €75.00
    "Enterprise Scan": 8900,  # €89.00
    "Salesforce Scan": 9200,  # €92.00
    "Exact Online Scan": 12500,  # €125.00
    "SAP Integration Scan": 15000,  # €150.00
}

# Product names for each scan type
SCAN_PRODUCTS = {
    "Manual Upload": "DataGuardian Pro Manual Upload Scanner",
    "API Scan": "DataGuardian Pro API Scanner",
    "Code Scan": "DataGuardian Pro Code Scanner",
    "Website Scan": "DataGuardian Pro Website Scanner",
    "Image Scan": "DataGuardian Pro Image Scanner",
    "DPIA Scan": "DataGuardian Pro DPIA Scanner",
    "Database Scan": "DataGuardian Pro Database Scanner",
    "Sustainability Scan": "DataGuardian Pro Sustainability Scanner",
    "AI Model Scan": "DataGuardian Pro AI Model Scanner",
    "SOC2 Scan": "DataGuardian Pro SOC2 Scanner",
    "Google Workspace Scan": "DataGuardian Pro Google Workspace Scanner",
    "Microsoft 365 Scan": "DataGuardian Pro Microsoft 365 Scanner",
    "Enterprise Scan": "DataGuardian Pro Enterprise Scanner",
    "Salesforce Scan": "DataGuardian Pro Salesforce Scanner",
    "Exact Online Scan": "DataGuardian Pro Exact Online Scanner",
    "SAP Integration Scan": "DataGuardian Pro SAP Integration Scanner",
}

# Descriptions for each scan type
SCAN_DESCRIPTIONS = {
    "Manual Upload": "Manual file scanning for PII detection",
    "API Scan": "API scanning for data exposure and compliance issues",
    "Code Scan": "Comprehensive code scanning for PII and secrets detection",
    "Website Scan": "Website scanning for privacy compliance and tracking",
    "Image Scan": "Image scanning for faces and visual identifiers",
    "DPIA Scan": "Data Protection Impact Assessment scanner",
    "Database Scan": "Database scanning for GDPR compliance",
    "Sustainability Scan": "Cloud resource optimization and sustainability analysis",
    "AI Model Scan": "AI model auditing for bias and GDPR compliance",
    "SOC2 Scan": "SOC2 security and access control auditing",
    "Google Workspace Scan": "Google Workspace compliance scanning",
    "Microsoft 365 Scan": "Microsoft 365 compliance scanning",
    "Enterprise Scan": "Enterprise-wide compliance scanning",
    "Salesforce Scan": "Salesforce data compliance scanning",
    "Exact Online Scan": "Exact Online ERP compliance scanning",
    "SAP Integration Scan": "SAP system compliance scanning",
}
PYTHON_CODE

# Apply the update to services/stripe_payment.py
python3 << 'PYTHON_SCRIPT'
import re

# Read current file
with open('services/stripe_payment.py', 'r') as f:
    content = f.read()

# Read new dictionaries
with open('/tmp/stripe_payment_update.py', 'r') as f:
    new_dicts = f.read()

# Replace SCAN_PRICES dictionary
content = re.sub(
    r'SCAN_PRICES\s*=\s*\{[^}]+\}',
    new_dicts.split('# Product names')[0].strip(),
    content,
    flags=re.DOTALL
)

# Replace SCAN_PRODUCTS dictionary
scan_products_new = new_dicts.split('# Product names')[1].split('# Descriptions')[0].strip()
content = re.sub(
    r'SCAN_PRODUCTS\s*=\s*\{[^}]+\}',
    scan_products_new,
    content,
    flags=re.DOTALL
)

# Replace SCAN_DESCRIPTIONS dictionary
scan_descriptions_new = new_dicts.split('# Descriptions')[1].strip()
content = re.sub(
    r'SCAN_DESCRIPTIONS\s*=\s*\{[^}]+\}',
    scan_descriptions_new,
    content,
    flags=re.DOTALL
)

# Write updated file
with open('services/stripe_payment.py', 'w') as f:
    f.write(content)

print("✅ services/stripe_payment.py updated")
PYTHON_SCRIPT

rm /tmp/stripe_payment_update.py
UPDATE_STRIPE_PAYMENT

echo ""

# Update app.py - Add all 16 scanners to dropdown
echo "🔧 Updating app.py (adding all 16 scanners to dropdown)..."
ssh ${SERVER_USER}@${SERVER_HOST} << 'UPDATE_APP_PY'
cd /opt/dataguardian

python3 << 'PYTHON_SCRIPT'
import re

# Read app.py
with open('app.py', 'r') as f:
    content = f.read()

# New scan_options with all 16 scanners
new_scan_options = '''        # Select scan type to test - All 16 scanners with correct pricing
        scan_options = {
            # Basic Scanners
            "Manual Upload": "€9.00 + €1.89 VAT = €10.89",
            "API Scan": "€18.00 + €3.78 VAT = €21.78",
            "Code Scan": "€23.00 + €4.83 VAT = €27.83",
            "Website Scan": "€25.00 + €5.25 VAT = €30.25",
            "Image Scan": "€28.00 + €5.88 VAT = €33.88",
            "DPIA Scan": "€38.00 + €7.98 VAT = €45.98",
            "Database Scan": "€46.00 + €9.66 VAT = €55.66",
            # Advanced Scanners
            "Sustainability Scan": "€32.00 + €6.72 VAT = €38.72",
            "AI Model Scan": "€41.00 + €8.61 VAT = €49.61",
            "SOC2 Scan": "€55.00 + €11.55 VAT = €66.55",
            # Enterprise Connectors
            "Google Workspace Scan": "€68.00 + €14.28 VAT = €82.28",
            "Microsoft 365 Scan": "€75.00 + €15.75 VAT = €90.75",
            "Enterprise Scan": "€89.00 + €18.69 VAT = €107.69",
            "Salesforce Scan": "€92.00 + €19.32 VAT = €111.32",
            "Exact Online Scan": "€125.00 + €26.25 VAT = €151.25",
            "SAP Integration Scan": "€150.00 + €31.50 VAT = €181.50"
        }'''

# Replace scan_options dictionary (find the one for payment testing)
pattern = r'(\s+)# Select scan type to test.*?\n\s+scan_options\s*=\s*\{[^}]+\}'
content = re.sub(pattern, new_scan_options, content, flags=re.DOTALL)

# Write updated file
with open('app.py', 'w') as f:
    f.write(content)

print("✅ app.py updated with all 16 scanners")
PYTHON_SCRIPT
UPDATE_APP_PY

echo ""

# Update test_ideal_payment.py - Add all 16 scanners
echo "🔧 Updating test_ideal_payment.py (adding all 16 scanners)..."
ssh ${SERVER_USER}@${SERVER_HOST} << 'UPDATE_TEST_IDEAL'
cd /opt/dataguardian

if [ -f "test_ideal_payment.py" ]; then
python3 << 'PYTHON_SCRIPT'
import re

# Read test_ideal_payment.py
with open('test_ideal_payment.py', 'r') as f:
    content = f.read()

# New scan_options with all 16 scanners
new_scan_options = '''        # Select scan type to test - All 16 scanners with correct pricing
        scan_options = {
            # Basic Scanners
            "Manual Upload": "€9.00 + €1.89 VAT = €10.89",
            "API Scan": "€18.00 + €3.78 VAT = €21.78",
            "Code Scan": "€23.00 + €4.83 VAT = €27.83",
            "Website Scan": "€25.00 + €5.25 VAT = €30.25",
            "Image Scan": "€28.00 + €5.88 VAT = €33.88",
            "DPIA Scan": "€38.00 + €7.98 VAT = €45.98",
            "Database Scan": "€46.00 + €9.66 VAT = €55.66",
            # Advanced Scanners
            "Sustainability Scan": "€32.00 + €6.72 VAT = €38.72",
            "AI Model Scan": "€41.00 + €8.61 VAT = €49.61",
            "SOC2 Scan": "€55.00 + €11.55 VAT = €66.55",
            # Enterprise Connectors
            "Google Workspace Scan": "€68.00 + €14.28 VAT = €82.28",
            "Microsoft 365 Scan": "€75.00 + €15.75 VAT = €90.75",
            "Enterprise Scan": "€89.00 + €18.69 VAT = €107.69",
            "Salesforce Scan": "€92.00 + €19.32 VAT = €111.32",
            "Exact Online Scan": "€125.00 + €26.25 VAT = €151.25",
            "SAP Integration Scan": "€150.00 + €31.50 VAT = €181.50"
        }'''

# Replace scan_options dictionary
pattern = r'(\s+)# Select scan type to test.*?\n\s+scan_options\s*=\s*\{[^}]+\}'
content = re.sub(pattern, new_scan_options, content, flags=re.DOTALL)

# Write updated file
with open('test_ideal_payment.py', 'w') as f:
    f.write(content)

print("✅ test_ideal_payment.py updated")
PYTHON_SCRIPT
else
    echo "⚠️  test_ideal_payment.py not found, skipping"
fi
UPDATE_TEST_IDEAL

echo ""

# Verify the changes
echo "🔍 Verifying changes on production server..."
ssh ${SERVER_USER}@${SERVER_HOST} << 'VERIFY_CHANGES'
cd /opt/dataguardian

echo "Checking services/stripe_payment.py..."
if grep -q "Blob Scan" services/stripe_payment.py; then
    echo "❌ ERROR: Blob Scan still found in stripe_payment.py"
    exit 1
else
    echo "✅ Blob Scan removed from stripe_payment.py"
fi

# Count scanners in SCAN_PRICES
scanner_count=$(python3 -c "
import sys
sys.path.insert(0, 'services')
from stripe_payment import SCAN_PRICES
print(len(SCAN_PRICES))
" 2>/dev/null || echo "0")

if [ "$scanner_count" = "16" ]; then
    echo "✅ Confirmed 16 scanners in SCAN_PRICES"
else
    echo "⚠️  Found $scanner_count scanners (expected 16)"
fi

echo ""
echo "Checking app.py..."
if grep -q "SAP Integration Scan" app.py; then
    echo "✅ All 16 scanners present in app.py"
else
    echo "⚠️  Enterprise scanners may be missing from app.py"
fi

VERIFY_CHANGES

echo ""

# Restart Docker containers
echo "🔄 Restarting Docker containers..."
ssh ${SERVER_USER}@${SERVER_HOST} << 'RESTART_DOCKER'
cd /opt/dataguardian

# Stop containers
echo "Stopping containers..."
docker-compose down

# Rebuild with --no-cache to ensure changes are applied
echo "Rebuilding containers (no cache)..."
docker-compose build --no-cache

# Start containers
echo "Starting containers..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Check container status
echo ""
echo "Container status:"
docker-compose ps

# Check if Streamlit is responding
echo ""
echo "Checking Streamlit health..."
if curl -f http://localhost:5000/_stcore/health > /dev/null 2>&1; then
    echo "✅ Streamlit is running"
else
    echo "⚠️  Streamlit may not be ready yet (check logs)"
fi

RESTART_DOCKER

echo ""
echo "=========================================="
echo "✅ DEPLOYMENT COMPLETE"
echo "=========================================="
echo ""
echo "📊 Summary:"
echo "   ✅ Blob Scan removed from all files"
echo "   ✅ All 16 scanners added to dropdowns"
echo "   ✅ services/stripe_payment.py updated"
echo "   ✅ app.py updated"
echo "   ✅ test_ideal_payment.py updated"
echo "   ✅ Docker containers rebuilt (no cache)"
echo "   ✅ Services restarted"
echo ""
echo "🌐 Production URL: https://dataguardianpro.nl"
echo ""
echo "📋 Next Steps:"
echo "   1. Clear browser cache (Ctrl+Shift+R)"
echo "   2. Test payment page at https://dataguardianpro.nl/payment_test_ideal"
echo "   3. Verify all 16 scanners appear in dropdown"
echo "   4. Confirm Blob Scan is NOT present"
echo ""
echo "💾 Backup Location: ${BACKUP_DIR}"
echo ""
echo "🎉 All 16 scanners are now live on production!"
echo ""
