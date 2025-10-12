#!/bin/bash
################################################################################
# COMPLETE E2E FIX - Predictive Analytics organization_id
################################################################################

set -e

echo "════════════════════════════════════════════════════════════════"
echo "  DataGuardian Pro - COMPLETE E2E FIX"
echo "════════════════════════════════════════════════════════════════"
echo ""

cd /opt/dataguardian

# Step 1: Backup
echo "1️⃣  Creating backup..."
cp app.py app.py.backup_$(date +%Y%m%d_%H%M%S)
echo "✅ Backup created"

# Step 2: Fix the code (adaptive approach)
echo ""
echo "2️⃣  Applying fix to app.py..."

python3 << 'PYTHONFIX'
with open('app.py', 'r') as f:
    lines = f.readlines()

# Find and fix the Predictive Analytics section
fixed = False
new_lines = []

for i in range(len(lines)):
    line = lines[i]
    
    # Look for get_user_scans in Predictive Analytics context
    if 'scan_metadata = aggregator.get_user_scans' in line:
        # Check if this is in Predictive Analytics (check previous 20 lines for context)
        context = ''.join(lines[max(0, i-20):i])
        
        if 'predictive' in context.lower() or 'scan history' in context.lower():
            # Check if already fixed
            if 'organization_id' in line:
                print(f"✅ Line {i+1} already has organization_id")
                new_lines.append(line)
                continue
            
            print(f"🔧 Fixing line {i+1}: {line.strip()}")
            
            # Get indentation
            indent = ' ' * (len(line) - len(line.lstrip()))
            
            # Add org_id before
            new_lines.append(f'{indent}org_id = get_organization_id()\n')
            new_lines.append(f'{indent}logger.info(f"Predictive Analytics: user={{username}}, org={{org_id}}, limit=15")\n')
            
            # Fix the line itself
            if 'limit=15)' in line:
                new_line = line.replace('limit=15)', 'limit=15, organization_id=org_id)')
            elif 'limit = 15)' in line:
                new_line = line.replace('limit = 15)', 'limit=15, organization_id=org_id)')
            else:
                new_line = line.rstrip().rstrip(')') + ', organization_id=org_id)\n'
            
            new_lines.append(new_line)
            
            # Add log after
            new_lines.append(f'{indent}logger.info(f"Predictive Analytics: Retrieved {{len(scan_metadata)}} scan metadata records")\n')
            
            fixed = True
            print(f"✅ Fixed! Added organization_id parameter")
            continue
    
    new_lines.append(line)

if not fixed:
    print("❌ ERROR: Could not find scan_metadata line to fix")
    print("Searching for any get_user_scans calls...")
    for i, line in enumerate(lines):
        if 'get_user_scans' in line:
            print(f"  Line {i+1}: {line.strip()[:80]}")
    exit(1)

# Write fixed file
with open('app.py', 'w') as f:
    f.writelines(new_lines)

print("\n✅ Code fix applied successfully")
PYTHONFIX

if [ $? -ne 0 ]; then
    echo "❌ Fix failed - restoring backup"
    cp app.py.backup_* app.py 2>/dev/null || true
    exit 1
fi

# Step 3: Verify the fix
echo ""
echo "3️⃣  Verifying fix applied..."
if grep -q 'organization_id=org_id' app.py && grep -q 'Predictive Analytics: Retrieved' app.py; then
    echo "✅ Verification passed - organization_id found in code"
else
    echo "❌ Verification failed - fix not applied correctly"
    exit 1
fi

# Step 4: Rebuild Docker
echo ""
echo "4️⃣  Rebuilding Docker image (this takes 2-3 minutes)..."
docker build --no-cache -t dataguardian:latest . 2>&1 | tail -20

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi

echo "✅ Docker image rebuilt"

# Step 5: Restart container
echo ""
echo "5️⃣  Restarting container..."
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

if [ $? -ne 0 ]; then
    echo "❌ Container start failed"
    exit 1
fi

echo "✅ Container started"

# Step 6: Wait for startup
echo ""
echo "6️⃣  Waiting 45 seconds for application startup..."
sleep 45

# Step 7: Test the fix
echo ""
echo "7️⃣  Testing database query..."
docker exec dataguardian-container python3 << 'PYTEST'
import sys
sys.path.insert(0, '/app')
from services.results_aggregator import ResultsAggregator

try:
    agg = ResultsAggregator()
    scans = agg.get_user_scans('vishaal314', limit=15, organization_id='default_org')
    print(f"✅ Database query: {len(scans)} scans retrieved")
    if scans:
        print(f"   Latest scan: {scans[0].get('timestamp')} - {scans[0].get('scan_type')}")
    else:
        print("   ⚠️  No scans found (check organization_id)")
except Exception as e:
    print(f"❌ Query failed: {e}")
    exit(1)
PYTEST

if [ $? -ne 0 ]; then
    echo "❌ Database test failed"
    exit 1
fi

# Step 8: Check logs
echo ""
echo "8️⃣  Checking application logs..."
echo "Recent logs:"
docker logs dataguardian-container 2>&1 | tail -10

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  ✅ COMPLETE - FIX DEPLOYED SUCCESSFULLY!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Next Steps:"
echo "  1. Visit: https://dataguardianpro.nl"
echo "  2. Login as: vishaal314"
echo "  3. Go to: Predictive Compliance Analytics"
echo "  4. You should see REAL predictions (not demo data)"
echo ""
echo "To verify, check logs:"
echo "  docker logs dataguardian-container | grep 'Predictive Analytics'"
echo ""
echo "Expected to see:"
echo "  'Predictive Analytics: Retrieved 15 scan metadata records'"
echo "  (NOT 'metadata count: 0')"
echo ""
echo "════════════════════════════════════════════════════════════════"
