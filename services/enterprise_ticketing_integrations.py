#!/usr/bin/env python3
"""
Enterprise Ticketing and SIEM Integrations
Comprehensive integration with Jira, ServiceNow, Splunk, and other enterprise systems
"""

import json
import uuid
import base64
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import requests
from urllib.parse import urlencode, quote
import hmac

logger = logging.getLogger(__name__)

class IntegrationType(Enum):
    """Types of enterprise integrations"""
    JIRA = "jira"
    SERVICENOW = "servicenow"
    SPLUNK = "splunk"
    SLACK = "slack"
    MICROSOFT_TEAMS = "microsoft_teams"
    PAGERDUTY = "pagerduty"
    WEBHOOK = "webhook"
    EMAIL = "email"

class TicketPriority(Enum):
    """Ticket priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"

class TicketStatus(Enum):
    """Ticket status"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_FOR_CUSTOMER = "waiting_for_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"

class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class TicketTemplate:
    """Template for creating tickets"""
    template_id: str
    name: str
    integration_type: IntegrationType
    title_template: str
    description_template: str
    priority: TicketPriority
    labels: List[str]
    custom_fields: Dict[str, Any]
    assignee: Optional[str] = None
    project_key: Optional[str] = None

@dataclass
class ComplianceTicket:
    """Compliance-related ticket"""
    ticket_id: str
    external_id: Optional[str]
    integration_type: IntegrationType
    title: str
    description: str
    priority: TicketPriority
    status: TicketStatus
    
    # Compliance context
    scan_id: str
    finding_type: str
    risk_level: str
    affected_systems: List[str]
    gdpr_articles: List[str]
    remediation_steps: List[str]
    
    # Metadata
    created_date: datetime
    updated_date: datetime
    assigned_to: Optional[str]
    due_date: Optional[datetime]
    resolution_notes: Optional[str]

@dataclass
class WebhookConfig:
    """Webhook configuration"""
    webhook_id: str
    name: str
    url: str
    secret: Optional[str]
    headers: Dict[str, str]
    retry_count: int
    timeout_seconds: int
    events: List[str]  # Which events trigger this webhook

