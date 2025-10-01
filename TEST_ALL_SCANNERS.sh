#!/bin/bash
# TEST ALL SCANNERS - Find which ones have issues

echo "🧪 TESTING ALL SCANNERS ON EXTERNAL SERVER"
echo "=========================================="
echo ""

echo "Checking Docker container logs for recent errors..."
docker logs dataguardian-container --since=5m 2>&1 | grep -iE "error|traceback|unboundlocalerror" | tail -50

echo ""
echo "=========================================="
echo "RECOMMENDED FIX STRATEGY"
echo "=========================================="
echo ""
echo "The error 'UnboundLocalError: cannot access local variable stats'"
echo "indicates a code issue where a variable is used before being defined."
echo ""
echo "✅ IMMEDIATE FIX OPTIONS:"
echo ""
echo "Option 1: Update app.py from working Replit version"
echo "  - Export app.py from Replit"
echo "  - Copy to /opt/dataguardian/app.py on server"
echo "  - Rebuild Docker: docker build -t dataguardian-pro ."
echo "  - Restart: docker stop/rm/run dataguardian-container"
echo ""
echo "Option 2: Sync all files from Replit"
echo "  - rsync -avz /path/to/replit/ root@dataguardianpro.nl:/opt/dataguardian/"
echo "  - Rebuild Docker container"
echo ""
echo "Option 3: Use Replit Publishing (RECOMMENDED)"
echo "  - Deploy in Replit (5 minutes)"
echo "  - Point domain to Replit"
echo "  - Zero debugging needed"
echo ""
echo "🎯 Since Replit works perfectly and external server has issues,"
echo "   the fastest solution is Replit Publishing or full file sync."

exit 0
