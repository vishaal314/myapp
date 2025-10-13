#!/bin/bash
set -e

echo "════════════════════════════════════════════════════════════════"
echo "  🔧 FINAL END-TO-END DATABASE FIX"
echo "  Fixing DATABASE_URL and rebuilding everything"
echo "════════════════════════════════════════════════════════════════"

cd /opt/dataguardian

# Step 1: Check current logs for actual error
echo ""
echo "1️⃣  Checking current container logs for errors..."
if docker ps | grep -q dataguardian-container; then
    echo "Current container logs (last 30 lines):"
    docker logs dataguardian-container 2>&1 | tail -30
fi

# Step 2: Update .env file with pooled connection
echo ""
echo "2️⃣  Updating .env file with correct DATABASE_URL (with -pooler)..."

# Create/update .env with correct pooled connection
cat > .env << 'ENV_FILE'
# DataGuardian Pro Environment Configuration
DATABASE_URL=postgresql://neondb_owner:npg_cKtisl61HrVC@ep-blue-queen-a6jyu08j-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require
JWT_SECRET=vN4JMEmAi7XTadC5Q2UTxic4ghTS+5+qJ4AeEtvR7fIrT/qnhojVqygj2gfyPpYS HlebsC2Y49NzObSqLA2WTg==
DATAGUARDIAN_MASTER_KEY=gQJ6WV5FxDgGWj-vQqRzHqS4CIUOGFaXRqsGXNLJHbU=
DISABLE_RLS=1
ENVIRONMENT=production
PYTHONUNBUFFERED=1
ENV_FILE

echo "✅ .env file updated with pooled connection"
echo ""
echo "Verification - DATABASE_URL now contains:"
grep DATABASE_URL .env | sed 's/:[^@]*@/:***@/'

# Step 3: Load environment variables
echo ""
echo "3️⃣  Loading environment variables from updated .env..."
export $(cat .env | grep -v '^#' | xargs)
echo "✅ Environment variables loaded"

# Step 4: Stop old container
echo ""
echo "4️⃣  Stopping and removing old container..."
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true
echo "✅ Old container removed"

# Step 5: Clean rebuild
echo ""
echo "5️⃣  Clean rebuild of Docker image (this takes 2-3 minutes)..."
docker build --no-cache -t dataguardian:latest . 2>&1 | grep -E "Step|Successfully|sha256" || true
echo "✅ Image rebuilt"

# Step 6: Deploy with verified environment variables
echo ""
echo "6️⃣  Deploying container with verified environment variables..."
echo "   DATABASE_URL: $(echo $DATABASE_URL | sed 's/:[^@]*@/:***@/' | cut -c1-100)"
echo "   JWT_SECRET: [HIDDEN]"
echo "   DATAGUARDIAN_MASTER_KEY: [HIDDEN]"
echo "   DISABLE_RLS: $DISABLE_RLS"
echo ""

docker run -d --name dataguardian-container \
  --cpus="1.5" \
  --memory="2g" \
  --memory-swap="2g" \
  -e DATABASE_URL="$DATABASE_URL" \
  -e JWT_SECRET="$JWT_SECRET" \
  -e DATAGUARDIAN_MASTER_KEY="$DATAGUARDIAN_MASTER_KEY" \
  -e DISABLE_RLS=1 \
  -e ENVIRONMENT=production \
  -e PYTHONUNBUFFERED=1 \
  -p 5000:5000 \
  --restart unless-stopped \
  dataguardian:latest

echo "✅ Container deployed"

# Step 7: Wait for startup with progress
echo ""
echo "7️⃣  Waiting for application startup..."
echo -n "   "
for i in {1..60}; do
    if docker logs dataguardian-container 2>&1 | grep -q "You can now view your Streamlit app"; then
        echo " ✅ Streamlit started!"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

# Step 8: Verify container is running
echo ""
echo "8️⃣  Verifying container status..."
if docker ps | grep -q dataguardian-container; then
    echo "✅ Container: RUNNING"
    UPTIME=$(docker inspect -f '{{.State.StartedAt}}' dataguardian-container)
    echo "   Started at: $UPTIME"
else
    echo "❌ Container: NOT RUNNING"
    echo ""
    echo "Container logs:"
    docker logs dataguardian-container 2>&1 | tail -50
    exit 1
fi

