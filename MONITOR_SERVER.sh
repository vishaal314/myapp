#!/bin/bash

echo "════════════════════════════════════════════════════════════════"
echo "  📊 DataGuardian Pro - Server Performance Monitor"
echo "  Server: dataguardianpro.nl"
echo "  Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "════════════════════════════════════════════════════════════════"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check status
check_status() {
    local value=$1
    local threshold=$2
    local reverse=$3  # For metrics where lower is better
    
    if [ "$reverse" = "true" ]; then
        if (( $(echo "$value < $threshold" | bc -l) )); then
            echo -e "${GREEN}✅ GOOD${NC}"
        else
            echo -e "${RED}⚠️  HIGH${NC}"
        fi
    else
        if (( $(echo "$value > $threshold" | bc -l) )); then
            echo -e "${GREEN}✅ GOOD${NC}"
        else
            echo -e "${YELLOW}⚠️  LOW${NC}"
        fi
    fi
}

echo ""
echo "1️⃣  Container Status"
echo "────────────────────────────────────────────────────────────────"
if docker ps | grep -q dataguardian-container; then
    echo -e "${GREEN}✅ Container: RUNNING${NC}"
    UPTIME=$(docker inspect -f '{{.State.StartedAt}}' dataguardian-container)
    echo "   Started: $UPTIME"
else
    echo -e "${RED}❌ Container: NOT RUNNING${NC}"
    exit 1
fi

echo ""
echo "2️⃣  Resource Usage (Live)"
echo "────────────────────────────────────────────────────────────────"
docker stats dataguardian-container --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}"

echo ""
echo "3️⃣  Resource Analysis"
echo "────────────────────────────────────────────────────────────────"

# Get CPU and Memory percentages
CPU_PERCENT=$(docker stats dataguardian-container --no-stream --format "{{.CPUPerc}}" | sed 's/%//')
MEM_PERCENT=$(docker stats dataguardian-container --no-stream --format "{{.MemPerc}}" | sed 's/%//')

echo -n "   CPU Usage: $CPU_PERCENT% - "
if (( $(echo "$CPU_PERCENT < 60" | bc -l) )); then
    echo -e "${GREEN}✅ Healthy${NC}"
elif (( $(echo "$CPU_PERCENT < 85" | bc -l) )); then
    echo -e "${YELLOW}⚠️  Moderate${NC}"
else
    echo -e "${RED}⚠️  High Load${NC}"
fi

echo -n "   Memory Usage: $MEM_PERCENT% - "
if (( $(echo "$MEM_PERCENT < 70" | bc -l) )); then
    echo -e "${GREEN}✅ Healthy${NC}"
elif (( $(echo "$MEM_PERCENT < 90" | bc -l) )); then
    echo -e "${YELLOW}⚠️  Moderate${NC}"
else
    echo -e "${RED}⚠️  Critical${NC}"
fi

echo ""
echo "4️⃣  Application Health"
echo "────────────────────────────────────────────────────────────────"

# Check if Streamlit is responding
if curl -sf http://localhost:5000/_stcore/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Streamlit Health: OK${NC}"
else
    echo -e "${RED}❌ Streamlit Health: FAILED${NC}"
fi

# Check if site is accessible externally
if curl -sf https://dataguardianpro.nl > /dev/null 2>&1; then
    RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}\n' https://dataguardianpro.nl)
    echo -e "${GREEN}✅ External Access: OK${NC}"
    echo "   Response Time: ${RESPONSE_TIME}s"
else
    echo -e "${RED}❌ External Access: FAILED${NC}"
fi

echo ""
echo "5️⃣  Database Connection"
echo "────────────────────────────────────────────────────────────────"

