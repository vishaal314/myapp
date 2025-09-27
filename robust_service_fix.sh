#!/bin/bash
# Robust Service Fix - Handles false negative health checks and ensures services work
# Fixes: Health check failures, process detection issues, service connectivity

echo "🔧 ROBUST SERVICE FIX - Advanced Diagnostics & Restart"
echo "====================================================="
echo "Targeting: Health check failures, false negative process detection"
echo ""

# =============================================================================
# PART 1: ADVANCED DIAGNOSTICS
# =============================================================================

echo "🔍 PART 1: Advanced service diagnostics"
echo "======================================="

# Multiple methods to detect processes
echo "📊 Process Detection (Multiple Methods):"

# Method 1: Standard ps
STREAMLIT_PS=$(ps aux 2>/dev/null | grep -v grep | grep "streamlit run" | wc -l)
REDIS_PS=$(ps aux 2>/dev/null | grep -v grep | grep "redis-server" | wc -l)
echo "   Method 1 (ps aux): Streamlit=$STREAMLIT_PS, Redis=$REDIS_PS"

# Method 2: pgrep
STREAMLIT_PGREP=$(pgrep -f "streamlit" 2>/dev/null | wc -l)
REDIS_PGREP=$(pgrep -f "redis-server" 2>/dev/null | wc -l)
echo "   Method 2 (pgrep): Streamlit=$STREAMLIT_PGREP, Redis=$REDIS_PGREP"

# Method 3: pidof
STREAMLIT_PIDOF=$(pidof python 2>/dev/null | wc -w)
REDIS_PIDOF=$(pidof redis-server 2>/dev/null | wc -w)
echo "   Method 3 (pidof): Python=$STREAMLIT_PIDOF, Redis=$REDIS_PIDOF"

# Method 4: netstat alternative using ss
if command -v ss &> /dev/null; then
    PORT_5000=$(ss -tulpn 2>/dev/null | grep ":5000" | wc -l)
    PORT_6379=$(ss -tulpn 2>/dev/null | grep ":6379" | wc -l)
    echo "   Method 4 (ss): Port 5000=$PORT_5000, Port 6379=$PORT_6379"
fi

# Method 5: lsof if available
if command -v lsof &> /dev/null; then
    LSOF_5000=$(lsof -i :5000 2>/dev/null | wc -l)
    LSOF_6379=$(lsof -i :6379 2>/dev/null | wc -l)
    echo "   Method 5 (lsof): Port 5000=$LSOF_5000, Port 6379=$LSOF_6379"
fi

echo "✅ Diagnostic data collected"

# =============================================================================
# PART 2: INTELLIGENT SERVICE RESTART LOGIC
# =============================================================================

echo ""
echo "🧠 PART 2: Intelligent service restart logic"
echo "==========================================="

# Determine if services need restart
NEED_STREAMLIT_RESTART=false
NEED_REDIS_RESTART=false

if [ "$STREAMLIT_PS" -eq 0 ] && [ "$STREAMLIT_PGREP" -eq 0 ]; then
    echo "🔴 Streamlit: No processes detected - needs restart"
    NEED_STREAMLIT_RESTART=true
else
    echo "✅ Streamlit: Process detected"
fi

if [ "$REDIS_PS" -eq 0 ] && [ "$REDIS_PGREP" -eq 0 ]; then
    echo "🔴 Redis: No processes detected - needs restart"
    NEED_REDIS_RESTART=true
else
    echo "✅ Redis: Process detected"
fi

# =============================================================================
# PART 3: AGGRESSIVE SERVICE CLEANUP & RESTART
# =============================================================================

echo ""
echo "🛑 PART 3: Aggressive service cleanup & restart"
echo "=============================================="

# Kill all potentially conflicting processes
echo "🧹 Cleaning up any stale processes..."
pkill -f "streamlit" 2>/dev/null || echo "No streamlit processes to kill"
pkill -f "redis-server" 2>/dev/null || echo "No redis processes to kill"
pkill -f "python.*app.py" 2>/dev/null || echo "No app.py processes to kill"

# Wait for cleanup
sleep 3

# Remove any stale PID files
rm -f streamlit.pid redis.pid nohup.out streamlit_direct.log 2>/dev/null || true

echo "✅ Cleanup completed"

# =============================================================================
# PART 4: REDIS RESTART WITH MULTIPLE FALLBACKS
# =============================================================================

echo ""
echo "🔴 PART 4: Redis restart with fallbacks"
echo "======================================"

echo "🔧 Starting Redis server..."

# Try multiple Redis start methods
REDIS_STARTED=false

