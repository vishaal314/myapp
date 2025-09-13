#!/usr/bin/env python3
"""
Vendor Risk Management and Third-Party Risk Assessment Platform
Comprehensive GDPR Article 28 compliance and vendor assessment workflows
"""

import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class VendorType(Enum):
    """Types of vendor relationships"""
    DATA_PROCESSOR = "data_processor"           # GDPR Article 28
    JOINT_CONTROLLER = "joint_controller"       # GDPR Article 26
    THIRD_PARTY_RECIPIENT = "third_party_recipient"
    SUB_PROCESSOR = "sub_processor"
    CLOUD_PROVIDER = "cloud_provider"
    SAAS_PROVIDER = "saas_provider"
    CONSULTING_SERVICE = "consulting_service"
    MARKETING_PARTNER = "marketing_partner"

class RiskLevel(Enum):
    """Risk assessment levels"""
    CRITICAL = "critical"     # 80-100 - Immediate action required
    HIGH = "high"            # 60-79 - High priority remediation
    MEDIUM = "medium"        # 40-59 - Moderate risk, monitor closely
    LOW = "low"             # 20-39 - Acceptable risk with controls
    MINIMAL = "minimal"      # 0-19 - Very low risk

class AssessmentStatus(Enum):
    """Assessment workflow status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PENDING_VENDOR_RESPONSE = "pending_vendor_response"
    UNDER_REVIEW = "under_review"
    COMPLETED = "completed"
    REQUIRES_REMEDIATION = "requires_remediation"
    APPROVED = "approved"
    REJECTED = "rejected"

class DataProcessingLocation(Enum):
    """Data processing locations for transfer impact assessment"""
    EU_EEA = "eu_eea"
    ADEQUATE_COUNTRY = "adequate_country"
    USA_PRIVACY_SHIELD = "usa_privacy_shield"  # Historical
    USA_DPF = "usa_dpf"  # Data Privacy Framework
    NON_ADEQUATE_COUNTRY = "non_adequate_country"
    UNKNOWN = "unknown"

@dataclass
class VendorContact:
    """Vendor contact information"""
    contact_id: str
    name: str
    role: str
    email: str
    phone: Optional[str]
    is_primary: bool
    is_dpo: bool  # Data Protection Officer
    is_security_contact: bool

@dataclass
class DataProcessingDetails:
    """Details of data processing by vendor"""
    processing_id: str
    data_categories: List[str]
    processing_purposes: List[str]
    legal_basis: List[str]
    data_subjects_count: Optional[int]
    retention_period: str
    deletion_procedures: str
    processing_locations: List[DataProcessingLocation]
    sub_processors: List[str]
    international_transfers: bool
    transfer_mechanisms: List[str]  # SCCs, BCRs, adequacy_decision

@dataclass
class SecurityAssessment:
    """Security and technical assessment"""
    assessment_id: str
    encryption_in_transit: bool
    encryption_at_rest: bool
    access_controls: List[str]
    authentication_methods: List[str]
    audit_logging: bool
    incident_response_plan: bool
    business_continuity_plan: bool
    disaster_recovery_plan: bool
    penetration_testing: bool
    vulnerability_management: bool
    security_certifications: List[str]  # ISO27001, SOC2, etc.
    last_security_review: Optional[datetime]
    security_score: float  # 0-100

@dataclass
class ComplianceAssessment:
    """Compliance and legal assessment"""
    assessment_id: str
    gdpr_compliant: bool
    dpa_signed: bool  # Data Processing Agreement
    privacy_policy_adequate: bool
    data_breach_notification: bool
    data_subject_rights_support: bool
    lawful_basis_documentation: bool
    privacy_by_design: bool
    data_protection_impact_assessment: bool
    compliance_certifications: List[str]
    regulatory_issues: List[str]
    compliance_score: float  # 0-100

@dataclass
class VendorAssessmentResult:
    """Complete vendor assessment result"""
    assessment_id: str
    vendor_id: str
    assessment_date: datetime
    assessor: str
    
    # Individual scores
    security_score: float
    compliance_score: float
    financial_stability_score: float
    service_quality_score: float
    contract_terms_score: float
    
    # Overall assessment
    overall_risk_score: float
    risk_level: RiskLevel
    
    # Recommendations
    approved_for_use: bool
    conditions: List[str]
    remediation_actions: List[str]
    review_date: datetime
    
    # Evidence
    assessment_evidence: List[str]
    documentation_reviewed: List[str]

@dataclass
class Vendor:
    """Vendor/Third-party entity"""
    vendor_id: str
    name: str
    vendor_type: VendorType
    description: str
    
    # Basic information
    legal_name: str
    website: str
    headquarters_country: str
    registration_number: Optional[str]
    
    # Contacts
    contacts: List[VendorContact]
    
    # Processing details
    data_processing: Optional[DataProcessingDetails]
    
    # Services provided
    services_description: str
    contract_start_date: datetime
    contract_end_date: Optional[datetime]
    contract_value: Optional[float]
    
    # Assessments
    security_assessment: Optional[SecurityAssessment]
    compliance_assessment: Optional[ComplianceAssessment]
    latest_assessment: Optional[VendorAssessmentResult]
    
    # Status
    assessment_status: AssessmentStatus
    approval_status: str  # approved, conditional, rejected, pending
    
    # Metadata
    created_date: datetime
    last_updated: datetime
    next_review_date: datetime
    responsible_person: str

class VendorRiskManager:
    """Vendor Risk Management Platform"""
    
    def __init__(self, organization_name: str, region: str = "Netherlands"):
        self.organization_name = organization_name
        self.region = region
        
        # Core storage
        self.vendors: Dict[str, Vendor] = {}
        self.assessments: Dict[str, VendorAssessmentResult] = {}
        
        # Risk assessment criteria
        self.risk_criteria = self._initialize_risk_criteria()
        self.compliance_requirements = self._initialize_compliance_requirements()
        
    def _initialize_risk_criteria(self) -> Dict[str, Dict[str, Any]]:
        """Initialize risk assessment criteria"""
        
        return {
            "security": {
                "encryption_required": True,
                "min_security_certifications": ["ISO27001", "SOC2"],
                "penetration_testing_frequency": "annual",
                "incident_response_required": True,
                "weight": 0.3
            },
            "compliance": {
                "gdpr_compliance_required": True,
                "dpa_required": True,
                "data_breach_notification_required": True,
                "privacy_policy_required": True,
                "weight": 0.25
            },
            "data_processing": {
                "international_transfers_risk_multiplier": 1.5,
                "sub_processors_risk_factor": 1.2,
                "special_category_data_multiplier": 2.0,
                "weight": 0.25
            },
            "financial": {
                "min_financial_stability_score": 60,
                "credit_rating_required": False,
                "insurance_required": True,
                "weight": 0.1
            },
            "operational": {
                "business_continuity_required": True,
                "disaster_recovery_required": True,
                "sla_requirements": True,
                "weight": 0.1
            }
        }
    
    def _initialize_compliance_requirements(self) -> Dict[str, Any]:
        """Initialize compliance requirements based on region"""
        
        requirements = {
            "gdpr_article_28": {
                "dpa_required": True,
                "processing_instructions": True,
                "confidentiality_commitment": True,
                "security_measures": True,
                "sub_processor_authorization": True,
                "data_subject_rights_assistance": True,
                "deletion_return_procedures": True,
                "audit_cooperation": True,
                "breach_notification": True
            },
            "netherlands_specific": {
                "ap_notification": True,  # Autoriteit Persoonsgegevens
                "dutch_language_support": False,
                "data_residency": False
            }
        }
        
        return requirements
    
    def create_vendor(self,
                     name: str,
                     vendor_type: VendorType,
                     legal_name: str,
                     website: str,
                     headquarters_country: str,
                     services_description: str,
                     contract_start_date: datetime,
                     responsible_person: str,
                     **kwargs) -> Vendor:
        """Create a new vendor record"""
        
        vendor_id = f"VENDOR-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Calculate next review date based on vendor type and risk
        next_review_date = self._calculate_review_date(vendor_type)
        
        vendor = Vendor(
            vendor_id=vendor_id,
            name=name,
            vendor_type=vendor_type,
            description=kwargs.get("description", ""),
            legal_name=legal_name,
            website=website,
            headquarters_country=headquarters_country,
            registration_number=kwargs.get("registration_number"),
            contacts=[],
            data_processing=None,
            services_description=services_description,
            contract_start_date=contract_start_date,
            contract_end_date=kwargs.get("contract_end_date"),
            contract_value=kwargs.get("contract_value"),
            security_assessment=None,
            compliance_assessment=None,
            latest_assessment=None,
            assessment_status=AssessmentStatus.NOT_STARTED,
            approval_status="pending",
            created_date=datetime.now(),
            last_updated=datetime.now(),
            next_review_date=next_review_date,
            responsible_person=responsible_person
        )
        
        self.vendors[vendor_id] = vendor
        
        logger.info(f"Created vendor {vendor_id}: {name}")
        return vendor
    
    def _calculate_review_date(self, vendor_type: VendorType) -> datetime:
        """Calculate next review date based on vendor type"""
        
        review_intervals = {
            VendorType.DATA_PROCESSOR: timedelta(days=365),      # Annual review
            VendorType.JOINT_CONTROLLER: timedelta(days=365),    # Annual review
            VendorType.CLOUD_PROVIDER: timedelta(days=180),     # Semi-annual
            VendorType.SUB_PROCESSOR: timedelta(days=365),      # Annual review
            VendorType.SAAS_PROVIDER: timedelta(days=365),      # Annual review
            VendorType.THIRD_PARTY_RECIPIENT: timedelta(days=730), # Biennial
            VendorType.CONSULTING_SERVICE: timedelta(days=730),  # Biennial
            VendorType.MARKETING_PARTNER: timedelta(days=365)    # Annual review
        }
        
        return datetime.now() + review_intervals.get(vendor_type, timedelta(days=365))
    
    def add_vendor_contact(self,
                          vendor_id: str,
                          name: str,
                          role: str,
                          email: str,
                          phone: Optional[str] = None,
                          is_primary: bool = False,
                          is_dpo: bool = False,
                          is_security_contact: bool = False) -> VendorContact:
        """Add contact to vendor"""
        
        if vendor_id not in self.vendors:
            raise ValueError(f"Vendor {vendor_id} not found")
        
        contact_id = f"CONTACT-{vendor_id}-{uuid.uuid4().hex[:4]}"
        
        contact = VendorContact(
            contact_id=contact_id,
            name=name,
            role=role,
            email=email,
            phone=phone,
            is_primary=is_primary,
            is_dpo=is_dpo,
            is_security_contact=is_security_contact
        )
        
        vendor = self.vendors[vendor_id]
        vendor.contacts.append(contact)
        vendor.last_updated = datetime.now()
        
        logger.info(f"Added contact {name} to vendor {vendor_id}")
        return contact
    
    def set_data_processing_details(self,
                                   vendor_id: str,
                                   data_categories: List[str],
                                   processing_purposes: List[str],
                                   legal_basis: List[str],
                                   retention_period: str,
                                   deletion_procedures: str,
                                   processing_locations: List[DataProcessingLocation],
                                   **kwargs) -> DataProcessingDetails:
        """Set data processing details for vendor"""
        
        if vendor_id not in self.vendors:
            raise ValueError(f"Vendor {vendor_id} not found")
        
        processing_id = f"PROCESSING-{vendor_id}-{uuid.uuid4().hex[:4]}"
        
        data_processing = DataProcessingDetails(
            processing_id=processing_id,
            data_categories=data_categories,
            processing_purposes=processing_purposes,
            legal_basis=legal_basis,
            data_subjects_count=kwargs.get("data_subjects_count"),
            retention_period=retention_period,
            deletion_procedures=deletion_procedures,
            processing_locations=processing_locations,
            sub_processors=kwargs.get("sub_processors", []),
            international_transfers=kwargs.get("international_transfers", False),
            transfer_mechanisms=kwargs.get("transfer_mechanisms", [])
        )
        
        vendor = self.vendors[vendor_id]
        vendor.data_processing = data_processing
        vendor.last_updated = datetime.now()
        
        logger.info(f"Set data processing details for vendor {vendor_id}")
        return data_processing
    
    def conduct_security_assessment(self,
                                   vendor_id: str,
                                   assessor: str,
                                   assessment_data: Dict[str, Any]) -> SecurityAssessment:
        """Conduct security assessment of vendor"""
        
        if vendor_id not in self.vendors:
            raise ValueError(f"Vendor {vendor_id} not found")
        
        assessment_id = f"SEC-ASSESS-{vendor_id}-{uuid.uuid4().hex[:4]}"
        
        # Calculate security score based on assessment data
        security_score = self._calculate_security_score(assessment_data)
        
        security_assessment = SecurityAssessment(
            assessment_id=assessment_id,
            encryption_in_transit=assessment_data.get("encryption_in_transit", False),
            encryption_at_rest=assessment_data.get("encryption_at_rest", False),
            access_controls=assessment_data.get("access_controls", []),
            authentication_methods=assessment_data.get("authentication_methods", []),
            audit_logging=assessment_data.get("audit_logging", False),
            incident_response_plan=assessment_data.get("incident_response_plan", False),
            business_continuity_plan=assessment_data.get("business_continuity_plan", False),
            disaster_recovery_plan=assessment_data.get("disaster_recovery_plan", False),
            penetration_testing=assessment_data.get("penetration_testing", False),
            vulnerability_management=assessment_data.get("vulnerability_management", False),
            security_certifications=assessment_data.get("security_certifications", []),
            last_security_review=datetime.now(),
            security_score=security_score
        )
        
        vendor = self.vendors[vendor_id]
        vendor.security_assessment = security_assessment
        vendor.last_updated = datetime.now()
        
        logger.info(f"Completed security assessment for vendor {vendor_id}, score: {security_score}")
        return security_assessment
    
    def _calculate_security_score(self, assessment_data: Dict[str, Any]) -> float:
        """Calculate security score based on assessment criteria"""
        
        score = 0.0
        max_score = 100.0
        
        # Encryption (20 points)
        if assessment_data.get("encryption_in_transit", False):
            score += 10
        if assessment_data.get("encryption_at_rest", False):
            score += 10
        
        # Access controls (15 points)
        access_controls = assessment_data.get("access_controls", [])
        if "multi_factor_authentication" in access_controls:
            score += 5
        if "role_based_access" in access_controls:
            score += 5
        if "principle_of_least_privilege" in access_controls:
            score += 5
        
        # Security practices (25 points)
        if assessment_data.get("audit_logging", False):
            score += 5
        if assessment_data.get("incident_response_plan", False):
            score += 5
        if assessment_data.get("vulnerability_management", False):
            score += 5
        if assessment_data.get("penetration_testing", False):
            score += 10
        
        # Business continuity (20 points)
        if assessment_data.get("business_continuity_plan", False):
            score += 10
        if assessment_data.get("disaster_recovery_plan", False):
            score += 10
        
        # Certifications (20 points)
        certifications = assessment_data.get("security_certifications", [])
        cert_score = 0
        for cert in ["ISO27001", "SOC2", "FedRAMP", "PCI_DSS"]:
            if cert in certifications:
                cert_score += 5
        score += min(cert_score, 20)
        
        return min(score, max_score)
    
    def conduct_compliance_assessment(self,
                                    vendor_id: str,
                                    assessor: str,
                                    assessment_data: Dict[str, Any]) -> ComplianceAssessment:
        """Conduct compliance assessment of vendor"""
        
        if vendor_id not in self.vendors:
            raise ValueError(f"Vendor {vendor_id} not found")
        
        assessment_id = f"COMP-ASSESS-{vendor_id}-{uuid.uuid4().hex[:4]}"
        
        # Calculate compliance score
        compliance_score = self._calculate_compliance_score(assessment_data)
        
        compliance_assessment = ComplianceAssessment(
            assessment_id=assessment_id,
            gdpr_compliant=assessment_data.get("gdpr_compliant", False),
            dpa_signed=assessment_data.get("dpa_signed", False),
            privacy_policy_adequate=assessment_data.get("privacy_policy_adequate", False),
            data_breach_notification=assessment_data.get("data_breach_notification", False),
            data_subject_rights_support=assessment_data.get("data_subject_rights_support", False),
            lawful_basis_documentation=assessment_data.get("lawful_basis_documentation", False),
            privacy_by_design=assessment_data.get("privacy_by_design", False),
            data_protection_impact_assessment=assessment_data.get("data_protection_impact_assessment", False),
            compliance_certifications=assessment_data.get("compliance_certifications", []),
            regulatory_issues=assessment_data.get("regulatory_issues", []),
            compliance_score=compliance_score
        )
        
        vendor = self.vendors[vendor_id]
        vendor.compliance_assessment = compliance_assessment
        vendor.last_updated = datetime.now()
        
        logger.info(f"Completed compliance assessment for vendor {vendor_id}, score: {compliance_score}")
        return compliance_assessment
    
    def _calculate_compliance_score(self, assessment_data: Dict[str, Any]) -> float:
        """Calculate compliance score based on GDPR and other requirements"""
        
        score = 0.0
        max_score = 100.0
        
        # GDPR Article 28 requirements (60 points)
        if assessment_data.get("gdpr_compliant", False):
            score += 15
        if assessment_data.get("dpa_signed", False):
            score += 15
        if assessment_data.get("data_breach_notification", False):
            score += 10
        if assessment_data.get("data_subject_rights_support", False):
            score += 10
        if assessment_data.get("lawful_basis_documentation", False):
            score += 10
        
        # Privacy practices (25 points)
        if assessment_data.get("privacy_policy_adequate", False):
            score += 10
        if assessment_data.get("privacy_by_design", False):
            score += 10
        if assessment_data.get("data_protection_impact_assessment", False):
            score += 5
        
        # Compliance certifications (15 points)
        certifications = assessment_data.get("compliance_certifications", [])
        for cert in certifications:
            if cert in ["ISO27701", "GDPR_CERTIFIED", "PRIVACY_SHIELD"]:
                score += 5
        
        # Deduct for regulatory issues
        regulatory_issues = assessment_data.get("regulatory_issues", [])
        score -= len(regulatory_issues) * 10
        
        return max(min(score, max_score), 0.0)
    
    def perform_comprehensive_assessment(self,
                                       vendor_id: str,
                                       assessor: str,
                                       security_data: Dict[str, Any],
                                       compliance_data: Dict[str, Any],
                                       additional_scores: Dict[str, float]) -> VendorAssessmentResult:
        """Perform comprehensive vendor risk assessment"""
        
        if vendor_id not in self.vendors:
            raise ValueError(f"Vendor {vendor_id} not found")
        
        vendor = self.vendors[vendor_id]
        
        # Conduct individual assessments
        security_assessment = self.conduct_security_assessment(vendor_id, assessor, security_data)
        compliance_assessment = self.conduct_compliance_assessment(vendor_id, assessor, compliance_data)
        
        # Get additional scores
        financial_stability_score = additional_scores.get("financial_stability", 75.0)
        service_quality_score = additional_scores.get("service_quality", 80.0)
        contract_terms_score = additional_scores.get("contract_terms", 70.0)
        
        # Calculate overall risk score
        overall_risk_score = self._calculate_overall_risk_score(
            security_assessment.security_score,
            compliance_assessment.compliance_score,
            financial_stability_score,
            service_quality_score,
            contract_terms_score,
            vendor
        )
        
        # Determine risk level
        risk_level = self._determine_risk_level(overall_risk_score)
        
        # Generate recommendations
        approved_for_use, conditions, remediation_actions = self._generate_recommendations(
            vendor, security_assessment, compliance_assessment, overall_risk_score
        )
        
        assessment_id = f"ASSESS-{vendor_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        assessment_result = VendorAssessmentResult(
            assessment_id=assessment_id,
            vendor_id=vendor_id,
            assessment_date=datetime.now(),
            assessor=assessor,
            security_score=security_assessment.security_score,
            compliance_score=compliance_assessment.compliance_score,
            financial_stability_score=financial_stability_score,
            service_quality_score=service_quality_score,
            contract_terms_score=contract_terms_score,
            overall_risk_score=overall_risk_score,
            risk_level=risk_level,
            approved_for_use=approved_for_use,
            conditions=conditions,
            remediation_actions=remediation_actions,
            review_date=datetime.now() + timedelta(days=365),
            assessment_evidence=additional_scores.get("evidence", []),
            documentation_reviewed=additional_scores.get("documentation", [])
        )
        
        # Update vendor
        vendor.latest_assessment = assessment_result
        vendor.assessment_status = AssessmentStatus.COMPLETED
        vendor.approval_status = "approved" if approved_for_use else "conditional"
        vendor.last_updated = datetime.now()
        
        # Store assessment
        self.assessments[assessment_id] = assessment_result
        
        logger.info(f"Completed comprehensive assessment for vendor {vendor_id}, risk level: {risk_level.value}")
        return assessment_result
    
    def _calculate_overall_risk_score(self,
                                    security_score: float,
                                    compliance_score: float,
                                    financial_score: float,
                                    service_score: float,
                                    contract_score: float,
                                    vendor: Vendor) -> float:
        """Calculate overall risk score using weighted criteria"""
        
        weights = self.risk_criteria
        
        # Base weighted score
        weighted_score = (
            security_score * weights["security"]["weight"] +
            compliance_score * weights["compliance"]["weight"] +
            financial_score * weights["financial"]["weight"] +
            service_score * weights["operational"]["weight"] +
            contract_score * 0.1  # Contract terms weight
        )
        
        # Apply risk multipliers based on data processing
        if vendor.data_processing:
            dp = vendor.data_processing
            
            # International transfer risk
            if dp.international_transfers:
                non_adequate_locations = [
                    loc for loc in dp.processing_locations 
                    if loc == DataProcessingLocation.NON_ADEQUATE_COUNTRY
                ]
                if non_adequate_locations:
                    weighted_score *= 0.8  # Reduce score by 20% for non-adequate countries
            
            # Sub-processor risk
            if dp.sub_processors:
                weighted_score *= (1 - (len(dp.sub_processors) * 0.05))  # 5% reduction per sub-processor
            
            # Special category data handling
            special_categories = ["health", "biometric", "genetic", "racial", "political", "religious"]
            if any(cat in dp.data_categories for cat in special_categories):
                weighted_score *= 0.9  # 10% reduction for special category data
        
        # Vendor type risk adjustments
        type_adjustments = {
            VendorType.DATA_PROCESSOR: 1.0,
            VendorType.JOINT_CONTROLLER: 0.95,
            VendorType.CLOUD_PROVIDER: 0.9,
            VendorType.SUB_PROCESSOR: 0.85,
            VendorType.SAAS_PROVIDER: 0.95,
            VendorType.THIRD_PARTY_RECIPIENT: 1.0,
            VendorType.CONSULTING_SERVICE: 1.05,
            VendorType.MARKETING_PARTNER: 0.9
        }
        
        weighted_score *= type_adjustments.get(vendor.vendor_type, 1.0)
        
        return max(min(weighted_score, 100.0), 0.0)
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level based on score"""
        
        if risk_score >= 80:
            return RiskLevel.MINIMAL
        elif risk_score >= 60:
            return RiskLevel.LOW
        elif risk_score >= 40:
            return RiskLevel.MEDIUM
        elif risk_score >= 20:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def _generate_recommendations(self,
                                vendor: Vendor,
                                security_assessment: SecurityAssessment,
                                compliance_assessment: ComplianceAssessment,
                                overall_score: float) -> tuple[bool, List[str], List[str]]:
        """Generate approval recommendations and remediation actions"""
        
        conditions = []
        remediation_actions = []
        
        # Security-based conditions
        if not security_assessment.encryption_in_transit:
            remediation_actions.append("Implement encryption in transit for all data communications")
        
        if not security_assessment.encryption_at_rest:
            remediation_actions.append("Implement encryption at rest for all stored data")
        
        if not security_assessment.incident_response_plan:
            conditions.append("Maintain and test incident response plan")
            remediation_actions.append("Develop and document comprehensive incident response plan")
        
        # Compliance-based conditions
        if not compliance_assessment.dpa_signed:
            remediation_actions.append("Execute Data Processing Agreement (DPA) per GDPR Article 28")
        
        if not compliance_assessment.gdpr_compliant:
            remediation_actions.append("Achieve GDPR compliance and provide evidence of compliance")
        
        if not compliance_assessment.data_subject_rights_support:
            conditions.append("Support data subject rights requests within required timeframes")
        
        # Risk level-based decisions
        if overall_score < 40:
            return False, conditions, remediation_actions  # Not approved
        elif overall_score < 60:
            conditions.extend([
                "Quarterly security and compliance reviews required",
                "Immediate notification of any security incidents",
                "Annual penetration testing with results shared"
            ])
        elif overall_score < 80:
            conditions.extend([
                "Semi-annual compliance reviews required",
                "Immediate notification of any data breaches"
            ])
        
        approved = overall_score >= 40
        return approved, conditions, remediation_actions
    
    def get_vendor_risk_dashboard(self) -> Dict[str, Any]:
        """Generate vendor risk dashboard summary"""
        
        total_vendors = len(self.vendors)
        assessed_vendors = len([v for v in self.vendors.values() if v.latest_assessment])
        
        # Risk level breakdown
        risk_breakdown = {level.value: 0 for level in RiskLevel}
        for vendor in self.vendors.values():
            if vendor.latest_assessment:
                risk_level = vendor.latest_assessment.risk_level.value
                risk_breakdown[risk_level] += 1
        
        # Approval status breakdown
        approval_breakdown = {}
        for vendor in self.vendors.values():
            status = vendor.approval_status
            approval_breakdown[status] = approval_breakdown.get(status, 0) + 1
        
        # Vendor type breakdown
        type_breakdown = {}
        for vendor in self.vendors.values():
            vtype = vendor.vendor_type.value
            type_breakdown[vtype] = type_breakdown.get(vtype, 0) + 1
        
        # Upcoming reviews
        upcoming_reviews = []
        thirty_days = datetime.now() + timedelta(days=30)
        for vendor in self.vendors.values():
            if vendor.next_review_date <= thirty_days:
                upcoming_reviews.append({
                    "vendor_id": vendor.vendor_id,
                    "name": vendor.name,
                    "review_date": vendor.next_review_date.isoformat(),
                    "risk_level": vendor.latest_assessment.risk_level.value if vendor.latest_assessment else "not_assessed"
                })
        
        # Critical issues
        critical_issues = []
        for vendor in self.vendors.values():
            if vendor.latest_assessment and vendor.latest_assessment.risk_level == RiskLevel.CRITICAL:
                critical_issues.append({
                    "vendor_id": vendor.vendor_id,
                    "name": vendor.name,
                    "risk_score": vendor.latest_assessment.overall_risk_score,
                    "remediation_actions": vendor.latest_assessment.remediation_actions
                })
        
        return {
            "dashboard_date": datetime.now().isoformat(),
            "summary": {
                "total_vendors": total_vendors,
                "assessed_vendors": assessed_vendors,
                "assessment_completion_rate": (assessed_vendors / total_vendors * 100) if total_vendors > 0 else 0,
                "critical_risk_vendors": risk_breakdown["critical"],
                "high_risk_vendors": risk_breakdown["high"]
            },
            "risk_breakdown": risk_breakdown,
            "approval_breakdown": approval_breakdown,
            "vendor_type_breakdown": type_breakdown,
            "upcoming_reviews": upcoming_reviews,
            "critical_issues": critical_issues,
            "compliance_metrics": {
                "gdpr_compliant_vendors": len([v for v in self.vendors.values() 
                                             if v.compliance_assessment and v.compliance_assessment.gdpr_compliant]),
                "dpa_signed_vendors": len([v for v in self.vendors.values() 
                                         if v.compliance_assessment and v.compliance_assessment.dpa_signed]),
                "international_transfer_vendors": len([v for v in self.vendors.values() 
                                                     if v.data_processing and v.data_processing.international_transfers])
            }
        }
    
    def generate_vendor_assessment_report(self, vendor_id: str) -> Dict[str, Any]:
        """Generate detailed assessment report for a vendor"""
        
        if vendor_id not in self.vendors:
            raise ValueError(f"Vendor {vendor_id} not found")
        
        vendor = self.vendors[vendor_id]
        
        return {
            "vendor_information": {
                "vendor_id": vendor.vendor_id,
                "name": vendor.name,
                "legal_name": vendor.legal_name,
                "vendor_type": vendor.vendor_type.value,
                "headquarters_country": vendor.headquarters_country,
                "website": vendor.website,
                "services_description": vendor.services_description,
                "contract_period": {
                    "start_date": vendor.contract_start_date.isoformat(),
                    "end_date": vendor.contract_end_date.isoformat() if vendor.contract_end_date else None
                },
                "responsible_person": vendor.responsible_person
            },
            "contacts": [
                {
                    "name": contact.name,
                    "role": contact.role,
                    "email": contact.email,
                    "is_primary": contact.is_primary,
                    "is_dpo": contact.is_dpo,
                    "is_security_contact": contact.is_security_contact
                } for contact in vendor.contacts
            ],
            "data_processing": asdict(vendor.data_processing) if vendor.data_processing else None,
            "security_assessment": asdict(vendor.security_assessment) if vendor.security_assessment else None,
            "compliance_assessment": asdict(vendor.compliance_assessment) if vendor.compliance_assessment else None,
            "latest_assessment": asdict(vendor.latest_assessment) if vendor.latest_assessment else None,
            "status": {
                "assessment_status": vendor.assessment_status.value,
                "approval_status": vendor.approval_status,
                "next_review_date": vendor.next_review_date.isoformat()
            },
            "report_generated": datetime.now().isoformat()
        }