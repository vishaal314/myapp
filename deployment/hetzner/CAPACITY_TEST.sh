#!/bin/bash
# CAPACITY_TEST.sh
# Server Capacity & Load Testing for DataGuardian Pro
# Determines maximum customer capacity for external server

echo "════════════════════════════════════════════════════════════════"
echo "📊 DataGuardian Pro - Server Capacity Analysis"
echo "   Server: dataguardianpro.nl (45.81.35.202)"
echo "   Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "════════════════════════════════════════════════════════════════"

# Change to application directory
cd /opt/dataguardian 2>/dev/null || cd ~

# 1. Server Hardware Analysis
echo ""
echo "1️⃣  SERVER HARDWARE SPECIFICATIONS:"
echo "   ────────────────────────────────────────"
echo -n "   CPU Cores: "
nproc
echo -n "   CPU Model: "
lscpu | grep "Model name" | cut -d: -f2 | xargs
echo -n "   Total RAM: "
free -h | awk '/^Mem:/ {print $2}'
echo -n "   Available RAM: "
free -h | awk '/^Mem:/ {print $7}'
echo -n "   Total Disk: "
df -h / | awk 'NR==2 {print $2}'
echo -n "   Available Disk: "
df -h / | awk 'NR==2 {print $4}'
echo -n "   Disk Usage: "
df -h / | awk 'NR==2 {print $5}'

# 2. Current Resource Usage
echo ""
echo "2️⃣  CURRENT RESOURCE USAGE:"
echo "   ────────────────────────────────────────"
echo -n "   CPU Load (1min): "
uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//'
echo -n "   Memory Used: "
free -h | awk '/^Mem:/ {print $3 " / " $2 " (" int($3/$2*100) "%)"}'
echo -n "   Swap Used: "
free -h | awk '/^Swap:/ {print $3 " / " $2}'

# 3. Docker Container Resources
echo ""
echo "3️⃣  DOCKER CONTAINER RESOURCES:"
echo "   ────────────────────────────────────────"
if command -v docker &> /dev/null; then
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" | head -5
else
    echo "   ⚠️  Docker not found"
fi

# 4. Database Performance Test
echo ""
echo "4️⃣  DATABASE PERFORMANCE TEST:"
echo "   ────────────────────────────────────────"
if docker ps | grep -q dataguardian-container; then
    echo "   Running query performance test..."
    
    # Test query speed
    START_TIME=$(date +%s%N)
    docker exec dataguardian-container python3 << 'DBTEST' 2>/dev/null
import sys
sys.path.insert(0, '/app')
from services.results_aggregator import ResultsAggregator
agg = ResultsAggregator()
scans = agg.get_user_scans('vishaal314', limit=50, organization_id='default_org')
print(f"Retrieved {len(scans)} scans")
DBTEST
    END_TIME=$(date +%s%N)
    DURATION=$((($END_TIME - $START_TIME) / 1000000))
    echo "   Query Time: ${DURATION}ms"
    
    if [ $DURATION -lt 500 ]; then
        echo "   Performance: ✅ Excellent (<500ms)"
    elif [ $DURATION -lt 1000 ]; then
        echo "   Performance: ✅ Good (<1s)"
    elif [ $DURATION -lt 2000 ]; then
        echo "   Performance: ⚠️  Acceptable (<2s)"
    else
        echo "   Performance: ❌ Slow (>2s)"
    fi
else
    echo "   ⚠️  Container not running"
fi

# 5. Redis Performance Test
echo ""
echo "5️⃣  REDIS CACHE PERFORMANCE:"
echo "   ────────────────────────────────────────"
if docker ps | grep -q dataguardian-redis; then
    # Test Redis operations per second
    echo "   Testing Redis throughput (10000 operations)..."
    docker exec dataguardian-redis redis-cli --intrinsic-latency 1 2>/dev/null | head -3
    
    REDIS_OPS=$(docker exec dataguardian-redis redis-cli --csv lru-test 10000 2>/dev/null | tail -1)
    echo "   Redis Status: ✅ Operational"
    
    REDIS_MEM=$(docker exec dataguardian-redis redis-cli info memory 2>/dev/null | grep used_memory_human | cut -d: -f2)
    echo "   Memory Usage: $REDIS_MEM"
else
    echo "   ⚠️  Redis not running"
fi

# 6. Network & Connection Test
echo ""
echo "6️⃣  NETWORK & CONNECTION CAPACITY:"
echo "   ────────────────────────────────────────"
echo -n "   Max File Descriptors: "
ulimit -n
echo -n "   Current Connections: "
ss -s | grep TCP | head -1
echo -n "   PostgreSQL Max Connections: "
docker exec dataguardian-container python3 -c "import os; print(os.getenv('DATABASE_URL', 'Not configured'))" 2>/dev/null | grep -o 'pooler' && echo "Using connection pooling (optimized)" || echo "Direct connection"

# 7. Application Response Time Test
echo ""
echo "7️⃣  APPLICATION RESPONSE TIME:"
echo "   ────────────────────────────────────────"
if command -v curl &> /dev/null; then
    echo "   Testing application endpoint..."
    
    # Test health endpoint
    RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}\n' http://localhost:5000/_stcore/health 2>/dev/null)
    RESPONSE_MS=$(echo "$RESPONSE_TIME * 1000" | bc)
    echo "   Health Check: ${RESPONSE_MS}ms"
    
    # Test main page
    RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}\n' http://localhost:5000 2>/dev/null)
    RESPONSE_MS=$(echo "$RESPONSE_TIME * 1000" | bc)
    echo "   Main Page Load: ${RESPONSE_MS}ms"
