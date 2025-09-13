"""
Enterprise Event Listeners

Implements automatic processing of enterprise events for:
- Automatic ticket creation from critical findings
- SOC2 evidence capture and storage
- DSAR request processing
- Vendor risk alerts
- Compliance trigger automation
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json

# Enterprise integration - non-breaking import
try:
    from utils.event_bus import EventType, Event, get_event_bus
    from repositories.ticket_repository import TicketRepository
    from repositories.dsar_repository import DSARRepository
    from repositories.audit_evidence_repository import EvidenceRepository
    from repositories.vendor_repository import VendorRepository
    from repositories.consent_repository import ConsentRepository
    ENTERPRISE_LISTENERS_AVAILABLE = True
except ImportError as e:
    # Create dummy classes for type hints when imports fail
    EventType = None
    Event = type('Event', (), {})
    get_event_bus = None
    TicketRepository = type('TicketRepository', (), {})
    DSARRepository = type('DSARRepository', (), {})
    EvidenceRepository = type('EvidenceRepository', (), {})
    VendorRepository = type('VendorRepository', (), {})
    ConsentRepository = type('ConsentRepository', (), {})
    ENTERPRISE_LISTENERS_AVAILABLE = False

# Centralized logging
try:
    from utils.centralized_logger import get_scanner_logger
    logger = get_scanner_logger("enterprise_listeners")
except ImportError:
    logger = logging.getLogger(__name__)

class EnterpriseEventListener:
    """
    Enterprise event listener that automatically processes compliance events
    and triggers appropriate enterprise workflows.
    """
    
    def __init__(self):
        if not ENTERPRISE_LISTENERS_AVAILABLE:
            logger.warning("Enterprise listeners not available - missing dependencies")
            return
            
        # Initialize repositories
        try:
            self.ticket_repo = TicketRepository()
            self.dsar_repo = DSARRepository()
            self.evidence_repo = EvidenceRepository()
            self.vendor_repo = VendorRepository()
            self.consent_repo = ConsentRepository()
            
            # Get event bus
            self.event_bus = get_event_bus()
            
            # Track listener registration
            self.listener_ids = []
            
            logger.info("Enterprise event listener initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize enterprise listeners: {e}")
            raise
    
    def register_listeners(self):
        """Register all enterprise event listeners"""
        if not ENTERPRISE_LISTENERS_AVAILABLE:
            return []
        
        try:
            # Critical issue auto-ticketing
            critical_listener_id = self.event_bus.subscribe(
                EventType.CRITICAL_ISSUE_FOUND,
                self._handle_critical_issue
            )
            self.listener_ids.append(critical_listener_id)
            
            # DSAR request processing
            dsar_listener_id = self.event_bus.subscribe(
                EventType.DSAR_REQUEST_SUBMITTED,
                self._handle_dsar_request
            )
            self.listener_ids.append(dsar_listener_id)
            
            # Evidence capture automation
            evidence_listener_id = self.event_bus.subscribe(
                EventType.COMPLIANCE_EVIDENCE_ADDED,
                self._handle_evidence_capture
            )
            self.listener_ids.append(evidence_listener_id)
            
            # Vendor risk alert processing
            vendor_listener_id = self.event_bus.subscribe(
                EventType.VENDOR_RISK_ALERT,
                self._handle_vendor_risk_alert
            )
            self.listener_ids.append(vendor_listener_id)
            
            # Consent update processing
            consent_listener_id = self.event_bus.subscribe(
                EventType.CONSENT_UPDATED,
                self._handle_consent_update
            )
            self.listener_ids.append(consent_listener_id)
            
            # Ticket creation from enterprise actions
            ticket_listener_id = self.event_bus.subscribe(
                EventType.TICKET_CREATED,
                self._handle_ticket_creation
            )
            self.listener_ids.append(ticket_listener_id)
            
            # General scan completion for evidence
            scan_listener_id = self.event_bus.subscribe(
                EventType.SCAN_COMPLETED,
                self._handle_scan_completion
            )
            self.listener_ids.append(scan_listener_id)
            
            logger.info(f"Registered {len(self.listener_ids)} enterprise listeners")
            return self.listener_ids
            
        except Exception as e:
            logger.error(f"Failed to register enterprise listeners: {e}")
            raise
    
    def _handle_critical_issue(self, event: Event):
        """Handle critical issue detection - auto-create tickets"""
        try:
            logger.info(f"Processing critical issue event from {event.source}")
            
            # Extract critical issue data
            data = event.data
            finding_type = data.get('finding_type', 'Critical Security Issue')
            severity = data.get('severity', 'Critical')
            source_scan_id = data.get('source_scan_id', getattr(event, 'scan_id', 'unknown'))
            
            # Create high-priority ticket automatically
            ticket_data = {
                'title': f"CRITICAL: {finding_type}",
                'description': self._generate_critical_issue_description(data),
                'ticket_type': 'security_finding',
                'priority': 'critical',
                'source_scan_id': source_scan_id,
                'source_event_id': event.event_id,
                'risk_level': 'critical',
                'finding_type': finding_type,
                'affected_systems': data.get('affected_systems', 'Unknown'),
                'region': data.get('region', 'EU'),
                'compliance_framework': data.get('compliance_framework', 'GDPR'),
                'created_by_automation': True,
                'auto_close_eligible': False,  # Critical issues need manual review
                'due_date': (datetime.now() + timedelta(hours=4)).isoformat(),  # 4 hour SLA
                'tags': 'critical,security,auto-generated'
            }
            
            ticket_id = self.ticket_repo.create_ticket(ticket_data)
            
            # Also create audit evidence for the critical finding
            self._create_critical_finding_evidence(event, ticket_id)
            
            logger.info(f"Auto-created critical ticket: {ticket_id}")
            
        except Exception as e:
            logger.error(f"Failed to handle critical issue event: {e}")
    
    def _handle_dsar_request(self, event: Event):
        """Handle DSAR request submission - create DSAR record"""
        try:
            logger.info(f"Processing DSAR request event from {event.source}")
            
            data = event.data
            
            # If this came from manual entry, create DSAR directly
            if event.source == 'quick_actions':
                dsar_id = self.dsar_repo.create_request(data)
                logger.info(f"Created DSAR from manual entry: {dsar_id}")
                return
            
            # If this came from scan findings, create contextual DSAR
            if event.source == 'enterprise_actions':
                dsar_data = {
                    'requester_email': 'compliance@company.com',  # Default for scan-triggered DSARs
                    'requester_name': 'Compliance Team',
                    'request_type': 'access',  # Default to access request
                    'request_details': self._generate_dsar_details_from_scan(data),
                    'source_scan_id': data.get('source_scan_id'),
                    'priority': data.get('risk_level', 'medium'),
                    'region': data.get('region', 'EU'),
                    'user_id': event.user_id,
                    'session_id': event.session_id,
                    'notes': f"Auto-generated from scan findings. PII types: {', '.join(data.get('pii_types', []))}",
                    'estimated_completion': (datetime.now() + timedelta(days=20)).isoformat()
                }
                
                dsar_id = self.dsar_repo.create_request(dsar_data)
                logger.info(f"Created DSAR from scan findings: {dsar_id}")
            
        except Exception as e:
            logger.error(f"Failed to handle DSAR request event: {e}")
    
    def _handle_evidence_capture(self, event: Event):
        """Handle evidence capture - store in audit evidence repository"""
        try:
            logger.info(f"Processing evidence capture event from {event.source}")
            
            data = event.data
            
            # Create evidence record
            evidence_data = {
                'evidence_type': data.get('evidence_type', 'scan_result'),
                'evidence_data': json.dumps(data),
                'source': event.source,
                'metadata': json.dumps({
                    'event_id': event.event_id,
                    'user_id': event.user_id,
                    'session_id': event.session_id,
                    'timestamp': event.timestamp.isoformat(),
                    'scan_type': data.get('scan_type', 'unknown'),
                    'compliance_framework': data.get('compliance_framework', 'GDPR')
                }),
                'source_data': json.dumps(event.__dict__),
                'collection_method': 'automated_event',
                'collector_id': 'enterprise_listener',
                'retention_period_months': data.get('retention_period_months', 84),
                'control_objective': self._determine_control_objective(data),
                'risk_level': data.get('risk_level', 'medium'),
                'compliance_framework': data.get('compliance_framework', 'SOC2'),
                'region': data.get('region', 'EU'),
                'scan_id': data.get('source_scan_id', getattr(event, 'scan_id', 'unknown')),
                'user_id': event.user_id,
                'session_id': event.session_id,
                'classification': data.get('classification', 'internal'),
                'tags': f"auto-generated,{data.get('evidence_type', 'scan_result')}"
            }
            
            evidence_id = self.evidence_repo.store_evidence(evidence_data)
            logger.info(f"Stored audit evidence: {evidence_id}")
            
        except Exception as e:
            logger.error(f"Failed to handle evidence capture event: {e}")
    
    def _handle_vendor_risk_alert(self, event: Event):
        """Handle vendor risk alerts - create/update vendor assessments"""
        try:
            logger.info(f"Processing vendor risk alert from {event.source}")
            
            data = event.data
            vendor_name = data.get('vendor_name', 'Unknown Vendor')
            
            # Check if vendor assessment already exists
            existing_vendors = self.vendor_repo.find_by_criteria({'vendor_name': vendor_name}, limit=1)
            
            if existing_vendors:
                # Update existing vendor with new risk information
                vendor_id = existing_vendors[0]['id']
                risk_level = data.get('risk_level', 'medium')
                
                self.vendor_repo.update_risk_level(
                    vendor_id, 
                    risk_level, 
                    f"Risk updated from scan findings: {data.get('findings_count', 0)} issues found"
                )
                
                logger.info(f"Updated vendor risk for {vendor_name}: {risk_level}")
            else:
                # Create new vendor assessment
                vendor_data = {
                    'vendor_name': vendor_name,
                    'vendor_type': 'web_service',
                    'risk_level': data.get('risk_level', 'medium'),
                    'website': data.get('vendor_url', ''),
                    'data_processing': data.get('data_processing', True),
                    'gdpr_compliant': None,  # To be assessed
                    'region': data.get('region', 'EU'),
                    'assessor_id': event.user_id,
                    'assessment_notes': f"Auto-generated from scan findings. Found {data.get('findings_count', 0)} issues.",
                    'next_review_date': (datetime.now() + timedelta(days=90)).isoformat(),
                    'requires_dpa': True,  # Assume true for safety
                    'dpa_signed': False
                }
                
                vendor_id = self.vendor_repo.create_vendor_assessment(vendor_data)
                logger.info(f"Created vendor assessment: {vendor_id}")
            
        except Exception as e:
            logger.error(f"Failed to handle vendor risk alert: {e}")
    
    def _handle_consent_update(self, event: Event):
        """Handle consent updates from privacy scans"""
        try:
            logger.info(f"Processing consent update event from {event.source}")
            
            data = event.data
            consent_type = data.get('consent_type', 'tracking')
            
            # Create consent record for compliance tracking
            consent_data = {
                'user_identifier': f"scan_user_{event.session_id}",
                'consent_type': consent_type,
                'status': 'withdrawn' if data.get('privacy_findings_count', 0) > 0 else 'granted',
                'purpose': f"Privacy compliance from {data.get('scan_type', 'scan')}",
                'legal_basis': 'legitimate_interest',
                'source': 'compliance_scan',
                'region': data.get('region', 'EU'),
                'session_id': event.session_id,
                'version': '1.0'
            }
            
            consent_id = self.consent_repo.record_consent(consent_data)
            logger.info(f"Recorded consent tracking: {consent_id}")
            
        except Exception as e:
            logger.error(f"Failed to handle consent update: {e}")
    
    def _handle_ticket_creation(self, event: Event):
        """Handle ticket creation events from enterprise actions"""
        try:
            logger.info(f"Processing ticket creation event from {event.source}")
            
            data = event.data
            
            # Create ticket from event data
            ticket_id = self.ticket_repo.create_ticket(data)
            
            # Create associated evidence
            evidence_data = {
                'evidence_type': 'incident_report',
                'evidence_data': json.dumps(data),
                'source': event.source,
                'metadata': json.dumps({
                    'ticket_id': ticket_id,
                    'event_id': event.event_id
                }),
                'control_objective': 'Incident Response',
                'compliance_framework': data.get('compliance_framework', 'GDPR'),
                'region': data.get('region', 'EU'),
                'scan_id': data.get('source_scan_id'),
                'user_id': event.user_id,
                'session_id': event.session_id
            }
            
            evidence_id = self.evidence_repo.store_evidence(evidence_data)
            
            logger.info(f"Created ticket {ticket_id} with evidence {evidence_id}")
            
        except Exception as e:
            logger.error(f"Failed to handle ticket creation: {e}")
    
    def _handle_scan_completion(self, event: Event):
        """Handle scan completion - automatic evidence capture"""
        try:
            logger.debug(f"Processing scan completion event from {event.source}")
            
            data = event.data
            
            # Only create evidence for scans with significant findings
            findings_count = data.get('findings_count', 0)
            if findings_count < 1:
                return  # Skip empty scans
            
            # Create scan completion evidence
            evidence_data = {
                'evidence_type': 'scan_result',
                'evidence_data': json.dumps(data),
                'source': f"scan_completion_{event.source}",
                'metadata': json.dumps({
                    'scan_type': data.get('scan_type', 'unknown'),
                    'findings_count': findings_count,
                    'scan_duration': data.get('scan_duration', 0),
                    'completion_timestamp': event.timestamp.isoformat()
                }),
                'control_objective': 'Continuous Compliance Monitoring',
                'risk_level': 'low' if findings_count < 5 else 'medium' if findings_count < 20 else 'high',
                'compliance_framework': 'GDPR',
                'region': data.get('region', 'EU'),
                'scan_id': getattr(event, 'scan_id', 'unknown'),
                'user_id': event.user_id,
                'session_id': event.session_id
            }
            
            evidence_id = self.evidence_repo.store_evidence(evidence_data)
            logger.debug(f"Auto-captured scan evidence: {evidence_id}")
            
        except Exception as e:
            logger.error(f"Failed to handle scan completion: {e}")
    
    def _generate_critical_issue_description(self, data: Dict[str, Any]) -> str:
        """Generate ticket description for critical issues"""
        finding_type = data.get('finding_type', 'Critical Security Issue')
        source_scan = data.get('source_scan_id', 'Unknown')
        details = data.get('details', 'No additional details available')
        
        return f"""CRITICAL SECURITY ISSUE DETECTED
        
