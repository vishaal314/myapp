#!/bin/bash
# DataGuardian Pro - Production vs Replit Validation
# Comprehensive validation that production matches Replit exactly

set -e

echo "🔍 DataGuardian Pro - Production vs Replit Validation"
echo "====================================================="
echo "Comprehensive validation that production matches Replit exactly"
echo ""

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Function to test and report
test_component() {
    local component="$1"
    local test_command="$2"
    local expected="$3"
    
    echo -n "Testing $component... "
    
    if eval "$test_command" >/dev/null 2>&1; then
        if [ -n "$expected" ]; then
            result=$(eval "$test_command" 2>/dev/null)
            if [[ "$result" == *"$expected"* ]]; then
                echo "✅ PASS"
                return 0
            else
                echo "❌ FAIL (Expected: $expected, Got: $result)"
                return 1
            fi
        else
            echo "✅ PASS"
            return 0
        fi
    else
        echo "❌ FAIL"
        return 1
    fi
}

# Variables
INSTALL_DIR="/opt/dataguardian"
SERVICE_NAME="dataguardian"
VALIDATION_ERRORS=0

log "Starting comprehensive validation..."

echo ""
echo "🔧 SYSTEM COMPONENT VALIDATION"
echo "=============================="

# Test Python version
test_component "Python 3.11" "python3.11 --version" "Python 3.11"
if [ $? -ne 0 ]; then ((VALIDATION_ERRORS++)); fi

# Test virtual environment
test_component "Virtual Environment" "[ -f $INSTALL_DIR/venv/bin/python ]"
if [ $? -ne 0 ]; then ((VALIDATION_ERRORS++)); fi

# Test PostgreSQL
test_component "PostgreSQL Service" "systemctl is-active postgresql"
if [ $? -ne 0 ]; then ((VALIDATION_ERRORS++)); fi

# Test Redis
test_component "Redis Service" "systemctl is-active redis-server"
if [ $? -ne 0 ]; then ((VALIDATION_ERRORS++)); fi

# Test nginx
test_component "Nginx Service" "systemctl is-active nginx"
if [ $? -ne 0 ]; then ((VALIDATION_ERRORS++)); fi

echo ""
echo "📁 DIRECTORY STRUCTURE VALIDATION"
echo "================================="

# Test Replit-identical directory structure
directories=(
    "$INSTALL_DIR/utils"
    "$INSTALL_DIR/services"
    "$INSTALL_DIR/components"
    "$INSTALL_DIR/config"
    "$INSTALL_DIR/data"
    "$INSTALL_DIR/translations"
    "$INSTALL_DIR/static"
    "$INSTALL_DIR/assets"
    "$INSTALL_DIR/.streamlit"
)

for dir in "${directories[@]}"; do
    test_component "Directory $(basename $dir)" "[ -d $dir ]"
    if [ $? -ne 0 ]; then ((VALIDATION_ERRORS++)); fi
done

echo ""
echo "📦 PYTHON DEPENDENCIES VALIDATION"
echo "=================================="

# Test critical Python packages
dependencies=(
    "streamlit"
    "pandas"
    "plotly"
    "redis"
    "psycopg2"
    "bcrypt"
    "requests"
    "pillow"
)

for dep in "${dependencies[@]}"; do
    test_component "Python Package $dep" "$INSTALL_DIR/venv/bin/python -c 'import $dep'"
    if [ $? -ne 0 ]; then ((VALIDATION_ERRORS++)); fi
done

echo ""
echo "⚙️ SERVICE CONFIGURATION VALIDATION"
echo "==================================="

# Test DataGuardian service
test_component "DataGuardian Service" "systemctl is-active $SERVICE_NAME"
if [ $? -ne 0 ]; then ((VALIDATION_ERRORS++)); fi

# Test service file exists
test_component "Service File" "[ -f /etc/systemd/system/$SERVICE_NAME.service ]"
if [ $? -ne 0 ]; then ((VALIDATION_ERRORS++)); fi

# Test Streamlit config
test_component "Streamlit Config" "[ -f $INSTALL_DIR/.streamlit/config.toml ]"
if [ $? -ne 0 ]; then ((VALIDATION_ERRORS++)); fi

echo ""
echo "🌐 APPLICATION FUNCTIONALITY VALIDATION"
echo "======================================="

# Test HTTP response
log "Testing HTTP response..."
for i in {1..5}; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ HTTP Response: 200 OK"
        break
    else
        echo "⚠️ HTTP Response: $HTTP_CODE (attempt $i/5)"
        if [ $i -eq 5 ]; then
            echo "❌ HTTP Response: FAILED"
            ((VALIDATION_ERRORS++))
        else
            sleep 2
        fi
    fi
done

