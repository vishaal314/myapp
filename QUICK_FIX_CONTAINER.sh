#!/bin/bash
set -e

echo "Removing old container..."
docker rm -f dataguardian-container 2>/dev/null || true

echo "Starting new container with fixed code..."
docker run -d \
    --name dataguardian-container \
    --network host \
    --env-file /opt/dataguardian/.env.production \
    -v /opt/dataguardian/license.json:/app/license.json:ro \
    -v /opt/dataguardian/reports:/app/reports \
    --restart unless-stopped \
    dataguardian:latest

echo ""
echo "Waiting 30 seconds for startup..."
sleep 30

echo ""
echo "Checking status..."
if docker ps | grep -q dataguardian-container; then
    echo "✅ Container running"
    echo "✅ Document scanner fix deployed"
    echo ""
    echo "Test at: https://dataguardianpro.nl"
else
    echo "❌ Container not running"
    docker logs dataguardian-container --tail 20
fi
