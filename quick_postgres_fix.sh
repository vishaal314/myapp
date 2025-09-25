#!/bin/bash
# Quick PostgreSQL Fix

echo "🔧 Quick PostgreSQL Fix"
echo "======================="

# Stop everything
docker-compose down

# Force use alternative port
echo "🔄 Using PostgreSQL port 5433 to avoid conflicts..."

# Update docker-compose.yml to use port 5433
sed -i 's/"5432:5432"/"5433:5432"/g' docker-compose.yml
sed -i 's/"$POSTGRES_PORT:5432"/"5433:5432"/g' docker-compose.yml

# Update .env file
echo "POSTGRES_PORT=5433" > .env
echo "REDIS_PORT=6379" >> .env

# Simplified database schema (remove potential problematic parts)
cat > database_schema.sql << 'EOF'
-- Basic DataGuardian Pro Database Schema

-- Main scans table
CREATE TABLE IF NOT EXISTS scans (
    id SERIAL PRIMARY KEY,
    scan_id VARCHAR(255) UNIQUE,
    username VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scan_type VARCHAR(100),
    region VARCHAR(50),
    file_count INTEGER DEFAULT 0,
    total_pii_found INTEGER DEFAULT 0,
    high_risk_count INTEGER DEFAULT 0,
    result JSONB
);

-- Insert test data
INSERT INTO scans (scan_id, username, scan_type, region, file_count, total_pii_found, high_risk_count) VALUES
('test_scan_001', 'admin', 'code', 'Netherlands', 25, 15, 3)
ON CONFLICT (scan_id) DO NOTHING;
EOF

echo "✅ PostgreSQL configuration updated to port 5433"
echo "✅ Simplified database schema created"
echo ""
echo "🚀 Now run: docker-compose up -d"