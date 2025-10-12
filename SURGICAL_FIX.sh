#!/bin/bash
set -e

echo "🔧 SURGICAL FIX - Direct Code Replacement"
echo ""

cd /opt/dataguardian

# Create exact fix for Predictive Analytics
echo "Fixing Predictive Analytics directly..."

# Method: Direct line replacement with sed
sed -i.backup '/with st.spinner("🔍 Analyzing scan history..."):/{
N
s/with st.spinner("🔍 Analyzing scan history..."):\n                scan_metadata = aggregator.get_user_scans(username, limit=15)/with st.spinner("🔍 Analyzing scan history..."):\n                org_id = get_organization_id()\n                logger.info(f"Predictive Analytics: user={username}, org={org_id}, limit=15")\n                scan_metadata = aggregator.get_user_scans(username, limit=15, organization_id=org_id)\n                logger.info(f"Predictive Analytics: Retrieved {len(scan_metadata)} scans")/
}' app.py

echo "✅ Code fixed"

# Verify the fix
echo ""
echo "Verifying fix applied:"
grep -A 5 'with st.spinner("🔍 Analyzing scan history' app.py | head -10

# Rebuild
echo ""
echo "Rebuilding Docker..."
docker build --no-cache -t dataguardian:latest . 2>&1 | tail -15

# Restart
echo ""
echo "Restarting..."
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true

docker run -d \
  --name dataguardian-container \
  -e DATABASE_URL="postgresql://neondb_owner:npg_cKtisl61HrVC@ep-blue-queen-a6jyu08j.us-west-2.aws.neon.tech/neondb?sslmode=require" \
  -e JWT_SECRET="vN4JMEmAi7XTadC5Q2UTxic4ghTS+5+qJ4AeEtvR7fIrT/qnhojVqygj2gfyPpYS HlebsC2Y49NzObSqLA2WTg==" \
  -e DATAGUARDIAN_MASTER_KEY="gQJ6WV5FxDgGWj-vQqRzHqS4CIUOGFaXRqsGXNLJHbU=" \
  -e DISABLE_RLS=1 \
  -p 5000:5000 \
  --restart unless-stopped \
  dataguardian:latest

sleep 40

echo ""
echo "🎉 DONE! Test: Visit Predictive Analytics page and check logs"
echo "docker logs dataguardian-container | grep 'Predictive Analytics'"
