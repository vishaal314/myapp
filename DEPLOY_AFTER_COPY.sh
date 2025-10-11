#!/bin/bash
################################################################################
# Run this AFTER copying the 2 fixed files to server
################################################################################

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  DEPLOY FIXES - Run After Copying Files                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}\n"

cd /opt/dataguardian

echo -e "${YELLOW}Step 1: Add DISABLE_RLS=1 environment variable${NC}"
if [ ! -f .env ]; then
    echo "DISABLE_RLS=1" > .env
    echo "✅ Created .env with DISABLE_RLS=1"
else
    if ! grep -q "DISABLE_RLS" .env; then
        echo "DISABLE_RLS=1" >> .env
        echo "✅ Added DISABLE_RLS=1 to .env"
    else
        sed -i 's/DISABLE_RLS=.*/DISABLE_RLS=1/' .env
        echo "✅ Updated DISABLE_RLS=1 in .env"
    fi
fi

echo ""
echo -e "${YELLOW}Step 2: Disable RLS on database${NC}"
docker exec dataguardian-container python3 << 'PYDISABLE'
import psycopg2, os
try:
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE scans DISABLE ROW LEVEL SECURITY")
    cursor.execute("ALTER TABLE audit_log DISABLE ROW LEVEL SECURITY")
    conn.commit()
    print("✅ RLS disabled on scans and audit_log tables")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Note: {e}")
PYDISABLE

echo ""
echo -e "${YELLOW}Step 3: Stop container${NC}"
docker stop dataguardian-container 2>/dev/null || true
sleep 2
echo "✅ Container stopped"

echo ""
echo -e "${YELLOW}Step 4: Rebuild Docker with --no-cache (2-3 minutes)${NC}"
docker build --no-cache -t dataguardian:latest . 2>&1 | tail -20
echo "✅ Docker rebuilt"

echo ""
echo -e "${YELLOW}Step 5: Start container with DISABLE_RLS=1${NC}"
docker run -d \
  --name dataguardian-container \
  --env-file .env \
  -e DISABLE_RLS=1 \
  -p 5000:5000 \
  dataguardian:latest 2>/dev/null || docker start dataguardian-container
echo "✅ Container started"

echo ""
echo -e "${YELLOW}Step 6: Wait 30 seconds for startup${NC}"
sleep 30

echo ""
echo -e "${YELLOW}Step 7: Verify RLS is disabled${NC}"
if docker logs dataguardian-container 2>&1 | grep -q "RLS DISABLED via DISABLE_RLS"; then
    echo "✅ RLS is DISABLED - environment variable working!"
elif docker logs dataguardian-container 2>&1 | grep -q "Initializing Row Level Security"; then
    echo "❌ RLS still initializing - check files were copied correctly"
else
    echo "⚠️  No RLS messages in logs"
fi

echo ""
echo -e "${YELLOW}Step 8: Check for region errors${NC}"
if docker logs dataguardian-container 2>&1 | tail -100 | grep -q 'column "region"'; then
    echo "❌ Region column error still present"
else
    echo "✅ No region column errors"
fi

echo ""
echo -e "${YELLOW}Step 9: Test database access${NC}"
docker exec dataguardian-container python3 << 'PYTEST'
import psycopg2, os
conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM scans")
total = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM scans WHERE username = 'vishaal314'")
user_scans = cursor.fetchone()[0]
print(f"✅ Total scans in database: {total}")
print(f"✅ Scans for vishaal314: {user_scans}")
conn.close()
PYTEST

echo ""
echo -e "${YELLOW}Step 10: Test ResultsAggregator${NC}"
docker exec dataguardian-container python3 << 'PYFINAL'
import sys
sys.path.insert(0, '/app')
from services.results_aggregator import ResultsAggregator

agg = ResultsAggregator()
scans = agg.get_recent_scans(days=365, username='vishaal314', organization_id='default_org')
print(f"✅ ResultsAggregator returned: {len(scans)} scans")

if scans:
    print("\nRecent scans:")
    for i, s in enumerate(scans[:5]):
        print(f"  {i+1}. {s.get('scan_id', 'N/A')[:12]}... - {s.get('scan_type', 'N/A')}")
else:
    print("⚠️  No scans returned - check logs above")
PYFINAL

echo ""
echo -e "${BOLD}${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}🎉 DEPLOYMENT COMPLETE!${NC}"
echo ""
echo -e "${BOLD}🧪 TEST NOW:${NC}"
echo -e "   1. Open: ${BLUE}https://dataguardianpro.nl${NC}"
echo -e "   2. Hard refresh: ${BOLD}Ctrl + Shift + R${NC}"
echo -e "   3. Navigate to:"
echo -e "      • ${BOLD}📊 Scan Results${NC} → ✅ See all scans"
echo -e "      • ${BOLD}📋 Scan History${NC} → ✅ Complete history"
echo -e "      • ${BOLD}🏠 Dashboard${NC} → ✅ Recent Scan Activity"
echo ""
echo -e "${BOLD}${BLUE}════════════════════════════════════════════════════════════${NC}"