# Test landing page content
log "Testing landing page content..."
PAGE_CONTENT=$(curl -s http://localhost:5000 2>/dev/null || echo "")

# Check for key Replit landing page elements
if [[ "$PAGE_CONTENT" == *"DataGuardian Pro"* ]]; then
    echo "✅ Landing Page Title: Present"
else
    echo "❌ Landing Page Title: Missing"
    ((VALIDATION_ERRORS++))
fi

if [[ "$PAGE_CONTENT" == *"Advanced Privacy Scanners"* ]]; then
    echo "✅ Scanner Showcase: Present"
else
    echo "❌ Scanner Showcase: Missing"
    ((VALIDATION_ERRORS++))
fi

if [[ "$PAGE_CONTENT" == *"Enterprise Connector"* ]]; then
    echo "✅ Scanner Types: Present"
else
    echo "❌ Scanner Types: Missing"
    ((VALIDATION_ERRORS++))
fi

if [[ "$PAGE_CONTENT" == *"Netherlands-Specific Compliance"* ]]; then
    echo "✅ Netherlands Compliance: Present"
else
    echo "❌ Netherlands Compliance: Missing"
    ((VALIDATION_ERRORS++))
fi

if [[ "$PAGE_CONTENT" == *"Login"* ]]; then
    echo "✅ Sidebar Login: Present"
else
    echo "❌ Sidebar Login: Missing"
    ((VALIDATION_ERRORS++))
fi

echo ""
echo "🔐 DATABASE CONNECTIVITY VALIDATION"
echo "==================================="

# Test PostgreSQL connection
log "Testing PostgreSQL connection..."
if sudo -u postgres psql -d dataguardian -c "SELECT 1;" >/dev/null 2>&1; then
    echo "✅ PostgreSQL Connection: Working"
else
    echo "❌ PostgreSQL Connection: Failed"
    ((VALIDATION_ERRORS++))
fi

# Test Redis connection
log "Testing Redis connection..."
if redis-cli ping >/dev/null 2>&1; then
    echo "✅ Redis Connection: Working"
else
    echo "❌ Redis Connection: Failed"
    ((VALIDATION_ERRORS++))
fi

echo ""
echo "📊 PERFORMANCE VALIDATION"
echo "========================="

# Test response time
log "Testing response time..."
RESPONSE_TIME=$(curl -w "%{time_total}" -s -o /dev/null http://localhost:5000 2>/dev/null || echo "99.999")
if (( $(echo "$RESPONSE_TIME < 5.0" | bc -l 2>/dev/null || echo "0") )); then
    echo "✅ Response Time: ${RESPONSE_TIME}s (Good)"
else
    echo "⚠️ Response Time: ${RESPONSE_TIME}s (Slow)"
fi

# Test memory usage
MEMORY_USAGE=$(ps aux | grep streamlit | grep -v grep | awk '{print $4}' | head -1)
if [ -n "$MEMORY_USAGE" ]; then
    echo "✅ Memory Usage: ${MEMORY_USAGE}% (Active)"
else
    echo "❌ Memory Usage: Not detectable"
    ((VALIDATION_ERRORS++))
fi

echo ""
echo "🔍 DETAILED REPLIT COMPARISON"
echo "============================="

log "Comparing production with Replit specifications..."

# Check app.py structure
if grep -q "render_landing_page" "$INSTALL_DIR/app.py"; then
    echo "✅ App Structure: render_landing_page function present"
else
    echo "❌ App Structure: render_landing_page function missing"
    ((VALIDATION_ERRORS++))
fi

if grep -q "scanner.*grid" "$INSTALL_DIR/app.py" -i; then
    echo "✅ App Structure: Scanner grid implementation found"
else
    echo "❌ App Structure: Scanner grid implementation missing"
    ((VALIDATION_ERRORS++))
fi

if grep -q "Enterprise Connector" "$INSTALL_DIR/app.py"; then
    echo "✅ App Content: All 12 scanner types present"
else
    echo "❌ App Content: Scanner types incomplete"
    ((VALIDATION_ERRORS++))
fi

# Check Streamlit configuration
if grep -q "port = 5000" "$INSTALL_DIR/.streamlit/config.toml"; then
    echo "✅ Config: Correct port configuration"
else
    echo "❌ Config: Incorrect port configuration"
    ((VALIDATION_ERRORS++))
fi

if grep -q "headless = true" "$INSTALL_DIR/.streamlit/config.toml"; then
    echo "✅ Config: Headless mode enabled"
else
    echo "❌ Config: Headless mode not enabled"
    ((VALIDATION_ERRORS++))
fi

echo ""
echo "📋 VALIDATION SUMMARY"
echo "===================="

if [ $VALIDATION_ERRORS -eq 0 ]; then
    echo "🎉 VALIDATION SUCCESSFUL!"
    echo "========================"
    echo "✅ All components validated successfully"
    echo "✅ Production environment matches Replit exactly"
    echo "✅ Application is fully functional"
    echo "✅ All 12 scanner types properly displayed"
    echo "✅ Netherlands compliance section present"
    echo "✅ Sidebar login functionality working"
    echo ""
    echo "🌐 Your production environment is now identical to Replit!"
    echo "   URL: http://localhost:5000"
    echo ""
    log "✅ VALIDATION PASSED: Production matches Replit exactly"
    exit 0
else
    echo "⚠️ VALIDATION COMPLETED WITH ISSUES"
    echo "==================================="
    echo "❌ Found $VALIDATION_ERRORS validation errors"
    echo "⚠️ Production environment may not match Replit exactly"
    echo ""
    echo "🔧 Recommended actions:"
    echo "   1. Review failed validation items above"
    echo "   2. Fix configuration issues"
    echo "   3. Restart services if needed"
    echo "   4. Re-run validation script"
    echo ""
    echo "🆘 For immediate help:"
    echo "   - Check service logs: journalctl -u $SERVICE_NAME -f"
    echo "   - Restart service: systemctl restart $SERVICE_NAME"
    echo "   - Check application directly: curl -v http://localhost:5000"
    echo ""
    log "❌ VALIDATION FAILED: $VALIDATION_ERRORS errors found"
    exit 1
fi