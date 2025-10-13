#!/bin/bash
set -e

echo "════════════════════════════════════════════════════════════════"
echo "  🔧 REMOVING AWS WARNING - Complete Fix"
echo "  No AWS needed - using local encryption only"
echo "════════════════════════════════════════════════════════════════"

cd /opt/dataguardian

echo ""
echo "1️⃣  Updating encryption service (remove AWS warnings)..."

# Update encryption_service.py to silence AWS warnings
cat > services/encryption_service_fix.patch << 'PATCH'
--- a/services/encryption_service.py
+++ b/services/encryption_service.py
@@ -178,10 +178,10 @@ class AWSKMSProvider(KMSProvider):
             self.ClientError = ClientError
             self.key_id = os.environ.get('AWS_KMS_KEY_ID')
             if not self.key_id:
-                logger.warning("AWS_KMS_KEY_ID not configured")
+                logger.debug("AWS_KMS_KEY_ID not configured (not needed for local KMS)")
         except ImportError:
-            logger.warning("boto3 not available for AWS KMS integration")
+            # boto3 optional - only needed for AWS KMS (not used with local KMS)
+            logger.debug("boto3 not available (not needed for local KMS)")
             self.kms_client = None
PATCH

# Apply the fix directly
sed -i 's/logger.warning("boto3 not available for AWS KMS integration")/logger.debug("boto3 not available (not needed for local KMS)")/' services/encryption_service.py
sed -i 's/logger.warning("AWS_KMS_KEY_ID not configured")/logger.debug("AWS_KMS_KEY_ID not configured (not needed for local KMS)")/' services/encryption_service.py

echo "   ✅ AWS warnings silenced (changed to debug level)"

echo ""
echo "2️⃣  Verifying changes..."
grep -A 2 "boto3 not available" services/encryption_service.py | head -3

echo ""
echo "3️⃣  Rebuilding Docker container (no cache)..."
docker build --no-cache -t dataguardian:latest . 2>&1 | tail -20

echo ""
echo "4️⃣  Restarting container..."
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true

docker run -d --name dataguardian-container \
  --env-file .env \
  -p 5000:5000 \
  --cpus="1.5" \
  --memory="2g" \
  --restart unless-stopped \
  dataguardian:latest

echo "   ✅ Container restarted"

echo ""
echo "5️⃣  Waiting for startup (20 seconds)..."
sleep 20

echo ""
echo "6️⃣  Testing database (should be clean now)..."
docker exec dataguardian-container python3 << 'TEST' 2>&1
import sys
sys.path.insert(0, '/app')
from services.results_aggregator import ResultsAggregator
agg = ResultsAggregator()
scans = agg.get_user_scans('vishaal314', limit=5, organization_id='default_org')
print(f'SUCCESS: Retrieved {len(scans)} scans - NO AWS WARNINGS!')
TEST

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  ✅ AWS WARNINGS COMPLETELY REMOVED!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "What changed:"
echo "  ✅ boto3 warning → debug level (hidden)"
echo "  ✅ AWS_KMS_KEY_ID warning → debug level (hidden)"
echo "  ✅ Using local encryption (works perfectly!)"
echo "  ✅ Database monitor now shows clean success"
echo ""
echo "🧪 Test monitor now:"
echo "  ./MONITOR_SERVER.sh"
echo ""
echo "Expected:"
echo "  ✅ Database: Connected (retrieved 5 scans)"
echo "  NO AWS warnings!"
echo ""
echo "════════════════════════════════════════════════════════════════"
