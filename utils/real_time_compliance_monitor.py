"""
Real-Time Compliance Monitoring System

Implements continuous compliance checking, automated DPIA triggering,
DPO requirements assessment, and cross-border transfer validation.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

class RealTimeComplianceMonitor:
    """Real-time compliance monitoring for GDPR and EU AI Act 2025."""
    
    def __init__(self):
        self.monitoring_active = True
        self.last_assessment = datetime.now()
        self.compliance_thresholds = {
            'dpia_trigger_score': 75,
            'dpo_requirement_score': 80,
            'critical_violation_limit': 5,
            'assessment_frequency_hours': 24
        }
    
    def perform_real_time_assessment(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform comprehensive real-time compliance assessment."""
        findings = []
        
        # Real-time AI system monitoring
        ai_monitoring_results = self._monitor_ai_systems_continuously(content)
        findings.extend(ai_monitoring_results['findings'])
        
        # Automated DPIA triggering
        dpia_assessment = self._trigger_automated_dpia_assessment(content, metadata or {})
        findings.extend(dpia_assessment['findings'])
        
        # DPO requirement assessment
        dpo_assessment = self._assess_dpo_requirements_automated(content, metadata or {})
        findings.extend(dpo_assessment['findings'])
        
        # Cross-border transfer validation
        transfer_validation = self._validate_cross_border_transfers_enhanced(content)
        findings.extend(transfer_validation['findings'])
        
        # AI governance framework detection
        governance_assessment = self._detect_ai_governance_framework(content)
        findings.extend(governance_assessment['findings'])
        
        # Calculate overall compliance score
        compliance_score = self._calculate_real_time_compliance_score(findings)
        
        return {
            'assessment_timestamp': datetime.now().isoformat(),
            'monitoring_active': self.monitoring_active,
            'total_findings': len(findings),
            'compliance_score': compliance_score,
            'critical_violations': len([f for f in findings if f.get('severity') == 'Critical']),
            'high_priority_items': len([f for f in findings if f.get('severity') == 'High']),
            'findings': findings,
            'next_assessment_due': (datetime.now() + timedelta(hours=self.compliance_thresholds['assessment_frequency_hours'])).isoformat(),
            'recommendations': self._generate_priority_recommendations(findings)
        }
    
    def _monitor_ai_systems_continuously(self, content: str) -> Dict[str, Any]:
        """Continuous monitoring of AI systems for compliance changes."""
        findings = []
        
        # AI system lifecycle monitoring
        ai_lifecycle_patterns = {
            "development_phase": r"\b(?:ai.*development|model.*training|algorithm.*design|system.*development)\b",
            "testing_phase": r"\b(?:ai.*testing|model.*validation|system.*testing|performance.*testing)\b",
            "deployment_phase": r"\b(?:ai.*deployment|model.*deployment|production.*deployment|system.*launch)\b",
            "monitoring_phase": r"\b(?:ai.*monitoring|model.*monitoring|performance.*monitoring|system.*monitoring)\b",
            "maintenance_phase": r"\b(?:ai.*maintenance|model.*maintenance|system.*updates|continuous.*improvement)\b"
        }
        
        detected_phases = []
        for phase, pattern in ai_lifecycle_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                detected_phases.append(phase)
        
        # Continuous risk assessment patterns
        risk_indicators = {
            "high_risk_changes": r"\b(?:model.*update|algorithm.*change|data.*change|system.*modification)\b",
            "performance_degradation": r"\b(?:performance.*degradation|accuracy.*drop|bias.*increase|error.*rate.*increase)\b",
            "new_use_cases": r"\b(?:new.*use.*case|expanded.*functionality|additional.*purpose|scope.*change)\b",
            "user_feedback": r"\b(?:user.*feedback|complaint|incident.*report|issue.*report)\b"
        }
        
        continuous_risks = []
        for risk_type, pattern in risk_indicators.items():
            if re.search(pattern, content, re.IGNORECASE):
                continuous_risks.append(risk_type)
        
        if detected_phases and continuous_risks:
            findings.append({
                'type': 'AI_SYSTEM_CONTINUOUS_MONITORING_REQUIRED',
                'category': 'Real-Time AI Monitoring',
                'severity': 'High',
                'title': 'Continuous AI System Monitoring Required',
                'description': f'AI system in {len(detected_phases)} lifecycle phases with {len(continuous_risks)} risk factors',
                'article_reference': 'EU AI Act Articles 61-68 (Post-Market Monitoring)',
                'detected_phases': detected_phases,
                'risk_factors': continuous_risks,
                'monitoring_requirements': [
                    'Real-time performance monitoring',
                    'Continuous bias detection',
                    'User feedback integration',
                    'Regular risk reassessment'
                ],
                'compliance_deadline': 'Continuous - Real-time monitoring required',
                'penalty_risk': 'Up to €15M or 3% global turnover',
                'remediation': 'Implement continuous AI system monitoring with automated alerts'
            })
        
        return {'findings': findings}
    
    def _trigger_automated_dpia_assessment(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Smart threshold detection for automated DPIA triggering."""
        findings = []
        
        # Enhanced DPIA triggering algorithm
        dpia_risk_factors = {
            "automated_decision_making": {
                "pattern": r"\b(?:automated.*decision|algorithmic.*decision|ai.*decision|machine.*decision)\b",
                "weight": 25,
                "description": "Automated decision-making detected"
            },
            "large_scale_processing": {
                "pattern": r"\b(?:large.*scale|mass.*processing|bulk.*data|millions.*records|thousands.*users)\b",
                "weight": 20,
                "description": "Large-scale processing detected"
            },
            "special_categories": {
                "pattern": r"\b(?:health.*data|biometric.*data|genetic.*data|racial.*data|political.*opinion)\b",
                "weight": 30,
                "description": "Special categories of personal data detected"
            },
            "systematic_monitoring": {
                "pattern": r"\b(?:systematic.*monitoring|surveillance|tracking|behavioral.*analysis)\b",
                "weight": 25,
                "description": "Systematic monitoring detected"
            },
            "vulnerable_subjects": {
                "pattern": r"\b(?:children|minors|elderly|disabled|vulnerable.*individuals)\b",
                "weight": 20,
                "description": "Vulnerable data subjects detected"
            },
            "innovative_technology": {
                "pattern": r"\b(?:ai|machine.*learning|deep.*learning|neural.*network|innovative.*technology)\b",
                "weight": 15,
                "description": "Innovative technology detected"
            },
            "public_area_monitoring": {
                "pattern": r"\b(?:cctv|video.*surveillance|facial.*recognition|public.*monitoring)\b",
                "weight": 25,
                "description": "Public area monitoring detected"
            },
            "cross_border_processing": {
                "pattern": r"\b(?:cross.*border|international.*transfer|third.*country)\b",
                "weight": 15,
                "description": "Cross-border data processing detected"
            }
        }
        
        # Calculate DPIA risk score
        total_risk_score = 0
        triggered_factors = []
        
        for factor, config in dpia_risk_factors.items():
            if re.search(config["pattern"], content, re.IGNORECASE):
                total_risk_score += config["weight"]
                triggered_factors.append({
                    'factor': factor,
                    'weight': config['weight'],
                    'description': config['description']
                })
        
        # Check for existing DPIA
        existing_dpia_patterns = [
            r"\b(?:dpia|data.*protection.*impact.*assessment|privacy.*impact.*assessment)\b",
            r"\b(?:impact.*assessment.*completed|dpia.*conducted|privacy.*assessment.*done)\b"
        ]
        
        has_existing_dpia = any(re.search(pattern, content, re.IGNORECASE) for pattern in existing_dpia_patterns)
        
        # Automated DPIA triggering logic
        if total_risk_score >= self.compliance_thresholds['dpia_trigger_score'] and not has_existing_dpia:
            findings.append({
                'type': 'AUTOMATED_DPIA_TRIGGER_ACTIVATED',
                'category': 'Automated DPIA Triggering',
                'severity': 'Critical',
                'title': 'Automated DPIA Assessment Triggered',
                'description': f'DPIA risk score {total_risk_score} exceeds threshold {self.compliance_thresholds["dpia_trigger_score"]}',
                'article_reference': 'GDPR Article 35',
                'risk_score': total_risk_score,
                'threshold': self.compliance_thresholds['dpia_trigger_score'],
                'triggered_factors': triggered_factors,
                'dpia_required': True,
                'compliance_deadline': 'Before processing begins',
                'penalty_risk': 'Up to €10M or 2% global turnover + processing prohibition',
                'automated_action': 'DPIA template generated, stakeholders notified',
                'remediation': 'Complete Data Protection Impact Assessment immediately'
            })
        elif total_risk_score >= 50 and not has_existing_dpia:
            findings.append({
                'type': 'AUTOMATED_DPIA_RECOMMENDED',
                'category': 'Automated DPIA Triggering',
                'severity': 'High',
                'title': 'DPIA Recommended by Automated Assessment',
                'description': f'DPIA risk score {total_risk_score} suggests assessment recommended',
                'risk_score': total_risk_score,
                'triggered_factors': triggered_factors,
                'recommendation': 'Consider conducting Data Protection Impact Assessment'
            })
        
        return {'findings': findings}
    
    def _assess_dpo_requirements_automated(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Automated assessment of Data Protection Officer appointment requirements."""
        findings = []
        
        # DPO requirement scoring system
        dpo_criteria = {
            "public_authority": {
                "pattern": r"\b(?:public.*authority|government.*body|municipal.*authority|state.*agency)\b",
                "score": 100,
                "mandatory": True,
                "description": "Public authority - DPO mandatory"
            },
            "large_scale_monitoring": {
                "pattern": r"\b(?:large.*scale.*monitoring|systematic.*monitoring|mass.*surveillance)\b",
                "score": 100,
                "mandatory": True,
                "description": "Large-scale systematic monitoring - DPO mandatory"
            },
            "special_categories_core": {
                "pattern": r"\b(?:core.*activit.*special|primary.*business.*sensitive|main.*operation.*health)\b",
                "score": 100,
                "mandatory": True,
                "description": "Core activities involve special categories - DPO mandatory"
            },
            "employee_count_large": {
                "pattern": r"\b(?:250.*employ|500.*employ|1000.*employ|large.*organization|enterprise)\b",
                "score": 80,
                "mandatory": False,
                "description": "Large organization - DPO recommended"
            },
            "international_operations": {
                "pattern": r"\b(?:international.*operation|multinational|global.*company|cross.*border.*business)\b",
                "score": 60,
                "mandatory": False,
                "description": "International operations - DPO beneficial"
            },
            "complex_processing": {
                "pattern": r"\b(?:complex.*processing|multiple.*data.*sources|advanced.*analytics)\b",
                "score": 40,
                "mandatory": False,
                "description": "Complex processing operations"
            }
        }
        
        # Calculate DPO requirement score
        dpo_score = 0
        mandatory_criteria = []
        recommended_criteria = []
        
        for criterion, config in dpo_criteria.items():
            if re.search(config["pattern"], content, re.IGNORECASE):
                dpo_score += config["score"]
                if config["mandatory"]:
                    mandatory_criteria.append({
                        'criterion': criterion,
                        'description': config['description']
                    })
                else:
                    recommended_criteria.append({
                        'criterion': criterion,
                        'score': config['score'],
                        'description': config['description']
                    })
        
        # Check for existing DPO
        existing_dpo_patterns = [
            r"\b(?:data.*protection.*officer|dpo.*appointed|privacy.*officer|dpo.*contact)\b",
            r"\b(?:dpo@|privacy@|dataprotection@)\b"
        ]
        
        has_existing_dpo = any(re.search(pattern, content, re.IGNORECASE) for pattern in existing_dpo_patterns)
        
        # Automated DPO assessment
        if mandatory_criteria and not has_existing_dpo:
            findings.append({
                'type': 'AUTOMATED_DPO_APPOINTMENT_MANDATORY',
                'category': 'DPO Requirements Assessment',
                'severity': 'Critical',
                'title': 'DPO Appointment Mandatory - Automated Detection',
                'description': f'DPO required due to {len(mandatory_criteria)} mandatory criteria',
                'article_reference': 'GDPR Article 37',
                'mandatory_criteria': mandatory_criteria,
                'compliance_deadline': 'Immediate - before processing',
                'penalty_risk': 'Up to €10M or 2% global turnover',
                'automated_action': 'DPO job description template generated',
                'remediation': 'Appoint qualified Data Protection Officer immediately'
            })
        elif dpo_score >= self.compliance_thresholds['dpo_requirement_score'] and not has_existing_dpo:
            findings.append({
                'type': 'AUTOMATED_DPO_RECOMMENDATION',
                'category': 'DPO Requirements Assessment',
                'severity': 'High',
                'title': 'DPO Appointment Strongly Recommended',
                'description': f'DPO score {dpo_score} exceeds recommendation threshold {self.compliance_thresholds["dpo_requirement_score"]}',
                'dpo_score': dpo_score,
                'recommended_criteria': recommended_criteria,
                'business_benefits': [
                    'Expert compliance guidance',
                    'Reduced regulatory risk',
                    'Enhanced stakeholder confidence',
                    'Streamlined data protection processes'
                ],
                'recommendation': 'Consider appointing Data Protection Officer'
            })
        
        return {'findings': findings}
    
    def _validate_cross_border_transfers_enhanced(self, content: str) -> Dict[str, Any]:
        """Enhanced adequacy decision checking for cross-border transfers."""
        findings = []
        
        # Current adequacy decisions (as of 2025)
        adequacy_countries = {
            "adequate": ["andorra", "argentina", "canada", "faroe islands", "guernsey", "israel", "isle of man", "japan", "jersey", "new zealand", "south korea", "switzerland", "united kingdom", "uk", "uruguay"],
            "partial": ["us", "united states", "usa"],  # For specific frameworks only
            "no_adequacy": ["china", "russia", "india", "brazil", "australia"]  # Major countries without adequacy
        }
        
        # Transfer detection patterns
        transfer_patterns = {
            "cloud_providers": r"\b(?:aws|azure|google.*cloud|oracle.*cloud|alibaba.*cloud|tencent.*cloud)\b",
            "third_countries": r"\b(?:united.*states|usa|china|india|brazil|russia|australia|singapore)\b",
            "data_processing": r"\b(?:data.*processing|server.*location|data.*center|hosting.*location)\b"
        }
        
        # Safeguards detection
        safeguard_patterns = {
            "adequacy_decision": r"\b(?:adequacy.*decision|adequate.*protection|commission.*decision)\b",
            "standard_contractual_clauses": r"\b(?:standard.*contractual.*clauses|scc|model.*clauses)\b",
            "binding_corporate_rules": r"\b(?:binding.*corporate.*rules|bcr)\b",
            "certification": r"\b(?:certification.*scheme|approved.*certification|binding.*code)\b",
            "schrems_ii_measures": r"\b(?:schrems.*ii|supplementary.*measures|additional.*safeguards)\b"
        }
        
        # Detect transfers and countries
        detected_transfers = []
        for transfer_type, pattern in transfer_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                detected_transfers.extend([(transfer_type, match.lower()) for match in matches])
        
        # Analyze country adequacy status
        transfer_analysis = []
        for transfer_type, country_ref in detected_transfers:
            adequacy_status = "unknown"
            for status, countries in adequacy_countries.items():
                if any(country in country_ref for country in countries):
                    adequacy_status = status
                    break
            
            transfer_analysis.append({
                'transfer_type': transfer_type,
                'country_reference': country_ref,
                'adequacy_status': adequacy_status
            })
        
        # Check for implemented safeguards
        implemented_safeguards = []
        for safeguard, pattern in safeguard_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                implemented_safeguards.append(safeguard)
        
        # Enhanced cross-border validation
        high_risk_transfers = [t for t in transfer_analysis if t['adequacy_status'] in ['no_adequacy', 'partial']]
        
        if high_risk_transfers and not implemented_safeguards:
            findings.append({
                'type': 'ENHANCED_CROSS_BORDER_VIOLATION',
                'category': 'Enhanced Cross-Border Validation',
                'severity': 'Critical',
                'title': 'High-Risk International Transfer Without Safeguards',
                'description': f'{len(high_risk_transfers)} high-risk transfers detected without adequate safeguards',
                'article_reference': 'GDPR Articles 44-49',
                'high_risk_transfers': high_risk_transfers,
                'missing_safeguards': list(safeguard_patterns.keys()),
                'adequacy_status_summary': {
                    'no_adequacy': len([t for t in transfer_analysis if t['adequacy_status'] == 'no_adequacy']),
                    'partial_adequacy': len([t for t in transfer_analysis if t['adequacy_status'] == 'partial']),
                    'adequate': len([t for t in transfer_analysis if t['adequacy_status'] == 'adequate'])
                },
                'compliance_deadline': 'Immediate - cease transfers or implement safeguards',
                'penalty_risk': 'Up to €20M or 4% global turnover',
                'automated_action': 'Transfer impact assessment template generated',
                'remediation': 'Implement appropriate transfer safeguards or use adequate jurisdictions'
            })
        
        return {'findings': findings}
    
    def _detect_ai_governance_framework(self, content: str) -> Dict[str, Any]:
        """Detect organizational AI governance framework compliance."""
        findings = []
        
        # AI governance framework components
        governance_components = {
            "ai_policy": r"\b(?:ai.*policy|artificial.*intelligence.*policy|ai.*governance.*policy)\b",
            "ai_committee": r"\b(?:ai.*committee|ai.*board|ai.*governance.*committee|algorithm.*committee)\b",
            "ai_risk_assessment": r"\b(?:ai.*risk.*assessment|algorithm.*risk.*assessment|ai.*impact.*assessment)\b",
            "ai_training": r"\b(?:ai.*training|ai.*awareness|algorithm.*training|ai.*education)\b",
            "ai_documentation": r"\b(?:ai.*documentation|algorithm.*documentation|model.*documentation)\b",
            "ai_monitoring": r"\b(?:ai.*monitoring|algorithm.*monitoring|model.*monitoring)\b",
            "ai_incident_response": r"\b(?:ai.*incident|algorithm.*incident|ai.*emergency.*response)\b",
            "ai_vendor_management": r"\b(?:ai.*vendor|algorithm.*vendor|ai.*supplier.*management)\b"
        }
        
        # Check implementation status
        implemented_components = []
        missing_components = []
        
        for component, pattern in governance_components.items():
            if re.search(pattern, content, re.IGNORECASE):
                implemented_components.append(component)
            else:
                missing_components.append(component)
        
        # AI governance maturity assessment
        governance_maturity = len(implemented_components) / len(governance_components) * 100
        
        if governance_maturity < 50:
            findings.append({
                'type': 'AI_GOVERNANCE_FRAMEWORK_INSUFFICIENT',
                'category': 'AI Governance Framework',
                'severity': 'High',
                'title': 'Insufficient AI Governance Framework',
                'description': f'Only {governance_maturity:.1f}% of governance components implemented',
                'article_reference': 'EU AI Act Article 16 + Organizational Requirements',
                'governance_maturity_score': governance_maturity,
                'implemented_components': implemented_components,
                'missing_components': missing_components,
                'compliance_deadline': 'August 2, 2026',
                'penalty_risk': 'Up to €15M or 3% global turnover',
                'framework_recommendations': [
                    'Establish AI governance committee with executive sponsorship',
                    'Develop comprehensive AI policy covering all use cases',
                    'Implement regular AI risk assessments and audits',
                    'Create AI incident response and escalation procedures',
                    'Provide organization-wide AI ethics and compliance training'
                ],
                'remediation': 'Implement comprehensive AI governance framework'
            })
        
        return {'findings': findings}
    
    def _calculate_real_time_compliance_score(self, findings: List[Dict[str, Any]]) -> int:
        """Calculate real-time compliance score based on findings."""
        if not findings:
            return 100
        
        # Scoring weights by severity
        severity_weights = {
            'Critical': 40,
            'High': 25,
            'Medium': 15,
            'Low': 5
        }
        
        total_deduction = 0
        for finding in findings:
            severity = finding.get('severity', 'Medium')
            total_deduction += severity_weights.get(severity, 15)
        
        # Cap deduction at 95 (minimum score 5)
        total_deduction = min(total_deduction, 95)
        
        return max(5, 100 - total_deduction)
    
    def _generate_priority_recommendations(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Generate prioritized recommendations based on findings."""
        recommendations = []
        
        # Critical findings first
        critical_findings = [f for f in findings if f.get('severity') == 'Critical']
        if critical_findings:
            recommendations.append(f"URGENT: Address {len(critical_findings)} critical compliance violations immediately")
        
        # High priority findings
        high_findings = [f for f in findings if f.get('severity') == 'High']
        if high_findings:
            recommendations.append(f"HIGH PRIORITY: Resolve {len(high_findings)} high-priority compliance issues")
        
        # Specific category recommendations
        finding_types = [f.get('type', '') for f in findings]
        
        if any('DPIA' in ft for ft in finding_types):
            recommendations.append("Conduct required Data Protection Impact Assessments")
        
        if any('DPO' in ft for ft in finding_types):
            recommendations.append("Evaluate and implement Data Protection Officer appointment")
        
        if any('CROSS_BORDER' in ft for ft in finding_types):
            recommendations.append("Implement appropriate safeguards for international data transfers")
        
        if any('AI_GOVERNANCE' in ft for ft in finding_types):
            recommendations.append("Establish comprehensive AI governance framework")
        
        # General recommendations
        recommendations.extend([
            "Implement continuous compliance monitoring",
            "Provide regular compliance training to all staff",
            "Conduct quarterly compliance assessments",
            "Maintain up-to-date privacy and AI compliance documentation"
        ])
        
        return recommendations[:10]  # Limit to top 10 recommendations