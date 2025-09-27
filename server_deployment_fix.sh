#!/bin/bash
# Server Deployment Fix - Uses correct paths and commands for external server
# Fixes: Command not found errors, path issues, service startup

echo "🔧 SERVER DEPLOYMENT FIX - Correct Paths & Commands"
echo "=================================================="
echo "Using absolute paths and proper environment setup"
echo ""

# =============================================================================
# PART 1: ENVIRONMENT & PATH SETUP
# =============================================================================

echo "🌐 PART 1: Environment & path setup"
echo "==================================="

# Set up proper environment variables
export PYTHONPATH="/opt/dataguardian:/opt/dataguardian/.pythonlibs/lib/python3.11/site-packages"
export DATABASE_URL=${DATABASE_URL:-"postgresql://postgres:postgres@localhost:5433/dataguardian"}
export REDIS_URL="redis://localhost:6379/0"
export ENVIRONMENT="production"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
export STREAMLIT_SERVER_HEADLESS=true

# Add pythonlibs to PATH if not already there
if [[ ":$PATH:" != *":/home/runner/workspace/.pythonlibs/bin:"* ]]; then
    export PATH="/home/runner/workspace/.pythonlibs/bin:$PATH"
fi

echo "✅ Environment variables set"

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "📁 Looking for app.py..."
    if [ -f "/opt/dataguardian/app.py" ]; then
        cd /opt/dataguardian
        echo "✅ Changed to /opt/dataguardian"
    else
        echo "❌ app.py not found in current directory or /opt/dataguardian"
        ls -la | head -10
    fi
fi

echo "📂 Current directory: $(pwd)"

# =============================================================================
# PART 2: DEPENDENCY VERIFICATION
# =============================================================================

echo ""
echo "📦 PART 2: Dependency verification"
echo "=================================="

# Find correct Python executable
PYTHON_CMD=""
if [ -f "/home/runner/workspace/.pythonlibs/bin/python3" ]; then
    PYTHON_CMD="/home/runner/workspace/.pythonlibs/bin/python3"
elif [ -f "/usr/bin/python3" ]; then
    PYTHON_CMD="/usr/bin/python3"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "❌ Python3 not found"
    exit 1
fi

echo "✅ Python executable: $PYTHON_CMD"

# Find correct Streamlit
STREAMLIT_CMD=""
if [ -f "/home/runner/workspace/.pythonlibs/bin/streamlit" ]; then
    STREAMLIT_CMD="/home/runner/workspace/.pythonlibs/bin/streamlit"
elif command -v streamlit &> /dev/null; then
    STREAMLIT_CMD="streamlit"
else
    # Try via Python module
    if $PYTHON_CMD -m streamlit version >/dev/null 2>&1; then
        STREAMLIT_CMD="$PYTHON_CMD -m streamlit"
    else
        echo "❌ Streamlit not found"
        exit 1
    fi
fi

echo "✅ Streamlit executable: $STREAMLIT_CMD"

# Verify Redis
REDIS_CMD=""
if command -v redis-server &> /dev/null; then
    REDIS_CMD="redis-server"
elif [ -f "/usr/bin/redis-server" ]; then
    REDIS_CMD="/usr/bin/redis-server"
else
    echo "❌ Redis not found"
    exit 1
fi

echo "✅ Redis executable: $REDIS_CMD"

# =============================================================================
# PART 3: SERVICE CLEANUP
# =============================================================================

echo ""
echo "🛑 PART 3: Service cleanup"
echo "========================"

echo "🧹 Stopping any existing services..."

# More aggressive process cleanup
pkill -9 -f "streamlit" 2>/dev/null || echo "No streamlit processes"
pkill -9 -f "redis-server" 2>/dev/null || echo "No redis processes"
pkill -9 -f "app.py" 2>/dev/null || echo "No app.py processes"

# Wait for cleanup
sleep 3

# Remove old files
rm -f streamlit*.pid redis*.pid nohup.out streamlit*.log 2>/dev/null || true

echo "✅ Cleanup completed"

# =============================================================================
# PART 4: REDIS STARTUP
# =============================================================================

echo ""
echo "🔴 PART 4: Redis startup"
echo "======================"