class JiraIntegration:
    """Jira integration for compliance ticket management"""
    
    def __init__(self, base_url: str, username: str, api_token: str, project_key: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.api_token = api_token
        self.project_key = project_key
        self.session = requests.Session()
        
        # Set up authentication
        auth_string = f"{username}:{api_token}"
        auth_bytes = auth_string.encode('ascii')
        auth_header = base64.b64encode(auth_bytes).decode('ascii')
        
        self.session.headers.update({
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def create_compliance_ticket(self, ticket: ComplianceTicket) -> Optional[str]:
        """Create a compliance ticket in Jira"""
        
        try:
            # Prepare issue data
            issue_data = {
                "fields": {
                    "project": {"key": self.project_key},
                    "summary": ticket.title,
                    "description": self._format_jira_description(ticket),
                    "issuetype": {"name": "Task"},  # Or "Bug", "Story" based on your Jira config
                    "priority": {"name": self._map_priority_to_jira(ticket.priority)},
                    "labels": [
                        "gdpr_compliance",
                        "dataguardian_pro",
                        f"risk_{ticket.risk_level}",
                        f"scan_{ticket.scan_id}"
                    ]
                }
            }
            
            # Add custom fields if available
            if ticket.gdpr_articles:
                issue_data["fields"]["customfield_gdpr_articles"] = ", ".join(ticket.gdpr_articles)
            
            if ticket.affected_systems:
                issue_data["fields"]["customfield_affected_systems"] = ", ".join(ticket.affected_systems)
            
            # Create issue
            response = self.session.post(
                f"{self.base_url}/rest/api/3/issue",
                json=issue_data,
                timeout=30
            )
            
            if response.status_code == 201:
                issue_data = response.json()
                external_id = issue_data["key"]
                
                # Update ticket with external ID
                ticket.external_id = external_id
                ticket.status = TicketStatus.OPEN
                
                logger.info(f"Created Jira ticket {external_id} for compliance issue")
                return external_id
            else:
                logger.error(f"Failed to create Jira ticket: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating Jira ticket: {e}")
            return None
    
    def _format_jira_description(self, ticket: ComplianceTicket) -> str:
        """Format ticket description for Jira"""
        
        description = f"""
*Compliance Issue Detected by DataGuardian Pro*

*Scan Details:*
* Scan ID: {ticket.scan_id}
* Finding Type: {ticket.finding_type}
* Risk Level: {ticket.risk_level}
* Detection Date: {ticket.created_date.strftime('%Y-%m-%d %H:%M:%S')}

*Affected Systems:*
{chr(10).join(f'* {system}' for system in ticket.affected_systems)}

*GDPR Articles Involved:*
{chr(10).join(f'* Article {article}' for article in ticket.gdpr_articles)}

*Description:*
{ticket.description}

*Recommended Remediation Steps:*
{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(ticket.remediation_steps))}

*Priority Justification:*
This issue has been classified as {ticket.priority.value} priority based on the risk level ({ticket.risk_level}) and potential GDPR compliance impact.

---
_Generated by DataGuardian Pro - Enterprise Privacy Compliance Platform_
        """.strip()
        
        return description
    
    def _map_priority_to_jira(self, priority: TicketPriority) -> str:
        """Map internal priority to Jira priority"""
        
        mapping = {
            TicketPriority.CRITICAL: "Highest",
            TicketPriority.HIGH: "High",
            TicketPriority.MEDIUM: "Medium",
            TicketPriority.LOW: "Low",
            TicketPriority.INFORMATIONAL: "Lowest"
        }
        
        return mapping.get(priority, "Medium")
    
    def update_ticket_status(self, external_id: str, status: TicketStatus, comment: Optional[str] = None) -> bool:
        """Update ticket status in Jira"""
        
        try:
            # Get available transitions
            transitions_response = self.session.get(
                f"{self.base_url}/rest/api/3/issue/{external_id}/transitions",
                timeout=30
            )
            
            if transitions_response.status_code != 200:
                logger.error(f"Failed to get transitions for {external_id}")
                return False
            
            transitions = transitions_response.json()["transitions"]
            
            # Map status to transition
            status_transitions = {
                TicketStatus.IN_PROGRESS: ["In Progress", "Start Progress"],
                TicketStatus.RESOLVED: ["Resolve", "Done", "Resolved"],
                TicketStatus.CLOSED: ["Close", "Closed"]
            }
            
            target_transitions = status_transitions.get(status, [])
            transition_id = None
            
            for transition in transitions:
                if transition["name"] in target_transitions:
                    transition_id = transition["id"]
                    break
            
            if not transition_id:
                logger.warning(f"No suitable transition found for status {status}")
                return False
            
            # Perform transition
            transition_data = {
                "transition": {"id": transition_id}
            }
            
            if comment:
                transition_data["update"] = {
                    "comment": [{"add": {"body": comment}}]
                }
            
            response = self.session.post(
                f"{self.base_url}/rest/api/3/issue/{external_id}/transitions",
                json=transition_data,
                timeout=30
            )
            
            return response.status_code == 204
            
        except Exception as e:
            logger.error(f"Error updating Jira ticket status: {e}")
            return False

class ServiceNowIntegration:
    """ServiceNow integration for incident management"""
    
    def __init__(self, instance_url: str, username: str, password: str):
        self.instance_url = instance_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def create_incident(self, ticket: ComplianceTicket) -> Optional[str]:
        """Create an incident in ServiceNow"""
        
        try:
            incident_data = {
                "short_description": ticket.title,
                "description": self._format_servicenow_description(ticket),
                "urgency": self._map_priority_to_servicenow_urgency(ticket.priority),
                "impact": self._map_risk_to_servicenow_impact(ticket.risk_level),
                "category": "Data Privacy",
                "subcategory": "GDPR Compliance",
                "assignment_group": "Privacy Team",
                "caller_id": self.username,
                "u_scan_id": ticket.scan_id,  # Custom field
                "u_gdpr_articles": ", ".join(ticket.gdpr_articles),  # Custom field
                "u_affected_systems": ", ".join(ticket.affected_systems)  # Custom field
            }
            
            response = self.session.post(
                f"{self.instance_url}/api/now/table/incident",
                json=incident_data,
                timeout=30
            )
            
            if response.status_code == 201:
                incident = response.json()["result"]
                external_id = incident["number"]
                
                ticket.external_id = external_id
                ticket.status = TicketStatus.OPEN
                
                logger.info(f"Created ServiceNow incident {external_id}")
                return external_id
            else:
                logger.error(f"Failed to create ServiceNow incident: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating ServiceNow incident: {e}")
            return None
    
    def _format_servicenow_description(self, ticket: ComplianceTicket) -> str:
        """Format description for ServiceNow"""
        
        return f"""
COMPLIANCE ISSUE DETECTED BY DATAGUARDIAN PRO

Scan ID: {ticket.scan_id}
Finding Type: {ticket.finding_type}
Risk Level: {ticket.risk_level}
Detection Date: {ticket.created_date.strftime('%Y-%m-%d %H:%M:%S')}

AFFECTED SYSTEMS:
{chr(10).join(f'- {system}' for system in ticket.affected_systems)}

GDPR ARTICLES:
{chr(10).join(f'- Article {article}' for article in ticket.gdpr_articles)}

DESCRIPTION:
{ticket.description}

REMEDIATION STEPS:
{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(ticket.remediation_steps))}
        """.strip()
    
    def _map_priority_to_servicenow_urgency(self, priority: TicketPriority) -> str:
        """Map priority to ServiceNow urgency"""
        
        mapping = {
            TicketPriority.CRITICAL: "1",  # High
            TicketPriority.HIGH: "2",     # Medium
            TicketPriority.MEDIUM: "3",   # Low
            TicketPriority.LOW: "3",      # Low
            TicketPriority.INFORMATIONAL: "3"  # Low
        }
        
        return mapping.get(priority, "3")
    
    def _map_risk_to_servicenow_impact(self, risk_level: str) -> str:
        """Map risk level to ServiceNow impact"""
        
        mapping = {
            "critical": "1",  # High
            "high": "2",      # Medium
            "medium": "3",    # Low
            "low": "3"        # Low
        }
        
        return mapping.get(risk_level.lower(), "3")

class SplunkIntegration:
    """Splunk integration for security event logging"""
    
    def __init__(self, splunk_url: str, hec_token: str, index: str = "dataguardian"):
        self.splunk_url = splunk_url.rstrip('/')
        self.hec_token = hec_token
        self.index = index
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Splunk {hec_token}',
            'Content-Type': 'application/json'
        })
    
    def send_compliance_event(self, ticket: ComplianceTicket, event_type: str = "compliance_finding") -> bool:
        """Send compliance event to Splunk"""
        
        try:
            event_data = {
                "time": int(ticket.created_date.timestamp()),
                "index": self.index,
                "source": "dataguardian_pro",
                "sourcetype": "gdpr_compliance",
                "event": {
                    "event_type": event_type,
                    "ticket_id": ticket.ticket_id,
                    "external_id": ticket.external_id,
                    "title": ticket.title,
                    "description": ticket.description,
                    "priority": ticket.priority.value,
                    "status": ticket.status.value,
                    "scan_id": ticket.scan_id,
                    "finding_type": ticket.finding_type,
                    "risk_level": ticket.risk_level,
                    "affected_systems": ticket.affected_systems,
                    "gdpr_articles": ticket.gdpr_articles,
                    "remediation_steps": ticket.remediation_steps,
                    "created_date": ticket.created_date.isoformat(),
                    "assigned_to": ticket.assigned_to,
                    "due_date": ticket.due_date.isoformat() if ticket.due_date else None
                }
            }
            
            response = self.session.post(
                f"{self.splunk_url}/services/collector/event",
                json=event_data,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Sent compliance event to Splunk for ticket {ticket.ticket_id}")
                return True
            else:
                logger.error(f"Failed to send event to Splunk: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending event to Splunk: {e}")
            return False
    
    def send_scan_metrics(self, scan_results: Dict[str, Any]) -> bool:
        """Send scan metrics to Splunk"""
        
        try:
            event_data = {
                "time": int(datetime.now().timestamp()),
                "index": self.index,
                "source": "dataguardian_pro",
                "sourcetype": "scan_metrics",
                "event": {
                    "event_type": "scan_completed",
                    "scan_id": scan_results.get("scan_id"),
                    "scan_type": scan_results.get("scan_type"),
                    "total_findings": scan_results.get("total_findings", 0),
                    "critical_findings": scan_results.get("critical_findings", 0),
                    "high_risk_findings": scan_results.get("high_risk_findings", 0),
                    "compliance_score": scan_results.get("compliance_score", 0),
                    "scan_duration_seconds": scan_results.get("scan_duration_seconds", 0),
                    "files_scanned": scan_results.get("files_scanned", 0),
                    "region": scan_results.get("region", "Netherlands"),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            response = self.session.post(
                f"{self.splunk_url}/services/collector/event",
                json=event_data,
                timeout=30
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error sending scan metrics to Splunk: {e}")
            return False

class WebhookIntegration:
    """Generic webhook integration"""
    
    def __init__(self, webhook_config: WebhookConfig):
        self.config = webhook_config
        self.session = requests.Session()
    
    def send_webhook(self, payload: Dict[str, Any], event_type: str) -> bool:
        """Send webhook with payload"""
        
        if event_type not in self.config.events:
            return True  # Event not configured for this webhook
        
        try:
            headers = self.config.headers.copy()
            
            # Add signature if secret is configured
            if self.config.secret:
                payload_json = json.dumps(payload, sort_keys=True)
                signature = hmac.new(
                    self.config.secret.encode(),
                    payload_json.encode(),
                    hashlib.sha256
                ).hexdigest()
                headers['X-Signature-SHA256'] = f'sha256={signature}'
            
            # Add standard headers
            headers.update({
                'Content-Type': 'application/json',
                'User-Agent': 'DataGuardian-Pro-Webhook/1.0',
                'X-Event-Type': event_type
            })
            
            response = self.session.post(
                self.config.url,
                json=payload,
                headers=headers,
                timeout=self.config.timeout_seconds
            )
            
            if 200 <= response.status_code < 300:
                logger.info(f"Webhook {self.config.name} sent successfully")
                return True
            else:
                logger.error(f"Webhook {self.config.name} failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending webhook {self.config.name}: {e}")
            return False

class EnterpriseTicketingManager:
    """Central manager for enterprise ticketing integrations"""
    
    def __init__(self):
        self.integrations: Dict[str, Any] = {}
        self.templates: Dict[str, TicketTemplate] = {}
        self.webhooks: Dict[str, WebhookIntegration] = {}
        self.tickets: Dict[str, ComplianceTicket] = {}
        
        # Initialize default templates
        self._initialize_default_templates()
    
    def _initialize_default_templates(self):
        """Initialize default ticket templates"""
        
        # Critical GDPR violation template
        critical_template = TicketTemplate(
            template_id="gdpr_critical",
            name="Critical GDPR Violation",
            integration_type=IntegrationType.JIRA,
            title_template="CRITICAL: GDPR Violation Detected - {finding_type}",
            description_template="Critical GDPR compliance violation requiring immediate attention. Risk level: {risk_level}. Affected systems: {affected_systems}.",
            priority=TicketPriority.CRITICAL,
            labels=["gdpr", "critical", "compliance"],
            custom_fields={
                "environment": "production",
                "compliance_framework": "GDPR"
            }
        )
        
        self.templates["gdpr_critical"] = critical_template
        
        # High-risk PII exposure template
        pii_template = TicketTemplate(
            template_id="pii_exposure",
            name="PII Exposure Detected",
            integration_type=IntegrationType.SERVICENOW,
            title_template="PII Exposure: {finding_type} in {affected_systems}",
            description_template="Personally identifiable information exposure detected. Immediate review required for GDPR compliance.",
            priority=TicketPriority.HIGH,
            labels=["pii", "exposure", "privacy"],
            custom_fields={
                "data_classification": "confidential"
            }
        )
        
        self.templates["pii_exposure"] = pii_template
    
    def add_jira_integration(self, name: str, base_url: str, username: str, api_token: str, project_key: str):
        """Add Jira integration"""
        self.integrations[name] = JiraIntegration(base_url, username, api_token, project_key)
        logger.info(f"Added Jira integration: {name}")
    
    def add_servicenow_integration(self, name: str, instance_url: str, username: str, password: str):
        """Add ServiceNow integration"""
        self.integrations[name] = ServiceNowIntegration(instance_url, username, password)
        logger.info(f"Added ServiceNow integration: {name}")
    
    def add_splunk_integration(self, name: str, splunk_url: str, hec_token: str, index: str = "dataguardian"):
        """Add Splunk integration"""
        self.integrations[name] = SplunkIntegration(splunk_url, hec_token, index)
        logger.info(f"Added Splunk integration: {name}")
    
    def add_webhook(self, webhook_config: WebhookConfig):
        """Add webhook integration"""
        self.webhooks[webhook_config.webhook_id] = WebhookIntegration(webhook_config)
        logger.info(f"Added webhook: {webhook_config.name}")
    
    def create_compliance_ticket(self,
                                finding_type: str,
                                description: str,
                                risk_level: str,
                                scan_id: str,
                                affected_systems: List[str],
                                gdpr_articles: List[str],
                                remediation_steps: List[str],
                                template_id: Optional[str] = None,
                                integration_name: Optional[str] = None) -> Optional[ComplianceTicket]:
        """Create a compliance ticket using template and integration"""
        
        ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Select template
        template = None
        if template_id and template_id in self.templates:
            template = self.templates[template_id]
        else:
            # Auto-select template based on risk level
            if risk_level.lower() == "critical":
                template = self.templates.get("gdpr_critical")
            elif finding_type.lower() in ["pii", "personal_data"]:
                template = self.templates.get("pii_exposure")
        
        # Determine priority
        priority_map = {
            "critical": TicketPriority.CRITICAL,
            "high": TicketPriority.HIGH,
            "medium": TicketPriority.MEDIUM,
            "low": TicketPriority.LOW
        }
        priority = priority_map.get(risk_level.lower(), TicketPriority.MEDIUM)
        
        # Format title and description using template
        if template:
            title = template.title_template.format(
                finding_type=finding_type,
                risk_level=risk_level,
                affected_systems=", ".join(affected_systems)
            )
            formatted_description = template.description_template.format(
                finding_type=finding_type,
                risk_level=risk_level,
                affected_systems=", ".join(affected_systems)
            ) + "\n\n" + description
        else:
            title = f"{finding_type} - Risk Level: {risk_level}"
            formatted_description = description
        
        # Create ticket object
        ticket = ComplianceTicket(
            ticket_id=ticket_id,
            external_id=None,
            integration_type=template.integration_type if template else IntegrationType.JIRA,
            title=title,
            description=formatted_description,
            priority=priority,
            status=TicketStatus.OPEN,
            scan_id=scan_id,
            finding_type=finding_type,
            risk_level=risk_level,
            affected_systems=affected_systems,
            gdpr_articles=gdpr_articles,
            remediation_steps=remediation_steps,
            created_date=datetime.now(),
            updated_date=datetime.now(),
            assigned_to=None,
            due_date=self._calculate_due_date(priority),
            resolution_notes=None
        )
        
        # Create ticket in external system
        if integration_name and integration_name in self.integrations:
            integration = self.integrations[integration_name]
            
            if isinstance(integration, JiraIntegration):
                external_id = integration.create_compliance_ticket(ticket)
            elif isinstance(integration, ServiceNowIntegration):
                external_id = integration.create_incident(ticket)
            
            if external_id:
                ticket.external_id = external_id
            else:
                logger.error(f"Failed to create external ticket in {integration_name}")
        
        # Store ticket
        self.tickets[ticket_id] = ticket
        
        # Send to Splunk if configured
        splunk_integrations = [i for i in self.integrations.values() if isinstance(i, SplunkIntegration)]
        for splunk in splunk_integrations:
            splunk.send_compliance_event(ticket)
        
        # Send webhooks
        self._send_webhooks("ticket_created", {
            "ticket_id": ticket.ticket_id,
            "external_id": ticket.external_id,
            "title": ticket.title,
            "priority": ticket.priority.value,
            "risk_level": ticket.risk_level,
            "scan_id": ticket.scan_id,
            "created_date": ticket.created_date.isoformat()
        })
        
        logger.info(f"Created compliance ticket {ticket_id} with external ID {ticket.external_id}")
        return ticket
    
    def _calculate_due_date(self, priority: TicketPriority) -> Optional[datetime]:
        """Calculate due date based on priority"""
        
        due_date_map = {
            TicketPriority.CRITICAL: timedelta(hours=4),   # 4 hours for critical
            TicketPriority.HIGH: timedelta(days=1),        # 1 day for high
            TicketPriority.MEDIUM: timedelta(days=3),      # 3 days for medium
            TicketPriority.LOW: timedelta(days=7),         # 1 week for low
            TicketPriority.INFORMATIONAL: None             # No due date for informational
        }
        
        delta = due_date_map.get(priority)
        return datetime.now() + delta if delta else None
    
    def _send_webhooks(self, event_type: str, payload: Dict[str, Any]):
        """Send webhooks for event"""
        
        for webhook in self.webhooks.values():
            webhook.send_webhook(payload, event_type)
    
    def update_ticket_status(self, ticket_id: str, status: TicketStatus, resolution_notes: Optional[str] = None) -> bool:
        """Update ticket status"""
        
        if ticket_id not in self.tickets:
            logger.error(f"Ticket {ticket_id} not found")
            return False
        
        ticket = self.tickets[ticket_id]
        old_status = ticket.status
        
        ticket.status = status
        ticket.updated_date = datetime.now()
        
        if resolution_notes:
            ticket.resolution_notes = resolution_notes
        
        # Update external system
        success = True
        for integration in self.integrations.values():
            if isinstance(integration, JiraIntegration) and ticket.external_id:
                success &= integration.update_ticket_status(ticket.external_id, status, resolution_notes)
        
        # Send webhook
        self._send_webhooks("ticket_updated", {
            "ticket_id": ticket.ticket_id,
            "external_id": ticket.external_id,
            "old_status": old_status.value,
            "new_status": status.value,
            "resolution_notes": resolution_notes,
            "updated_date": ticket.updated_date.isoformat()
        })
        
        return success
    
    def get_ticket_analytics(self) -> Dict[str, Any]:
        """Get ticket analytics and metrics"""
        
        total_tickets = len(self.tickets)
        
        # Status breakdown
        status_counts = {}
        for status in TicketStatus:
            status_counts[status.value] = len([t for t in self.tickets.values() if t.status == status])
        
        # Priority breakdown
        priority_counts = {}
        for priority in TicketPriority:
            priority_counts[priority.value] = len([t for t in self.tickets.values() if t.priority == priority])
        
        # Risk level breakdown
        risk_counts = {}
        for ticket in self.tickets.values():
            risk_level = ticket.risk_level
            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
        
        # Overdue tickets
        now = datetime.now()
        overdue_tickets = [
            t for t in self.tickets.values() 
            if t.due_date and t.due_date < now and t.status not in [TicketStatus.RESOLVED, TicketStatus.CLOSED]
        ]
        
        # Average resolution time
        resolved_tickets = [t for t in self.tickets.values() if t.status == TicketStatus.RESOLVED]
        avg_resolution_time = 0
        if resolved_tickets:
            total_time = sum((t.updated_date - t.created_date).total_seconds() for t in resolved_tickets)
            avg_resolution_time = total_time / len(resolved_tickets) / 3600  # Convert to hours
        
        return {
            "total_tickets": total_tickets,
            "status_breakdown": status_counts,
            "priority_breakdown": priority_counts,
            "risk_level_breakdown": risk_counts,
            "overdue_tickets": len(overdue_tickets),
            "average_resolution_time_hours": round(avg_resolution_time, 2),
            "resolution_rate": (len(resolved_tickets) / total_tickets * 100) if total_tickets > 0 else 0,
            "created_last_24h": len([
                t for t in self.tickets.values() 
                if (now - t.created_date).total_seconds() < 86400
            ]),
            "created_last_7d": len([
                t for t in self.tickets.values() 
                if (now - t.created_date).total_seconds() < 604800
            ])
        }
    
    def export_tickets(self, status_filter: Optional[TicketStatus] = None) -> List[Dict[str, Any]]:
        """Export tickets for reporting"""
        
        tickets_to_export = self.tickets.values()
        
        if status_filter:
            tickets_to_export = [t for t in tickets_to_export if t.status == status_filter]
        
        return [
            {
                "ticket_id": ticket.ticket_id,
                "external_id": ticket.external_id,
                "integration_type": ticket.integration_type.value,
                "title": ticket.title,
                "description": ticket.description,
                "priority": ticket.priority.value,
                "status": ticket.status.value,
                "scan_id": ticket.scan_id,
                "finding_type": ticket.finding_type,
                "risk_level": ticket.risk_level,
                "affected_systems": ticket.affected_systems,
                "gdpr_articles": ticket.gdpr_articles,
                "remediation_steps": ticket.remediation_steps,
                "created_date": ticket.created_date.isoformat(),
                "updated_date": ticket.updated_date.isoformat(),
                "assigned_to": ticket.assigned_to,
                "due_date": ticket.due_date.isoformat() if ticket.due_date else None,
                "resolution_notes": ticket.resolution_notes
            }
            for ticket in tickets_to_export
        ]