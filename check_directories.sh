#!/bin/bash
echo "🔍 CHECKING DATAGUARDIAN DIRECTORY STRUCTURE"
echo "==========================================="
echo ""

cd /opt/dataguardian

echo "📁 TOP-LEVEL DIRECTORIES:"
ls -la | grep "^d" | awk '{print $9}' | grep -v "^\.$\|^\.\.$"

echo ""
echo "📁 CHECKING CRITICAL DIRECTORIES:"
for dir in utils services components scanners config; do
    if [ -d "$dir" ]; then
        count=$(find "$dir" -name "*.py" 2>/dev/null | wc -l)
        echo "   ✅ $dir/ exists ($count Python files)"
    else
        echo "   ❌ $dir/ MISSING"
    fi
done

echo ""
echo "📄 TOTAL PYTHON FILES:"
find . -name "*.py" | wc -l

echo ""
echo "📁 DIRECTORY TREE (first 3 levels):"
find . -maxdepth 3 -type d | head -30

echo ""
echo "✅ DIRECTORY CHECK COMPLETE"
