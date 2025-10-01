#!/bin/bash
# INSTALL MISSING PACKAGES - Final fix

set -e

echo "📦 INSTALLING MISSING PYTHON PACKAGES"
echo "====================================="
echo ""

# Update Dockerfile to include missing packages
cd /opt/dataguardian

echo "Adding psutil and authlib to Dockerfile..."

# Check if already added
if grep -q "psutil" Dockerfile; then
    echo "✅ Already in Dockerfile"
else
    # Add to pip install line
    sed -i 's/python-dotenv/python-dotenv \\\n    psutil \\\n    authlib/g' Dockerfile
    echo "✅ Added to Dockerfile"
fi

echo ""
echo "🐳 Rebuilding container with missing packages..."
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true

docker build -t dataguardian-pro . 2>&1 | tail -20

docker run -d \
    --name dataguardian-container \
    --restart always \
    -p 5000:5000 \
    -e PYTHONUNBUFFERED=1 \
    dataguardian-pro

echo "✅ Container restarted"

echo ""
echo "⏳ Waiting 45 seconds for initialization..."
sleep 45

echo ""
echo "🧪 FINAL TEST"
echo "============"

if curl -s http://localhost:5000 | grep -qi "dataguardian"; then
    echo "✅✅✅ SUCCESS! DataGuardian Pro is LIVE!"
    echo ""
    echo "🌐 Access: https://dataguardianpro.nl"
    echo "🔐 Login: demo / demo123"
else
    echo "Testing..."
    docker logs dataguardian-container 2>&1 | tail -30
fi
