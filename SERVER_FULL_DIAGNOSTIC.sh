#!/bin/bash
################################################################################
# Complete Server Diagnostic - Find out why Scan Results is empty
################################################################################

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  DataGuardian Pro - COMPLETE SERVER DIAGNOSTIC                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}\n"

echo -e "${YELLOW}═══ 1. Check Current Code ═══${NC}"
echo ""
echo "Method signature in results_aggregator.py:"
grep -n "def get_recent_scans" /opt/dataguardian/services/results_aggregator.py | head -5

echo ""
echo "Database call in get_recent_scans:"
grep -n "_get_recent_scans_db" /opt/dataguardian/services/results_aggregator.py | head -5

echo ""
echo -e "${YELLOW}═══ 2. Check Docker Container Logs ═══${NC}"
echo ""
echo "Last 100 lines of container logs:"
docker logs dataguardian-container 2>&1 | tail -100

echo ""
echo -e "${YELLOW}═══ 3. Test Database Directly ═══${NC}"
echo ""
docker exec dataguardian-container python3 << 'PYTEST'
import psycopg2
import os
import json

try:
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    cursor = conn.cursor()
    
    # Count total scans
    cursor.execute("SELECT COUNT(*) FROM scans")
    total = cursor.fetchone()[0]
    print(f"✅ Total scans in database: {total}")
    
    # Get recent scans
    cursor.execute("""
        SELECT scan_id, scan_type, username, organization_id, created_at
        FROM scans 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    
    print("\nMost recent scans:")
    for row in cursor.fetchall():
        print(f"  - {row[0][:12]}... | {row[1]} | user: {row[2]} | org: {row[3]} | {row[4]}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Database error: {e}")
    import traceback
    traceback.print_exc()
PYTEST

echo ""
echo -e "${YELLOW}═══ 4. Test ResultsAggregator Directly ═══${NC}"
echo ""
docker exec dataguardian-container python3 << 'PYTEST'
import sys
sys.path.insert(0, '/app')

try:
    from services.results_aggregator import ResultsAggregator
    import inspect
    
    # Create aggregator
    agg = ResultsAggregator()
    
    # Check method signature
    sig = inspect.signature(agg.get_recent_scans)
    print(f"✅ get_recent_scans signature: {sig}")
    
    # Test call WITHOUT organization_id
    print("\n--- Test 1: Call without organization_id ---")
    try:
        scans1 = agg.get_recent_scans(days=30, username='vishaal314')
        print(f"✅ Returned {len(scans1)} scans")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test call WITH organization_id
    print("\n--- Test 2: Call with organization_id ---")
    try:
        scans2 = agg.get_recent_scans(days=30, username='vishaal314', organization_id='default_org')
        print(f"✅ Returned {len(scans2)} scans")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test call with no username
    print("\n--- Test 3: Call with no username filter ---")
    try:
        scans3 = agg.get_recent_scans(days=30, organization_id='default_org')
        print(f"✅ Returned {len(scans3)} scans")
        if len(scans3) > 0:
            print(f"   Sample: {scans3[0].get('scan_id', 'N/A')[:12]} - {scans3[0].get('scan_type', 'N/A')}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
except Exception as e:
    print(f"❌ Import/Setup error: {e}")
    import traceback
    traceback.print_exc()
PYTEST

echo ""
echo -e "${YELLOW}═══ 5. Check Redis Status ═══${NC}"
echo ""
if docker ps | grep -q redis; then
    echo "✅ Redis container is running"
    docker exec dataguardian-container python3 << 'PYTEST'
import redis
try:
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    if r.ping():
        print("✅ Redis connected")
        keys = r.keys('*')
        print(f"✅ Redis has {len(keys)} keys")
except Exception as e:
    print(f"❌ Redis error: {e}")
PYTEST
else
    echo "❌ Redis container is NOT running"
fi

echo ""
echo -e "${YELLOW}═══ 6. Check Environment Variables ═══${NC}"
echo ""
docker exec dataguardian-container python3 -c "
import os
print(f'DATABASE_URL: {'✅ Set' if os.getenv('DATABASE_URL') else '❌ Missing'}')
print(f'USE_FILE_STORAGE: {os.getenv('USE_FILE_STORAGE', 'Not set')}')
print(f'DATAGUARDIAN_MASTER_KEY: {'✅ Set' if os.getenv('DATAGUARDIAN_MASTER_KEY') else '❌ Missing'}')
"

echo ""
echo -e "${YELLOW}═══ 7. Simulate UI Call ═══${NC}"
echo ""
docker exec dataguardian-container python3 << 'PYTEST'
import sys
sys.path.insert(0, '/app')

# Simulate what the UI does
try:
    from services.results_aggregator import ResultsAggregator
    
    print("Simulating UI call to render_results_page()...")
    
    aggregator = ResultsAggregator()
    username = 'vishaal314'
    
    # This is what app.py does
    recent_scans = aggregator.get_recent_scans(days=30, username=username)
    
    print(f"\nResult: {len(recent_scans)} scans returned")
    
    if not recent_scans:
        print("❌ UI would show: 'No scan results available'")
    else:
        print(f"✅ UI would show: {len(recent_scans)} scans")
        print(f"   First scan: {recent_scans[0].get('scan_id', 'N/A')[:12]} - {recent_scans[0].get('scan_type', 'N/A')}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
PYTEST

echo ""
echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}DIAGNOSTIC COMPLETE - Review output above${NC}"
echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════${NC}"

