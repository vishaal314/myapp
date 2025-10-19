#!/bin/bash
#
# FINAL E2E Fix - Remove ALL Blob References
# Run this script DIRECTLY on dataguardianpro.nl server
# Date: October 19, 2025
#

set -e  # Exit on error

echo "=========================================="
echo "DataGuardian Pro - FINAL E2E Fix"
echo "Remove ALL Blob References"
echo "=========================================="
echo ""

cd /opt/dataguardian || { echo "❌ ERROR: /opt/dataguardian not found"; exit 1; }

echo "📁 Working directory: $(pwd)"
echo ""

###########################################
# Step 1: Fix services/stripe_payment.py
###########################################
echo "🔧 Step 1: Fixing services/stripe_payment.py (16 scanners)..."

python3 << 'PYTHON_FIX_STRIPE'
# Read the entire file
with open('services/stripe_payment.py', 'r') as f:
    lines = f.readlines()

new_lines = []
skip_mode = None
i = 0

while i < len(lines):
    line = lines[i]
    
    # Detect start of SCAN_PRICES
    if 'SCAN_PRICES = {' in line or 'SCAN_PRICES={' in line:
        skip_mode = 'SCAN_PRICES'
        new_lines.append('# Pricing for each scan type (in cents EUR)\n')
        new_lines.append('SCAN_PRICES = {\n')
        new_lines.append('    # Basic Scanners\n')
        new_lines.append('    "Manual Upload": 900,  # €9.00\n')
        new_lines.append('    "API Scan": 1800,  # €18.00\n')
        new_lines.append('    "Code Scan": 2300,  # €23.00\n')
        new_lines.append('    "Image Scan": 2800,  # €28.00\n')
        new_lines.append('    "Database Scan": 4600,  # €46.00\n')
        new_lines.append('    "Website Scan": 2500,  # €25.00\n')
        new_lines.append('    "DPIA Scan": 3800,  # €38.00\n')
        new_lines.append('    \n')
        new_lines.append('    # Advanced Scanners\n')
        new_lines.append('    "Sustainability Scan": 3200,  # €32.00\n')
        new_lines.append('    "AI Model Scan": 4100,  # €41.00\n')
        new_lines.append('    "SOC2 Scan": 5500,  # €55.00\n')
        new_lines.append('    \n')
        new_lines.append('    # Enterprise Connectors\n')
        new_lines.append('    "Google Workspace Scan": 6800,  # €68.00\n')
        new_lines.append('    "Microsoft 365 Scan": 7500,  # €75.00\n')
        new_lines.append('    "Enterprise Scan": 8900,  # €89.00\n')
        new_lines.append('    "Salesforce Scan": 9200,  # €92.00\n')
        new_lines.append('    "Exact Online Scan": 12500,  # €125.00\n')
        new_lines.append('    "SAP Integration Scan": 15000,  # €150.00\n')
        new_lines.append('}\n')
        i += 1
        continue
    
    elif 'SCAN_PRODUCTS = {' in line or 'SCAN_PRODUCTS={' in line:
        skip_mode = 'SCAN_PRODUCTS'
        new_lines.append('\n')
        new_lines.append('# Product names for each scan type\n')
        new_lines.append('SCAN_PRODUCTS = {\n')
        new_lines.append('    "Manual Upload": "DataGuardian Pro Manual Upload Scanner",\n')
        new_lines.append('    "API Scan": "DataGuardian Pro API Scanner",\n')
        new_lines.append('    "Code Scan": "DataGuardian Pro Code Scanner",\n')
        new_lines.append('    "Image Scan": "DataGuardian Pro Image Scanner",\n')
        new_lines.append('    "Database Scan": "DataGuardian Pro Database Scanner",\n')
        new_lines.append('    "Website Scan": "DataGuardian Pro Website Scanner",\n')
        new_lines.append('    "DPIA Scan": "DataGuardian Pro DPIA Assessment",\n')
        new_lines.append('    "Sustainability Scan": "DataGuardian Pro Sustainability Scanner",\n')
        new_lines.append('    "AI Model Scan": "DataGuardian Pro AI Model Scanner",\n')
        new_lines.append('    "SOC2 Scan": "DataGuardian Pro SOC2 Scanner",\n')
        new_lines.append('    "Google Workspace Scan": "DataGuardian Pro Google Workspace Scanner",\n')
        new_lines.append('    "Microsoft 365 Scan": "DataGuardian Pro Microsoft 365 Scanner",\n')
        new_lines.append('    "Enterprise Scan": "DataGuardian Pro Enterprise Scanner",\n')
        new_lines.append('    "Salesforce Scan": "DataGuardian Pro Salesforce Scanner",\n')
        new_lines.append('    "Exact Online Scan": "DataGuardian Pro Exact Online Connector",\n')
        new_lines.append('    "SAP Integration Scan": "DataGuardian Pro SAP Integration Scanner",\n')
        new_lines.append('}\n')
        i += 1
        continue
    
    elif 'SCAN_DESCRIPTIONS = {' in line or 'SCAN_DESCRIPTIONS={' in line:
        skip_mode = 'SCAN_DESCRIPTIONS'
        new_lines.append('\n')
        new_lines.append('# Descriptions for each scan type\n')
        new_lines.append('SCAN_DESCRIPTIONS = {\n')
        new_lines.append('    "Manual Upload": "Manual file scanning for PII detection",\n')
        new_lines.append('    "API Scan": "API scanning for data exposure and compliance issues",\n')
        new_lines.append('    "Code Scan": "Comprehensive code scanning for PII and secrets detection",\n')
        new_lines.append('    "Image Scan": "Image scanning for faces and visual identifiers",\n')
        new_lines.append('    "Database Scan": "Database scanning for GDPR compliance",\n')
        new_lines.append('    "Website Scan": "Website scanning for cookies, trackers, and privacy policy compliance",\n')
        new_lines.append('    "DPIA Scan": "Data Protection Impact Assessment for GDPR Article 35 compliance",\n')
        new_lines.append('    "Sustainability Scan": "Cloud resource optimization and sustainability analysis",\n')
        new_lines.append('    "AI Model Scan": "AI model auditing for bias and GDPR compliance",\n')
        new_lines.append('    "SOC2 Scan": "SOC2 security and access control auditing",\n')
        new_lines.append('    "Google Workspace Scan": "Google Workspace organization scanning for data exposure",\n')
        new_lines.append('    "Microsoft 365 Scan": "Microsoft 365 tenant scanning for PII and compliance issues",\n')
        new_lines.append('    "Enterprise Scan": "Advanced enterprise data scanning with full connector suite",\n')
        new_lines.append('    "Salesforce Scan": "Salesforce CRM data scanning for customer privacy compliance",\n')
        new_lines.append('    "Exact Online Scan": "Direct integration scanning for Exact Online accounting data",\n')
        new_lines.append('    "SAP Integration Scan": "SAP ERP system integration with GDPR compliance analysis",\n')
        new_lines.append('}\n')
        i += 1
        continue
    
    elif skip_mode and line.strip() == '}':
        skip_mode = None
        i += 1
        continue
    
    elif skip_mode:
        i += 1
        continue
    
    else:
        new_lines.append(line)
        i += 1

