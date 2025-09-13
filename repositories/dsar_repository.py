"""
DSAR (Data Subject Access Request) Repository

Handles persistence for Data Subject Access Requests with encryption for
sensitive personal data and comprehensive audit trails.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum

from utils.base_repository import BaseRepository
from utils.centralized_logger import get_scanner_logger

logger = get_scanner_logger("dsar_repository")

class DSARStatus(Enum):
    """DSAR request status enumeration"""
    SUBMITTED = "submitted"
    IDENTITY_VERIFICATION = "identity_verification"
    PROCESSING = "processing"
    DATA_COLLECTION = "data_collection"
    REVIEW = "review"
    COMPLETED = "completed"
    REJECTED = "rejected"
    EXPIRED = "expired"

class DSARType(Enum):
    """DSAR request type enumeration"""
    ACCESS = "access"           # Right to access (Article 15)
    RECTIFICATION = "rectification"  # Right to rectify (Article 16)
    ERASURE = "erasure"         # Right to erasure (Article 17)
    PORTABILITY = "portability"  # Right to data portability (Article 20)
    RESTRICTION = "restriction"  # Right to restrict processing (Article 18)
    OBJECTION = "objection"     # Right to object (Article 21)
    AUTOMATED_DECISION = "automated_decision"  # Rights related to automated decision-making (Article 22)

class DSARRepository(BaseRepository):
    """Repository for Data Subject Access Request management"""
    
    def __init__(self):
        super().__init__('enterprise_dsar_requests')
        
        # Configure sensitive fields for encryption
        self.add_sensitive_field('requester_email')
        self.add_sensitive_field('requester_name')
        self.add_sensitive_field('identity_documents')
        self.add_sensitive_field('request_details')
        self.add_sensitive_field('response_data')
        self.add_sensitive_field('notes')
        
        # Configure integrity fields
        self.add_integrity_field('response_data')
        self.add_integrity_field('identity_documents')
        
        logger.info("DSAR Repository initialized with encryption and integrity protection")
    
    def create_request(self, request_data: Dict[str, Any]) -> str:
        """
        Create a new DSAR request
        
        Args:
            request_data: DSAR request information
            
        Returns:
            Request ID
        """
        try:
            # Validate required fields
            required_fields = ['requester_email', 'request_type', 'request_details']
            for field in required_fields:
                if field not in request_data:
                    raise ValueError(f"Required field missing: {field}")
            
            # Validate request type
            if request_data['request_type'] not in [t.value for t in DSARType]:
                raise ValueError(f"Invalid request type: {request_data['request_type']}")
            
            # Prepare DSAR data
            dsar_data = {
                'requester_email': request_data['requester_email'],
                'requester_name': request_data.get('requester_name', ''),
                'request_type': request_data['request_type'],
                'request_details': request_data['request_details'],
                'status': DSARStatus.SUBMITTED.value,
                'submitted_at': datetime.now().isoformat(),
                'due_date': (datetime.now() + timedelta(days=30)).isoformat(),  # GDPR 30-day requirement
                'identity_verified': False,
                'identity_documents': request_data.get('identity_documents', ''),
                'priority': request_data.get('priority', 'normal'),
                'region': request_data.get('region', 'EU'),
                'user_id': request_data.get('user_id', ''),
                'session_id': request_data.get('session_id', ''),
                'source': request_data.get('source', 'web'),
                'notes': request_data.get('notes', ''),
                'estimated_completion': request_data.get('estimated_completion', ''),
                'response_data': '',
                'completed_at': None,
                'rejected_reason': None
            }
            
            request_id = self.create(dsar_data)
            logger.info(f"DSAR request created: {request_id} for {request_data['requester_email']}")
            
            return request_id
            
        except Exception as e:
            logger.error(f"Failed to create DSAR request: {e}")
            raise
    
    def update_status(self, request_id: str, status: str, notes: str = "", 
                     completed_by: str = "") -> bool:
        """
        Update DSAR request status
        
        Args:
            request_id: Request identifier
            status: New status
            notes: Status update notes
            completed_by: User who updated the status
            
        Returns:
            True if updated successfully
        """
        try:
            if status not in [s.value for s in DSARStatus]:
                raise ValueError(f"Invalid status: {status}")
            
            update_data = {
                'status': status,
                'updated_at': datetime.now().isoformat(),
                'updated_by': completed_by,
                'status_notes': notes
            }
            
            # Add completion timestamp for final statuses
            if status in [DSARStatus.COMPLETED.value, DSARStatus.REJECTED.value]:
                update_data['completed_at'] = datetime.now().isoformat()
                
            if status == DSARStatus.REJECTED.value:
                update_data['rejected_reason'] = notes
            
            updated = self.update(request_id, update_data)
            
            if updated:
                logger.info(f"DSAR {request_id} status updated to {status}")
            
            return updated
            
        except Exception as e:
            logger.error(f"Failed to update DSAR status: {e}")
            raise
    
    def verify_identity(self, request_id: str, verified: bool, 
                       verification_method: str = "", verifier: str = "") -> bool:
        """
        Update identity verification status
        
        Args:
            request_id: Request identifier
            verified: Verification result
            verification_method: Method used for verification
            verifier: Who performed verification
            
        Returns:
            True if updated successfully
        """
        try:
            update_data = {
                'identity_verified': verified,
                'identity_verification_method': verification_method,
                'identity_verified_by': verifier,
                'identity_verified_at': datetime.now().isoformat()
            }
            
            # Auto-update status based on verification
            if verified:
                update_data['status'] = DSARStatus.PROCESSING.value
            else:
                update_data['status'] = DSARStatus.REJECTED.value
                update_data['rejected_reason'] = 'Identity verification failed'
                update_data['completed_at'] = datetime.now().isoformat()
            
            updated = self.update(request_id, update_data)
            
            if updated:
                logger.info(f"DSAR {request_id} identity verification: {verified}")
            
            return updated
            
        except Exception as e:
            logger.error(f"Failed to update identity verification: {e}")
            raise
    
    def add_response_data(self, request_id: str, response_data: str, 
                         data_sources: List[str] = None) -> bool:
        """
        Add response data to DSAR request
        
        Args:
            request_id: Request identifier
            response_data: Collected response data
            data_sources: Sources where data was collected from
            
        Returns:
            True if updated successfully
        """
        try:
            update_data = {
                'response_data': response_data,
                'data_sources': ','.join(data_sources or []),
                'response_generated_at': datetime.now().isoformat(),
                'status': DSARStatus.REVIEW.value
            }
            
            updated = self.update(request_id, update_data)
            
            if updated:
                logger.info(f"Response data added to DSAR {request_id}")
            
            return updated
            
        except Exception as e:
            logger.error(f"Failed to add response data: {e}")
            raise
    
    def get_requests_by_status(self, status: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get DSAR requests by status"""
        try:
            return self.find_by_criteria({'status': status}, limit=limit)
        except Exception as e:
            logger.error(f"Failed to get requests by status: {e}")
            raise
    
    def get_overdue_requests(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get overdue DSAR requests"""
        try:
            current_time = datetime.now().isoformat()
            
            # Custom query for overdue requests
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE due_date < %s 
                AND status NOT IN ('completed', 'rejected', 'expired')
                ORDER BY due_date ASC
                LIMIT %s
            """
            
            records = []
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (current_time, limit))
                    results = cursor.fetchall()
                    
                    for result in results:
                        if hasattr(result, '_asdict'):
                            record = dict(result._asdict())
                        else:
                            columns = [desc[0] for desc in cursor.description]
                            record = dict(zip(columns, result))
                        
                        records.append(self._prepare_data_from_storage(record))
            
            return records
            
        except Exception as e:
            logger.error(f"Failed to get overdue requests: {e}")
            raise
    
    def get_requests_by_email(self, email: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get DSAR requests by requester email"""
        try:
            # Note: Since email is encrypted, we need to encrypt the search term
            encrypted_email = self.encryption.encrypt_field(email, 'requester_email')
            return self.find_by_criteria({'requester_email': encrypted_email}, limit=limit)
        except Exception as e:
            logger.error(f"Failed to get requests by email: {e}")
            raise
    
    def get_request_statistics(self) -> Dict[str, Any]:
        """Get DSAR request statistics"""
        try:
            stats = {}
            
            # Count by status
            for status in DSARStatus:
                count = self.count_by_criteria({'status': status.value})
                stats[f'{status.value}_count'] = count
            
            # Count by type
            for req_type in DSARType:
                count = self.count_by_criteria({'request_type': req_type.value})
                stats[f'{req_type.value}_requests'] = count
            
            # Get overdue count
            overdue_requests = self.get_overdue_requests(limit=1000)
            stats['overdue_count'] = len(overdue_requests)
            
            # Total requests
            stats['total_requests'] = sum(
                stats[f'{status.value}_count'] for status in DSARStatus
            )
            
            # Average processing time (completed requests)
            completed_requests = self.get_requests_by_status('completed', limit=100)
            if completed_requests:
                processing_times = []
                for request in completed_requests:
                    if request.get('submitted_at') and request.get('completed_at'):
                        try:
                            submitted = datetime.fromisoformat(request['submitted_at'])
                            completed = datetime.fromisoformat(request['completed_at'])
                            processing_time = (completed - submitted).days
                            processing_times.append(processing_time)
                        except Exception:
                            continue
                
                if processing_times:
                    stats['avg_processing_days'] = sum(processing_times) / len(processing_times)
                else:
                    stats['avg_processing_days'] = 0
            else:
                stats['avg_processing_days'] = 0
            
            stats['last_updated'] = datetime.now().isoformat()
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get request statistics: {e}")
            raise
    
    def expire_old_requests(self, days_old: int = 365) -> int:
        """
        Expire old DSAR requests for compliance
        
        Args:
            days_old: Days after which to expire requests
            
        Returns:
            Number of requests expired
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
            
            # Find old requests
            query = f"""
                UPDATE {self.table_name}
                SET status = %s, updated_at = %s
                WHERE created_at < %s 
                AND status IN ('completed', 'rejected')
            """
            
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (DSARStatus.EXPIRED.value, datetime.now().isoformat(), cutoff_date))
                    expired_count = cursor.rowcount
            
            logger.info(f"Expired {expired_count} old DSAR requests")
            return expired_count
            
        except Exception as e:
            logger.error(f"Failed to expire old requests: {e}")
            raise