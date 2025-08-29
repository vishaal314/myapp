-- DataGuardian Pro Database Initialization
-- This script sets up the initial database structure

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS dataguardian;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS audit;

-- Set default schema
SET search_path TO dataguardian, public;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    organization VARCHAR(255),
    department VARCHAR(255),
    country VARCHAR(10) DEFAULT 'NL',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    license_tier VARCHAR(50) DEFAULT 'basic'
);

-- Scan results table
CREATE TABLE IF NOT EXISTS scan_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    scan_type VARCHAR(100) NOT NULL,
    source_type VARCHAR(100) NOT NULL,
    source_path TEXT,
    findings_count INTEGER DEFAULT 0,
    compliance_score DECIMAL(5,2),
    risk_level VARCHAR(20),
    scan_status VARCHAR(50) DEFAULT 'completed',
    findings JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Compliance certificates table
CREATE TABLE IF NOT EXISTS compliance_certificates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    certificate_type VARCHAR(100) NOT NULL,
    certificate_data JSONB NOT NULL,
    issue_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expiry_date TIMESTAMP WITH TIME ZONE,
    is_valid BOOLEAN DEFAULT true,
    verification_code VARCHAR(255) UNIQUE,
    payment_status VARCHAR(50) DEFAULT 'pending'
);

-- License usage tracking
CREATE TABLE IF NOT EXISTS license_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    action_type VARCHAR(100) NOT NULL,
    resource_count INTEGER DEFAULT 1,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Activity logs (audit schema)
CREATE TABLE IF NOT EXISTS audit.activity_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    ip_address INET,
    user_agent TEXT,
    details JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Analytics data (analytics schema)
CREATE TABLE IF NOT EXISTS analytics.usage_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_type VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4),
    dimensions JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    date_key DATE DEFAULT CURRENT_DATE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_organization ON users(organization);
CREATE INDEX IF NOT EXISTS idx_scan_results_user_id ON scan_results(user_id);
CREATE INDEX IF NOT EXISTS idx_scan_results_type ON scan_results(scan_type);
CREATE INDEX IF NOT EXISTS idx_scan_results_created ON scan_results(created_at);
CREATE INDEX IF NOT EXISTS idx_certificates_user_id ON compliance_certificates(user_id);
CREATE INDEX IF NOT EXISTS idx_certificates_type ON compliance_certificates(certificate_type);
CREATE INDEX IF NOT EXISTS idx_license_usage_user_id ON license_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_license_usage_timestamp ON license_usage(timestamp);
CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id ON audit.activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_timestamp ON audit.activity_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_usage_metrics_type ON analytics.usage_metrics(metric_type);
CREATE INDEX IF NOT EXISTS idx_usage_metrics_date ON analytics.usage_metrics(date_key);

-- Create default admin user (password: admin123 - change in production)
INSERT INTO users (username, email, password_hash, role, organization, country) 
VALUES (
    'admin',
    'admin@dataguardian.nl',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj1q8L9Y2bj6', -- admin123
    'admin',
    'DataGuardian Pro',
    'NL'
) ON CONFLICT (email) DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA dataguardian TO dataguardian;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA analytics TO dataguardian;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA audit TO dataguardian;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA dataguardian TO dataguardian;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA analytics TO dataguardian;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA audit TO dataguardian;