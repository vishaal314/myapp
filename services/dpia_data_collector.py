"""
DPIA Data Collector Service

Specialized service for collecting DPIA assessment data from users,
storing it in memory, and generating comprehensive DPIA reports
with legal compliance analysis for GDPR, Dutch UAVG, and EU AI Act.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import streamlit as st

class DPIADataCollector:
    """
    Handles DPIA data collection, memory storage, and report generation.
    """
    
    def __init__(self):
        self.dpia_data_key = "dpia_collected_data"
        self.dpia_reports_key = "dpia_generated_reports"
        
        # Initialize session state
        if self.dpia_data_key not in st.session_state:
            st.session_state[self.dpia_data_key] = {}
        
        if self.dpia_reports_key not in st.session_state:
            st.session_state[self.dpia_reports_key] = []
    
    def collect_organization_info(self, org_data: Dict[str, Any]) -> str:
        """Collect organization information for DPIA."""
        data_id = str(uuid.uuid4())
        
        collected_data = {
            'id': data_id,
            'section': 'organization_info',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'organization_name': org_data.get('name', ''),
                'dpo_contact': org_data.get('dpo_contact', ''),
                'industry_sector': org_data.get('industry', ''),
                'jurisdiction': org_data.get('jurisdiction', 'Netherlands'),
                'employee_count': org_data.get('employee_count', ''),
                'data_controller': org_data.get('controller', True),
                'data_processor': org_data.get('processor', False)
            },
            'user': st.session_state.get('username', 'anonymous')
        }
        
        st.session_state[self.dpia_data_key][data_id] = collected_data
        return data_id
    
    def collect_processing_description(self, processing_data: Dict[str, Any]) -> str:
        """Collect data processing description."""
        data_id = str(uuid.uuid4())
        
        collected_data = {
            'id': data_id,
            'section': 'processing_description',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'processing_purpose': processing_data.get('purpose', ''),
                'processing_description': processing_data.get('description', ''),
                'data_categories': processing_data.get('data_categories', []),
                'data_subjects': processing_data.get('data_subjects', []),
                'retention_period': processing_data.get('retention', ''),
                'automated_decision_making': processing_data.get('automated_decisions', False),
                'profiling': processing_data.get('profiling', False),
                'ai_system_used': processing_data.get('ai_system', False)
            },
            'user': st.session_state.get('username', 'anonymous')
        }
        
        st.session_state[self.dpia_data_key][data_id] = collected_data
        return data_id
    
    def collect_legal_basis(self, legal_data: Dict[str, Any]) -> str:
        """Collect legal basis information."""
        data_id = str(uuid.uuid4())
        
        collected_data = {
            'id': data_id,
            'section': 'legal_basis',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'legal_basis_gdpr': legal_data.get('gdpr_basis', ''),
                'legitimate_interest_details': legal_data.get('legitimate_interest', ''),
                'consent_mechanism': legal_data.get('consent_mechanism', ''),
                'special_categories': legal_data.get('special_categories', False),
                'criminal_data': legal_data.get('criminal_data', False),
                'children_data': legal_data.get('children_data', False),
                'cross_border_transfer': legal_data.get('cross_border', False),
                'adequacy_decision': legal_data.get('adequacy_decision', '')
            },
            'user': st.session_state.get('username', 'anonymous')
        }
        
        st.session_state[self.dpia_data_key][data_id] = collected_data
        return data_id
    
    def collect_risk_assessment(self, risk_data: Dict[str, Any]) -> str:
        """Collect risk assessment data."""
        data_id = str(uuid.uuid4())
        
        collected_data = {
            'id': data_id,
            'section': 'risk_assessment',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'privacy_risks': risk_data.get('privacy_risks', []),
                'data_breach_likelihood': risk_data.get('breach_likelihood', 'low'),
                'data_breach_impact': risk_data.get('breach_impact', 'low'),
                'discrimination_risk': risk_data.get('discrimination_risk', 'low'),
                'surveillance_concerns': risk_data.get('surveillance', False),
                'vulnerable_groups': risk_data.get('vulnerable_groups', []),
                'rights_impact': risk_data.get('rights_impact', {}),
                'overall_risk_level': self._calculate_overall_risk(risk_data)
            },
            'user': st.session_state.get('username', 'anonymous')
        }
        
        st.session_state[self.dpia_data_key][data_id] = collected_data
        return data_id
    
    def collect_technical_measures(self, tech_data: Dict[str, Any]) -> str:
        """Collect technical and organizational measures."""
        data_id = str(uuid.uuid4())
        
        collected_data = {
            'id': data_id,
            'section': 'technical_measures',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'encryption_at_rest': tech_data.get('encryption_rest', False),
                'encryption_in_transit': tech_data.get('encryption_transit', False),
                'access_controls': tech_data.get('access_controls', []),
                'audit_logging': tech_data.get('audit_logging', False),
                'data_minimization': tech_data.get('data_minimization', False),
                'pseudonymization': tech_data.get('pseudonymization', False),
                'anonymization': tech_data.get('anonymization', False),
                'backup_procedures': tech_data.get('backup_procedures', ''),
                'incident_response': tech_data.get('incident_response', ''),
                'staff_training': tech_data.get('staff_training', False)
            },
            'user': st.session_state.get('username', 'anonymous')
        }
        
        st.session_state[self.dpia_data_key][data_id] = collected_data
        return data_id
    
    def collect_dutch_compliance(self, dutch_data: Dict[str, Any]) -> str:
        """Collect Netherlands-specific compliance data."""
        data_id = str(uuid.uuid4())
        
        collected_data = {
            'id': data_id,
            'section': 'dutch_compliance',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'uavg_compliance': dutch_data.get('uavg_compliant', False),
                'dutch_dpa_notification': dutch_data.get('dpa_notification', False),
                'police_act_applicable': dutch_data.get('police_act', False),
                'police_processing_purpose': dutch_data.get('police_purpose', ''),
                'bsn_processing': dutch_data.get('bsn_processing', False),
                'dutch_sector_codes': dutch_data.get('sector_codes', []),
                'municipal_processing': dutch_data.get('municipal', False),
                'healthcare_bsn': dutch_data.get('healthcare_bsn', False)
            },
            'user': st.session_state.get('username', 'anonymous')
        }
        
        st.session_state[self.dpia_data_key][data_id] = collected_data
        return data_id
    
    def collect_mitigation_measures(self, mitigation_data: Dict[str, Any]) -> str:
        """Collect mitigation measures data."""
        data_id = str(uuid.uuid4())
        
        collected_data = {
            'id': data_id,
            'section': 'mitigation_measures',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'proposed_measures': mitigation_data.get('measures', []),
                'implementation_timeline': mitigation_data.get('timeline', ''),
                'responsible_parties': mitigation_data.get('responsible', []),
                'monitoring_procedures': mitigation_data.get('monitoring', ''),
                'review_schedule': mitigation_data.get('review_schedule', ''),
                'cost_assessment': mitigation_data.get('cost', ''),
                'effectiveness_metrics': mitigation_data.get('metrics', [])
            },
            'user': st.session_state.get('username', 'anonymous')
        }
        
        st.session_state[self.dpia_data_key][data_id] = collected_data
        return data_id
    
    def _calculate_overall_risk(self, risk_data: Dict[str, Any]) -> str:
        """Calculate overall risk level based on individual assessments."""
        risk_scores = {
            'low': 1,
            'medium': 2,
            'high': 3
        }
        
        likelihood = risk_scores.get(risk_data.get('breach_likelihood', 'low'), 1)
        impact = risk_scores.get(risk_data.get('breach_impact', 'low'), 1)
        discrimination = risk_scores.get(risk_data.get('discrimination_risk', 'low'), 1)
        
        # Calculate weighted average
        total_score = (likelihood * 0.4 + impact * 0.4 + discrimination * 0.2)
        
        if total_score >= 2.5:
            return 'high'
        elif total_score >= 1.5:
            return 'medium'
        else:
            return 'low'
    
    def generate_dpia_report(self) -> Dict[str, Any]:
        """Generate comprehensive DPIA report from collected data."""
        report_id = str(uuid.uuid4())
        
        # Aggregate all collected data by section
        sections_data = {}
        for entry in st.session_state[self.dpia_data_key].values():
            section = entry.get('section', 'unknown')
            sections_data[section] = entry.get('data', {})
        
        # Generate compliance analysis
        compliance_analysis = self._analyze_compliance(sections_data)
        
        # Generate risk assessment summary
        risk_summary = self._generate_risk_summary(sections_data)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(sections_data, compliance_analysis)
        
        report_data = {
            'report_id': report_id,
            'generated_at': datetime.now().isoformat(),
            'user': st.session_state.get('username', 'anonymous'),
            'dpia_version': '2.0',
            'jurisdiction': sections_data.get('organization_info', {}).get('jurisdiction', 'Netherlands'),
            
            # Executive Summary
            'executive_summary': {
                'organization': sections_data.get('organization_info', {}).get('organization_name', ''),
                'assessment_date': datetime.now().strftime('%Y-%m-%d'),
                'overall_risk_level': risk_summary.get('overall_risk', 'medium'),
                'dpia_required': risk_summary.get('dpia_required', True),
                'compliance_status': compliance_analysis.get('overall_status', 'non-compliant')
            },
            
            # Detailed Sections
            'organization_info': sections_data.get('organization_info', {}),
            'processing_description': sections_data.get('processing_description', {}),
            'legal_basis': sections_data.get('legal_basis', {}),
            'risk_assessment': sections_data.get('risk_assessment', {}),
            'technical_measures': sections_data.get('technical_measures', {}),
            'dutch_compliance': sections_data.get('dutch_compliance', {}),
            'mitigation_measures': sections_data.get('mitigation_measures', {}),
            
            # Analysis Results
            'compliance_analysis': compliance_analysis,
            'risk_summary': risk_summary,
            'recommendations': recommendations,
            
            # Legal Assessment
            'legal_assessment': {
                'gdpr_compliance_score': compliance_analysis.get('gdpr_score', 0),
                'uavg_compliance_score': compliance_analysis.get('uavg_score', 0),
                'eu_ai_act_score': compliance_analysis.get('ai_act_score', 0),
                'police_act_compliance': compliance_analysis.get('police_act_compliant', False)
            },
            
            # Conclusion
            'conclusion': {
                'can_proceed': compliance_analysis.get('can_proceed', False),
                'additional_measures_required': len(recommendations) > 0,
                'review_required': risk_summary.get('overall_risk') == 'high',
                'dpo_consultation_required': risk_summary.get('dpia_required', True)
            }
        }
        
        # Store the generated report
        st.session_state[self.dpia_reports_key].append(report_data)
        
        return report_data
    
    def _analyze_compliance(self, sections_data: Dict[str, Dict]) -> Dict[str, Any]:
        """Analyze compliance with various regulations."""
        gdpr_score = 0
        uavg_score = 0
        ai_act_score = 0
        
        # GDPR Compliance Analysis
        legal_basis = sections_data.get('legal_basis', {})
        if legal_basis.get('legal_basis_gdpr'):
            gdpr_score += 20
        if legal_basis.get('consent_mechanism') and 'consent' in legal_basis.get('legal_basis_gdpr', ''):
            gdpr_score += 15
        
        tech_measures = sections_data.get('technical_measures', {})
        if tech_measures.get('encryption_at_rest'):
            gdpr_score += 10
        if tech_measures.get('encryption_in_transit'):
            gdpr_score += 10
        if tech_measures.get('data_minimization'):
            gdpr_score += 15
        if tech_measures.get('pseudonymization'):
            gdpr_score += 10
        if tech_measures.get('audit_logging'):
            gdpr_score += 10
        if tech_measures.get('staff_training'):
            gdpr_score += 10
        
        # Dutch UAVG Compliance
        dutch_compliance = sections_data.get('dutch_compliance', {})
        uavg_score = gdpr_score  # UAVG is largely aligned with GDPR
        if dutch_compliance.get('uavg_compliance'):
            uavg_score += 10
        if dutch_compliance.get('dutch_dpa_notification'):
            uavg_score += 5
        
        # EU AI Act Compliance (if AI system is used)
        processing = sections_data.get('processing_description', {})
        if processing.get('ai_system_used'):
            if tech_measures.get('audit_logging'):
                ai_act_score += 25
            if not sections_data.get('risk_assessment', {}).get('discrimination_risk') == 'high':
                ai_act_score += 25
            if tech_measures.get('staff_training'):
                ai_act_score += 20
            if processing.get('automated_decision_making'):
                ai_act_score += 30  # High-risk AI system requirements
        else:
            ai_act_score = 100  # Not applicable
        
        return {
            'gdpr_score': min(gdpr_score, 100),
            'uavg_score': min(uavg_score, 100),
            'ai_act_score': min(ai_act_score, 100),
            'police_act_compliant': dutch_compliance.get('police_act_applicable', False),
            'overall_status': 'compliant' if min(gdpr_score, uavg_score) >= 80 else 'non-compliant',
            'can_proceed': min(gdpr_score, uavg_score) >= 70
        }
    
    def _generate_risk_summary(self, sections_data: Dict[str, Dict]) -> Dict[str, Any]:
        """Generate risk assessment summary."""
        risk_data = sections_data.get('risk_assessment', {})
        processing_data = sections_data.get('processing_description', {})
        
        high_risk_factors = []
        
        # Check for high-risk processing
        if processing_data.get('automated_decision_making'):
            high_risk_factors.append('Automated decision-making')
        if processing_data.get('profiling'):
            high_risk_factors.append('Profiling activities')
        if processing_data.get('ai_system_used'):
            high_risk_factors.append('AI system usage')
        
        # Check data categories
        sensitive_categories = ['health', 'biometric', 'genetic', 'criminal', 'political']
        data_categories = processing_data.get('data_categories', [])
        for category in data_categories:
            if any(sensitive in category.lower() for sensitive in sensitive_categories):
                high_risk_factors.append(f'Sensitive data: {category}')
        
        # Check vulnerable groups
        vulnerable_groups = risk_data.get('vulnerable_groups', [])
        if vulnerable_groups:
            high_risk_factors.append(f'Vulnerable data subjects: {", ".join(vulnerable_groups)}')
        
        overall_risk = risk_data.get('overall_risk_level', 'medium')
        dpia_required = len(high_risk_factors) > 0 or overall_risk in ['high', 'medium']
        
        return {
            'overall_risk': overall_risk,
            'high_risk_factors': high_risk_factors,
            'dpia_required': dpia_required,
            'risk_count': {
                'high': len([f for f in high_risk_factors if 'AI' in f or 'automated' in f]),
                'medium': len([f for f in high_risk_factors if 'Sensitive' in f]),
                'low': len(high_risk_factors) - len([f for f in high_risk_factors if 'AI' in f or 'automated' in f or 'Sensitive' in f])
            }
        }
    
    def _generate_recommendations(self, sections_data: Dict[str, Dict], compliance_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific recommendations based on analysis."""
        recommendations = []
        
        # GDPR recommendations
        if compliance_analysis.get('gdpr_score', 0) < 80:
            tech_measures = sections_data.get('technical_measures', {})
            
            if not tech_measures.get('encryption_at_rest'):
                recommendations.append({
                    'priority': 'high',
                    'category': 'Technical Measures',
                    'recommendation': 'Implement encryption at rest for all personal data storage',
                    'regulation': 'GDPR Article 32'
                })
            
            if not tech_measures.get('data_minimization'):
                recommendations.append({
                    'priority': 'high',
                    'category': 'Data Protection',
                    'recommendation': 'Implement data minimization principles to collect only necessary data',
                    'regulation': 'GDPR Article 5(1)(c)'
                })
        
        # Dutch UAVG recommendations
        dutch_compliance = sections_data.get('dutch_compliance', {})
        if not dutch_compliance.get('uavg_compliance'):
            recommendations.append({
                'priority': 'medium',
                'category': 'Legal Compliance',
                'recommendation': 'Ensure full compliance with Dutch UAVG requirements',
                'regulation': 'Dutch UAVG'
            })
        
        # AI Act recommendations
        processing = sections_data.get('processing_description', {})
        if processing.get('ai_system_used') and compliance_analysis.get('ai_act_score', 0) < 80:
            recommendations.append({
                'priority': 'high',
                'category': 'AI Governance',
                'recommendation': 'Implement EU AI Act compliance measures for high-risk AI systems',
                'regulation': 'EU AI Act'
            })
        
        return recommendations
    
    def get_collected_sections(self) -> List[str]:
        """Get list of completed DPIA sections."""
        sections = set()
        for entry in st.session_state[self.dpia_data_key].values():
            sections.add(entry.get('section', 'unknown'))
        return list(sections)
    
    def is_assessment_complete(self) -> bool:
        """Check if all required DPIA sections are completed."""
        required_sections = [
            'organization_info', 'processing_description', 'legal_basis',
            'risk_assessment', 'technical_measures'
        ]
        completed_sections = self.get_collected_sections()
        return all(section in completed_sections for section in required_sections)
    
    def clear_dpia_data(self) -> None:
        """Clear all collected DPIA data from memory."""
        st.session_state[self.dpia_data_key] = {}
    
    def export_dpia_data(self) -> str:
        """Export collected DPIA data as JSON."""
        return json.dumps(st.session_state[self.dpia_data_key], indent=2, default=str)