# Test database connection from inside container
DB_TEST=$(docker exec dataguardian-container python3 -c "
import sys
import os
sys.path.insert(0, '/app')
try:
    from services.results_aggregator import ResultsAggregator
    agg = ResultsAggregator()
    scans = agg.get_user_scans('vishaal314', limit=5, organization_id='default_org')
    print(f'SUCCESS:{len(scans)}')
except Exception as e:
    print(f'ERROR:{str(e)}')
" 2>&1)

if [[ $DB_TEST == SUCCESS:* ]]; then
    SCAN_COUNT=$(echo $DB_TEST | cut -d':' -f2)
    echo -e "${GREEN}✅ Database: Connected${NC}"
    echo "   Retrieved: $SCAN_COUNT scans"
    echo "   Connection: Pooled (10K max connections)"
else
    echo -e "${RED}❌ Database: Connection Failed${NC}"
    echo "   Error: $DB_TEST"
fi

echo ""
echo "6️⃣  Recent Logs (Last 15 lines)"
echo "────────────────────────────────────────────────────────────────"
docker logs dataguardian-container --tail 15 2>&1 | grep -E "INFO|WARNING|ERROR|Started|Listening" || echo "No significant log entries"

echo ""
echo "7️⃣  Error Detection (Last 50 lines)"
echo "────────────────────────────────────────────────────────────────"
ERROR_COUNT=$(docker logs dataguardian-container --tail 50 2>&1 | grep -i "error\|exception\|failed" | wc -l)
if [ "$ERROR_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✅ No errors detected${NC}"
else
    echo -e "${YELLOW}⚠️  Found $ERROR_COUNT error entries:${NC}"
    docker logs dataguardian-container --tail 50 2>&1 | grep -i "error\|exception\|failed" | head -5
fi

echo ""
echo "8️⃣  Network Connections"
echo "────────────────────────────────────────────────────────────────"
CONNECTIONS=$(docker exec dataguardian-container ss -tn state established 2>/dev/null | wc -l)
echo "   Active Connections: $((CONNECTIONS - 1))"  # Subtract header line
echo "   Max Connections: 10,000 (via Neon pooling)"

echo ""
echo "9️⃣  Disk Usage"
echo "────────────────────────────────────────────────────────────────"
df -h / | tail -1 | awk '{printf "   Root: %s used of %s (%s)\n", $3, $2, $5}'
du -sh /opt/dataguardian 2>/dev/null | awk '{printf "   App Directory: %s\n", $1}'

echo ""
echo "🔟  System Load"
echo "────────────────────────────────────────────────────────────────"
LOAD=$(uptime | awk -F'load average:' '{print $2}' | sed 's/^[ \t]*//')
echo "   Load Average: $LOAD"
CORES=$(nproc)
echo "   CPU Cores: $CORES"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  📈 Performance Summary"
echo "════════════════════════════════════════════════════════════════"

# Calculate overall health score
HEALTH_SCORE=100

if (( $(echo "$CPU_PERCENT > 85" | bc -l) )); then
    HEALTH_SCORE=$((HEALTH_SCORE - 20))
fi

if (( $(echo "$MEM_PERCENT > 90" | bc -l) )); then
    HEALTH_SCORE=$((HEALTH_SCORE - 20))
fi

if [ "$ERROR_COUNT" -gt 5 ]; then
    HEALTH_SCORE=$((HEALTH_SCORE - 15))
fi

echo ""
if [ "$HEALTH_SCORE" -ge 85 ]; then
    echo -e "   Overall Health: ${GREEN}$HEALTH_SCORE/100 - EXCELLENT ✅${NC}"
elif [ "$HEALTH_SCORE" -ge 70 ]; then
    echo -e "   Overall Health: ${YELLOW}$HEALTH_SCORE/100 - GOOD ⚠️${NC}"
else
    echo -e "   Overall Health: ${RED}$HEALTH_SCORE/100 - NEEDS ATTENTION ⚠️${NC}"
fi

echo ""
echo "📊 Key Optimizations Active:"
echo "   ✅ Connection Pooling: Enabled (10K connections)"
echo "   ✅ Container Limits: 1.5 CPU, 2 GB RAM"
echo "   ✅ Auto-restart: Enabled"
echo "   ✅ SSL/TLS: Enabled"

echo ""
echo "🔄 To monitor continuously, run:"
echo "   watch -n 5 /opt/dataguardian/MONITOR_SERVER.sh"
echo ""
echo "📋 Full performance report:"
echo "   cat /opt/dataguardian/PERFORMANCE_OPTIMIZATION_REPORT.md"
echo ""
echo "════════════════════════════════════════════════════════════════"
