#!/bin/bash
# Complete Database Test - Self-contained script

echo "🔍 DataGuardian Pro - Complete Database Test"
echo "Date: $(date)"
echo "=" * 70
echo ""

# Create the Python test script inline
cat > /tmp/db_test_temp.py << 'PYTHON_SCRIPT'
#!/usr/bin/env python3
import sys
import os

print("🔍 Database Connection Diagnostic")
print("=" * 60)

db_url = os.getenv('DATABASE_URL', 'NOT_SET')
print(f"\n1. Environment Check:")
print(f"   DATABASE_URL: {'SET (length: ' + str(len(db_url)) + ')' if db_url != 'NOT_SET' else 'NOT SET'}")
print(f"   Current dir: {os.getcwd()}")

sys.path.insert(0, '/app')
print(f"\n2. Python Path:")
print(f"   App added to path: {'/app' in sys.path}")

print(f"\n3. Module Import Test:")
try:
    from services.results_aggregator import ResultsAggregator
    print("   ✅ ResultsAggregator import: SUCCESS")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

print(f"\n4. ResultsAggregator Initialization:")
try:
    agg = ResultsAggregator()
    print("   ✅ ResultsAggregator() init: SUCCESS")
except Exception as e:
    print(f"   ❌ Init failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\n5. Database Query Test:")
try:
    scans = agg.get_user_scans('vishaal314', limit=10, organization_id='default_org')
    print(f"   ✅ Query executed: SUCCESS")
    print(f"   ✅ Scans found: {len(scans)}")
    
    if scans:
        scan = scans[0]
        print(f"\n6. Sample Scan Data:")
        print(f"   Scan ID: {scan.get('scan_id', 'N/A')[:30]}...")
        print(f"   Scanner Type: {scan.get('scanner_type', 'N/A')}")
        print(f"   Findings: {len(scan.get('findings', []))}")
        print(f"   Compliance: {scan.get('compliance_score', 'N/A')}%")
        
        # Count scanner types
        all_scans = agg.get_user_scans('vishaal314', limit=1000, organization_id='default_org')
        scanner_types = {}
        total_pii = 0
        
        for s in all_scans:
            stype = s.get('scanner_type', 'unknown')
            scanner_types[stype] = scanner_types.get(stype, 0) + 1
            total_pii += len(s.get('findings', []))
        
        print(f"\n7. Full Database Statistics:")
        print(f"   Total Scans: {len(all_scans)}")
        print(f"   Total PII Items: {total_pii}")
        print(f"   Scanner Types:")
        for stype, count in sorted(scanner_types.items()):
            print(f"      - {stype}: {count} scans")
    else:
        print(f"\n6. ⚠️  No scans found in database")
        
except Exception as e:
    print(f"   ❌ Query failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ Database Test Complete - All Systems Operational!")
PYTHON_SCRIPT

# Copy script into container
echo "Copying test script into container..."
docker cp /tmp/db_test_temp.py dataguardian-container:/tmp/db_test.py

# Run the test
echo ""
docker exec dataguardian-container python3 /tmp/db_test.py

# Cleanup
docker exec dataguardian-container rm /tmp/db_test.py 2>/dev/null
rm /tmp/db_test_temp.py 2>/dev/null

echo ""
echo "=" * 70
echo "✅ Complete Database Test Finished!"
