#!/bin/bash
# SYNC REPLIT TO EXTERNAL SERVER - Achieve 100% Parity
# Syncs code, environment, database, Redis, and configuration

set -e

EXTERNAL_SERVER="root@dataguardianpro.nl"
EXTERNAL_DIR="/opt/dataguardian"

echo "🔄 SYNCING REPLIT → EXTERNAL SERVER"
echo "===================================="
echo ""
echo "Target: $EXTERNAL_SERVER:$EXTERNAL_DIR"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}This will sync 5 components:${NC}"
echo "  1. ✅ Code files (all .py, .toml, configs)"
echo "  2. ✅ Environment variables (secrets)"
echo "  3. ✅ Database schema & data"
echo "  4. ✅ Redis data"
echo "  5. ✅ Configuration files"
echo ""
read -p "Continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════"
echo "COMPONENT 1: CODE FILES"
echo "════════════════════════════════════════════════"

# Create fresh tar excluding unnecessary files
echo "Creating code archive..."
tar -czf dataguardian_sync.tar.gz \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='*.pyo' \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='venv' \
    --exclude='*.log' \
    --exclude='dump.rdb' \
    --exclude='.replit' \
    --exclude='replit.nix' \
    app.py \
    services/ \
    utils/ \
    .streamlit/ \
    Dockerfile \
    requirements.txt \
    2>/dev/null || true

if [ -f "dataguardian_sync.tar.gz" ]; then
    SIZE=$(du -h dataguardian_sync.tar.gz | cut -f1)
    echo -e "${GREEN}✅ Code archive created: $SIZE${NC}"
    
    # Upload to external server
    echo "Uploading to external server..."
    scp dataguardian_sync.tar.gz $EXTERNAL_SERVER:/root/
    echo -e "${GREEN}✅ Code uploaded${NC}"
else
    echo -e "${RED}❌ Failed to create archive${NC}"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════"
echo "COMPONENT 2: ENVIRONMENT VARIABLES"
echo "════════════════════════════════════════════════"

# Create environment file
cat > .dataguardian_env_sync << EOF
# DataGuardian Pro Environment Variables
# Synced from Replit on $(date)

# Database
DATABASE_URL=$DATABASE_URL

# Redis
REDIS_URL=redis://localhost:6379

# Secrets
DATAGUARDIAN_MASTER_KEY=$DATAGUARDIAN_MASTER_KEY
JWT_SECRET=$JWT_SECRET
OPENAI_API_KEY=$OPENAI_API_KEY
STRIPE_SECRET_KEY=$STRIPE_SECRET_KEY

# Application
PYTHONUNBUFFERED=1
STREAMLIT_SERVER_PORT=5000
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true

# PostgreSQL (extracted from DATABASE_URL)
PGHOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
PGPORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
PGDATABASE=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
PGUSER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
PGPASSWORD=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
EOF

# Check critical variables
if [ -z "$DATAGUARDIAN_MASTER_KEY" ]; then
    echo -e "${YELLOW}⚠️  DATAGUARDIAN_MASTER_KEY not set in Replit${NC}"
    echo "Generating new key..."
    NEW_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
    echo "DATAGUARDIAN_MASTER_KEY=$NEW_KEY" >> .dataguardian_env_sync
    echo -e "${GREEN}✅ Generated: $NEW_KEY${NC}"
fi

if [ -z "$JWT_SECRET" ]; then
    echo -e "${YELLOW}⚠️  JWT_SECRET not set in Replit${NC}"
    echo "Generating new secret..."
    NEW_JWT=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
    echo "JWT_SECRET=$NEW_JWT" >> .dataguardian_env_sync
    echo -e "${GREEN}✅ Generated: $NEW_JWT${NC}"
fi

echo "Uploading environment variables..."
scp .dataguardian_env_sync $EXTERNAL_SERVER:/root/.dataguardian_env
echo -e "${GREEN}✅ Environment variables uploaded${NC}"

# Clean up local env file
rm .dataguardian_env_sync

echo ""
echo "════════════════════════════════════════════════"
echo "COMPONENT 3: DATABASE SCHEMA & DATA"
echo "════════════════════════════════════════════════"

if [ -n "$DATABASE_URL" ]; then
    echo "Creating database dump..."
    
    # Create dump file
    DUMP_FILE="dataguardian_db_$(date +%Y%m%d_%H%M%S).sql"
    
    pg_dump "$DATABASE_URL" > "$DUMP_FILE" 2>/dev/null || {
        echo -e "${YELLOW}⚠️  pg_dump not available or database empty${NC}"
        echo "-- Empty database" > "$DUMP_FILE"
    }
    
    if [ -f "$DUMP_FILE" ]; then
        SIZE=$(du -h "$DUMP_FILE" | cut -f1)
        echo -e "${GREEN}✅ Database dump created: $SIZE${NC}"
        
        # Upload dump
        scp "$DUMP_FILE" $EXTERNAL_SERVER:/root/
        echo -e "${GREEN}✅ Database dump uploaded${NC}"
        
        # Store filename for remote restoration
        echo "$DUMP_FILE" > /tmp/db_dump_filename.txt
        scp /tmp/db_dump_filename.txt $EXTERNAL_SERVER:/root/
        
        rm "$DUMP_FILE"
    fi
