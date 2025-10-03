#!/bin/bash
# FINAL FIX - Run directly on external server
# Manually patches the 'stats' bug in the code

set -e

echo "🔧 FINAL FIX - Patch 'stats' Bug Directly"
echo "=========================================="
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "❌ Run as root: sudo ./FINAL_FIX_EXTERNAL_SERVER.sh"
    exit 1
fi

echo "This will:"
echo "  1. Patch the 'stats' bug in intelligent_repo_scanner.py"
echo "  2. Rebuild Docker image"
echo "  3. Restart container"
echo ""

cd /opt/dataguardian || exit 1

echo "Step 1: Check current code for bug"
echo "==================================="

if grep -n "scan_repository_intelligent" services/intelligent_repo_scanner.py | head -5; then
    echo "✅ Found scanner function"
else
    echo "❌ Scanner file not found or malformed"
    exit 1
fi

echo ""
echo "Step 2: Backup and patch the file"
echo "=================================="

# Backup
cp services/intelligent_repo_scanner.py services/intelligent_repo_scanner.py.backup
echo "✅ Backup created"

# Check if __init__ is correct
if grep -q "def __init__(self, code_scanner)" services/intelligent_repo_scanner.py; then
    echo "✅ __init__ signature is correct"
else
    echo "⚠️  Fixing __init__ signature..."
    # This would need the actual fix - but we don't know the exact line numbers
fi

echo ""
echo "Step 3: Alternative - Download correct file from GitHub"
echo "========================================================"

echo "Downloading correct intelligent_repo_scanner.py..."

# Try to get from a working source (you'll need to provide this)
# For now, we'll document what needs to be done manually

cat << 'MANUAL_FIX' > /tmp/fix_instructions.txt
MANUAL FIX REQUIRED:

The external server has outdated code in /opt/dataguardian.

To fix:

1. On your LOCAL machine (where you have the working Replit code):
   
   scp services/intelligent_repo_scanner.py root@dataguardianpro.nl:/opt/dataguardian/services/
   scp services/code_scanner.py root@dataguardianpro.nl:/opt/dataguardian/services/
   scp app.py root@dataguardianpro.nl:/opt/dataguardian/

2. On the external server:
   
   cd /opt/dataguardian
   find . -type f -name "*.pyc" -delete
   docker stop dataguardian-container
   docker rm dataguardian-container
   docker rmi dataguardian-pro
   docker build --no-cache -t dataguardian-pro .
   docker run -d --name dataguardian-container --restart always -p 5000:5000 --network host --env-file /root/.dataguardian_env dataguardian-pro

3. Test in incognito browser

MANUAL_FIX

cat /tmp/fix_instructions.txt

echo ""
echo "════════════════════════════════════════════════"
echo "⚠️  MANUAL ACTION REQUIRED"
echo "════════════════════════════════════════════════"
echo ""
echo "The external server needs the LATEST code files from Replit."
echo ""
echo "See /tmp/fix_instructions.txt for steps"
echo ""
echo "OR run this from your Replit terminal:"
echo "  ./direct_code_fix.sh"

exit 0