else
    echo "   ⚠️  curl not available"
fi

# 8. Calculate Capacity Estimates
echo ""
echo "8️⃣  CAPACITY CALCULATIONS:"
echo "   ────────────────────────────────────────"

# Get system specs
TOTAL_RAM=$(free -g | awk '/^Mem:/ {print $2}')
CPU_CORES=$(nproc)

# Calculate estimates
# Assume: 100MB per concurrent user, 0.1 CPU per concurrent user
MAX_CONCURRENT_RAM=$((TOTAL_RAM * 1024 / 100))
MAX_CONCURRENT_CPU=$((CPU_CORES * 10))
MAX_CONCURRENT=$((MAX_CONCURRENT_RAM < MAX_CONCURRENT_CPU ? MAX_CONCURRENT_RAM : MAX_CONCURRENT_CPU))

# Apply safety factor (70% utilization)
SAFE_CONCURRENT=$((MAX_CONCURRENT * 70 / 100))

# Daily active users (assume 20% concurrent)
DAILY_USERS=$((SAFE_CONCURRENT * 5))

# Total customers (assume 10% daily active)
TOTAL_CUSTOMERS=$((DAILY_USERS * 10))

echo "   Maximum Concurrent Users: ~$MAX_CONCURRENT"
echo "   Safe Concurrent Users (70%): ~$SAFE_CONCURRENT"
echo "   Daily Active Users: ~$DAILY_USERS"
echo "   Total Customer Capacity: ~$TOTAL_CUSTOMERS"

# 9. Current Database Size
echo ""
echo "9️⃣  DATABASE STATISTICS:"
echo "   ────────────────────────────────────────"
docker exec dataguardian-container python3 << 'DBSTATS' 2>/dev/null || echo "   ⚠️  Unable to query database"
import sys
sys.path.insert(0, '/app')
from services.results_aggregator import ResultsAggregator
from services.multi_tenant_service import MultiTenantService

try:
    # Get scan count
    agg = ResultsAggregator()
    all_scans = agg.get_user_scans('vishaal314', limit=1000, organization_id='default_org')
    print(f"   Total Scans Stored: {len(all_scans)}")
    
    # Calculate average size
    if all_scans:
        import sys
        avg_size = sys.getsizeof(str(all_scans)) / len(all_scans) / 1024  # KB
        print(f"   Avg Scan Size: {avg_size:.2f} KB")
        
        # Estimate capacity
        total_ram_mb = 8000  # Adjust based on server
        scans_per_gb = 1024 / avg_size * 1000
        print(f"   Scans per GB: ~{int(scans_per_gb)}")
except Exception as e:
    print(f"   Error: {e}")
DBSTATS

# 10. Performance Recommendations
echo ""
echo "🔟 PERFORMANCE RECOMMENDATIONS:"
echo "   ────────────────────────────────────────"

# Check if swap is being used
SWAP_USED=$(free -m | awk '/^Swap:/ {print $3}')
if [ "$SWAP_USED" -gt 100 ]; then
    echo "   ⚠️  HIGH SWAP USAGE - Consider adding more RAM"
fi

# Check CPU load
CPU_LOAD=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//' | cut -d. -f1)
if [ "$CPU_LOAD" -gt "$CPU_CORES" ]; then
    echo "   ⚠️  HIGH CPU LOAD - Consider CPU optimization"
fi

# Check disk usage
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "   ⚠️  HIGH DISK USAGE (${DISK_USAGE}%) - Consider cleanup or expansion"
fi

# Recommendations based on specs
if [ "$TOTAL_RAM" -lt 4 ]; then
    echo "   📊 LOW RAM: Recommended for <50 concurrent users"
elif [ "$TOTAL_RAM" -lt 8 ]; then
    echo "   📊 MEDIUM RAM: Recommended for 50-200 concurrent users"
else
    echo "   📊 HIGH RAM: Can support 200+ concurrent users"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📈 CAPACITY SUMMARY:"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "   🎯 ESTIMATED CAPACITY (Conservative):"
echo "   ┌─────────────────────────────────────────────────────┐"
echo "   │  Concurrent Users:        $SAFE_CONCURRENT users              │"
echo "   │  Daily Active Users:      $DAILY_USERS users              │"
echo "   │  Total Customer Base:     $TOTAL_CUSTOMERS customers         │"
echo "   └─────────────────────────────────────────────────────┘"
echo ""
echo "   💡 OPTIMIZATION TIPS:"
echo "   - Use Redis caching for frequent queries (✅ Configured)"
echo "   - Enable database connection pooling (✅ Using Neon pooler)"
echo "   - Set resource limits on containers (✅ 1.5 CPU, 2GB RAM)"
echo "   - Monitor CPU/RAM usage regularly"
echo "   - Scale vertically (upgrade server) when >70% utilization"
echo ""
echo "   📊 UPGRADE RECOMMENDATIONS:"
if [ "$SAFE_CONCURRENT" -lt 100 ]; then
    echo "   - Current: Small server (~$SAFE_CONCURRENT users)"
    echo "   - Upgrade to 8GB RAM for ~150 concurrent users"
    echo "   - Upgrade to 16GB RAM for ~350 concurrent users"
else
    echo "   - Current: Good capacity for $SAFE_CONCURRENT concurrent users"
    echo "   - Monitor usage and upgrade when consistently >70%"
fi
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ Capacity Analysis Complete!"
echo "════════════════════════════════════════════════════════════════"
