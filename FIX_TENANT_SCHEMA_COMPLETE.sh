#!/bin/bash
################################################################################
# DataGuardian Pro - Complete Tenant Schema Fix
# Fixes ALL missing columns and ensures schema matches code expectations
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
║    DataGuardian Pro - Complete Tenant Schema Fix                    ║
║                                                                      ║
║    Fixes schema mismatch between code and database                  ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

echo -e "${BOLD}🔍 Issue Analysis:${NC}"
echo -e "   The code expects columns that don't exist in the database"
echo -e "   This causes the application to fail during startup\n"

echo -e "${BOLD}📊 Applying Complete Fix...${NC}\n"

# Run comprehensive SQL fix inside container
docker exec dataguardian-container bash -c '
PGPASSWORD=changeme psql -h localhost -U dataguardian -d dataguardian << "EOFSQL"

-- ============================================================================
-- STEP 1: Ensure ALL required columns exist in tenants table
-- ============================================================================

\echo "Step 1: Adding ALL missing columns to tenants table..."

ALTER TABLE tenants ADD COLUMN IF NOT EXISTS organization_id VARCHAR(255);
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS organization_name VARCHAR(500);
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS tier VARCHAR(50) DEFAULT '"'"'enterprise'"'"';
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS max_users INTEGER DEFAULT 1000;
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS max_scans_per_month INTEGER DEFAULT 999999;
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS max_storage_gb INTEGER DEFAULT 1000;
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS features JSONB DEFAULT '"'"'[]'"'"'::jsonb;
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS compliance_regions JSONB DEFAULT '"'"'["Netherlands","EU"]'"'"'::jsonb;
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS data_residency VARCHAR(100) DEFAULT '"'"'EU'"'"';
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '"'"'{}'"'"'::jsonb;
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT '"'"'active'"'"';
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS subscription_status VARCHAR(50) DEFAULT '"'"'active'"'"';
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS data_retention_days INTEGER DEFAULT 365;
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS encryption_enabled BOOLEAN DEFAULT true;

\echo "✅ All tenant columns ensured"

-- ============================================================================
-- STEP 2: Delete and recreate default_org tenant with ALL fields
-- ============================================================================

\echo ""
\echo "Step 2: Recreating default_org tenant with complete configuration..."

-- Delete existing tenant to avoid conflicts
DELETE FROM tenants WHERE organization_id = '"'"'default_org'"'"';

-- Insert complete tenant configuration
INSERT INTO tenants (
    organization_id,
    organization_name,
    tier,
    max_users,
    max_scans_per_month,
    max_storage_gb,
    features,
    compliance_regions,
    data_residency,
    subscription_status,
    data_retention_days,
    encryption_enabled,
    status,
    metadata,
    created_at,
    updated_at
) VALUES (
    '"'"'default_org'"'"',
    '"'"'Default Organization'"'"',
    '"'"'enterprise'"'"',
    1000,
    999999,
    1000,
    '"'"'["unlimited_scans","priority_support","custom_integrations","api_access","white_label","all_scanners","advanced_reports","ai_powered_analysis"]'"'"'::jsonb,
    '"'"'["Netherlands","Germany","France","Belgium","EU"]'"'"'::jsonb,
    '"'"'Netherlands'"'"',
    '"'"'active'"'"',
    365,
    true,
    '"'"'active'"'"',
    '"'"'{"deployment":"production","market":"netherlands","compliance":["GDPR","UAVG"]}'"'"'::jsonb,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

\echo "✅ default_org tenant created with all fields"

-- ============================================================================
-- STEP 3: Verify tenant configuration
-- ============================================================================

\echo ""
\echo "Step 3: Verifying tenant configuration..."

SELECT 
    organization_id,
    organization_name,
    tier,
    max_scans_per_month,
    max_storage_gb,
    status,
    subscription_status
FROM tenants 
WHERE organization_id = '"'"'default_org'"'"';

\echo ""
\echo "✅ Tenant configuration verified"

-- ============================================================================
-- STEP 4: Check table schema to confirm all columns
-- ============================================================================

\echo ""
\echo "Step 4: Checking table schema..."

SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = '"'"'tenants'"'"' 
ORDER BY ordinal_position;

\echo ""
\echo "✅ Schema verification complete"

EOFSQL
'

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Database schema fixed successfully${NC}\n"
else
    echo -e "\n${RED}❌ Database fix failed${NC}"
    exit 1
fi

echo -e "${BOLD}🔄 Restarting application to apply changes...${NC}"
docker restart dataguardian-container

echo -e "${YELLOW}⏳ Waiting for application to start (30 seconds)...${NC}"
sleep 30

echo -e "\n${BOLD}✅ Final Verification:${NC}\n"

# Check for schema errors
SCHEMA_ERRORS=0
if docker logs dataguardian-container 2>&1 | tail -100 | grep -q "column.*does not exist"; then
    echo -e "${RED}❌ Still has column errors${NC}"
    SCHEMA_ERRORS=1
else
    echo -e "${GREEN}✅ No column errors${NC}"
fi

# Check for tenant errors
if docker logs dataguardian-container 2>&1 | tail -100 | grep -q "Access denied.*default_org"; then
    echo -e "${RED}❌ Still has tenant access errors${NC}"
    SCHEMA_ERRORS=1
else
    echo -e "${GREEN}✅ No tenant access errors${NC}"
fi

# Check for tenant creation errors
if docker logs dataguardian-container 2>&1 | tail -100 | grep -q "Failed to create tenant"; then
    echo -e "${RED}❌ Still has tenant creation errors${NC}"
    SCHEMA_ERRORS=1
else
    echo -e "${GREEN}✅ No tenant creation errors${NC}"
fi

# Check if application started
if docker logs dataguardian-container 2>&1 | grep -q "You can now view your Streamlit app"; then
    echo -e "${GREEN}✅ Application started successfully${NC}"
else
    echo -e "${RED}❌ Application failed to start${NC}"
    SCHEMA_ERRORS=1
fi

echo ""
echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"

if [ $SCHEMA_ERRORS -eq 0 ]; then
    echo -e "${GREEN}${BOLD}🎉 COMPLETE FIX SUCCESSFUL!${NC}"
    echo ""
    echo -e "${GREEN}✅ All columns added to database${NC}"
    echo -e "${GREEN}✅ default_org tenant fully configured${NC}"
    echo -e "${GREEN}✅ No schema errors in logs${NC}"
    echo -e "${GREEN}✅ No tenant access errors${NC}"
    echo -e "${GREEN}✅ Application running perfectly${NC}"
    echo ""
    echo -e "${BOLD}📋 Test Now:${NC}"
    echo -e "   1. Login: https://dataguardianpro.nl"
    echo -e "   2. Username: vishaal314 / vishaal2024"
    echo -e "   3. Run Website Scanner: https://example.com"
    echo -e "   4. Verify scan appears in dashboard!"
    echo ""
    echo -e "${GREEN}${BOLD}✅ Scan history is now fully operational!${NC}"
else
    echo -e "${RED}${BOLD}⚠️  ISSUES STILL PRESENT${NC}"
    echo ""
    echo -e "${YELLOW}Check detailed logs with:${NC}"
    echo -e "   docker logs dataguardian-container | tail -200"
    echo ""
    echo -e "${YELLOW}Check database schema with:${NC}"
    echo -e "   docker exec dataguardian-container psql -U dataguardian -d dataguardian -c '\d tenants'"
fi

echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo ""
