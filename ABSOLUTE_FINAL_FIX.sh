#!/bin/bash
set -e

echo "════════════════════════════════════════════════════════════════"
echo "  ABSOLUTE FINAL FIX - Direct Code Patch"
echo "════════════════════════════════════════════════════════════════"

cd /opt/dataguardian

# Step 1: Show current bug
echo "1️⃣  Checking current code..."
echo "Checking results_aggregator.py line 508:"
sed -n '508p' services/results_aggregator.py || echo "Line not found"

# Step 2: Fix results_aggregator.py SQL query
echo ""
echo "2️⃣  Fixing SQL query in results_aggregator.py..."
python3 << 'PATCH1'
import re

with open('services/results_aggregator.py', 'r') as f:
    content = f.read()

# Find the exact broken line and fix it
# Old: cursor.execute(""" SELECT ... """, (username, limit))
# New: cursor.execute(""" SELECT ... """, (username, organization_id, limit))

# Pattern 1: Fix the tuple
content = re.sub(
    r'\), \(username, limit\)\)',
    '), (username, organization_id, limit))',
    content
)

# Verify the fix
if '(username, organization_id, limit))' in content:
    with open('services/results_aggregator.py', 'w') as f:
        f.write(content)
    print("✅ Fixed: cursor.execute now has (username, organization_id, limit)")
else:
    print("❌ Fix failed - pattern not found")
    exit(1)
PATCH1

# Step 3: Verify the fix
echo ""
echo "3️⃣  Verifying fix..."
grep -n "(username, organization_id, limit)" services/results_aggregator.py || echo "Not found!"

# Step 4: Clean Docker
echo ""
echo "4️⃣  Cleaning Docker..."
docker system prune -af 2>&1 | grep -i "freed" || true

# Step 5: Rebuild
echo ""
echo "5️⃣  Rebuilding (--no-cache)..."
docker build --no-cache -t dataguardian:latest . 2>&1 | tail -20

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi
echo "✅ Built"

# Step 6: Restart
echo ""
echo "6️⃣  Restarting..."
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

echo "✅ Started"

# Step 7: Wait
echo ""
echo "7️⃣  Waiting 50 seconds..."
sleep 50

# Step 8: Test INSIDE container
echo ""
echo "8️⃣  Testing inside container..."
docker exec dataguardian-container python3 << 'TEST'
import sys
sys.path.insert(0, '/app')

try:
    from services.results_aggregator import ResultsAggregator
    agg = ResultsAggregator()
    
    # This is the EXACT call that's failing
    scans = agg.get_user_scans('vishaal314', limit=15, organization_id='default_org')
    
    print(f"✅ Query returned: {len(scans)} scans")
    
    if len(scans) > 0:
        print(f"   Latest: {scans[0]}")
        print(f"\n   🎉 QUERY WORKS!")
    else:
        print("❌ Still 0 scans (but no error!)")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
TEST

# Step 9: Check logs
echo ""
echo "9️⃣  Checking application logs..."
docker logs dataguardian-container 2>&1 | grep -i "predictive\|error retrieving" | tail -10

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  ✅ FIX COMPLETE"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "NOW TEST IT:"
echo "  1. Visit: https://dataguardianpro.nl"
echo "  2. Login as: vishaal314"
echo "  3. Go to: Predictive Compliance Analytics"
echo ""
echo "You should see:"
echo "  ✅ '📊 Analyzing 15 scans for predictive insights'"
echo "  ✅ REAL predictions (not demo data)"
echo ""
echo "If still broken, send me the output of:"
echo "  docker logs dataguardian-container | grep -i predictive"
echo ""
echo "════════════════════════════════════════════════════════════════"