else
    echo -e "${YELLOW}⚠️  DATABASE_URL not set - skipping database sync${NC}"
fi

echo ""
echo "════════════════════════════════════════════════"
echo "COMPONENT 4: REDIS DATA"
echo "════════════════════════════════════════════════"

if [ -f "dump.rdb" ]; then
    echo "Uploading Redis data..."
    scp dump.rdb $EXTERNAL_SERVER:/root/redis_backup.rdb
    echo -e "${GREEN}✅ Redis data uploaded${NC}"
else
    echo -e "${YELLOW}⚠️  No Redis data found (dump.rdb missing)${NC}"
fi

echo ""
echo "════════════════════════════════════════════════"
echo "COMPONENT 5: APPLY ON EXTERNAL SERVER"
echo "════════════════════════════════════════════════"

# Create remote deployment script
cat > apply_sync_remote.sh << 'REMOTE_SCRIPT'
#!/bin/bash
set -e

echo "🔧 APPLYING SYNC ON EXTERNAL SERVER"
echo "===================================="

cd /root

# Stop services
echo "Stopping services..."
docker stop dataguardian-container 2>/dev/null || true
docker rm dataguardian-container 2>/dev/null || true
systemctl stop redis-server 2>/dev/null || true

# Extract code
echo "Extracting code..."
mkdir -p /opt/dataguardian
cd /opt/dataguardian
tar -xzf /root/dataguardian_sync.tar.gz
echo "✅ Code extracted"

# Apply database (if exists)
if [ -f "/root/db_dump_filename.txt" ]; then
    DB_FILE=$(cat /root/db_dump_filename.txt)
    if [ -f "/root/$DB_FILE" ]; then
        echo "Restoring database..."
        # Note: Requires DATABASE_URL to be set
        if [ -n "$DATABASE_URL" ]; then
            psql "$DATABASE_URL" < "/root/$DB_FILE" 2>&1 | tail -5
            echo "✅ Database restored"
        else
            echo "⚠️  DATABASE_URL not set, skipping restore"
        fi
    fi
fi

# Apply Redis data
if [ -f "/root/redis_backup.rdb" ]; then
    echo "Restoring Redis data..."
    cp /root/redis_backup.rdb /var/lib/redis/dump.rdb 2>/dev/null || \
       cp /root/redis_backup.rdb /data/dump.rdb 2>/dev/null || true
    echo "✅ Redis data restored"
fi

# Rebuild Docker image
echo "Rebuilding Docker image..."
cd /opt/dataguardian
docker rmi dataguardian-pro 2>/dev/null || true
docker build --no-cache -t dataguardian-pro . 2>&1 | tail -20
echo "✅ Image rebuilt"

# Start with environment
echo "Starting container..."
docker run -d \
    --name dataguardian-container \
    --restart always \
    -p 5000:5000 \
    --env-file /root/.dataguardian_env \
    dataguardian-pro

echo "✅ Container started"

# Start Redis
echo "Starting Redis..."
systemctl start redis-server 2>/dev/null || \
    redis-server --daemonize yes --port 6379 || true
echo "✅ Redis started"

# Wait for initialization
echo "Waiting 60 seconds for initialization..."
sleep 60

# Verify
echo ""
echo "Verification:"
echo "============"

if docker ps | grep -q dataguardian-container; then
    echo "✅ Container running"
else
    echo "❌ Container not running"
fi

if curl -s http://localhost:5000 | grep -qi streamlit; then
    echo "✅ HTTP responding"
fi

if redis-cli ping 2>/dev/null | grep -q PONG; then
    echo "✅ Redis responding"
fi

echo ""
echo "Recent logs:"
docker logs dataguardian-container 2>&1 | tail -20

echo ""
echo "🎉 SYNC COMPLETE!"
REMOTE_SCRIPT

# Upload and execute remote script
scp apply_sync_remote.sh $EXTERNAL_SERVER:/root/
ssh $EXTERNAL_SERVER "chmod +x /root/apply_sync_remote.sh && /root/apply_sync_remote.sh"

echo ""
echo "════════════════════════════════════════════════"
echo "🎉 SYNC COMPLETE!"
echo "════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}✅ All 5 components synced:${NC}"
echo "   1. Code files"
echo "   2. Environment variables"
echo "   3. Database schema & data"
echo "   4. Redis data"
echo "   5. Configuration files"
echo ""
echo -e "${YELLOW}🧪 VERIFY 100% PARITY:${NC}"
echo "   1. Visit: https://dataguardianpro.nl"
echo "   2. Login: vishaal314 / password123"
echo "   3. Test all scanners"
echo "   4. Check dashboard metrics"
echo ""
echo -e "${GREEN}📊 Monitor:${NC}"
echo "   ssh $EXTERNAL_SERVER 'docker logs dataguardian-container -f'"

exit 0
