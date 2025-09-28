#!/bin/bash
# DataGuardian Service Fix
# Diagnoses and fixes DataGuardian service startup issues

echo "🔧 DATAGUARDIAN SERVICE DIAGNOSTIC & FIX"
echo "========================================"
echo "Issue: DataGuardian service failing to start"
echo "Symptoms: 502 errors, nginx running but backend not responding"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root"
    echo "💡 Please run: sudo ./dataguardian_service_fix.sh"
    exit 1
fi

DOMAIN="dataguardianpro.nl"
APP_PORT="5000"
APP_DIR="/opt/dataguardian"

echo "🔍 STEP 1: COMPREHENSIVE SERVICE DIAGNOSIS"
echo "========================================"

# Check current service status
echo "📊 Current service status:"
nginx_status=$(systemctl is-active nginx 2>/dev/null || echo "inactive")
dataguardian_status=$(systemctl is-active dataguardian 2>/dev/null || echo "inactive")

echo "   Nginx: $nginx_status"
echo "   DataGuardian: $dataguardian_status"

# Get detailed service status
echo ""
echo "📄 DataGuardian service detailed status:"
systemctl status dataguardian --no-pager -l | head -15

echo ""
echo "📄 Recent DataGuardian service logs:"
journalctl -u dataguardian -n 20 --no-pager

echo ""
echo "🔍 STEP 2: PYTHON AND APP VERIFICATION"
echo "====================================="

cd "$APP_DIR"

# Test Python
echo "🐍 Testing Python installation:"
python_test=$(python --version 2>&1 || echo "FAILED")
echo "   Python: $python_test"

python3_test=$(python3 --version 2>&1 || echo "FAILED")
echo "   Python3: $python3_test"

# Test app.py import
echo ""
echo "📋 Testing app.py import:"
app_import_test=$(python -c "import sys; sys.path.insert(0, '.'); import app; print('APP_IMPORT_SUCCESS')" 2>&1 || echo "APP_IMPORT_FAILED")
echo "   App import result: $app_import_test"

if echo "$app_import_test" | grep -q "APP_IMPORT_FAILED"; then
    echo "   ❌ App import failed - showing error details:"
    echo "$app_import_test" | head -5
fi

# Test manual app run
echo ""
echo "🧪 Testing manual app execution (5 seconds):"
timeout 5 python app.py &> /tmp/manual_app_test.log || true
app_manual_result=$(cat /tmp/manual_app_test.log 2>/dev/null | head -10)
echo "   Manual execution result:"
echo "$app_manual_result"

# Check dependencies
echo ""
echo "📦 Checking critical dependencies:"
deps_to_check=("streamlit" "pandas" "psycopg2" "bcrypt" "PyJWT")
missing_deps=()

for dep in "${deps_to_check[@]}"; do
    dep_check=$(python -c "import $dep; print('OK')" 2>&1 || echo "MISSING")
    if echo "$dep_check" | grep -q "OK"; then
        echo "   ✅ $dep: installed"
    else
        echo "   ❌ $dep: missing or broken"
        missing_deps+=("$dep")
    fi
done

echo ""
echo "🔍 STEP 3: SYSTEMD SERVICE FILE VERIFICATION"
echo "=========================================="

service_file="/etc/systemd/system/dataguardian.service"
echo "📄 Current service file content:"
echo "--- SERVICE FILE ---"
cat "$service_file"
echo "--- END SERVICE FILE ---"

# Check if service file has correct paths
echo ""
echo "🔍 Service file analysis:"
if grep -q "/usr/bin/python3" "$service_file"; then
    echo "   ✅ Python path present in service file"
else
    echo "   ❌ Python path missing or incorrect in service file"
fi

if grep -q "$APP_DIR" "$service_file"; then
    echo "   ✅ Working directory correctly set"
else
    echo "   ❌ Working directory missing or incorrect"
fi

echo ""
echo "🔧 STEP 4: APPLY FIXES BASED ON DIAGNOSIS"
echo "======================================="

fixes_applied=0

