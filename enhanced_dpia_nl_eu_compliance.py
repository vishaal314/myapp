"""
Enhanced DPIA Form with Netherlands UAVG and EU AI Act Compliance

This module enhances the existing DPIA form with proper Netherlands-specific
requirements and EU AI Act compliance validation.
"""

import streamlit as st
import time
from datetime import datetime
from typing import Dict, List, Any
from services.dpia_scanner import DPIAScanner
from utils.netherlands_gdpr import detect_nl_violations
from utils.eu_ai_act_compliance import detect_ai_act_violations

# Netherlands-specific DPIA triggers per AP guidance
NL_DPIA_TRIGGERS = {
    'bsn_processing_non_statutory': {
        'name': 'BSN Processing (Non-Statutory)',
        'description': 'Processing BSN outside legal mandate requires DPIA',
        'legal_basis': 'UAVG Article 46'
    },
    'large_scale_biometric': {
        'name': 'Large-Scale Biometric Processing',
        'description': 'Biometric processing affecting >1000 individuals',
        'legal_basis': 'GDPR Article 35(3)(b)'
    },
    'public_area_monitoring': {
        'name': 'Public Area Monitoring',
        'description': 'Systematic monitoring in publicly accessible areas',
        'legal_basis': 'GDPR Article 35(3)(c)'
    },
    'vulnerable_groups': {
        'name': 'Vulnerable Groups Processing',
        'description': 'Processing affecting children, elderly, or disabled persons',
        'legal_basis': 'GDPR Article 35(3)(b)'
    },
    'medical_data_processing': {
        'name': 'Medical Data Processing',
        'description': 'Processing health data outside direct care',
        'legal_basis': 'UAVG Article 30'
    }
}

# EU AI Act risk categories for DPIA integration
AI_ACT_DPIA_REQUIREMENTS = {
    'prohibited_practices': {
        'dpia_required': True,
        'description': 'Prohibited AI practices require immediate cessation',
        'legal_basis': 'EU AI Act Article 5'
    },
    'high_risk_systems': {
        'dpia_required': True,
        'description': 'High-risk AI systems require comprehensive assessment',
        'legal_basis': 'EU AI Act Annex III'
    },
    'foundation_models': {
        'dpia_required': True,
        'description': 'Foundation models require systemic risk assessment',
        'legal_basis': 'EU AI Act Article 51'
    }
}

def run_enhanced_nl_eu_dpia():
    """Run enhanced DPIA with Netherlands and EU AI Act compliance."""
    st.title("🇳🇱 Enhanced DPIA - Netherlands UAVG & EU AI Act Compliance")
    
    # Initialize scanner with Netherlands region
    scanner = DPIAScanner(language=st.session_state.get('language', 'en'))
    
    # Initialize session state
    if 'enhanced_dpia_step' not in st.session_state:
        st.session_state.enhanced_dpia_step = 0
    
    if 'enhanced_dpia_data' not in st.session_state:
        st.session_state.enhanced_dpia_data = {
            'nl_triggers': {},
            'ai_act_assessment': {},
            'fundamental_rights_impact': {},
            'ap_specific_requirements': {}
        }
    
    # Step navigation
    steps = [
        "Pre-Assessment: NL/EU Compliance Check",
        "Step 1: Enhanced Processing Description", 
        "Step 2: Stakeholder Consultation (AP Requirements)",
        "Step 3: Necessity & Proportionality (AI Act)",
        "Step 4: Enhanced Risk Assessment (NL + AI Act)",
        "Step 5: Enhanced Mitigation Measures",
        "Step 6: AP-Compliant Sign-off",
        "Step 7: Integration & Monitoring"
    ]
    
    # Progress indicator
    st.progress((st.session_state.enhanced_dpia_step + 1) / len(steps))
    st.caption(f"Step {st.session_state.enhanced_dpia_step + 1} of {len(steps)}: {steps[st.session_state.enhanced_dpia_step]}")
    
    # Route to appropriate step
    if st.session_state.enhanced_dpia_step == 0:
        handle_pre_assessment()
    elif st.session_state.enhanced_dpia_step == 1:
        handle_enhanced_step1()
    elif st.session_state.enhanced_dpia_step == 2:
        handle_enhanced_step2()
    elif st.session_state.enhanced_dpia_step == 3:
        handle_enhanced_step3()
    elif st.session_state.enhanced_dpia_step == 4:
        handle_enhanced_step4()
    elif st.session_state.enhanced_dpia_step == 5:
        handle_enhanced_step5()
    elif st.session_state.enhanced_dpia_step == 6:
        handle_enhanced_step6()
    elif st.session_state.enhanced_dpia_step == 7:
        handle_enhanced_step7()

