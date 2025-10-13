#!/bin/bash
echo "════════════════════════════════════════════════════════════════"
echo "  📊 DataGuardian Pro - Performance Monitor"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "════════════════════════════════════════════════════════════════"

echo ""
echo "Container Status:"
docker ps | grep -q dataguardian-container && echo "✅ Running" || echo "❌ Stopped"

echo ""
echo "Resources:"
docker stats dataguardian-container --no-stream --format "CPU: {{.CPUPerc}}  Memory: {{.MemUsage}} ({{.MemPerc}})"

echo ""
echo "Database:"
# Capture ALL output and look for OK: pattern specifically
DB_OUTPUT=$(docker exec dataguardian-container python3 << 'DBTEST' 2>&1
import sys
sys.path.insert(0, '/app')
try:
    from services.results_aggregator import ResultsAggregator
    agg = ResultsAggregator()
    scans = agg.get_user_scans('vishaal314', limit=5, organization_id='default_org')
    print(f'DB_SUCCESS:{len(scans)}')
except Exception as e:
    print(f'DB_ERROR:{e}')
DBTEST
)

# Check if output contains DB_SUCCESS anywhere in the text
if echo "$DB_OUTPUT" | grep -q "DB_SUCCESS:"; then
    COUNT=$(echo "$DB_OUTPUT" | grep -o "DB_SUCCESS:[0-9]*" | cut -d':' -f2)
    echo "✅ Connected (retrieved $COUNT scans)"
else
    echo "❌ Connection failed"
    echo "$DB_OUTPUT" | grep "DB_ERROR:" | cut -d':' -f2- | head -1
fi

echo ""
echo "External Access:"
if curl -sf https://dataguardianpro.nl >/dev/null 2>&1; then
    RESP_TIME=$(curl -o /dev/null -s -w '%{time_total}\n' https://dataguardianpro.nl)
    echo "✅ https://dataguardianpro.nl (${RESP_TIME}s)"
else
    echo "❌ Site down"
fi

echo ""
echo "Disk Usage:"
df -h / | tail -1 | awk '{printf "%s used of %s (%s)\n", $3, $2, $5}'

DISK_PCT=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_PCT" -gt 90 ]; then
    echo "⚠️  WARNING: Disk >90% - Run cleanup!"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Continuous monitor: watch -n 5 ./MONITOR_SERVER.sh"
echo "════════════════════════════════════════════════════════════════"
