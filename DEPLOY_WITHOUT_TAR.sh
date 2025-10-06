#!/bin/bash
################################################################################
# DEPLOY WITHOUT TAR - Direct Server Deployment
# No tar.gz needed - creates minimal working deployment
################################################################################

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 DataGuardian Pro - Direct Deployment (No tar.gz)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

APP_DIR="/opt/dataguardian"
ENV_FILE="/root/.dataguardian_env"

# Step 1: Fix PostgreSQL
echo ""
echo "📊 Step 1/5: Fixing PostgreSQL..."
sudo -u postgres psql -c "ALTER USER dataguardian WITH PASSWORD 'changeme';" 2>/dev/null || \
sudo -u postgres psql -c "CREATE USER dataguardian WITH PASSWORD 'changeme';"
sudo -u postgres psql -c "ALTER DATABASE dataguardian OWNER TO dataguardian;" 2>/dev/null || \
sudo -u postgres psql -c "CREATE DATABASE dataguardian OWNER dataguardian;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE dataguardian TO dataguardian;"
echo "✅ PostgreSQL configured"

# Step 2: Initialize database schema
echo ""
echo "🗄️  Step 2/5: Initializing database schema..."
PGPASSWORD=changeme psql -h localhost -U dataguardian -d dataguardian << 'EOFSQL'
CREATE TABLE IF NOT EXISTS tenants (
    id SERIAL PRIMARY KEY,
    organization_id VARCHAR(255) UNIQUE NOT NULL,
    organization_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    tier VARCHAR(50) DEFAULT 'professional',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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

CREATE INDEX IF NOT EXISTS idx_scans_username_timestamp ON scans(username, scan_time DESC);
CREATE INDEX IF NOT EXISTS idx_scans_organization_timestamp ON scans(organization_id, scan_time DESC);
CREATE INDEX IF NOT EXISTS idx_scans_scan_type ON scans(scan_type);
CREATE INDEX IF NOT EXISTS idx_scans_timestamp ON scans(scan_time DESC);
CREATE INDEX IF NOT EXISTS idx_scans_composite ON scans(organization_id, username, scan_time DESC);

INSERT INTO tenants (organization_id, organization_name, status, tier)
VALUES ('default_org', 'Default Organization', 'active', 'enterprise')
ON CONFLICT (organization_id) DO NOTHING;

GRANT ALL PRIVILEGES ON TABLE tenants TO dataguardian;
GRANT ALL PRIVILEGES ON TABLE scans TO dataguardian;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO dataguardian;
EOFSQL
echo "✅ Database schema initialized"

# Step 3: Environment variables
echo ""
echo "🔐 Step 3/5: Setting environment..."
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

# Step 4: Rebuild Docker
echo ""
echo "🐳 Step 4/5: Rebuilding Docker..."
cd "$APP_DIR"
docker stop dataguardian-container 2>/dev/null || true
docker rm -f dataguardian-container 2>/dev/null || true
docker build --no-cache -t dataguardian-pro .
echo "✅ Docker rebuilt"

# Step 5: Start container
echo ""
echo "🚀 Step 5/5: Starting container..."
docker run -d \
    --name dataguardian-container \
    --restart always \
    --network host \
    --env-file "$ENV_FILE" \
    dataguardian-pro

sleep 30

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 DEPLOYMENT STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker ps | grep dataguardian-container && echo "✅ Container RUNNING" || echo "❌ Container FAILED"
echo ""
echo "📋 Recent Logs:"
docker logs dataguardian-container 2>&1 | tail -40
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Application: https://dataguardianpro.nl"
echo "👤 Login: vishaal314 / vishaal2024"
