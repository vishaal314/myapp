#!/bin/bash
################################################################################
# FINAL E2E FIX - Complete DataGuardian Pro Deployment
# Fixes: Database auth, config package, all imports, environment variables
################################################################################

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 DataGuardian Pro - FINAL E2E FIX"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

APP_DIR="/opt/dataguardian"
ENV_FILE="/root/.dataguardian_env"

# Step 1: Fix PostgreSQL
echo ""
echo "📊 Step 1/6: Fixing PostgreSQL authentication..."
sudo -u postgres psql -c "ALTER USER dataguardian WITH PASSWORD 'changeme';" 2>/dev/null || \
sudo -u postgres psql -c "CREATE USER dataguardian WITH PASSWORD 'changeme';"
sudo -u postgres psql -c "ALTER DATABASE dataguardian OWNER TO dataguardian;" 2>/dev/null || \
sudo -u postgres psql -c "CREATE DATABASE dataguardian OWNER dataguardian;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE dataguardian TO dataguardian;"
echo "✅ PostgreSQL configured"

# Step 2: Test database
echo ""
echo "🔍 Step 2/6: Testing database connection..."
PGPASSWORD=changeme psql -h localhost -U dataguardian -d dataguardian -c "SELECT 1;" > /dev/null || {
    echo "❌ Database connection failed!"
    exit 1
}
echo "✅ Database connection verified"

# Step 3: Extract code
echo ""
echo "📦 Step 3/6: Extracting latest code..."
cd "$APP_DIR"
if [ -f "/tmp/dataguardian_complete.tar.gz" ]; then
    tar -xzf /tmp/dataguardian_complete.tar.gz --overwrite
    echo "✅ Code extracted"
else
    echo "❌ ERROR: /tmp/dataguardian_complete.tar.gz not found!"
    echo "Please run: scp dataguardian_complete.tar.gz root@dataguardianpro.nl:/tmp/"
    exit 1
fi

# Step 4: Environment variables
echo ""
echo "🔐 Step 4/6: Setting environment variables..."
MASTER_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

cat > "$ENV_FILE" << EOF
DATAGUARDIAN_MASTER_KEY=$MASTER_KEY
JWT_SECRET=$JWT_SECRET
DATABASE_URL=postgresql://dataguardian:changeme@localhost:5432/dataguardian
PGHOST=localhost
PGPORT=5432
PGDATABASE=dataguardian
PGUSER=dataguardian
PGPASSWORD=changeme
REDIS_HOST=localhost
REDIS_PORT=6379
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=False
EOF
chmod 600 "$ENV_FILE"
echo "✅ Environment configured"

# Step 5: Clean and rebuild
echo ""
echo "🧹 Step 5/6: Cleaning cache and rebuilding..."
find "$APP_DIR" -type f -name "*.pyc" -delete
find "$APP_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

docker stop dataguardian-container 2>/dev/null || true
docker rm -f dataguardian-container 2>/dev/null || true

docker build --no-cache -t dataguardian-pro . || {
    echo "❌ Docker build failed!"
    exit 1
}
echo "✅ Docker image rebuilt"

# Step 6: Start container
echo ""
echo "🚀 Step 6/6: Starting container..."
docker run -d \
    --name dataguardian-container \
    --restart always \
    --network host \
    --env-file "$ENV_FILE" \
    dataguardian-pro

echo "✅ Container started"
echo ""
echo "⏳ Waiting 30 seconds for initialization..."
sleep 30

# Check status
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 DEPLOYMENT STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if docker ps | grep -q dataguardian-container; then
    echo "✅ Container: RUNNING"
else
    echo "❌ Container: FAILED"
    docker logs dataguardian-container 2>&1 | tail -30
    exit 1
fi

echo ""
echo "📋 Recent Logs:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker logs dataguardian-container 2>&1 | tail -30
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verify no critical errors
ERRORS=0
if docker logs dataguardian-container 2>&1 | grep -q "password authentication failed"; then
    echo "❌ ERROR: PostgreSQL authentication still failing"
    ERRORS=1
fi

if docker logs dataguardian-container 2>&1 | grep -q "No module named 'config"; then
    echo "❌ ERROR: Config module issues detected"
    ERRORS=1
fi

if docker logs dataguardian-container 2>&1 | grep -q "safe mode"; then
    echo "⚠️  WARNING: Application may be in safe mode"
    ERRORS=1
fi

if [ $ERRORS -eq 0 ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎉 DEPLOYMENT SUCCESSFUL!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🌐 Application: https://dataguardianpro.nl"
    echo "👤 Login: vishaal314 / vishaal2024"
    echo ""
    echo "🧪 TEST:"
    echo "   1. Open INCOGNITO browser"
    echo "   2. Visit https://dataguardianpro.nl"
    echo "   3. Login and test scanners"
    echo ""
    echo "✅ All systems operational!"
else
    echo ""
    echo "⚠️  Deployment completed with warnings - check logs above"
fi
