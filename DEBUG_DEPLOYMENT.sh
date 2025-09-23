#!/bin/bash
# Debug deployment issue - check what's actually being packaged

echo "🔍 DEBUGGING DEPLOYMENT ISSUE"
echo "=============================="

# Check current directory
echo "Current directory: $(pwd)"
echo ""

# Check if critical files exist here
echo "Checking for critical files in current location:"
critical_files=(
    "utils/activity_tracker.py"
    "utils/code_profiler.py"
    "services/license_integration.py"
    "app.py"
)

for file in "${critical_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ Found: $file"
    else
        echo "❌ Missing: $file"
    fi
done
echo ""

# Check what directories exist
echo "Available directories:"
ls -la | grep "^d"
echo ""

# Test tar command
echo "Testing tar archive creation..."
tar --exclude='*.log' \
    --exclude='*.tmp' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='venv' \
    --exclude='*.pyc' \
    -czf /tmp/test_debug.tar.gz . 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Tar creation successful"
    
    echo ""
    echo "Checking archive contents..."
    tar -tzf /tmp/test_debug.tar.gz | grep -E "(utils/activity_tracker|services/license_integration|app\.py)" | head -10
    
    echo ""
    echo "Archive size:"
    ls -lh /tmp/test_debug.tar.gz
    
    echo ""
    echo "Testing extraction..."
    mkdir -p /tmp/test_extract
    cd /tmp/test_extract
    tar -xzf /tmp/test_debug.tar.gz
    
    echo "Checking extracted files:"
    for file in "${critical_files[@]}"; do
        if [ -f "$file" ]; then
            echo "✅ Extracted: $file"
        else
            echo "❌ Missing after extraction: $file"
        fi
    done
    
    # Clean up
    rm -rf /tmp/test_extract /tmp/test_debug.tar.gz
else
    echo "❌ Tar creation failed"
fi