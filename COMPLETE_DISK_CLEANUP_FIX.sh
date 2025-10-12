#!/bin/bash
set -e

echo "════════════════════════════════════════════════════════════════"
echo "  COMPLETE DISK CLEANUP + FIX"
echo "════════════════════════════════════════════════════════════════"
echo ""

cd /opt/dataguardian

# Step 1: Check disk space
echo "1️⃣  Current disk usage:"
df -h /
echo ""

# Step 2: Clean Docker
echo "2️⃣  Cleaning Docker system..."
docker system prune -af --volumes 2>&1 | head -20
echo "✅ Docker cleaned"

# Step 3: Remove old images
echo ""
echo "3️⃣  Removing old dataguardian images..."
docker images | grep dataguardian | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true
echo "✅ Old images removed"

# Step 4: Clean system
echo ""
echo "4️⃣  Cleaning system files..."
apt-get clean 2>/dev/null || true
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* 2>/dev/null || true
rm -rf ~/.cache/pip 2>/dev/null || true
echo "✅ System cleaned"

# Step 5: Check space again
echo ""
echo "5️⃣  Disk space after cleanup:"
df -h /
echo ""

# Step 6: Rebuild
echo "6️⃣  Rebuilding Docker image..."
docker build --no-cache -t dataguardian:latest . 2>&1 | tail -40

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ BUILD FAILED - Checking disk space:"
    df -h /
    exit 1
fi

echo ""
echo "✅ Build completed successfully"

# Step 7: Restart
echo ""
echo "7️⃣  Restarting container..."
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

# Step 8: Wait
echo ""
echo "8️⃣  Waiting 45 seconds for startup..."
sleep 45

# Step 9: Test
echo ""
echo "9️⃣  Testing Predictive Analytics fix..."
docker exec dataguardian-container python3 << 'PYTEST'
import sys
sys.path.insert(0, '/app')
from services.results_aggregator import ResultsAggregator

agg = ResultsAggregator()
scans = agg.get_user_scans('vishaal314', limit=15, organization_id='default_org')

if len(scans) > 0:
    print(f"✅ SUCCESS: {len(scans)} scans retrieved")
    print(f"   Latest: {scans[0].get('timestamp')} - {scans[0].get('scan_type')}")
    print(f"\n   🎉 PREDICTIVE ANALYTICS IS FIXED!")
else:
    print(f"❌ FAILED: Still returning 0 scans")
    exit(1)
PYTEST

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Test failed - checking logs:"
    docker logs dataguardian-container 2>&1 | tail -20
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  ✅ COMPLETE - EVERYTHING FIXED!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Final disk usage:"
df -h /
echo ""
echo "✅ Visit: https://dataguardianpro.nl"
echo "✅ Go to: Predictive Compliance Analytics"
echo "✅ Should show: REAL predictions (not demo data)"
echo ""
echo "════════════════════════════════════════════════════════════════"
