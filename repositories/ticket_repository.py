"""
Enterprise Ticket Repository

Handles persistence for enterprise ticketing system integration,
tracking tickets created from compliance findings and their resolution.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum

from utils.base_repository import BaseRepository
from utils.centralized_logger import get_scanner_logger

logger = get_scanner_logger("ticket_repository")

class TicketStatus(Enum):
    """Ticket status enumeration"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"
    REOPENED = "reopened"

class TicketPriority(Enum):
    """Ticket priority levels"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"

class TicketType(Enum):
    """Types of tickets"""
    COMPLIANCE_ISSUE = "compliance_issue"
    SECURITY_FINDING = "security_finding"
    PRIVACY_VIOLATION = "privacy_violation"
    DSAR_REQUEST = "dsar_request"
    VENDOR_RISK = "vendor_risk"
    AUDIT_FINDING = "audit_finding"
    INCIDENT = "incident"
    MAINTENANCE = "maintenance"

class TicketRepository(BaseRepository):
    """Repository for enterprise ticket management"""
    
    def __init__(self):
        super().__init__('enterprise_tickets')
        
        # Configure sensitive fields
        self.add_sensitive_field('description')
        self.add_sensitive_field('resolution_notes')
        self.add_sensitive_field('internal_notes')
        
        # Configure integrity fields
        self.add_integrity_field('source_data')
        
        logger.info("Ticket Repository initialized")
    
    def create_ticket(self, ticket_data: Dict[str, Any]) -> str:
        """Create enterprise ticket"""
        try:
            required_fields = ['title', 'ticket_type', 'priority']
            for field in required_fields:
                if field not in ticket_data:
                    raise ValueError(f"Required field missing: {field}")
            
            ticket_record = {
                'title': ticket_data['title'],
                'description': ticket_data.get('description', ''),
                'ticket_type': ticket_data['ticket_type'],
                'priority': ticket_data['priority'],
                'status': ticket_data.get('status', TicketStatus.OPEN.value),
                'external_ticket_id': ticket_data.get('external_ticket_id', ''),
                'external_system': ticket_data.get('external_system', ''),
                'source_scan_id': ticket_data.get('source_scan_id', ''),
                'source_event_id': ticket_data.get('source_event_id', ''),
                'source_data': ticket_data.get('source_data', '{}'),
                'assigned_to': ticket_data.get('assigned_to', ''),
                'assignee_email': ticket_data.get('assignee_email', ''),
                'reporter_id': ticket_data.get('reporter_id', ''),
                'region': ticket_data.get('region', 'EU'),
                'compliance_framework': ticket_data.get('compliance_framework', 'GDPR'),
                'risk_level': ticket_data.get('risk_level', 'medium'),
                'finding_type': ticket_data.get('finding_type', ''),
                'affected_systems': ticket_data.get('affected_systems', ''),
                'estimated_effort': ticket_data.get('estimated_effort', ''),
                'due_date': ticket_data.get('due_date'),
                'resolution_notes': ticket_data.get('resolution_notes', ''),
                'internal_notes': ticket_data.get('internal_notes', ''),
                'tags': ticket_data.get('tags', ''),
                'created_by_automation': ticket_data.get('created_by_automation', False),
                'auto_close_eligible': ticket_data.get('auto_close_eligible', False),
                'escalated': False,
                'escalation_date': None,
                'resolved_at': None,
                'closed_at': None,
                'resolution_time_hours': None
            }
            
            ticket_id = self.create(ticket_record)
            logger.info(f"Ticket created: {ticket_id} - {ticket_data['title']}")
            return ticket_id
            
        except Exception as e:
            logger.error(f"Failed to create ticket: {e}")
            raise
    
    def update_status(self, ticket_id: str, status: str, resolution_notes: str = "", 
                     updated_by: str = "") -> bool:
        """Update ticket status"""
        try:
            update_data = {
                'status': status,
                'updated_by': updated_by,
                'status_updated_at': datetime.now().isoformat()
            }
            
            if status == TicketStatus.RESOLVED.value:
                update_data['resolved_at'] = datetime.now().isoformat()
                update_data['resolution_notes'] = resolution_notes
            elif status == TicketStatus.CLOSED.value:
                update_data['closed_at'] = datetime.now().isoformat()
                if not resolution_notes:
                    update_data['resolution_notes'] = resolution_notes
            
            updated = self.update(ticket_id, update_data)
            
            if updated:
                logger.info(f"Ticket {ticket_id} status updated to {status}")
            
            return updated
            
        except Exception as e:
            logger.error(f"Failed to update ticket status: {e}")
            raise
    
    def get_tickets_by_status(self, status: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get tickets by status"""
        try:
            return self.find_by_criteria({'status': status}, limit=limit)
        except Exception as e:
            logger.error(f"Failed to get tickets by status: {e}")
            raise
    
    def get_tickets_by_scan(self, scan_id: str) -> List[Dict[str, Any]]:
        """Get tickets related to a specific scan"""
        try:
            return self.find_by_criteria({'source_scan_id': scan_id})
        except Exception as e:
            logger.error(f"Failed to get tickets by scan: {e}")
            raise
    
    def get_high_priority_tickets(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get high priority tickets"""
        try:
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE priority IN ('high', 'critical', 'urgent')
                AND status NOT IN ('resolved', 'closed', 'cancelled')
                ORDER BY 
                    CASE priority
                        WHEN 'urgent' THEN 1
                        WHEN 'critical' THEN 2
                        WHEN 'high' THEN 3
                    END,
                    created_at ASC
                LIMIT %s
            """
            
            records = []
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (limit,))
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
            logger.error(f"Failed to get high priority tickets: {e}")
            raise