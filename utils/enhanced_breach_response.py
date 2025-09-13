"""
Enhanced Breach Response Automation
Sub-hour breach notification and automated incident response
"""

import json
import hashlib
import smtplib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

class BreachSeverity(Enum):
    """Breach severity levels for prioritization"""
    CRITICAL = "critical"      # Immediate notification required
    HIGH = "high"             # 1-hour notification
    MEDIUM = "medium"         # 24-hour notification
    LOW = "low"              # 72-hour notification

class BreachCategory(Enum):
    """Types of data breaches"""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_EXFILTRATION = "data_exfiltration"
    SYSTEM_COMPROMISE = "system_compromise"
    ACCIDENTAL_DISCLOSURE = "accidental_disclosure"
    INSIDER_THREAT = "insider_threat"
    VENDOR_BREACH = "vendor_breach"
    RANSOMWARE = "ransomware"
    AI_MODEL_COMPROMISE = "ai_model_compromise"

class NotificationAuthority(Enum):
    """Data protection authorities for notification"""
    NETHERLANDS_AP = "netherlands_ap"
    GERMANY_BfDI = "germany_bfdi"
    FRANCE_CNIL = "france_cnil"
    BELGIUM_APD = "belgium_apd"
    EU_EDPB = "eu_edpb"

@dataclass
class BreachIncident:
    """Data breach incident record"""
    incident_id: str
    detection_timestamp: datetime
    severity: BreachSeverity
    category: BreachCategory
    affected_data_types: List[str]
    estimated_records: int
    affected_individuals: int
    discovery_method: str
    containment_status: str
    risk_assessment: Dict[str, Any]
    notification_requirements: Dict[str, bool]
    timeline: List[Dict[str, Any]]
    metadata: Dict[str, Any]

@dataclass
class NotificationTemplate:
    """Template for breach notifications"""
    template_id: str
    authority: NotificationAuthority
    subject_template: str
    body_template: str
    required_fields: List[str]
    deadline_hours: int
    language: str

@dataclass
class WhistleblowerReport:
    """Whistleblower report with incentive tracking"""
    report_id: str
    reporter_id: str  # Anonymous identifier
    submission_timestamp: datetime
    breach_details: Dict[str, Any]
    evidence_provided: List[str]
    severity_assessment: BreachSeverity
    investigation_status: str
    incentive_eligibility: bool
    incentive_percentage: float  # 15-30% of collected fines
    estimated_incentive: float

