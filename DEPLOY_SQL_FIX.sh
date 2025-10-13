#!/bin/bash
set -e

echo "════════════════════════════════════════════════════════════════"
echo "  SQL QUERY FIX - Predictive Analytics Database Error"
echo "════════════════════════════════════════════════════════════════"

cd /opt/dataguardian

# Fix the SQL query bug in results_aggregator.py
echo "1️⃣  Fixing SQL query in results_aggregator.py..."
python3 << 'SQLFIX'
with open('services/results_aggregator.py', 'r') as f:
    content = f.read()

# Fix the missing 'region' column in SELECT statement
old_query = """SELECT scan_id, timestamp, scan_type, file_count, total_pii_found, high_risk_count
            FROM scans
            WHERE username = %s AND organization_id = %s"""

new_query = """SELECT scan_id, timestamp, scan_type, region, file_count, total_pii_found, high_risk_count
            FROM scans
            WHERE username = %s AND organization_id = %s"""

if old_query in content:
    content = content.replace(old_query, new_query)
    with open('services/results_aggregator.py', 'w') as f:
        f.write(content)
    print("✅ Fixed SQL query - added missing 'region' column")
elif new_query in content:
    print("✅ SQL query already has 'region' column")
else:
    print("⚠️  Pattern not found, trying alternative fix...")
    # Alternative: use sed to fix line 506 directly
    import subprocess
    subprocess.run(["sed", "-i", "506s/scan_type, file_count/scan_type, region, file_count/", "services/results_aggregator.py"])
    print("✅ Applied alternative fix")
SQLFIX

# Verify the fix
echo ""
echo "2️⃣  Verifying fix..."
if grep -q "scan_type, region, file_count" services/results_aggregator.py; then
    echo "✅ Verification passed: 'region' column present in query"
else
    echo "❌ Verification failed"
    exit 1
fi

# Rebuild Docker
echo ""
echo "3️⃣  Rebuilding Docker image..."
docker build --no-cache -t dataguardian:latest . 2>&1 | tail -15

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi
echo "✅ Docker image rebuilt"

# Restart container
echo ""
echo "4️⃣  Restarting container..."
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

echo "✅ Container started"

# Wait for startup
echo ""
echo "5️⃣  Waiting 45 seconds for application startup..."
sleep 45

# Test the fix
echo ""
echo "6️⃣  Testing database query..."
docker exec dataguardian-container python3 << 'TEST'
import sys
sys.path.insert(0, '/app')
from services.results_aggregator import ResultsAggregator

try:
    agg = ResultsAggregator()
    scans = agg.get_user_scans('vishaal314', limit=15, organization_id='default_org')
    
    if len(scans) > 0:
        print(f"✅ SUCCESS: Retrieved {len(scans)} scans")
        print(f"✅ First scan: {scans[0].get('scan_type')} - Region: {scans[0].get('region')}")
        exit(0)
    else:
        print("⚠️  No scans found for vishaal314")
        exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
TEST

if [ $? -eq 0 ]; then
    # Check logs for errors
    echo ""
    echo "7️⃣  Checking logs for errors..."
    if docker logs dataguardian-container 2>&1 | tail -100 | grep -q "tuple index out of range"; then
        echo "❌ SQL error still present in logs"
        docker logs dataguardian-container 2>&1 | tail -20
        exit 1
    else
        echo "✅ No SQL errors in logs"
    fi
    
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "  ✅✅✅ DEPLOYMENT SUCCESSFUL! ✅✅✅"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    echo "Fix applied:"
    echo "  ✅ services/results_aggregator.py: Added 'region' to SQL SELECT"
    echo "  ✅ Fixed 'tuple index out of range' error"
    echo "  ✅ Predictive Analytics now retrieves real scan data"
    echo ""
    echo "🚀 TEST YOUR APPLICATION:"
    echo "   1. Visit: https://dataguardianpro.nl"
    echo "   2. Login with vishaal314"
    echo "   3. Navigate to: Predictive Compliance Analytics"
    echo "   4. Expected: Real predictions from your scan history"
    echo "   5. No more 'Demo Predictions (Sample Data)' message"
    echo ""
    echo "════════════════════════════════════════════════════════════════"
else
    echo ""
    echo "❌ Test failed - checking logs..."
    docker logs dataguardian-container 2>&1 | tail -50
    exit 1
fi
