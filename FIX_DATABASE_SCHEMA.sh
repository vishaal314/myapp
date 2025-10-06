#!/bin/bash
################################################################################
# FIX DATABASE SCHEMA - Complete schema rebuild
################################################################################

set -e

echo "🗄️  Fixing database schema completely..."
echo ""

# Drop and recreate ALL tables with complete schema
PGPASSWORD=changeme psql -h localhost -U dataguardian -d dataguardian << 'EOFSQL'
-- Drop existing tables
DROP TABLE IF EXISTS scans CASCADE;
DROP TABLE IF EXISTS tenants CASCADE;
DROP TABLE IF EXISTS audit_log CASCADE;

-- Create tenants table with ALL required columns
CREATE TABLE tenants (
    id SERIAL PRIMARY KEY,
    organization_id VARCHAR(255) UNIQUE NOT NULL,
    organization_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    tier VARCHAR(50) DEFAULT 'professional',
    max_users INTEGER DEFAULT 10,
    max_scans_per_month INTEGER DEFAULT 1000,
    features JSONB DEFAULT '[]'::jsonb,
    subscription_status VARCHAR(50) DEFAULT 'active',
    subscription_end_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create scans table with ALL required columns
CREATE TABLE scans (
    id SERIAL PRIMARY KEY,
    scan_id VARCHAR(255) UNIQUE NOT NULL,
    organization_id VARCHAR(255) DEFAULT 'default_org',
    username VARCHAR(255) NOT NULL,
    scan_type VARCHAR(100) NOT NULL,
    scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    result_data JSONB,
    compliance_score INTEGER,
    files_scanned INTEGER DEFAULT 0,
    total_pii_found INTEGER DEFAULT 0,
    high_risk_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create audit_log table
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    organization_id VARCHAR(255) DEFAULT 'default_org',
    username VARCHAR(255),
    action VARCHAR(255),
    details JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create all indexes
CREATE INDEX idx_scans_username_timestamp ON scans(username, scan_time DESC);
CREATE INDEX idx_scans_organization_timestamp ON scans(organization_id, scan_time DESC);
CREATE INDEX idx_scans_scan_type ON scans(scan_type);
CREATE INDEX idx_scans_timestamp ON scans(scan_time DESC);
CREATE INDEX idx_scans_composite ON scans(organization_id, username, scan_time DESC);
CREATE INDEX idx_audit_org_timestamp ON audit_log(organization_id, timestamp DESC);

-- Insert default tenant with ALL fields
INSERT INTO tenants (
    organization_id, 
    organization_name, 
    status, 
    tier,
    max_users,
    max_scans_per_month,
    features,
    subscription_status
) VALUES (
    'default_org', 
    'Default Organization', 
    'active', 
    'enterprise',
    100,
    -1,
    '["unlimited_scans", "priority_support", "custom_integrations", "api_access"]'::jsonb,
    'active'
);

-- Grant all permissions
GRANT ALL PRIVILEGES ON TABLE tenants TO dataguardian;
GRANT ALL PRIVILEGES ON TABLE scans TO dataguardian;
GRANT ALL PRIVILEGES ON TABLE audit_log TO dataguardian;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO dataguardian;

-- Verify tables
SELECT 'TENANTS TABLE:' as info;
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name = 'tenants' ORDER BY ordinal_position;

SELECT 'SCANS TABLE:' as info;
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name = 'scans' ORDER BY ordinal_position;

SELECT 'DEFAULT TENANT:' as info;
SELECT organization_id, organization_name, tier, max_users, max_scans_per_month 
FROM tenants WHERE organization_id = 'default_org';
EOFSQL

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database schema fixed successfully!"
    echo ""
    echo "🔄 Restarting container to apply changes..."
    docker restart dataguardian-container
    
    sleep 20
    
    echo ""
    echo "📊 Checking for database errors..."
    if docker logs dataguardian-container 2>&1 | tail -100 | grep -q "column.*does not exist"; then
        echo "❌ Still has column errors"
        docker logs dataguardian-container 2>&1 | grep "does not exist" | head -5
    else
        echo "✅ No column errors!"
    fi
    
    if docker logs dataguardian-container 2>&1 | tail -100 | grep -q "Access denied: Unknown organization default_org"; then
        echo "❌ Still has org access errors"
    else
        echo "✅ No organization errors!"
    fi
    
    echo ""
    echo "🌐 Application: https://dataguardianpro.nl"
    echo "   Test in INCOGNITO mode!"
else
    echo "❌ Database schema fix failed!"
    exit 1
fi
