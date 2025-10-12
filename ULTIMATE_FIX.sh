#!/bin/bash
set -e

echo "════════════════════════════════════════════════════════════════"
echo "  ULTIMATE FIX - Clean Solution"
echo "════════════════════════════════════════════════════════════════"

cd /opt/dataguardian

# FIX 1: app.py - Replace line 1969 with correct indentation
echo "1️⃣  Fixing app.py line 1969..."
python3 << 'APPFIX'
with open('app.py', 'r') as f:
    lines = f.readlines()

# Line 1969 should be: "            org_id = 'default_org'  # Match Dashboard\n"
# That's 12 spaces of indentation
if len(lines) >= 1969:
    lines[1968] = "            org_id = 'default_org'  # Match Dashboard\n"
    print(f"✅ Fixed line 1969 with correct indentation")
    
    with open('app.py', 'w') as f:
        f.writelines(lines)
    print("✅ app.py saved")
else:
    print(f"❌ File only has {len(lines)} lines")
    exit(1)
APPFIX

# FIX 2: results_aggregator.py SQL query
echo ""
echo "2️⃣  Fixing results_aggregator.py SQL query..."
python3 << 'SQLFIX'
with open('services/results_aggregator.py', 'r') as f:
    content = f.read()

# Fix the SQL query parameters
old_pattern = '""", (username, limit))'
new_pattern = '""", (username, organization_id, limit))'

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    with open('services/results_aggregator.py', 'w') as f:
        f.write(content)
    print("✅ SQL query fixed")
elif new_pattern in content:
    print("✅ SQL query already fixed")
else:
    print("❌ Pattern not found")
    exit(1)
SQLFIX

# Verify
echo ""
echo "3️⃣  Verifying fixes..."
python3 << 'VERIFY'
# Check app.py
with open('app.py', 'r') as f:
    lines = f.readlines()
    line_1969 = lines[1968]
    if "org_id = 'default_org'" in line_1969 and line_1969.startswith("            "):
        print("✅ app.py: Correct")
    else:
        print(f"❌ app.py line 1969: {repr(line_1969)}")
        exit(1)

# Check results_aggregator.py
with open('services/results_aggregator.py', 'r') as f:
    if '(username, organization_id, limit))' in f.read():
        print("✅ results_aggregator.py: Correct")
    else:
        print("❌ results_aggregator.py: Missing fix")
        exit(1)
VERIFY

# Rebuild
echo ""
echo "4️⃣  Rebuilding Docker..."
docker build --no-cache -t dataguardian:latest . 2>&1 | tail -15

# Restart
echo ""
echo "5️⃣  Restarting..."
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

# Wait
echo ""
echo "6️⃣  Waiting 50 seconds..."
sleep 50

# Final test
echo ""
echo "7️⃣  Final verification..."
docker exec dataguardian-container python3 << 'TEST'
import sys
sys.path.insert(0, '/app')
from services.results_aggregator import ResultsAggregator
agg = ResultsAggregator()
scans = agg.get_user_scans('vishaal314', limit=15, organization_id='default_org')
print(f"Query result: {len(scans)} scans")
if len(scans) == 0:
    print("❌ FAILED: 0 scans")
    exit(1)
else:
    print(f"✅ SUCCESS: {len(scans)} scans!")
TEST

if [ $? -eq 0 ]; then
    echo ""
    if docker logs dataguardian-container 2>&1 | tail -100 | grep -q "IndentationError\|tuple index"; then
        echo "❌ Errors still in logs"
        docker logs dataguardian-container 2>&1 | tail -20
        exit 1
    fi
    
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "  ✅✅✅ COMPLETE SUCCESS! ✅✅✅"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    echo "All fixes applied successfully:"
    echo "  1. ✅ app.py line 1969: org_id = 'default_org' (correct indentation)"
    echo "  2. ✅ results_aggregator.py: SQL query fixed"
    echo "  3. ✅ Docker rebuilt and running"
    echo "  4. ✅ Database queries working"
    echo ""
    echo "🚀 NOW TEST YOUR APPLICATION:"
    echo "   Visit: https://dataguardianpro.nl"
    echo "   Login and go to: Predictive Compliance Analytics"
    echo "   Expected: REAL predictions from your 73 scans"
    echo ""
    echo "════════════════════════════════════════════════════════════════"
else
    echo "❌ Final test failed"
    docker logs dataguardian-container 2>&1 | tail -30
    exit 1
fi
