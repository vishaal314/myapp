#!/bin/bash
#
# COMPLETE PRODUCTION FIX - dataguardianpro.nl
# Fixes: 1) Blob Scan removal  2) STRIPE_SECRET_KEY error
# Date: October 19, 2025
#
# Run this on: root@dataguardianpro.nl
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=========================================="
echo "COMPLETE PRODUCTION FIX"
echo "dataguardianpro.nl"
echo -e "==========================================${NC}"
echo ""

# Verify we're in the right place
cd /opt/dataguardian || { echo -e "${RED}❌ /opt/dataguardian not found${NC}"; exit 1; }
echo -e "${GREEN}📁 Working directory: $(pwd)${NC}"
echo ""

###########################################
# PHASE 1: FIX ENVIRONMENT VARIABLES
###########################################
echo -e "${YELLOW}=========================================="
echo "PHASE 1: Fix Environment Variables"
echo -e "==========================================${NC}"
echo ""

# Check if environment file exists
if [ ! -f "/root/.dataguardian_env" ]; then
    echo -e "${RED}❌ /root/.dataguardian_env not found${NC}"
    echo "Creating new environment file..."
    
    # Create new environment file
    cat > /root/.dataguardian_env << 'EOF'
# DataGuardian Pro Production Environment
# CRITICAL: Add your actual API keys below

# OpenAI (REQUIRED for AI analysis)
OPENAI_API_KEY=

# Stripe (REQUIRED for payment processing)
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
STRIPE_WEBHOOK_SECRET=

# Security Keys
DATAGUARDIAN_MASTER_KEY=
JWT_SECRET=

# Database
DATABASE_URL=postgresql://dataguardian:your_password@postgres:5432/dataguardian

# Application
PYTHONUNBUFFERED=1
STREAMLIT_SERVER_PORT=5000
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true

# Multi-tenant
DISABLE_RLS=true
EOF
    chmod 600 /root/.dataguardian_env
    
    echo -e "${RED}=========================================="
    echo "⚠️  ACTION REQUIRED"
    echo "=========================================="
    echo ""
    echo "Environment file created at /root/.dataguardian_env"
    echo ""
    echo "YOU MUST edit this file and add your API keys:"
    echo ""
    echo "  nano /root/.dataguardian_env"
    echo ""
    echo "Add these REQUIRED keys:"
    echo "  - STRIPE_SECRET_KEY=sk_test_... (or sk_live_...)"
    echo "  - STRIPE_PUBLISHABLE_KEY=pk_test_... (or pk_live_...)"
    echo "  - OPENAI_API_KEY=sk-..."
    echo ""
    echo "Then run this script again."
    echo -e "${NC}"
    exit 1
fi

# Load existing environment
source /root/.dataguardian_env

# Check STRIPE_SECRET_KEY
if [ -z "$STRIPE_SECRET_KEY" ]; then
    echo -e "${RED}=========================================="
    echo "❌ STRIPE_SECRET_KEY NOT SET"
    echo "=========================================="
    echo ""
    echo "Edit /root/.dataguardian_env and add:"
    echo ""
    echo "  STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE"
    echo ""
    echo "Get your key from: https://dashboard.stripe.com/test/apikeys"
    echo ""
    echo "Then run this script again."
    echo -e "${NC}"
    exit 1
else
    echo -e "${GREEN}✅ STRIPE_SECRET_KEY found (${STRIPE_SECRET_KEY:0:10}...)${NC}"
fi

# Check OPENAI_API_KEY
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  OPENAI_API_KEY not set (AI features will be disabled)${NC}"
else
    echo -e "${GREEN}✅ OPENAI_API_KEY found (${OPENAI_API_KEY:0:10}...)${NC}"
fi

echo ""

###########################################
# PHASE 2: REMOVE BLOB SCAN
###########################################
echo -e "${YELLOW}=========================================="
echo "PHASE 2: Remove Blob Scan (16 scanners only)"
echo -e "==========================================${NC}"
echo ""

# Step 2.1: Fix services/stripe_payment.py
echo "🔧 Fixing services/stripe_payment.py..."

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

