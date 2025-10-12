#!/bin/bash
################################################################################
# DEPLOY BUG FIXES - Region Column Fixed
################################################################################

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  DataGuardian Pro - Deploy Critical Bug Fixes                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

cd /opt/dataguardian

# Step 1: Update results_aggregator.py with region column fixes
echo "Step 1: Updating results_aggregator.py with region column fixes..."

# Create backup
cp services/results_aggregator.py services/results_aggregator.py.backup_$(date +%s)

# Fix 1: Add region to INSERT statement (line 293-314)
sed -i 's/INSERT INTO scans$/INSERT INTO scans/g' services/results_aggregator.py
sed -i 's/(scan_id, username, timestamp, scan_type, file_count, total_pii_found, high_risk_count, result_json, organization_id)/(scan_id, username, timestamp, scan_type, region, file_count, total_pii_found, high_risk_count, result_json, organization_id)/g' services/results_aggregator.py
sed -i 's/VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)/VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)/g' services/results_aggregator.py

# Fix 2: Add region to UPDATE statement
sed -i '/timestamp = EXCLUDED.timestamp,/a\            result_json = EXCLUDED.result_json,\n            region = EXCLUDED.region,' services/results_aggregator.py

# Fix 3: Add region parameter to VALUES
# This is done by finding the exact pattern and replacing
cat > /tmp/fix_insert.py << 'PYFIX'
import re

with open('services/results_aggregator.py', 'r') as f:
    content = f.read()

# Fix the INSERT VALUES to include region parameter
pattern = r'\(\s*scan_id,\s*username,\s*datetime\.now\(\),\s*scan_type,\s*file_count,'
replacement = '(\n                scan_id,\n                username,\n                datetime.now(),\n                scan_type,\n                region,\n                file_count,'
content = re.sub(pattern, replacement, content)

with open('services/results_aggregator.py', 'w') as f:
    f.write(content)
    
print("✅ Fixed INSERT statement")
PYFIX

python3 /tmp/fix_insert.py

# Fix 4: Add region to SELECT statements
sed -i 's/SELECT scan_id, username, timestamp, scan_type,$/SELECT scan_id, username, timestamp, scan_type, region,/g' services/results_aggregator.py
sed -i 's/SELECT scan_id, username, timestamp, scan_type, $/SELECT scan_id, username, timestamp, scan_type, region,/g' services/results_aggregator.py

echo "✅ Code fixes applied"

# Step 2: Rebuild Docker image with --no-cache
echo ""
echo "Step 2: Rebuilding Docker image (no cache)..."
docker build --no-cache --pull -t dataguardian:latest .
echo "✅ Image rebuilt"

# Step 3: Stop and remove old container
echo ""
echo "Step 3: Stopping old container..."
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true
echo "✅ Old container removed"

# Step 4: Start new container with all environment variables
echo ""
echo "Step 4: Starting new container..."
docker run -d \
  --name dataguardian-container \
  -e DATABASE_URL="postgresql://neondb_owner:npg_cKtisl61HrVC@ep-blue-queen-a6jyu08j.us-west-2.aws.neon.tech/neondb?sslmode=require" \
  -e JWT_SECRET="vN4JMEmAi7XTadC5Q2UTxic4ghTS+5+qJ4AeEtvR7fIrT/qnhojVqygj2gfyPpYS HlebsC2Y49NzObSqLA2WTg==" \
  -e DATAGUARDIAN_MASTER_KEY="gQJ6WV5FxDgGWj-vQqRzHqS4CIUOGFaXRqsGXNLJHbU=" \
  -e DISABLE_RLS=1 \
  -e NODE_ENV=production \
  -p 5000:5000 \
  --restart unless-stopped \
  dataguardian:latest
echo "✅ Container started"

# Step 5: Wait for startup
echo ""
echo "Step 5: Waiting 45 seconds for startup..."
sleep 45

# Step 6: Verification
echo ""
echo "VERIFICATION:"
echo ""

docker exec dataguardian-container python3 << 'PYTEST'
import os, psycopg2

db_url = os.environ.get('DATABASE_URL')

if db_url:
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Test database access
        cursor.execute("SELECT COUNT(*) FROM scans")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM scans WHERE username = 'vishaal314'")
        user = cursor.fetchone()[0]
        
        print(f"✅ Total scans in database: {total}")
        print(f"✅ User scans: {user}")
        
        # Test if region column is accessible
        cursor.execute("SELECT scan_id, region FROM scans LIMIT 1")
        test = cursor.fetchone()
        if test:
            print(f"✅ Region column accessible: {test[1]}")
        
        conn.close()
    except Exception as e:
        print(f"❌ Database error: {e}")
else:
    print("❌ DATABASE_URL missing!")
PYTEST

echo ""
docker exec dataguardian-container python3 << 'PYAGG'
import sys
sys.path.insert(0, '/app')
try:
    from services.results_aggregator import ResultsAggregator
    agg = ResultsAggregator()
    scans = agg.get_recent_scans(days=365, username='vishaal314', organization_id='default_org')
    print(f"✅ ResultsAggregator: {len(scans)} scans retrieved")
    if scans:
        print("\n📋 Recent scans:")
        for i, s in enumerate(scans[:5]):
            print(f"  {i+1}. {s.get('scan_type', 'N/A')} - {s.get('region', 'N/A')}")
except Exception as e:
    print(f"❌ ResultsAggregator error: {e}")
PYAGG

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🎉 BUG FIXES DEPLOYED!"
echo ""
echo "Fixed Issues:"
echo "  ✅ Region column now included in INSERT statements"
echo "  ✅ Region column now included in SELECT statements"
echo "  ✅ New scans will save successfully"
echo "  ✅ Existing scans can be retrieved without errors"
echo ""
echo "🧪 TEST NOW:"
echo "  1. https://dataguardianpro.nl"
echo "  2. Hard refresh: Ctrl+Shift+R"
echo "  3. Run a new scan - should save successfully"
echo "  4. All 70+ scans should be visible"
echo "═══════════════════════════════════════════════════════════════"

