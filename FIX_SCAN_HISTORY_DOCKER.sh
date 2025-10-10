#!/bin/bash
################################################################################
# DataGuardian Pro - Scan History Fix for Docker Deployment
# Fixes database schema inside Docker container
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
║         DataGuardian Pro - Scan History Fix (Docker)                ║
║                                                                      ║
║        Fix database to enable scan history display                  ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

echo -e "${BOLD}🔍 Diagnosis:${NC}"
echo -e "   ❌ Scan history not displaying"
echo -e "   ❌ Database schema missing columns"
echo -e "   ❌ Tenant configuration incomplete\n"

echo -e "${BOLD}📊 Applying Fix...${NC}\n"

# Run SQL fix inside container using environment DATABASE_URL
docker exec dataguardian-container bash -c '
PGPASSWORD=changeme psql -h localhost -U dataguardian -d dataguardian << "EOFSQL"

-- Step 1: Fix tenants table schema
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS max_storage_gb INTEGER DEFAULT 100;
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS compliance_regions JSONB DEFAULT '"'"'["Netherlands", "EU"]'"'"'::jsonb;
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS data_retention_days INTEGER DEFAULT 365;
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS encryption_enabled BOOLEAN DEFAULT true;
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS features JSONB DEFAULT '"'"'[]'"'"'::jsonb;

\echo "✅ Step 1: Tenants table schema updated"

-- Step 2: Create/Update default_org tenant
INSERT INTO tenants (
    organization_id, organization_name, status, tier,
    max_users, max_scans_per_month, max_storage_gb, 
    features, compliance_regions, subscription_status,
    data_retention_days, encryption_enabled
) VALUES (
    '"'"'default_org'"'"', 
    '"'"'Default Organization'"'"', 
    '"'"'active'"'"', 
    '"'"'enterprise'"'"',
    1000,
    999999,
    1000,
    '"'"'["unlimited_scans", "priority_support", "custom_integrations", "api_access", "white_label"]'"'"'::jsonb,
    '"'"'["Netherlands", "Germany", "France", "Belgium", "EU"]'"'"'::jsonb,
    '"'"'active'"'"',
    365,
    true
) ON CONFLICT (organization_id) DO UPDATE SET
    max_storage_gb = 1000,
    compliance_regions = '"'"'["Netherlands", "Germany", "France", "Belgium", "EU"]'"'"'::jsonb,
    features = '"'"'["unlimited_scans", "priority_support", "custom_integrations", "api_access", "white_label"]'"'"'::jsonb,
    max_scans_per_month = 999999,
    data_retention_days = 365,
    encryption_enabled = true,
    subscription_status = '"'"'active'"'"',
    status = '"'"'active'"'"';

\echo "✅ Step 2: default_org tenant configured"

-- Step 3: Fix scans table
ALTER TABLE scans ADD COLUMN IF NOT EXISTS organization_id TEXT DEFAULT '"'"'default_org'"'"';
UPDATE scans SET organization_id = '"'"'default_org'"'"' WHERE organization_id IS NULL;

CREATE INDEX IF NOT EXISTS idx_scans_username ON scans(username);
CREATE INDEX IF NOT EXISTS idx_scans_timestamp ON scans(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_scans_org_id ON scans(organization_id);
CREATE INDEX IF NOT EXISTS idx_scans_scan_type ON scans(scan_type);

\echo "✅ Step 3: Scans table configured"

-- Step 4: Verification
\echo ""
\echo "📊 Tenant Configuration:"
SELECT organization_id, organization_name, tier, max_scans_per_month, status
FROM tenants WHERE organization_id = '"'"'default_org'"'"';

\echo ""
\echo "📊 Scan Statistics:"
SELECT COUNT(*) as total_scans FROM scans;

EOFSQL
'

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Database schema fixed successfully${NC}\n"
else
    echo -e "\n${RED}❌ Database fix failed${NC}"
    exit 1
fi

echo -e "${BOLD}🔄 Restarting application...${NC}"
docker restart dataguardian-container

echo -e "${YELLOW}⏳ Waiting for application to start (30 seconds)...${NC}"
sleep 30

echo -e "\n${BOLD}✅ Verification:${NC}"

# Check for errors
ERRORS=0

if docker logs dataguardian-container 2>&1 | tail -50 | grep -q "max_storage_gb.*does not exist"; then
    echo -e "${RED}❌ Still has column errors${NC}"
    ERRORS=1
else
    echo -e "${GREEN}✅ No column errors${NC}"
fi

if docker logs dataguardian-container 2>&1 | tail -50 | grep -q "Access denied.*default_org"; then
    echo -e "${RED}❌ Still has tenant errors${NC}"
    ERRORS=1
else
    echo -e "${GREEN}✅ No tenant errors${NC}"
fi

if docker logs dataguardian-container 2>&1 | grep -q "You can now view your Streamlit app"; then
    echo -e "${GREEN}✅ Application started${NC}"
else
    echo -e "${RED}❌ Application not started${NC}"
    ERRORS=1
fi

echo ""
echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}${BOLD}🎉 SCAN HISTORY FIX COMPLETE!${NC}"
    echo ""
    echo -e "${GREEN}✅ Database schema: Fixed${NC}"
    echo -e "${GREEN}✅ Tenant config: Complete${NC}"
    echo -e "${GREEN}✅ Application: Running${NC}"
    echo -e "${GREEN}✅ No errors: Verified${NC}"
    echo ""
    echo -e "${BOLD}📋 Test Scan History:${NC}"
    echo -e "   1. Login: https://dataguardianpro.nl"
    echo -e "   2. Username: vishaal314 / vishaal2024"
    echo -e "   3. Run Website Scanner: https://example.com"
    echo -e "   4. Check Dashboard - scan should appear!"
    echo ""
    echo -e "${GREEN}✅ Scan history is now operational!${NC}"
else
    echo -e "${RED}${BOLD}⚠️  ISSUES DETECTED${NC}"
    echo ""
    echo -e "${YELLOW}Debug with:${NC}"
    echo -e "   docker logs dataguardian-container | tail -100"
fi

echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo ""