def handle_pre_assessment():
    """Pre-assessment to determine NL and EU AI Act requirements."""
    form_key = f"pre_assessment_{int(time.time() * 1000)}"
    
    with st.form(form_key):
        st.markdown("""
        ### Pre-Assessment: Netherlands & EU AI Act Compliance Check
        
        This preliminary assessment determines which specific requirements apply to your processing activities.
        """)
        
        st.markdown("#### Netherlands DPIA Triggers")
        st.info("Select all that apply to your processing activities:")
        
        # Netherlands-specific triggers
        for trigger_id, trigger_info in NL_DPIA_TRIGGERS.items():
            checked = st.checkbox(
                f"**{trigger_info['name']}**: {trigger_info['description']}",
                key=f"nl_trigger_{trigger_id}",
                value=st.session_state.enhanced_dpia_data['nl_triggers'].get(trigger_id, False)
            )
            st.session_state.enhanced_dpia_data['nl_triggers'][trigger_id] = checked
            if checked:
                st.caption(f"Legal basis: {trigger_info['legal_basis']}")
        
        st.markdown("#### EU AI Act Assessment")
        
        # AI system involvement
        ai_system_involved = st.selectbox(
            "Does your processing involve AI systems?",
            options=["No", "Yes - Limited risk", "Yes - High risk", "Yes - Prohibited practices"],
            index=0
        )
        
        if ai_system_involved != "No":
            st.markdown("##### AI System Details")
            
            ai_system_type = st.multiselect(
                "Select AI system types involved:",
                options=[
                    "Biometric identification",
                    "Employment/HR decisions", 
                    "Educational assessment",
                    "Credit scoring/financial",
                    "Healthcare diagnosis",
                    "Law enforcement",
                    "Content moderation",
                    "Recommendation systems",
                    "Automated decision-making"
                ]
            )
            
            high_risk_indicators = st.multiselect(
                "High-risk indicators present:",
                options=[
                    "Affects fundamental rights",
                    "Large-scale processing",
                    "Vulnerable populations",
                    "Public safety impact",
                    "Automated decision-making",
                    "Profiling with legal effects"
                ]
            )
            
            st.session_state.enhanced_dpia_data['ai_act_assessment'] = {
                'involvement_level': ai_system_involved,
                'system_types': ai_system_type,
                'high_risk_indicators': high_risk_indicators
            }
        
        # Continue button
        if st.form_submit_button("Continue to Enhanced DPIA", type="primary"):
            # Determine required assessments
            nl_triggers_active = any(st.session_state.enhanced_dpia_data['nl_triggers'].values())
            ai_act_relevant = ai_system_involved != "No"
            
            if nl_triggers_active or ai_act_relevant:
                st.session_state.enhanced_dpia_step = 1
                st.rerun()
            else:
                st.warning("Based on your responses, an enhanced DPIA may not be required. However, you can continue with a standard assessment.")
                if st.button("Continue anyway"):
                    st.session_state.enhanced_dpia_step = 1
                    st.rerun()

