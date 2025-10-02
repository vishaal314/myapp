#!/bin/bash
# CREATE DEPLOYMENT TAR - Run this in Replit to create full deployment package

echo "📦 CREATING FULL DEPLOYMENT TAR"
echo "================================"
echo ""

# Create tar with all necessary files
tar -czf dataguardian_deploy.tar.gz \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    --exclude='node_modules' \
    --exclude='.venv' \
    --exclude='venv' \
    --exclude='*.log' \
    --exclude='*.db' \
    --exclude='*.sqlite' \
    --exclude='scan_checkpoint_*' \
    app.py \
    services/ \
    utils/ \
    translations/ \
    Dockerfile \
    requirements.txt \
    .streamlit/ \
    secure_users.json \
    2>/dev/null

if [ -f "dataguardian_deploy.tar.gz" ]; then
    SIZE=$(du -h dataguardian_deploy.tar.gz | cut -f1)
    echo "✅ Created: dataguardian_deploy.tar.gz ($SIZE)"
    echo ""
    echo "📤 NEXT STEPS:"
    echo "============="
    echo ""
    echo "1. Download this file from Replit:"
    echo "   Right-click dataguardian_deploy.tar.gz → Download"
    echo ""
    echo "2. Upload to your server:"
    echo "   scp dataguardian_deploy.tar.gz root@dataguardianpro.nl:/tmp/"
    echo ""
    echo "3. SSH to server and run fix:"
    echo "   ssh root@dataguardianpro.nl"
    echo "   sudo ./APPLY_TAR_FIX.sh"
    echo ""
    echo "✅ All files included, ready for deployment!"
else
    echo "❌ Failed to create tar file"
    exit 1
fi
