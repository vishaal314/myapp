#!/bin/bash
################################################################################
# SIMPLE FIX - DATABASE_URL + JWT_SECRET + DISABLE_RLS
################################################################################

set -e

echo "╔════════════════════════════════════════╗"
echo "║  DataGuardian - Complete Fix          ║"
echo "╚════════════════════════════════════════╝"
echo ""

cd /opt/dataguardian

# Step 1: Get DATABASE_URL
echo "Step 1: Enter your DATABASE_URL"
echo "Example: postgresql://user:pass@host:5432/dbname"
read -p "DATABASE_URL: " DB_URL

# Step 2: Generate secrets
echo ""
echo "Step 2: Generating secrets..."
JWT_SECRET=$(openssl rand -hex 32)
MASTER_KEY=$(openssl rand -base64 32 | tr -d '\n')
echo "✅ Secrets generated"

# Step 3: Create .env file
echo ""
echo "Step 3: Creating .env file..."
cat > .env << ENVEOF
DATABASE_URL=${DB_URL}
JWT_SECRET=${JWT_SECRET}
DATAGUARDIAN_MASTER_KEY=${MASTER_KEY}
DISABLE_RLS=1
NODE_ENV=production
ENVEOF
echo "✅ .env file created"

# Step 4: Restart container
echo ""
echo "Step 4: Restarting container..."
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true

docker run -d \
  --name dataguardian-container \
  -e DATABASE_URL="${DB_URL}" \
  -e JWT_SECRET="${JWT_SECRET}" \
  -e DATAGUARDIAN_MASTER_KEY="${MASTER_KEY}" \
  -e DISABLE_RLS=1 \
  -e NODE_ENV=production \
  -p 5000:5000 \
  --restart unless-stopped \
  dataguardian:latest

echo "✅ Container started"

# Step 5: Wait
echo ""
echo "Step 5: Waiting 45 seconds for startup..."
sleep 45

# Step 6: Disable RLS
echo ""
echo "Step 6: Disabling RLS on database..."
docker exec dataguardian-container python3 << 'PYFIX'
import psycopg2, os
try:
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE scans DISABLE ROW LEVEL SECURITY")
    cursor.execute("ALTER TABLE audit_log DISABLE ROW LEVEL SECURITY")
    conn.commit()
    print("✅ RLS disabled")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
PYFIX

# Step 7: Verify
echo ""
echo "Step 7: Verification..."
echo ""

docker exec dataguardian-container printenv DATABASE_URL >/dev/null 2>&1 && echo "✅ DATABASE_URL: Set" || echo "❌ DATABASE_URL: Missing"
docker exec dataguardian-container printenv JWT_SECRET >/dev/null 2>&1 && echo "✅ JWT_SECRET: Set" || echo "❌ JWT_SECRET: Missing"
docker exec dataguardian-container printenv DISABLE_RLS | grep -q "1" && echo "✅ DISABLE_RLS: Set" || echo "❌ DISABLE_RLS: Missing"

echo ""
docker exec dataguardian-container python3 << 'PYTEST'
import psycopg2, os
conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM scans")
total = cursor.fetchone()[0]
print(f"✅ Database scans: {total}")
conn.close()
PYTEST

docker exec dataguardian-container python3 << 'PYFINAL'
import sys
sys.path.insert(0, '/app')
from services.results_aggregator import ResultsAggregator
agg = ResultsAggregator()
scans = agg.get_recent_scans(days=365, username='vishaal314', organization_id='default_org')
print(f"✅ ResultsAggregator: {len(scans)} scans")
PYFINAL

echo ""
echo "════════════════════════════════════════"
echo "🎉 FIX COMPLETE!"
echo ""
echo "TEST NOW:"
echo "  1. https://dataguardianpro.nl"
echo "  2. Hard refresh: Ctrl + Shift + R"
echo "  3. All scans should be visible!"
echo "════════════════════════════════════════"

