#!/bin/bash
echo "🔍 CHECKING EXTERNAL SERVER LOGS"
echo "==============================="
echo ""

echo "📄 LAST 50 LINES OF DATAGUARDIAN LOGS:"
echo "===================================="
journalctl -u dataguardian -n 50 --no-pager

echo ""
echo "🔍 SEARCH FOR KEY INITIALIZATION MESSAGES:"
echo "======================================"
echo ""
echo "Looking for 'Performance optimizations initialized':"
journalctl -u dataguardian --no-pager | grep -i "performance.*optimiz" | tail -5

echo ""
echo "Looking for 'Successfully initialized translations':"
journalctl -u dataguardian --no-pager | grep -i "translation" | tail -5

echo ""
echo "Looking for 'System monitoring started':"
journalctl -u dataguardian --no-pager | grep -i "system.*monitor" | tail -5

echo ""
echo "Looking for DataGuardian-specific logs:"
journalctl -u dataguardian --no-pager | grep -i "dataguardian" | tail -10

echo ""
echo "🔍 CHECK IF APP.PY IS ACTUALLY EXECUTING:"
echo "====================================="
echo ""
echo "Looking for app.py execution in logs:"
journalctl -u dataguardian -n 100 --no-pager | grep -i "app\.py\|main\|__main__" | tail -10

echo ""
echo "✅ LOG CHECK COMPLETE"