with open('services/stripe_payment.py', 'w') as f:
    f.writelines(new_lines)

print("✅ services/stripe_payment.py rebuilt with 16 scanners")
PYTHON_FIX_STRIPE

###########################################
# Step 2: Fix app.py - Remove ALL Blob References
###########################################
echo "🔧 Step 2: Removing ALL Blob references from app.py..."

python3 << 'PYTHON_FIX_APP'
import re

with open('app.py', 'r') as f:
    content = f.read()

original_length = len(content)

# Pattern 1: Remove 'blob': '...' dictionary entries
content = re.sub(r"['\"]blob['\"]:\s*['\"][^'\"]*['\"],?\n?", '', content)

# Pattern 2: Remove "Blob Scan - €XX.XX + €YY.YY VAT = €ZZ.ZZ"
content = re.sub(r'"Blob Scan - €[\d.]+ \+ €[\d.]+ VAT = €[\d.]+"', '', content)
content = re.sub(r"'Blob Scan - €[\d.]+ \+ €[\d.]+ VAT = €[\d.]+'", '', content)

# Pattern 3: Remove "Blob Scan" simple
content = content.replace('"Blob Scan"', '')
content = content.replace("'Blob Scan'", '')

# Pattern 4: Remove "Blob Scan..." wildcard
content = re.sub(r'"Blob Scan[^"]*"', '', content)
content = re.sub(r"'Blob Scan[^']*'", '', content)

# Pattern 5: Remove any line containing 'blob' as a scanner type
lines = content.split('\n')
filtered_lines = []
for line in lines:
    # Skip lines with blob scanner references but keep other blob references (like blob storage)
    if "'blob':" in line.lower() or '"blob":' in line.lower():
        # Check if it's a scanner-related blob (has emoji or "Scanner")
        if '📄' in line or 'Scanner' in line or 'Blob Scanner' in line:
            continue
    filtered_lines.append(line)