def handle_enhanced_step4():
    """Enhanced Step 4: Risk Assessment with NL and AI Act integration."""
    form_key = f"enhanced_step4_{int(time.time() * 1000)}"
    
    with st.form(form_key):
        st.markdown("""
        ### Enhanced Step 4: Risk Assessment
        
        This enhanced risk assessment incorporates:
        - Netherlands UAVG specific requirements
        - EU AI Act compliance checks
        - Fundamental rights impact assessment
        """)
        
        # Netherlands-specific risk assessment
        st.markdown("#### Netherlands UAVG Risk Factors")
        
        nl_risks = {
            'bsn_misuse': st.selectbox(
                "Risk of BSN misuse or unauthorized processing:",
                options=["Low", "Medium", "High", "Critical"],
                help="Consider potential for identity fraud or discrimination"
            ),
            'ap_enforcement': st.selectbox(
                "Risk of AP enforcement action:",
                options=["Low", "Medium", "High", "Critical"], 
                help="Based on AP guidance and precedent"
            ),
            'minor_consent': st.selectbox(
                "Risk regarding processing of minors' data (<16 years):",
                options=["Low", "Medium", "High", "Critical"],
                help="Consider consent validity and parental involvement"
            ),
            'medical_data_breach': st.selectbox(
                "Risk of medical data breach or misuse:",
                options=["Low", "Medium", "High", "Critical"],
                help="Consider EPD regulations and patient confidentiality"
            )
        }
        
        # EU AI Act risk assessment
        ai_involvement = st.session_state.enhanced_dpia_data.get('ai_act_assessment', {}).get('involvement_level', 'No')
        
        if ai_involvement != "No":
            st.markdown("#### EU AI Act Risk Assessment")
            
            ai_risks = {
                'prohibited_practices': st.selectbox(
                    "Risk of prohibited AI practices:",
                    options=["None", "Low", "Medium", "High", "Critical"],
                    help="Subliminal techniques, social scoring, mass surveillance"
                ),
                'algorithmic_bias': st.selectbox(
                    "Risk of algorithmic bias or discrimination:",
                    options=["Low", "Medium", "High", "Critical"],
                    help="Consider fairness, accuracy, and representativeness"
                ),
                'transparency_failure': st.selectbox(
                    "Risk of transparency/explainability failure:",
                    options=["Low", "Medium", "High", "Critical"],
                    help="User understanding and decision transparency"
                ),
                'human_oversight_failure': st.selectbox(
                    "Risk of inadequate human oversight:",
                    options=["Low", "Medium", "High", "Critical"],
                    help="Human intervention and control mechanisms"
                ),
                'fundamental_rights_impact': st.selectbox(
                    "Risk to fundamental rights:",
                    options=["Low", "Medium", "High", "Critical"],
                    help="Privacy, dignity, non-discrimination, freedom of expression"
                )
            }
        else:
            ai_risks = {}
        
        # Fundamental Rights Impact Assessment (FRIA)
        st.markdown("#### Fundamental Rights Impact Assessment")
        
        fria_assessment = {
            'privacy_rights': st.selectbox(
                "Impact on privacy and data protection rights:",
                options=["Minimal", "Limited", "Significant", "Severe"]
            ),
            'non_discrimination': st.selectbox(
                "Impact on non-discrimination and equality:",
                options=["Minimal", "Limited", "Significant", "Severe"]
            ),
            'freedom_expression': st.selectbox(
                "Impact on freedom of expression and information:",
                options=["Minimal", "Limited", "Significant", "Severe"] 
            ),
            'due_process': st.selectbox(
                "Impact on right to fair trial and due process:",
                options=["Minimal", "Limited", "Significant", "Severe"]
            )
        }
        
        # Additional risk factors
        st.markdown("#### Additional Risk Considerations")
        
        additional_risks = st.text_area(
            "Describe any additional risks not covered above:",
            help="Include context-specific risks, cumulative effects, or novel risks"
        )
        
        # Risk mitigation urgency
        mitigation_urgency = st.selectbox(
            "Overall risk mitigation urgency:",
            options=["Low - Monitor", "Medium - Plan mitigation", "High - Immediate action", "Critical - Stop processing"]
        )
        
        # Navigation
        col1, col2 = st.columns(2)
        with col1:
            back = st.form_submit_button("Back to Step 3", use_container_width=True)
        with col2:
            next_step = st.form_submit_button("Continue to Mitigation", type="primary", use_container_width=True)
    
    if back:
        st.session_state.enhanced_dpia_step = 3
        st.rerun()
    
    if next_step:
        # Store risk assessment results
        st.session_state.enhanced_dpia_data['risk_assessment'] = {
            'nl_risks': nl_risks,
            'ai_risks': ai_risks,
            'fria_assessment': fria_assessment,
            'additional_risks': additional_risks,
            'mitigation_urgency': mitigation_urgency
        }
        
        st.session_state.enhanced_dpia_step = 5
        st.rerun()

