-- Enterprise Feature Database Migration
-- Adds tables for DSAR, Consent Management, Audit Evidence, Vendor Risk, and Ticketing

-- DSAR Requests Table
CREATE TABLE IF NOT EXISTS enterprise_dsar_requests (
    id TEXT PRIMARY KEY,
    requester_email TEXT NOT NULL,
    requester_name TEXT,
    request_type TEXT NOT NULL CHECK (request_type IN ('access', 'rectification', 'erasure', 'portability', 'restriction', 'objection', 'automated_decision')),
    request_details TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'submitted' CHECK (status IN ('submitted', 'identity_verification', 'processing', 'data_collection', 'review', 'completed', 'rejected', 'expired')),
    submitted_at TEXT NOT NULL,
    due_date TEXT NOT NULL,
    identity_verified BOOLEAN DEFAULT FALSE,
    identity_documents TEXT,
    identity_verification_method TEXT,
    identity_verified_by TEXT,
    identity_verified_at TEXT,
    priority TEXT DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    region TEXT DEFAULT 'EU',
    user_id TEXT,
    session_id TEXT,
    source TEXT DEFAULT 'web',
    notes TEXT,
    status_notes TEXT,
    estimated_completion TEXT,
    response_data TEXT,
    data_sources TEXT,
    response_generated_at TEXT,
    completed_at TEXT,
    rejected_reason TEXT,
    updated_by TEXT,
    response_data_hash TEXT,
    identity_documents_hash TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Consent Records Table
CREATE TABLE IF NOT EXISTS enterprise_consent_records (
    id TEXT PRIMARY KEY,
    user_identifier TEXT NOT NULL,
    consent_type TEXT NOT NULL CHECK (consent_type IN ('marketing', 'analytics', 'functional', 'necessary', 'profiling', 'third_party')),
    status TEXT NOT NULL CHECK (status IN ('granted', 'withdrawn', 'expired', 'pending')),
    granted_at TEXT,
    withdrawn_at TEXT,
    expires_at TEXT,
    purpose TEXT,
    legal_basis TEXT DEFAULT 'consent',
    ip_address TEXT,
    user_agent TEXT,
    consent_evidence TEXT,
    withdrawal_method TEXT,
    region TEXT DEFAULT 'EU',
    version TEXT DEFAULT '1.0',
    source TEXT DEFAULT 'web',
    session_id TEXT,
    parent_consent_id TEXT,
    is_minor BOOLEAN DEFAULT FALSE,
    parental_consent BOOLEAN DEFAULT FALSE,
    consent_evidence_hash TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Audit Evidence Table
CREATE TABLE IF NOT EXISTS enterprise_audit_evidence (
    id TEXT PRIMARY KEY,
    evidence_type TEXT NOT NULL CHECK (evidence_type IN ('scan_result', 'compliance_report', 'security_log', 'access_log', 'configuration', 'policy_document', 'training_record', 'incident_report', 'dsar_record', 'consent_record', 'vendor_assessment')),
    evidence_data TEXT NOT NULL,
    source TEXT NOT NULL,
    metadata TEXT DEFAULT '{}',
    source_data TEXT,
    collection_method TEXT DEFAULT 'automated',
    collector_id TEXT DEFAULT 'system',
    retention_period_months INTEGER DEFAULT 84,
    control_objective TEXT,
    risk_level TEXT DEFAULT 'medium' CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    compliance_framework TEXT DEFAULT 'SOC2',
    region TEXT DEFAULT 'EU',
    scan_id TEXT,
    user_id TEXT,
    session_id TEXT,
    is_sensitive BOOLEAN DEFAULT FALSE,
    classification TEXT DEFAULT 'internal',
    tags TEXT,
    related_evidence_ids TEXT,
    expires_at TEXT,
    reviewed BOOLEAN DEFAULT FALSE,
    reviewer_id TEXT,
    review_notes TEXT,
    evidence_data_hash TEXT,
    metadata_hash TEXT,
    source_data_hash TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Vendor Assessments Table  
CREATE TABLE IF NOT EXISTS enterprise_vendor_assessments (
    id TEXT PRIMARY KEY,
    vendor_name TEXT NOT NULL,
    vendor_type TEXT NOT NULL,
    risk_level TEXT NOT NULL CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'pending_review', 'suspended', 'terminated', 'under_review')),
    contact_email TEXT,
    contact_phone TEXT,
    website TEXT,
    country TEXT,
    data_processing BOOLEAN DEFAULT FALSE,
    gdpr_compliant BOOLEAN,
    iso27001_certified BOOLEAN DEFAULT FALSE,
    soc2_certified BOOLEAN DEFAULT FALSE,
    contract_start_date TEXT,
    contract_end_date TEXT,
    contract_details TEXT,
    assessment_data TEXT DEFAULT '{}',
    assessment_notes TEXT,
    last_review_date TEXT,
    next_review_date TEXT,
    compliance_score INTEGER DEFAULT 0,
    security_score INTEGER DEFAULT 0,
    region TEXT DEFAULT 'EU',
    assessor_id TEXT,
    requires_dpa BOOLEAN DEFAULT FALSE,
    dpa_signed BOOLEAN DEFAULT FALSE,
    privacy_policy_reviewed BOOLEAN DEFAULT FALSE,
    subprocessors_identified BOOLEAN DEFAULT FALSE,
    incident_count INTEGER DEFAULT 0,
    last_incident_date TEXT,
    risk_update_reason TEXT,
    risk_updated_at TEXT,
    assessment_data_hash TEXT,
    contract_details_hash TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Enterprise Tickets Table
CREATE TABLE IF NOT EXISTS enterprise_tickets (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    ticket_type TEXT NOT NULL CHECK (ticket_type IN ('compliance_issue', 'security_finding', 'privacy_violation', 'dsar_request', 'vendor_risk', 'audit_finding', 'incident', 'maintenance')),
    priority TEXT NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'critical', 'urgent')),
    status TEXT DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved', 'closed', 'cancelled', 'reopened')),
    external_ticket_id TEXT,
    external_system TEXT,
    source_scan_id TEXT,
    source_event_id TEXT,
    source_data TEXT DEFAULT '{}',
    assigned_to TEXT,
    assignee_email TEXT,
    reporter_id TEXT,
    region TEXT DEFAULT 'EU',
    compliance_framework TEXT DEFAULT 'GDPR',
    risk_level TEXT DEFAULT 'medium',
    finding_type TEXT,
    affected_systems TEXT,
    estimated_effort TEXT,
    due_date TEXT,
    resolution_notes TEXT,
    internal_notes TEXT,
    tags TEXT,
    created_by_automation BOOLEAN DEFAULT FALSE,
    auto_close_eligible BOOLEAN DEFAULT FALSE,
    escalated BOOLEAN DEFAULT FALSE,
    escalation_date TEXT,
    resolved_at TEXT,
    closed_at TEXT,
    resolution_time_hours INTEGER,
    updated_by TEXT,
    status_updated_at TEXT,
    source_data_hash TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_dsar_status ON enterprise_dsar_requests(status);
CREATE INDEX IF NOT EXISTS idx_dsar_due_date ON enterprise_dsar_requests(due_date);
CREATE INDEX IF NOT EXISTS idx_dsar_user_id ON enterprise_dsar_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_dsar_region ON enterprise_dsar_requests(region);

CREATE INDEX IF NOT EXISTS idx_consent_user ON enterprise_consent_records(user_identifier);
CREATE INDEX IF NOT EXISTS idx_consent_type ON enterprise_consent_records(consent_type);
CREATE INDEX IF NOT EXISTS idx_consent_status ON enterprise_consent_records(status);

CREATE INDEX IF NOT EXISTS idx_evidence_type ON enterprise_audit_evidence(evidence_type);
CREATE INDEX IF NOT EXISTS idx_evidence_scan ON enterprise_audit_evidence(scan_id);
CREATE INDEX IF NOT EXISTS idx_evidence_framework ON enterprise_audit_evidence(compliance_framework);

CREATE INDEX IF NOT EXISTS idx_vendor_risk ON enterprise_vendor_assessments(risk_level);
CREATE INDEX IF NOT EXISTS idx_vendor_status ON enterprise_vendor_assessments(status);
CREATE INDEX IF NOT EXISTS idx_vendor_compliance ON enterprise_vendor_assessments(gdpr_compliant);

CREATE INDEX IF NOT EXISTS idx_ticket_status ON enterprise_tickets(status);
CREATE INDEX IF NOT EXISTS idx_ticket_priority ON enterprise_tickets(priority);
CREATE INDEX IF NOT EXISTS idx_ticket_scan ON enterprise_tickets(source_scan_id);
CREATE INDEX IF NOT EXISTS idx_ticket_assigned ON enterprise_tickets(assigned_to);

-- Insert initial data for compliance frameworks reference
CREATE TABLE IF NOT EXISTS compliance_frameworks (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    region TEXT,
    version TEXT DEFAULT '1.0',
    mandatory_retention_years INTEGER,
    created_at TEXT NOT NULL
);

INSERT OR IGNORE INTO compliance_frameworks (id, name, description, region, mandatory_retention_years, created_at) VALUES
    ('gdpr', 'General Data Protection Regulation', 'EU data protection regulation', 'EU', 7, CURRENT_TIMESTAMP),
    ('uavg', 'Uitvoeringswet Algemene Verordening Gegevensbescherming', 'Dutch GDPR implementation', 'Netherlands', 7, CURRENT_TIMESTAMP),
    ('soc2', 'SOC 2 Type II', 'System and Organization Controls 2', 'Global', 7, CURRENT_TIMESTAMP),
    ('iso27001', 'ISO 27001', 'Information Security Management System', 'Global', 3, CURRENT_TIMESTAMP),
    ('ccpa', 'California Consumer Privacy Act', 'California privacy regulation', 'US-CA', 2, CURRENT_TIMESTAMP);