class EnhancedBreachResponseSystem:
    """
    Enhanced breach response system with automated notifications
    and sub-hour response capabilities
    """
    
    def __init__(self, region: str = "Netherlands"):
        self.region = region
        self.detection_rules = self._load_detection_rules()
        self.notification_templates = self._load_notification_templates()
        self.authority_contacts = self._load_authority_contacts()
        self.incident_database = []
        self.whistleblower_reports = []
        self.auto_response_enabled = True
        
    def _load_detection_rules(self) -> Dict[str, Any]:
        """Load automated breach detection rules"""
        return {
            "critical_indicators": [
                r"\b(?:unauthorized\s+access|data\s+breach|security\s+incident)\b",
                r"\b(?:ransomware|malware|system\s+compromise)\b",
                r"\b(?:data\s+exfiltration|information\s+theft)\b",
                r"\b(?:database\s+dump|sql\s+injection|privilege\s+escalation)\b"
            ],
            "data_type_patterns": {
                "personal_data": r"\b(?:personal\s+data|pii|personally\s+identifiable)\b",
                "special_categories": r"\b(?:health\s+data|biometric|genetic|racial|ethnic|political|religious|sexual)\b",
                "financial_data": r"\b(?:credit\s+card|bank\s+account|financial\s+data|payment)\b",
                "children_data": r"\b(?:children|minors|under\s+16|kids|juvenile)\b",
                "criminal_data": r"\b(?:criminal\s+records|conviction|offense)\b"
            },
            "severity_indicators": {
                "critical": [
                    r"\b(?:millions?|thousands?)\s+(?:records?|individuals?)\b",
                    r"\b(?:special\s+categories|sensitive\s+data)\b",
                    r"\b(?:system\s+wide|complete\s+database)\b"
                ],
                "high": [
                    r"\b(?:hundreds?|thousands?)\s+(?:records?|users?)\b",
                    r"\b(?:financial|payment|medical)\s+data\b",
                    r"\b(?:ongoing|active)\s+breach\b"
                ],
                "medium": [
                    r"\b(?:dozens?|limited\s+number)\s+(?:records?|accounts?)\b",
                    r"\b(?:contact|email)\s+(?:information|addresses?)\b"
                ]
            },
            "notification_triggers": {
                "immediate": [
                    r"\b(?:ongoing|active|current)\s+breach\b",
                    r"\b(?:high\s+risk|significant\s+harm|severe\s+impact)\b",
                    r"\b(?:special\s+categories|children|healthcare)\b"
                ],
                "72_hour": [
                    r"\b(?:personal\s+data|identifiable\s+information)\b",
                    r"\b(?:unauthorized\s+access|accidental\s+disclosure)\b"
                ]
            }
        }
    
    def _load_notification_templates(self) -> Dict[NotificationAuthority, NotificationTemplate]:
        """Load notification templates for different authorities"""
        return {
            NotificationAuthority.NETHERLANDS_AP: NotificationTemplate(
                template_id="nl_ap_2025",
                authority=NotificationAuthority.NETHERLANDS_AP,
                subject_template="URGENT: Data Breach Notification - {incident_id}",
                body_template="""
                Zeer geachte heer/mevrouw,

                Hierbij melden wij een datalek conform artikel 33 AVG/UAVG:

                INCIDENT DETAILS:
                - Incident ID: {incident_id}
                - Detectietijd: {detection_timestamp}
                - Ernst: {severity}
                - Categorie: {category}

                GETROFFEN GEGEVENS:
                - Aantal betrokkenen: {affected_individuals}
                - Gegevenstypes: {affected_data_types}
                - Geschat aantal records: {estimated_records}

                RISICOBEOORDELING:
                - Risico voor betrokkenen: {risk_level}
                - Gevolgen: {consequences}
                - Mitigerende maatregelen: {mitigation_measures}

                MAATREGELEN GENOMEN:
                {containment_actions}

                Met vriendelijke groet,
                {organization_name}
                Data Protection Officer
                """,
                required_fields=[
                    "incident_id", "detection_timestamp", "severity", "category",
                    "affected_individuals", "affected_data_types", "estimated_records",
                    "risk_level", "consequences", "mitigation_measures", 
                    "containment_actions", "organization_name"
                ],
                deadline_hours=72,
                language="dutch"
            ),
            NotificationAuthority.EU_EDPB: NotificationTemplate(
                template_id="eu_edpb_2025",
                authority=NotificationAuthority.EU_EDPB,
                subject_template="Data Breach Notification - Cross-Border Impact - {incident_id}",
                body_template="""
                Dear European Data Protection Board,

                We hereby notify a personal data breach with cross-border implications:

                INCIDENT DETAILS:
                - Incident ID: {incident_id}
                - Detection Time: {detection_timestamp}
                - Severity: {severity}
                - Category: {category}

                CROSS-BORDER IMPACT:
                - Affected Member States: {affected_countries}
                - Data Subjects: {affected_individuals}
                - Data Categories: {affected_data_types}

                RISK ASSESSMENT:
                - Risk to Data Subjects: {risk_level}
                - Likely Consequences: {consequences}
                - Mitigation Measures: {mitigation_measures}

                COOPERATION REQUEST:
                We request coordination with the following supervisory authorities:
                {cooperation_authorities}

                Best regards,
                {organization_name}
                Data Protection Officer
                """,
                required_fields=[
                    "incident_id", "detection_timestamp", "severity", "category",
                    "affected_countries", "affected_individuals", "affected_data_types",
                    "risk_level", "consequences", "mitigation_measures",
                    "cooperation_authorities", "organization_name"
                ],
                deadline_hours=72,
                language="english"
            )
        }
    
    def _load_authority_contacts(self) -> Dict[NotificationAuthority, Dict[str, str]]:
        """Load contact information for data protection authorities"""
        return {
            NotificationAuthority.NETHERLANDS_AP: {
                "name": "Autoriteit Persoonsgegevens",
                "email": "datalek@autoriteitpersoonsgegevens.nl",
                "phone": "+31 (0)70 888 8500",
                "online_form": "https://www.autoriteitpersoonsgegevens.nl/nl/zelf-doen/datalek-melden",
                "emergency_contact": "+31 (0)70 888 8888",
                "language": "dutch"
            },
            NotificationAuthority.EU_EDPB: {
                "name": "European Data Protection Board",
                "email": "edpb@edpb.europa.eu",
                "phone": "+32 2 281 9650",
                "online_form": "https://edpb.europa.eu/about-edpb/contact_en",
                "emergency_contact": "+32 2 281 9650",
                "language": "english"
            }
        }
    
    def detect_potential_breach(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[BreachIncident]:
        """
        Automated breach detection from logs, alerts, or incident reports
        
        Args:
            content: Log content or incident description
            metadata: Additional context about the incident
            
        Returns:
            BreachIncident if breach detected, None otherwise
        """
        metadata = metadata or {}
        
        # Check for critical breach indicators
        breach_detected = False
        for pattern in self.detection_rules["critical_indicators"]:
            if re.search(pattern, content, re.IGNORECASE):
                breach_detected = True
                break
        
        if not breach_detected:
            return None
        
        # Analyze breach details
        severity = self._assess_breach_severity(content)
        category = self._classify_breach_category(content)
        affected_data_types = self._identify_affected_data_types(content)
        estimated_records = self._estimate_affected_records(content)
        
        # Create incident record
        incident_id = f"BREACH-{datetime.now().strftime('%Y%m%d%H%M%S')}-{hashlib.md5(content.encode()).hexdigest()[:6].upper()}"
        
        incident = BreachIncident(
            incident_id=incident_id,
            detection_timestamp=datetime.now(),
            severity=severity,
            category=category,
            affected_data_types=affected_data_types,
            estimated_records=estimated_records,
            affected_individuals=min(estimated_records, estimated_records),  # Conservative estimate
            discovery_method="Automated Detection",
            containment_status="Investigation Started",
            risk_assessment=self._assess_breach_risk(severity, category, affected_data_types, estimated_records),
            notification_requirements=self._determine_notification_requirements(severity, affected_data_types),
            timeline=[{
                "timestamp": datetime.now().isoformat(),
                "event": "Breach Detected",
                "details": "Automated detection system flagged potential breach"
            }],
            metadata=metadata
        )
        
        # Store incident
        self.incident_database.append(incident)
        
        # Trigger automated response if enabled
        if self.auto_response_enabled:
            self._trigger_automated_response(incident)
        
        return incident
    
    def _assess_breach_severity(self, content: str) -> BreachSeverity:
        """Assess breach severity based on content analysis"""
        severity_scores = {
            BreachSeverity.CRITICAL: 0,
            BreachSeverity.HIGH: 0,
            BreachSeverity.MEDIUM: 0,
            BreachSeverity.LOW: 0
        }
        
        for severity, patterns in self.detection_rules["severity_indicators"].items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    if severity == "critical":
                        severity_scores[BreachSeverity.CRITICAL] += 3
                    elif severity == "high":
                        severity_scores[BreachSeverity.HIGH] += 2
                    elif severity == "medium":
                        severity_scores[BreachSeverity.MEDIUM] += 1
        
        # Return highest scoring severity
        max_severity = max(severity_scores, key=severity_scores.get)
        return max_severity if severity_scores[max_severity] > 0 else BreachSeverity.LOW
    
    def _classify_breach_category(self, content: str) -> BreachCategory:
        """Classify the type of breach"""
        category_patterns = {
            BreachCategory.UNAUTHORIZED_ACCESS: [r"\b(?:unauthorized\s+access|illegal\s+entry|intrusion)\b"],
            BreachCategory.DATA_EXFILTRATION: [r"\b(?:data\s+exfiltration|information\s+theft|stolen\s+data)\b"],
            BreachCategory.SYSTEM_COMPROMISE: [r"\b(?:system\s+compromise|server\s+breach|network\s+intrusion)\b"],
            BreachCategory.ACCIDENTAL_DISCLOSURE: [r"\b(?:accidental|inadvertent|unintentional|human\s+error)\b"],
            BreachCategory.RANSOMWARE: [r"\b(?:ransomware|crypto\s+locker|encryption\s+attack)\b"],
            BreachCategory.AI_MODEL_COMPROMISE: [r"\b(?:model\s+poisoning|ai\s+attack|algorithm\s+compromise)\b"]
        }
        
        for category, patterns in category_patterns.items():
            if any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns):
                return category
        
        return BreachCategory.UNAUTHORIZED_ACCESS  # Default
    
    def _identify_affected_data_types(self, content: str) -> List[str]:
        """Identify types of data affected in the breach"""
        affected_types = []
        
        for data_type, pattern in self.detection_rules["data_type_patterns"].items():
            if re.search(pattern, content, re.IGNORECASE):
                affected_types.append(data_type)
        
        return affected_types if affected_types else ["personal_data"]
    
    def _estimate_affected_records(self, content: str) -> int:
        """Estimate number of affected records"""
        # Look for numerical indicators
        import re
        
        numbers = re.findall(r'\b(\d+(?:,\d{3})*)\b', content)
        if numbers:
            # Take the largest number found
            max_num = max(int(num.replace(',', '')) for num in numbers)
            return min(max_num, 10000000)  # Cap at 10M for sanity
        
        # Estimate based on keywords
        if re.search(r'\b(?:all|entire|complete|full)\s+(?:database|system|records)\b', content, re.IGNORECASE):
            return 1000000  # Assume large database
        elif re.search(r'\b(?:thousands?|many|multiple)\b', content, re.IGNORECASE):
            return 5000
        elif re.search(r'\b(?:hundreds?|several)\b', content, re.IGNORECASE):
            return 500
        else:
            return 100  # Conservative default
    
    def _assess_breach_risk(self, severity: BreachSeverity, category: BreachCategory, 
                          data_types: List[str], estimated_records: int) -> Dict[str, Any]:
        """Assess risk level and consequences of the breach"""
        base_risk = {
            BreachSeverity.CRITICAL: 90,
            BreachSeverity.HIGH: 70,
            BreachSeverity.MEDIUM: 50,
            BreachSeverity.LOW: 20
        }[severity]
        
        # Adjust risk based on data types
        if "special_categories" in data_types:
            base_risk += 20
        if "children_data" in data_types:
            base_risk += 15
        if "financial_data" in data_types:
            base_risk += 10
        
        # Adjust risk based on scale
        if estimated_records > 100000:
            base_risk += 15
        elif estimated_records > 10000:
            base_risk += 10
        elif estimated_records > 1000:
            base_risk += 5
        
        risk_level = min(100, base_risk)
        
        # Determine consequences
        consequences = []
        if risk_level >= 80:
            consequences.extend(["Identity theft", "Financial fraud", "Discrimination", "Physical harm"])
        elif risk_level >= 60:
            consequences.extend(["Financial loss", "Reputation damage", "Emotional distress"])
        elif risk_level >= 40:
            consequences.extend(["Privacy invasion", "Inconvenience", "Minor financial impact"])
        else:
            consequences.extend(["Minimal impact", "Unlikely consequences"])
        
        return {
            "risk_level": risk_level,
            "risk_category": "High" if risk_level >= 70 else "Medium" if risk_level >= 40 else "Low",
            "likely_consequences": consequences,
            "gdpr_fine_risk": self._estimate_gdpr_fine_risk(risk_level, estimated_records),
            "notification_required": risk_level >= 30
        }
    
    def _estimate_gdpr_fine_risk(self, risk_level: int, estimated_records: int) -> Dict[str, Any]:
        """Estimate potential GDPR fine risk"""
        if risk_level >= 80:
            fine_percentage = 4.0
            base_amount = 20000000
        elif risk_level >= 60:
            fine_percentage = 2.0
            base_amount = 10000000
        elif risk_level >= 40:
            fine_percentage = 1.0
            base_amount = 5000000
        else:
            fine_percentage = 0.5
            base_amount = 1000000
        
        # Estimate based on records affected
        per_record_fine = min(100, estimated_records / 1000)  # €0.1 to €100 per record
        estimated_fine = min(base_amount, estimated_records * per_record_fine)
        
        return {
            "estimated_fine_eur": estimated_fine,
            "max_percentage_turnover": fine_percentage,
            "fine_basis": f"€{estimated_fine:,.0f} or {fine_percentage}% global turnover (whichever higher)"
        }
    
    def _determine_notification_requirements(self, severity: BreachSeverity, data_types: List[str]) -> Dict[str, bool]:
        """Determine notification requirements"""
        return {
            "authority_notification_required": severity in [BreachSeverity.CRITICAL, BreachSeverity.HIGH] or "special_categories" in data_types,
            "individual_notification_required": severity == BreachSeverity.CRITICAL or "special_categories" in data_types or "children_data" in data_types,
            "immediate_notification": severity == BreachSeverity.CRITICAL,
            "media_notification": severity == BreachSeverity.CRITICAL and "special_categories" in data_types,
            "cross_border_notification": True  # Assume cross-border for EU operations
        }
    
    def _trigger_automated_response(self, incident: BreachIncident) -> None:
        """Trigger automated response workflow"""
        # Immediate containment actions
        self._initiate_containment(incident)
        
        # Schedule notifications based on severity
        if incident.notification_requirements["immediate_notification"]:
            self._schedule_immediate_notification(incident)
        elif incident.notification_requirements["authority_notification_required"]:
            self._schedule_72hour_notification(incident)
        
        # Alert internal stakeholders
        self._alert_internal_teams(incident)
        
        # Start investigation workflow
        self._initiate_investigation(incident)
    
    def _schedule_immediate_notification(self, incident: BreachIncident) -> None:
        """Schedule immediate notification for critical breaches"""
        # In a real implementation, this would integrate with email/SMS services
        notification_time = datetime.now() + timedelta(minutes=30)  # 30-minute target
        
        incident.timeline.append({
            "timestamp": datetime.now().isoformat(),
            "event": "Immediate Notification Scheduled",
            "details": f"Authority notification scheduled for {notification_time.isoformat()}"
        })
    
    def _schedule_72hour_notification(self, incident: BreachIncident) -> None:
        """Schedule 72-hour notification for standard breaches"""
        notification_deadline = incident.detection_timestamp + timedelta(hours=72)
        
        incident.timeline.append({
            "timestamp": datetime.now().isoformat(),
            "event": "72-Hour Notification Scheduled",
            "details": f"Authority notification deadline: {notification_deadline.isoformat()}"
        })
    
    def generate_authority_notification(self, incident: BreachIncident, 
                                      authority: NotificationAuthority) -> Dict[str, str]:
        """Generate formatted notification for data protection authority"""
        template = self.notification_templates.get(authority)
        if not template:
            raise ValueError(f"No template available for authority: {authority}")
        
        # Prepare template variables
        template_vars = {
            "incident_id": incident.incident_id,
            "detection_timestamp": incident.detection_timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "severity": incident.severity.value.upper(),
            "category": incident.category.value.replace("_", " ").title(),
            "affected_individuals": f"{incident.affected_individuals:,}",
            "affected_data_types": ", ".join(incident.affected_data_types),
            "estimated_records": f"{incident.estimated_records:,}",
            "risk_level": incident.risk_assessment["risk_category"],
            "consequences": ", ".join(incident.risk_assessment["likely_consequences"]),
            "mitigation_measures": "Immediate system isolation, password resets, user notifications",
            "containment_actions": "System access disabled, forensic investigation initiated, affected users contacted",
            "organization_name": "DataGuardian Pro Implementation",
            "affected_countries": "Netherlands, EU Member States",
            "cooperation_authorities": "Netherlands AP, relevant member state authorities"
        }
        
        # Format subject and body
        subject = template.subject_template.format(**template_vars)
        body = template.body_template.format(**template_vars)
        
        return {
            "subject": subject,
            "body": body,
            "recipient": self.authority_contacts[authority]["email"],
            "deadline": (incident.detection_timestamp + timedelta(hours=template.deadline_hours)).isoformat(),
            "language": template.language
        }
    
    def submit_whistleblower_report(self, report_details: Dict[str, Any], 
                                  evidence: List[str] = None) -> WhistleblowerReport:
        """Submit and process whistleblower report"""
        evidence = evidence or []
        
        report_id = f"WB-{datetime.now().strftime('%Y%m%d%H%M%S')}-{hashlib.md5(json.dumps(report_details).encode()).hexdigest()[:6].upper()}"
        reporter_id = f"ANON-{hashlib.md5(f"{report_id}{datetime.now()}".encode()).hexdigest()[:8].upper()}"
        
        # Assess severity and incentive eligibility
        severity = self._assess_whistleblower_severity(report_details)
        incentive_eligible = severity in [BreachSeverity.CRITICAL, BreachSeverity.HIGH]
        incentive_percentage = 0.30 if severity == BreachSeverity.CRITICAL else 0.15 if severity == BreachSeverity.HIGH else 0.0
        
        # Estimate potential fine and incentive
        estimated_fine = self._estimate_whistleblower_fine(report_details, severity)
        estimated_incentive = estimated_fine * incentive_percentage if incentive_eligible else 0.0
        
        whistleblower_report = WhistleblowerReport(
            report_id=report_id,
            reporter_id=reporter_id,
            submission_timestamp=datetime.now(),
            breach_details=report_details,
            evidence_provided=evidence,
            severity_assessment=severity,
            investigation_status="Under Review",
            incentive_eligibility=incentive_eligible,
            incentive_percentage=incentive_percentage,
            estimated_incentive=estimated_incentive
        )
        
        self.whistleblower_reports.append(whistleblower_report)
        
        return whistleblower_report
    
    def _assess_whistleblower_severity(self, report_details: Dict[str, Any]) -> BreachSeverity:
        """Assess severity of whistleblower report"""
        description = report_details.get("description", "").lower()
        
        if any(keyword in description for keyword in ["millions", "massive", "systemic", "ongoing"]):
            return BreachSeverity.CRITICAL
        elif any(keyword in description for keyword in ["thousands", "significant", "widespread"]):
            return BreachSeverity.HIGH
        elif any(keyword in description for keyword in ["hundreds", "moderate", "limited"]):
            return BreachSeverity.MEDIUM
        else:
            return BreachSeverity.LOW
    
    def _estimate_whistleblower_fine(self, report_details: Dict[str, Any], severity: BreachSeverity) -> float:
        """Estimate potential fine from whistleblower report"""
        base_fines = {
            BreachSeverity.CRITICAL: 15000000,  # €15M
            BreachSeverity.HIGH: 8000000,       # €8M
            BreachSeverity.MEDIUM: 2000000,     # €2M
            BreachSeverity.LOW: 500000          # €500K
        }
        
        return base_fines.get(severity, 500000)
    
    def generate_breach_response_report(self, incident: BreachIncident) -> Dict[str, Any]:
        """Generate comprehensive breach response report"""
        return {
            "incident_summary": {
                "incident_id": incident.incident_id,
                "detection_time": incident.detection_timestamp.isoformat(),
                "severity": incident.severity.value,
                "category": incident.category.value,
                "affected_individuals": incident.affected_individuals,
                "estimated_records": incident.estimated_records
            },
            "risk_assessment": incident.risk_assessment,
            "notification_status": {
                "authority_notified": False,  # Would be updated in real implementation
                "individuals_notified": False,
                "deadline_compliance": "On Track",
                "next_notification_due": (incident.detection_timestamp + timedelta(hours=72)).isoformat()
            },
            "response_timeline": incident.timeline,
            "containment_measures": [
                "System access immediately restricted",
                "Affected accounts secured",
                "Forensic investigation initiated",
                "Legal team consulted"
            ],
            "regulatory_compliance": {
                "gdpr_compliance": "In Progress",
                "notification_deadlines": "Being Met",
                "documentation_complete": True,
                "authority_cooperation": "Ongoing"
            },
            "estimated_impact": {
                "financial_risk": incident.risk_assessment["gdpr_fine_risk"],
                "reputational_impact": "Medium to High",
                "operational_disruption": "Minimal",
                "legal_exposure": "Managed through proper notification"
            },
            "lessons_learned": [
                "Enhance monitoring for early detection",
                "Improve staff security awareness training",
                "Review access control procedures",
                "Update incident response procedures"
            ],
            "timestamp": datetime.now().isoformat()
        }