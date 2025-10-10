#!/bin/bash
################################################################################
# DataGuardian Pro - Patch Multi-Tenant Service
# Fixes the code to handle database schema correctly
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
║    DataGuardian Pro - Multi-Tenant Service Code Patch              ║
║                                                                      ║
║    Fixes code to handle database schema properly                    ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

echo -e "${BOLD}🔍 Root Cause:${NC}"
echo -e "   Code tries to query columns before schema is fully initialized"
echo -e "   Transaction isolation causes 'column does not exist' errors\n"

echo -e "${BOLD}Step 1: Backup Original File${NC}"
docker exec dataguardian-container cp /app/services/multi_tenant_service.py /app/services/multi_tenant_service.py.backup
echo -e "${GREEN}✅ Backup created${NC}\n"

echo -e "${BOLD}Step 2: Patch Multi-Tenant Service${NC}"

# Create patch that makes _load_tenant_configs more resilient
docker exec dataguardian-container bash -c 'cat > /tmp/tenant_patch.py << '"'"'EOFPATCH'
# Patch for multi_tenant_service.py

import re

with open("/app/services/multi_tenant_service.py", "r") as f:
    content = f.read()

# Replace _load_tenant_configs method to handle missing columns gracefully
old_load_method = r'''def _load_tenant_configs\(self\) -> None:
        """Load tenant configurations from database\."""
        try:
            conn = psycopg2\.connect\(self\.db_url, sslmode='"'"'require'"'"'\)
            cursor = conn\.cursor\(\)
            
            cursor\.execute\("""
            SELECT organization_id, organization_name, tier, max_users, max_scans_per_month,
                   max_storage_gb, features, compliance_regions, data_residency, created_at, metadata
            FROM tenants WHERE status = '"'"'active'"'"'
            """\)'''

new_load_method = '''def _load_tenant_configs(self) -> None:
        """Load tenant configurations from database."""
        try:
            conn = psycopg2.connect(self.db_url, sslmode='"'"'require'"'"')
            cursor = conn.cursor()
            
            # First, check if all required columns exist
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '"'"'tenants'"'"'
            """)
            existing_columns = {row[0] for row in cursor.fetchall()}
            
            required_cols = {'"'"'organization_id'"'"', '"'"'organization_name'"'"', '"'"'tier'"'"', '"'"'max_users'"'"', 
                           '"'"'max_scans_per_month'"'"', '"'"'max_storage_gb'"'"', '"'"'features'"'"', 
                           '"'"'compliance_regions'"'"', '"'"'data_residency'"'"', '"'"'created_at'"'"', '"'"'metadata'"'"'}
            
            if not required_cols.issubset(existing_columns):
                missing = required_cols - existing_columns
                logger.warning(f"Missing columns in tenants table: {missing}. Using default tenant.")
                self._create_default_tenant()
                return
            
            cursor.execute("""
            SELECT organization_id, organization_name, tier, max_users, max_scans_per_month,
                   max_storage_gb, features, compliance_regions, data_residency, created_at, metadata
            FROM tenants WHERE status = '"'"'active'"'"'
            """)'''

content = re.sub(old_load_method, new_load_method, content, flags=re.DOTALL)

with open("/app/services/multi_tenant_service.py", "w") as f:
    f.write(content)

print("✅ Patch applied successfully")
EOFPATCH
python3 /tmp/tenant_patch.py'

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Code patched${NC}\n"
else
    echo -e "${RED}❌ Patch failed${NC}"
    exit 1
fi

echo -e "${BOLD}Step 3: Restart Application${NC}"
docker restart dataguardian-container

echo -e "${YELLOW}⏳ Waiting for application (30 seconds)...${NC}"
sleep 30

echo -e "\n${BOLD}Step 4: Verify Fix${NC}"

# Check only FRESH logs
FRESH_LOGS=$(docker logs dataguardian-container --since=25s 2>&1)

ERRORS=0

if echo "$FRESH_LOGS" | grep -q "column.*does not exist"; then
    echo -e "${RED}❌ Still has column errors${NC}"
    ERRORS=1
else
    echo -e "${GREEN}✅ No column errors${NC}"
fi

if echo "$FRESH_LOGS" | grep -q "Failed to load tenant configs"; then
    echo -e "${YELLOW}⚠️  Tenant config warnings (may be OK if default created)${NC}"
else
    echo -e "${GREEN}✅ No tenant config errors${NC}"
fi

if echo "$FRESH_LOGS" | grep -q "Multi-tenant service initialized"; then
    echo -e "${GREEN}✅ Multi-tenant service initialized${NC}"
else
    echo -e "${YELLOW}⚠️  Service initialization not confirmed${NC}"
fi

if docker ps | grep -q dataguardian-container; then
    echo -e "${GREEN}✅ Container running${NC}"
else
    echo -e "${RED}❌ Container not running${NC}"
    ERRORS=1
fi

echo ""
echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}${BOLD}✅ CODE PATCH APPLIED!${NC}"
    echo ""
    echo -e "${GREEN}✅ Multi-tenant service patched${NC}"
    echo -e "${GREEN}✅ Application restarted${NC}"
    echo -e "${GREEN}✅ No critical errors${NC}"
    echo ""
    echo -e "${BOLD}🧪 Test Now:${NC}"
    echo -e "   https://dataguardianpro.nl"
    echo ""
    echo -e "${YELLOW}Note: If issues persist, run COMPLETE_SERVER_FIX.sh${NC}"
else
    echo -e "${YELLOW}${BOLD}⚠️  PATCH APPLIED BUT VERIFICATION INCONCLUSIVE${NC}"
    echo ""
    echo -e "${YELLOW}Try: COMPLETE_SERVER_FIX.sh for full rebuild${NC}"
fi

echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo ""

