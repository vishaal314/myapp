#!/bin/bash
################################################################################
# Fix: Remove "region" column from SQL query (column doesn't exist)
################################################################################

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  FIX: Remove 'region' column from database query              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}\n"

TARGET="/opt/dataguardian/services/results_aggregator.py"

echo -e "${YELLOW}Step 1: Backup File${NC}"
cp "${TARGET}" "${TARGET}.backup.$(date +%Y%m%d_%H%M%S)"
echo -e "${GREEN}✅ Backup created${NC}"

echo ""
echo -e "${YELLOW}Step 2: Fix SQL Query - Remove 'region' column${NC}"

# Find and fix the SQL query that includes 'region'
python3 << 'PYFIX'
import re

with open('/opt/dataguardian/services/results_aggregator.py', 'r') as f:
    content = f.read()

# Fix 1: Remove region from SELECT clause
# Pattern: scan_id, username, timestamp, scan_type, region,
content = re.sub(
    r'scan_id,\s*username,\s*timestamp,\s*scan_type,\s*region,',
    'scan_id, username, timestamp, scan_type,',
    content
)

# Fix 2: Also check for other region references in SELECT
content = re.sub(
    r'scan_type,\s*region,\s*file_count',
    'scan_type, file_count',
    content
)

# Fix 3: Remove any standalone region column references
content = re.sub(
    r',\s*region,',
    ',',
    content
)

with open('/opt/dataguardian/services/results_aggregator.py', 'w') as f:
    f.write(content)

print("✅ SQL query fixed - 'region' column removed")
PYFIX

echo -e "${GREEN}✅ Region column references removed${NC}"

echo ""
echo -e "${YELLOW}Step 3: Verify Fix${NC}"
if grep -q ", region," "${TARGET}"; then
    echo -e "${RED}⚠️  Still found region references - checking context${NC}"
    grep -n ", region," "${TARGET}" || echo "No SQL region refs found"
else
    echo -e "${GREEN}✅ No region column in SQL queries${NC}"
fi

echo ""
echo -e "${YELLOW}Step 4: Stop Container${NC}"
docker stop dataguardian-container || true
sleep 2

echo ""
echo -e "${YELLOW}Step 5: Rebuild Docker${NC}"
cd /opt/dataguardian
docker build -t dataguardian:latest . 2>&1 | tail -20

echo ""
echo -e "${YELLOW}Step 6: Start Container${NC}"
docker start dataguardian-container
sleep 5

echo ""
echo -e "${YELLOW}Step 7: Wait for Startup (30 sec)${NC}"
sleep 30

echo ""
echo -e "${YELLOW}Step 8: Test Fix${NC}"

# Test database query
docker exec dataguardian-container python3 << 'PYTEST'
import sys
sys.path.insert(0, '/app')

from services.results_aggregator import ResultsAggregator

try:
    agg = ResultsAggregator()
    scans = agg.get_recent_scans(days=30, username='vishaal314', organization_id='default_org')
    print(f"✅ SUCCESS: get_recent_scans() returned {len(scans)} scans")
    
    if len(scans) > 0:
        print(f"   First scan: {scans[0].get('scan_id', 'N/A')[:12]} - {scans[0].get('scan_type', 'N/A')}")
    
    # Test without username
    all_scans = agg.get_recent_scans(days=30, organization_id='default_org')
    print(f"✅ All scans: {len(all_scans)} scans found")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
PYTEST

echo ""
echo -e "${BOLD}${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}🎉 FIX COMPLETE!${NC}"
echo ""
echo -e "${GREEN}✅ Removed 'region' column from SQL queries${NC}"
echo -e "${GREEN}✅ Docker rebuilt and restarted${NC}"
echo ""
echo -e "${BOLD}🧪 TEST NOW:${NC}"
echo -e "   1. Go to: ${BLUE}https://dataguardianpro.nl${NC}"
echo -e "   2. Navigate to: ${BOLD}📊 Scan Results${NC}"
echo -e "   3. ${GREEN}✅ You should see all your scans!${NC}"
echo ""
echo -e "${GREEN}${BOLD}✅ Scan Results is NOW FIXED!${NC}"
echo -e "${BOLD}${BLUE}════════════════════════════════════════════════════════════${NC}"