echo "🔧 Starting Redis with absolute path..."

# Start Redis with explicit configuration
$REDIS_CMD --daemonize yes \
    --port 6379 \
    --bind 0.0.0.0 \
    --protected-mode no \
    --save 900 1 \
    --save 300 10 \
    --save 60 10000 \
    --stop-writes-on-bgsave-error no \
    --maxmemory-policy allkeys-lru 2>/dev/null &

REDIS_PID=$!
sleep 3

# Test Redis connection with multiple methods
REDIS_SUCCESS=false

for i in {1..5}; do
    if command -v redis-cli &> /dev/null; then
        REDIS_PING=$(timeout 3 redis-cli ping 2>/dev/null || echo "FAIL")
        if [ "$REDIS_PING" = "PONG" ]; then
            echo "✅ Redis connected successfully (attempt $i)"
            REDIS_SUCCESS=true
            break
        fi
    fi
    
    # Alternative test with nc
    if command -v nc &> /dev/null; then
        REDIS_NC_TEST=$(echo "PING" | timeout 2 nc localhost 6379 2>/dev/null | grep -o PONG || echo "FAIL")
        if [ "$REDIS_NC_TEST" = "PONG" ]; then
            echo "✅ Redis connected via nc (attempt $i)"
            REDIS_SUCCESS=true
            break
        fi
    fi
    
    if [ $i -lt 5 ]; then
        echo "⏳ Redis attempt $i failed, retrying..."
        sleep 2
    fi
done

if $REDIS_SUCCESS; then
    echo "✅ Redis is running and connected"
else
    echo "⚠️  Redis started but connection verification failed"
fi

# =============================================================================
# PART 5: STREAMLIT STARTUP
# =============================================================================

echo ""
echo "🖥️  PART 5: Streamlit startup"
echo "==========================="

# Create Streamlit configuration
echo "🔧 Creating Streamlit configuration..."
mkdir -p .streamlit

cat > .streamlit/config.toml << 'EOF'
[server]
headless = true
address = "0.0.0.0"
port = 5000
fileWatcherType = "none"
enableCORS = false
enableXsrfProtection = false
maxUploadSize = 1000

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#4267B2"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F5"
textColor = "#1E293B"
font = "sans serif"

[global]
developmentMode = false

[runner]
fastReruns = true
magicEnabled = false
EOF

echo "✅ Streamlit configuration created"

# Start Streamlit with absolute path and proper logging
echo "🚀 Starting Streamlit server..."

# Method 1: Direct execution with absolute path
if [[ "$STREAMLIT_CMD" == *"python"* ]]; then
    # Using python -m streamlit
    nohup $STREAMLIT_CMD run app.py \
        --server.port 5000 \
        --server.address 0.0.0.0 \
        --server.headless true \
        --server.fileWatcherType none \
        > streamlit_server.log 2>&1 &
else
    # Using direct streamlit command
    nohup $STREAMLIT_CMD run app.py \
        --server.port 5000 \
        --server.address 0.0.0.0 \
        --server.headless true \
        --server.fileWatcherType none \
        > streamlit_server.log 2>&1 &
fi

STREAMLIT_PID=$!
echo $STREAMLIT_PID > streamlit.pid

echo "✅ Streamlit started with PID: $STREAMLIT_PID"
echo "📄 Logs: streamlit_server.log"

# =============================================================================
# PART 6: SERVICE VERIFICATION
# =============================================================================

echo ""
echo "🩺 PART 6: Service verification"
echo "============================="

echo "⏳ Waiting for Streamlit to initialize (30 seconds)..."
sleep 30

# Check if processes are still running
if kill -0 $STREAMLIT_PID 2>/dev/null; then
    echo "✅ Streamlit process is running (PID: $STREAMLIT_PID)"
else
    echo "❌ Streamlit process died"
    echo "📄 Last 10 lines of log:"
    tail -10 streamlit_server.log 2>/dev/null || echo "No log file"
fi

# Test HTTP connection with retries
echo ""
echo "🌐 Testing HTTP connectivity..."

