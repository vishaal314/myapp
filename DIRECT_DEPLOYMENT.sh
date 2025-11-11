#!/bin/bash

# Direct Deployment Script - Bypass Browser Download
# Transfers patch directly from Replit to production server

set -e

echo "=============================================="
echo "DataGuardian Pro - Direct Deployment"
echo "=============================================="
echo ""

PATCH_FILE="dataguardian_patch_nov2025_20251111_221928.tar.gz"
SERVER="root@dataguardianpro.nl"
REMOTE_PATH="/tmp"
INSTALL_PATH="/opt/dataguardian"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if patch file exists
if [ ! -f "$PATCH_FILE" ]; then
    echo -e "${RED}[ERROR]${NC} Patch file not found: $PATCH_FILE"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Patch file found: $PATCH_FILE ($(du -h $PATCH_FILE | cut -f1))"
echo ""

# STEP 1: Transfer patch to server
echo -e "${YELLOW}[STEP 1]${NC} Transferring patch to server..."
echo "Command: scp $PATCH_FILE $SERVER:$REMOTE_PATH/"
echo ""
echo "This will transfer directly from Replit to your server (no browser download needed)"
echo ""

scp -o StrictHostKeyChecking=no $PATCH_FILE $SERVER:$REMOTE_PATH/

if [ $? -eq 0 ]; then
    echo -e "${GREEN}[OK]${NC} Patch transferred successfully!"
else
    echo -e "${RED}[ERROR]${NC} Transfer failed. Check SSH connection."
    exit 1
fi
echo ""

# STEP 2: Verify on server
echo -e "${YELLOW}[STEP 2]${NC} Verifying patch on server..."
REMOTE_SIZE=$(ssh $SERVER "ls -lh $REMOTE_PATH/$PATCH_FILE 2>/dev/null | awk '{print \$5}'" || echo "NOT_FOUND")

if [ "$REMOTE_SIZE" = "NOT_FOUND" ]; then
    echo -e "${RED}[ERROR]${NC} Patch not found on server!"
    exit 1
elif [ "$REMOTE_SIZE" = "0" ]; then
    echo -e "${RED}[ERROR]${NC} Patch transferred but is 0 bytes!"
    exit 1
else
    echo -e "${GREEN}[OK]${NC} Patch verified on server: $REMOTE_SIZE"
fi
echo ""

# STEP 3: Extract patch
echo -e "${YELLOW}[STEP 3]${NC} Extracting patch on server..."
ssh $SERVER "cd $REMOTE_PATH && tar -xzf $PATCH_FILE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}[OK]${NC} Patch extracted successfully!"
else
    echo -e "${RED}[ERROR]${NC} Extraction failed!"
    exit 1
fi
echo ""

# STEP 4: Get user confirmation before applying
echo -e "${YELLOW}[STEP 4]${NC} Ready to apply patch to $INSTALL_PATH"
echo ""
echo "This will:"
echo "  1. Stop services (~10 seconds)"
echo "  2. Apply patch files (~20 seconds)"
echo "  3. Add DISABLE_RLS=true to .env"
echo "  4. Rebuild Docker with --no-cache (~2-5 minutes)"
echo "  5. Start services (~30 seconds)"
echo ""
echo "Total downtime: ~3-6 minutes"
echo "No backup will be created (per your request)"
echo ""
read -p "Continue with deployment? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${YELLOW}[CANCELLED]${NC} Deployment cancelled by user"
    exit 0
fi
echo ""

# STEP 5: Apply patch
echo -e "${YELLOW}[STEP 5]${NC} Applying patch..."
PATCH_DIR="${PATCH_FILE%.tar.gz}"
ssh $SERVER "cd $REMOTE_PATH/$PATCH_DIR && bash deploy_patch_nov2025.sh apply $INSTALL_PATH"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=============================================="
    echo -e "✅ DEPLOYMENT COMPLETED SUCCESSFULLY! 🎉"
    echo -e "==============================================${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Visit https://dataguardianpro.nl"
    echo "  2. Test Database Scanner (PostgreSQL, MySQL, SQL Server)"
    echo "  3. Test Enterprise Scanner (M365, Google, Exact Online)"
    echo "  4. Switch to Dutch language (🇬🇧 → 🇳🇱)"
    echo "  5. Check Dashboard for scan activity"
    echo ""
else
    echo -e "${RED}[ERROR]${NC} Deployment failed! Check logs above."
    exit 1
fi
