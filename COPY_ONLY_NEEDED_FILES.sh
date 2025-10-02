#!/bin/bash
# COPY ONLY SCANNER FILES - Targeted fix for scanner errors
# Run this ON the external server after uploading specific files

set -e

echo "📋 EXACT FILES NEEDED TO FIX SCANNERS"
echo "======================================"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "❌ Run as root: sudo ./COPY_ONLY_NEEDED_FILES.sh"
    exit 1
fi

echo "CRITICAL FILES TO COPY:"
echo "======================"
echo ""
echo "1️⃣  app.py (575KB) - Main application with scanner UI"
echo "2️⃣  services/code_scanner.py (81KB) - Code Scanner logic"
echo "3️⃣  services/intelligent_repo_scanner.py (38KB) - Repository scanning"
echo ""
echo "OPTIONAL (if other scanners have issues):"
echo "4️⃣  services/repo_scanner.py (27KB)"
echo "5️⃣  services/enhanced_repo_scanner.py (57KB)"
echo "6️⃣  services/parallel_repo_scanner.py (37KB)"
echo "7️⃣  services/enterprise_repo_scanner.py (27KB)"
echo ""
echo "RECOMMENDED: Copy all scanner files for complete fix:"
echo "8️⃣  services/*scanner*.py (all 29 scanner files)"
echo ""
echo "=========================================="
echo "UPLOAD INSTRUCTIONS"
echo "=========================================="
echo ""
echo "From Replit, download ONLY these files:"
echo ""
echo "📥 METHOD 1 - Manual download (in Replit):"
echo "   1. Right-click app.py → Download"
echo "   2. Right-click services/code_scanner.py → Download"
echo "   3. Right-click services/intelligent_repo_scanner.py → Download"
echo ""
echo "📥 METHOD 2 - Download full project, then extract:"
echo "   1. Download Replit as zip"
echo "   2. Extract and keep only:"
echo "      - app.py"
echo "      - services/code_scanner.py"
echo "      - services/intelligent_repo_scanner.py"
echo ""
echo "Then upload to server:"
echo ""
echo "   scp app.py root@dataguardianpro.nl:/tmp/"
echo "   scp services/code_scanner.py root@dataguardianpro.nl:/tmp/"
echo "   scp services/intelligent_repo_scanner.py root@dataguardianpro.nl:/tmp/"
echo ""
echo "Or all scanners at once:"
echo ""
echo "   scp app.py root@dataguardianpro.nl:/tmp/"
echo "   scp -r services root@dataguardianpro.nl:/tmp/"
echo ""

# Check if files are uploaded
if [ ! -f "/tmp/app.py" ]; then
    echo "❌ Files not uploaded yet"
    echo ""
    read -p "Press Enter after uploading files to /tmp/..."
fi

if [ ! -f "/tmp/app.py" ]; then
    echo "❌ /tmp/app.py still not found!"
    echo "Please upload the files first."
    exit 1
fi

echo ""
echo "=========================================="
echo "APPLYING FIX"
echo "=========================================="
echo ""

echo "Step 1: Backup current files"
echo "=========================="
cd /opt/dataguardian
backup_file="/root/scanner_fix_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf "$backup_file" app.py services/*scanner*.py 2>/dev/null
echo "✅ Backup: $backup_file"

echo ""
echo "Step 2: Copy new files"
echo "===================="
cp /tmp/app.py /opt/dataguardian/app.py
echo "✅ Copied app.py"

if [ -d "/tmp/services" ]; then
    cp /tmp/services/*scanner*.py /opt/dataguardian/services/
    echo "✅ Copied all scanner files"
elif [ -f "/tmp/code_scanner.py" ]; then
    cp /tmp/code_scanner.py /opt/dataguardian/services/
    cp /tmp/intelligent_repo_scanner.py /opt/dataguardian/services/ 2>/dev/null || true
    echo "✅ Copied scanner files"
fi

echo ""
echo "Step 3: Rebuild Docker container"
echo "=============================="
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true

echo "Building..."
docker build -t dataguardian-pro /opt/dataguardian 2>&1 | tail -15

docker run -d \
    --name dataguardian-container \
    --restart always \
    -p 5000:5000 \
    -e PYTHONUNBUFFERED=1 \
    dataguardian-pro

echo "✅ Container started"

echo ""
echo "Step 4: Wait for initialization (30 seconds)"
echo "========================================"
for i in {1..30}; do
    if [ $((i % 5)) -eq 0 ]; then
        echo -n " $i"
    else
        echo -n "."
    fi
    sleep 1
done
echo ""

echo ""
echo "Step 5: Verify"
echo "============"
docker ps | grep dataguardian && echo "✅ Running" || echo "❌ Not running"

echo ""
echo "Testing..."
if curl -s http://localhost:5000 | grep -qi "dataguardian"; then
    echo "✅ DataGuardian loaded"
fi

echo ""
echo "Recent logs:"
docker logs dataguardian-container 2>&1 | tail -20

echo ""
echo "Clean up:"
rm -f /tmp/app.py /tmp/*scanner*.py 2>/dev/null
rm -rf /tmp/services 2>/dev/null
echo "✅ Temp files removed"

echo ""
echo "=========================================="
echo "🎉 TARGETED FIX COMPLETE!"
echo "=========================================="
echo ""
echo "✅ Only scanner files updated"
echo "✅ Minimal changes applied"
echo "✅ Docker rebuilt"
echo ""
echo "🌐 Test: https://dataguardianpro.nl"
echo "🧪 Test Code Scanner → Sampling Strategy"
echo ""
echo "Scanners should now work without errors! ✅"

exit 0
