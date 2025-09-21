#!/bin/bash
# Test DataGuardian Access

echo "🌐 Testing DataGuardian Pro Access..."

echo "1. Testing local access:"
curl -s -o /dev/null -w "Local (localhost:5000): HTTP %{http_code} - %{time_total}s\n" http://localhost:5000

echo "2. Testing domain access:"
curl -s -o /dev/null -w "Domain (dataguardianpro.nl:5000): HTTP %{http_code} - %{time_total}s\n" http://dataguardianpro.nl:5000

echo "3. Service status:"
systemctl is-active dataguardian

echo "4. Port check:"
netstat -tlnp | grep :5000

echo ""
echo "✅ If you see HTTP 200, your app is working!"
echo "🌐 Access at: http://dataguardianpro.nl:5000"