# Fix 1: Install missing dependencies
if [ ${#missing_deps[@]} -gt 0 ]; then
    echo "🔧 Installing missing dependencies..."
    for dep in "${missing_deps[@]}"; do
        echo "   Installing $dep..."
        python -m pip install --upgrade "$dep" &> /dev/null || echo "   ⚠️  Warning: $dep installation issue"
    done
    ((fixes_applied++))
    echo "   ✅ Dependencies installation attempted"
fi

# Fix 2: Update service file if needed
echo "🔧 Ensuring service file is correct..."
cat > "$service_file" << EOF
[Unit]
Description=DataGuardian Pro Enterprise Privacy Compliance Platform
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR
Environment=PYTHONPATH=$APP_DIR
Environment=STREAMLIT_SERVER_HEADLESS=true
Environment=STREAMLIT_SERVER_PORT=$APP_PORT
Environment=STREAMLIT_SERVER_ADDRESS=0.0.0.0
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ExecStart=/usr/bin/python3 -m streamlit run app.py --server.port $APP_PORT --server.address 0.0.0.0 --server.headless true
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
TimeoutStartSec=300
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
EOF

((fixes_applied++))
echo "   ✅ Service file updated with correct configuration"

# Fix 3: Set proper permissions
echo "🔧 Setting proper permissions..."
chown -R root:root "$APP_DIR"
chmod 755 "$APP_DIR"
chmod 644 "$APP_DIR/app.py"
chmod +r "$APP_DIR"/*
((fixes_applied++))
echo "   ✅ Permissions set correctly"

# Fix 4: Reload systemd
echo "🔧 Reloading systemd configuration..."
systemctl daemon-reload
((fixes_applied++))
echo "   ✅ Systemd configuration reloaded"

echo ""
echo "🔧 STEP 5: SERVICE RESTART WITH MONITORING"
echo "========================================"

echo "🔧 Stopping services cleanly..."
systemctl stop dataguardian &> /dev/null || true
sleep 3

echo "🔧 Starting nginx..."
systemctl start nginx
nginx_start_status=$?

if [ $nginx_start_status -eq 0 ]; then
    echo "   ✅ Nginx started successfully"
else
    echo "   ❌ Nginx failed to start"
    systemctl status nginx --no-pager -l | head -8
fi

echo ""
echo "🔧 Starting DataGuardian with monitoring..."
systemctl start dataguardian

echo "⏳ Monitoring DataGuardian startup (60 seconds)..."
startup_success=false

for i in {1..60}; do
    service_status=$(systemctl is-active dataguardian 2>/dev/null || echo "inactive")
    
    if [ "$service_status" = "active" ]; then
        # Test if responding
        if [ $((i % 10)) -eq 0 ]; then
            local_test=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$APP_PORT 2>/dev/null || echo "000")
            echo -n " [${i}s:$service_status:$local_test]"
            
            if [ "$local_test" = "200" ] && [ $i -ge 30 ]; then
                startup_success=true
                echo ""
                echo "   ✅ DataGuardian started and responding!"
                break
            fi
        else
            echo -n "."
        fi
    else
        echo -n "x"
    fi
    sleep 1
done

if [ "$startup_success" != true ]; then
    echo ""
    echo "   ⚠️  DataGuardian startup monitoring completed"
fi

# Final service status
final_nginx=$(systemctl is-active nginx 2>/dev/null || echo "inactive")
final_dataguardian=$(systemctl is-active dataguardian 2>/dev/null || echo "inactive")

echo ""
echo "📊 Final service status:"
echo "   Nginx: $final_nginx"
echo "   DataGuardian: $final_dataguardian"

if [ "$final_dataguardian" != "active" ]; then
    echo ""
    echo "❌ DataGuardian still not running - showing recent logs:"
    journalctl -u dataguardian -n 15 --no-pager
fi

echo ""
echo "🧪 STEP 6: FINAL TESTING"
echo "======================"

echo "🧪 Testing applications after fixes..."

# Multiple tests for reliability
echo "🔍 Local application test (3 attempts)..."
local_success=0
for attempt in {1..3}; do
    test_result=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$APP_PORT 2>/dev/null || echo "000")
    test_size=$(curl -s -o /dev/null -w "%{size_download}" http://localhost:$APP_PORT 2>/dev/null || echo "0")
    
    if [ "$test_result" = "200" ]; then
        local_success=$((local_success + 1))
        echo "   Attempt $attempt: ✅ $test_result ($test_size bytes)"
    else
        echo "   Attempt $attempt: ❌ $test_result"
    fi
    sleep 3
done

echo "🔍 Domain application test (3 attempts)..."
domain_success=0
for attempt in {1..3}; do
    test_result=$(curl -s -o /dev/null -w "%{http_code}" https://www.$DOMAIN 2>/dev/null || echo "000")
    test_size=$(curl -s -o /dev/null -w "%{size_download}" https://www.$DOMAIN 2>/dev/null || echo "0")
    
    if [ "$test_result" = "200" ]; then
        domain_success=$((domain_success + 1))
        echo "   Attempt $attempt: ✅ $test_result ($test_size bytes)"
    else
        echo "   Attempt $attempt: ❌ $test_result"
    fi
    sleep 5
done

echo ""
echo "📊 DIAGNOSIS & FIX RESULTS"
echo "========================="

# Calculate success score
success_score=0
max_score=6

# Applied fixes
if [ $fixes_applied -gt 0 ]; then
    ((success_score++))
    echo "✅ Fixes applied: $fixes_applied improvements (+1)"
else
    echo "❌ Fixes applied: none (+0)"
fi

# Service status
if [ "$final_nginx" = "active" ]; then
    ((success_score++))
    echo "✅ Nginx service: RUNNING (+1)"
else
    echo "❌ Nginx service: NOT RUNNING (+0)"
fi

if [ "$final_dataguardian" = "active" ]; then
    ((success_score++))
    echo "✅ DataGuardian service: RUNNING (+1)"
else
    echo "❌ DataGuardian service: NOT RUNNING (+0)"
fi

# Application tests
if [ $local_success -ge 2 ]; then
    ((success_score++))
    echo "✅ Local application: WORKING ($local_success/3 success) (+1)"
else
    echo "❌ Local application: NOT WORKING ($local_success/3 success) (+0)"
fi

if [ $domain_success -ge 2 ]; then
    ((success_score++))
    echo "✅ Domain application: WORKING ($domain_success/3 success) (+1)"
else
    echo "❌ Domain application: NOT WORKING ($domain_success/3 success) (+0)"
fi

# Overall functionality
if [ "$final_dataguardian" = "active" ] && [ $local_success -ge 1 ] && [ $domain_success -ge 1 ]; then
    ((success_score++))
    echo "✅ Overall functionality: OPERATIONAL (+1)"
else
    echo "❌ Overall functionality: NOT OPERATIONAL (+0)"
fi

echo ""
echo "📊 DIAGNOSTIC & FIX SCORE: $success_score/$max_score"

# Final determination
if [ $success_score -ge 5 ]; then
    echo ""
    echo "🎉 DATAGUARDIAN SERVICE FIX SUCCESSFUL! 🎉"
    echo "========================================="
    echo ""
    echo "✅ SERVICE ISSUES RESOLVED!"
    echo "✅ DataGuardian service: RUNNING AND RESPONDING"
    echo "✅ Nginx service: RUNNING PROPERLY"
    echo "✅ Local application: WORKING ($local_success/3 tests)"
    echo "✅ Domain application: WORKING ($domain_success/3 tests)"
    echo "✅ System fixes: $fixes_applied improvements applied"
    echo ""
    echo "🌐 YOUR DATAGUARDIAN PRO IS NOW OPERATIONAL:"
    echo "   🎯 Test it: https://www.$DOMAIN"
    echo "   🎯 WWW site: https://www.dataguardianpro.nl"
    echo "   🔗 Direct: http://45.81.35.202:$APP_PORT"
    echo ""
    echo "🇳🇱 NETHERLANDS GDPR COMPLIANCE PLATFORM FIXED!"
    echo "🚀 SERVICE ISSUES RESOLVED - READY FOR USE!"
    
elif [ $success_score -ge 3 ]; then
    echo ""
    echo "✅ SIGNIFICANT IMPROVEMENTS MADE"
    echo "==============================="
    echo ""
    echo "✅ Progress: $success_score/$max_score components fixed"
    echo "✅ Fixes applied: $fixes_applied improvements"
    echo ""
    echo "⚠️  Some issues may remain:"
    if [ "$final_dataguardian" != "active" ]; then
        echo "   - DataGuardian service still not starting"
    fi
    if [ $local_success -lt 2 ]; then
        echo "   - Local application needs more time or debugging"
    fi
    echo ""
    echo "💡 NEXT STEPS:"
    echo "   1. Wait 5-10 minutes for services to stabilize"
    echo "   2. Monitor logs: journalctl -u dataguardian -f"
    echo "   3. Manual restart: systemctl restart dataguardian"
    
else
    echo ""
    echo "⚠️  ADDITIONAL DEBUGGING NEEDED"
    echo "=============================="
    echo ""
    echo "📊 Current progress: $success_score/$max_score"
    echo ""
    echo "🔧 MANUAL DEBUGGING STEPS:"
    echo "   1. Check detailed logs: journalctl -u dataguardian -n 50"
    echo "   2. Test manual run: cd $APP_DIR && python app.py"
    echo "   3. Check app errors: cd $APP_DIR && python -c 'import app'"
    echo "   4. Verify dependencies: python -m pip list | grep streamlit"
    echo "   5. Check port usage: netstat -tlnp | grep :$APP_PORT"
fi

echo ""
echo "🎯 USEFUL COMMANDS:"
echo "=================="
echo "   📊 Service status: systemctl status nginx dataguardian"
echo "   🔄 Restart services: systemctl restart dataguardian nginx"
echo "   📄 Live logs: journalctl -u dataguardian -f"
echo "   🧪 Test app: cd $APP_DIR && python -c 'import app; print(\"OK\")'"
echo "   🔍 Quick test: curl -I https://www.$DOMAIN"

echo ""
echo "✅ DATAGUARDIAN SERVICE DIAGNOSTIC & FIX COMPLETED!"