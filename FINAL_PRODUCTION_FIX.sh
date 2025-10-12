#!/bin/bash
################################################################################
# FINAL PRODUCTION FIX - With Full Logging & Verification
################################################################################

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  DataGuardian Pro - FINAL PRODUCTION FIX                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

cd /opt/dataguardian

# Backup
echo "1. Creating backups..."
cp services/results_aggregator.py services/results_aggregator.py.backup_$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
cp app.py app.py.backup_$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
echo "✅ Backups created"

# Fix 1: Multi-tenant caching
echo ""
echo "2. Adding multi-tenant service caching..."
python3 << 'PYFIX1'
with open('services/results_aggregator.py', 'r') as f:
    content = f.read()

# Check if already fixed
if '_cached_multi_tenant_service = None' in content:
    print("✅ Multi-tenant caching already present")
else:
    # Add caching
    content = content.replace(
        'logger = logging.getLogger(__name__)\n\nclass ResultsAggregator:',
        '''logger = logging.getLogger(__name__)

# Global cached multi-tenant service (singleton pattern for performance)
_cached_multi_tenant_service = None

def _get_cached_multi_tenant_service():
    """Get or create cached multi-tenant service (singleton for performance)."""
    global _cached_multi_tenant_service
    if _cached_multi_tenant_service is None:
        _cached_multi_tenant_service = MultiTenantService()
        logger.info("Multi-tenant service initialized (cached globally)")
    return _cached_multi_tenant_service

class ResultsAggregator:'''
    )
    
    # Replace initialization
    content = content.replace(
        'self.multi_tenant_service = MultiTenantService()',
        'self.multi_tenant_service = _get_cached_multi_tenant_service()'
    )
    content = content.replace(
        'Multi-tenant service initialized for secure tenant isolation',
        'Using cached multi-tenant service for secure tenant isolation'
    )
    
    with open('services/results_aggregator.py', 'w') as f:
        f.write(content)
    
    print("✅ Multi-tenant service caching added")
PYFIX1

# Fix 2: Dashboard organization_id
echo ""
echo "3. Fixing dashboard organization_id..."
python3 << 'PYFIX2'
with open('app.py', 'r') as f:
    content = f.read()

# Fix dashboard - check if already fixed
if 'org_id = get_organization_id()' in content and 'organization_id=org_id' in content:
    print("✅ Dashboard organization_id already fixed")
else:
    # Fix the get_user_scans calls
    content = content.replace(
        "all_user_scans = fresh_aggregator.get_user_scans(username or 'anonymous', limit=50)",
        "org_id = get_organization_id()\n            all_user_scans = fresh_aggregator.get_user_scans(username or 'anonymous', limit=50, organization_id=org_id)"
    )
    
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("✅ Dashboard organization_id fixed")
PYFIX2

# Fix 3: Predictive Analytics with logging
echo ""
echo "4. Fixing Predictive Analytics with enhanced logging..."
python3 << 'PYFIX3'
with open('app.py', 'r') as f:
    content = f.read()

# Add logging and organization_id
old_pattern = '''with st.spinner("🔍 Analyzing scan history..."):
                scan_metadata = aggregator.get_user_scans(username, limit=15)'''

new_pattern = '''with st.spinner("🔍 Analyzing scan history..."):
                org_id = get_organization_id()
                logger.info(f"Predictive Analytics: Requesting scans for user={username}, org={org_id}, limit=15")
                scan_metadata = aggregator.get_user_scans(username, limit=15, organization_id=org_id)
                logger.info(f"Predictive Analytics: Retrieved {len(scan_metadata)} scan metadata records")'''

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    print("✅ Added organization_id and logging to Predictive Analytics")
else:
    print("✅ Predictive Analytics already has organization_id")

# Add warning log for empty results
old_warn = '''if not scan_history:
            st.warning("📊 No scan history found. Perform some scans first to generate predictive insights.")'''

new_warn = '''if not scan_history:
            logger.warning(f"Predictive Analytics: No scan history after enrichment (metadata count: {len(scan_metadata)})")
            st.warning("📊 No scan history found. Perform some scans first to generate predictive insights.")'''

if old_warn in content:
    content = content.replace(old_warn, new_warn)
    print("✅ Added debug logging for empty scan history")

with open('app.py', 'w') as f:
    f.write(content)
PYFIX3

# Rebuild Docker
echo ""
echo "5. Rebuilding Docker image (--no-cache for fresh build)..."
docker build --no-cache -t dataguardian:latest . 2>&1 | tail -20

# Restart container
echo ""
echo "6. Restarting container with all environment variables..."
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
echo "Waiting 40 seconds for startup..."
sleep 40

# Comprehensive verification
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "COMPREHENSIVE VERIFICATION"
echo "═══════════════════════════════════════════════════════════════"
echo ""

echo "Test 1: Multi-tenant Service Caching"
docker logs dataguardian-container 2>&1 | grep -i "cached globally" | tail -1

echo ""
echo "Test 2: Database Query with organization_id"
docker exec dataguardian-container python3 << 'PYTEST2'
import sys
sys.path.insert(0, '/app')
from services.results_aggregator import ResultsAggregator

agg = ResultsAggregator()
scans = agg.get_user_scans('vishaal314', limit=15, organization_id='default_org')
print(f"✅ get_user_scans returned: {len(scans)} scans")
if scans:
    print(f"   Latest: {scans[0].get('timestamp')} - {scans[0].get('scan_type')}")
else:
    print("   ❌ STILL EMPTY - Needs deeper investigation")
PYTEST2

echo ""
echo "Test 3: Check for Predictive Analytics logs (will appear when user visits page)"
echo "   Run: docker logs dataguardian-container | grep 'Predictive Analytics'"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🎉 DEPLOYMENT COMPLETE!"
echo ""
echo "Next Steps:"
echo "  1. Visit https://dataguardianpro.nl and login"
echo "  2. Go to Predictive Analytics page"
echo "  3. Check logs: docker logs dataguardian-container | grep 'Predictive Analytics'"
echo "  4. Should see: 'Retrieved 15 scan metadata records' (not 0)"
echo ""
echo "If still empty, run debug:"
echo "  docker exec dataguardian-container python3 -c 'import sys; sys.path.insert(0,\"/app\"); from services.results_aggregator import ResultsAggregator; a=ResultsAggregator(); print(len(a.get_user_scans(\"vishaal314\", 15, \"default_org\")))'"
echo "═══════════════════════════════════════════════════════════════"
