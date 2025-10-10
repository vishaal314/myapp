#!/bin/bash
################################################################################
# DataGuardian Pro - Scan History Fix for External Server
# Fixes database schema and tenant configuration to enable scan history display
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
║           DataGuardian Pro - Scan History Fix                       ║
║                                                                      ║
║        Fix database schema to enable scan history display           ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

echo -e "${BOLD}📊 Analyzing Issue...${NC}"
echo -e "   Scan history not displaying due to database schema issues\n"

# Database connection details (adjust if needed)
DB_HOST="${DB_HOST:-localhost}"
DB_USER="${DB_USER:-dataguardian}"
DB_NAME="${DB_NAME:-dataguardian}"
DB_PASSWORD="${DB_PASSWORD:-changeme}"

echo -e "${BOLD}Step 1: Fix Tenants Table Schema${NC}"
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" << 'EOFSQL'
-- Add missing columns to tenants table
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS max_storage_gb INTEGER DEFAULT 100;
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS compliance_regions JSONB DEFAULT '["Netherlands", "EU"]'::jsonb;
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS data_retention_days INTEGER DEFAULT 365;
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS encryption_enabled BOOLEAN DEFAULT true;
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS features JSONB DEFAULT '[]'::jsonb;

SELECT 'Tenants table schema updated' AS status;
EOFSQL

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Tenants table schema fixed${NC}\n"
else
    echo -e "${RED}❌ Failed to fix tenants table${NC}"
    exit 1
fi

echo -e "${BOLD}Step 2: Create/Update default_org Tenant${NC}"
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" << 'EOFSQL'
-- Create or update default_org tenant with all required fields
INSERT INTO tenants (
    organization_id, organization_name, status, tier,
    max_users, max_scans_per_month, max_storage_gb, 
    features, compliance_regions, subscription_status,
    data_retention_days, encryption_enabled
) VALUES (
    'default_org', 
    'Default Organization', 
    'active', 
    'enterprise',
    1000,
    999999,
    1000,
    '["unlimited_scans", "priority_support", "custom_integrations", "api_access", "white_label"]'::jsonb,
    '["Netherlands", "Germany", "France", "Belgium", "EU"]'::jsonb,
    'active',
    365,
    true
) ON CONFLICT (organization_id) DO UPDATE SET
    max_storage_gb = 1000,
    compliance_regions = '["Netherlands", "Germany", "France", "Belgium", "EU"]'::jsonb,
    features = '["unlimited_scans", "priority_support", "custom_integrations", "api_access", "white_label"]'::jsonb,
    max_scans_per_month = 999999,
    data_retention_days = 365,
    encryption_enabled = true,
    subscription_status = 'active',
    status = 'active';

SELECT 'default_org tenant created/updated' AS status;
EOFSQL

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ default_org tenant configured${NC}\n"
else
    echo -e "${RED}❌ Failed to configure tenant${NC}"
    exit 1
fi

echo -e "${BOLD}Step 3: Verify Scans Table${NC}"
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" << 'EOFSQL'
-- Ensure scans table has organization_id column
ALTER TABLE scans ADD COLUMN IF NOT EXISTS organization_id TEXT DEFAULT 'default_org';

-- Update any existing scans to have organization_id
UPDATE scans SET organization_id = 'default_org' WHERE organization_id IS NULL;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_scans_username ON scans(username);
CREATE INDEX IF NOT EXISTS idx_scans_timestamp ON scans(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_scans_org_id ON scans(organization_id);
CREATE INDEX IF NOT EXISTS idx_scans_scan_type ON scans(scan_type);

SELECT 'Scans table verified and indexed' AS status;
EOFSQL

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Scans table configured${NC}\n"
else
    echo -e "${RED}❌ Failed to configure scans table${NC}"
    exit 1
fi

echo -e "${BOLD}Step 4: Verify Configuration${NC}"
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" << 'EOFSQL'
-- Show tenant configuration
SELECT 
    organization_id, 
    organization_name, 
    tier, 
    max_scans_per_month, 
    max_storage_gb,
    status
FROM tenants 
WHERE organization_id = 'default_org';

-- Show scan count
SELECT COUNT(*) as total_scans FROM scans;

-- Show recent scans
SELECT scan_id, username, scan_type, timestamp 
FROM scans 
ORDER BY timestamp DESC 
LIMIT 5;
EOFSQL

echo -e "\n${BOLD}Step 5: Restart Application${NC}"
if docker ps | grep -q dataguardian-container; then
    echo -e "   Restarting Docker container..."
    docker restart dataguardian-container
    
    echo -e "\n${YELLOW}   Waiting for application to start (30 seconds)...${NC}"
    sleep 30
    
    if docker ps | grep -q dataguardian-container; then
        echo -e "${GREEN}✅ Application restarted successfully${NC}\n"
    else
        echo -e "${RED}❌ Application failed to restart${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Docker container not found - manual restart required${NC}\n"
fi

echo -e "${BOLD}Step 6: Verification${NC}"
# Check for errors in logs
if docker logs dataguardian-container 2>&1 | tail -50 | grep -q "max_storage_gb.*does not exist"; then
    echo -e "${RED}❌ Still has max_storage_gb errors${NC}"
    ERRORS=1
else
    echo -e "${GREEN}✅ No max_storage_gb errors${NC}"
fi

if docker logs dataguardian-container 2>&1 | tail -50 | grep -q "Access denied.*default_org"; then
    echo -e "${RED}❌ Still has tenant access errors${NC}"
    ERRORS=1
else
    echo -e "${GREEN}✅ No tenant access errors${NC}"
fi

if docker logs dataguardian-container 2>&1 | grep -q "You can now view your Streamlit app"; then
    echo -e "${GREEN}✅ Application started successfully${NC}"
else
    echo -e "${RED}❌ Application not started${NC}"
    ERRORS=1
fi

echo ""
echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${BLUE}  FIX SUMMARY${NC}"
echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo ""

if [ "${ERRORS:-0}" -eq 0 ]; then
    echo -e "${GREEN}${BOLD}🎉 SCAN HISTORY FIX COMPLETE!${NC}"
    echo -e "${GREEN}✅ Database schema fixed${NC}"
    echo -e "${GREEN}✅ Tenant configuration complete${NC}"
    echo -e "${GREEN}✅ Application restarted${NC}"
    echo -e "${GREEN}✅ No errors detected${NC}"
    echo ""
    echo -e "${BOLD}📋 Next Steps:${NC}"
    echo -e "   1. Login: https://dataguardianpro.nl"
    echo -e "   2. Run a test scan (Website Scanner)"
    echo -e "   3. Check if scan appears in history"
    echo -e "   4. Verify dashboard shows scan results"
    echo ""
    echo -e "${GREEN}✅ Scan history should now display correctly!${NC}"
else
    echo -e "${RED}${BOLD}⚠️  SOME ISSUES REMAIN${NC}"
    echo -e "${YELLOW}Check the errors above and review logs${NC}"
    echo ""
    echo -e "${BOLD}Debug Commands:${NC}"
    echo -e "   docker logs dataguardian-container | tail -100"
    echo -e "   PGPASSWORD=changeme psql -h localhost -U dataguardian -d dataguardian -c 'SELECT * FROM tenants;'"
fi

echo ""
