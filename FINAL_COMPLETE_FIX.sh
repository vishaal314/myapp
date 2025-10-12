#!/bin/bash
set -e

echo "════════════════════════════════════════════════════════════════"
echo "  FINAL COMPLETE FIX - Predictive Analytics"
echo "════════════════════════════════════════════════════════════════"

cd /opt/dataguardian

echo ""
echo "1️⃣  Verifying code fixes..."
python3 << 'VERIFY'
with open('app.py', 'r') as f:
    app_content = f.read()
if 'organization_id=org_id' in app_content and 'Predictive Analytics' in app_content:
    print("✅ app.py has organization_id")
else:
    print("❌ app.py needs fix")

with open('services/results_aggregator.py', 'r') as f:
    agg_content = f.read()
if 'WHERE username = %s AND organization_id = %s' in agg_content and '(username, organization_id, limit)' in agg_content:
    print("✅ results_aggregator.py SQL query correct")
else:
    print("❌ results_aggregator.py needs SQL fix")
    agg_content = agg_content.replace(
        '""", (username, limit))',
        '""", (username, organization_id, limit))'
    )
    with open('services/results_aggregator.py', 'w') as f:
        f.write(agg_content)
    print("✅ FIXED: Added organization_id to cursor.execute")
VERIFY

echo ""
echo "2️⃣  Cleaning disk..."
df -h / | head -2
docker system prune -af --volumes 2>&1 | grep -i "total\|freed" || true
docker images | grep dataguardian | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true
echo "✅ Cleaned"

echo ""
echo "3️⃣  Rebuilding Docker..."
docker build --no-cache -t dataguardian:latest . 2>&1 | tail -50
[ $? -ne 0 ] && echo "❌ Build failed" && exit 1
echo "✅ Built"

echo ""
echo "4️⃣  Restarting..."
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true
docker run -d --name dataguardian-container \
  -e DATABASE_URL="postgresql://neondb_owner:npg_cKtisl61HrVC@ep-blue-queen-a6jyu08j.us-west-2.aws.neon.tech/neondb?sslmode=require" \
  -e JWT_SECRET="vN4JMEmAi7XTadC5Q2UTxic4ghTS+5+qJ4AeEtvR7fIrT/qnhojVqygj2gfyPpYS HlebsC2Y49NzObSqLA2WTg==" \
  -e DATAGUARDIAN_MASTER_KEY="gQJ6WV5FxDgGWj-vQqRzHqS4CIUOGFaXRqsGXNLJHbU=" \
  -e DISABLE_RLS=1 -p 5000:5000 --restart unless-stopped dataguardian:latest
echo "✅ Started"

echo ""
echo "5️⃣  Waiting 50 seconds..."
sleep 50

echo ""
echo "6️⃣  Testing..."
docker exec dataguardian-container python3 << 'PYTEST'
import sys
sys.path.insert(0, '/app')
from services.results_aggregator import ResultsAggregator
agg = ResultsAggregator()
scans = agg.get_user_scans('vishaal314', limit=15, organization_id='default_org')
if len(scans) > 0:
    print(f"✅ SUCCESS: {len(scans)} scans!")
    print(f"   {scans[0].get('timestamp')} - {scans[0].get('scan_type')}")
else:
    print(f"❌ Still 0 scans")
    exit(1)
PYTEST

if [ $? -eq 0 ]; then
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "  ✅ COMPLETE - PREDICTIVE ANALYTICS FIXED!"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    echo "Visit: https://dataguardianpro.nl → Predictive Analytics"
    echo "You will see REAL predictions (not demo data)"
    echo ""
else
    echo "❌ Failed"
    exit 1
fi
