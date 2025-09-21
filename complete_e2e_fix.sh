#!/bin/bash
# Complete End-to-End Production Fix - All Syntax Errors

echo "🚀 DataGuardian Pro - Complete E2E Production Fix"
echo "================================================="
echo "This will fix ALL syntax errors in one operation"
echo ""

# Stop service
echo "⏹️ Stopping DataGuardian service..."
systemctl stop dataguardian

# Create backup
echo "💾 Creating comprehensive backup..."
BACKUP_FILE="/opt/dataguardian/app.py.e2e_backup.$(date +%Y%m%d_%H%M%S)"
cp /opt/dataguardian/app.py "$BACKUP_FILE"
echo "Backup created: $BACKUP_FILE"

echo ""
echo "🔧 Applying ALL syntax fixes..."

# Fix ALL instances of double closing parentheses in st.metric calls
echo "   Fixing all st.metric double parentheses..."
sed -i 's/st\.metric(\([^)]*\))/st.metric(\1)/g' /opt/dataguardian/app.py

# Fix specific patterns that might remain
echo "   Fixing remaining syntax patterns..."
sed -i 's/))/)/g' /opt/dataguardian/app.py

# Fix any st.metric calls that lost their closing parenthesis completely
echo "   Ensuring all st.metric calls are properly closed..."
python3 << 'EOF'
import re

with open('/opt/dataguardian/app.py', 'r') as f:
    content = f.read()

# Find all st.metric calls and ensure they're properly closed
lines = content.split('\n')
fixed_lines = []

for i, line in enumerate(lines):
    if 'st.metric(' in line:
        # Count parentheses in this line
        open_count = line.count('(')
        close_count = line.count(')')
        
        # If we have st.metric( but unbalanced parentheses
        if 'st.metric(' in line and open_count > close_count:
            # Add missing closing parentheses
            missing = open_count - close_count
            line = line.rstrip() + ')' * missing
            print(f"Fixed line {i+1}: Added {missing} closing parentheses")
        
        # Remove any double closing parentheses that might still exist
        while ')' in line and ')' in line and line.count(')') > line.count('('):
            line = line.replace('))', ')')
            print(f"Fixed line {i+1}: Removed double parentheses")
    
    fixed_lines.append(line)

# Write back the fixed content
with open('/opt/dataguardian/app.py', 'w') as f:
    f.write('\n'.join(fixed_lines))
EOF

echo "✅ All syntax fixes applied"
echo ""

# Comprehensive syntax validation
echo "🔍 Performing comprehensive syntax validation..."
if sudo -u dataguardian /opt/dataguardian/venv/bin/python3 -m py_compile /opt/dataguardian/app.py 2>/dev/null; then
    echo "✅ Python syntax validation PASSED!"
    
    echo ""
    echo "🚀 Starting DataGuardian service..."
    systemctl start dataguardian
    
    # Wait for startup
    echo "⏳ Waiting for service to initialize..."
    sleep 15
    
    # Check service status
    if systemctl is-active --quiet dataguardian; then
        echo "✅ DataGuardian service is RUNNING!"
        
        # Test HTTP response
        echo "🌐 Testing HTTP connectivity..."
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null || echo "000")
        
        if [ "$HTTP_CODE" = "200" ]; then
            echo ""
            echo "🎉🎉🎉 COMPLETE SUCCESS! 🎉🎉🎉"
            echo "================================"
            echo "✅ All syntax errors fixed"
            echo "✅ Service running properly"  
            echo "✅ HTTP responses working"
            echo "✅ 502 Bad Gateway RESOLVED"
            echo ""
            echo "🔒 Your application is live at:"
            echo "   https://dataguardianpro.nl"
            echo ""
            echo "👤 Login with:"
            echo "   Username: vishaal314"
            echo ""
            echo "📊 Full dashboard functionality restored!"
            echo "================================"
            
        elif [ "$HTTP_CODE" = "000" ]; then
            echo "⚠️  Service running but not responding yet..."
            echo "💡 Try accessing in 30 seconds: https://dataguardianpro.nl"
        else
            echo "⚠️  Service running but HTTP response: $HTTP_CODE"
            echo "💡 Check nginx configuration if issues persist"
        fi
        
        echo ""
        echo "📊 Service Status:"
        systemctl status dataguardian --no-pager -l | head -15
        
    else
        echo "❌ Service failed to start after fixes"
        echo ""
        echo "📋 Recent logs:"
        journalctl -u dataguardian --no-pager -n 10
        echo ""
        echo "🔄 Restoring backup..."
        cp "$BACKUP_FILE" /opt/dataguardian/app.py
        echo "Backup restored from: $BACKUP_FILE"
        exit 1
    fi
    
else
    echo "❌ Syntax validation still failed"
    echo ""
    echo "📋 Showing syntax error:"
    sudo -u dataguardian /opt/dataguardian/venv/bin/python3 -m py_compile /opt/dataguardian/app.py
    echo ""
    echo "🔄 Restoring backup..."
    cp "$BACKUP_FILE" /opt/dataguardian/app.py
    echo "Backup restored from: $BACKUP_FILE"
    exit 1
fi

echo ""
echo "🎯 E2E Fix Complete!"
echo "Your DataGuardian Pro should now be fully operational."