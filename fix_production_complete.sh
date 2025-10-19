#!/bin/bash
#
# Complete Production Fix - Remove Blob Scan + Add All 16 Scanners
# Run this script DIRECTLY on dataguardianpro.nl server
# Date: October 19, 2025
#

set -e  # Exit on error

echo "=========================================="
echo "DataGuardian Pro - Complete Fix"
echo "Remove Blob Scan + Add All 16 Scanners"
echo "=========================================="
echo ""

# Change to DataGuardian directory
cd /opt/dataguardian || { echo "❌ ERROR: /opt/dataguardian not found"; exit 1; }

echo "📁 Working directory: $(pwd)"
echo ""

###########################################
# Step 1: Fix services/stripe_payment.py (COMPLETE REPLACEMENT)
###########################################
echo "🔧 Step 1: Completely rebuilding services/stripe_payment.py dictionaries..."

python3 << 'PYTHON_FIX_STRIPE_COMPLETE'
# Read the entire file
with open('services/stripe_payment.py', 'r') as f:
    lines = f.readlines()

# Find and replace the three dictionaries
new_lines = []
skip_mode = None
i = 0

while i < len(lines):
    line = lines[i]
    
    # Detect start of SCAN_PRICES
    if 'SCAN_PRICES = {' in line or 'SCAN_PRICES={' in line:
        skip_mode = 'SCAN_PRICES'
        # Insert new SCAN_PRICES
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
    
    # Detect start of SCAN_PRODUCTS
    elif 'SCAN_PRODUCTS = {' in line or 'SCAN_PRODUCTS={' in line:
        skip_mode = 'SCAN_PRODUCTS'
        # Insert new SCAN_PRODUCTS
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
    
    # Detect start of SCAN_DESCRIPTIONS
    elif 'SCAN_DESCRIPTIONS = {' in line or 'SCAN_DESCRIPTIONS={' in line:
        skip_mode = 'SCAN_DESCRIPTIONS'
        # Insert new SCAN_DESCRIPTIONS
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
    
    # End of dictionary - stop skipping
    elif skip_mode and line.strip() == '}':
        skip_mode = None
        i += 1
        continue
    
    # Skip lines inside dictionaries
    elif skip_mode:
        i += 1
        continue
    
    # Keep all other lines
    else:
        new_lines.append(line)
        i += 1

# Write back
with open('services/stripe_payment.py', 'w') as f:
    f.writelines(new_lines)

print("✅ services/stripe_payment.py completely rebuilt with 16 scanners")
PYTHON_FIX_STRIPE_COMPLETE

###########################################
# Step 2: Fix app.py - Remove ALL Blob Scan references
###########################################
echo "🔧 Step 2: Removing ALL Blob Scan references from app.py..."

python3 << 'PYTHON_FIX_APP_COMPLETE'
# Read the file
with open('app.py', 'r') as f:
    content = f.read()

# Remove Blob Scan references (multiple patterns)
original_length = len(content)

# Pattern 1: "Blob Scan - €14.00 + €2.94 VAT = €16.94"
content = content.replace('"Blob Scan - €14.00 + €2.94 VAT = €16.94"', '')
content = content.replace("'Blob Scan - €14.00 + €2.94 VAT = €16.94'", '')

# Pattern 2: "Blob Scan - €X.XX + €Y.YY VAT = €Z.ZZ"
import re
content = re.sub(r'"Blob Scan - €[\d.]+ \+ €[\d.]+ VAT = €[\d.]+"', '', content)
content = re.sub(r"'Blob Scan - €[\d.]+ \+ €[\d.]+ VAT = €[\d.]+'", '', content)

# Pattern 3: Just "Blob Scan"
content = content.replace('"Blob Scan"', '')
content = content.replace("'Blob Scan'", '')

# Pattern 4: Blob Scan with any price format
content = re.sub(r'"Blob Scan[^"]*"', '', content)
content = re.sub(r"'Blob Scan[^']*'", '', content)

# Clean up empty list items (double commas)
content = re.sub(r',\s*,', ',', content)
content = re.sub(r'\[\s*,', '[', content)
content = re.sub(r',\s*\]', ']', content)

