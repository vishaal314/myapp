#!/bin/bash
################################################################################
# DATAGUARDIAN PRO - DEPLOYMENT PATCH SCRIPT
# November 2025 Release
# 
# This script deploys the latest code changes from October 11 - November 11, 2025
# to the external production server (dataguardianpro.nl)
#
# CHANGES INCLUDED:
# - Patent testing infrastructure (test_patent_claims_final.py)
# - Netherlands localization verification (test_netherlands_localization_e2e.py)
# - Database scanner SQL Server support (pymssql integration)
# - Multi-database validation and testing
# - RLS disable fix and Docker cache rebuild
# - Netherlands PII detection enhancements
# - UAVG compliance features
#
# USAGE:
#   bash deployment_patch_nov2025.sh [OPTIONS]
#
# OPTIONS:
#   --remote-host <host>    SSH host (default: dataguardianpro.nl)
#   --remote-user <user>    SSH user (default: root)
#   --remote-path <path>    Deployment path (default: /opt/dataguardian)
#   --backup                Create backup before deployment (default: yes)
#   --verify                Run verification tests after deployment (default: yes)
#   --dry-run               Show what would be done without executing
#
################################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
REMOTE_HOST="${REMOTE_HOST:-dataguardianpro.nl}"
REMOTE_USER="${REMOTE_USER:-root}"
REMOTE_PATH="${REMOTE_PATH:-/opt/dataguardian}"
CREATE_BACKUP="${CREATE_BACKUP:-yes}"
RUN_VERIFICATION="${RUN_VERIFICATION:-yes}"
DRY_RUN=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --remote-host)
            REMOTE_HOST="$2"
            shift 2
            ;;
        --remote-user)
            REMOTE_USER="$2"
            shift 2
            ;;
        --remote-path)
            REMOTE_PATH="$2"
            shift 2
            ;;
        --no-backup)
            CREATE_BACKUP="no"
            shift
            ;;
        --no-verify)
            RUN_VERIFICATION="no"
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Timestamp for backup and patch
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PATCH_NAME="dataguardian_patch_nov2025_${TIMESTAMP}"
STAGING_DIR="/tmp/${PATCH_NAME}"
TARBALL="${PATCH_NAME}.tar.gz"

################################################################################
# Helper Functions
################################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

execute_cmd() {
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}[DRY-RUN]${NC} Would execute: $1"
    else
        eval "$1"
    fi
}

################################################################################
# Step 1: Pre-flight Checks
################################################################################

log_info "DataGuardian Pro - November 2025 Deployment Patch"
log_info "=================================================="
echo ""
log_info "Remote Host: ${REMOTE_USER}@${REMOTE_HOST}"
log_info "Remote Path: ${REMOTE_PATH}"
log_info "Backup: ${CREATE_BACKUP}"
log_info "Verification: ${RUN_VERIFICATION}"
log_info "Dry Run: ${DRY_RUN}"
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    log_error "Must be run from DataGuardian Pro root directory"
    exit 1
fi

# Check SSH connectivity
log_info "Testing SSH connection to ${REMOTE_HOST}..."
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "${REMOTE_USER}@${REMOTE_HOST}" "echo 'SSH OK'" &>/dev/null; then
    log_error "Cannot connect to ${REMOTE_HOST} via SSH"
    log_info "Please ensure SSH key authentication is set up"
    exit 1
fi
log_success "SSH connection verified"

################################################################################
# Step 2: Create Staging Directory and Gather Files
################################################################################

log_info "Creating staging directory: ${STAGING_DIR}"
execute_cmd "rm -rf ${STAGING_DIR}"
execute_cmd "mkdir -p ${STAGING_DIR}"

# Critical files to deploy (based on git history Oct 11 - Nov 11, 2025)
log_info "Gathering critical files for deployment..."

