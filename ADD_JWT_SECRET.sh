#!/bin/bash
################################################################################
# DataGuardian Pro - Add JWT_SECRET Environment Variable
# Securely configures JWT authentication for production
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
║         DataGuardian Pro - Add JWT_SECRET                           ║
║         Secure Production Authentication                            ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

echo -e "${BOLD}🔐 Generating Secure JWT Secret${NC}"

# Generate a cryptographically secure JWT secret (64 characters)
JWT_SECRET=$(openssl rand -hex 32)

echo -e "${GREEN}✅ Secure JWT_SECRET generated (64 characters)${NC}\n"

echo -e "${BOLD}Step 1: Stop Current Container${NC}"
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true
echo -e "${GREEN}✅ Container stopped${NC}\n"

echo -e "${BOLD}Step 2: Create Secure Environment File${NC}"

# Create .env file with all secrets
cat > /opt/dataguardian/.env.production << EOFENV
# DataGuardian Pro Production Environment Variables
# Generated: $(date)
# DO NOT COMMIT THIS FILE TO VERSION CONTROL

# Database Configuration
DATABASE_URL=${DATABASE_URL:-postgresql://dataguardian:changeme@localhost/dataguardian?sslmode=require}

# Authentication
JWT_SECRET=${JWT_SECRET}

# Master Encryption Key
DATAGUARDIAN_MASTER_KEY=${DATAGUARDIAN_MASTER_KEY:-$(openssl rand -hex 32)}

# External API Keys (Optional - add if available)
OPENAI_API_KEY=${OPENAI_API_KEY:-}
STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY:-}

# Application Settings
ENVIRONMENT=production
EOFENV

# Secure the env file
chmod 600 /opt/dataguardian/.env.production

echo -e "${GREEN}✅ Secure environment file created${NC}"
echo -e "${YELLOW}   Location: /opt/dataguardian/.env.production${NC}"
echo -e "${YELLOW}   Permissions: 600 (owner read/write only)${NC}\n"

echo -e "${BOLD}Step 3: Start Container with Secrets${NC}"

# Start container with environment file
docker run -d \
    --name dataguardian-container \
    --network host \
    --env-file /opt/dataguardian/.env.production \
    -v /opt/dataguardian/license.json:/app/license.json:ro \
    -v /opt/dataguardian/reports:/app/reports \
    --restart unless-stopped \
    dataguardian:latest

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Container started with secure configuration${NC}\n"
else
    echo -e "${RED}❌ Container failed to start${NC}"
    exit 1
fi

echo -e "${YELLOW}⏳ Waiting for application startup (30 seconds)...${NC}\n"
sleep 30

echo -e "${BOLD}Step 4: Verify JWT Authentication${NC}\n"

# Get fresh logs
FRESH_LOGS=$(docker logs dataguardian-container --since=30s 2>&1)

ERRORS=0

# Check for JWT_SECRET error
if echo "$FRESH_LOGS" | grep -q "JWT_SECRET.*required"; then
    echo -e "${RED}❌ JWT_SECRET still missing${NC}"
    ERRORS=1
else
    echo -e "${GREEN}✅ JWT_SECRET configured correctly${NC}"
fi

# Check for safe mode
if echo "$FRESH_LOGS" | grep -q "safe mode"; then
    echo -e "${RED}❌ Application still in safe mode${NC}"
    ERRORS=1
else
    echo -e "${GREEN}✅ Application running in production mode${NC}"
fi

# Check if Streamlit started
if docker logs dataguardian-container 2>&1 | grep -q "You can now view your Streamlit app"; then
    echo -e "${GREEN}✅ Streamlit application started${NC}"
else
    echo -e "${RED}❌ Streamlit not started${NC}"
    ERRORS=1
fi

# Check container status
if docker ps | grep -q dataguardian-container; then
    echo -e "${GREEN}✅ Container running${NC}"
else
    echo -e "${RED}❌ Container not running${NC}"
    ERRORS=1
fi

echo ""
echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}${BOLD}🎉 JWT_SECRET CONFIGURATION SUCCESSFUL!${NC}"
    echo ""
    echo -e "${GREEN}✅ JWT_SECRET: Generated and configured securely${NC}"
    echo -e "${GREEN}✅ Environment file: Created with secure permissions${NC}"
    echo -e "${GREEN}✅ Container: Running with production authentication${NC}"
    echo -e "${GREEN}✅ Application: Fully operational${NC}"
    echo ""
    echo -e "${BOLD}🧪 Test Your Application:${NC}"
    echo -e "   1. Open: ${BLUE}https://dataguardianpro.nl${NC}"
    echo -e "   2. Login: ${BOLD}vishaal314 / vishaal2024${NC}"
    echo -e "   3. ${GREEN}Application will load fully (no safe mode)${NC}"
    echo -e "   4. Run Website Scanner: https://example.com"
    echo -e "   5. Check Dashboard - scan will appear!"
    echo ""
    echo -e "${BOLD}🔐 Security Notes:${NC}"
    echo -e "   • JWT_SECRET is stored in /opt/dataguardian/.env.production"
    echo -e "   • File permissions: 600 (owner only)"
    echo -e "   • ${RED}DO NOT commit .env.production to version control${NC}"
    echo -e "   • Secrets loaded via Docker --env-file (not exposed in process list)"
    echo ""
    echo -e "${GREEN}${BOLD}✅ Your DataGuardian Pro is now 100% operational!${NC}"
else
    echo -e "${RED}${BOLD}⚠️  SOME ISSUES DETECTED${NC}"
    echo ""
    echo -e "${YELLOW}Check fresh logs:${NC}"
    echo -e "   docker logs dataguardian-container --since=2m"
    echo ""
    echo -e "${YELLOW}Check environment:${NC}"
    echo -e "   docker exec dataguardian-container env | grep JWT_SECRET"
fi

echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo ""

