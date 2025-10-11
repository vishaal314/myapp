#!/bin/bash
################################################################################
# DataGuardian Pro - Complete Database Diagnostic & Fix
# Verifies actual database state, not just log messages
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
║      DataGuardian Pro - DATABASE DIAGNOSTIC                         ║
║      Complete verification of database persistence                  ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

# Extract DATABASE_URL from .env.production
if [ -f /opt/dataguardian/.env.production ]; then
    export $(grep DATABASE_URL /opt/dataguardian/.env.production | xargs)
fi

if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}❌ DATABASE_URL not found${NC}"
    exit 1
fi

echo -e "${BOLD}Step 1: Test Database Connection${NC}"

# Test basic connection
if psql "$DATABASE_URL" -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL connection: Working${NC}"
else
    echo -e "${RED}❌ PostgreSQL connection: Failed${NC}"
    echo -e "${YELLOW}Check: systemctl status postgresql${NC}"
    exit 1
fi

echo ""
echo -e "${BOLD}Step 2: Verify Database Tables${NC}"

# Check if critical tables exist
TABLES=$(psql "$DATABASE_URL" -t -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public'" 2>/dev/null || echo "")

if echo "$TABLES" | grep -q "scans"; then
    echo -e "${GREEN}✅ Table 'scans': Exists${NC}"
else
    echo -e "${RED}❌ Table 'scans': Missing${NC}"
fi

if echo "$TABLES" | grep -q "audit_log"; then
    echo -e "${GREEN}✅ Table 'audit_log': Exists${NC}"
else
    echo -e "${RED}❌ Table 'audit_log': Missing${NC}"
fi

if echo "$TABLES" | grep -q "user_sessions"; then
    echo -e "${GREEN}✅ Table 'user_sessions': Exists${NC}"
else
    echo -e "${RED}❌ Table 'user_sessions': Missing${NC}"
fi

echo ""
echo -e "${BOLD}Step 3: Check Table Schemas${NC}"

# Verify scans table has organization_id column
COLUMNS=$(psql "$DATABASE_URL" -t -c "SELECT column_name FROM information_schema.columns WHERE table_name='scans'" 2>/dev/null || echo "")

if echo "$COLUMNS" | grep -q "organization_id"; then
    echo -e "${GREEN}✅ Column 'organization_id': Exists in scans table${NC}"
else
    echo -e "${YELLOW}⚠️  Column 'organization_id': Missing from scans table${NC}"
fi

if echo "$COLUMNS" | grep -q "scan_id"; then
    echo -e "${GREEN}✅ Column 'scan_id': Exists in scans table${NC}"
else
    echo -e "${RED}❌ Column 'scan_id': Missing from scans table${NC}"
fi

echo ""
echo -e "${BOLD}Step 4: Test Data Operations${NC}"

# Test insert
TEST_ID="diagnostic_test_$(date +%s)"
if psql "$DATABASE_URL" -c "INSERT INTO scans (scan_id, username, timestamp, scan_type, region, file_count, total_pii_found, high_risk_count, result_json, organization_id) VALUES ('$TEST_ID', 'test_user', NOW(), 'test', 'NL', 1, 0, 0, '{}'::jsonb, 'default_org')" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Insert test: Success${NC}"
    
    # Test select
    if psql "$DATABASE_URL" -t -c "SELECT scan_id FROM scans WHERE scan_id='$TEST_ID'" | grep -q "$TEST_ID"; then
        echo -e "${GREEN}✅ Select test: Success${NC}"
    else
        echo -e "${RED}❌ Select test: Failed${NC}"
    fi
    
    # Clean up test data
    psql "$DATABASE_URL" -c "DELETE FROM scans WHERE scan_id='$TEST_ID'" > /dev/null 2>&1
    echo -e "${GREEN}✅ Delete test: Success${NC}"
else
    echo -e "${RED}❌ Insert test: Failed${NC}"
    echo -e "${YELLOW}This indicates a schema or permission issue${NC}"
fi

echo ""
echo -e "${BOLD}Step 5: Check Container Application Logs${NC}"

# Get full logs and search for key messages
FULL_LOGS=$(docker logs dataguardian-container 2>&1)

echo ""
echo -e "${YELLOW}Searching for key initialization messages...${NC}"

if echo "$FULL_LOGS" | grep -q "ResultsAggregator initialized"; then
    echo -e "${GREEN}✅ ResultsAggregator: Initialized${NC}"
else
    echo -e "${YELLOW}⚠️  ResultsAggregator: Message not found in logs${NC}"
fi

if echo "$FULL_LOGS" | grep -q "falling back to file-based storage"; then
    echo -e "${RED}❌ File storage fallback: Detected (DATABASE NOT WORKING)${NC}"
else
    echo -e "${GREEN}✅ File storage fallback: Not detected${NC}"
fi

if echo "$FULL_LOGS" | grep -q "current transaction is aborted"; then
    echo -e "${RED}❌ Transaction abort: Detected${NC}"
else
    echo -e "${GREEN}✅ Transaction abort: Not detected${NC}"
fi

if echo "$FULL_LOGS" | grep -q "Error creating database tables"; then
    echo -e "${RED}❌ Table creation error: Detected${NC}"
    echo ""
    echo -e "${YELLOW}Error details:${NC}"
    echo "$FULL_LOGS" | grep -A 3 "Error creating database tables"
else
    echo -e "${GREEN}✅ Table creation: No errors detected${NC}"
fi

echo ""
echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}DIAGNOSTIC COMPLETE${NC}"
echo ""
echo -e "${BOLD}Summary:${NC}"
echo -e "  • Database connection status above"
echo -e "  • Table existence verified above"
echo -e "  • Data operations tested above"
echo ""
echo -e "${BOLD}Next Steps:${NC}"
echo -e "  1. If tables are missing, container needs database initialization"
echo -e "  2. If data operations fail, check PostgreSQL permissions"
echo -e "  3. If file fallback detected, database init failed during startup"
echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"