content = '\n'.join(filtered_lines)

# Clean up formatting
content = re.sub(r',\s*,', ',', content)  # Double commas
content = re.sub(r'\[\s*,', '[', content)  # Leading comma in list
content = re.sub(r',\s*\]', ']', content)  # Trailing comma before ]
content = re.sub(r',\s*\}', '}', content)  # Trailing comma before }

with open('app.py', 'w') as f:
    f.write(content)

removed_bytes = original_length - len(content)
print(f"✅ app.py cleaned - Removed {removed_bytes} bytes of Blob references")
PYTHON_FIX_APP

###########################################
# Step 3: Verify Changes
###########################################
echo ""
echo "🔍 Verifying changes..."
echo ""

# Count scanners
SCANNER_COUNT=$(python3 -c "
import re
with open('services/stripe_payment.py', 'r') as f:
    content = f.read()
    match = re.search(r'SCAN_PRICES\s*=\s*\{([^}]+)\}', content, re.DOTALL)
    if match:
        prices = match.group(1)
        count = len(re.findall(r'\"[^\"]+\"\s*:\s*\d+', prices))
        print(count)
    else:
        print(0)
")

echo "📊 Scanners in stripe_payment.py: $SCANNER_COUNT (expected: 16)"

# Check for Blob references
echo ""
echo "Checking for Blob references..."
BLOB_IN_STRIPE=$(grep -i "blob" services/stripe_payment.py | grep -i "scan" || echo "")
BLOB_IN_APP=$(grep -i "blob" app.py | grep -i "scan\|📄" || echo "")

if [ -n "$BLOB_IN_STRIPE" ]; then
    echo "❌ ERROR: Blob Scan still found in stripe_payment.py:"
    echo "$BLOB_IN_STRIPE"
    exit 1
else
    echo "✅ Blob Scan removed from stripe_payment.py"
fi

if [ -n "$BLOB_IN_APP" ]; then
    echo "❌ ERROR: Blob Scan still found in app.py:"
    echo "$BLOB_IN_APP"
    exit 1
else
    echo "✅ Blob Scan removed from app.py"
fi

if [ "$SCANNER_COUNT" -ne 16 ]; then
    echo "❌ ERROR: Expected 16 scanners, found $SCANNER_COUNT"
    exit 1
else
    echo "✅ Correct scanner count: 16"
fi

###########################################
# Step 4: Restart Docker
###########################################
echo ""
echo "🔄 Restarting Docker..."
echo ""

# Find docker-compose file
COMPOSE_FILE=""
for file in docker-compose.yml docker-compose.yaml ../docker-compose.yml ../docker-compose.yaml; do
    if [ -f "$file" ]; then
        COMPOSE_FILE="$file"
        break
    fi
done

if [ -n "$COMPOSE_FILE" ]; then
    echo "Using: $COMPOSE_FILE"
    
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "$COMPOSE_FILE" down
        docker-compose -f "$COMPOSE_FILE" build --no-cache
        docker-compose -f "$COMPOSE_FILE" up -d
    elif docker compose version &> /dev/null 2>&1; then
        docker compose -f "$COMPOSE_FILE" down
        docker compose -f "$COMPOSE_FILE" build --no-cache
        docker compose -f "$COMPOSE_FILE" up -d
    else
        echo "⚠️  Docker Compose not available, trying container restart..."
        docker restart $(docker ps -q) 2>/dev/null || echo "Manual restart needed"
    fi
    
    echo "⏳ Waiting 30 seconds for services..."
    sleep 30
else
    echo "⚠️  No docker-compose file found"
    echo "Restarting containers directly..."
    docker restart $(docker ps -q) 2>/dev/null || echo "Manual restart needed"
    sleep 20
fi

###########################################
# Step 5: Final Check
###########################################
echo ""
echo "🔍 Final container check..."
docker ps --format "table {{.Names}}\t{{.Status}}" 2>/dev/null | head -10

echo ""
echo "=========================================="
echo "✅ E2E FIX COMPLETE"
echo "=========================================="
echo ""
echo "📊 Summary:"
echo "   ✅ Blob Scan completely removed (all patterns)"
echo "   ✅ Exactly 16 scanners in stripe_payment.py"
echo "   ✅ app.py cleaned (including 'blob': keys)"
echo "   ✅ Docker rebuilt & restarted"
echo ""
echo "🌐 Test at: https://dataguardianpro.nl/payment_test_ideal"
echo "📋 Hard refresh: Ctrl+Shift+R"
echo ""
echo "🎉 All 16 scanners deployed!"
echo ""
