#!/bin/bash
# Check HTTPS/Nginx Status

echo "🔍 CHECKING HTTPS/NGINX STATUS"
echo "=============================="
echo ""

echo "Test 1: Is Nginx Running?"
echo "======================="
systemctl is-active nginx && echo "✅ Nginx running" || echo "❌ Nginx stopped"

echo ""
echo "Test 2: What Ports is Nginx Listening On?"
echo "======================================"
netstat -tlnp | grep nginx

echo ""
echo "Test 3: Nginx Config for dataguardianpro.nl"
echo "======================================="
cat /etc/nginx/sites-available/dataguardianpro.nl | head -30

echo ""
echo "Test 4: Is SSL Configured?"
echo "======================="
grep -i "ssl" /etc/nginx/sites-available/dataguardianpro.nl | head -10

echo ""
echo "Test 5: Firewall Status"
echo "==================="
if command -v ufw &> /dev/null; then
    ufw status | grep -E "443|80"
else
    echo "UFW not installed"
fi

echo ""
echo "Test 6: Try HTTPS Connection"
echo "========================"
curl -k -I https://dataguardianpro.nl 2>&1 | head -10

echo ""
echo "Test 7: Try HTTP Connection"  
echo "======================="
curl -I http://dataguardianpro.nl 2>&1 | head -10
