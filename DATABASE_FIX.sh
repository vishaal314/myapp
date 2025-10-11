#!/bin/bash
################################################################################
# DataGuardian Pro - Complete Database Fix for External Server
# Fixes: Results, History, Scanner Logs persistence
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
║      DataGuardian Pro - DATABASE PERSISTENCE FIX                    ║
║      Fixes: Results, History, Scanner Logs Empty Issue             ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

echo -e "${RED}Critical Issues Fixed:${NC}"
echo -e "   1. ❌ Transaction abort in results_aggregator.py (organization_id column)"
echo -e "   2. ❌ Database tables not created properly"
echo -e "   3. ❌ Falling back to file-based storage (data not persisting)"
echo -e "   4. ❌ Results, History, Scanner Logs sections empty"
echo -e "   ${GREEN}✅ Solution: Fixed transaction handling + proper database init${NC}"
echo ""

echo -e "${BOLD}Step 1: Verify Database Configuration${NC}"

# Check if .env.production exists
if [ ! -f /opt/dataguardian/.env.production ]; then
    echo -e "${RED}❌ .env.production not found${NC}"
    exit 1
fi

# Check DATABASE_URL
if grep -q "DATABASE_URL=" /opt/dataguardian/.env.production; then
    echo -e "${GREEN}✅ DATABASE_URL configured${NC}"
    
    # Extract and validate DATABASE_URL (without exposing it)
    if grep "DATABASE_URL=" /opt/dataguardian/.env.production | grep -q "postgresql://"; then
        echo -e "${GREEN}✅ DATABASE_URL format valid (PostgreSQL)${NC}"
    else
        echo -e "${RED}❌ DATABASE_URL format invalid${NC}"
        echo -e "${YELLOW}Format should be: postgresql://user:password@host:port/database${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ DATABASE_URL not set in .env.production${NC}"
    echo ""
    echo -e "${YELLOW}Add DATABASE_URL to /opt/dataguardian/.env.production:${NC}"
    echo -e "DATABASE_URL=postgresql://user:password@localhost:5432/dataguardian"
    exit 1
fi

echo ""
echo -e "${BOLD}Step 2: Remove Old Container${NC}"
docker rm -f dataguardian-container 2>/dev/null || true
echo -e "${GREEN}✅ Old container removed${NC}"

echo ""
echo -e "${BOLD}Step 3: Rebuild Docker Image with Database Fix${NC}"
cd /opt/dataguardian
docker build -t dataguardian:latest . 2>&1 | tail -30

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image rebuilt successfully${NC}"
else
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

echo ""
echo -e "${BOLD}Step 4: Start Container with Fixed Database${NC}"

docker run -d \
    --name dataguardian-container \
    --network host \
    --env-file /opt/dataguardian/.env.production \
    -v /opt/dataguardian/license.json:/app/license.json:ro \
    -v /opt/dataguardian/reports:/app/reports \
    --restart unless-stopped \
    dataguardian:latest

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Container started successfully${NC}"
else
    echo -e "${RED}❌ Container failed to start${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}⏳ Waiting for database initialization (45 seconds)...${NC}"
sleep 45

echo ""
echo -e "${BOLD}Step 5: Verify Database Fix${NC}"
echo ""

# Get full container logs to ensure we catch all startup messages
# (not --since=40s which would miss the beginning)
LOGS=$(docker logs dataguardian-container 2>&1)

ERRORS=0

# Check for transaction abort errors
if echo "$LOGS" | grep -q "current transaction is aborted"; then
    echo -e "${RED}❌ Transaction abort error still present${NC}"
    ERRORS=1
else
    echo -e "${GREEN}✅ No transaction abort errors${NC}"
fi

# Check for file storage fallback
if echo "$LOGS" | grep -q "falling back to file-based storage"; then
    echo -e "${RED}❌ Still falling back to file storage${NC}"
    ERRORS=1
else
    echo -e "${GREEN}✅ Using database storage (not file-based)${NC}"
fi

# Check for database initialization success
if echo "$LOGS" | grep -q "ResultsAggregator initialized with enterprise security"; then
    echo -e "${GREEN}✅ Database initialized successfully${NC}"
else
    echo -e "${RED}❌ Database initialization may have failed${NC}"
    ERRORS=1
fi

# Check for migration errors
if echo "$LOGS" | grep -q "Migration note: organization_id column already exists"; then
    echo -e "${GREEN}✅ Migration handled correctly (column exists check working)${NC}"
elif echo "$LOGS" | grep -q "Added organization_id column"; then
    echo -e "${GREEN}✅ Migration successful (column added)${NC}"
else
    echo -e "${YELLOW}⚠️  Migration status unclear (check logs)${NC}"
fi

# Check container health
if docker ps | grep -q dataguardian-container; then
    echo -e "${GREEN}✅ Container running${NC}"
else
    echo -e "${RED}❌ Container not running${NC}"
    ERRORS=1
fi

# Check Streamlit startup
if echo "$LOGS" | grep -q "You can now view your Streamlit app"; then
    echo -e "${GREEN}✅ Streamlit started${NC}"
else
    echo -e "${RED}❌ Streamlit not started${NC}"
    ERRORS=1
fi

echo ""
echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}${BOLD}🎉 DATABASE FIX SUCCESSFUL!${NC}"
    echo ""
    echo -e "${GREEN}✅ Transaction abort: FIXED${NC}"
    echo -e "${GREEN}✅ Database initialization: Working${NC}"
    echo -e "${GREEN}✅ Data persistence: Enabled${NC}"
    echo -e "${GREEN}✅ Results section: Should populate${NC}"
    echo -e "${GREEN}✅ History section: Should populate${NC}"
    echo -e "${GREEN}✅ Scanner Logs: Should populate${NC}"
    echo ""
    echo -e "${BOLD}🧪 Test Now:${NC}"
    echo -e "   1. Open: ${BLUE}https://dataguardianpro.nl${NC}"
    echo -e "   2. Login with your credentials"
    echo -e "   3. Navigate to: ${BOLD}Code Scanner${NC}"
    echo -e "   4. Upload a file (e.g., test.py with email addresses)"
    echo -e "   5. Run scan"
    echo -e "   6. ${GREEN}Check Results tab (should show scan data!)${NC}"
    echo -e "   7. ${GREEN}Check History tab (should show scan in list!)${NC}"
    echo -e "   8. ${GREEN}Check Scanner Logs (should show activity!)${NC}"
    echo -e "   9. ${GREEN}Dashboard should show metrics!${NC}"
    echo ""
    echo -e "${GREEN}${BOLD}✅ All data persistence issues are now FIXED!${NC}"
else
    echo -e "${RED}${BOLD}⚠️  SOME ISSUES REMAIN${NC}"
    echo ""
    echo -e "${YELLOW}Recent logs (last 50 lines):${NC}"
    docker logs dataguardian-container 2>&1 | tail -50
    echo ""
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo -e "1. Check DATABASE_URL format in .env.production"
    echo -e "2. Verify PostgreSQL is running: systemctl status postgresql"
    echo -e "3. Test database connection: psql \$DATABASE_URL -c 'SELECT 1'"
    echo -e "4. Check full logs: docker logs dataguardian-container"
fi

echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"

