#!/bin/bash
#
# Ultimate Blob Removal - Remove ALL Blob References E2E
# Run this script DIRECTLY on dataguardianpro.nl server
# Date: October 19, 2025
#

set -e

echo "=========================================="
echo "Ultimate Blob Removal - E2E Fix"
echo "=========================================="
echo ""

cd /opt/dataguardian || { echo "❌ /opt/dataguardian not found"; exit 1; }

echo "📁 Working directory: $(pwd)"
echo ""

###########################################
# Step 1: Fix services/stripe_payment.py
###########################################
echo "🔧 Step 1: Fixing services/stripe_payment.py (16 scanners only)..."

python3 << 'PYTHON_STRIPE'
with open('services/stripe_payment.py', 'r') as f:
    lines = f.readlines()

new_lines = []
skip_mode = None

for line in lines:
    if 'SCAN_PRICES = {' in line or 'SCAN_PRICES={' in line:
        skip_mode = 'SCAN_PRICES'
        new_lines.extend([
            '# Pricing for each scan type (in cents EUR)\n',
            'SCAN_PRICES = {\n',
            '    # Basic Scanners\n',
            '    "Manual Upload": 900,\n',
            '    "API Scan": 1800,\n',
            '    "Code Scan": 2300,\n',
            '    "Image Scan": 2800,\n',
            '    "Database Scan": 4600,\n',
            '    "Website Scan": 2500,\n',
            '    "DPIA Scan": 3800,\n',
            '    \n',
            '    # Advanced Scanners\n',
            '    "Sustainability Scan": 3200,\n',
            '    "AI Model Scan": 4100,\n',
            '    "SOC2 Scan": 5500,\n',
            '    \n',
            '    # Enterprise Connectors\n',
            '    "Google Workspace Scan": 6800,\n',
            '    "Microsoft 365 Scan": 7500,\n',
            '    "Enterprise Scan": 8900,\n',
            '    "Salesforce Scan": 9200,\n',
            '    "Exact Online Scan": 12500,\n',
            '    "SAP Integration Scan": 15000,\n',
            '}\n'
        ])
        continue
    elif 'SCAN_PRODUCTS = {' in line or 'SCAN_PRODUCTS={' in line:
        skip_mode = 'SCAN_PRODUCTS'
        new_lines.extend([
            '\n# Product names for each scan type\n',
            'SCAN_PRODUCTS = {\n',
            '    "Manual Upload": "DataGuardian Pro Manual Upload Scanner",\n',
            '    "API Scan": "DataGuardian Pro API Scanner",\n',
            '    "Code Scan": "DataGuardian Pro Code Scanner",\n',
            '    "Image Scan": "DataGuardian Pro Image Scanner",\n',
            '    "Database Scan": "DataGuardian Pro Database Scanner",\n',
            '    "Website Scan": "DataGuardian Pro Website Scanner",\n',
            '    "DPIA Scan": "DataGuardian Pro DPIA Assessment",\n',
            '    "Sustainability Scan": "DataGuardian Pro Sustainability Scanner",\n',
            '    "AI Model Scan": "DataGuardian Pro AI Model Scanner",\n',
            '    "SOC2 Scan": "DataGuardian Pro SOC2 Scanner",\n',
            '    "Google Workspace Scan": "DataGuardian Pro Google Workspace Scanner",\n',
            '    "Microsoft 365 Scan": "DataGuardian Pro Microsoft 365 Scanner",\n',
            '    "Enterprise Scan": "DataGuardian Pro Enterprise Scanner",\n',
            '    "Salesforce Scan": "DataGuardian Pro Salesforce Scanner",\n',
            '    "Exact Online Scan": "DataGuardian Pro Exact Online Connector",\n',
            '    "SAP Integration Scan": "DataGuardian Pro SAP Integration Scanner",\n',
            '}\n'
        ])
        continue
    elif 'SCAN_DESCRIPTIONS = {' in line or 'SCAN_DESCRIPTIONS={' in line:
        skip_mode = 'SCAN_DESCRIPTIONS'
        new_lines.extend([
            '\n# Descriptions for each scan type\n',
            'SCAN_DESCRIPTIONS = {\n',
            '    "Manual Upload": "Manual file scanning for PII detection",\n',
            '    "API Scan": "API scanning for data exposure and compliance issues",\n',
            '    "Code Scan": "Comprehensive code scanning for PII and secrets detection",\n',
            '    "Image Scan": "Image scanning for faces and visual identifiers",\n',
            '    "Database Scan": "Database scanning for GDPR compliance",\n',
            '    "Website Scan": "Website scanning for cookies, trackers, and privacy policy compliance",\n',
            '    "DPIA Scan": "Data Protection Impact Assessment for GDPR Article 35 compliance",\n',
            '    "Sustainability Scan": "Cloud resource optimization and sustainability analysis",\n',
            '    "AI Model Scan": "AI model auditing for bias and GDPR compliance",\n',
            '    "SOC2 Scan": "SOC2 security and access control auditing",\n',
            '    "Google Workspace Scan": "Google Workspace organization scanning for data exposure",\n',
            '    "Microsoft 365 Scan": "Microsoft 365 tenant scanning for PII and compliance issues",\n',
            '    "Enterprise Scan": "Advanced enterprise data scanning with full connector suite",\n',
            '    "Salesforce Scan": "Salesforce CRM data scanning for customer privacy compliance",\n',
            '    "Exact Online Scan": "Direct integration scanning for Exact Online accounting data",\n',
            '    "SAP Integration Scan": "SAP ERP system integration with GDPR compliance analysis",\n',
            '}\n'
        ])
        continue
    elif skip_mode and line.strip() == '}':
        skip_mode = None
        continue
    elif skip_mode:
        continue
    else:
        new_lines.append(line)

