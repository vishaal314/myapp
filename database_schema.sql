-- Complete DataGuardian Pro Database Schema
-- This replicates the exact database structure from Replit

-- Core tables matching Replit environment
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

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

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    log_id TEXT PRIMARY KEY,
    username TEXT,
    action TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details JSONB,
    organization_id VARCHAR(255)
);

-- Compliance scores table
CREATE TABLE IF NOT EXISTS compliance_scores (
    score_id TEXT PRIMARY KEY,
    username TEXT,
    repo_name TEXT,
    scan_id TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    overall_score INTEGER,
    principle_scores JSONB
);

-- Data minimization table
CREATE TABLE IF NOT EXISTS data_minimization (
    id SERIAL PRIMARY KEY,
    scan_id TEXT,
    pii_type TEXT,
    location TEXT,
    file_name TEXT,
    is_excessive BOOLEAN,
    is_unused BOOLEAN,
    reason TEXT,
    flagged_by TEXT,
    flagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data accuracy table
CREATE TABLE IF NOT EXISTS data_accuracy (
    id SERIAL PRIMARY KEY,
    scan_id TEXT,
    pii_type TEXT,
    location TEXT,
    is_verified BOOLEAN,
    is_current BOOLEAN,
    verification_method TEXT,
    verified_by TEXT,
    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- Data purposes table
CREATE TABLE IF NOT EXISTS data_purposes (
    purpose_id TEXT PRIMARY KEY,
    name TEXT,
    description TEXT,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT TRUE
);

-- GDPR principles table
CREATE TABLE IF NOT EXISTS gdpr_principles (
    principle_id TEXT PRIMARY KEY,
    name TEXT,
    description TEXT,
    article TEXT
);

-- DPIA assessments table
CREATE TABLE IF NOT EXISTS nl_dpia_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id VARCHAR(255),
    user_id VARCHAR(255),
    organization_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(255)
);

-- PII types table
CREATE TABLE IF NOT EXISTS pii_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    pattern TEXT,
    description TEXT,
    risk_level VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Storage policies table
CREATE TABLE IF NOT EXISTS storage_policies (
    id SERIAL PRIMARY KEY,
    policy_name VARCHAR(255) NOT NULL,
    retention_period INTEGER,
    deletion_method VARCHAR(100),
    encryption_required BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Region rules table
CREATE TABLE IF NOT EXISTS region_rules (
    id SERIAL PRIMARY KEY,
    region VARCHAR(100) NOT NULL,
    regulation VARCHAR(100),
    penalty_multiplier DECIMAL(3,2) DEFAULT 1.0,
    specific_rules JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User sessions table
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    data JSONB
);

-- Simple DPIA assessments table
CREATE TABLE IF NOT EXISTS simple_dpia_assessments (
    id SERIAL PRIMARY KEY,
    assessment_id VARCHAR(255) UNIQUE,
    user_data JSONB,
    risk_assessment JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User settings table
CREATE TABLE IF NOT EXISTS user_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    setting_key VARCHAR(255),
    setting_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tenants table
CREATE TABLE IF NOT EXISTS tenants (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    domain VARCHAR(255),
    settings JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tenant usage table
CREATE TABLE IF NOT EXISTS tenant_usage (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255),
    usage_type VARCHAR(100),
    usage_count INTEGER DEFAULT 0,
    usage_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data for testing
INSERT INTO pii_types (name, pattern, description, risk_level) VALUES
('Email', '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', 'Email addresses', 'medium'),
('Phone', '\+?[1-9]\d{1,14}', 'Phone numbers', 'medium'),
('BSN', '\d{9}', 'Dutch BSN numbers', 'high'),
('Credit Card', '\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}', 'Credit card numbers', 'high'),
('IBAN', '[A-Z]{2}[0-9]{2}[A-Z0-9]{4}[0-9]{7}([A-Z0-9]?){0,16}', 'International Bank Account Number', 'high')
ON CONFLICT (name) DO NOTHING;

INSERT INTO gdpr_principles (principle_id, name, description, article) VALUES
('lawfulness', 'Lawfulness', 'Processing must have a legal basis', 'Art. 6'),
('purpose_limitation', 'Purpose Limitation', 'Data collected for specified purposes', 'Art. 5(1)(b)'),
('data_minimisation', 'Data Minimisation', 'Adequate, relevant and limited to what is necessary', 'Art. 5(1)(c)'),
('accuracy', 'Accuracy', 'Data must be accurate and kept up to date', 'Art. 5(1)(d)'),
('storage_limitation', 'Storage Limitation', 'Data kept no longer than necessary', 'Art. 5(1)(e)'),
('integrity_confidentiality', 'Integrity and Confidentiality', 'Appropriate security measures', 'Art. 5(1)(f)')
ON CONFLICT (principle_id) DO NOTHING;

INSERT INTO region_rules (region, regulation, penalty_multiplier, specific_rules) VALUES
('Netherlands', 'UAVG', 1.2, '{"data_protection_authority": "Autoriteit Persoonsgegevens", "notification_required": true}'),
('Germany', 'DSGVO', 1.1, '{"data_protection_authority": "BfDI", "notification_required": true}'),
('Belgium', 'AVG/RGPD', 1.0, '{"data_protection_authority": "APD/DPA", "notification_required": true}')
ON CONFLICT (region) DO NOTHING;

-- Insert test scan data
INSERT INTO scans (scan_id, username, scan_type, region, file_count, total_pii_found, high_risk_count, result) VALUES
('test_scan_001', 'admin', 'code', 'Netherlands', 25, 15, 3, '{"status": "completed", "findings": ["email addresses", "phone numbers"]}'),
('test_scan_002', 'admin', 'database', 'Netherlands', 10, 8, 2, '{"status": "completed", "findings": ["BSN numbers", "credit cards"]}')
ON CONFLICT (scan_id) DO NOTHING;