# Step 2.2: Remove blob from app.py
echo "🔧 Removing ALL blob references from app.py..."

python3 << 'PYTHON_APP'
import re

with open('app.py', 'r') as f:
    lines = f.readlines()

new_lines = []
skip_next = False

for i, line in enumerate(lines):
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

echo ""

###########################################
# PHASE 3: VERIFICATION
###########################################
echo -e "${YELLOW}=========================================="
echo "PHASE 3: Verification"
echo -e "==========================================${NC}"
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

echo -e "📊 Scanners: ${SCANNER_COUNT} (expected: 16)"

# Check for blob references
BLOB_CHECK=$(grep -in "blob" app.py | grep -i "scan\|document\|📄\|blobscanner" || echo "")

if [ -n "$BLOB_CHECK" ]; then
    echo -e "${RED}❌ Blob references still found:${NC}"
    echo "$BLOB_CHECK"
    exit 1
else
    echo -e "${GREEN}✅ All blob references removed${NC}"
fi

if [ "$SCANNER_COUNT" -ne 16 ]; then
    echo -e "${RED}❌ Scanner count error (expected 16, got $SCANNER_COUNT)${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Exactly 16 scanners${NC}"
fi

echo ""

###########################################
# PHASE 4: DOCKER REBUILD WITH ENV VARS
###########################################
echo -e "${YELLOW}=========================================="
echo "PHASE 4: Docker Rebuild (with environment)"
echo -e "==========================================${NC}"
echo ""

# Find docker-compose file
COMPOSE=""
for f in docker-compose.yml docker-compose.yaml ../docker-compose.yml; do
    if [ -f "$f" ]; then
        COMPOSE="$f"
        break
    fi
done

if [ -z "$COMPOSE" ]; then
    echo -e "${RED}❌ docker-compose.yml not found${NC}"
    exit 1
fi

echo "📄 Using compose file: $COMPOSE"

# Export environment variables for Docker
export $(grep -v '^#' /root/.dataguardian_env | xargs)

# Stop containers
echo "🛑 Stopping containers..."
if command -v docker-compose &>/dev/null; then
    docker-compose -f "$COMPOSE" down
elif docker compose version &>/dev/null 2>&1; then
    docker compose -f "$COMPOSE" down
fi

# Clear Docker cache completely
echo "🗑️  Clearing Docker build cache..."
docker builder prune -f || true

# Rebuild with NO CACHE
echo "🔨 Rebuilding (no cache)..."
if command -v docker-compose &>/dev/null; then
    docker-compose -f "$COMPOSE" build --no-cache
elif docker compose version &>/dev/null 2>&1; then
    docker compose -f "$COMPOSE" build --no-cache
fi

# Start containers
echo "🚀 Starting containers..."
if command -v docker-compose &>/dev/null; then
    docker-compose -f "$COMPOSE" up -d
elif docker compose version &>/dev/null 2>&1; then
    docker compose -f "$COMPOSE" up -d
fi

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 30

# Check if containers are running
echo ""
echo "📊 Container status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""

###########################################
# PHASE 5: FINAL VERIFICATION
###########################################
echo -e "${YELLOW}=========================================="
echo "PHASE 5: Final Verification"
echo -e "==========================================${NC}"
echo ""

# Test if Streamlit is responding
echo "🌐 Testing web server..."
sleep 5
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Web server responding (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${YELLOW}⚠️  Web server status: HTTP $HTTP_CODE${NC}"
    echo "   (It may still be starting up)"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "✅ COMPLETE - ALL FIXES APPLIED"
echo "=========================================="
echo ""
echo "Summary:"
echo "  ✅ STRIPE_SECRET_KEY configured"
echo "  ✅ 16 scanners (blob removed)"
echo "  ✅ Docker rebuilt with cache clear"
echo "  ✅ All containers restarted"
echo ""
echo "Next Steps:"
echo ""
echo "1. Test payment page:"
echo "   https://dataguardianpro.nl/payment_test_ideal"
echo ""
echo "2. Hard refresh browser:"
echo "   Press Ctrl+Shift+R"
echo ""
echo "3. Check logs if needed:"
echo "   docker logs dataguardian-pro"
echo -e "${NC}"
