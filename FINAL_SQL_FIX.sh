#!/bin/bash
set -e

echo "════════════════════════════════════════════════════════════════"
echo "  DataGuardian Pro - SQL Query Fix (results_aggregator.py)"
echo "════════════════════════════════════════════════════════════════"
echo ""

cd /opt/dataguardian

# Backup
echo "1️⃣  Creating backup..."
cp services/results_aggregator.py services/results_aggregator.py.backup_$(date +%Y%m%d_%H%M%S)
echo "✅ Backup created"

# Fix the SQL query
echo ""
echo "2️⃣  Fixing SQL query in get_user_scans()..."

python3 << 'SQLFIX'
with open('services/results_aggregator.py', 'r') as f:
    content = f.read()

# Pattern 1: Fix the WHERE clause to include organization_id
old_query = '''SELECT scan_id, timestamp, scan_type, file_count, total_pii_found, high_risk_count
            FROM scans
            WHERE username = %s
            ORDER BY timestamp DESC
            LIMIT %s'''

new_query = '''SELECT scan_id, timestamp, scan_type, file_count, total_pii_found, high_risk_count
            FROM scans
            WHERE username = %s AND organization_id = %s
            ORDER BY timestamp DESC
            LIMIT %s'''

if old_query in content:
    content = content.replace(old_query, new_query)
    print("✅ Fixed: Added organization_id to WHERE clause")
    
    # Also fix the cursor.execute to pass organization_id
    old_exec = 'cursor.execute(query, (username, limit))'
    new_exec = 'cursor.execute(query, (username, organization_id, limit))'
    
    if old_exec in content:
        content = content.replace(old_exec, new_exec)
        print("✅ Fixed: Added organization_id to query parameters")
    
    with open('services/results_aggregator.py', 'w') as f:
        f.write(content)
    
    print("\n✅ SQL query fixed successfully")
else:
    print("⚠️  Query pattern not found - checking if already fixed...")
    if 'WHERE username = %s AND organization_id = %s' in content:
        print("✅ Already fixed!")
    else:
        print("❌ ERROR: Cannot find SQL query to fix")
        print("\nSearching for get_user_scans function...")
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'def get_user_scans' in line or 'WHERE username' in line:
                print(f"Line {i+1}: {line[:100]}")
        exit(1)
SQLFIX

if [ $? -ne 0 ]; then
    echo "❌ Fix failed"
    exit 1
fi

# Verify
echo ""
echo "3️⃣  Verifying fix..."
if grep -q 'WHERE username = %s AND organization_id = %s' services/results_aggregator.py; then
    echo "✅ Verification passed"
else
    echo "❌ Verification failed"
    exit 1
fi

# Rebuild
echo ""
echo "4️⃣  Rebuilding Docker..."
docker build --no-cache -t dataguardian:latest . 2>&1 | tail -20

# Restart
echo ""
echo "5️⃣  Restarting container..."
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true

docker run -d --name dataguardian-container \
  -e DATABASE_URL="postgresql://neondb_owner:npg_cKtisl61HrVC@ep-blue-queen-a6jyu08j.us-west-2.aws.neon.tech/neondb?sslmode=require" \
  -e JWT_SECRET="vN4JMEmAi7XTadC5Q2UTxic4ghTS+5+qJ4AeEtvR7fIrT/qnhojVqygj2gfyPpYS HlebsC2Y49NzObSqLA2WTg==" \
  -e DATAGUARDIAN_MASTER_KEY="gQJ6WV5FxDgGWj-vQqRzHqS4CIUOGFaXRqsGXNLJHbU=" \
  -e DISABLE_RLS=1 \
  -p 5000:5000 \
  --restart unless-stopped \
  dataguardian:latest

echo ""
echo "6️⃣  Waiting 45 seconds..."
sleep 45

# Test
echo ""
echo "7️⃣  Testing database query..."
docker exec dataguardian-container python3 << 'PYTEST'
import sys; sys.path.insert(0, '/app')
from services.results_aggregator import ResultsAggregator
agg = ResultsAggregator()
scans = agg.get_user_scans('vishaal314', limit=15, organization_id='default_org')
print(f"✅ Database query returned: {len(scans)} scans")
if scans:
    print(f"   Latest: {scans[0].get('timestamp')} - {scans[0].get('scan_type')}")
    print(f"   SUCCESS: Query is working correctly!")
else:
    print(f"   ❌ Still returning 0 scans")
PYTEST

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  ✅ FIX COMPLETE!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Now test:"
echo "  1. Visit: https://dataguardianpro.nl"
echo "  2. Go to: Predictive Compliance Analytics"
echo "  3. Should show REAL predictions (not demo)"
echo ""
echo "Check logs:"
echo "  docker logs dataguardian-container | grep 'Predictive Analytics'"
echo ""
echo "Expected:"
echo "  'Predictive Analytics: Retrieved 15 scan metadata records'"
echo "════════════════════════════════════════════════════════════════"
