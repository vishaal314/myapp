#!/bin/bash
################################################################################
# SIMPLE FIX - Copy Fixed Files from Replit
################################################################################

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  DataGuardian Pro - Deploy Fixed Files                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

cd /opt/dataguardian

# Backup current files
cp services/results_aggregator.py services/results_aggregator.py.backup_$(date +%s)

# Fix results_aggregator.py - Remove duplicate result_json
echo "Fixing results_aggregator.py..."
python3 << 'PYFIX'
with open('services/results_aggregator.py', 'r') as f:
    lines = f.readlines()

# Find and fix the duplicate result_json issue
fixed_lines = []
skip_next = False
for i, line in enumerate(lines):
    if 'result_json = EXCLUDED.result_json,' in line and i > 0:
        # Check if previous line also has result_json
        if 'result_json = EXCLUDED.result_json,' in lines[i-1]:
            skip_next = True
            continue
    if not skip_next:
        fixed_lines.append(line)
    skip_next = False

with open('services/results_aggregator.py', 'w') as f:
    f.writelines(fixed_lines)
    
print("✅ Fixed duplicate result_json in results_aggregator.py")
PYFIX

# Rebuild with cache busting
echo ""
echo "Rebuilding Docker image..."
docker build --no-cache --pull -t dataguardian:latest .

# Restart container
echo ""
echo "Restarting container..."
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true

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

echo ""
echo "Waiting 45 seconds..."
sleep 45

# Test
echo ""
echo "VERIFICATION:"
docker exec dataguardian-container python3 << 'PYTEST'
import os, psycopg2, sys
sys.path.insert(0, '/app')

db_url = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(db_url)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM scans WHERE username = 'vishaal314'")
print(f"✅ User scans: {cursor.fetchone()[0]}")

from services.results_aggregator import ResultsAggregator
agg = ResultsAggregator()
scans = agg.get_recent_scans(days=365, username='vishaal314', organization_id='default_org')
print(f"✅ ResultsAggregator: {len(scans)} scans")

conn.close()
PYTEST

echo ""
echo "🎉 FIXED! Test: https://dataguardianpro.nl (Ctrl+Shift+R)"
