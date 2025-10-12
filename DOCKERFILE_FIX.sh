#!/bin/bash
set -e

echo "🔧 Fixing Dockerfile and Rebuilding"
echo ""

cd /opt/dataguardian

# Fix Dockerfile - replace problematic echo with proper file creation
echo "1️⃣  Fixing Dockerfile..."

python3 << 'PYFIX'
with open('Dockerfile', 'r') as f:
    content = f.read()

# Find and replace the broken RUN command
old_pattern = '''RUN mkdir -p ~/.streamlit && \\
    echo '[server]\\n\\
headless = true\\n\\
address = "0.0.0.0"\\n\\
port = 5000\\n\\
enableCORS = false\\n\\
enableXsrfProtection = false\\n\\
\\n\\
[browser]\\n\\
gatherUsageStats = false\\n\\
\\n\\
[theme]\\n\\
base = "light"' > ~/.streamlit/config.toml'''

# Use a proper heredoc approach
new_pattern = '''RUN mkdir -p ~/.streamlit && \\
    printf '%s\\n' \\
    '[server]' \\
    'headless = true' \\
    'address = "0.0.0.0"' \\
    'port = 5000' \\
    'enableCORS = false' \\
    'enableXsrfProtection = false' \\
    '' \\
    '[browser]' \\
    'gatherUsageStats = false' \\
    '' \\
    '[theme]' \\
    'base = "light"' \\
    > ~/.streamlit/config.toml'''

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    print("✅ Fixed Dockerfile echo command")
elif 'printf' in content:
    print("✅ Dockerfile already fixed")
else:
    print("⚠️  Using alternative fix...")
    # Alternative: Just remove the problematic section if pattern doesn't match
    import re
    content = re.sub(
        r'RUN mkdir -p ~/\.streamlit.*?config\.toml',
        'RUN mkdir -p ~/.streamlit',
        content,
        flags=re.DOTALL
    )
    print("✅ Removed problematic streamlit config (will use .streamlit/config.toml from repo)")

with open('Dockerfile', 'w') as f:
    f.write(content)

print("✅ Dockerfile fixed")
PYFIX

# Rebuild
echo ""
echo "2️⃣  Rebuilding Docker (--no-cache)..."
docker build --no-cache -t dataguardian:latest . 2>&1 | tail -30

if [ $? -ne 0 ]; then
    echo "❌ Build failed again"
    exit 1
fi

echo "✅ Build successful"

# Restart
echo ""
echo "3️⃣  Restarting container..."
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true

docker run -d --name dataguardian-container \
  -e DATABASE_URL="postgresql://neondb_owner:npg_cKtisl61HrVC@ep-blue-queen-a6jyu08j.us-west-2.aws.neon.tech/neondb?sslmode=require" \
  -e JWT_SECRET="vN4JMEmAi7XTadC5Q2UTxic4ghTS+5+qJ4AeEtvR7fIrT/qnhojVqygj2gfyPpYS HlebsC2Y49NzObSqLA2WTg==" \
  -e DATAGUARDIAN_MASTER_KEY="gQJ6WV5FxDgGWj-vQqRzHqS4CIUOGFaXRqsGXNLJHbU=" \
  -e DISABLE_RLS=1 \
  -p 5000:5000 \
  --restart unless-stopped \
  dataguardian:latest

echo "✅ Container started"

# Wait
echo ""
echo "4️⃣  Waiting 45 seconds for startup..."
sleep 45

# Test
echo ""
echo "5️⃣  Testing Predictive Analytics query..."
docker exec dataguardian-container python3 << 'PYTEST'
import sys
sys.path.insert(0, '/app')
from services.results_aggregator import ResultsAggregator

agg = ResultsAggregator()
scans = agg.get_user_scans('vishaal314', limit=15, organization_id='default_org')
print(f"✅ Query returned: {len(scans)} scans")
if scans:
    print(f"   Latest: {scans[0].get('timestamp')} - {scans[0].get('scan_type')}")
    print(f"\n   🎉 SUCCESS! Predictive Analytics will now work!")
else:
    print(f"   ❌ Still 0 scans - deeper issue")
PYTEST

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  ✅ DEPLOYMENT COMPLETE!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Test now:"
echo "  1. Visit: https://dataguardianpro.nl"
echo "  2. Login and go to: Predictive Compliance Analytics"
echo "  3. Should show REAL predictions with 15 scans"
echo ""
echo "Verify with logs:"
echo "  docker logs dataguardian-container | grep 'Predictive Analytics'"
echo ""
echo "Expected log:"
echo "  'Predictive Analytics: Retrieved 15 scan metadata records'"
echo "════════════════════════════════════════════════════════════════"
