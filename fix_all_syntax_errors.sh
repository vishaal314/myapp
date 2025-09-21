#!/bin/bash
# Comprehensive Syntax Fix for DataGuardian Pro

echo "🔧 Comprehensive syntax error fix..."

# Stop the service
echo "⏹️ Stopping DataGuardian service..."
systemctl stop dataguardian

# Create backup
echo "💾 Creating comprehensive backup..."
cp /opt/dataguardian/app.py /opt/dataguardian/app.py.comprehensive.backup.$(date +%Y%m%d_%H%M%S)

# Comprehensive Python fix for all syntax errors
echo "🔧 Fixing ALL syntax errors..."

python3 << 'EOF'
import re

# Read the app.py file
with open('/opt/dataguardian/app.py', 'r') as f:
    content = f.read()

print("🔍 Scanning for syntax errors...")

# Track all fixes
fixes_applied = 0

# Fix 1: Find all st.metric calls with extra closing parentheses
def fix_st_metric_extra_parens(text):
    global fixes_applied
    # Pattern: st.metric("anything", "anything"))
    pattern = r'(st\.metric\([^)]+\))\)'
    matches = re.findall(pattern, text)
    if matches:
        print(f"Found {len(matches)} st.metric calls with extra closing parentheses")
        for match in matches:
            print(f"  Fixing: {match})")
        fixes_applied += len(matches)
        text = re.sub(pattern, r'\1', text)
    return text

# Fix 2: Find all st.metric calls missing closing parentheses
def fix_st_metric_missing_parens(text):
    global fixes_applied
    lines = text.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        if 'st.metric(' in line and not line.strip().endswith(')'):
            # Count parentheses
            open_parens = line.count('(')
            close_parens = line.count(')')
            
            if open_parens > close_parens:
                missing = open_parens - close_parens
                print(f"Line {i+1}: Missing {missing} closing parenthesis: {line.strip()}")
                line = line.rstrip() + ')' * missing
                fixes_applied += 1
                print(f"  Fixed to: {line.strip()}")
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

# Fix 3: General unmatched parentheses around st.metric
def fix_general_unmatched_parens(text):
    global fixes_applied
    lines = text.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        if 'st.metric(' in line:
            # Check for double closing parentheses
            if ')' in line and '))' in line:
                original = line
                # More careful replacement - only fix obvious double parentheses at end
                if line.strip().endswith('))'):
                    line = line.rstrip(')') + ')'
                    print(f"Line {i+1}: Fixed double parentheses")
                    print(f"  From: {original.strip()}")
                    print(f"  To:   {line.strip()}")
                    fixes_applied += 1
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

# Apply all fixes
print("\n🔧 Applying Fix 1: Extra closing parentheses...")
content = fix_st_metric_extra_parens(content)

print("\n🔧 Applying Fix 2: Missing closing parentheses...")
content = fix_st_metric_missing_parens(content)

print("\n🔧 Applying Fix 3: General unmatched parentheses...")
content = fix_general_unmatched_parens(content)

# Write the fixed content back
with open('/opt/dataguardian/app.py', 'w') as f:
    f.write(content)

print(f"\n✅ Applied {fixes_applied} syntax fixes")
EOF

# Check if fix was successful
if [ $? -eq 0 ]; then
    echo "✅ Comprehensive syntax fix applied"
    
    # Thorough syntax check
    echo "🔍 Performing thorough Python syntax check..."
    if sudo -u dataguardian /opt/dataguardian/venv/bin/python3 -m py_compile /opt/dataguardian/app.py; then
        echo "✅ Python syntax is now completely valid!"
        
        # Additional syntax verification
        echo "🔍 Double-checking with syntax validation..."
        if sudo -u dataguardian /opt/dataguardian/venv/bin/python3 -c "import ast; ast.parse(open('/opt/dataguardian/app.py').read())" 2>/dev/null; then
            echo "✅ AST parsing successful - syntax is perfect!"
        else
            echo "⚠️  AST parsing failed, but py_compile passed"
        fi
    else
        echo "❌ Syntax still has issues, restoring backup"
        latest_backup=$(ls -t /opt/dataguardian/app.py.*.backup* 2>/dev/null | head -1)
        if [ -n "$latest_backup" ]; then
            cp "$latest_backup" /opt/dataguardian/app.py
            echo "🔄 Restored from: $latest_backup"
        fi
        exit 1
    fi
else
    echo "❌ Comprehensive syntax fix failed"
    exit 1
fi

# Start the service
echo "🚀 Starting DataGuardian service..."
systemctl start dataguardian

# Wait and test
sleep 10
echo "🔍 Testing service status..."

if systemctl is-active --quiet dataguardian; then
    echo "✅ Service is running!"
    
    # Test HTTP response  
    echo "🌐 Testing HTTP response..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ SUCCESS! All syntax errors fixed and application working!"
        echo ""
        echo "🎉 DataGuardian Pro is fully operational!"
        echo "🔒 Access: https://dataguardianpro.nl"  
        echo "👤 Login with: vishaal314"
        echo ""
        echo "✅ Fixed issues:"
        echo "   - Unmatched closing parentheses in st.metric calls"
        echo "   - Missing closing parentheses"
        echo "   - All Python syntax errors resolved"
    else
        echo "⚠️  Service running but HTTP response: $HTTP_CODE"
        echo "🔧 Check logs: journalctl -u dataguardian -n 10"
    fi
else
    echo "❌ Service failed to start after comprehensive fix"
    echo "📋 Service logs:"
    journalctl -u dataguardian --no-pager -n 10
fi