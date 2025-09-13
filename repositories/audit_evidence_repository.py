"""
Audit Evidence Repository

Handles persistence for SOC2 audit evidence with tamper-proof storage,
content integrity verification, and comprehensive audit trails.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum

from utils.base_repository import BaseRepository
from utils.centralized_logger import get_scanner_logger

logger = get_scanner_logger("audit_evidence_repository")

class EvidenceType(Enum):
    """Types of audit evidence"""
    SCAN_RESULT = "scan_result"
    COMPLIANCE_REPORT = "compliance_report"
    SECURITY_LOG = "security_log"
    ACCESS_LOG = "access_log"
    CONFIGURATION = "configuration"
    POLICY_DOCUMENT = "policy_document"
    TRAINING_RECORD = "training_record"
    INCIDENT_REPORT = "incident_report"
    DSAR_RECORD = "dsar_record"
    CONSENT_RECORD = "consent_record"
    VENDOR_ASSESSMENT = "vendor_assessment"

class EvidenceRepository(BaseRepository):
    """Repository for audit evidence with WORM (Write Once, Read Many) principles"""
    
    def __init__(self):
        super().__init__('enterprise_audit_evidence')
        
        # Configure integrity fields for tamper detection
        self.add_integrity_field('evidence_data')
        self.add_integrity_field('metadata')
        self.add_integrity_field('source_data')
        
        logger.info("Audit Evidence Repository initialized with integrity protection")
    
    def store_evidence(self, evidence_data: Dict[str, Any]) -> str:
        """Store audit evidence with integrity protection"""
        try:
            required_fields = ['evidence_type', 'evidence_data', 'source']
            for field in required_fields:
                if field not in evidence_data:
                    raise ValueError(f"Required field missing: {field}")
            
            evidence_record = {
                'evidence_type': evidence_data['evidence_type'],
                'evidence_data': evidence_data['evidence_data'],
                'source': evidence_data['source'],
                'metadata': evidence_data.get('metadata', '{}'),
                'source_data': evidence_data.get('source_data', ''),
                'collection_method': evidence_data.get('collection_method', 'automated'),
                'collector_id': evidence_data.get('collector_id', 'system'),
                'retention_period_months': evidence_data.get('retention_period_months', 84),  # 7 years default
                'control_objective': evidence_data.get('control_objective', ''),
                'risk_level': evidence_data.get('risk_level', 'medium'),
                'compliance_framework': evidence_data.get('compliance_framework', 'SOC2'),
                'region': evidence_data.get('region', 'EU'),
                'scan_id': evidence_data.get('scan_id', ''),
                'user_id': evidence_data.get('user_id', ''),
                'session_id': evidence_data.get('session_id', ''),
                'is_sensitive': evidence_data.get('is_sensitive', False),
                'classification': evidence_data.get('classification', 'internal'),
                'tags': evidence_data.get('tags', ''),
                'related_evidence_ids': evidence_data.get('related_evidence_ids', ''),
                'expires_at': evidence_data.get('expires_at'),
                'reviewed': False,
                'reviewer_id': None,
                'review_notes': ''
            }
            
            evidence_id = self.create(evidence_record)
            logger.info(f"Audit evidence stored: {evidence_id}")
            return evidence_id
            
        except Exception as e:
            logger.error(f"Failed to store audit evidence: {e}")
            raise
    
    def get_evidence_by_scan(self, scan_id: str) -> List[Dict[str, Any]]:
        """Get all evidence related to a specific scan"""
        try:
            return self.find_by_criteria({'scan_id': scan_id})
        except Exception as e:
            logger.error(f"Failed to get evidence by scan: {e}")
            raise
    
    def get_evidence_by_type(self, evidence_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get evidence by type"""
        try:
            return self.find_by_criteria({'evidence_type': evidence_type}, limit=limit)
        except Exception as e:
            logger.error(f"Failed to get evidence by type: {e}")
            raise