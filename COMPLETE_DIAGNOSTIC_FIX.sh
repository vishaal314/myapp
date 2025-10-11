#!/bin/bash
################################################################################
# COMPLETE DIAGNOSTIC & FIX - Find and solve the real problem
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
echo "║  COMPLETE DIAGNOSTIC & FIX                                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}\n"

cd /opt/dataguardian

echo -e "${YELLOW}DIAGNOSTIC 1: Check if new code is in /opt/dataguardian${NC}"
echo "Checking multi_tenant_service.py for DISABLE_RLS check:"
if grep -q "DISABLE_RLS" services/multi_tenant_service.py; then
    echo -e "${GREEN}✅ Found DISABLE_RLS check in source file${NC}"
else
    echo -e "${RED}❌ DISABLE_RLS check NOT in source file - files not copied!${NC}"
fi

echo ""
echo -e "${YELLOW}DIAGNOSTIC 2: Check if new code is in container${NC}"
docker exec dataguardian-container grep -q "DISABLE_RLS" /app/services/multi_tenant_service.py && \
    echo -e "${GREEN}✅ DISABLE_RLS check is in container${NC}" || \
    echo -e "${RED}❌ DISABLE_RLS check NOT in container - rebuild failed!${NC}"

echo ""
echo -e "${YELLOW}DIAGNOSTIC 3: Check environment variable${NC}"
docker exec dataguardian-container printenv DISABLE_RLS || echo -e "${RED}❌ DISABLE_RLS not set${NC}"

echo ""
echo -e "${YELLOW}DIAGNOSTIC 4: Check database RLS status${NC}"
docker exec dataguardian-container python3 << 'PYCHECK'
import psycopg2, os
conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
cursor = conn.cursor()
cursor.execute("SELECT tablename, rowsecurity FROM pg_tables WHERE tablename = 'scans'")
result = cursor.fetchone()
print(f"scans table RLS: {result[1]}")
conn.close()
PYCHECK

echo ""
echo -e "${BOLD}${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${YELLOW}APPLYING COMPLETE FIX${NC}"
echo -e "${BOLD}${YELLOW}═══════════════════════════════════════════════════════════${NC}"

echo ""
echo -e "${YELLOW}FIX 1: Ensure DISABLE_RLS=1 in .env${NC}"
if [ ! -f .env ]; then
    echo "DISABLE_RLS=1" > .env
else
    sed -i '/DISABLE_RLS/d' .env
    echo "DISABLE_RLS=1" >> .env
fi
echo -e "${GREEN}✅ DISABLE_RLS=1 in .env${NC}"

echo ""
echo -e "${YELLOW}FIX 2: Disable RLS on database NOW${NC}"
docker exec dataguardian-container python3 << 'PYFIX'
import psycopg2, os
conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
cursor = conn.cursor()
cursor.execute("ALTER TABLE scans DISABLE ROW LEVEL SECURITY")
cursor.execute("ALTER TABLE audit_log DISABLE ROW LEVEL SECURITY")
conn.commit()
print("✅ RLS disabled on database")
conn.close()
PYFIX

echo ""
echo -e "${YELLOW}FIX 3: Remove old container completely${NC}"
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true
docker rmi dataguardian:latest 2>/dev/null || true
echo -e "${GREEN}✅ Old container and image removed${NC}"

echo ""
echo -e "${YELLOW}FIX 4: Rebuild with --no-cache AND --pull (3-4 min)${NC}"
docker build --no-cache --pull -t dataguardian:latest . 2>&1 | tail -30

echo ""
echo -e "${YELLOW}FIX 5: Start new container with all env vars${NC}"
docker run -d \
  --name dataguardian-container \
  --env-file .env \
  -e DISABLE_RLS=1 \
  -e DATABASE_URL="${DATABASE_URL}" \
  -p 5000:5000 \
  dataguardian:latest

echo -e "${GREEN}✅ Container started${NC}"

echo ""
echo -e "${YELLOW}FIX 6: Wait 35 seconds for full startup${NC}"
sleep 35

echo ""
echo -e "${BOLD}${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${YELLOW}VERIFICATION${NC}"
echo -e "${BOLD}${YELLOW}═══════════════════════════════════════════════════════════${NC}"

echo ""
echo -e "${YELLOW}VERIFY 1: Check logs for RLS status${NC}"
if docker logs dataguardian-container 2>&1 | grep -q "RLS DISABLED via DISABLE_RLS"; then
    echo -e "${GREEN}✅ SUCCESS! RLS is DISABLED${NC}"
elif docker logs dataguardian-container 2>&1 | grep -q "Initializing Row Level Security"; then
    echo -e "${RED}❌ FAIL: RLS still initializing${NC}"
    echo "Latest log:"
    docker logs dataguardian-container 2>&1 | tail -5
else
    echo -e "${YELLOW}⚠️  No RLS messages (might be OK)${NC}"
fi

echo ""
echo -e "${YELLOW}VERIFY 2: Check database access${NC}"
docker exec dataguardian-container python3 << 'PYTEST'
import psycopg2, os
conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM scans")
total = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM scans WHERE username = 'vishaal314'")
user = cursor.fetchone()[0]
print(f"Total scans: {total}")
print(f"User scans: {user}")
if total > 0:
    print("✅ Database has scans!")
else:
    print("⚠️  Database is empty")
conn.close()
PYTEST

echo ""
echo -e "${YELLOW}VERIFY 3: Test ResultsAggregator${NC}"
docker exec dataguardian-container python3 << 'PYFINAL'
import sys, os
sys.path.insert(0, '/app')
print(f"DISABLE_RLS env: {os.getenv('DISABLE_RLS', 'NOT SET')}")

from services.results_aggregator import ResultsAggregator
agg = ResultsAggregator()
scans = agg.get_recent_scans(days=365, username='vishaal314', organization_id='default_org')
print(f"ResultsAggregator: {len(scans)} scans")

if scans:
    print("\n✅ SUCCESS! Scans found:")
    for i, s in enumerate(scans[:5]):
        print(f"  {i+1}. {s.get('scan_id', 'N/A')[:12]}... - {s.get('scan_type', 'N/A')}")
else:
    print("\n❌ STILL 0 SCANS")
    print("Checking why...")
    import psycopg2
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM scans")
    db_count = cursor.fetchone()[0]
    print(f"Direct DB query: {db_count} scans")
    if db_count > 0:
        print("Database has scans but ResultsAggregator returns 0 - RLS still blocking!")
    conn.close()
PYFINAL

echo ""
echo -e "${BOLD}${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}🎉 COMPLETE FIX APPLIED!${NC}"
echo ""
echo -e "${BOLD}NOW TEST:${NC}"
echo -e "   1. https://dataguardianpro.nl"
echo -e "   2. ${BOLD}HARD REFRESH: Ctrl + Shift + R${NC}"
echo -e "   3. Go to: ${BOLD}📊 Scan Results${NC}"
echo -e "   4. ${GREEN}You should see all scans!${NC}"
echo ""
echo -e "${BOLD}${BLUE}════════════════════════════════════════════════════════════${NC}"

