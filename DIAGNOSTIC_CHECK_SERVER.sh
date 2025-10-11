#!/bin/bash
################################################################################
# Diagnostic - Check what's on the external server
################################################################################

echo "Checking services/results_aggregator.py on server..."
echo ""

TARGET="/opt/dataguardian/services/results_aggregator.py"

if [ ! -f "$TARGET" ]; then
    echo "❌ File not found: $TARGET"
    exit 1
fi

echo "=== Searching for get_recent_scans method ==="
grep -n -A 20 "def get_recent_scans" "$TARGET" | head -30

echo ""
echo "=== Checking method signature specifically ==="
grep -n "def get_recent_scans(" "$TARGET"

echo ""
echo "=== Checking _get_recent_scans_db calls ==="
grep -n "_get_recent_scans_db" "$TARGET"

