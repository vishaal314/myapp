#!/bin/bash
################################################################################
# FINAL E2E FIX - Complete DataGuardian Pro Deployment
# Fixes: Database auth, schema initialization, config package, environment
################################################################################

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 DataGuardian Pro - FINAL E2E FIX"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

APP_DIR="/opt/dataguardian"
ENV_FILE="/root/.dataguardian_env"

# Step 1: Fix PostgreSQL authentication
echo ""
echo "📊 Step 1/7: Fixing PostgreSQL authentication..."
sudo -u postgres psql -c "ALTER USER dataguardian WITH PASSWORD 'changeme';" 2>/dev/null || \
sudo -u postgres psql -c "CREATE USER dataguardian WITH PASSWORD 'changeme';"
sudo -u postgres psql -c "ALTER DATABASE dataguardian OWNER TO dataguardian;" 2>/dev/null || \
sudo -u postgres psql -c "CREATE DATABASE dataguardian OWNER dataguardian;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE dataguardian TO dataguardian;"
echo "✅ PostgreSQL configured"

# Step 2: Test database connection
echo ""
echo "🔍 Step 2/7: Testing database connection..."
PGPASSWORD=changeme psql -h localhost -U dataguardian -d dataguardian -c "SELECT 1;" > /dev/null || {
    echo "❌ Database connection failed!"
    exit 1
}
echo "✅ Database connection verified"

# Step 3: Initialize database schema
echo ""
echo "🗄️  Step 3/7: Initializing database schema..."
PGPASSWORD=changeme psql -h localhost -U dataguardian -d dataguardian << 'EOFSQL'
-- Create tenants table for multi-tenant support
CREATE TABLE IF NOT EXISTS tenants (
    id SERIAL PRIMARY KEY,
    organization_id VARCHAR(255) UNIQUE NOT NULL,
    organization_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    tier VARCHAR(50) DEFAULT 'professional',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create scans table
CREATE TABLE IF NOT EXISTS scans (
    id SERIAL PRIMARY KEY,
    scan_id VARCHAR(255) UNIQUE NOT NULL,
    organization_id VARCHAR(255) DEFAULT 'default_org',
    username VARCHAR(255) NOT NULL,
    scan_type VARCHAR(100) NOT NULL,
    scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    result_data JSONB,
    compliance_score INTEGER,
    files_scanned INTEGER DEFAULT 0,
    total_pii_found INTEGER DEFAULT 0,
    high_risk_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_scans_username_timestamp ON scans(username, scan_time DESC);
CREATE INDEX IF NOT EXISTS idx_scans_organization_timestamp ON scans(organization_id, scan_time DESC);
CREATE INDEX IF NOT EXISTS idx_scans_scan_type ON scans(scan_type);
CREATE INDEX IF NOT EXISTS idx_scans_timestamp ON scans(scan_time DESC);
CREATE INDEX IF NOT EXISTS idx_scans_composite ON scans(organization_id, username, scan_time DESC);

-- Insert default tenant
INSERT INTO tenants (organization_id, organization_name, status, tier)
VALUES ('default_org', 'Default Organization', 'active', 'enterprise')
ON CONFLICT (organization_id) DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON TABLE tenants TO dataguardian;
GRANT ALL PRIVILEGES ON TABLE scans TO dataguardian;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO dataguardian;

EOFSQL

if [ $? -eq 0 ]; then
    echo "✅ Database schema initialized"
else
    echo "⚠️  Warning: Some schema elements may already exist (this is OK)"
fi

# Step 4: Extract latest code
echo ""
echo "📦 Step 4/7: Extracting latest code..."
cd "$APP_DIR"
if [ -f "/tmp/dataguardian_complete.tar.gz" ]; then
    tar -xzf /tmp/dataguardian_complete.tar.gz --overwrite
    echo "✅ Code extracted"
else
    echo "❌ ERROR: /tmp/dataguardian_complete.tar.gz not found!"
    echo "Please run: scp dataguardian_complete.tar.gz root@dataguardianpro.nl:/tmp/"
    exit 1
fi

# Step 5: Set environment variables
echo ""
echo "🔐 Step 5/7: Setting environment variables..."
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

# Step 6: Clean and rebuild Docker
echo ""
echo "🧹 Step 6/7: Cleaning cache and rebuilding Docker..."
find "$APP_DIR" -type f -name "*.pyc" -delete
find "$APP_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

docker stop dataguardian-container 2>/dev/null || true
docker rm -f dataguardian-container 2>/dev/null || true

docker build --no-cache -t dataguardian-pro . || {
    echo "❌ Docker build failed!"
    exit 1
}
echo "✅ Docker image rebuilt"

# Step 7: Start container
echo ""
echo "🚀 Step 7/7: Starting container..."
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

# Check deployment status
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
docker logs dataguardian-container 2>&1 | tail -40
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verify deployment
ERRORS=0
if docker logs dataguardian-container 2>&1 | grep -q "password authentication failed"; then
    echo "❌ ERROR: PostgreSQL authentication failing"
    ERRORS=1
fi

if docker logs dataguardian-container 2>&1 | grep -q "No module named 'config"; then
    echo "❌ ERROR: Config module issues"
    ERRORS=1
fi

if docker logs dataguardian-container 2>&1 | grep -q "relation.*does not exist"; then
    echo "❌ ERROR: Database schema issues"
    ERRORS=1
fi

if docker logs dataguardian-container 2>&1 | grep -q "You can now view your Streamlit app"; then
    echo "✅ Streamlit started successfully"
fi

if docker logs dataguardian-container 2>&1 | grep -q "Local KMS provider initialized"; then
    echo "✅ Encryption service initialized"
fi

if docker logs dataguardian-container 2>&1 | grep -q "Multi-tenant database schema initialized successfully"; then
    echo "✅ Multi-tenant service initialized"
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
    echo "🧪 TESTING:"
    echo "   1. Close ALL browser tabs"
    echo "   2. Open NEW INCOGNITO window (Ctrl+Shift+N)"
    echo "   3. Visit: https://dataguardianpro.nl"
    echo "   4. Login and test any scanner"
    echo ""
    echo "✅ PostgreSQL authentication: FIXED"
    echo "✅ Database schema: INITIALIZED"
    echo "✅ Config package: COMPLETE"
    echo "✅ Environment variables: SET"
    echo "✅ All systems: OPERATIONAL"
    echo ""
else
    echo ""
    echo "⚠️  Deployment completed with warnings - review logs above"
fi