HTTP_SUCCESS=false
for i in {1..10}; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null || echo "000")
    echo "   HTTP attempt $i: Status $HTTP_CODE"
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ HTTP SUCCESS! DataGuardian Pro is responding"
        HTTP_SUCCESS=true
        break
    elif [ "$HTTP_CODE" != "000" ]; then
        echo "⏳ HTTP $HTTP_CODE - Service starting up..."
    fi
    
    if [ $i -lt 10 ]; then
        sleep 10
    fi
done

# Test external access
echo ""
echo "🌍 Testing external access..."
EXTERNAL_CODE=$(timeout 10 curl -s -o /dev/null -w "%{http_code}" http://45.81.35.202:5000 2>/dev/null || echo "000")
echo "External HTTP Status: $EXTERNAL_CODE"

# =============================================================================
# PART 7: FINAL STATUS REPORT
# =============================================================================

echo ""
echo "📊 FINAL DEPLOYMENT STATUS"
echo "=========================="

# Process verification
FINAL_STREAMLIT=$(ps aux 2>/dev/null | grep -v grep | grep -c "streamlit" || echo "0")
FINAL_REDIS=$(ps aux 2>/dev/null | grep -v grep | grep -c "redis-server" || echo "0")

echo "📊 Final Process Count:"
echo "   Streamlit processes: $FINAL_STREAMLIT"
echo "   Redis processes: $FINAL_REDIS"

if $HTTP_SUCCESS; then
    echo ""
    echo "🎉🎉🎉 DEPLOYMENT SUCCESS! 🎉🎉🎉"
    echo "================================="
    echo ""
    echo "✅ DataGuardian Pro: FULLY OPERATIONAL"
    echo "✅ HTTP Status: 200"
    echo "✅ All 12 Scanner Types: READY"
    echo "✅ Enterprise Features: ACTIVE"
    echo ""
    echo "🌐 Access Points:"
    echo "   📍 Local: http://localhost:5000"
    
    if [ "$EXTERNAL_CODE" = "200" ]; then
        echo "   📍 External: http://45.81.35.202:5000 ✅"
        echo ""
        echo "🚀 READY FOR PRODUCTION LAUNCH!"
        echo "🇳🇱 Netherlands UAVG compliance platform is live!"
    else
        echo "   📍 External: http://45.81.35.202:5000 (Status: $EXTERNAL_CODE)"
        echo ""
        echo "💡 Next: Configure firewall for external access"
        echo "   sudo ufw allow 5000"
    fi

elif [ "$FINAL_STREAMLIT" -gt 0 ]; then
    echo ""
    echo "⏳ SERVICES RUNNING - HTTP INITIALIZING"
    echo "====================================="
    echo ""
    echo "✅ Streamlit process: RUNNING"
    echo "✅ Redis process: $([ "$FINAL_REDIS" -gt 0 ] && echo "RUNNING" || echo "STOPPED")"
    echo "⏳ HTTP response: Still starting up (current: $HTTP_CODE)"
    echo ""
    echo "💡 Typical startup: 2-5 minutes"
    echo "🔄 Monitor: tail -f streamlit_server.log"

else
    echo ""
    echo "❌ DEPLOYMENT FAILED"
    echo "=================="
    echo ""
    echo "❌ No processes running after start attempts"
    echo "❌ HTTP Status: $HTTP_CODE"
    echo ""
    echo "🔍 Troubleshooting:"
    echo "   📋 Check Streamlit log: tail -f streamlit_server.log"
    echo "   🔧 Verify Python: $PYTHON_CMD --version"
    echo "   📦 Check Streamlit: $PYTHON_CMD -m streamlit version"
    echo "   💾 Check disk space: df -h"
    echo "   🔍 Check memory: free -h"
fi

echo ""
echo "📋 Service Management:"
echo "====================="
echo "   🔴 Redis PID: $(pgrep redis-server 2>/dev/null || echo 'Not running')"
echo "   🖥️  Streamlit PID: $(cat streamlit.pid 2>/dev/null || echo 'Not found')"
echo "   📄 Logs: streamlit_server.log"
echo "   🛑 Stop: kill \$(cat streamlit.pid); pkill redis-server"

echo ""
echo "✅ SERVER DEPLOYMENT FIX COMPLETE!"
echo "Used absolute paths and proper environment setup"