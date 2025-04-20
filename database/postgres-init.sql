-- PostgreSQL Database schema for GDPR Scan Engine

-- Scans table
CREATE TABLE IF NOT EXISTS scans (
    scan_id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    scan_type TEXT NOT NULL,
    region TEXT NOT NULL,
    file_count INTEGER NOT NULL,
    total_pii_found INTEGER NOT NULL,
    high_risk_count INTEGER NOT NULL,
    result_json JSONB NOT NULL
);

-- Users table (for authentication)
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    email TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login TIMESTAMP
);

-- Insert default users (default password 'password' with SHA-512 hash)
INSERT INTO users (username, password_hash, role, email, created_at)
VALUES 
    ('admin', 'c7ad44cbad762a5da0a452f9e854fdc1e0e7a52a38015f23f3eab1d80b931dd472634dfac71cd34ebc35d16ab7fb8a90c81f975113d6c7538dc69dd8de9077ec', 'admin', 'admin@example.com', NOW()),
    ('analyst', '5d5c7688b2c180ae159459219a14f016f07b471792e36d77a842894d5100aeaaa53edad7c28238ce2863207bedcfb6515c832581d6a2e99d8ab14a1f6b3c98c5', 'analyst', 'analyst@example.com', NOW()),
    ('viewer', 'ee79976c9380d5e337fc1c095ece8c8f22f91f306ceeb161fa51fecede2c4ba1d0b2e187f9e44873de3ea6a44899d6ebb97a33ea95f4b645de017cfdf9ee9cd0', 'viewer', 'viewer@example.com', NOW())
ON CONFLICT (username) DO NOTHING;

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    log_id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    action TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    details JSONB
);

-- PII types reference table
CREATE TABLE IF NOT EXISTS pii_types (
    type_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    risk_level TEXT NOT NULL,
    category TEXT,
    requires_consent BOOLEAN NOT NULL
);

-- Insert standard PII types
INSERT INTO pii_types (type_id, name, description, risk_level, category, requires_consent)
VALUES
    ('bsn', 'BSN', 'Dutch citizen service number', 'High', 'National ID', true),
    ('email', 'Email', 'Email address', 'Low', 'Contact', true),
    ('phone', 'Phone', 'Phone number', 'Medium', 'Contact', true),
    ('address', 'Address', 'Physical address', 'Medium', 'Contact', true),
    ('name', 'Name', 'Personal name', 'Low', 'Identity', true),
    ('credit_card', 'Credit Card', 'Credit card number', 'High', 'Financial', true),
    ('ip_address', 'IP Address', 'Internet Protocol address', 'Low', 'Technical', true),
    ('dob', 'Date of Birth', 'Date of birth', 'Medium', 'Identity', true),
    ('passport', 'Passport Number', 'Passport identification number', 'High', 'National ID', true),
    ('medical', 'Medical Data', 'Health-related information', 'High', 'Special Category', true),
    ('financial', 'Financial Data', 'Bank details, account numbers', 'High', 'Financial', true),
    ('username', 'Username', 'System username', 'Low', 'Technical', true),
    ('password', 'Password', 'System password', 'High', 'Technical', true)
ON CONFLICT (type_id) DO NOTHING;

-- Region-specific rules table
CREATE TABLE IF NOT EXISTS region_rules (
    region_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    minor_age_limit INTEGER NOT NULL,
    breach_notification_hours INTEGER NOT NULL,
    special_requirements TEXT
);

-- Insert region data
INSERT INTO region_rules (region_id, name, minor_age_limit, breach_notification_hours, special_requirements)
VALUES
    ('NL', 'Netherlands', 16, 72, 'Special rules for BSN, medical data. Must follow UAVG.'),
    ('DE', 'Germany', 16, 72, 'Strict rules for data minimization. Must follow BDSG.'),
    ('FR', 'France', 15, 72, 'Special rules for minor data.'),
    ('BE', 'Belgium', 13, 72, 'Special rules for processing activities.')
ON CONFLICT (region_id) DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_scans_username ON scans (username);
CREATE INDEX IF NOT EXISTS idx_scans_timestamp ON scans (timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_log_username ON audit_log (username);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log (timestamp);

-- Set proper permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dataguardian;