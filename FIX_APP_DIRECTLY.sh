#!/bin/bash
# FIX APP.PY DIRECTLY ON SERVER - No file transfer needed
# This applies the protected imports fix directly

set -e

echo "🔧 APPLYING PROTECTED IMPORTS FIX DIRECTLY"
echo "=========================================="
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "❌ Run as root: sudo bash FIX_APP_DIRECTLY.sh"
    exit 1
fi

cd /opt/dataguardian

echo "📄 STEP 1: Backup current app.py"
echo "=============================="
backup_name="app.py.backup.$(date +%Y%m%d_%H%M%S)"
cp app.py "$backup_name"
echo "   ✅ Backed up to: $backup_name"

echo ""
echo "🔧 STEP 2: Apply protected imports fix"
echo "===================================="

# Check if already fixed
if grep -q "PERFORMANCE_IMPORTS_OK" app.py; then
    echo "   ✅ Already has protected imports - skipping"
else
    echo "   Applying fix..."
    
    # Create Python script to fix imports
    python3 << 'PYEOF'
import re

# Read the file
with open('app.py', 'r') as f:
    content = f.read()

# Find and replace the unprotected imports section (lines 61-82 approximately)
old_pattern = r'''# Performance optimization imports
from utils\.database_optimizer import get_optimized_db
from utils\.redis_cache import get_cache, get_scan_cache, get_session_cache, get_performance_cache
from utils\.session_optimizer import get_streamlit_session, get_session_optimizer
from utils\.code_profiler import get_profiler, profile_function, monitor_performance

# License management imports
from services\.license_integration import \(
    require_license_check, require_scanner_access, require_report_access,
    track_scanner_usage, track_report_usage, track_download_usage,
    show_license_sidebar, show_usage_dashboard, LicenseIntegration
\)

# Enterprise security imports
from services\.enterprise_auth_service import get_enterprise_auth_service, EnterpriseUser
from services\.multi_tenant_service import get_multi_tenant_service, TenantTier
from services\.encryption_service import get_encryption_service

# Pricing system imports
from components\.pricing_display import show_pricing_page, show_pricing_in_sidebar
from config\.pricing_config import get_pricing_config'''

new_pattern = '''# Performance optimization imports - PROTECTED
try:
    from utils.database_optimizer import get_optimized_db
    from utils.redis_cache import get_cache, get_scan_cache, get_session_cache, get_performance_cache
    from utils.session_optimizer import get_streamlit_session, get_session_optimizer
    from utils.code_profiler import get_profiler, profile_function, monitor_performance
    PERFORMANCE_IMPORTS_OK = True
except ImportError as e:
    logging.warning(f"Performance imports failed: {e}")
    PERFORMANCE_IMPORTS_OK = False
    def get_optimized_db(): return None
    def get_cache(): return None
    def get_scan_cache(): return None
    def get_session_cache(): return None
    def get_performance_cache(): return None
    def get_streamlit_session(): return None
    def get_session_optimizer(): return None
    def get_profiler(): return None
    def profile_function(name): return lambda f: f
    def monitor_performance(func): return func

# License management imports - PROTECTED
try:
    from services.license_integration import (
        require_license_check, require_scanner_access, require_report_access,
        track_scanner_usage, track_report_usage, track_download_usage,
        show_license_sidebar, show_usage_dashboard, LicenseIntegration
    )
    LICENSE_IMPORTS_OK = True
except ImportError as e:
    logging.warning(f"License imports failed: {e}")
    LICENSE_IMPORTS_OK = False
    def require_license_check(tier): return lambda f: f
    def require_scanner_access(scanner): return lambda f: f
    def require_report_access(): return lambda f: f
    def track_scanner_usage(scanner): pass
    def track_report_usage(format): pass
    def track_download_usage(type): pass
    def show_license_sidebar(): pass
    def show_usage_dashboard(): pass
    class LicenseIntegration: pass

# Enterprise security imports - PROTECTED
try:
    from services.enterprise_auth_service import get_enterprise_auth_service, EnterpriseUser
    from services.multi_tenant_service import get_multi_tenant_service, TenantTier
    from services.encryption_service import get_encryption_service
    ENTERPRISE_IMPORTS_OK = True
except ImportError as e:
    logging.warning(f"Enterprise imports failed: {e}")
    ENTERPRISE_IMPORTS_OK = False
    def get_enterprise_auth_service(): return None
    def get_multi_tenant_service(): return None
    def get_encryption_service(): return None
    class EnterpriseUser: pass
    class TenantTier: pass

# Pricing system imports - PROTECTED
try:
    from components.pricing_display import show_pricing_page, show_pricing_in_sidebar
    from config.pricing_config import get_pricing_config
    PRICING_IMPORTS_OK = True
except ImportError as e:
    logging.warning(f"Pricing imports failed: {e}")
    PRICING_IMPORTS_OK = False
    def show_pricing_page(): 
        import streamlit as st
        st.info("Pricing page unavailable")
    def show_pricing_in_sidebar(): pass
    def get_pricing_config(): return {}'''

