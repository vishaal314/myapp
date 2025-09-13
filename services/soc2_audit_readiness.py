#!/usr/bin/env python3
"""
SOC2 Type II Audit Readiness and Compliance Tracking
Comprehensive SOC2 audit preparation and continuous compliance monitoring
"""

import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)

class SOC2TrustService(Enum):
    """SOC2 Trust Service Categories"""
    SECURITY = "security"
    AVAILABILITY = "availability"
    PROCESSING_INTEGRITY = "processing_integrity"
    CONFIDENTIALITY = "confidentiality"
    PRIVACY = "privacy"

class ControlType(Enum):
    """Types of SOC2 controls"""
    ENTITY_LEVEL = "entity_level"
    PROCESS_LEVEL = "process_level"
    IT_GENERAL = "it_general"
    APPLICATION = "application"
    COMPLEMENTARY_USER_ENTITY = "complementary_user_entity"

class ControlEffectiveness(Enum):
    """Control effectiveness ratings"""
    EFFECTIVE = "effective"
    DEFICIENT = "deficient"
    NOT_TESTED = "not_tested"
    NOT_APPLICABLE = "not_applicable"

class AuditStatus(Enum):
    """Audit readiness status"""
    READY = "ready"
    IN_PREPARATION = "in_preparation"
    GAPS_IDENTIFIED = "gaps_identified"
    REMEDIATION_REQUIRED = "remediation_required"
    NOT_READY = "not_ready"

class EvidenceType(Enum):
    """Types of audit evidence"""
    DOCUMENT = "document"
    SCREENSHOT = "screenshot"
    LOG_FILE = "log_file"
    REPORT = "report"
    CONFIGURATION = "configuration"
    POLICY = "policy"
    PROCEDURE = "procedure"
    TRAINING_RECORD = "training_record"

@dataclass
class SOC2Control:
    """Individual SOC2 control"""
    control_id: str
    name: str
    description: str
    trust_service: SOC2TrustService
    control_type: ControlType
    
    # Control details
    control_objective: str
    control_activity: str
    frequency: str  # daily, weekly, monthly, quarterly, annually
    responsible_party: str
    
    # Testing information
    test_procedure: str
    evidence_requirements: List[EvidenceType]
    last_test_date: Optional[datetime]
    next_test_date: Optional[datetime]
    
    # Effectiveness
    effectiveness: ControlEffectiveness
    deficiencies: List[str]
    remediation_actions: List[str]
    
    # Evidence tracking
    evidence_collected: List[str]  # File paths or references
    evidence_gaps: List[str]
    
    # Risk assessment
    risk_level: str  # low, medium, high, critical
    compensating_controls: List[str]

@dataclass
class AuditEvidence:
    """Audit evidence item"""
    evidence_id: str
    control_id: str
    evidence_type: EvidenceType
    title: str
    description: str
    file_path: Optional[str]
    
    # Metadata
    created_date: datetime
    created_by: str
    review_date: Optional[datetime]
    reviewed_by: Optional[str]
    approved: bool
    
    # Content
    content_hash: Optional[str]
    retention_period: str
    confidentiality_level: str

@dataclass
class ComplianceGap:
    """Identified compliance gap"""
    gap_id: str
    control_id: str
    gap_type: str  # control_design, control_operation, evidence
    severity: str  # low, medium, high, critical
    
    # Description
    title: str
    description: str
    impact_assessment: str
    
    # Remediation
    remediation_plan: str
    assigned_to: str
    target_date: datetime
    status: str  # open, in_progress, resolved, accepted_risk
    
    # Tracking
    identified_date: datetime
    resolved_date: Optional[datetime]
    resolution_notes: Optional[str]

