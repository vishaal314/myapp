"""
Consent Management Repository

Handles persistence for consent records with GDPR compliance,
including consent history, withdrawal tracking, and audit trails.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum

from utils.base_repository import BaseRepository
from utils.centralized_logger import get_scanner_logger

logger = get_scanner_logger("consent_repository")

class ConsentStatus(Enum):
    """Consent status enumeration"""
    GRANTED = "granted"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"
    PENDING = "pending"

class ConsentType(Enum):
    """Types of consent"""
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    FUNCTIONAL = "functional"
    NECESSARY = "necessary"
    PROFILING = "profiling"
    THIRD_PARTY = "third_party"

class ConsentRepository(BaseRepository):
    """Repository for consent management"""
    
    def __init__(self):
        super().__init__('enterprise_consent_records')
        
        # Configure sensitive fields
        self.add_sensitive_field('user_identifier')
        self.add_sensitive_field('ip_address')
        self.add_sensitive_field('user_agent')
        self.add_sensitive_field('consent_evidence')
        
        # Configure integrity fields
        self.add_integrity_field('consent_evidence')
        
        logger.info("Consent Repository initialized with privacy protection")
    
    def record_consent(self, consent_data: Dict[str, Any]) -> str:
        """Record user consent"""
        try:
            required_fields = ['user_identifier', 'consent_type', 'status']
            for field in required_fields:
                if field not in consent_data:
                    raise ValueError(f"Required field missing: {field}")
            
            consent_record = {
                'user_identifier': consent_data['user_identifier'],
                'consent_type': consent_data['consent_type'],
                'status': consent_data['status'],
                'granted_at': datetime.now().isoformat() if consent_data['status'] == ConsentStatus.GRANTED.value else None,
                'withdrawn_at': datetime.now().isoformat() if consent_data['status'] == ConsentStatus.WITHDRAWN.value else None,
                'expires_at': consent_data.get('expires_at'),
                'purpose': consent_data.get('purpose', ''),
                'legal_basis': consent_data.get('legal_basis', 'consent'),
                'ip_address': consent_data.get('ip_address', ''),
                'user_agent': consent_data.get('user_agent', ''),
                'consent_evidence': consent_data.get('consent_evidence', ''),
                'withdrawal_method': consent_data.get('withdrawal_method', ''),
                'region': consent_data.get('region', 'EU'),
                'version': consent_data.get('version', '1.0'),
                'source': consent_data.get('source', 'web'),
                'session_id': consent_data.get('session_id', ''),
                'parent_consent_id': consent_data.get('parent_consent_id', ''),
                'is_minor': consent_data.get('is_minor', False),
                'parental_consent': consent_data.get('parental_consent', False)
            }
            
            consent_id = self.create(consent_record)
            logger.info(f"Consent recorded: {consent_id}")
            return consent_id
            
        except Exception as e:
            logger.error(f"Failed to record consent: {e}")
            raise
    
    def withdraw_consent(self, user_identifier: str, consent_type: str, 
                        withdrawal_method: str = "user_request") -> bool:
        """Withdraw user consent"""
        try:
            # Create withdrawal record
            withdrawal_data = {
                'user_identifier': user_identifier,
                'consent_type': consent_type,
                'status': ConsentStatus.WITHDRAWN.value,
                'withdrawn_at': datetime.now().isoformat(),
                'withdrawal_method': withdrawal_method,
                'legal_basis': 'withdrawal_consent'
            }
            
            consent_id = self.record_consent(withdrawal_data)
            logger.info(f"Consent withdrawn for {user_identifier}: {consent_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to withdraw consent: {e}")
            raise
    
    def get_user_consents(self, user_identifier: str) -> List[Dict[str, Any]]:
        """Get all consent records for a user"""
        try:
            encrypted_user_id = self.encryption.encrypt_field(user_identifier, 'user_identifier')
            return self.find_by_criteria({'user_identifier': encrypted_user_id})
        except Exception as e:
            logger.error(f"Failed to get user consents: {e}")
            raise
    
    def get_active_consent(self, user_identifier: str, consent_type: str) -> Optional[Dict[str, Any]]:
        """Get active consent for user and type"""
        try:
            consents = self.get_user_consents(user_identifier)
            
            # Find most recent consent for this type
            type_consents = [c for c in consents if c.get('consent_type') == consent_type]
            
            if not type_consents:
                return None
            
            # Sort by created_at descending
            type_consents.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            most_recent = type_consents[0]
            
            # Check if still active
            if most_recent.get('status') == ConsentStatus.GRANTED.value:
                # Check expiration
                expires_at = most_recent.get('expires_at')
                if expires_at and datetime.fromisoformat(expires_at) < datetime.now():
                    return None  # Expired
                return most_recent
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get active consent: {e}")
            raise