def handle_enhanced_step5():
    """Enhanced Step 5: Mitigation measures with NL and AI Act requirements."""
    form_key = f"enhanced_step5_{int(time.time() * 1000)}"
    
    with st.form(form_key):
        st.markdown("""
        ### Enhanced Step 5: Mitigation Measures
        
        Based on the risk assessment, implement specific mitigation measures for:
        - Netherlands UAVG compliance
        - EU AI Act requirements
        - Fundamental rights protection
        """)
        
        # Netherlands-specific mitigations
        st.markdown("#### Netherlands UAVG Mitigation Measures")
        
        nl_mitigations = {
            'bsn_safeguards': st.text_area(
                "BSN processing safeguards:",
                help="Describe specific measures for BSN protection and access control"
            ),
            'ap_compliance': st.text_area(
                "AP compliance measures:",
                help="Procedures for AP communication, reporting, and compliance demonstration"
            ),
            'minor_protection': st.text_area(
                "Minor protection measures:",
                help="Age verification, parental consent mechanisms, and special safeguards"
            ),
            'medical_data_security': st.text_area(
                "Medical data security measures:",
                help="Enhanced security for health data, access logging, and breach prevention"
            )
        }
        
        # AI Act mitigation measures
        ai_involvement = st.session_state.enhanced_dpia_data.get('ai_act_assessment', {}).get('involvement_level', 'No')
        
        if ai_involvement != "No":
            st.markdown("#### EU AI Act Mitigation Measures")
            
            ai_mitigations = {
                'ai_governance': st.text_area(
                    "AI governance framework:",
                    help="Risk management system, quality management, and organizational measures"
                ),
                'human_oversight': st.text_area(
                    "Human oversight measures:",
                    help="Human intervention points, review mechanisms, and override capabilities"
                ),
                'transparency_measures': st.text_area(
                    "Transparency and explainability measures:",
                    help="User disclosure, decision explanation, and audit trail mechanisms"
                ),
                'bias_mitigation': st.text_area(
                    "Bias prevention and mitigation:",
                    help="Data quality measures, testing procedures, and fairness monitoring"
                ),
                'fundamental_rights_safeguards': st.text_area(
                    "Fundamental rights safeguards:",
                    help="Specific measures to protect fundamental rights and freedoms"
                )
            }
        else:
            ai_mitigations = {}
        
        # Implementation timeline
        st.markdown("#### Implementation Timeline")
        
        implementation_plan = {
            'immediate_actions': st.text_area(
                "Immediate actions (0-30 days):",
                help="Critical measures that must be implemented immediately"
            ),
            'short_term': st.text_area(
                "Short-term measures (1-6 months):",
                help="Important measures requiring planning and resources"
            ),
            'long_term': st.text_area(
                "Long-term measures (6+ months):",
                help="Strategic improvements and ongoing enhancements"
            )
        }
        
        # Monitoring and review
        st.markdown("#### Monitoring and Review")
        
        monitoring_plan = {
            'review_frequency': st.selectbox(
                "Review frequency:",
                options=["Monthly", "Quarterly", "Semi-annually", "Annually"]
            ),
            'kpis': st.text_area(
                "Key performance indicators:",
                help="Metrics to track effectiveness of mitigation measures"
            ),
            'escalation_procedures': st.text_area(
                "Escalation procedures:",
                help="When and how to escalate issues or update measures"
            )
        }
        
        # Navigation
        col1, col2 = st.columns(2)
        with col1:
            back = st.form_submit_button("Back to Risk Assessment", use_container_width=True)
        with col2:
            next_step = st.form_submit_button("Continue to Sign-off", type="primary", use_container_width=True)
    
    if back:
        st.session_state.enhanced_dpia_step = 4
        st.rerun()
    
    if next_step:
        # Store mitigation measures
        st.session_state.enhanced_dpia_data['mitigation_measures'] = {
            'nl_mitigations': nl_mitigations,
            'ai_mitigations': ai_mitigations,
            'implementation_plan': implementation_plan,
            'monitoring_plan': monitoring_plan
        }
        
        st.session_state.enhanced_dpia_step = 6
        st.rerun()

# Simplified placeholder implementations for other steps
def handle_enhanced_step1():
    """Enhanced Step 1 placeholder."""
    st.write("Enhanced Step 1: Processing Description")
    if st.button("Continue"):
        st.session_state.enhanced_dpia_step = 2
        st.rerun()

def handle_enhanced_step2():
    """Enhanced Step 2 placeholder.""" 
    st.write("Enhanced Step 2: Stakeholder Consultation")
    if st.button("Continue"):
        st.session_state.enhanced_dpia_step = 3
        st.rerun()

def handle_enhanced_step3():
    """Enhanced Step 3 placeholder."""
    st.write("Enhanced Step 3: Necessity & Proportionality")
    if st.button("Continue"):
        st.session_state.enhanced_dpia_step = 4
        st.rerun()

def handle_enhanced_step6():
    """Enhanced Step 6 placeholder."""
    st.write("Enhanced Step 6: AP-Compliant Sign-off")
    if st.button("Continue"):
        st.session_state.enhanced_dpia_step = 7
        st.rerun()

def handle_enhanced_step7():
    """Enhanced Step 7 placeholder."""
    st.write("Enhanced Step 7: Integration & Monitoring")
    if st.button("Complete DPIA"):
        st.success("Enhanced DPIA completed with Netherlands and EU AI Act compliance!")

if __name__ == "__main__":
    run_enhanced_nl_eu_dpia()