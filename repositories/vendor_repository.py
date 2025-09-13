"""
Vendor Risk Repository

Handles persistence for vendor risk assessments, monitoring data,
and compliance tracking for third-party vendor management.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum

from utils.base_repository import BaseRepository
from utils.centralized_logger import get_scanner_logger

logger = get_scanner_logger("vendor_repository")

class VendorRiskLevel(Enum):
    """Vendor risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class VendorStatus(Enum):
    """Vendor assessment status"""
    ACTIVE = "active"
    PENDING_REVIEW = "pending_review"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    UNDER_REVIEW = "under_review"

class VendorRepository(BaseRepository):
    """Repository for vendor risk management"""
    
    def __init__(self):
        super().__init__('enterprise_vendor_assessments')
        
        # Configure sensitive fields
        self.add_sensitive_field('contact_email')
        self.add_sensitive_field('contact_phone')
        self.add_sensitive_field('contract_details')
        self.add_sensitive_field('assessment_notes')
        
        # Configure integrity fields
        self.add_integrity_field('assessment_data')
        self.add_integrity_field('contract_details')
        
        logger.info("Vendor Repository initialized with risk tracking")
    
    def create_vendor_assessment(self, vendor_data: Dict[str, Any]) -> str:
        """Create vendor risk assessment"""
        try:
            required_fields = ['vendor_name', 'vendor_type', 'risk_level']
            for field in required_fields:
                if field not in vendor_data:
                    raise ValueError(f"Required field missing: {field}")
            
            assessment_record = {
                'vendor_name': vendor_data['vendor_name'],
                'vendor_type': vendor_data['vendor_type'],
                'risk_level': vendor_data['risk_level'],
                'status': vendor_data.get('status', VendorStatus.ACTIVE.value),
                'contact_email': vendor_data.get('contact_email', ''),
                'contact_phone': vendor_data.get('contact_phone', ''),
                'website': vendor_data.get('website', ''),
                'country': vendor_data.get('country', ''),
                'data_processing': vendor_data.get('data_processing', False),
                'gdpr_compliant': vendor_data.get('gdpr_compliant', None),
                'iso27001_certified': vendor_data.get('iso27001_certified', False),
                'soc2_certified': vendor_data.get('soc2_certified', False),
                'contract_start_date': vendor_data.get('contract_start_date'),
                'contract_end_date': vendor_data.get('contract_end_date'),
                'contract_details': vendor_data.get('contract_details', ''),
                'assessment_data': vendor_data.get('assessment_data', '{}'),
                'assessment_notes': vendor_data.get('assessment_notes', ''),
                'last_review_date': vendor_data.get('last_review_date'),
                'next_review_date': vendor_data.get('next_review_date'),
                'compliance_score': vendor_data.get('compliance_score', 0),
                'security_score': vendor_data.get('security_score', 0),
                'region': vendor_data.get('region', 'EU'),
                'assessor_id': vendor_data.get('assessor_id', ''),
                'requires_dpa': vendor_data.get('requires_dpa', False),
                'dpa_signed': vendor_data.get('dpa_signed', False),
                'privacy_policy_reviewed': vendor_data.get('privacy_policy_reviewed', False),
                'subprocessors_identified': vendor_data.get('subprocessors_identified', False),
                'incident_count': 0,
                'last_incident_date': None
            }
            
            vendor_id = self.create(assessment_record)
            logger.info(f"Vendor assessment created: {vendor_id} for {vendor_data['vendor_name']}")
            return vendor_id
            
        except Exception as e:
            logger.error(f"Failed to create vendor assessment: {e}")
            raise
    
    def update_risk_level(self, vendor_id: str, risk_level: str, reason: str = "") -> bool:
        """Update vendor risk level"""
        try:
            update_data = {
                'risk_level': risk_level,
                'risk_update_reason': reason,
                'risk_updated_at': datetime.now().isoformat()
            }
            
            updated = self.update(vendor_id, update_data)
            if updated:
                logger.info(f"Vendor {vendor_id} risk level updated to {risk_level}")
            
            return updated
            
        except Exception as e:
            logger.error(f"Failed to update vendor risk level: {e}")
            raise
    
    def get_high_risk_vendors(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get high-risk vendors"""
        try:
            return self.find_by_criteria({'risk_level': VendorRiskLevel.HIGH.value}, limit=limit)
        except Exception as e:
            logger.error(f"Failed to get high-risk vendors: {e}")
            raise