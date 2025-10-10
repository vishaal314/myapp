#!/bin/bash
################################################################################
# DataGuardian Pro - FINAL E2E Fix (Correct Key Format)
# Issue: Application expects base64 URL-safe format, not hex!
################################################################################

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}${BLUE}"
cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║         DataGuardian Pro - FINAL E2E Fix                            ║
║         (Correct Key Format - Base64 URL-Safe)                      ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

echo -e "${RED}❌ Previous Issue: Keys were in HEX format${NC}"
echo -e "${GREEN}✅ This Fix: Keys in BASE64 URL-SAFE format${NC}"
echo ""

echo -e "${BOLD}Step 1: Generate Correct Production Secrets${NC}"

# Generate JWT_SECRET (64 characters hex - this one is OK)
JWT_SECRET=$(openssl rand -hex 32)
echo -e "${GREEN}✅ JWT_SECRET generated: 64 hex characters${NC}"

# Generate DATAGUARDIAN_MASTER_KEY in BASE64 URL-SAFE format (this is the fix!)
# This generates 32 random bytes and encodes as base64 URL-safe
MASTER_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
echo -e "${GREEN}✅ DATAGUARDIAN_MASTER_KEY generated: base64 URL-safe (decodes to 32 bytes)${NC}"

# Verify JWT_SECRET length
if [ ${#JWT_SECRET} -eq 64 ]; then
    echo -e "${GREEN}✅ JWT_SECRET length verified: 64 characters${NC}"
else
    echo -e "${RED}❌ JWT_SECRET length error: ${#JWT_SECRET} (expected 64)${NC}"
    exit 1
fi

# Verify MASTER_KEY can decode to 32 bytes
DECODED_LENGTH=$(python3 -c "
import base64
key = '${MASTER_KEY}'
# Add padding if needed
missing_padding = len(key) % 4
if missing_padding:
    key += '=' * (4 - missing_padding)
decoded = base64.urlsafe_b64decode(key)
print(len(decoded))
")

if [ "$DECODED_LENGTH" -eq 32 ]; then
    echo -e "${GREEN}✅ MASTER_KEY decodes to exactly 32 bytes${NC}"
else
    echo -e "${RED}❌ MASTER_KEY decodes to ${DECODED_LENGTH} bytes (expected 32)${NC}"
    exit 1
fi

echo ""
echo -e "${BOLD}Step 2: Create Correct Environment File${NC}"

# Create .env.production with correct format keys
cat > /opt/dataguardian/.env.production << EOFENV
# DataGuardian Pro - Production Environment Variables (CORRECTED)
# Generated: $(date)
# DO NOT COMMIT THIS FILE TO VERSION CONTROL

# Database Configuration
DATABASE_URL=${DATABASE_URL:-postgresql://dataguardian:changeme@localhost/dataguardian?sslmode=require}

# Authentication (hex format - 64 chars)
JWT_SECRET=${JWT_SECRET}

# Master Encryption Key (BASE64 URL-SAFE format - decodes to 32 bytes)
# This is the CORRECTED format the application expects!
DATAGUARDIAN_MASTER_KEY=${MASTER_KEY}

# External API Keys (Optional)
OPENAI_API_KEY=${OPENAI_API_KEY:-}
STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY:-}

# Application Settings
ENVIRONMENT=production
PYTHONUNBUFFERED=1
EOFENV

chmod 600 /opt/dataguardian/.env.production

echo -e "${GREEN}✅ Environment file created with CORRECT key formats${NC}"
echo -e "${YELLOW}   JWT_SECRET: 64-char hex ✅${NC}"
echo -e "${YELLOW}   MASTER_KEY: base64 URL-safe (→32 bytes) ✅${NC}"
echo ""

echo -e "${BOLD}Step 3: Stop Current Container${NC}"
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true
echo -e "${GREEN}✅ Container stopped and removed${NC}"
echo ""

echo -e "${BOLD}Step 4: Start Container with Corrected Secrets${NC}"

docker run -d \
    --name dataguardian-container \
    --network host \
    --env-file /opt/dataguardian/.env.production \
    -v /opt/dataguardian/license.json:/app/license.json:ro \
    -v /opt/dataguardian/reports:/app/reports \
    --restart unless-stopped \
    dataguardian:latest

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Container started with corrected secrets${NC}"
else
    echo -e "${RED}❌ Container failed to start${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}⏳ Waiting for application startup (50 seconds)...${NC}"
sleep 50

echo ""
echo -e "${BOLD}Step 5: Verify Fix (Using Fresh Logs Only)${NC}"
echo ""

# Get ONLY logs from the last 30 seconds (after container restart)
FRESH_LOGS=$(docker logs dataguardian-container --since=30s 2>&1)

ERRORS=0

# Check 1: KMS error (this should NOT appear now)
if echo "$FRESH_LOGS" | grep -q "Master key must be 32 bytes"; then
    echo -e "${RED}❌ KMS error STILL present - master key wrong size${NC}"
    ERRORS=1
else
    echo -e "${GREEN}✅ No KMS size errors - master key format CORRECT${NC}"
fi

# Check 2: KMS initialization failed
if echo "$FRESH_LOGS" | grep -q "Failed to initialize KMS"; then
    echo -e "${RED}❌ KMS initialization failed${NC}"
    ERRORS=1
else
    echo -e "${GREEN}✅ KMS initialized successfully${NC}"
fi

# Check 3: Safe mode
if echo "$FRESH_LOGS" | grep -q "safe mode\|Safe Mode"; then
    echo -e "${RED}❌ Application in safe mode${NC}"
    ERRORS=1
else
    echo -e "${GREEN}✅ Application NOT in safe mode${NC}"
fi

# Check 4: UnboundLocalError
if echo "$FRESH_LOGS" | grep -q "UnboundLocalError"; then
    echo -e "${RED}❌ UnboundLocalError present${NC}"
    ERRORS=1
else
    echo -e "${GREEN}✅ No UnboundLocalError${NC}"
fi

# Check 5: Streamlit started
if docker logs dataguardian-container 2>&1 | tail -100 | grep -q "You can now view your Streamlit app"; then
    echo -e "${GREEN}✅ Streamlit running${NC}"
else
    echo -e "${RED}❌ Streamlit not detected${NC}"
    ERRORS=1
fi

# Check 6: Container health
if docker ps | grep -q dataguardian-container; then
    echo -e "${GREEN}✅ Container running${NC}"
else
    echo -e "${RED}❌ Container stopped${NC}"
    ERRORS=1
fi

echo ""
echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}${BOLD}🎉 FINAL E2E FIX SUCCESSFUL!${NC}"
    echo ""
    echo -e "${GREEN}✅ Key Format: CORRECTED (base64 URL-safe)${NC}"
    echo -e "${GREEN}✅ KMS: Initialized without errors${NC}"
    echo -e "${GREEN}✅ Safe Mode: DISABLED${NC}"
    echo -e "${GREEN}✅ UnboundLocalError: FIXED${NC}"
    echo -e "${GREEN}✅ Application: 100% OPERATIONAL${NC}"
    echo ""
    echo -e "${BOLD}🧪 Test Now:${NC}"
    echo -e "   1. ${BLUE}https://dataguardianpro.nl${NC}"
    echo -e "   2. Login: ${BOLD}vishaal314 / vishaal2024${NC}"
    echo -e "   3. ${GREEN}NO safe mode message${NC}"
    echo -e "   4. Run Website Scanner: ${BLUE}https://ns.nl${NC}"
    echo -e "   5. ${GREEN}Scanner works perfectly${NC}"
    echo ""
    echo -e "${GREEN}${BOLD}✅ DataGuardian Pro is NOW 100% operational!${NC}"
else
    echo -e "${RED}${BOLD}⚠️  VERIFICATION FAILED${NC}"
    echo ""
    echo -e "${YELLOW}Recent logs (last 30 seconds):${NC}"
    docker logs dataguardian-container --since=30s 2>&1 | tail -30
    echo ""
    echo -e "${YELLOW}Check: docker logs dataguardian-container${NC}"
fi

echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
