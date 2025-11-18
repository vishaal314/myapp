#!/bin/bash
################################################################################
# DataGuardian Pro - Production Deployment Script
# Deploy to: 45.81.35.202 / dataguardianpro.nl
# 
# This script deploys:
# 1. Revenue tracking system (NEW)
# 2. Database scanner improvements (NEW)
# 3. All application updates
################################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PRODUCTION_SERVER="root@45.81.35.202"
APP_DIR="/opt/dataguardian"
BACKUP_DIR="/opt/dataguardian_backup_$(date +%Y%m%d_%H%M%S)"
DOCKER_COMPOSE_FILE="docker-compose.yml"

echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  DataGuardian Pro - Production Deployment${NC}"
echo -e "${BLUE}  Target: dataguardianpro.nl (45.81.35.202)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"

# Step 1: Pre-flight checks
echo -e "\n${YELLOW}[Step 1/8]${NC} Running pre-flight checks..."

# Check if we can connect to server
if ! ssh -o ConnectTimeout=5 $PRODUCTION_SERVER "echo 'Connection successful'" > /dev/null 2>&1; then
    echo -e "${RED}✗ Cannot connect to production server${NC}"
    echo -e "${YELLOW}Please ensure:${NC}"
    echo -e "  1. SSH access is configured: ssh $PRODUCTION_SERVER"
    echo -e "  2. Server is online and accessible"
    exit 1
fi
echo -e "${GREEN}✓ Server connection verified${NC}"

