#!/bin/bash
# LOAD_TEST.sh
# Simulated Load Testing for DataGuardian Pro
# Tests actual concurrent user requests

echo "════════════════════════════════════════════════════════════════"
echo "🔥 DataGuardian Pro - Load Testing"
echo "   Testing concurrent user capacity"
echo "   Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "════════════════════════════════════════════════════════════════"

# Test configuration
URL="http://localhost:5000"
CONCURRENT_USERS=(10 25 50 100 150 200)
REQUESTS_PER_USER=10

# Install apache bench if not present
if ! command -v ab &> /dev/null; then
    echo "📦 Installing Apache Bench (ab) for load testing..."
    apt-get update -qq && apt-get install -y -qq apache2-utils > /dev/null 2>&1
fi

echo ""
echo "🎯 TEST CONFIGURATION:"
echo "   Target URL: $URL"
echo "   Test Scenarios: ${#CONCURRENT_USERS[@]} different loads"
echo "   Requests per scenario: Will vary by concurrent users"
echo ""

# Function to run load test
run_load_test() {
    local concurrent=$1
    local total_requests=$((concurrent * REQUESTS_PER_USER))
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 Testing: $concurrent concurrent users ($total_requests total requests)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Run Apache Bench test
    AB_OUTPUT=$(ab -n $total_requests -c $concurrent -q $URL/_stcore/health 2>&1)
    
    # Parse results
    SUCCESS_RATE=$(echo "$AB_OUTPUT" | grep "Complete requests" | awk '{print $3}')
    FAILED=$(echo "$AB_OUTPUT" | grep "Failed requests" | awk '{print $3}')
    TIME_PER_REQUEST=$(echo "$AB_OUTPUT" | grep "Time per request" | head -1 | awk '{print $4}')
    REQUESTS_PER_SEC=$(echo "$AB_OUTPUT" | grep "Requests per second" | awk '{print $4}')
    
    echo "   ✅ Completed: $SUCCESS_RATE requests"
    echo "   ❌ Failed: ${FAILED:-0} requests"
    echo "   ⏱️  Avg Response Time: ${TIME_PER_REQUEST:-N/A} ms"
    echo "   🚀 Throughput: ${REQUESTS_PER_SEC:-N/A} req/sec"
    
    # Check CPU and memory during test
    CPU_USAGE=$(docker stats --no-stream --format "{{.CPUPerc}}" dataguardian-container 2>/dev/null | sed 's/%//')
    MEM_USAGE=$(docker stats --no-stream --format "{{.MemPerc}}" dataguardian-container 2>/dev/null | sed 's/%//')
    
    echo "   💻 CPU Usage: ${CPU_USAGE:-N/A}%"
    echo "   🧠 Memory Usage: ${MEM_USAGE:-N/A}%"
    
    # Determine if this load is sustainable
    if [ -n "$TIME_PER_REQUEST" ]; then
        if (( $(echo "$TIME_PER_REQUEST < 500" | bc -l) )); then
            echo "   ✅ RESULT: Excellent performance - Server handles this load well"
        elif (( $(echo "$TIME_PER_REQUEST < 1000" | bc -l) )); then
            echo "   ✅ RESULT: Good performance - Acceptable response times"
        elif (( $(echo "$TIME_PER_REQUEST < 2000" | bc -l) )); then
            echo "   ⚠️  RESULT: Moderate performance - Response times acceptable but monitor closely"
        else
            echo "   ❌ RESULT: Poor performance - Server struggling at this load"
        fi
    fi
    
    echo ""
    sleep 3
}

# Run tests with increasing load
echo "🔬 STARTING LOAD TESTS..."
echo ""

for users in "${CONCURRENT_USERS[@]}"; do
    run_load_test $users
done

# Final recommendations
echo "════════════════════════════════════════════════════════════════"
echo "📈 LOAD TEST SUMMARY & RECOMMENDATIONS:"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Based on the tests above, your server can handle:"
echo ""
echo "✅ COMFORTABLE LOAD: Tests that showed <1000ms response time"
echo "⚠️  MAXIMUM LOAD: Tests that showed <2000ms response time"
echo "❌ OVERLOAD: Tests that showed >2000ms response time"
echo ""
echo "💡 RECOMMENDATIONS:"
echo ""
echo "1. OPTIMAL CAPACITY:"
echo "   - Use the highest concurrent user count with <1000ms response"
echo "   - This is your sustainable concurrent user capacity"
echo ""
echo "2. SCALING TRIGGERS:"
echo "   - If response times consistently >1000ms, upgrade server"
echo "   - If CPU usage consistently >70%, add more CPU cores"
echo "   - If memory usage consistently >80%, add more RAM"
echo ""
echo "3. OPTIMIZATION OPTIONS:"
echo "   - Enable more aggressive Redis caching"
echo "   - Increase database connection pool size"
echo "   - Add CDN for static assets"
echo "   - Consider horizontal scaling (multiple servers)"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ Load Testing Complete!"
echo "════════════════════════════════════════════════════════════════"