Finding Type: {finding_type}
Source Scan: {source_scan}
Risk Level: Critical
Detection Time: {datetime.now().isoformat()}

Details:
{details}

This ticket was automatically generated from critical security findings.
Immediate action required within 4 hours per security SLA.

Recommended Actions:
1. Investigate the security finding immediately
2. Assess impact and affected systems
3. Implement immediate mitigation if needed
4. Update this ticket with findings and resolution
5. Review security controls to prevent recurrence
"""
    
    def _generate_dsar_details_from_scan(self, data: Dict[str, Any]) -> str:
        """Generate DSAR request details from scan findings"""
        pii_types = data.get('pii_types', [])
        source_scan = data.get('source_scan_id', 'Unknown')
        findings_count = data.get('pii_findings_count', 0)
        
        return f"""Data Subject Access Request - Auto-Generated from Compliance Scan

This DSAR was automatically generated after detecting {findings_count} PII findings in compliance scan {source_scan}.

PII Types Detected:
{chr(10).join([f"• {pii_type}" for pii_type in pii_types])}

Request Details:
- Access to all personal data processed related to the detected PII
- Information about processing purposes and legal basis
- Data retention policies and deletion schedules
- Third-party data sharing arrangements

Generated: {datetime.now().isoformat()}
Requester Context: Compliance audit trigger
Priority: {data.get('risk_level', 'medium')} (based on scan findings)
"""
    
    def _determine_control_objective(self, data: Dict[str, Any]) -> str:
        """Determine SOC2 control objective based on evidence type"""
        evidence_type = data.get('evidence_type', 'scan_result')
        scan_type = data.get('scan_type', '')
        
        if evidence_type == 'security_log':
            return 'CC6.1 - Logical Access Controls'
        elif evidence_type == 'access_log':
            return 'CC6.2 - Authentication'
        elif 'privacy' in scan_type.lower() or 'gdpr' in scan_type.lower():
            return 'PI1.1 - Privacy Notice and Choice'
        elif 'security' in scan_type.lower():
            return 'CC6.0 - Logical and Physical Access Controls'
        elif evidence_type == 'vendor_assessment':
            return 'CC9.1 - Vendor and Business Partner Agreements'
        elif evidence_type == 'incident_report':
            return 'CC7.4 - Response to System Incidents'
        else:
            return 'CC1.4 - Information and Communication'
    
    def _create_critical_finding_evidence(self, event: Event, ticket_id: str):
        """Create audit evidence for critical findings"""
        try:
            evidence_data = {
                'evidence_type': 'security_log',
                'evidence_data': json.dumps({
                    'critical_finding': event.data,
                    'ticket_id': ticket_id,
                    'auto_generated': True
                }),
                'source': f"critical_finding_{event.source}",
                'metadata': json.dumps({
                    'ticket_id': ticket_id,
                    'event_id': event.event_id,
                    'severity': 'critical'
                }),
                'control_objective': 'CC7.4 - Response to System Incidents',
                'risk_level': 'critical',
                'compliance_framework': 'SOC2',
                'region': event.data.get('region', 'EU'),
                'scan_id': getattr(event, 'scan_id', 'unknown'),
                'user_id': event.user_id,
                'session_id': event.session_id,
                'is_sensitive': True,
                'classification': 'confidential'
            }
            
            evidence_id = self.evidence_repo.store_evidence(evidence_data)
            logger.info(f"Created critical finding evidence: {evidence_id}")
            
        except Exception as e:
            logger.error(f"Failed to create critical finding evidence: {e}")
    
    def unregister_listeners(self):
        """Unregister all event listeners"""
        if not ENTERPRISE_LISTENERS_AVAILABLE:
            return
        
        try:
            for listener_id in self.listener_ids:
                for event_type in EventType:
                    self.event_bus.unsubscribe(event_type, listener_id)
            
            self.listener_ids.clear()
            logger.info("Unregistered all enterprise listeners")
            
        except Exception as e:
            logger.error(f"Failed to unregister listeners: {e}")
    
    def get_listener_status(self) -> Dict[str, Any]:
        """Get status of enterprise listeners"""
        if not ENTERPRISE_LISTENERS_AVAILABLE:
            return {
                'status': 'unavailable',
                'reason': 'Dependencies not available',
                'listeners_registered': 0
            }
        
        return {
            'status': 'active',
            'listeners_registered': len(self.listener_ids),
            'listener_ids': self.listener_ids,
            'event_types_monitored': [
                'CRITICAL_ISSUE_FOUND',
                'DSAR_REQUEST_SUBMITTED',
                'COMPLIANCE_EVIDENCE_ADDED',
                'VENDOR_RISK_ALERT',
                'CONSENT_UPDATED',
                'TICKET_CREATED',
                'SCAN_COMPLETED'
            ],
            'last_status_check': datetime.now().isoformat()
        }

# Global enterprise listener instance
_enterprise_listener = None

def get_enterprise_listener() -> EnterpriseEventListener:
    """Get singleton enterprise event listener"""
    global _enterprise_listener
    if _enterprise_listener is None:
        _enterprise_listener = EnterpriseEventListener()
    return _enterprise_listener

def initialize_enterprise_listeners():
    """Initialize enterprise listeners (returns empty list - orchestrator handles coordination)"""
    if not ENTERPRISE_LISTENERS_AVAILABLE:
        logger.warning("Enterprise listeners not available - skipping initialization")
        return []
    
    try:
        # Just initialize the listener instance, orchestrator will handle coordination
        listener = get_enterprise_listener()
        logger.info("Enterprise listeners initialized for orchestrator coordination")
        return []  # Return empty list - no direct subscriptions
    except Exception as e:
        logger.error(f"Failed to initialize enterprise listeners: {e}")
        return []

def shutdown_enterprise_listeners():
    """Shutdown enterprise listeners"""
    global _enterprise_listener
    if _enterprise_listener:
        _enterprise_listener.unregister_listeners()
        _enterprise_listener = None
        logger.info("Enterprise listeners shut down")