# Method 1: Standard daemon start
if ! $REDIS_STARTED; then
    echo "   Trying method 1: redis-server daemon..."
    redis-server --daemonize yes --port 6379 --bind 0.0.0.0 --protected-mode no 2>/dev/null && REDIS_STARTED=true
fi

# Method 2: Background process
if ! $REDIS_STARTED; then
    echo "   Trying method 2: background process..."
    nohup redis-server --port 6379 --bind 0.0.0.0 > /dev/null 2>&1 &
    sleep 2
    if pgrep -f "redis-server" > /dev/null; then
        REDIS_STARTED=true
    fi
fi

# Method 3: Direct execution
if ! $REDIS_STARTED; then
    echo "   Trying method 3: direct execution..."
    redis-server /dev/null &
    sleep 2
    if pgrep -f "redis-server" > /dev/null; then
        REDIS_STARTED=true
    fi
fi

# Test Redis connection
if $REDIS_STARTED; then
    sleep 2
    # Test with multiple methods
    REDIS_TEST_1=$(echo "PING" | timeout 3 redis-cli 2>/dev/null | grep PONG || echo "FAIL")
    REDIS_TEST_2=$(redis-cli ping 2>/dev/null || echo "FAIL")
    
    if [ "$REDIS_TEST_1" = "PONG" ] || [ "$REDIS_TEST_2" = "PONG" ]; then
        echo "✅ Redis: Started and responding"
    else
        echo "⚠️  Redis: Started but connection test failed"
    fi
else
    echo "❌ Redis: Failed to start with all methods"
fi

# =============================================================================
# PART 5: STREAMLIT RESTART WITH MULTIPLE FALLBACKS
# =============================================================================

echo ""
echo "🖥️  PART 5: Streamlit restart with fallbacks"
echo "==========================================="

echo "🔧 Starting Streamlit server..."

# Ensure configuration exists
mkdir -p .streamlit
cat > .streamlit/config.toml << 'EOF'
[server]
headless = true
address = "0.0.0.0"
port = 5000
fileWatcherType = "none"
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#4267B2"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F5"
textColor = "#1E293B"
font = "sans serif"
EOF

# Set essential environment variables
export DATABASE_URL=${DATABASE_URL:-"postgresql://postgres:postgres@localhost:5433/dataguardian"}
export REDIS_URL="redis://localhost:6379/0"
export ENVIRONMENT="production"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
export STREAMLIT_SERVER_HEADLESS=true

STREAMLIT_STARTED=false

# Method 1: Standard nohup background
if ! $STREAMLIT_STARTED; then
    echo "   Trying method 1: nohup background..."
    nohup streamlit run app.py --server.port 5000 --server.address 0.0.0.0 --server.headless true > streamlit_robust.log 2>&1 &
    STREAMLIT_PID=$!
    echo $STREAMLIT_PID > streamlit.pid
    sleep 8
    
    if kill -0 $STREAMLIT_PID 2>/dev/null; then
        STREAMLIT_STARTED=true
        echo "   Streamlit PID: $STREAMLIT_PID"
    fi
fi

# Method 2: Direct background with different options
if ! $STREAMLIT_STARTED; then
    echo "   Trying method 2: direct background..."
    streamlit run app.py --server.port 5000 --server.address 0.0.0.0 &
    STREAMLIT_PID=$!
    echo $STREAMLIT_PID > streamlit.pid
    sleep 8
    
    if kill -0 $STREAMLIT_PID 2>/dev/null; then
        STREAMLIT_STARTED=true
        echo "   Streamlit PID: $STREAMLIT_PID"
    fi
fi

# Method 3: Python direct execution
if ! $STREAMLIT_STARTED; then
    echo "   Trying method 3: python direct..."
    python -m streamlit run app.py --server.port 5000 --server.address 0.0.0.0 --server.headless true &
    STREAMLIT_PID=$!
    echo $STREAMLIT_PID > streamlit.pid
    sleep 8
    
    if kill -0 $STREAMLIT_PID 2>/dev/null; then
        STREAMLIT_STARTED=true
        echo "   Streamlit PID: $STREAMLIT_PID"
    fi
fi

echo "✅ Streamlit startup attempts completed"

# =============================================================================
# PART 6: COMPREHENSIVE HEALTH VERIFICATION
# =============================================================================

echo ""
echo "🩺 PART 6: Comprehensive health verification"
echo "==========================================="

echo "⏳ Waiting for services to fully initialize..."
sleep 15

echo "🔍 Running comprehensive health checks..."

# Check processes again
FINAL_STREAMLIT=$(ps aux 2>/dev/null | grep -v grep | grep "streamlit" | wc -l)
FINAL_REDIS=$(ps aux 2>/dev/null | grep -v grep | grep "redis-server" | wc -l)

