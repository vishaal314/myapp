"""
AI Act Compliance Calculator
Comprehensive tool for calculating AI Act 2025 compliance requirements and risk scores
"""

import streamlit as st
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import uuid

class AISystemRiskLevel(Enum):
    """AI System Risk Levels according to EU AI Act"""
    UNACCEPTABLE = "unacceptable"
    HIGH_RISK = "high_risk"
    LIMITED_RISK = "limited_risk"
    MINIMAL_RISK = "minimal_risk"

class AIActArticle(Enum):
    """Key AI Act Articles for compliance checking"""
    ARTICLE_5 = "article_5"  # Prohibited practices
    ARTICLE_6 = "article_6"  # Classification rules
    ARTICLE_9 = "article_9"  # Risk management
    ARTICLE_10 = "article_10"  # Data and data governance
    ARTICLE_11 = "article_11"  # Technical documentation
    ARTICLE_12 = "article_12"  # Record keeping
    ARTICLE_13 = "article_13"  # Transparency and information
    ARTICLE_14 = "article_14"  # Human oversight
    ARTICLE_15 = "article_15"  # Accuracy, robustness, cybersecurity

@dataclass
class AISystemProfile:
    """Profile of an AI system for compliance assessment"""
    system_name: str
    purpose: str
    use_case: str
    deployment_context: str
    data_types: List[str]
    user_groups: List[str]
    decision_impact: str
    automation_level: str
    human_oversight: bool
    data_processing_scope: str
    geographic_deployment: List[str]
    regulatory_context: str

@dataclass
class ComplianceRequirement:
    """Individual compliance requirement"""
    article: AIActArticle
    requirement: str
    description: str
    mandatory: bool
    deadline: Optional[str]
    implementation_effort: str  # Low, Medium, High, Very High

@dataclass
class ComplianceAssessment:
    """Complete compliance assessment result"""
    system_profile: AISystemProfile
    risk_level: AISystemRiskLevel
    compliance_score: float
    requirements: List[ComplianceRequirement]
    gaps: List[str]
    recommendations: List[str]
    implementation_timeline: Dict[str, str]
    cost_estimate: Dict[str, float]
    fine_risk: float

