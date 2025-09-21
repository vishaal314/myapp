#!/bin/bash
# Quick Fix for Syntax Error - DataGuardian Pro

echo "🔧 Fixing syntax error at line 11124..."

# Stop the service
echo "⏹️ Stopping DataGuardian service..."
systemctl stop dataguardian

# Create backup
echo "💾 Creating syntax error backup..."
cp /opt/dataguardian/app.py /opt/dataguardian/app.py.syntax.backup.$(date +%Y%m%d_%H%M%S)

# Fix the syntax error
echo "🔧 Fixing unmatched parenthesis..."

python3 << 'EOF'
# Read the app.py file
with open('/opt/dataguardian/app.py', 'r') as f:
    lines = f.readlines()

# Fix line 11124 specifically - remove the extra closing parenthesis
if len(lines) > 11123:  # Line 11124 is index 11123
    line = lines[11123]
    print(f"Original line 11124: {line.strip()}")
    
    # Fix the unmatched parenthesis by removing extra '))'
    if ')' in line and '))' in line:
        fixed_line = line.replace('))', ')')
        lines[11123] = fixed_line
        print(f"Fixed line 11124: {fixed_line.strip()}")
    
    # Also check nearby lines for similar issues
    for i in range(max(0, 11120), min(len(lines), 11130)):
        if ')' in lines[i] and '))' in lines[i]:
            lines[i] = lines[i].replace('))', ')')
            print(f"Fixed line {i+1}: {lines[i].strip()}")

# Write the fixed content back
with open('/opt/dataguardian/app.py', 'w') as f:
    f.writelines(lines)

print("✅ Syntax error fixed")
EOF

# Check if fix was successful
if [ $? -eq 0 ]; then
    echo "✅ Syntax fix applied"
    
    # Quick syntax check
    echo "🔍 Checking Python syntax..."
    if sudo -u dataguardian /opt/dataguardian/venv/bin/python3 -m py_compile /opt/dataguardian/app.py; then
        echo "✅ Python syntax is now valid"
    else
        echo "❌ Syntax still has issues, restoring backup"
        cp /opt/dataguardian/app.py.syntax.backup.* /opt/dataguardian/app.py 2>/dev/null
        exit 1
    fi
else
    echo "❌ Syntax fix failed"
    exit 1
fi

# Start the service
echo "🚀 Starting DataGuardian service..."
systemctl start dataguardian

# Quick test
sleep 8
if systemctl is-active --quiet dataguardian; then
    echo "✅ Service is running!"
    
    # Test HTTP response
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ SUCCESS! Syntax error fixed and application working!"
        echo ""
        echo "🔒 Access: https://dataguardianpro.nl"
        echo "👤 Login with: vishaal314"
    else
        echo "⚠️  Service running but HTTP response: $HTTP_CODE"
        echo "🔧 Check logs: journalctl -u dataguardian -n 10"
    fi
else
    echo "❌ Service failed to start after syntax fix"
    journalctl -u dataguardian --no-pager -n 10
fi