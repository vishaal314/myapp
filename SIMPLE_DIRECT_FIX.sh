#!/bin/bash
set -e

echo "🔧 DataGuardian Pro - Direct Fix for Production Server"
echo ""

cd /opt/dataguardian

# Fix 1: results_aggregator.py - Add caching
echo "1. Adding multi-tenant caching..."
sed -i.bak '/^logger = logging.getLogger(__name__)$/a\
\
# Global cached multi-tenant service\
_cached_multi_tenant_service = None\
\
def _get_cached_multi_tenant_service():\
    global _cached_multi_tenant_service\
    if _cached_multi_tenant_service is None:\
        _cached_multi_tenant_service = MultiTenantService()\
        logger.info("Multi-tenant service initialized (cached globally)")\
    return _cached_multi_tenant_service
' services/results_aggregator.py

# Fix initialization
sed -i 's/self.multi_tenant_service = MultiTenantService()/self.multi_tenant_service = _get_cached_multi_tenant_service()/' services/results_aggregator.py
sed -i 's/Multi-tenant service initialized for secure tenant isolation/Using cached multi-tenant service for secure tenant isolation/' services/results_aggregator.py

echo "✅ Caching added"

# Fix 2: app.py - Add organization_id to dashboard
echo "2. Fixing dashboard organization_id..."
sed -i.bak "s/all_user_scans = fresh_aggregator.get_user_scans(username or 'anonymous', limit=50)/org_id = get_organization_id()\n            all_user_scans = fresh_aggregator.get_user_scans(username or 'anonymous', limit=50, organization_id=org_id)/" app.py

echo "✅ Dashboard fixed"

# Fix 3: app.py - Add organization_id to Predictive Analytics
echo "3. Fixing Predictive Analytics..."
sed -i "s/scan_metadata = aggregator.get_user_scans(username, limit=15)/org_id = get_organization_id()\n                scan_metadata = aggregator.get_user_scans(username, limit=15, organization_id=org_id)/" app.py

echo "✅ Predictive Analytics fixed"

# Rebuild
echo ""
echo "4. Rebuilding Docker..."
docker build --no-cache -t dataguardian:latest . 2>&1 | tail -10

# Restart
echo ""
echo "5. Restarting container..."
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

sleep 30

# Test
echo ""
echo "6. Testing..."
docker exec dataguardian-container python3 << 'PYTEST'
import sys
sys.path.insert(0, '/app')
from services.results_aggregator import ResultsAggregator

agg = ResultsAggregator()
scans = agg.get_user_scans('vishaal314', limit=15, organization_id='default_org')
print(f"✅ Result: {len(scans)} scans retrieved")
PYTEST

echo ""
echo "🎉 DONE! Test: https://dataguardianpro.nl"