class AIActCalculator:
    """AI Act Compliance Calculator"""
    
    def __init__(self, region: str = "Netherlands"):
        self.region = region
        self.high_risk_use_cases = self._load_high_risk_use_cases()
        self.prohibited_practices = self._load_prohibited_practices()
        self.compliance_articles = self._load_compliance_articles()
        
    def _load_high_risk_use_cases(self) -> List[Dict[str, Any]]:
        """Load high-risk AI use cases from AI Act Annex III"""
        return [
            {
                "category": "Biometric identification",
                "description": "Real-time remote biometric identification systems",
                "examples": ["Facial recognition", "Voice recognition", "Gait analysis"],
                "risk_multiplier": 2.0
            },
            {
                "category": "Critical infrastructure",
                "description": "AI systems for critical infrastructure management",
                "examples": ["Traffic management", "Power grid control", "Water supply"],
                "risk_multiplier": 1.8
            },
            {
                "category": "Education and training",
                "description": "AI systems for educational assessment",
                "examples": ["Automated grading", "Student evaluation", "Admission systems"],
                "risk_multiplier": 1.5
            },
            {
                "category": "Employment",
                "description": "AI systems for recruitment and HR",
                "examples": ["CV screening", "Interview assessment", "Performance evaluation"],
                "risk_multiplier": 1.6
            },
            {
                "category": "Essential services",
                "description": "AI systems for essential private/public services",
                "examples": ["Credit scoring", "Insurance assessment", "Healthcare diagnosis"],
                "risk_multiplier": 1.7
            },
            {
                "category": "Law enforcement",
                "description": "AI systems for law enforcement purposes",
                "examples": ["Crime prediction", "Evidence analysis", "Risk assessment"],
                "risk_multiplier": 1.9
            },
            {
                "category": "Migration and asylum",
                "description": "AI systems for migration/asylum decisions",
                "examples": ["Visa processing", "Asylum assessment", "Border control"],
                "risk_multiplier": 1.8
            },
            {
                "category": "Democratic processes",
                "description": "AI systems influencing democratic processes",
                "examples": ["Voting systems", "Election monitoring", "Political analysis"],
                "risk_multiplier": 2.0
            }
        ]
    
    def _load_prohibited_practices(self) -> List[Dict[str, Any]]:
        """Load prohibited AI practices from AI Act Article 5"""
        return [
            {
                "practice": "Subliminal techniques",
                "description": "AI systems using subliminal techniques to manipulate behavior",
                "fine_risk": 35000000  # €35M or 7% of annual turnover
            },
            {
                "practice": "Exploiting vulnerabilities",
                "description": "AI systems exploiting vulnerabilities of specific groups",
                "fine_risk": 35000000
            },
            {
                "practice": "Social scoring",
                "description": "General-purpose social scoring systems by public authorities",
                "fine_risk": 35000000
            },
            {
                "practice": "Real-time biometric identification",
                "description": "Real-time remote biometric identification in public spaces",
                "fine_risk": 35000000
            }
        ]
    
    def _load_compliance_articles(self) -> Dict[AIActArticle, Dict[str, Any]]:
        """Load compliance requirements by AI Act article"""
        return {
            AIActArticle.ARTICLE_9: {
                "title": "Risk Management System",
                "requirements": [
                    "Establish, implement, document and maintain a risk management system",
                    "Continuously monitor and update risk assessment",
                    "Identify and analyze known and foreseeable risks",
                    "Implement appropriate risk mitigation measures"
                ],
                "deadline": "2025-08-02",
                "implementation_effort": "High",
                "cost_estimate": 25000
            },
            AIActArticle.ARTICLE_10: {
                "title": "Data and Data Governance",
                "requirements": [
                    "Ensure training data is relevant, representative and error-free",
                    "Implement data governance and management practices",
                    "Examine training data for possible biases",
                    "Identify data gaps and implement mitigation measures"
                ],
                "deadline": "2025-08-02",
                "implementation_effort": "High",
                "cost_estimate": 30000
            },
            AIActArticle.ARTICLE_11: {
                "title": "Technical Documentation",
                "requirements": [
                    "Draw up technical documentation before placing on market",
                    "Ensure documentation demonstrates conformity with requirements",
                    "Keep documentation up-to-date",
                    "Make documentation available to authorities"
                ],
                "deadline": "2025-08-02",
                "implementation_effort": "Medium",
                "cost_estimate": 15000
            },
            AIActArticle.ARTICLE_12: {
                "title": "Record Keeping",
                "requirements": [
                    "Ensure automatic recording of events during operation",
                    "Maintain logs for appropriate periods",
                    "Ensure logs are protected against tampering",
                    "Make logs available to authorities"
                ],
                "deadline": "2025-08-02",
                "implementation_effort": "Medium",
                "cost_estimate": 20000
            },
            AIActArticle.ARTICLE_13: {
                "title": "Transparency and Information",
                "requirements": [
                    "Ensure AI systems are designed to be sufficiently transparent",
                    "Provide clear and adequate information to users",
                    "Enable users to interpret system outputs",
                    "Facilitate human oversight"
                ],
                "deadline": "2025-08-02",
                "implementation_effort": "Medium",
                "cost_estimate": 18000
            },
            AIActArticle.ARTICLE_14: {
                "title": "Human Oversight",
                "requirements": [
                    "Ensure effective human oversight during system operation",
                    "Design systems to enable human intervention",
                    "Ensure humans can interrupt or stop system operation",
                    "Enable humans to understand system capabilities and limitations"
                ],
                "deadline": "2025-08-02",
                "implementation_effort": "High",
                "cost_estimate": 35000
            },
            AIActArticle.ARTICLE_15: {
                "title": "Accuracy, Robustness and Cybersecurity",
                "requirements": [
                    "Ensure appropriate level of accuracy",
                    "Ensure robustness against errors and faults",
                    "Implement cybersecurity measures",
                    "Maintain performance throughout system lifecycle"
                ],
                "deadline": "2025-08-02",
                "implementation_effort": "Very High",
                "cost_estimate": 45000
            }
        }
    
    def classify_ai_system(self, system_profile: AISystemProfile) -> AISystemRiskLevel:
        """Classify AI system risk level according to AI Act"""
        
        # Check for prohibited practices
        if self._is_prohibited_practice(system_profile):
            return AISystemRiskLevel.UNACCEPTABLE
        
        # Check for high-risk use cases
        if self._is_high_risk_use_case(system_profile):
            return AISystemRiskLevel.HIGH_RISK
        
        # Check for limited risk indicators
        if self._is_limited_risk_use_case(system_profile):
            return AISystemRiskLevel.LIMITED_RISK
        
        # Default to minimal risk
        return AISystemRiskLevel.MINIMAL_RISK
    
    def _is_prohibited_practice(self, system_profile: AISystemProfile) -> bool:
        """Check if system involves prohibited practices"""
        prohibited_keywords = [
            "subliminal", "manipulation", "social scoring", "vulnerabilities exploitation",
            "real-time biometric identification", "emotion recognition children"
        ]
        
        system_text = f"{system_profile.purpose} {system_profile.use_case} {system_profile.deployment_context}".lower()
        
        for keyword in prohibited_keywords:
            if keyword in system_text:
                return True
        
        return False
    
    def _is_high_risk_use_case(self, system_profile: AISystemProfile) -> bool:
        """Check if system falls under high-risk use cases"""
        
        # Check against known high-risk categories
        for use_case in self.high_risk_use_cases:
            if any(example.lower() in system_profile.use_case.lower() for example in use_case["examples"]):
                return True
        
        # Additional high-risk indicators
        high_risk_indicators = [
            "biometric identification",
            "critical infrastructure",
            "educational assessment",
            "employment screening",
            "credit scoring",
            "law enforcement",
            "medical diagnosis",
            "migration assessment"
        ]
        
        system_text = f"{system_profile.purpose} {system_profile.use_case}".lower()
        
        for indicator in high_risk_indicators:
            if indicator in system_text:
                return True
        
        # Check decision impact
        if system_profile.decision_impact in ["High", "Critical"]:
            return True
        
        # Check automation level
        if system_profile.automation_level in ["Fully automated", "Mostly automated"] and not system_profile.human_oversight:
            return True
        
        return False
    
    def _is_limited_risk_use_case(self, system_profile: AISystemProfile) -> bool:
        """Check if system falls under limited risk use cases"""
        
        limited_risk_indicators = [
            "chatbot", "virtual assistant", "content generation", "emotion recognition",
            "recommendation system", "personalization", "content moderation"
        ]
        
        system_text = f"{system_profile.purpose} {system_profile.use_case}".lower()
        
        for indicator in limited_risk_indicators:
            if indicator in system_text:
                return True
        
        return False
    
    def calculate_compliance_score(self, system_profile: AISystemProfile, 
                                 current_compliance: Dict[str, bool]) -> float:
        """Calculate compliance score based on current implementation"""
        
        risk_level = self.classify_ai_system(system_profile)
        
        if risk_level == AISystemRiskLevel.UNACCEPTABLE:
            return 0.0  # Prohibited systems cannot be compliant
        
        if risk_level == AISystemRiskLevel.MINIMAL_RISK:
            return 95.0  # Minimal requirements
        
        # Calculate based on implemented requirements
        total_requirements = 0
        implemented_requirements = 0
        
        applicable_articles = self._get_applicable_articles(risk_level)
        
        for article in applicable_articles:
            article_requirements = self.compliance_articles[article]["requirements"]
            total_requirements += len(article_requirements)
            
            if current_compliance.get(article.value, False):
                implemented_requirements += len(article_requirements)
        
        if total_requirements == 0:
            return 95.0
        
        base_score = (implemented_requirements / total_requirements) * 100
        
        # Apply risk-based adjustments
        if risk_level == AISystemRiskLevel.HIGH_RISK:
            # High-risk systems need stricter compliance
            base_score *= 0.9
        
        return min(100.0, max(0.0, base_score))
    
    def _get_applicable_articles(self, risk_level: AISystemRiskLevel) -> List[AIActArticle]:
        """Get applicable AI Act articles based on risk level"""
        
        if risk_level == AISystemRiskLevel.MINIMAL_RISK:
            return [AIActArticle.ARTICLE_13]  # Basic transparency
        
        if risk_level == AISystemRiskLevel.LIMITED_RISK:
            return [
                AIActArticle.ARTICLE_13,  # Transparency
                AIActArticle.ARTICLE_14   # Human oversight
            ]
        
        if risk_level == AISystemRiskLevel.HIGH_RISK:
            return [
                AIActArticle.ARTICLE_9,   # Risk management
                AIActArticle.ARTICLE_10,  # Data governance
                AIActArticle.ARTICLE_11,  # Technical documentation
                AIActArticle.ARTICLE_12,  # Record keeping
                AIActArticle.ARTICLE_13,  # Transparency
                AIActArticle.ARTICLE_14,  # Human oversight
                AIActArticle.ARTICLE_15   # Accuracy, robustness, cybersecurity
            ]
        
        return []
    
    def generate_compliance_requirements(self, system_profile: AISystemProfile) -> List[ComplianceRequirement]:
        """Generate specific compliance requirements for the system"""
        
        risk_level = self.classify_ai_system(system_profile)
        applicable_articles = self._get_applicable_articles(risk_level)
        
        requirements = []
        
        for article in applicable_articles:
            article_info = self.compliance_articles[article]
            
            for req_text in article_info["requirements"]:
                requirement = ComplianceRequirement(
                    article=article,
                    requirement=req_text,
                    description=f"{article_info['title']}: {req_text}",
                    mandatory=True,
                    deadline=article_info["deadline"],
                    implementation_effort=article_info["implementation_effort"]
                )
                requirements.append(requirement)
        
        return requirements
    
    def assess_compliance_gaps(self, system_profile: AISystemProfile, 
                             current_compliance: Dict[str, bool]) -> List[str]:
        """Assess compliance gaps and provide specific recommendations"""
        
        gaps = []
        requirements = self.generate_compliance_requirements(system_profile)
        
        for requirement in requirements:
            if not current_compliance.get(requirement.article.value, False):
                gaps.append(f"Missing: {requirement.description}")
        
        return gaps
    
    def calculate_fine_risk(self, system_profile: AISystemProfile, 
                           compliance_score: float, annual_turnover: float) -> float:
        """Calculate potential fine risk based on compliance score"""
        
        risk_level = self.classify_ai_system(system_profile)
        
        if risk_level == AISystemRiskLevel.UNACCEPTABLE:
            return min(35000000, annual_turnover * 0.07)  # Maximum fine
        
        if risk_level == AISystemRiskLevel.HIGH_RISK:
            # High-risk systems face significant fines only if non-compliant
            non_compliance_factor = max(0, (100 - compliance_score) / 100)
            max_fine = min(35000000, annual_turnover * 0.07)
            
            # Apply exponential reduction for high compliance scores
            if compliance_score >= 85:
                # Very low risk for high compliance scores
                non_compliance_factor *= 0.1  # 90% reduction in fine risk
            elif compliance_score >= 70:
                # Moderate risk reduction
                non_compliance_factor *= 0.3  # 70% reduction in fine risk
            
            return max_fine * non_compliance_factor
        
        if risk_level == AISystemRiskLevel.LIMITED_RISK:
            # Limited risk systems face lower fines
            non_compliance_factor = max(0, (100 - compliance_score) / 100)
            max_fine = min(15000000, annual_turnover * 0.03)
            
            # Apply reduction for good compliance
            if compliance_score >= 80:
                non_compliance_factor *= 0.2  # 80% reduction
            
            return max_fine * non_compliance_factor
        
        # Minimal risk systems have very low fine risk
        return 0.0
    
    def generate_implementation_timeline(self, system_profile: AISystemProfile) -> Dict[str, str]:
        """Generate implementation timeline based on system complexity"""
        
        risk_level = self.classify_ai_system(system_profile)
        
        if risk_level == AISystemRiskLevel.MINIMAL_RISK:
            return {
                "Week 1": "Review transparency requirements",
                "Week 2": "Implement basic user information",
                "Week 3": "Test and validate implementation",
                "Week 4": "Documentation and final review"
            }
        
        if risk_level == AISystemRiskLevel.LIMITED_RISK:
            return {
                "Week 1-2": "Implement transparency measures",
                "Week 3-4": "Design human oversight protocols",
                "Week 5-6": "Test oversight mechanisms",
                "Week 7-8": "Documentation and compliance validation"
            }
        
        if risk_level == AISystemRiskLevel.HIGH_RISK:
            return {
                "Month 1": "Risk management system design and implementation",
                "Month 2": "Data governance and quality assurance implementation",
                "Month 3": "Technical documentation and record keeping systems",
                "Month 4": "Human oversight and transparency implementation",
                "Month 5": "Accuracy, robustness and cybersecurity measures",
                "Month 6": "Testing, validation and final compliance review"
            }
        
        return {"Immediate": "System is prohibited - discontinue use"}
    
    def estimate_implementation_cost(self, system_profile: AISystemProfile) -> Dict[str, float]:
        """Estimate implementation costs based on system requirements"""
        
        risk_level = self.classify_ai_system(system_profile)
        applicable_articles = self._get_applicable_articles(risk_level)
        
        costs = {}
        total_cost = 0
        
        for article in applicable_articles:
            article_cost = self.compliance_articles[article]["cost_estimate"]
            costs[article.value] = article_cost
            total_cost += article_cost
        
        # Add overhead costs
        costs["project_management"] = total_cost * 0.15
        costs["legal_consultation"] = 15000
        costs["audit_and_certification"] = 10000
        
        # Calculate total with overhead
        total_with_overhead = total_cost + costs["project_management"] + costs["legal_consultation"] + costs["audit_and_certification"]
        costs["total_estimated_cost"] = total_with_overhead
        
        return costs
    
    def perform_complete_assessment(self, system_profile: AISystemProfile, 
                                  current_compliance: Dict[str, bool],
                                  annual_turnover: float) -> ComplianceAssessment:
        """Perform complete AI Act compliance assessment"""
        
        risk_level = self.classify_ai_system(system_profile)
        compliance_score = self.calculate_compliance_score(system_profile, current_compliance)
        requirements = self.generate_compliance_requirements(system_profile)
        gaps = self.assess_compliance_gaps(system_profile, current_compliance)
        fine_risk = self.calculate_fine_risk(system_profile, compliance_score, annual_turnover)
        timeline = self.generate_implementation_timeline(system_profile)
        costs = self.estimate_implementation_cost(system_profile)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_level, compliance_score, gaps)
        
        return ComplianceAssessment(
            system_profile=system_profile,
            risk_level=risk_level,
            compliance_score=compliance_score,
            requirements=requirements,
            gaps=gaps,
            recommendations=recommendations,
            implementation_timeline=timeline,
            cost_estimate=costs,
            fine_risk=fine_risk
        )
    
    def _generate_recommendations(self, risk_level: AISystemRiskLevel, 
                                compliance_score: float, gaps: List[str]) -> List[str]:
        """Generate specific recommendations based on assessment"""
        
        recommendations = []
        
        if risk_level == AISystemRiskLevel.UNACCEPTABLE:
            recommendations.append("🚨 IMMEDIATE ACTION REQUIRED: System involves prohibited practices")
            recommendations.append("Discontinue system use immediately")
            recommendations.append("Consult legal counsel for compliance strategy")
            return recommendations
        
        if risk_level == AISystemRiskLevel.HIGH_RISK:
            if compliance_score >= 85:
                # Well-managed high-risk systems get specific maintenance recommendations
                recommendations.append("✅ MAINTAIN EXCELLENCE: Continue robust compliance monitoring")
                recommendations.append("📋 Conduct quarterly AI Act compliance audits")
                recommendations.append("🔄 Update risk assessment documentation annually")
                recommendations.append("👥 Ensure AI governance team receives ongoing training")
                recommendations.append("📊 Monitor algorithmic performance for bias or drift")
            elif compliance_score >= 70:
                # Good compliance systems need targeted improvements
                recommendations.append("🟡 STRENGTHEN COMPLIANCE: Focus on remaining gaps")
                recommendations.append("📈 Improve data governance and quality assurance")
                recommendations.append("🛡️ Enhance cybersecurity measures for AI systems")
                recommendations.append("📋 Complete technical documentation requirements")
                recommendations.append("👁️ Strengthen human oversight mechanisms")
            else:
                # Poor compliance systems need urgent action
                recommendations.append("🔴 URGENT: Implement comprehensive compliance program")
                recommendations.append("⚠️ HIGH FINE RISK: Immediate remediation required")
                recommendations.append("🏢 Establish dedicated AI compliance team")
                recommendations.append("👨‍💼 Engage external AI Act compliance consultant")
                recommendations.append("🚨 Implement emergency risk mitigation measures")
            
        if risk_level == AISystemRiskLevel.LIMITED_RISK:
            recommendations.append("🟡 IMPLEMENT TRANSPARENCY: Ensure users know they're interacting with AI")
            recommendations.append("👁️ Establish basic human oversight procedures")
            recommendations.append("📋 Document AI system capabilities and limitations")
            recommendations.append("🔄 Monitor for use case expansion that might increase risk")
            
        if risk_level == AISystemRiskLevel.MINIMAL_RISK:
            recommendations.append("🟢 BASIC TRANSPARENCY: Inform users about AI system use")
            recommendations.append("📝 Maintain simple documentation of system purpose")
            recommendations.append("👀 Monitor for changes in use case or data types")
            recommendations.append("📊 Conduct annual review of risk classification")
        
        # Add specific gap-based recommendations
        if len(gaps) > 5:
            recommendations.append(f"🎯 PRIORITIZE GAPS: Address {len(gaps)} compliance gaps systematically")
            recommendations.append("📅 Create 6-month action plan with milestone reviews")
        elif len(gaps) > 0:
            recommendations.append(f"🔧 CLOSE GAPS: Address remaining {len(gaps)} compliance requirements")
        
        # Netherlands-specific recommendations
        if self.region == "Netherlands":
            recommendations.append("🇳🇱 NETHERLANDS COMPLIANCE: Align with Dutch DPA guidance on AI Act")
            if compliance_score < 85:
                recommendations.append("📞 Consider consultation with Dutch AI Act legal specialist")
                recommendations.append("🏛️ Review registration requirements with Dutch Data Protection Authority")
            recommendations.append("🆔 Implement proper BSN handling if processing Dutch citizen data")
            recommendations.append("📋 Ensure Dutch language transparency notices where required")
        
        return recommendations
    
    def export_assessment_report(self, assessment: ComplianceAssessment) -> Dict[str, Any]:
        """Export assessment as comprehensive report"""
        
        return {
            "assessment_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "region": self.region,
            "system_profile": {
                "system_name": assessment.system_profile.system_name,
                "purpose": assessment.system_profile.purpose,
                "use_case": assessment.system_profile.use_case,
                "deployment_context": assessment.system_profile.deployment_context,
                "data_types": assessment.system_profile.data_types,
                "user_groups": assessment.system_profile.user_groups,
                "decision_impact": assessment.system_profile.decision_impact,
                "automation_level": assessment.system_profile.automation_level,
                "human_oversight": assessment.system_profile.human_oversight,
                "data_processing_scope": assessment.system_profile.data_processing_scope,
                "geographic_deployment": assessment.system_profile.geographic_deployment,
                "regulatory_context": assessment.system_profile.regulatory_context
            },
            "risk_assessment": {
                "risk_level": assessment.risk_level.value,
                "compliance_score": assessment.compliance_score,
                "fine_risk": assessment.fine_risk
            },
            "requirements": [
                {
                    "article": req.article.value,
                    "requirement": req.requirement,
                    "description": req.description,
                    "mandatory": req.mandatory,
                    "deadline": req.deadline,
                    "implementation_effort": req.implementation_effort
                }
                for req in assessment.requirements
            ],
            "gaps": assessment.gaps,
            "recommendations": assessment.recommendations,
            "implementation_timeline": assessment.implementation_timeline,
            "cost_estimate": assessment.cost_estimate,
            "netherlands_specific": {
                "uavg_compliance": True,
                "bsn_handling": "person_data" in assessment.system_profile.data_types,
                "dpa_registration": assessment.risk_level == AISystemRiskLevel.HIGH_RISK
            }
        }