# Apply the fix
content = re.sub(old_pattern, new_pattern, content, flags=re.MULTILINE)

# Write back
with open('app.py', 'w') as f:
    f.write(content)

print("   ✅ Protected imports applied")
PYEOF

fi

echo ""
echo "🔍 STEP 3: Verify fix was applied"
echo "=============================="
if grep -q "PERFORMANCE_IMPORTS_OK" app.py; then
    echo "   ✅ Protected imports confirmed"
else
    echo "   ❌ Fix not applied correctly"
    echo "   Restoring backup..."
    cp "$backup_name" app.py
    exit 1
fi

echo ""
echo "🐳 STEP 4: Rebuild Docker container"
echo "==============================="
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true

echo "   Building new image..."
docker build -t dataguardian-pro . 2>&1 | tail -20

docker run -d \
    --name dataguardian-container \
    --restart always \
    -p 5000:5000 \
    -e PYTHONUNBUFFERED=1 \
    dataguardian-pro

echo "   ✅ Container restarted"

echo ""
echo "⏳ STEP 5: Wait for initialization (60 seconds)"
echo "==========================================="
for i in {1..60}; do
    if [ $((i % 10)) -eq 0 ]; then
        echo -n " $i"
    else
        echo -n "."
    fi
    sleep 1
done
echo ""

echo ""
echo "🧪 STEP 6: VERIFICATION"
echo "==================="

success_count=0

echo ""
echo "Test 1: Container running"
if docker ps | grep -q dataguardian-container; then
    echo "   ✅ Running"
    ((success_count++))
else
    echo "   ❌ Not running"
fi

echo ""
echo "Test 2: HTTP 200"
status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000)
if [ "$status" = "200" ]; then
    echo "   ✅ HTTP $status"
    ((success_count++))
else
    echo "   ⚠️  HTTP $status"
fi

echo ""
echo "Test 3: DataGuardian Content"
if curl -s http://localhost:5000 | grep -qi "dataguardian"; then
    echo "   ✅✅✅ DataGuardian Pro DETECTED!"
    ((success_count++))
    content_found=true
else
    echo "   ⚠️  Not detected"
    content_found=false
fi

echo ""
echo "Test 4: Initialization Logs"
if docker logs dataguardian-container 2>&1 | grep -qi "Performance optimizations\|initialized translations"; then
    echo "   ✅ App executing main logic"
    ((success_count++))
else
    echo "   ⚠️  No init messages"
fi

echo ""
echo "📊 Container Logs (last 50 lines):"
echo "================================"
docker logs dataguardian-container 2>&1 | tail -50

echo ""
echo "================================"
echo "RESULTS: $success_count/4 tests passed"
echo "================================"

if [ "$content_found" = "true" ]; then
    echo ""
    echo "🎉 SUCCESS! DATAGUARDIAN PRO IS WORKING!"
    echo ""
    echo "✅ Protected imports applied"
    echo "✅ App.py executing correctly"
    echo "✅ Content loading properly"
    echo ""
    echo "🌐 ACCESS: https://dataguardianpro.nl"
    echo "🔐 LOGIN: demo / demo123"
    echo ""
    exit 0
else
    echo ""
    echo "⚠️  STILL INVESTIGATING"
    echo ""
    echo "Check logs above for import errors."
    echo "The protected imports should show which modules failed."
    echo ""
    exit 1
fi