with open('services/stripe_payment.py', 'w') as f:
    f.writelines(new_lines)

print("✅ stripe_payment.py: 16 scanners only")
PYTHON_STRIPE

###########################################
# Step 2: Ultimate app.py Blob Removal
###########################################
echo "🔧 Step 2: Removing ALL blob references from app.py..."

python3 << 'PYTHON_APP'
import re

with open('app.py', 'r') as f:
    lines = f.readlines()

new_lines = []
skip_next = False

for i, line in enumerate(lines):
    # Skip empty lines that were marked
    if skip_next:
        skip_next = False
        continue
    
    # Pattern 1: ScannerType.BLOB references
    if 'ScannerType.BLOB' in line:
        continue
    
    # Pattern 2: _('scan.blob', ...) translation functions
    if "_('scan.blob'" in line or '_("scan.blob"' in line:
        continue
    
    # Pattern 3: "Blob Scan" strings
    if '"Blob Scan"' in line or "'Blob Scan'" in line:
        continue
    
    # Pattern 4: 'blob': dictionary entries
    if ("'blob':" in line or '"blob":' in line) and ('Scanner' in line or '📄' in line):
        continue
    
    # Pattern 5: BlobScanner import
    if 'from services.blob_scanner import' in line:
        continue
    
    # Pattern 6: BlobScanner instantiation
    if 'BlobScanner(' in line:
        continue
    
    # Pattern 7: elif checks for blob
    if 'elif' in line and ('blob' in line.lower()) and ('Document' in line or 'Scanner' in line):
        continue
    
    # Pattern 8: Blob in f-strings
    if 'f"📄' in line and 'blob' in line.lower():
        continue
    
    # Keep all other lines
    new_lines.append(line)

# Clean up formatting
content = ''.join(new_lines)
content = re.sub(r',\s*,', ',', content)
content = re.sub(r'\[\s*,', '[', content)
content = re.sub(r',\s*\]', ']', content)
content = re.sub(r',\s*\}', '}', content)

with open('app.py', 'w') as f:
    f.write(content)

removed = len(lines) - len(new_lines)
print(f"✅ app.py: Removed {removed} lines containing blob references")
PYTHON_APP

###########################################
# Step 3: Verify
###########################################
echo ""
echo "🔍 Verification..."
echo ""

# Count scanners
SCANNER_COUNT=$(python3 -c "
import re
with open('services/stripe_payment.py', 'r') as f:
    content = f.read()
    match = re.search(r'SCAN_PRICES\s*=\s*\{([^}]+)\}', content, re.DOTALL)
    if match:
        print(len(re.findall(r'\"[^\"]+\"\s*:\s*\d+', match.group(1))))
    else:
        print(0)
")

echo "📊 Scanners: $SCANNER_COUNT (expected: 16)"

# Check for any blob references
BLOB_CHECK=$(grep -in "blob" app.py | grep -i "scan\|document\|📄\|blobscanner" || echo "")

if [ -n "$BLOB_CHECK" ]; then
    echo "❌ Blob references still found:"
    echo "$BLOB_CHECK"
    exit 1
else
    echo "✅ All blob references removed"
fi

if [ "$SCANNER_COUNT" -ne 16 ]; then
    echo "❌ Scanner count error"
    exit 1
else
    echo "✅ Exactly 16 scanners"
fi

###########################################
# Step 4: Docker Restart
###########################################
echo ""
echo "🔄 Restarting Docker..."
echo ""

# Find compose file
for f in docker-compose.yml docker-compose.yaml ../docker-compose.yml; do
    if [ -f "$f" ]; then
        COMPOSE="$f"
        break
    fi
done

if [ -n "$COMPOSE" ]; then
    if command -v docker-compose &>/dev/null; then
        docker-compose -f "$COMPOSE" down
        docker-compose -f "$COMPOSE" build --no-cache
        docker-compose -f "$COMPOSE" up -d
    elif docker compose version &>/dev/null 2>&1; then
        docker compose -f "$COMPOSE" down
        docker compose -f "$COMPOSE" build --no-cache
        docker compose -f "$COMPOSE" up -d
    fi
    sleep 30
else
    docker restart $(docker ps -q) 2>/dev/null || echo "Manual restart needed"
    sleep 20
fi

echo ""
echo "=========================================="
echo "✅ COMPLETE - ALL BLOB REMOVED"
echo "=========================================="
echo ""
echo "Summary:"
echo "  ✅ 16 scanners in stripe_payment.py"
echo "  ✅ All blob code removed from app.py"
echo "  ✅ Docker rebuilt & restarted"
echo ""
echo "Test: https://dataguardianpro.nl/payment_test_ideal"
echo "Hard refresh: Ctrl+Shift+R"
echo ""