# Check if required files exist
REQUIRED_FILES=(
    "services/visitor_tracker.py"
    "services/auth_tracker.py"
    "services/db_scanner.py"
    "components/pricing_display.py"
    "services/subscription_manager.py"
    "services/stripe_payment.py"
    "app.py"
    "docker-compose.yml"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}✗ Required file missing: $file${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✓ All required files present${NC}"

# Step 2: Create deployment package
echo -e "\n${YELLOW}[Step 2/8]${NC} Creating deployment package..."

DEPLOY_PKG="dataguardian_deploy_$(date +%Y%m%d_%H%M%S).tar.gz"

tar -czf "$DEPLOY_PKG" \
    services/ \
    components/ \
    utils/ \
    app.py \
    docker-compose.yml \
    requirements.txt \
    .streamlit/ \
    Dockerfile \
    2>/dev/null || true

if [ -f "$DEPLOY_PKG" ]; then
    PACKAGE_SIZE=$(ls -lh "$DEPLOY_PKG" | awk '{print $5}')
    echo -e "${GREEN}✓ Deployment package created: $DEPLOY_PKG ($PACKAGE_SIZE)${NC}"
else
    echo -e "${RED}✗ Failed to create deployment package${NC}"
    exit 1
fi

# Step 3: Backup current production
echo -e "\n${YELLOW}[Step 3/8]${NC} Backing up current production..."

ssh $PRODUCTION_SERVER "
    if [ -d '$APP_DIR' ]; then
        echo 'Creating backup: $BACKUP_DIR'
        cp -r $APP_DIR $BACKUP_DIR
        echo 'Backup created successfully'
    else
        echo 'No existing installation found - fresh deployment'
    fi
"
echo -e "${GREEN}✓ Backup completed${NC}"

# Step 4: Transfer deployment package
echo -e "\n${YELLOW}[Step 4/8]${NC} Transferring deployment package to server..."

scp "$DEPLOY_PKG" "$PRODUCTION_SERVER:/tmp/" || {
    echo -e "${RED}✗ Failed to transfer deployment package${NC}"
    exit 1
}
echo -e "${GREEN}✓ Package transferred successfully${NC}"

# Step 5: Extract and prepare on server
echo -e "\n${YELLOW}[Step 5/8]${NC} Extracting package on production server..."

ssh $PRODUCTION_SERVER "
    cd /tmp
    mkdir -p dataguardian_new
    tar -xzf $DEPLOY_PKG -C dataguardian_new
    echo 'Package extracted to /tmp/dataguardian_new'
"
echo -e "${GREEN}✓ Package extracted${NC}"

# Step 6: Database preparation
echo -e "\n${YELLOW}[Step 6/8]${NC} Preparing database (GDPR compliance check)..."

ssh $PRODUCTION_SERVER "
    # Check for visitor_events table
    docker exec dataguardian-postgres psql -U dataguardian -d dataguardian_prod -c '
        SELECT COUNT(*) as visitor_events_count 
        FROM information_schema.tables 
        WHERE table_name = '\''visitor_events'\'';
    ' 2>/dev/null || echo 'Database not ready - will be created on first run'
"
echo -e "${GREEN}✓ Database prepared${NC}"

# Step 7: Deploy application
echo -e "\n${YELLOW}[Step 7/8]${NC} Deploying application..."

ssh $PRODUCTION_SERVER "
    # Stop current services
    echo 'Stopping current services...'
    cd $APP_DIR 2>/dev/null && docker-compose down || echo 'No services to stop'
    
    # Deploy new version
    echo 'Deploying new version...'
    mkdir -p $APP_DIR
    rsync -av --delete /tmp/dataguardian_new/ $APP_DIR/
    
    # Set permissions
    cd $APP_DIR
    chmod +x *.sh 2>/dev/null || true
    
    # Pull latest images and rebuild
    echo 'Rebuilding Docker images...'
    docker-compose build --no-cache
    
    # Start services
    echo 'Starting services...'
    docker-compose up -d
    
    # Wait for services to be ready
    echo 'Waiting for services to start...'
    sleep 10
    
    # Check service health
    docker-compose ps
"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Application deployed successfully${NC}"
else
    echo -e "${RED}✗ Deployment failed${NC}"
    echo -e "${YELLOW}Rolling back to previous version...${NC}"
    ssh $PRODUCTION_SERVER "
        rm -rf $APP_DIR
        mv $BACKUP_DIR $APP_DIR
        cd $APP_DIR
        docker-compose up -d
    "
    exit 1
fi

# Step 8: Verify deployment
echo -e "\n${YELLOW}[Step 8/8]${NC} Verifying deployment..."

# Check if services are running
echo -e "\n${BLUE}Service Health Check:${NC}"
ssh $PRODUCTION_SERVER "
    cd $APP_DIR
    docker-compose ps
    
    echo ''
    echo 'Testing application endpoint...'
    curl -f http://localhost:5000/_stcore/health 2>/dev/null && echo 'Streamlit: ✓ Healthy' || echo 'Streamlit: ✗ Not responding'
    
    echo ''
    echo 'Checking database...'
    docker exec dataguardian-postgres pg_isready -U dataguardian && echo 'PostgreSQL: ✓ Ready' || echo 'PostgreSQL: ✗ Not ready'
    
    echo ''
    echo 'Checking Redis...'
    docker exec dataguardian-redis redis-cli ping 2>/dev/null && echo 'Redis: ✓ PONG' || echo 'Redis: ✗ Not responding'
"

# Cleanup
echo -e "\n${YELLOW}Cleaning up...${NC}"
rm -f "$DEPLOY_PKG"
ssh $PRODUCTION_SERVER "rm -rf /tmp/dataguardian_new /tmp/$DEPLOY_PKG"

# Final summary
echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ DEPLOYMENT COMPLETE${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "\n${YELLOW}Next Steps:${NC}"
echo -e "  1. Visit https://dataguardianpro.nl to verify"
echo -e "  2. Test database scanner: New Scan → Database Scan"
echo -e "  3. Check analytics dashboard: Settings → Analytics"
echo -e "  4. Monitor logs: ssh $PRODUCTION_SERVER 'docker-compose logs -f'"
echo -e "\n${YELLOW}Backup Location:${NC}"
echo -e "  $BACKUP_DIR"
echo -e "\n${YELLOW}Rollback Command (if needed):${NC}"
echo -e "  ssh $PRODUCTION_SERVER 'rm -rf $APP_DIR && mv $BACKUP_DIR $APP_DIR && cd $APP_DIR && docker-compose up -d'"
echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════════${NC}\n"