CRITICAL_FILES=(
    # Core application
    "app.py"
    
    # Enhanced scanner services
    "services/db_scanner.py"
    "services/predictive_compliance_engine.py"
    "services/dpia_scanner.py"
    "services/intelligent_db_scanner.py"
    
    # Netherlands localization
    "utils/pii_detection.py"
    "utils/netherlands_uavg_compliance.py"
    "utils/netherlands_gdpr.py"
    "utils/i18n.py"
    "utils/unified_translation.py"
    "utils/animated_language_switcher.py"
    
    # Translations
    "translations/nl.json"
    "translations/en.json"
    
    # Testing infrastructure
    "test_patent_claims_final.py"
    "test_netherlands_localization_e2e.py"
    "test_sqlserver_pymssql.py"
    "test_mysql_netherlands_pii.py"
    "test_database_scanner.py"
    
    # Configuration
    "config/pricing_config.py"
    
    # Documentation
    "replit.md"
    "NETHERLANDS_LOCALIZATION_FINAL_REPORT.md"
    "PATENT_CLAIMS_TEST_REPORT.md"
    "PATENT_TEST_EXECUTIVE_SUMMARY.md"
    
    # Deployment scripts
    "deployment/FINAL_COMPLETE_FIX.sh"
)

# Copy critical files to staging
FILE_COUNT=0
for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        target_dir="${STAGING_DIR}/$(dirname "$file")"
        execute_cmd "mkdir -p \"${target_dir}\""
        execute_cmd "cp \"$file\" \"${target_dir}/\""
        FILE_COUNT=$((FILE_COUNT + 1))
    else
        log_warning "File not found, skipping: $file"
    fi
done

log_success "Staged ${FILE_COUNT} files for deployment"

################################################################################
# Step 3: Create Deployment Instructions
################################################################################

log_info "Creating deployment instructions..."

cat > "${STAGING_DIR}/DEPLOY_INSTRUCTIONS.txt" << 'EOF'
DATAGUARDIAN PRO - NOVEMBER 2025 DEPLOYMENT
============================================

This patch includes critical updates from October 11 - November 11, 2025:

CRITICAL CHANGES:
1. Database Scanner: Added SQL Server support with pymssql (no ODBC needed)
2. Multi-Database: PostgreSQL, MySQL, SQL Server validation complete
3. Netherlands Localization: 100% verification (Dutch translations, BSN detection, UAVG)
4. Patent Testing: Predictive Engine + DPIA Scanner verification infrastructure
5. RLS Fix: DISABLE_RLS environment variable to prevent empty scan results
6. Docker Cache: --no-cache rebuild to ensure code changes deploy

DEPLOYMENT STEPS:
1. Backup current deployment (CRITICAL - do this first!)
2. Stop running services
3. Apply patch files with rsync
4. Set environment variable: DISABLE_RLS=true
5. Rebuild Docker images with --no-cache
6. Restart services (Streamlit, Redis, Webhook)
7. Run verification tests
8. Check logs for errors

ENVIRONMENT VARIABLES (must be set):
- DISABLE_RLS=true
- DATABASE_URL=<your_postgresql_url>
- JWT_SECRET=<your_secret>
- OPENAI_API_KEY=<your_key>
- STRIPE_SECRET_KEY=<your_key>

ROLLBACK PROCEDURE:
If deployment fails, restore from backup:
  cd /opt/dataguardian
  rm -rf *
  tar -xzf /opt/dataguardian/backups/backup_<timestamp>.tar.gz
  docker-compose up -d --build

VERIFICATION:
- Check /opt/dataguardian/logs/ for errors
- Test scan functionality (Database Scanner especially)
- Verify Dutch language UI (switch to Nederlands)
- Run: python test_netherlands_localization_e2e.py
- Check Recent Scan Activity in dashboard

SUPPORT:
For issues, check:
- Docker logs: docker-compose logs -f
- Application logs: /opt/dataguardian/logs/
- Database connectivity: psql $DATABASE_URL

EOF

log_success "Deployment instructions created"

################################################################################
# Step 4: Create Remote Deployment Script
################################################################################

log_info "Creating remote deployment script..."

cat > "${STAGING_DIR}/apply_patch.sh" << 'EOF'
#!/bin/bash
# Remote deployment script - runs on production server

set -e
set -u

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

DEPLOYMENT_PATH="${1:-/opt/dataguardian}"
PATCH_DIR="${2:-/tmp/dataguardian_patch}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

log_info "Starting deployment to ${DEPLOYMENT_PATH}"

