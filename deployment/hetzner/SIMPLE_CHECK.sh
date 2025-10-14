#!/bin/bash
# SIMPLE_CHECK.sh - Quick diagnostic to check why database queries fail

echo "🔍 DataGuardian Pro - Simple Diagnostic Check"
echo "Date: $(date)"
echo ""

echo "1️⃣  Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "2️⃣  Database Connection Test:"
docker exec dataguardian-container python3 << 'DBTEST'
import sys
import os

print(f"   Python version: {sys.version}")
print(f"   Python path: {sys.path}")
print(f"   Current dir: {os.getcwd()}")

# Check environment variables
db_url = os.getenv('DATABASE_URL', 'NOT_SET')
print(f"   DATABASE_URL: {db_url[:50]}..." if len(db_url) > 50 else f"   DATABASE_URL: {db_url}")

# Try to import and use ResultsAggregator
try:
    sys.path.insert(0, '/app')
    from services.results_aggregator import ResultsAggregator
    print("   ✅ ResultsAggregator import: SUCCESS")
    
    # Try to get scans
    agg = ResultsAggregator()
    print("   ✅ ResultsAggregator init: SUCCESS")
    
    scans = agg.get_user_scans('vishaal314', limit=10, organization_id='default_org')
    print(f"   ✅ Scans retrieved: {len(scans)}")
    
    if scans:
        print(f"   ✅ First scan ID: {scans[0].get('scan_id', 'N/A')[:20]}...")
        print(f"   ✅ First scan type: {scans[0].get('scanner_type', 'N/A')}")
    
except Exception as e:
    print(f"   ❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

DBTEST

echo ""
echo "3️⃣  Application Response Test:"
curl -s http://localhost:5000/_stcore/health | head -3
echo ""

echo "4️⃣  Redis Test:"
docker exec dataguardian-redis redis-cli ping
echo ""

echo "5️⃣  Recent App Logs:"
docker logs dataguardian-container --tail 20 2>&1 | tail -10
echo ""

echo "✅ Diagnostic Complete!"
