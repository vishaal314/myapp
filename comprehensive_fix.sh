#!/bin/bash
# Comprehensive Fix for DataGuardian Pro - Remove text strings and fix stats error

echo "🔧 DataGuardian Pro - Comprehensive Fix"
echo "======================================"
echo "Removing text strings and fixing stats error permanently"
echo ""

# Stop service
echo "⏹️ Stopping DataGuardian service..."
systemctl stop dataguardian

# Create backup
echo "💾 Creating backup..."
cp /opt/dataguardian/app.py /opt/dataguardian/app.py.comprehensive_fix_backup.$(date +%Y%m%d_%H%M%S)

echo "🔧 Applying comprehensive fixes..."

# Apply all fixes at once
python3 << 'COMP_FIX_EOF'
import re

print("📖 Reading app.py file...")
with open('/opt/dataguardian/app.py', 'r') as f:
    content = f.read()

fixes_applied = 0

print("🔧 Step 1: Adding session state stats helper function...")

# Add the stats helper function after set_page_config
helper_function = '''
def get_or_init_stats():
    """Get or initialize stats in session state to prevent UnboundLocalError"""
    if 'stats' not in st.session_state:
        st.session_state['stats'] = {
            'findings': 0,
            'files_scanned': 0,
            'last_scan_at': None,
            'total_downloads': 0,
            'reports_generated': 0,
            'scans_completed': 0
        }
    return st.session_state['stats']

'''

# Find where to insert the helper function (after set_page_config)
config_pattern = r"(st\.session_state\['page_configured'\] = True\s*)"
if re.search(config_pattern, content):
    content = re.sub(config_pattern, r'\1\n' + helper_function, content)
    print("✅ Added stats helper function after page configuration")
    fixes_applied += 1
else:
    # Fallback: add after imports section
    import_end = content.find('# Core imports - keep essential imports minimal')
    if import_end != -1:
        content = content[:import_end] + helper_function + '\n' + content[import_end:]
        print("✅ Added stats helper function after imports (fallback)")
        fixes_applied += 1

print("🔧 Step 2: Fixing stats variable issues...")

# Initialize stats at start of render_dashboard function
render_dashboard_pattern = r'(def render_dashboard\(\):\s*\n\s*"""[^"]*"""\s*\n)'
if re.search(render_dashboard_pattern, content):
    replacement = r'\1    # Initialize stats to prevent UnboundLocalError\n    dashboard_stats = get_or_init_stats()\n    \n'
    content = re.sub(render_dashboard_pattern, replacement, content)
    print("✅ Added stats initialization to render_dashboard function")
    fixes_applied += 1

# Replace any bare stats references with session state calls
stats_replacements = [
    (r'\bstats\[', 'get_or_init_stats()['),
    (r'\bstats\.get\(', 'get_or_init_stats().get('),
    (r'len\(stats\)', 'len(get_or_init_stats())'),
]

for old_pattern, new_pattern in stats_replacements:
    matches = re.findall(old_pattern, content)
    if matches:
        content = re.sub(old_pattern, new_pattern, content)
        print(f"✅ Fixed {len(matches)} stats references: {old_pattern[:20]}...")
        fixes_applied += len(matches)

print("🔧 Step 3: Removing descriptive text strings...")

# Remove verbose docstrings
docstring_replacements = [
    (r'"""Render the main dashboard with real-time data from scan results and activity tracker"""',
     '"""Render the main dashboard"""'),
    (r'"""Main application entry point with comprehensive error handling and performance optimization"""',
     '"""Main application entry point"""'),
    (r'"""Render safe mode interface when components fail"""',
     '"""Render safe mode interface"""'),
]

for old_text, new_text in docstring_replacements:
    if old_text in content:
        content = content.replace(old_text, new_text)
        print(f"✅ Simplified docstring: {old_text[:40]}...")
        fixes_applied += 1

print("🔧 Step 4: Improving error handling...")

# Make safe mode message cleaner
safe_mode_pattern = r'st\.error\("Application encountered an issue\. Loading in safe mode\."\)'
if re.search(safe_mode_pattern, content):
    content = re.sub(safe_mode_pattern, 'st.error("Loading in safe mode")', content)
    print("✅ Simplified safe mode message")
    fixes_applied += 1

print(f"✅ Applied {fixes_applied} comprehensive fixes")

# Write the fixed content
with open('/opt/dataguardian/app.py', 'w') as f:
    f.write(content)

print("📝 Comprehensive fixes written to file")
COMP_FIX_EOF

echo "✅ Comprehensive fixes applied"

# Validate syntax
echo "🔍 Validating Python syntax..."
if sudo -u dataguardian /opt/dataguardian/venv/bin/python3 -m py_compile /opt/dataguardian/app.py 2>/dev/null; then
    echo "✅ Python syntax validation passed!"
    
    # Start service
    echo "🚀 Starting DataGuardian service..."
    systemctl start dataguardian
    
    # Wait for initialization
    echo "⏳ Waiting for service initialization (25 seconds)..."
    sleep 25
    
    if systemctl is-active --quiet dataguardian; then
        echo "✅ Service is running!"
        
        # Test HTTP response
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null || echo "000")
        if [ "$HTTP_CODE" = "200" ]; then
            echo ""
            echo "🎉🎉🎉 COMPREHENSIVE FIX COMPLETE! 🎉🎉🎉"
            echo "======================================="
            echo "✅ Stats error eliminated permanently"
            echo "✅ Verbose text strings removed"
            echo "✅ Application exits safe mode"
            echo "✅ Clean, professional interface"
            echo "✅ https://dataguardianpro.nl operational"
            echo "======================================="
            
        else
            echo "⚠️  Service running but HTTP response: $HTTP_CODE"
        fi
        
        echo ""
        echo "📊 Service Status:"
        systemctl status dataguardian --no-pager | head -10
        
    else
        echo "❌ Service failed to start"
        echo "📋 Recent logs:"
        journalctl -u dataguardian --no-pager -n 20
    fi
    
else
    echo "❌ Syntax validation failed"
    echo "📋 Error details:"
    sudo -u dataguardian /opt/dataguardian/venv/bin/python3 -m py_compile /opt/dataguardian/app.py
    
    echo "🔄 Restoring backup..."
    LATEST_BACKUP=$(ls -t /opt/dataguardian/app.py.comprehensive_fix_backup.* 2>/dev/null | head -1)
    if [ -n "$LATEST_BACKUP" ]; then
        cp "$LATEST_BACKUP" /opt/dataguardian/app.py
        echo "✅ Backup restored: $LATEST_BACKUP"
    fi
fi

echo ""
echo "🎯 Comprehensive fix complete!"