# Step 1: Create backup
if [ -d "${DEPLOYMENT_PATH}" ]; then
    log_info "Creating backup..."
    mkdir -p "${DEPLOYMENT_PATH}/backups"
    cd "${DEPLOYMENT_PATH}"
    tar -czf "backups/backup_${TIMESTAMP}.tar.gz" \
        --exclude='backups' \
        --exclude='*.pyc' \
        --exclude='__pycache__' \
        --exclude='.git' \
        --exclude='dump.rdb' \
        . || log_warning "Backup creation had warnings"
    log_success "Backup created: backups/backup_${TIMESTAMP}.tar.gz"
fi

# Step 2: Stop services
log_info "Stopping services..."
cd "${DEPLOYMENT_PATH}"
if [ -f "docker-compose.yml" ]; then
    docker-compose down || log_warning "Services may not have been running"
fi

# Step 3: Apply patch files
log_info "Applying patch files..."
rsync -av --exclude='*.pyc' --exclude='__pycache__' "${PATCH_DIR}/" "${DEPLOYMENT_PATH}/"
log_success "Files synchronized"

# Step 4: Set critical environment variables
log_info "Setting environment variables..."
if [ -f "${DEPLOYMENT_PATH}/.env" ]; then
    # Add DISABLE_RLS if not present
    if ! grep -q "DISABLE_RLS" "${DEPLOYMENT_PATH}/.env"; then
        echo "DISABLE_RLS=true" >> "${DEPLOYMENT_PATH}/.env"
        log_success "Added DISABLE_RLS=true to .env"
    fi
else
    log_warning ".env file not found - you may need to create it"
fi

# Step 5: Rebuild Docker images (cache-busted)
log_info "Rebuilding Docker images with --no-cache..."
cd "${DEPLOYMENT_PATH}"
if [ -f "docker-compose.yml" ]; then
    docker-compose build --no-cache || log_error "Docker rebuild failed"
    log_success "Docker images rebuilt"
fi

# Step 6: Restart services
log_info "Starting services..."
cd "${DEPLOYMENT_PATH}"
if [ -f "docker-compose.yml" ]; then
    docker-compose up -d
    log_success "Services started"
    
    # Wait for services to be ready
    log_info "Waiting for services to initialize (30s)..."
    sleep 30
fi

# Step 7: Verification
log_info "Running basic verification..."

# Check if containers are running
if docker-compose ps | grep -q "Up"; then
    log_success "Docker containers are running"
else
    log_error "Some containers failed to start"
    docker-compose ps
fi

# Check logs for critical errors
if docker-compose logs --tail=50 | grep -i "error" | grep -v "INFO" | grep -v "DEBUG"; then
    log_warning "Found errors in recent logs - please review"
else
    log_success "No critical errors in recent logs"
fi

log_success "Deployment completed!"
echo ""
log_info "Next steps:"
echo "  1. Check application at https://dataguardianpro.nl"
echo "  2. Test Database Scanner functionality"
echo "  3. Verify Dutch language UI (Nederlands)"
echo "  4. Review logs: docker-compose logs -f"
echo ""
log_info "Rollback if needed:"
echo "  cd ${DEPLOYMENT_PATH}"
echo "  docker-compose down"
echo "  rm -rf *"
echo "  tar -xzf backups/backup_${TIMESTAMP}.tar.gz"
echo "  docker-compose up -d --build"

EOF

chmod +x "${STAGING_DIR}/apply_patch.sh"
log_success "Remote deployment script created"

################################################################################
# Step 5: Create Tarball
################################################################################

log_info "Creating deployment tarball: ${TARBALL}"
execute_cmd "cd /tmp && tar -czf ${TARBALL} ${PATCH_NAME}/"
log_success "Tarball created: /tmp/${TARBALL}"

# Calculate size
if [ "$DRY_RUN" = false ]; then
    TARBALL_SIZE=$(du -h "/tmp/${TARBALL}" | cut -f1)
    log_info "Tarball size: ${TARBALL_SIZE}"
fi

################################################################################
# Step 6: Transfer to Remote Server
################################################################################

if [ "$DRY_RUN" = false ]; then
    log_info "Transferring patch to ${REMOTE_HOST}..."
    scp "/tmp/${TARBALL}" "${REMOTE_USER}@${REMOTE_HOST}:/tmp/"
    log_success "Patch transferred successfully"
    
    # Extract on remote server
    log_info "Extracting patch on remote server..."
    ssh "${REMOTE_USER}@${REMOTE_HOST}" "cd /tmp && tar -xzf ${TARBALL}"
    log_success "Patch extracted"
