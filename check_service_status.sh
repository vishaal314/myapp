#!/bin/bash
# Check DataGuardian Service Status

echo "🔍 Checking DataGuardian Service Status..."
echo "==========================================="

echo "📊 Service Status:"
systemctl status dataguardian --no-pager -l

echo ""
echo "📋 Recent Logs (last 20 lines):"
journalctl -u dataguardian --no-pager -n 20

echo ""
echo "🌐 Port 5000 Status:"
netstat -tlnp | grep :5000 || echo "Port 5000 not listening"

echo ""
echo "🔐 Environment File Check:"
ls -la /opt/dataguardian/.env
echo "Environment file contents (API keys hidden):"
sed 's/API_KEY=.*/API_KEY=***HIDDEN***/' /opt/dataguardian/.env

echo ""
echo "📁 DataGuardian Directory:"
ls -la /opt/dataguardian/