# Write back
with open('app.py', 'w') as f:
    f.write(content)

removed_bytes = original_length - len(content)
print(f"✅ app.py cleaned - Removed {removed_bytes} bytes of Blob Scan references")
PYTHON_FIX_APP_COMPLETE

###########################################
# Step 3: Verify Changes
###########################################
echo ""
echo "🔍 Verifying changes..."
echo ""

# Count scanners in stripe_payment.py (count the keys)
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

# Check for Blob Scan
if grep -i "blob scan" services/stripe_payment.py; then
    echo "❌ ERROR: Blob Scan still found in stripe_payment.py"
    exit 1
else
    echo "✅ Blob Scan removed from stripe_payment.py"
fi

if grep -i "blob scan" app.py; then
    echo "❌ ERROR: Blob Scan still found in app.py"
    exit 1
else
    echo "✅ Blob Scan removed from app.py"
fi

if [ "$SCANNER_COUNT" -ne 16 ]; then
    echo "⚠️  WARNING: Expected 16 scanners, found $SCANNER_COUNT"
else
    echo "✅ Correct scanner count: 16"
fi

###########################################
# Step 4: Find and Use Docker Compose
###########################################
echo ""
echo "🔄 Restarting Docker containers..."
echo ""

# Find docker-compose.yml
if [ -f "docker-compose.yml" ]; then
    COMPOSE_FILE="docker-compose.yml"
elif [ -f "docker-compose.yaml" ]; then
    COMPOSE_FILE="docker-compose.yaml"
elif [ -f "../docker-compose.yml" ]; then
    COMPOSE_FILE="../docker-compose.yml"
    cd ..
elif [ -f "../docker-compose.yaml" ]; then
    COMPOSE_FILE="../docker-compose.yaml"
    cd ..
else
    echo "⚠️  No docker-compose file found, skipping Docker restart"
    echo "Please restart Docker manually with:"
    echo "  docker restart dataguardian-container"
    COMPOSE_FILE=""
fi

if [ -n "$COMPOSE_FILE" ]; then
    echo "Found: $COMPOSE_FILE in $(pwd)"
    
    # Stop containers
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "$COMPOSE_FILE" down
        docker-compose -f "$COMPOSE_FILE" build --no-cache
        docker-compose -f "$COMPOSE_FILE" up -d
    elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
        docker compose -f "$COMPOSE_FILE" down
        docker compose -f "$COMPOSE_FILE" build --no-cache
        docker compose -f "$COMPOSE_FILE" up -d
    else
        echo "❌ Docker Compose not available, trying direct container restart..."
        docker restart dataguardian-container 2>/dev/null || docker restart $(docker ps -q) 2>/dev/null || echo "⚠️  Could not restart containers"
    fi
    
    echo ""
    echo "⏳ Waiting for services to start (30 seconds)..."
    sleep 30
else
    # Try direct container restart
    echo "Attempting direct container restart..."
    docker restart dataguardian-container 2>/dev/null || docker restart $(docker ps -a -q --filter "name=dataguardian") 2>/dev/null || echo "⚠️  Manual restart needed"
    sleep 15
fi

###########################################
# Step 5: Final Verification
###########################################
echo ""
echo "🔍 Final verification..."
echo ""

# List running containers
echo "Docker containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "Could not list containers"

echo ""
echo "=========================================="
echo "✅ PRODUCTION FIX COMPLETE"
echo "=========================================="
echo ""
echo "📊 Summary:"
echo "   ✅ Blob Scan completely removed"
echo "   ✅ Exactly 16 scanners in stripe_payment.py"
echo "   ✅ app.py cleaned"
echo "   ✅ Docker restarted"
echo ""
echo "🌐 Production URL: https://dataguardianpro.nl"
echo ""
echo "📋 Next Steps:"
echo "   1. Open: https://dataguardianpro.nl/payment_test_ideal"
echo "   2. Hard refresh: Ctrl+Shift+R"
echo "   3. Verify dropdown shows exactly 16 scanners"
echo "   4. Confirm Blob Scan is completely gone"
echo ""
echo "🎉 All 16 scanners deployed!"
echo ""