@dataclass
class AuditReadinessAssessment:
    """Overall audit readiness assessment"""
    assessment_id: str
    assessment_date: datetime
    assessor: str
    
    # Overall status
    overall_status: AuditStatus
    readiness_percentage: float
    
    # Trust service breakdown
    trust_service_readiness: Dict[SOC2TrustService, float]
    
    # Control effectiveness
    total_controls: int
    effective_controls: int
    deficient_controls: int
    not_tested_controls: int
    
    # Evidence status
    evidence_complete: int
    evidence_incomplete: int
    evidence_missing: int
    
    # Gaps and recommendations
    critical_gaps: List[str]
    recommendations: List[str]
    estimated_remediation_time: str
    
    # Next steps
    priority_actions: List[str]
    next_assessment_date: datetime

class SOC2AuditManager:
    """SOC2 Type II audit readiness manager"""
    
    def __init__(self, organization_name: str, service_description: str):
        self.organization_name = organization_name
        self.service_description = service_description
        
        # Core storage
        self.controls: Dict[str, SOC2Control] = {}
        self.evidence: Dict[str, AuditEvidence] = {}
        self.gaps: Dict[str, ComplianceGap] = {}
        self.assessments: Dict[str, AuditReadinessAssessment] = {}
        
        # Initialize standard SOC2 controls
        self._initialize_soc2_controls()
    
    def _initialize_soc2_controls(self):
        """Initialize standard SOC2 Type II controls"""
        
        standard_controls = [
            # Security Controls
            {
                "name": "Information Security Program",
                "description": "Entity has implemented an information security program",
                "trust_service": SOC2TrustService.SECURITY,
                "control_type": ControlType.ENTITY_LEVEL,
                "control_objective": "To ensure entity has documented and implemented an information security program",
                "control_activity": "Maintain and review information security policies and procedures",
                "frequency": "annually",
                "responsible_party": "CISO",
                "test_procedure": "Review security policies, interview security personnel, examine evidence of policy implementation",
                "evidence_requirements": [EvidenceType.POLICY, EvidenceType.PROCEDURE, EvidenceType.TRAINING_RECORD],
                "risk_level": "high"
            },
            {
                "name": "Access Control Management",
                "description": "Logical and physical access is restricted to authorized personnel",
                "trust_service": SOC2TrustService.SECURITY,
                "control_type": ControlType.IT_GENERAL,
                "control_objective": "To ensure access to systems and data is appropriately restricted",
                "control_activity": "Review and approve user access requests, perform periodic access reviews",
                "frequency": "quarterly",
                "responsible_party": "IT Security Team",
                "test_procedure": "Test user access provisioning, review access logs, examine access review procedures",
                "evidence_requirements": [EvidenceType.LOG_FILE, EvidenceType.REPORT, EvidenceType.CONFIGURATION],
                "risk_level": "high"
            },
            {
                "name": "Change Management",
                "description": "Changes to system components are authorized and tested",
                "trust_service": SOC2TrustService.SECURITY,
                "control_type": ControlType.PROCESS_LEVEL,
                "control_objective": "To ensure changes are properly authorized, tested, and documented",
                "control_activity": "Review and approve change requests, test changes in non-production environments",
                "frequency": "continuous",
                "responsible_party": "Development Team Lead",
                "test_procedure": "Review change management procedures, examine change tickets, test change approval process",
                "evidence_requirements": [EvidenceType.DOCUMENT, EvidenceType.REPORT, EvidenceType.PROCEDURE],
                "risk_level": "medium"
            },
            {
                "name": "Data Backup and Recovery",
                "description": "Data is regularly backed up and recovery procedures are tested",
                "trust_service": SOC2TrustService.AVAILABILITY,
                "control_type": ControlType.IT_GENERAL,
                "control_objective": "To ensure data can be recovered in case of system failure",
                "control_activity": "Perform regular data backups, test backup restoration procedures",
                "frequency": "daily",
                "responsible_party": "Infrastructure Team",
                "test_procedure": "Review backup logs, test data restoration, examine backup retention policies",
                "evidence_requirements": [EvidenceType.LOG_FILE, EvidenceType.REPORT, EvidenceType.PROCEDURE],
                "risk_level": "high"
            },
            {
                "name": "Incident Response",
                "description": "Security incidents are identified, reported, and resolved",
                "trust_service": SOC2TrustService.SECURITY,
                "control_type": ControlType.PROCESS_LEVEL,
                "control_objective": "To ensure security incidents are properly handled",
                "control_activity": "Monitor for security events, investigate and respond to incidents",
                "frequency": "continuous",
                "responsible_party": "Security Operations Center",
                "test_procedure": "Review incident response procedures, examine incident logs, test incident escalation",
                "evidence_requirements": [EvidenceType.LOG_FILE, EvidenceType.REPORT, EvidenceType.PROCEDURE],
                "risk_level": "high"
            },
            {
                "name": "Vulnerability Management",
                "description": "Vulnerabilities are identified and remediated in a timely manner",
                "trust_service": SOC2TrustService.SECURITY,
                "control_type": ControlType.IT_GENERAL,
                "control_objective": "To ensure vulnerabilities are identified and addressed",
                "control_activity": "Perform vulnerability scans, track and remediate identified vulnerabilities",
                "frequency": "monthly",
                "responsible_party": "Security Team",
                "test_procedure": "Review vulnerability scan reports, examine remediation tracking, test patch management",
                "evidence_requirements": [EvidenceType.REPORT, EvidenceType.LOG_FILE, EvidenceType.PROCEDURE],
                "risk_level": "medium"
            },
            {
                "name": "Data Encryption",
                "description": "Sensitive data is encrypted in transit and at rest",
                "trust_service": SOC2TrustService.CONFIDENTIALITY,
                "control_type": ControlType.APPLICATION,
                "control_objective": "To protect sensitive data through encryption",
                "control_activity": "Implement and maintain encryption for data transmission and storage",
                "frequency": "continuous",
                "responsible_party": "Development Team",
                "test_procedure": "Test encryption implementation, review encryption policies, examine key management",
                "evidence_requirements": [EvidenceType.CONFIGURATION, EvidenceType.PROCEDURE, EvidenceType.REPORT],
                "risk_level": "high"
            },
            {
                "name": "Data Processing Accuracy",
                "description": "Data processing is complete and accurate",
                "trust_service": SOC2TrustService.PROCESSING_INTEGRITY,
                "control_type": ControlType.APPLICATION,
                "control_objective": "To ensure data processing is accurate and complete",
                "control_activity": "Implement data validation controls, monitor processing accuracy",
                "frequency": "continuous",
                "responsible_party": "Application Team",
                "test_procedure": "Test data validation controls, review processing logs, examine error handling",
                "evidence_requirements": [EvidenceType.LOG_FILE, EvidenceType.REPORT, EvidenceType.CONFIGURATION],
                "risk_level": "medium"
            },
            {
                "name": "Privacy Notice and Consent",
                "description": "Privacy notices are provided and consent is obtained when required",
                "trust_service": SOC2TrustService.PRIVACY,
                "control_type": ControlType.PROCESS_LEVEL,
                "control_objective": "To ensure individuals are informed about data collection and use",
                "control_activity": "Maintain privacy notices, obtain and record consent when required",
                "frequency": "continuous",
                "responsible_party": "Privacy Officer",
                "test_procedure": "Review privacy notices, examine consent mechanisms, test consent recording",
                "evidence_requirements": [EvidenceType.DOCUMENT, EvidenceType.SCREENSHOT, EvidenceType.REPORT],
                "risk_level": "medium"
            },
            {
                "name": "Vendor Management",
                "description": "Third-party vendors are appropriately managed and monitored",
                "trust_service": SOC2TrustService.SECURITY,
                "control_type": ControlType.ENTITY_LEVEL,
                "control_objective": "To ensure third-party risks are properly managed",
                "control_activity": "Assess vendor security, monitor vendor performance, review vendor agreements",
                "frequency": "annually",
                "responsible_party": "Vendor Management Team",
                "test_procedure": "Review vendor assessments, examine vendor agreements, test vendor monitoring",
                "evidence_requirements": [EvidenceType.DOCUMENT, EvidenceType.REPORT, EvidenceType.PROCEDURE],
                "risk_level": "medium"
            }
        ]
        
        for control_data in standard_controls:
            self.create_control(**control_data)
    
    def create_control(self,
                      name: str,
                      description: str,
                      trust_service: SOC2TrustService,
                      control_type: ControlType,
                      control_objective: str,
                      control_activity: str,
                      frequency: str,
                      responsible_party: str,
                      test_procedure: str,
                      evidence_requirements: List[EvidenceType],
                      risk_level: str,
                      **kwargs) -> SOC2Control:
        """Create a new SOC2 control"""
        
        control_id = f"SOC2-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Calculate next test date based on frequency
        next_test_date = self._calculate_next_test_date(frequency)
        
        control = SOC2Control(
            control_id=control_id,
            name=name,
            description=description,
            trust_service=trust_service,
            control_type=control_type,
            control_objective=control_objective,
            control_activity=control_activity,
            frequency=frequency,
            responsible_party=responsible_party,
            test_procedure=test_procedure,
            evidence_requirements=evidence_requirements,
            last_test_date=None,
            next_test_date=next_test_date,
            effectiveness=ControlEffectiveness.NOT_TESTED,
            deficiencies=[],
            remediation_actions=[],
            evidence_collected=[],
            evidence_gaps=[et.value for et in evidence_requirements],  # Initially all evidence is gaps
            risk_level=risk_level,
            compensating_controls=[]
        )
        
        self.controls[control_id] = control
        logger.info(f"Created SOC2 control {control_id}: {name}")
        return control
    
    def _calculate_next_test_date(self, frequency: str) -> datetime:
        """Calculate next test date based on frequency"""
        
        now = datetime.now()
        
        frequency_map = {
            "daily": timedelta(days=1),
            "weekly": timedelta(weeks=1),
            "monthly": timedelta(days=30),
            "quarterly": timedelta(days=90),
            "semi-annually": timedelta(days=180),
            "annually": timedelta(days=365),
            "continuous": timedelta(days=1)  # Daily for continuous controls
        }
        
        delta = frequency_map.get(frequency.lower(), timedelta(days=90))
        return now + delta
    
    def add_evidence(self,
                    control_id: str,
                    evidence_type: EvidenceType,
                    title: str,
                    description: str,
                    created_by: str,
                    file_path: Optional[str] = None,
                    **kwargs) -> AuditEvidence:
        """Add evidence for a control"""
        
        if control_id not in self.controls:
            raise ValueError(f"Control {control_id} not found")
        
        evidence_id = f"EVIDENCE-{control_id}-{uuid.uuid4().hex[:6].upper()}"
        
        # Generate content hash if file path provided
        content_hash = None
        if file_path:
            content_hash = hashlib.sha256(f"{file_path}{datetime.now().isoformat()}".encode()).hexdigest()
        
        evidence = AuditEvidence(
            evidence_id=evidence_id,
            control_id=control_id,
            evidence_type=evidence_type,
            title=title,
            description=description,
            file_path=file_path,
            created_date=datetime.now(),
            created_by=created_by,
            review_date=kwargs.get("review_date"),
            reviewed_by=kwargs.get("reviewed_by"),
            approved=kwargs.get("approved", False),
            content_hash=content_hash,
            retention_period=kwargs.get("retention_period", "7 years"),
            confidentiality_level=kwargs.get("confidentiality_level", "confidential")
        )
        
        self.evidence[evidence_id] = evidence
        
        # Update control evidence tracking
        control = self.controls[control_id]
        control.evidence_collected.append(evidence_id)
        
        # Remove from evidence gaps if this type was missing
        if evidence_type in control.evidence_gaps:
            control.evidence_gaps.remove(evidence_type)
        
        logger.info(f"Added evidence {evidence_id} for control {control_id}")
        return evidence
    
    def test_control(self,
                    control_id: str,
                    tester: str,
                    test_results: str,
                    effectiveness: ControlEffectiveness,
                    deficiencies: List[str] = None,
                    remediation_actions: List[str] = None) -> bool:
        """Record control testing results"""
        
        if control_id not in self.controls:
            raise ValueError(f"Control {control_id} not found")
        
        control = self.controls[control_id]
        
        # Update control testing information
        control.last_test_date = datetime.now()
        control.next_test_date = self._calculate_next_test_date(control.frequency)
        control.effectiveness = effectiveness
        control.deficiencies = deficiencies if deficiencies is not None else []
        control.remediation_actions = remediation_actions if remediation_actions is not None else []
        
        # Create gap entries for deficiencies
        if deficiencies:
            for deficiency in deficiencies:
                self.create_compliance_gap(
                    control_id=control_id,
                    gap_type="control_operation",
                    title=f"Control Deficiency: {deficiency}",
                    description=f"Deficiency identified during control testing: {deficiency}",
                    severity="medium",  # Default severity
                    assigned_to=control.responsible_party,
                    target_date=datetime.now() + timedelta(days=30)
                )
        
        logger.info(f"Tested control {control_id} with effectiveness: {effectiveness.value}")
        return True
    
    def create_compliance_gap(self,
                            control_id: str,
                            gap_type: str,
                            title: str,
                            description: str,
                            severity: str,
                            assigned_to: str,
                            target_date: datetime,
                            **kwargs) -> ComplianceGap:
        """Create a compliance gap"""
        
        gap_id = f"GAP-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        gap = ComplianceGap(
            gap_id=gap_id,
            control_id=control_id,
            gap_type=gap_type,
            severity=severity,
            title=title,
            description=description,
            impact_assessment=kwargs.get("impact_assessment", "To be assessed"),
            remediation_plan=kwargs.get("remediation_plan", "To be developed"),
            assigned_to=assigned_to,
            target_date=target_date,
            status="open",
            identified_date=datetime.now(),
            resolved_date=None,
            resolution_notes=None
        )
        
        self.gaps[gap_id] = gap
        logger.info(f"Created compliance gap {gap_id}: {title}")
        return gap
    
    def resolve_gap(self, gap_id: str, resolution_notes: str, resolved_by: str) -> bool:
        """Resolve a compliance gap"""
        
        if gap_id not in self.gaps:
            logger.error(f"Gap {gap_id} not found")
            return False
        
        gap = self.gaps[gap_id]
        gap.status = "resolved"
        gap.resolved_date = datetime.now()
        gap.resolution_notes = f"Resolved by {resolved_by}: {resolution_notes}"
        
        logger.info(f"Resolved compliance gap {gap_id}")
        return True
    
    def perform_readiness_assessment(self, assessor: str) -> AuditReadinessAssessment:
        """Perform comprehensive audit readiness assessment"""
        
        assessment_id = f"ASSESS-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Calculate control effectiveness metrics
        total_controls = len(self.controls)
        effective_controls = len([c for c in self.controls.values() if c.effectiveness == ControlEffectiveness.EFFECTIVE])
        deficient_controls = len([c for c in self.controls.values() if c.effectiveness == ControlEffectiveness.DEFICIENT])
        not_tested_controls = len([c for c in self.controls.values() if c.effectiveness == ControlEffectiveness.NOT_TESTED])
        
        # Calculate evidence metrics
        evidence_complete = 0
        evidence_incomplete = 0
        evidence_missing = 0
        
        for control in self.controls.values():
            required_evidence = len(control.evidence_requirements)
            collected_evidence = len(control.evidence_collected)
            
            if collected_evidence == required_evidence:
                evidence_complete += 1
            elif collected_evidence > 0:
                evidence_incomplete += 1
            else:
                evidence_missing += 1
        
        # Calculate trust service readiness
        trust_service_readiness = {}
        for trust_service in SOC2TrustService:
            service_controls = [c for c in self.controls.values() if c.trust_service == trust_service]
            if service_controls:
                effective_count = len([c for c in service_controls if c.effectiveness == ControlEffectiveness.EFFECTIVE])
                readiness = (effective_count / len(service_controls)) * 100
                trust_service_readiness[trust_service] = readiness
            else:
                trust_service_readiness[trust_service] = 0.0
        
        # Calculate overall readiness percentage
        control_readiness = (effective_controls / total_controls * 100) if total_controls > 0 else 0
        evidence_readiness = (evidence_complete / total_controls * 100) if total_controls > 0 else 0
        overall_readiness = (control_readiness * 0.7) + (evidence_readiness * 0.3)  # Weighted average
        
        # Determine overall status
        if overall_readiness >= 90:
            overall_status = AuditStatus.READY
        elif overall_readiness >= 75:
            overall_status = AuditStatus.IN_PREPARATION
        elif overall_readiness >= 50:
            overall_status = AuditStatus.GAPS_IDENTIFIED
        else:
            overall_status = AuditStatus.REMEDIATION_REQUIRED
        
        # Identify critical gaps
        critical_gaps = []
        high_risk_deficient = [c for c in self.controls.values() 
                              if c.effectiveness == ControlEffectiveness.DEFICIENT and c.risk_level == "high"]
        for control in high_risk_deficient:
            critical_gaps.append(f"Control '{control.name}' is deficient and high risk")
        
        untested_high_risk = [c for c in self.controls.values() 
                             if c.effectiveness == ControlEffectiveness.NOT_TESTED and c.risk_level == "high"]
        for control in untested_high_risk:
            critical_gaps.append(f"Control '{control.name}' is not tested and high risk")
        
        # Generate recommendations
        recommendations = self._generate_recommendations(overall_readiness, critical_gaps)
        
        # Calculate estimated remediation time
        open_gaps = [g for g in self.gaps.values() if g.status == "open"]
        estimated_time = f"{len(open_gaps) * 2} weeks"  # Rough estimate
        
        # Generate priority actions
        priority_actions = []
        if untested_high_risk:
            priority_actions.append("Test all high-risk controls immediately")
        if high_risk_deficient:
            priority_actions.append("Remediate deficient high-risk controls")
        if evidence_missing > 0:
            priority_actions.append("Collect missing evidence for all controls")
        
        assessment = AuditReadinessAssessment(
            assessment_id=assessment_id,
            assessment_date=datetime.now(),
            assessor=assessor,
            overall_status=overall_status,
            readiness_percentage=round(overall_readiness, 2),
            trust_service_readiness=trust_service_readiness,
            total_controls=total_controls,
            effective_controls=effective_controls,
            deficient_controls=deficient_controls,
            not_tested_controls=not_tested_controls,
            evidence_complete=evidence_complete,
            evidence_incomplete=evidence_incomplete,
            evidence_missing=evidence_missing,
            critical_gaps=critical_gaps,
            recommendations=recommendations,
            estimated_remediation_time=estimated_time,
            priority_actions=priority_actions,
            next_assessment_date=datetime.now() + timedelta(days=30)
        )
        
        self.assessments[assessment_id] = assessment
        logger.info(f"Completed audit readiness assessment {assessment_id}, readiness: {overall_readiness:.1f}%")
        return assessment
    
    def _generate_recommendations(self, readiness_percentage: float, critical_gaps: List[str]) -> List[str]:
        """Generate recommendations based on assessment results"""
        
        recommendations = []
        
        if readiness_percentage < 50:
            recommendations.append("Immediate focus required on control implementation and testing")
            recommendations.append("Consider engaging external SOC2 consultant for remediation planning")
        elif readiness_percentage < 75:
            recommendations.append("Prioritize testing of untested controls")
            recommendations.append("Complete evidence collection for all controls")
        elif readiness_percentage < 90:
            recommendations.append("Focus on remediation of identified deficiencies")
            recommendations.append("Ensure all evidence is properly reviewed and approved")
        else:
            recommendations.append("Maintain current control environment")
            recommendations.append("Schedule formal SOC2 Type II audit")
        
        if critical_gaps:
            recommendations.append("Address all critical gaps before proceeding with audit")
        
        recommendations.append("Implement continuous monitoring for ongoing compliance")
        recommendations.append("Train staff on SOC2 requirements and responsibilities")
        
        return recommendations
    
    def generate_soc2_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive SOC2 compliance report"""
        
        # Get latest assessment
        latest_assessment = None
        if self.assessments:
            latest_assessment = max(self.assessments.values(), key=lambda a: a.assessment_date)
        
        # Control summary by trust service
        controls_by_trust_service = {}
        for trust_service in SOC2TrustService:
            service_controls = [c for c in self.controls.values() if c.trust_service == trust_service]
            controls_by_trust_service[trust_service.value] = {
                "total": len(service_controls),
                "effective": len([c for c in service_controls if c.effectiveness == ControlEffectiveness.EFFECTIVE]),
                "deficient": len([c for c in service_controls if c.effectiveness == ControlEffectiveness.DEFICIENT]),
                "not_tested": len([c for c in service_controls if c.effectiveness == ControlEffectiveness.NOT_TESTED])
            }
        
        # Evidence summary
        evidence_summary = {
            "total_evidence_items": len(self.evidence),
            "approved_evidence": len([e for e in self.evidence.values() if e.approved]),
            "pending_review": len([e for e in self.evidence.values() if not e.approved]),
            "evidence_by_type": {}
        }
        
        for evidence_type in EvidenceType:
            count = len([e for e in self.evidence.values() if e.evidence_type == evidence_type])
            evidence_summary["evidence_by_type"][evidence_type.value] = count
        
        # Gap analysis
        gap_summary = {
            "total_gaps": len(self.gaps),
            "open_gaps": len([g for g in self.gaps.values() if g.status == "open"]),
            "resolved_gaps": len([g for g in self.gaps.values() if g.status == "resolved"]),
            "critical_gaps": len([g for g in self.gaps.values() if g.severity == "critical" and g.status == "open"]),
            "overdue_gaps": len([g for g in self.gaps.values() if g.target_date < datetime.now() and g.status == "open"])
        }
        
        # Control testing schedule
        upcoming_tests = []
        for control in self.controls.values():
            if control.next_test_date and control.next_test_date <= datetime.now() + timedelta(days=30):
                upcoming_tests.append({
                    "control_id": control.control_id,
                    "control_name": control.name,
                    "next_test_date": control.next_test_date.isoformat(),
                    "responsible_party": control.responsible_party,
                    "frequency": control.frequency
                })
        
        return {
            "report_date": datetime.now().isoformat(),
            "organization": self.organization_name,
            "service_description": self.service_description,
            "latest_assessment": asdict(latest_assessment) if latest_assessment else None,
            "controls_summary": {
                "total_controls": len(self.controls),
                "by_trust_service": controls_by_trust_service,
                "by_effectiveness": {
                    "effective": len([c for c in self.controls.values() if c.effectiveness == ControlEffectiveness.EFFECTIVE]),
                    "deficient": len([c for c in self.controls.values() if c.effectiveness == ControlEffectiveness.DEFICIENT]),
                    "not_tested": len([c for c in self.controls.values() if c.effectiveness == ControlEffectiveness.NOT_TESTED])
                }
            },
            "evidence_summary": evidence_summary,
            "gap_analysis": gap_summary,
            "upcoming_tests": upcoming_tests,
            "compliance_metrics": {
                "control_effectiveness_rate": (len([c for c in self.controls.values() if c.effectiveness == ControlEffectiveness.EFFECTIVE]) / len(self.controls) * 100) if self.controls else 0,
                "evidence_completion_rate": (evidence_summary["approved_evidence"] / len(self.evidence) * 100) if self.evidence else 0,
                "gap_resolution_rate": (gap_summary["resolved_gaps"] / gap_summary["total_gaps"] * 100) if gap_summary["total_gaps"] > 0 else 100
            }
        }
    
    def export_audit_workbook(self) -> Dict[str, Any]:
        """Export comprehensive audit workbook for auditors"""
        
        # Control matrix
        control_matrix = []
        for control in self.controls.values():
            control_data = {
                "control_id": control.control_id,
                "control_name": control.name,
                "trust_service": control.trust_service.value,
                "control_type": control.control_type.value,
                "control_objective": control.control_objective,
                "control_activity": control.control_activity,
                "frequency": control.frequency,
                "responsible_party": control.responsible_party,
                "effectiveness": control.effectiveness.value,
                "last_test_date": control.last_test_date.isoformat() if control.last_test_date else None,
                "evidence_collected": len(control.evidence_collected),
                "evidence_required": len(control.evidence_requirements),
                "deficiencies": len(control.deficiencies),
                "risk_level": control.risk_level
            }
            control_matrix.append(control_data)
        
        # Evidence inventory
        evidence_inventory = []
        for evidence in self.evidence.values():
            evidence_data = {
                "evidence_id": evidence.evidence_id,
                "control_id": evidence.control_id,
                "evidence_type": evidence.evidence_type.value,
                "title": evidence.title,
                "description": evidence.description,
                "file_path": evidence.file_path,
                "created_date": evidence.created_date.isoformat(),
                "created_by": evidence.created_by,
                "approved": evidence.approved,
                "reviewed_by": evidence.reviewed_by,
                "confidentiality_level": evidence.confidentiality_level
            }
            evidence_inventory.append(evidence_data)
        
        # Exception report (gaps and deficiencies)
        exception_report = []
        for gap in self.gaps.values():
            if gap.status == "open":
                exception_data = {
                    "gap_id": gap.gap_id,
                    "control_id": gap.control_id,
                    "gap_type": gap.gap_type,
                    "severity": gap.severity,
                    "title": gap.title,
                    "description": gap.description,
                    "assigned_to": gap.assigned_to,
                    "target_date": gap.target_date.isoformat(),
                    "days_overdue": (datetime.now() - gap.target_date).days if gap.target_date < datetime.now() else 0
                }
                exception_report.append(exception_data)
        
        return {
            "workbook_date": datetime.now().isoformat(),
            "organization": self.organization_name,
            "service_description": self.service_description,
            "control_matrix": control_matrix,
            "evidence_inventory": evidence_inventory,
            "exception_report": exception_report,
            "summary_statistics": {
                "total_controls": len(self.controls),
                "total_evidence": len(self.evidence),
                "total_exceptions": len(exception_report),
                "audit_readiness": self.assessments[max(self.assessments.keys())].readiness_percentage if self.assessments else 0
            }
        }
    
    def get_control_testing_schedule(self, days_ahead: int = 90) -> List[Dict[str, Any]]:
        """Get control testing schedule for specified period"""
        
        end_date = datetime.now() + timedelta(days=days_ahead)
        testing_schedule = []
        
        for control in self.controls.values():
            if control.next_test_date and control.next_test_date <= end_date:
                schedule_item = {
                    "control_id": control.control_id,
                    "control_name": control.name,
                    "trust_service": control.trust_service.value,
                    "frequency": control.frequency,
                    "responsible_party": control.responsible_party,
                    "next_test_date": control.next_test_date.isoformat(),
                    "days_until_test": (control.next_test_date - datetime.now()).days,
                    "last_test_date": control.last_test_date.isoformat() if control.last_test_date else None,
                    "current_effectiveness": control.effectiveness.value,
                    "risk_level": control.risk_level,
                    "test_procedure": control.test_procedure,
                    "evidence_requirements": [et.value for et in control.evidence_requirements]
                }
                testing_schedule.append(schedule_item)
        
        # Sort by next test date
        testing_schedule.sort(key=lambda x: x["next_test_date"])
        
        return testing_schedule