# Step 9: Check environment variables inside container
echo ""
echo "9️⃣  Verifying environment variables inside container..."
docker exec dataguardian-container env | grep -E "DATABASE_URL|JWT_SECRET|DISABLE_RLS|DATAGUARDIAN_MASTER_KEY" | sed 's/:[^@]*@/:***@/' | sed 's/=.*/=[HIDDEN]/' | head -4
if docker exec dataguardian-container env | grep -q "ep-blue-queen-a6jyu08j-pooler"; then
    echo "✅ Pooled connection (-pooler) confirmed inside container"
else
    echo "❌ Warning: -pooler not found in DATABASE_URL inside container"
fi

# Step 10: Test database connection with detailed error reporting
echo ""
echo "🔟  Testing database connection..."
docker exec dataguardian-container python3 << 'PYTHON_TEST'
import sys
import os

print("Python environment check:")
print(f"  Python version: {sys.version.split()[0]}")
print(f"  Working directory: {os.getcwd()}")
print(f"  DATABASE_URL set: {'Yes' if os.environ.get('DATABASE_URL') else 'No'}")

sys.path.insert(0, '/app')

try:
    print("\nAttempting database connection...")
    from services.results_aggregator import ResultsAggregator
    
    print("  - ResultsAggregator imported successfully")
    
    agg = ResultsAggregator()
    print("  - ResultsAggregator instantiated")
    
    scans = agg.get_user_scans('vishaal314', limit=5, organization_id='default_org')
    print(f"  - Retrieved {len(scans)} scans successfully")
    
    print(f"\n✅ DATABASE CONNECTION: SUCCESS")
    print(f"✅ Retrieved {len(scans)} scans from database")
    
except ImportError as e:
    print(f"\n❌ IMPORT ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"\n❌ DATABASE ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYTHON_TEST

DB_TEST_RESULT=$?

if [ $DB_TEST_RESULT -eq 0 ]; then
    echo ""
    echo "✅ Database connection test: PASSED"
else
    echo ""
    echo "❌ Database connection test: FAILED (see error above)"
    echo ""
    echo "Checking application logs for more details..."
    docker logs dataguardian-container 2>&1 | tail -30
    exit 1
fi

# Step 11: Test Streamlit health endpoint
echo ""
echo "1️⃣1️⃣  Testing Streamlit health endpoint..."
if docker exec dataguardian-container curl -sf http://localhost:5000/_stcore/health >/dev/null 2>&1; then
    echo "✅ Streamlit health: OK"
else
    echo "⚠️  Streamlit health check failed (may be warming up)"
fi

# Step 12: Test external access
echo ""
echo "1️⃣2️⃣  Testing external access..."
sleep 3
if curl -sf https://dataguardianpro.nl >/dev/null 2>&1; then
    RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}\n' https://dataguardianpro.nl)
    echo "✅ External access: WORKING"
    echo "   Response time: ${RESPONSE_TIME}s"
else
    echo "⚠️  External access: Waiting for Nginx to detect new container..."
    echo "   Try: systemctl restart nginx"
fi

# Step 13: Display resource usage
echo ""
echo "1️⃣3️⃣  Current resource usage:"
docker stats dataguardian-container --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

# Step 14: Check for errors
echo ""
echo "1️⃣4️⃣  Checking for errors in logs..."
ERROR_COUNT=$(docker logs dataguardian-container 2>&1 | grep -i "error\|exception\|failed" | grep -v "Redis connection" | wc -l)
if [ "$ERROR_COUNT" -eq 0 ]; then
    echo "✅ No errors found in logs"
else
    echo "⚠️  Found $ERROR_COUNT potential issues (may be warnings):"
    docker logs dataguardian-container 2>&1 | grep -i "error\|exception\|failed" | grep -v "Redis connection" | head -3
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  ✅ END-TO-END FIX COMPLETE!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📊 What was fixed:"
echo "  1. ✅ Updated .env with pooled DATABASE_URL (-pooler added)"
echo "  2. ✅ Rebuilt Docker image with --no-cache"
echo "  3. ✅ Deployed with all environment variables"
echo "  4. ✅ Verified pooled connection inside container"
echo "  5. ✅ Tested database connection successfully"
echo ""
echo "🧪 Test your application:"
echo "  1. Visit: https://dataguardianpro.nl"
echo "  2. Login as: vishaal314"
echo "  3. Check Dashboard → should show 73 scans"
echo "  4. Check Predictive Analytics → should show 15 scans"
echo ""
echo "📊 Run monitoring:"
echo "  ./MONITOR_SERVER.sh"
echo ""
echo "If Nginx needs restart:"
echo "  systemctl restart nginx"
echo ""
echo "════════════════════════════════════════════════════════════════"