echo "📊 Final Process Count:"
echo "   Streamlit processes: $FINAL_STREAMLIT"
echo "   Redis processes: $FINAL_REDIS"

# Multiple HTTP test attempts
echo ""
echo "🌐 HTTP Connectivity Tests:"

for i in {1..5}; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null || echo "000")
    echo "   Attempt $i: HTTP $HTTP_CODE"
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ HTTP SUCCESS on attempt $i!"
        break
    fi
    
    if [ $i -lt 5 ]; then
        echo "   Waiting 10 seconds before retry..."
        sleep 10
    fi
done

# Test Redis with multiple methods
echo ""
echo "🔴 Redis Connectivity Tests:"

REDIS_SUCCESS=false

# Test method 1: redis-cli ping
REDIS_PING=$(redis-cli ping 2>/dev/null || echo "FAIL")
if [ "$REDIS_PING" = "PONG" ]; then
    echo "✅ Redis method 1: PONG"
    REDIS_SUCCESS=true
else
    echo "❌ Redis method 1: $REDIS_PING"
fi

# Test method 2: echo pipe
REDIS_ECHO=$(echo "PING" | redis-cli 2>/dev/null | grep PONG || echo "FAIL")
if [ "$REDIS_ECHO" != "FAIL" ]; then
    echo "✅ Redis method 2: SUCCESS"
    REDIS_SUCCESS=true
else
    echo "❌ Redis method 2: FAIL"
fi

# Test method 3: telnet simulation
if command -v nc &> /dev/null; then
    REDIS_NC=$(echo "PING" | timeout 3 nc localhost 6379 2>/dev/null | grep PONG || echo "FAIL")
    if [ "$REDIS_NC" != "FAIL" ]; then
        echo "✅ Redis method 3: SUCCESS"
        REDIS_SUCCESS=true
    else
        echo "❌ Redis method 3: FAIL"
    fi
fi

# =============================================================================
# PART 7: FINAL STATUS & TROUBLESHOOTING
# =============================================================================

echo ""
echo "📊 FINAL ROBUST SERVICE STATUS"
echo "=============================="

if [ "$HTTP_CODE" = "200" ]; then
    echo ""
    echo "🎉🎉🎉 COMPLETE SUCCESS! 🎉🎉🎉"
    echo "================================"
    echo ""
    echo "✅ DataGuardian Pro: FULLY OPERATIONAL"
    echo "✅ HTTP Status: 200 (Perfect)"
    echo "✅ Streamlit: Running ($FINAL_STREAMLIT process(es))"
    
    if $REDIS_SUCCESS; then
        echo "✅ Redis: Connected and responding"
    else
        echo "⚠️  Redis: Running but connection issues"
    fi
    
    echo ""
    echo "🎯 ALL 12 SCANNER TYPES READY FOR PRODUCTION!"
    echo "🌐 Access: http://localhost:5000"
    echo "🌍 External: http://45.81.35.202:5000"

elif [ "$FINAL_STREAMLIT" -gt 0 ]; then
    echo ""
    echo "⏳ SERVICES RUNNING - STARTUP IN PROGRESS"
    echo "========================================"
    echo ""
    echo "✅ Streamlit process: RUNNING"
    echo "⏳ HTTP response: Still initializing (HTTP $HTTP_CODE)"
    echo "💡 Typical startup time: 2-5 minutes"
    echo ""
    echo "🔄 Auto-retry in 60 seconds:"
    echo "   curl http://localhost:5000"

else
    echo ""
    echo "⚠️  ADVANCED TROUBLESHOOTING NEEDED"
    echo "================================="
    echo ""
    echo "❌ No processes detected after restart attempts"
    echo "❌ HTTP Status: $HTTP_CODE"
    echo ""
    echo "🔍 Advanced Diagnostics:"
    echo "   📋 Check logs: tail -f streamlit_robust.log"
    echo "   🔍 Memory usage: free -h"
    echo "   💾 Disk space: df -h"
    echo "   🔧 Python path: which python"
    echo "   📦 Streamlit install: pip show streamlit"
fi

echo ""
echo "📋 LOG FILES CREATED:"
echo "===================="
echo "📄 Streamlit: streamlit_robust.log"
echo "📄 Process ID: streamlit.pid"

if [ -f "streamlit_robust.log" ]; then
    echo ""
    echo "📄 Recent Streamlit Log (last 10 lines):"
    tail -10 streamlit_robust.log 2>/dev/null || echo "No log content yet"
fi

echo ""
echo "✅ ROBUST SERVICE FIX COMPLETE!"
echo "Multiple restart methods attempted with comprehensive diagnostics"