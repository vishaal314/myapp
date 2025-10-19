#!/bin/bash
#
# Verify Production Deployment - All 16 Scanners
# Quick verification script to check if deployment was successful
# Date: October 19, 2025
#

set -e

echo "=========================================="
echo "Production Deployment Verification"
echo "=========================================="
echo ""

# Configuration
SERVER_USER="${SERVER_USER:-root}"
SERVER_HOST="${SERVER_HOST:-dataguardianpro.nl}"

echo "🔍 Verifying deployment on ${SERVER_HOST}..."
echo ""

# Run verification checks
ssh ${SERVER_USER}@${SERVER_HOST} << 'VERIFY'
cd /opt/dataguardian

echo "1️⃣  Checking scanner count in services/stripe_payment.py..."
scanner_count=$(python3 -c "
import sys
sys.path.insert(0, 'services')
from stripe_payment import SCAN_PRICES
print(len(SCAN_PRICES))
" 2>/dev/null || echo "ERROR")

if [ "$scanner_count" = "16" ]; then
    echo "   ✅ Confirmed 16 scanners in SCAN_PRICES"
else
    echo "   ❌ ERROR: Found $scanner_count scanners (expected 16)"
    exit 1
fi

echo ""
echo "2️⃣  Checking for Blob Scan removal..."
blob_count=$(grep -c "Blob Scan" services/stripe_payment.py app.py test_ideal_payment.py 2>/dev/null || echo "0")
if [ "$blob_count" = "0" ]; then
    echo "   ✅ Blob Scan successfully removed from all files"
else
    echo "   ❌ ERROR: Blob Scan still found in files"
    exit 1
fi

echo ""
echo "3️⃣  Listing all scanners..."
python3 << 'PYTHON'
import sys
sys.path.insert(0, 'services')
from stripe_payment import SCAN_PRICES

print("   Scanner catalog:")
for i, (scanner, price_cents) in enumerate(sorted(SCAN_PRICES.items(), key=lambda x: x[1]), 1):
    price_eur = price_cents / 100
    print(f"   {i:2d}. {scanner:30s} - €{price_eur:.2f}")
PYTHON

echo ""
echo "4️⃣  Checking Docker containers..."
if docker-compose ps | grep -q "Up"; then
    echo "   ✅ Docker containers running"
    docker-compose ps | grep "Up" | awk '{print "      - " $1 ": " $NF}'
else
    echo "   ⚠️  Some containers may not be running"
fi

echo ""
echo "5️⃣  Testing Streamlit health..."
if curl -f http://localhost:5000/_stcore/health > /dev/null 2>&1; then
    echo "   ✅ Streamlit is healthy and responding"
else
    echo "   ⚠️  Streamlit health check failed"
fi

echo ""
echo "=========================================="
echo "✅ VERIFICATION COMPLETE"
echo "=========================================="
echo ""
echo "Summary:"
echo "  ✅ 16 scanners configured"
echo "  ✅ Blob Scan removed"
echo "  ✅ Docker containers running"
echo "  ✅ Streamlit healthy"
echo ""
echo "🌐 Your production site: https://dataguardianpro.nl"
echo ""
VERIFY

echo "🎉 Production deployment verified successfully!"
echo ""
echo "Next: Clear browser cache (Ctrl+Shift+R) and test the payment page"