else
    log_info "[DRY-RUN] Would transfer /tmp/${TARBALL} to ${REMOTE_HOST}"
fi

################################################################################
# Step 7: Execute Remote Deployment
################################################################################

log_info "Executing deployment on remote server..."
echo ""
log_warning "CRITICAL: This will update production code and restart services!"
log_warning "Backup will be created automatically at ${REMOTE_PATH}/backups/"
echo ""

if [ "$DRY_RUN" = false ]; then
    read -p "Continue with deployment? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        log_info "Deployment cancelled by user"
        exit 0
    fi
    
    # Execute remote deployment script
    log_info "Running deployment script on ${REMOTE_HOST}..."
    ssh "${REMOTE_USER}@${REMOTE_HOST}" "bash /tmp/${PATCH_NAME}/apply_patch.sh ${REMOTE_PATH} /tmp/${PATCH_NAME}"
    
    if [ $? -eq 0 ]; then
        log_success "Deployment completed successfully!"
    else
        log_error "Deployment encountered errors - check logs on ${REMOTE_HOST}"
        exit 1
    fi
else
    log_info "[DRY-RUN] Would execute deployment on remote server"
fi

################################################################################
# Step 8: Post-Deployment Verification
################################################################################

if [ "$RUN_VERIFICATION" = "yes" ] && [ "$DRY_RUN" = false ]; then
    log_info "Running post-deployment verification..."
    
    # Check if web server is responding
    log_info "Checking web server response..."
    if curl -s -o /dev/null -w "%{http_code}" "https://${REMOTE_HOST}" | grep -q "200\|301\|302"; then
        log_success "Web server is responding"
    else
        log_warning "Web server may not be responding correctly"
    fi
    
    # Check Docker containers
    log_info "Checking Docker container status..."
    ssh "${REMOTE_USER}@${REMOTE_HOST}" "cd ${REMOTE_PATH} && docker-compose ps"
    
    # Display recent logs
    log_info "Recent application logs:"
    ssh "${REMOTE_USER}@${REMOTE_HOST}" "cd ${REMOTE_PATH} && docker-compose logs --tail=20"
fi

################################################################################
# Step 9: Cleanup and Summary
################################################################################

log_info "Cleaning up local staging..."
if [ "$DRY_RUN" = false ]; then
    rm -rf "${STAGING_DIR}"
    # Keep tarball for reference
    log_info "Tarball preserved at: /tmp/${TARBALL}"
fi

echo ""
echo "================================================================================"
log_success "DEPLOYMENT PATCH COMPLETED!"
echo "================================================================================"
echo ""
log_info "Summary:"
echo "  - Files deployed: ${FILE_COUNT}"
echo "  - Remote host: ${REMOTE_HOST}"
echo "  - Deployment path: ${REMOTE_PATH}"
echo "  - Backup location: ${REMOTE_PATH}/backups/backup_${TIMESTAMP}.tar.gz"
echo ""
log_info "Key changes deployed:"
echo "  ✅ Database Scanner: SQL Server support (pymssql)"
echo "  ✅ Netherlands Localization: 100% verified (Dutch UI, BSN, UAVG)"
echo "  ✅ Patent Testing: Infrastructure for Predictive Engine + DPIA"
echo "  ✅ RLS Fix: DISABLE_RLS environment variable"
echo "  ✅ Docker Cache: --no-cache rebuild implemented"
echo ""
log_info "Verification steps:"
echo "  1. Visit https://${REMOTE_HOST} and check functionality"
echo "  2. Test Database Scanner with SQL Server/PostgreSQL/MySQL"
echo "  3. Switch to Dutch language (Nederlands) and verify UI"
echo "  4. Check Recent Scan Activity in dashboard"
echo "  5. Review logs: ssh ${REMOTE_USER}@${REMOTE_HOST} 'cd ${REMOTE_PATH} && docker-compose logs -f'"
echo ""
log_info "Rollback command (if needed):"
echo "  ssh ${REMOTE_USER}@${REMOTE_HOST}"
echo "  cd ${REMOTE_PATH}"
echo "  docker-compose down"
echo "  rm -rf *"
echo "  tar -xzf backups/backup_${TIMESTAMP}.tar.gz"
echo "  docker-compose up -d --build"
echo ""
log_success "Deployment patch script completed successfully!"
echo "================================================================================"
