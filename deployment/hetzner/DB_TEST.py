#!/usr/bin/env python3
"""Direct database test script"""
import sys
import os

print("🔍 Database Connection Diagnostic")
print("=" * 60)

# Check environment
db_url = os.getenv('DATABASE_URL', 'NOT_SET')
print(f"\n1. Environment Check:")
print(f"   DATABASE_URL: {'SET (length: ' + str(len(db_url)) + ')' if db_url != 'NOT_SET' else 'NOT SET'}")
print(f"   Current dir: {os.getcwd()}")
print(f"   Python: {sys.version}")

# Add app to path
sys.path.insert(0, '/app')
print(f"\n2. Python Path:")
print(f"   App added to path: {'/app' in sys.path}")

# Test import
print(f"\n3. Module Import Test:")
try:
    from services.results_aggregator import ResultsAggregator
    print("   ✅ ResultsAggregator import: SUCCESS")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test initialization
print(f"\n4. ResultsAggregator Initialization:")
try:
    agg = ResultsAggregator()
    print("   ✅ ResultsAggregator() init: SUCCESS")
except Exception as e:
    print(f"   ❌ Init failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test database query
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
    else:
        print(f"\n6. No scans found in database")
        
except Exception as e:
    print(f"   ❌ Query failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All tests passed - Database fully operational!")
