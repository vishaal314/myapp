"""
Comprehensive DPIA Assessment Tool

This module implements a complete Data Protection Impact Assessment tool
that collects user data and analyzes it according to:
- GDPR (General Data Protection Regulation)
- Dutch Police Act (Politiewet)
- Netherlands jurisdiction requirements
- UAVG (Dutch GDPR implementation)

Outputs professional HTML reports with legal compliance analysis.
"""

import streamlit as st
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import uuid
import base64

@dataclass
class DPIAAssessment:
    """Data structure for DPIA assessment data."""
    assessment_id: str
    created_date: datetime
    organization: Dict[str, str]
    processing_description: Dict[str, Any]
    legal_basis: Dict[str, Any]
    data_categories: Dict[str, Any]
    data_subjects: Dict[str, Any]
    data_sharing: Dict[str, Any]
    technical_measures: Dict[str, Any]
    organizational_measures: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    dutch_specific: Dict[str, Any]
    police_act_compliance: Dict[str, Any]
    mitigation_measures: List[Dict[str, Any]]
    overall_risk_level: str
    compliance_status: str

def run_comprehensive_dpia_assessment():
    """Main function to run the comprehensive DPIA assessment."""
    st.title("Data Protection Impact Assessment")
    st.subheader("GDPR • Dutch Police Act • Netherlands Jurisdiction Compliance")
    
    # Check if we should show results instead
    if st.session_state.get('dpia_show_results', False):
        if 'dpia_results' in st.session_state:
            display_assessment_results(
                st.session_state.dpia_results,
                st.session_state.dpia_report_data
            )
            return
    
    # Initialize session state for 7-step GDPR DPIA
    if 'gdpr_dpia_step' not in st.session_state:
        st.session_state.gdpr_dpia_step = 1
    
    if 'gdpr_dpia_answers' not in st.session_state:
        st.session_state.gdpr_dpia_answers = {
            'step1': {},
            'step2': {},
            'step3': {},
            'step4': {},
            'step5': {},
            'step6': {},
            'step7': {}
        }
    
    # Progress indicator for 7 steps
    progress_value = (st.session_state.gdpr_dpia_step - 1) / 7
    st.progress(progress_value)
    st.markdown(f"**Step {st.session_state.gdpr_dpia_step} of 7:** {get_step_title(st.session_state.gdpr_dpia_step)}")
    
    # Navigation based on current step
    if st.session_state.gdpr_dpia_step == 1:
        handle_step1_processing()
    elif st.session_state.gdpr_dpia_step == 2:
        handle_step2_consultation()
    elif st.session_state.gdpr_dpia_step == 3:
        handle_step3_necessity()
    elif st.session_state.gdpr_dpia_step == 4:
        handle_step4_risks()
    elif st.session_state.gdpr_dpia_step == 5:
        handle_step5_mitigation()
    elif st.session_state.gdpr_dpia_step == 6:
        handle_step6_signoff()
    elif st.session_state.gdpr_dpia_step == 7:
        handle_step7_integration()

def initialize_dpia_data() -> Dict[str, Any]:
    """Initialize empty DPIA assessment data structure."""
    return {
        'assessment_id': str(uuid.uuid4()),
        'created_date': datetime.now().isoformat(),
        'organization': {},
        'processing_description': {},
        'legal_basis': {},
        'data_categories': {},
        'data_subjects': {},
        'data_sharing': {},
        'technical_measures': {},
        'organizational_measures': {},
        'risk_assessment': {},
        'dutch_specific': {},
        'police_act_compliance': {},
        'mitigation_measures': [],
        'overall_risk_level': '',
        'compliance_status': ''
    }

def handle_organization_info():
    """Handle organization information collection."""
    st.markdown("### Organization Information")
    st.markdown("Please provide details about your organization and the assessment scope.")
    
    form_key = f"org_info_{int(time.time() * 1000)}"
    with st.form(form_key):
        col1, col2 = st.columns(2)
        
        with col1:
            org_name = st.text_input(
                "Organization Name *",
                value=st.session_state.dpia_assessment_data['organization'].get('name', ''),
                help="Full legal name of the organization"
            )
            
            org_type = st.selectbox(
                "Organization Type *",
                options=[
                    "Private Company",
                    "Public Authority", 
                    "Healthcare Institution",
                    "Educational Institution",
                    "Law Enforcement",
                    "Financial Institution",
                    "NGO/Non-Profit",
                    "Other"
                ],
                index=0
            )
            
            dpo_present = st.selectbox(
                "Do you have a Data Protection Officer (DPO)? *",
                options=["Yes", "No", "Required but not appointed"],
                help="DPO required for public authorities and certain processing activities"
            )
            
        with col2:
            contact_person = st.text_input(
                "Contact Person *",
                value=st.session_state.dpia_assessment_data['organization'].get('contact_person', ''),
                help="Person responsible for this DPIA"
            )
            
            contact_email = st.text_input(
                "Contact Email *",
                value=st.session_state.dpia_assessment_data['organization'].get('contact_email', ''),
                help="Email for DPIA correspondence"
            )
            
            jurisdiction = st.selectbox(
                "Primary Jurisdiction *",
                options=[
                    "Netherlands",
                    "Netherlands + EU Member States",
                    "Netherlands + Third Countries",
                    "Other EU Member State",
                    "Third Country"
                ],
                help="Primary legal jurisdiction for data processing"
            )
        
        assessment_purpose = st.text_area(
            "Assessment Purpose *",
            value=st.session_state.dpia_assessment_data['organization'].get('assessment_purpose', ''),
            help="Describe why this DPIA is being conducted",
            height=100
        )
        
        assessment_scope = st.text_area(
            "Assessment Scope *",
            value=st.session_state.dpia_assessment_data['organization'].get('assessment_scope', ''),
            help="Define what processing activities are covered by this assessment",
            height=100
        )
        
        submitted = st.form_submit_button("Continue to Processing Description", type="primary")
        
        if submitted:
            if not all([org_name, contact_person, contact_email, assessment_purpose, assessment_scope]):
                st.error("Please fill in all required fields marked with *")
                return
            
            # Store organization data
            st.session_state.dpia_assessment_data['organization'] = {
                'name': org_name,
                'type': org_type,
                'dpo_present': dpo_present,
                'contact_person': contact_person,
                'contact_email': contact_email,
                'jurisdiction': jurisdiction,
                'assessment_purpose': assessment_purpose,
                'assessment_scope': assessment_scope
            }
            
            st.session_state.dpia_current_section = 1
            st.rerun()

def handle_step2_consultation():
    """Step 2: Consider consultation with stakeholders."""
    st.markdown("### Step 2: Consider consultation")
    st.markdown("This step covers consultation with stakeholders, including data subjects and DPO.")
    
    form_key = f"step2_{int(time.time() * 1000)}"
    with st.form(form_key):
        st.markdown("#### Consultation with Data Subjects")
        
        consultation_needed = st.radio(
            "Is consultation with data subjects needed or practical?",
            options=["Yes", "No", "Unsure"],
            index=["Yes", "No", "Unsure"].index(st.session_state.gdpr_dpia_answers['step2'].get('consultation_needed', "Unsure"))
        )
        
        consultation_method = st.text_area(
            "If yes, how will you seek the views of data subjects?",
            value=st.session_state.gdpr_dpia_answers['step2'].get('consultation_method', ''),
            help="Describe your approach to consultation (e.g., surveys, focus groups)"
        )
        
        st.markdown("#### Data Protection Officer")
        
        dpo_consultation = st.radio(
            "Have you consulted your Data Protection Officer (DPO)?",
            options=["Yes", "No", "Not applicable"],
            index=["Yes", "No", "Not applicable"].index(st.session_state.gdpr_dpia_answers['step2'].get('dpo_consultation', "No"))
        )
        
        dpo_advice = st.text_area(
            "If yes, what advice did your DPO provide?",
            value=st.session_state.gdpr_dpia_answers['step2'].get('dpo_advice', '')
        )
        
        other_consultations = st.multiselect(
            "Have you consulted any other stakeholders?",
            options=[
                "IT security team",
                "Legal department", 
                "Compliance officer",
                "External privacy consultant",
                "Supervisory authority",
                "Processor or service provider",
                "Other departments in your organization",
                "Industry association",
                "None of the above"
            ],
            default=st.session_state.gdpr_dpia_answers['step2'].get('other_consultations', [])
        )
        
        consultation_outcomes = st.text_area(
            "Summarize the key outcomes from consultations:",
            value=st.session_state.gdpr_dpia_answers['step2'].get('consultation_outcomes', '')
        )
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            back = st.form_submit_button("Back to Step 1")
        with col2:
            next_step = st.form_submit_button("Continue to Step 3", type="primary")
    
    if back:
        st.session_state.gdpr_dpia_step = 1
        st.rerun()
    
    if next_step:
        # Store answers
        st.session_state.gdpr_dpia_answers['step2'] = {
            'consultation_needed': consultation_needed,
            'consultation_method': consultation_method,
            'dpo_consultation': dpo_consultation,
            'dpo_advice': dpo_advice,
            'other_consultations': other_consultations,
            'consultation_outcomes': consultation_outcomes
        }
        
        # Move to next step
        st.session_state.gdpr_dpia_step = 3
        st.rerun()

def handle_step3_necessity():
    """Step 3: Assess necessity and proportionality."""
    st.markdown("### Step 3: Assess necessity and proportionality") 
    st.markdown("Evaluate whether the processing is necessary and proportionate.")
    
    form_key = f"step3_{int(time.time() * 1000)}"
    with st.form(form_key):
        legal_basis = st.selectbox(
            "What is the legal basis for processing?",
            options=[
                "Consent",
                "Contract",
                "Legal obligation", 
                "Vital interests",
                "Public task",
                "Legitimate interests"
            ],
            index=["Consent", "Contract", "Legal obligation", "Vital interests", "Public task", "Legitimate interests"].index(
                st.session_state.gdpr_dpia_answers['step3'].get('legal_basis', "Consent")
            )
        )
        
        necessity_justification = st.text_area(
            "Justify why the processing is necessary:",
            value=st.session_state.gdpr_dpia_answers['step3'].get('necessity_justification', ''),
            help="Explain why you cannot achieve your purpose without processing personal data"
        )
        
        proportionality_assessment = st.text_area(
            "Assess proportionality - is the processing proportionate to the aim?",
            value=st.session_state.gdpr_dpia_answers['step3'].get('proportionality_assessment', ''),
            help="Consider whether less intrusive methods could achieve the same result"
        )
        
        data_minimization = st.radio(
            "Have you applied data minimization principles?",
            options=["Yes, fully applied", "Partially applied", "Not yet applied", "Not applicable"],
            index=["Yes, fully applied", "Partially applied", "Not yet applied", "Not applicable"].index(
                st.session_state.gdpr_dpia_answers['step3'].get('data_minimization', "Not yet applied")
            )
        )
        
        retention_period = st.text_input(
            "Data retention period:",
            value=st.session_state.gdpr_dpia_answers['step3'].get('retention_period', ''),
            help="How long will personal data be kept?"
        )
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            back = st.form_submit_button("Back to Step 2")
        with col2:
            next_step = st.form_submit_button("Continue to Step 4", type="primary")
    
    if back:
        st.session_state.gdpr_dpia_step = 2
        st.rerun()
    
    if next_step:
        # Store answers
        st.session_state.gdpr_dpia_answers['step3'] = {
            'legal_basis': legal_basis,
            'necessity_justification': necessity_justification,
            'proportionality_assessment': proportionality_assessment,
            'data_minimization': data_minimization,
            'retention_period': retention_period
        }
        
        # Move to next step
        st.session_state.gdpr_dpia_step = 4
        st.rerun()

def handle_step4_risks():
    """Step 4: Identify and assess risks."""
    st.markdown("### Step 4: Identify and assess risks")
    st.markdown("Identify privacy risks and assess their likelihood and impact.")
    
    form_key = f"step4_{int(time.time() * 1000)}"
    with st.form(form_key):
        identified_risks = st.text_area(
            "What privacy risks have you identified?",
            value=st.session_state.gdpr_dpia_answers['step4'].get('identified_risks', ''),
            help="List specific risks to individuals' rights and freedoms",
            height=150
        )
        
        risk_sources = st.multiselect(
            "What are the sources of risk?",
            options=[
                "Data collection methods",
                "Data storage and security",
                "Data processing activities", 
                "Data sharing and transfers",
                "Third party processors",
                "New technology or algorithms",
                "Profiling or automated decision-making",
                "Large scale processing",
                "Vulnerable data subjects",
                "Other"
            ],
            default=st.session_state.gdpr_dpia_answers['step4'].get('risk_sources', [])
        )
        
        likelihood_assessment = st.radio(
            "Overall likelihood of risks occurring:",
            options=["Low", "Medium", "High"],
            index=["Low", "Medium", "High"].index(
                st.session_state.gdpr_dpia_answers['step4'].get('likelihood_assessment', "Medium")
            )
        )
        
        impact_assessment = st.radio(
            "Potential impact on individuals if risks occur:",
            options=["Low", "Medium", "High"],
            index=["Low", "Medium", "High"].index(
                st.session_state.gdpr_dpia_answers['step4'].get('impact_assessment', "Medium")
            )
        )
        
        overall_risk_level = st.radio(
            "Overall risk level:",
            options=["Low", "Medium", "High"],
            index=["Low", "Medium", "High"].index(
                st.session_state.gdpr_dpia_answers['step4'].get('overall_risk_level', "Medium")
            )
        )
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            back = st.form_submit_button("Back to Step 3")
        with col2:
            next_step = st.form_submit_button("Continue to Step 5", type="primary")
    
    if back:
        st.session_state.gdpr_dpia_step = 3
        st.rerun()
    
    if next_step:
        # Store answers
        st.session_state.gdpr_dpia_answers['step4'] = {
            'identified_risks': identified_risks,
            'risk_sources': risk_sources,
            'likelihood_assessment': likelihood_assessment,
            'impact_assessment': impact_assessment,
            'overall_risk_level': overall_risk_level
        }
        
        # Move to next step
        st.session_state.gdpr_dpia_step = 5
        st.rerun()

def handle_step5_mitigation():
    """Step 5: Identify measures to mitigate risk."""
    st.markdown("### Step 5: Identify measures to mitigate risk")
    st.markdown("Specify measures to reduce the identified risks.")
    
    form_key = f"step5_{int(time.time() * 1000)}"
    with st.form(form_key):
        technical_measures = st.text_area(
            "Technical measures to reduce risks:",
            value=st.session_state.gdpr_dpia_answers['step5'].get('technical_measures', ''),
            help="e.g., encryption, access controls, anonymization",
            height=120
        )
        
        organizational_measures = st.text_area(
            "Organizational measures to reduce risks:",
            value=st.session_state.gdpr_dpia_answers['step5'].get('organizational_measures', ''),
            help="e.g., policies, training, governance procedures",
            height=120
        )
        
        additional_safeguards = st.text_area(
            "Additional safeguards or controls:",
            value=st.session_state.gdpr_dpia_answers['step5'].get('additional_safeguards', ''),
            help="Any other measures to protect individuals",
            height=100
        )
        
        residual_risk = st.radio(
            "Residual risk level after implementing measures:",
            options=["Low", "Medium", "High"],
            index=["Low", "Medium", "High"].index(
                st.session_state.gdpr_dpia_answers['step5'].get('residual_risk', "Low")
            )
        )
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            back = st.form_submit_button("Back to Step 4")
        with col2:
            next_step = st.form_submit_button("Continue to Step 6", type="primary")
    
    if back:
        st.session_state.gdpr_dpia_step = 4
        st.rerun()
    
    if next_step:
        # Store answers
        st.session_state.gdpr_dpia_answers['step5'] = {
            'technical_measures': technical_measures,
            'organizational_measures': organizational_measures,
            'additional_safeguards': additional_safeguards,
            'residual_risk': residual_risk
        }
        
        # Move to next step
        st.session_state.gdpr_dpia_step = 6
        st.rerun()

def handle_step6_signoff():
    """Step 6: Sign off and record outcomes."""
    st.markdown("### Step 6: Sign off and record outcomes")
    st.markdown("Document the decision and outcome of the DPIA.")
    
    form_key = f"step6_{int(time.time() * 1000)}"
    with st.form(form_key):
        decision = st.radio(
            "What is your decision about proceeding with the processing?",
            options=[
                "Proceed - Risks have been eliminated",
                "Proceed - Risks have been reduced to acceptable level", 
                "Proceed - Benefits outweigh risks",
                "Proceed - Only with prior consultation with supervisory authority",
                "Do not proceed - Risks remain unacceptably high"
            ],
            index=["Proceed - Risks have been eliminated", 
                   "Proceed - Risks have been reduced to acceptable level", 
                   "Proceed - Benefits outweigh risks",
                   "Proceed - Only with prior consultation with supervisory authority",
                   "Do not proceed - Risks remain unacceptably high"].index(
                st.session_state.gdpr_dpia_answers['step6'].get('decision', "Proceed - Risks have been reduced to acceptable level")
            )
        )
        
        decision_rationale = st.text_area(
            "Decision rationale:",
            value=st.session_state.gdpr_dpia_answers['step6'].get('decision_rationale', ''),
            help="Explain the reasoning behind this decision"
        )
        
        approver_name = st.text_input(
            "Approver name:",
            value=st.session_state.gdpr_dpia_answers['step6'].get('approver_name', ''),
            help="Name of the person approving this DPIA"
        )
        
        approver_role = st.text_input(
            "Approver role:",
            value=st.session_state.gdpr_dpia_answers['step6'].get('approver_role', ''),
            help="Role/title of the approver"
        )
        
        approval_date = st.date_input(
            "Approval date:",
            value=datetime.now().date()
        )
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            back = st.form_submit_button("Back to Step 5")
        with col2:
            next_step = st.form_submit_button("Continue to Step 7", type="primary")
    
    if back:
        st.session_state.gdpr_dpia_step = 5
        st.rerun()
    
    if next_step:
        # Store answers
        st.session_state.gdpr_dpia_answers['step6'] = {
            'decision': decision,
            'decision_rationale': decision_rationale,
            'approver_name': approver_name,
            'approver_role': approver_role,
            'approval_date': approval_date.isoformat()
        }
        
        # Move to next step
        st.session_state.gdpr_dpia_step = 7
        st.rerun()

def handle_step7_integration():
    """Step 7: Integrate outcomes into plan."""
    st.markdown("### Step 7: Integrate outcomes into plan")
    st.markdown("Plan how to implement the identified measures and complete the DPIA.")
    
    form_key = f"step7_{int(time.time() * 1000)}"
    with st.form(form_key):
        implementation_plan = st.text_area(
            "Implementation plan for identified measures:",
            value=st.session_state.gdpr_dpia_answers['step7'].get('implementation_plan', ''),
            help="How will you implement the risk mitigation measures?",
            height=150
        )
        
        timeline = st.text_input(
            "Timeline for implementation:",
            value=st.session_state.gdpr_dpia_answers['step7'].get('timeline', ''),
            help="Provide target dates for implementing measures"
        )
        
        responsibility = st.text_input(
            "Who is responsible for implementation?",
            value=st.session_state.gdpr_dpia_answers['step7'].get('responsibility', ''),
            help="Name and role of responsible person/team"
        )
        
        review_schedule = st.radio(
            "How often will this DPIA be reviewed?",
            options=[
                "Quarterly",
                "Semi-annually", 
                "Annually",
                "When significant changes occur",
                "Other"
            ],
            index=["Quarterly", "Semi-annually", "Annually", "When significant changes occur", "Other"].index(
                st.session_state.gdpr_dpia_answers['step7'].get('review_schedule', "Annually")
            )
        )
        
        monitoring_process = st.text_area(
            "How will you monitor the effectiveness of measures?",
            value=st.session_state.gdpr_dpia_answers['step7'].get('monitoring_process', ''),
            help="Describe ongoing monitoring and review processes"
        )
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            back = st.form_submit_button("Back to Step 6")
        with col2:
            complete = st.form_submit_button("Complete DPIA Assessment", type="primary")
    
    if back:
        st.session_state.gdpr_dpia_step = 6
        st.rerun()
    
    if complete:
        # Store answers
        st.session_state.gdpr_dpia_answers['step7'] = {
            'implementation_plan': implementation_plan,
            'timeline': timeline,
            'responsibility': responsibility,
            'review_schedule': review_schedule,
            'monitoring_process': monitoring_process
        }
        
        # Process the completed assessment
        process_dpia_assessment()
        st.rerun()

def process_dpia_assessment():
    """Process the completed DPIA assessment and generate results."""
    try:
        # Create assessment results from collected answers
        assessment_results = {
            'assessment_id': str(uuid.uuid4()),
            'created_date': datetime.now().isoformat(),
            'overall_risk_level': st.session_state.gdpr_dpia_answers['step4'].get('overall_risk_level', 'Medium'),
            'decision': st.session_state.gdpr_dpia_answers['step6'].get('decision', 'Proceed'),
            'project_name': st.session_state.gdpr_dpia_answers['step1'].get('project_name', 'Unnamed Project'),
            'findings': generate_findings_from_answers(),
            'recommendations': generate_recommendations_from_answers(),
            'compliance_status': 'Compliant' if st.session_state.gdpr_dpia_answers['step5'].get('residual_risk', 'Medium') == 'Low' else 'Action Required'
        }
        
        # Generate report data
        report_data = {
            'title': f"DPIA Report - {assessment_results['project_name']}",
            'generated_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'assessment_data': st.session_state.gdpr_dpia_answers,
            'summary': assessment_results
        }
        
        # Store results in session state
        st.session_state.dpia_results = assessment_results
        st.session_state.dpia_report_data = report_data
        st.session_state.dpia_show_results = True
        
        st.success("DPIA assessment completed successfully!")
        
    except Exception as e:
        st.error(f"Error processing DPIA assessment: {str(e)}")

def generate_findings_from_answers():
    """Generate findings summary from user answers."""
    findings = []
    
    # Risk level findings
    risk_level = st.session_state.gdpr_dpia_answers['step4'].get('overall_risk_level', 'Medium')
    findings.append({
        'category': 'Risk Assessment',
        'finding': f'Overall risk level assessed as {risk_level}',
        'severity': risk_level.lower()
    })
    
    # Legal basis findings
    legal_basis = st.session_state.gdpr_dpia_answers['step3'].get('legal_basis', 'Not specified')
    findings.append({
        'category': 'Legal Compliance',
        'finding': f'Processing based on legal basis: {legal_basis}',
        'severity': 'medium'
    })
    
    # Data minimization findings
    data_min = st.session_state.gdpr_dpia_answers['step3'].get('data_minimization', 'Not yet applied')
    if data_min != 'Yes, fully applied':
        findings.append({
            'category': 'Data Minimization',
            'finding': f'Data minimization status: {data_min}',
            'severity': 'medium' if 'Partially' in data_min else 'high'
        })
    
    return findings

def generate_recommendations_from_answers():
    """Generate recommendations from user answers."""
    recommendations = []
    
    # Risk-based recommendations
    risk_level = st.session_state.gdpr_dpia_answers['step4'].get('overall_risk_level', 'Medium')
    if risk_level == 'High':
        recommendations.append("Implement additional technical and organizational measures to reduce high-risk processing")
        recommendations.append("Consider consultation with supervisory authority before proceeding")
    
    # Legal basis recommendations
    legal_basis = st.session_state.gdpr_dpia_answers['step3'].get('legal_basis', '')
    if legal_basis == 'Consent':
        recommendations.append("Ensure consent is freely given, specific, informed and withdrawable")
    elif legal_basis == 'Legitimate interests':
        recommendations.append("Conduct and document legitimate interests assessment")
    
    # Data minimization recommendations
    data_min = st.session_state.gdpr_dpia_answers['step3'].get('data_minimization', 'Not yet applied')
    if data_min != 'Yes, fully applied':
        recommendations.append("Review data collection to ensure only necessary data is processed")
    
    # General recommendations
    recommendations.append("Implement regular DPIA reviews as specified in Step 7")
    recommendations.append("Ensure staff training on privacy requirements")
    recommendations.append("Maintain documentation of all processing activities")
    
    return recommendations

def display_assessment_results(results, report_data):
    """Display the DPIA assessment results."""
    st.markdown("## DPIA Assessment Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Overall Risk", results.get('overall_risk_level', 'Unknown'))
    
    with col2:
        st.metric("Decision", results.get('decision', 'Pending')[:20] + "...")
    
    with col3:
        st.metric("Compliance Status", results.get('compliance_status', 'Unknown'))
    
    with col4:
        st.metric("Assessment ID", results.get('assessment_id', 'Unknown')[:8] + "...")
    
    # Findings
    if 'findings' in results and results['findings']:
        st.markdown("### Key Findings")
        findings_df = []
        for finding in results['findings']:
            findings_df.append({
                'Category': finding.get('category', ''),
                'Finding': finding.get('finding', ''),
                'Severity': finding.get('severity', '').title()
            })
        
        if findings_df:
            import pandas as pd
            df = pd.DataFrame(findings_df)
            st.dataframe(df, use_container_width=True)
    
    # Recommendations  
    if 'recommendations' in results and results['recommendations']:
        st.markdown("### Recommendations")
        for i, rec in enumerate(results['recommendations'], 1):
            st.markdown(f"{i}. {rec}")
    
    # Assessment Details
    with st.expander("View Assessment Details"):
        st.json(st.session_state.gdpr_dpia_answers)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Download HTML Report", type="primary"):
            html_report = generate_html_report(results, report_data)
            st.download_button(
                label="Save HTML Report",
                data=html_report,
                file_name=f"DPIA_Report_{results.get('assessment_id', 'unknown')[:8]}.html",
                mime="text/html"
            )
    
    with col2:
        if st.button("New Assessment"):
            # Clear session state for new assessment
            for key in list(st.session_state.keys()):
                if key.startswith('gdpr_dpia') or key.startswith('dpia_'):
                    del st.session_state[key]
            st.rerun()
    
    with col3:
        if st.button("View in History"):
            st.session_state.selected_nav = "History"
            st.rerun()

def generate_html_report(results, report_data):
    """Generate HTML report for the DPIA assessment."""
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>DPIA Assessment Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background-color: #1e3c72; color: white; padding: 20px; text-align: center; }}
            .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #1e3c72; }}
            .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #f5f5f5; border-radius: 5px; }}
            .finding {{ margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-radius: 5px; }}
            .high {{ border-left: 4px solid #dc3545; }}
            .medium {{ border-left: 4px solid #ffc107; }}
            .low {{ border-left: 4px solid #28a745; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Data Protection Impact Assessment Report</h1>
            <p>Generated on {report_data.get('generated_date', 'Unknown')}</p>
        </div>
        
        <div class="section">
            <h2>Assessment Summary</h2>
            <div class="metric">
                <strong>Project:</strong> {results.get('project_name', 'Unknown')}
            </div>
            <div class="metric">
                <strong>Overall Risk:</strong> {results.get('overall_risk_level', 'Unknown')}
            </div>
            <div class="metric">
                <strong>Decision:</strong> {results.get('decision', 'Pending')}
            </div>
            <div class="metric">
                <strong>Compliance Status:</strong> {results.get('compliance_status', 'Unknown')}
            </div>
        </div>
        
        <div class="section">
            <h2>Key Findings</h2>
            {generate_findings_html(results.get('findings', []))}
        </div>
        
        <div class="section">
            <h2>Recommendations</h2>
            {generate_recommendations_html(results.get('recommendations', []))}
        </div>
        
        <div class="section">
            <h2>Assessment Details</h2>
            {generate_assessment_details_html(report_data.get('assessment_data', {}))}
        </div>
        
        <div class="section">
            <p><small>This report was generated by DataGuardian Pro DPIA Assessment Tool</small></p>
        </div>
    </body>
    </html>
    """
    
    return html_template

def generate_findings_html(findings):
    """Generate HTML for findings section."""
    if not findings:
        return "<p>No specific findings to report.</p>"
    
    html = ""
    for finding in findings:
        severity = finding.get('severity', 'medium')
        html += f"""
        <div class="finding {severity}">
            <strong>{finding.get('category', 'General')}:</strong> {finding.get('finding', '')}
        </div>
        """
    return html

def generate_recommendations_html(recommendations):
    """Generate HTML for recommendations section."""
    if not recommendations:
        return "<p>No specific recommendations at this time.</p>"
    
    html = "<ol>"
    for rec in recommendations:
        html += f"<li>{rec}</li>"
    html += "</ol>"
    return html

def generate_assessment_details_html(assessment_data):
    """Generate HTML for assessment details."""
    html = ""
    for step, data in assessment_data.items():
        if data:  # Only show steps with data
            html += f"<h3>Step {step.replace('step', '').upper()}</h3>"
            html += "<ul>"
            for key, value in data.items():
                if isinstance(value, list):
                    value = ", ".join(value)
                html += f"<li><strong>{key.replace('_', ' ').title()}:</strong> {value}</li>"
            html += "</ul>"
    return html
                    "Small (<1,000 individuals)",
                    "Medium (1,000-10,000 individuals)", 
                    "Large (10,000-100,000 individuals)",
                    "Very Large (>100,000 individuals)"
                ],
                help="Estimated number of data subjects affected"
            )
            
            processing_frequency = st.selectbox(
                "Processing Frequency *",
                options=[
                    "One-time",
                    "Periodic (monthly/quarterly)",
                    "Regular (daily/weekly)",
                    "Continuous/Real-time"
                ]
            )
            
        with col2:
            retention_period = st.text_input(
                "Data Retention Period *",
                value=st.session_state.dpia_assessment_data['processing_description'].get('retention_period', ''),
                help="How long will data be retained? (e.g., '2 years', 'Until purpose fulfilled')"
            )
            
            automated_decision = st.selectbox(
                "Automated Decision Making *",
                options=[
                    "No automated decisions",
                    "Automated decisions with human review",
                    "Fully automated decisions",
                    "Profiling activities"
                ],
                help="Does processing involve automated decision-making?"
            )
        
        new_technology = st.selectbox(
            "Use of New Technology *",
            options=[
                "No - established technology",
                "Yes - emerging technology",
                "Yes - AI/ML systems",
                "Yes - experimental technology"
            ],
            help="Does processing use new or innovative technology?"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            back = st.form_submit_button("Back")
        with col2:
            next_btn = st.form_submit_button("Continue to Legal Basis", type="primary")
        
        if back:
            st.session_state.dpia_current_section = 0
            st.rerun()
            
        if next_btn:
            if not all([processing_name, processing_purpose, processing_description, retention_period]):
                st.error("Please fill in all required fields marked with *")
                return
            
            st.session_state.dpia_assessment_data['processing_description'] = {
                'name': processing_name,
                'purpose': processing_purpose,
                'description': processing_description,
                'data_volume': data_volume,
                'processing_frequency': processing_frequency,
                'retention_period': retention_period,
                'automated_decision': automated_decision,
                'new_technology': new_technology
            }
            
            st.session_state.dpia_current_section = 2
            st.rerun()

def handle_legal_basis():
    """Handle legal basis analysis."""
    st.markdown("### Legal Basis Analysis")
    st.markdown("Identify the legal basis for processing under GDPR Article 6 and any special category provisions.")
    
    form_key = f"legal_basis_{int(time.time() * 1000)}"
    with st.form(form_key):
        st.markdown("#### GDPR Article 6 Legal Basis")
        
        legal_basis_art6 = st.multiselect(
            "Article 6 Legal Basis (select all that apply) *",
            options=[
                "Art 6(1)(a) - Consent",
                "Art 6(1)(b) - Contract performance",
                "Art 6(1)(c) - Legal obligation",
                "Art 6(1)(d) - Vital interests",
                "Art 6(1)(e) - Public task",
                "Art 6(1)(f) - Legitimate interests"
            ],
            help="Select the legal basis under GDPR Article 6"
        )
        
        if "Art 6(1)(f) - Legitimate interests" in legal_basis_art6:
            legitimate_interests = st.text_area(
                "Legitimate Interests Assessment *",
                help="Describe the legitimate interests and balancing test performed",
                height=120
            )
        else:
            legitimate_interests = ""
        
        legal_basis_justification = st.text_area(
            "Legal Basis Justification *",
            value=st.session_state.dpia_assessment_data['legal_basis'].get('justification', ''),
            help="Explain why the selected legal basis is appropriate",
            height=120
        )
        
        st.markdown("#### Special Categories (Article 9)")
        
        special_categories = st.multiselect(
            "Special Categories of Data Processed",
            options=[
                "Health data",
                "Genetic data", 
                "Biometric data",
                "Racial/ethnic origin",
                "Political opinions",
                "Religious beliefs",
                "Trade union membership",
                "Sexual orientation data",
                "Criminal conviction data"
            ],
            help="Select any special categories that apply"
        )
        
        if special_categories:
            special_legal_basis = st.multiselect(
                "Article 9 Legal Basis for Special Categories *",
                options=[
                    "Art 9(2)(a) - Explicit consent",
                    "Art 9(2)(b) - Employment/social security law",
                    "Art 9(2)(c) - Vital interests",
                    "Art 9(2)(d) - Legitimate activities",
                    "Art 9(2)(e) - Data made public",
                    "Art 9(2)(f) - Legal claims",
                    "Art 9(2)(g) - Substantial public interest",
                    "Art 9(2)(h) - Healthcare",
                    "Art 9(2)(i) - Public health",
                    "Art 9(2)(j) - Research/statistics"
                ]
            )
        else:
            special_legal_basis = []
        
        col1, col2 = st.columns(2)
        with col1:
            back = st.form_submit_button("Back")
        with col2:
            next_btn = st.form_submit_button("Continue to Data Categories", type="primary")
        
        if back:
            st.session_state.dpia_current_section = 1
            st.rerun()
            
        if next_btn:
            if not legal_basis_art6 or not legal_basis_justification:
                st.error("Please fill in all required fields marked with *")
                return
                
            if special_categories and not special_legal_basis:
                st.error("Please select Article 9 legal basis for special categories")
                return
            
            st.session_state.dpia_assessment_data['legal_basis'] = {
                'article_6_basis': legal_basis_art6,
                'justification': legal_basis_justification,
                'legitimate_interests': legitimate_interests,
                'special_categories': special_categories,
                'article_9_basis': special_legal_basis
            }
            
            st.session_state.dpia_current_section = 3
            st.rerun()

def handle_risk_assessment():
    """Handle comprehensive risk assessment."""
    st.markdown("### Risk Assessment")
    st.markdown("Assess privacy risks to data subjects and compliance risks.")
    
    form_key = f"risk_assessment_{int(time.time() * 1000)}"
    with st.form(form_key):
        st.markdown("#### Privacy Risks to Data Subjects")
        
        # Privacy impact assessment
        privacy_risks = {}
        risk_categories = [
            ("unlawful_processing", "Unlawful or unfair processing"),
            ("loss_control", "Loss of control over personal data"),
            ("discrimination", "Discrimination or bias"),
            ("identity_theft", "Identity theft or fraud"),
            ("financial_loss", "Financial or economic loss"),
            ("reputation_damage", "Reputation damage"),
            ("physical_harm", "Physical harm or safety risks"),
            ("emotional_distress", "Emotional distress"),
            ("violation_rights", "Violation of fundamental rights")
        ]
        
        for risk_id, risk_name in risk_categories:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{risk_name}**")
            with col2:
                risk_level = st.selectbox(
                    f"Risk level",
                    options=["None", "Low", "Medium", "High", "Critical"],
                    key=f"privacy_risk_{risk_id}",
                    label_visibility="collapsed"
                )
                privacy_risks[risk_id] = risk_level
        
        st.markdown("#### Compliance Risks")
        
        compliance_risks = {}
        compliance_categories = [
            ("gdpr_violation", "GDPR violation and fines"),
            ("supervisory_action", "Supervisory authority action"),
            ("data_breach", "Data breach notification requirements"),
            ("subject_rights", "Data subject rights violations"),
            ("third_country", "Third country transfer violations"),
            ("consent_issues", "Consent validity issues"),
            ("retention_violations", "Data retention violations"),
            ("security_failures", "Security measure failures")
        ]
        
        for risk_id, risk_name in compliance_categories:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{risk_name}**")
            with col2:
                risk_level = st.selectbox(
                    f"Risk level",
                    options=["None", "Low", "Medium", "High", "Critical"],
                    key=f"compliance_risk_{risk_id}",
                    label_visibility="collapsed"
                )
                compliance_risks[risk_id] = risk_level
        
        st.markdown("#### Risk Likelihood and Impact")
        
        overall_likelihood = st.selectbox(
            "Overall Risk Likelihood *",
            options=["Very Low", "Low", "Medium", "High", "Very High"],
            help="What is the likelihood that identified risks will materialize?"
        )
        
        overall_impact = st.selectbox(
            "Overall Risk Impact *",
            options=["Minimal", "Limited", "Significant", "Severe", "Critical"],
            help="What would be the impact if risks materialize?"
        )
        
        additional_risks = st.text_area(
            "Additional Risk Considerations",
            help="Describe any other risks not covered above",
            height=100
        )
        
        col1, col2 = st.columns(2)
        with col1:
            back = st.form_submit_button("Back")
        with col2:
            next_btn = st.form_submit_button("Continue to Dutch Requirements", type="primary")
        
        if back:
            st.session_state.dpia_current_section = 5
            st.rerun()
            
        if next_btn:
            # Calculate overall risk level
            all_risks = list(privacy_risks.values()) + list(compliance_risks.values())
            critical_count = all_risks.count("Critical")
            high_count = all_risks.count("High")
            
            if critical_count > 0:
                overall_risk = "Critical"
            elif high_count >= 3:
                overall_risk = "High"
            elif high_count > 0 or all_risks.count("Medium") >= 5:
                overall_risk = "Medium"
            else:
                overall_risk = "Low"
            
            st.session_state.dpia_assessment_data['risk_assessment'] = {
                'privacy_risks': privacy_risks,
                'compliance_risks': compliance_risks,
                'overall_likelihood': overall_likelihood,
                'overall_impact': overall_impact,
                'additional_risks': additional_risks,
                'calculated_risk_level': overall_risk
            }
            
            st.session_state.dpia_current_section = 7
            st.rerun()

def handle_dutch_requirements():
    """Handle Netherlands-specific requirements."""
    st.markdown("### Dutch Specific Requirements")
    st.markdown("Assessment against Netherlands UAVG and specific Dutch data protection requirements.")
    
    form_key = f"dutch_req_{int(time.time() * 1000)}"
    with st.form(form_key):
        st.markdown("#### BSN (Burgerservicenummer) Processing")
        
        bsn_processing = st.selectbox(
            "Does processing involve BSN? *",
            options=["No", "Yes - with legal authorization", "Yes - without clear authorization", "Uncertain"],
            help="BSN processing requires specific legal authorization under UAVG Article 46"
        )
        
        if bsn_processing.startswith("Yes"):
            bsn_authorization = st.text_area(
                "BSN Processing Authorization *",
                help="Describe the specific legal authorization for BSN processing",
                height=100
            )
            
            bsn_safeguards = st.text_area(
                "BSN Safeguards *",
                help="Describe specific safeguards for BSN protection",
                height=100
            )
        else:
            bsn_authorization = ""
            bsn_safeguards = ""
        
        st.markdown("#### Autoriteit Persoonsgegevens (AP) Requirements")
        
        ap_notification = st.selectbox(
            "AP Notification Requirements *",
            options=[
                "No notification required",
                "Notification required - completed",
                "Notification required - pending",
                "Uncertain about requirements"
            ],
            help="Some processing activities require notification to the Dutch DPA"
        )
        
        breach_procedures = st.selectbox(
            "Data Breach Procedures Compliance *",
            options=[
                "Fully compliant with 72-hour notification",
                "Procedures in place but untested",
                "Partial procedures in place",
                "No specific procedures"
            ],
            help="AP requires specific breach notification procedures"
        )
        
        st.markdown("#### Netherlands-Specific Data Subject Rights")
        
        nl_rights_implementation = st.multiselect(
            "Implemented Dutch-Specific Rights Procedures",
            options=[
                "Age verification for minors (<16 years)",
                "Parental consent mechanisms",
                "Dutch language privacy notices",
                "AP complaint procedures",
                "Dutch court jurisdiction clauses",
                "UAVG-specific rectification procedures"
            ],
            help="Select implemented procedures for Netherlands-specific rights"
        )
        
        minor_processing = st.selectbox(
            "Processing of Minors' Data (<16 years) *",
            options=[
                "No processing of minors' data",
                "With verified parental consent",
                "With appropriate safeguards",
                "Without specific safeguards"
            ],
            help="Netherlands requires parental consent for children under 16"
        )
        
        st.markdown("#### Data Localization and Sovereignty")
        
        data_location = st.selectbox(
            "Primary Data Storage Location *",
            options=[
                "Netherlands only",
                "EU/EEA only", 
                "EU/EEA + adequate countries",
                "Including non-adequate countries"
            ],
            help="Consider Dutch data sovereignty requirements"
        )
        
        if "non-adequate" in data_location:
            transfer_safeguards = st.text_area(
                "Third Country Transfer Safeguards *",
                help="Describe safeguards for transfers to non-adequate countries",
                height=100
            )
        else:
            transfer_safeguards = ""
        
        col1, col2 = st.columns(2)
        with col1:
            back = st.form_submit_button("Back")
        with col2:
            next_btn = st.form_submit_button("Continue to Police Act Compliance", type="primary")
        
        if back:
            st.session_state.dpia_current_section = 6
            st.rerun()
            
        if next_btn:
            st.session_state.dpia_assessment_data['dutch_specific'] = {
                'bsn_processing': bsn_processing,
                'bsn_authorization': bsn_authorization,
                'bsn_safeguards': bsn_safeguards,
                'ap_notification': ap_notification,
                'breach_procedures': breach_procedures,
                'nl_rights_implementation': nl_rights_implementation,
                'minor_processing': minor_processing,
                'data_location': data_location,
                'transfer_safeguards': transfer_safeguards
            }
            
            st.session_state.dpia_current_section = 8
            st.rerun()

def handle_police_act_compliance():
    """Handle Dutch Police Act compliance assessment."""
    st.markdown("### Dutch Police Act (Politiewet) Compliance")
    st.markdown("Assessment of compliance with Dutch Police Act requirements for law enforcement data processing.")
    
    form_key = f"police_act_{int(time.time() * 1000)}"
    with st.form(form_key):
        st.markdown("#### Law Enforcement Context")
        
        law_enforcement_context = st.selectbox(
            "Is this processing in a law enforcement context? *",
            options=[
                "No - not law enforcement related",
                "Yes - direct law enforcement processing",
                "Yes - supporting law enforcement activities", 
                "Partial - mixed purposes"
            ],
            help="Determine if Police Act provisions apply"
        )
        
        if law_enforcement_context != "No - not law enforcement related":
            st.markdown("#### Police Act Compliance Assessment")
            
            police_act_basis = st.text_area(
                "Police Act Legal Basis *",
                help="Specify the legal basis under the Dutch Police Act",
                height=100
            )
            
            purpose_limitation = st.selectbox(
                "Purpose Limitation Compliance *",
                options=[
                    "Fully compliant - clear law enforcement purpose",
                    "Mostly compliant - minor concerns",
                    "Partially compliant - some issues",
                    "Non-compliant - purpose unclear"
                ],
                help="Police Act requires strict purpose limitation"
            )
            
            proportionality_assessment = st.text_area(
                "Proportionality Assessment *",
                help="Describe the proportionality assessment conducted",
                height=120
            )
            
            data_minimization = st.selectbox(
                "Data Minimization Implementation *",
                options=[
                    "Strict minimization applied",
                    "Generally minimized",
                    "Some unnecessary data collected",
                    "Excessive data collection"
                ],
                help="Police Act requires strict data minimization"
            )
            
            special_investigative_powers = st.selectbox(
                "Use of Special Investigative Powers",
                options=[
                    "Not applicable",
                    "Yes - with proper authorization",
                    "Yes - authorization unclear",
                    "No special powers used"
                ],
                help="Special powers require specific legal authorization"
            )
            
            data_sharing_law_enforcement = st.multiselect(
                "Data Sharing with Law Enforcement",
                options=[
                    "National police forces",
                    "Local police authorities",
                    "Public Prosecutor's Office",
                    "International law enforcement (EU)",
                    "International law enforcement (non-EU)",
                    "Intelligence services",
                    "Administrative authorities"
                ],
                help="Specify law enforcement data sharing arrangements"
            )
            
            oversight_mechanisms = st.multiselect(
                "Oversight Mechanisms in Place",
                options=[
                    "Internal oversight procedures",
                    "External judicial oversight",
                    "Parliamentary oversight",
                    "Data protection oversight",
                    "Independent review board",
                    "Regular audits"
                ],
                help="Police Act requires appropriate oversight mechanisms"
            )
            
        else:
            # Set default values for non-law enforcement
            police_act_basis = "Not applicable - not law enforcement processing"
            purpose_limitation = "Not applicable"
            proportionality_assessment = "Not applicable - not law enforcement processing"
            data_minimization = "Not applicable"
            special_investigative_powers = "Not applicable"
            data_sharing_law_enforcement = []
            oversight_mechanisms = []
        
        col1, col2 = st.columns(2)
        with col1:
            back = st.form_submit_button("Back")
        with col2:
            next_btn = st.form_submit_button("Continue to Mitigation Measures", type="primary")
        
        if back:
            st.session_state.dpia_current_section = 7
            st.rerun()
            
        if next_btn:
            st.session_state.dpia_assessment_data['police_act_compliance'] = {
                'law_enforcement_context': law_enforcement_context,
                'police_act_basis': police_act_basis,
                'purpose_limitation': purpose_limitation,
                'proportionality_assessment': proportionality_assessment,
                'data_minimization': data_minimization,
                'special_investigative_powers': special_investigative_powers,
                'data_sharing_law_enforcement': data_sharing_law_enforcement,
                'oversight_mechanisms': oversight_mechanisms
            }
            
            st.session_state.dpia_current_section = 9
            st.rerun()

def handle_mitigation_measures():
    """Handle mitigation measures."""
    st.markdown("### Mitigation Measures")
    st.markdown("Define specific measures to address identified risks and ensure compliance.")
    
    form_key = f"mitigation_{int(time.time() * 1000)}"
    with st.form(form_key):
        # Get risk assessment data
        risk_data = st.session_state.dpia_assessment_data.get('risk_assessment', {})
        overall_risk = risk_data.get('calculated_risk_level', 'Medium')
        
        st.info(f"Overall Risk Level: **{overall_risk}**")
        
        st.markdown("#### Technical Mitigation Measures")
        
        technical_measures = st.multiselect(
            "Technical Safeguards Implemented *",
            options=[
                "Data encryption at rest",
                "Data encryption in transit", 
                "Access control systems",
                "Audit logging",
                "Data anonymization/pseudonymization",
                "Secure data deletion",
                "Network security measures",
                "Backup and recovery procedures",
                "Vulnerability management",
                "Incident response procedures"
            ],
            help="Select all technical measures implemented or planned"
        )
        
        technical_details = st.text_area(
            "Technical Measures Details",
            help="Provide specific details about technical implementation",
            height=120
        )
        
        st.markdown("#### Organizational Mitigation Measures")
        
        organizational_measures = st.multiselect(
            "Organizational Safeguards Implemented *",
            options=[
                "Staff training on data protection",
                "Clear data handling procedures",
                "Data protection policies",
                "Privacy by design procedures",
                "Data breach response plan",
                "Regular compliance audits",
                "Vendor management procedures",
                "Data retention schedules",
                "Access authorization procedures",
                "Incident escalation procedures"
            ],
            help="Select all organizational measures implemented or planned"
        )
        
        organizational_details = st.text_area(
            "Organizational Measures Details",
            help="Provide specific details about organizational implementation",
            height=120
        )
        
        st.markdown("#### Risk-Specific Mitigation")
        
        high_risk_mitigation = st.text_area(
            "High-Risk Mitigation Plan *",
            help="Describe specific measures to address high and critical risks identified",
            height=150
        )
        
        st.markdown("#### Implementation Timeline")
        
        immediate_actions = st.text_area(
            "Immediate Actions (0-30 days) *",
            help="List actions to be taken immediately",
            height=100
        )
        
        short_term_actions = st.text_area(
            "Short-term Actions (1-6 months)",
            help="List actions to be completed within 6 months",
            height=100
        )
        
        ongoing_monitoring = st.text_area(
            "Ongoing Monitoring Procedures *",
            help="Describe how compliance will be monitored ongoing",
            height=100
        )
        
        col1, col2 = st.columns(2)
        with col1:
            back = st.form_submit_button("Back")
        with col2:
            next_btn = st.form_submit_button("Complete Assessment", type="primary")
        
        if back:
            st.session_state.dpia_current_section = 8
            st.rerun()
            
        if next_btn:
            if not all([technical_measures, organizational_measures, high_risk_mitigation, immediate_actions, ongoing_monitoring]):
                st.error("Please fill in all required fields marked with *")
                return
            
            st.session_state.dpia_assessment_data['mitigation_measures'] = {
                'technical_measures': technical_measures,
                'technical_details': technical_details,
                'organizational_measures': organizational_measures,
                'organizational_details': organizational_details,
                'high_risk_mitigation': high_risk_mitigation,
                'immediate_actions': immediate_actions,
                'short_term_actions': short_term_actions,
                'ongoing_monitoring': ongoing_monitoring
            }
            
            st.session_state.dpia_current_section = 10
            st.rerun()

def handle_final_assessment():
    """Handle final assessment and report generation."""
    st.markdown("### Final Assessment & Report Generation")
    
    # Calculate final compliance status
    assessment_data = st.session_state.dpia_assessment_data
    risk_level = assessment_data.get('risk_assessment', {}).get('calculated_risk_level', 'Medium')
    
    # Determine compliance status
    compliance_issues = []
    
    # Check legal basis
    legal_basis = assessment_data.get('legal_basis', {})
    if not legal_basis.get('article_6_basis'):
        compliance_issues.append("Missing Article 6 legal basis")
    
    # Check Dutch specific requirements
    dutch_req = assessment_data.get('dutch_specific', {})
    if dutch_req.get('bsn_processing', '').startswith('Yes') and not dutch_req.get('bsn_authorization'):
        compliance_issues.append("BSN processing without clear authorization")
    
    # Check mitigation measures
    mitigation = assessment_data.get('mitigation_measures', {})
    if not mitigation.get('technical_measures') or not mitigation.get('organizational_measures'):
        compliance_issues.append("Insufficient mitigation measures")
    
    # Determine overall compliance status
    if risk_level == "Critical" or len(compliance_issues) >= 3:
        compliance_status = "Non-Compliant"
        status_color = "red"
    elif risk_level == "High" or len(compliance_issues) >= 1:
        compliance_status = "Needs Improvement" 
        status_color = "orange"
    else:
        compliance_status = "Compliant"
        status_color = "green"
    
    # Display assessment summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Overall Risk Level", risk_level)
    
    with col2:
        st.metric("Compliance Issues", len(compliance_issues))
    
    with col3:
        st.markdown(f"**Compliance Status**")
        st.markdown(f":{status_color}[{compliance_status}]")
    
    if compliance_issues:
        st.markdown("#### ⚠️ Compliance Issues Identified")
        for issue in compliance_issues:
            st.write(f"• {issue}")
    
    # Store final assessment data
    assessment_data['overall_risk_level'] = risk_level
    assessment_data['compliance_status'] = compliance_status
    assessment_data['compliance_issues'] = compliance_issues
    assessment_data['completed_date'] = datetime.now().isoformat()
    
    # Generate and display HTML report
    st.markdown("### 📊 DPIA Assessment Report")
    
    html_report = generate_comprehensive_html_report(assessment_data)
    
    # Display download button
    st.download_button(
        label="📄 Download Complete DPIA Report (HTML)",
        data=html_report,
        file_name=f"DPIA_Report_{assessment_data.get('assessment_id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
        mime="text/html",
        use_container_width=True,
        type="primary"
    )
    
    # Option to start new assessment
    if st.button("🔄 Start New Assessment", use_container_width=True):
        # Clear session state
        del st.session_state.dpia_assessment_data
        del st.session_state.dpia_current_section
        st.rerun()

# Continue with placeholder implementations for data collection sections
def handle_data_categories():
    """Handle data categories and data subjects."""
    st.markdown("### Data Categories & Data Subjects")
    st.markdown("Specify the types of personal data and categories of data subjects involved.")
    
    form_key = f"data_categories_{int(time.time() * 1000)}"
    with st.form(form_key):
        st.markdown("#### Personal Data Categories")
        
        personal_data_categories = st.multiselect(
            "Select all personal data categories processed *",
            options=[
                "Basic identification data (name, address, email)",
                "Government identifiers (BSN, passport number)",
                "Financial data (bank accounts, payment info)",
                "Employment data (salary, performance, contracts)", 
                "Educational data (grades, qualifications)",
                "Health data (medical records, diagnoses)",
                "Biometric data (fingerprints, facial recognition)",
                "Location data (GPS, tracking information)",
                "Online identifiers (IP addresses, cookies)",
                "Communication data (emails, messages, calls)",
                "Behavioral data (browsing history, preferences)",
                "Criminal conviction data",
                "Other sensitive data"
            ],
            help="Select all categories that apply to your processing"
        )
        
        if "Other sensitive data" in personal_data_categories:
            other_data_description = st.text_area(
                "Describe other sensitive data *",
                help="Provide details about other sensitive data processed",
                height=100
            )
        else:
            other_data_description = ""
        
        st.markdown("#### Data Subjects Categories")
        
        data_subject_categories = st.multiselect(
            "Select all data subject categories *",
            options=[
                "Employees",
                "Job applicants", 
                "Customers/Clients",
                "Website visitors",
                "Students",
                "Patients",
                "Suppliers/Vendors",
                "Children (<16 years)",
                "Vulnerable adults",
                "Public officials",
                "Suspects/Offenders",
                "Witnesses",
                "General public"
            ],
            help="Select all categories of individuals whose data is processed"
        )
        
        st.markdown("#### Data Sources")
        
        data_sources = st.multiselect(
            "How is personal data obtained? *",
            options=[
                "Directly from data subjects",
                "From public records",
                "From third parties (partners, vendors)",
                "From social media/public sources",
                "Through automatic collection (cookies, logs)",
                "From government databases",
                "From healthcare providers",
                "From educational institutions",
                "Through surveillance systems",
                "Other sources"
            ],
            help="Select all sources of personal data"
        )
        
        if "Other sources" in data_sources:
            other_sources_description = st.text_area(
                "Describe other data sources",
                help="Provide details about other data sources",
                height=80
            )
        else:
            other_sources_description = ""
        
        st.markdown("#### Data Volume and Processing Scale")
        
        col1, col2 = st.columns(2)
        
        with col1:
            expected_volume = st.selectbox(
                "Expected number of data subjects *",
                options=[
                    "Small scale (<1,000)",
                    "Medium scale (1,000-10,000)",
                    "Large scale (10,000-100,000)", 
                    "Very large scale (>100,000)",
                    "Unclear/Variable"
                ]
            )
            
        with col2:
            geographic_scope = st.selectbox(
                "Geographic scope *",
                options=[
                    "Local (city/region)",
                    "National (Netherlands only)",
                    "EU/EEA countries",
                    "International (including third countries)",
                    "Global"
                ]
            )
        
        vulnerable_groups = st.multiselect(
            "Vulnerable groups involved",
            options=[
                "Children under 16",
                "Elderly persons",
                "Persons with disabilities",
                "Mentally incapacitated persons",
                "Economically disadvantaged",
                "Minority groups",
                "None of the above"
            ],
            help="Select if processing involves vulnerable populations requiring special protection"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            back = st.form_submit_button("Back")
        with col2:
            next_btn = st.form_submit_button("Continue to Data Sharing", type="primary")
        
        if back:
            st.session_state.dpia_current_section = 2
            st.rerun()
            
        if next_btn:
            if not all([personal_data_categories, data_subject_categories, data_sources]):
                st.error("Please fill in all required fields marked with *")
                return
            
            st.session_state.dpia_assessment_data['data_categories'] = {
                'personal_data_categories': personal_data_categories,
                'other_data_description': other_data_description,
                'data_subject_categories': data_subject_categories,
                'data_sources': data_sources,
                'other_sources_description': other_sources_description,
                'expected_volume': expected_volume,
                'geographic_scope': geographic_scope,
                'vulnerable_groups': vulnerable_groups
            }
            
            st.session_state.dpia_current_section = 4
            st.rerun()

def handle_data_sharing():
    """Handle data sharing and transfers."""
    st.markdown("### Data Sharing & Transfers")
    st.markdown("Describe how personal data is shared with third parties and transferred.")
    
    form_key = f"data_sharing_{int(time.time() * 1000)}"
    with st.form(form_key):
        st.markdown("#### Data Recipients")
        
        data_sharing_occurs = st.selectbox(
            "Is personal data shared with third parties? *",
            options=[
                "No data sharing with third parties",
                "Yes - with specific partners/vendors",
                "Yes - with group companies/affiliates", 
                "Yes - with government authorities",
                "Yes - with multiple types of recipients"
            ],
            help="Indicate if and how data is shared externally"
        )
        
        if data_sharing_occurs != "No data sharing with third parties":
            data_recipients = st.multiselect(
                "Select all types of data recipients *",
                options=[
                    "Service providers/processors",
                    "IT service providers",
                    "Cloud service providers",
                    "Marketing companies",
                    "Analytics providers",
                    "Payment processors",
                    "Legal/accounting advisors",
                    "Group companies",
                    "Government agencies",
                    "Law enforcement",
                    "Healthcare providers",
                    "Educational institutions",
                    "Research organizations",
                    "Other recipients"
                ],
                help="Select all categories of organizations that receive data"
            )
            
            if "Other recipients" in data_recipients:
                other_recipients = st.text_area(
                    "Describe other recipients *",
                    help="Specify other types of data recipients",
                    height=80
                )
            else:
                other_recipients = ""
            
            sharing_purpose = st.text_area(
                "Purpose of data sharing *",
                help="Explain why data needs to be shared with these recipients",
                height=100
            )
            
            sharing_legal_basis = st.text_area(
                "Legal basis for sharing *",
                help="Specify the legal basis for sharing data with third parties",
                height=100
            )
        else:
            data_recipients = []
            other_recipients = ""
            sharing_purpose = "No data sharing occurs"
            sharing_legal_basis = "No sharing legal basis required"
        
        st.markdown("#### International Data Transfers")
        
        international_transfers = st.selectbox(
            "Are there international data transfers? *",
            options=[
                "No international transfers",
                "Transfers to EU/EEA countries only",
                "Transfers to adequate countries (Commission decision)",
                "Transfers with appropriate safeguards (SCCs, BCRs)",
                "Transfers based on derogations",
                "Uncertain about transfer arrangements"
            ],
            help="Specify the nature of any international data transfers"
        )
        
        if international_transfers not in ["No international transfers", "Transfers to EU/EEA countries only"]:
            transfer_countries = st.text_input(
                "Destination countries *",
                help="List the countries where data is transferred",
                placeholder="e.g., United States, United Kingdom, Canada"
            )
            
            transfer_safeguards = st.multiselect(
                "Transfer safeguards in place *",
                options=[
                    "Standard Contractual Clauses (SCCs)",
                    "Binding Corporate Rules (BCRs)",
                    "Adequacy decision",
                    "Certification mechanisms",
                    "Approved codes of conduct",
                    "Explicit consent",
                    "Contract performance necessity",
                    "Public interest",
                    "Legal claims",
                    "Vital interests"
                ],
                help="Select all safeguards used for international transfers"
            )
            
            transfer_assessment = st.text_area(
                "Transfer Impact Assessment",
                help="Describe any transfer impact assessment conducted (Schrems II requirements)",
                height=100
            )
        else:
            transfer_countries = ""
            transfer_safeguards = []
            transfer_assessment = ""
        
        st.markdown("#### Data Processor Arrangements")
        
        processors_used = st.selectbox(
            "Are data processors used? *",
            options=[
                "No processors used",
                "Yes - with written agreements",
                "Yes - but agreements need review",
                "Yes - no formal agreements in place"
            ],
            help="Indicate if data processors are engaged"
        )
        
        if processors_used != "No processors used":
            processor_categories = st.multiselect(
                "Types of processors used",
                options=[
                    "Cloud hosting providers",
                    "Software service providers (SaaS)",
                    "IT support companies",
                    "Data analytics providers",
                    "Customer support providers",
                    "Marketing service providers",
                    "Backup/storage providers",
                    "Security service providers",
                    "Other technical service providers"
                ],
                help="Select types of data processors engaged"
            )
            
            processor_oversight = st.selectbox(
                "Processor oversight procedures *",
                options=[
                    "Regular audits and assessments",
                    "Annual compliance reviews",
                    "Informal monitoring only",
                    "No specific oversight procedures"
                ],
                help="Describe how processors are monitored for compliance"
            )
        else:
            processor_categories = []
            processor_oversight = "No processors used"
        
        col1, col2 = st.columns(2)
        with col1:
            back = st.form_submit_button("Back")
        with col2:
            next_btn = st.form_submit_button("Continue to Technical Measures", type="primary")
        
        if back:
            st.session_state.dpia_current_section = 3
            st.rerun()
            
        if next_btn:
            # Validate required fields based on selections
            if data_sharing_occurs != "No data sharing with third parties" and (not data_recipients or not sharing_purpose or not sharing_legal_basis):
                st.error("Please complete all data sharing fields")
                return
                
            if international_transfers not in ["No international transfers", "Transfers to EU/EEA countries only"] and (not transfer_countries or not transfer_safeguards):
                st.error("Please complete international transfer details")
                return
                
            if processors_used != "No processors used" and not processor_oversight:
                st.error("Please specify processor oversight procedures")
                return
            
            st.session_state.dpia_assessment_data['data_sharing'] = {
                'data_sharing_occurs': data_sharing_occurs,
                'data_recipients': data_recipients,
                'other_recipients': other_recipients,
                'sharing_purpose': sharing_purpose,
                'sharing_legal_basis': sharing_legal_basis,
                'international_transfers': international_transfers,
                'transfer_countries': transfer_countries,
                'transfer_safeguards': transfer_safeguards,
                'transfer_assessment': transfer_assessment,
                'processors_used': processors_used,
                'processor_categories': processor_categories,
                'processor_oversight': processor_oversight
            }
            
            st.session_state.dpia_current_section = 5
            st.rerun()

def handle_technical_measures():
    """Handle technical and organizational measures."""
    st.markdown("### Technical & Organizational Measures")
    st.markdown("Describe the security measures implemented to protect personal data.")
    
    form_key = f"tech_measures_{int(time.time() * 1000)}"
    with st.form(form_key):
        st.markdown("#### Technical Security Measures")
        
        technical_measures = st.multiselect(
            "Technical safeguards implemented *",
            options=[
                "Encryption at rest",
                "Encryption in transit (TLS/SSL)",
                "Access control systems",
                "Multi-factor authentication",
                "Audit logging and monitoring",
                "Intrusion detection systems",
                "Firewall protection",
                "Regular security updates",
                "Data backup procedures",
                "Secure data deletion",
                "Network segregation",
                "Vulnerability scanning",
                "Penetration testing",
                "Data masking/tokenization",
                "Pseudonymization techniques",
                "Anonymization procedures"
            ],
            help="Select all technical measures implemented or planned"
        )
        
        encryption_details = st.text_area(
            "Encryption implementation details",
            help="Describe encryption standards, key management, and implementation",
            height=100
        )
        
        access_control_details = st.text_area(
            "Access control implementation",
            help="Describe role-based access, authentication methods, and authorization procedures",
            height=100
        )
        
        st.markdown("#### Organizational Security Measures")
        
        organizational_measures = st.multiselect(
            "Organizational safeguards implemented *",
            options=[
                "Data protection policies",
                "Privacy by design procedures",
                "Staff training programs",
                "Regular compliance audits",
                "Data breach response plan",
                "Incident management procedures",
                "Vendor management program",
                "Data retention schedules",
                "Data minimization procedures",
                "Privacy impact assessments",
                "Data protection officer appointed",
                "Regular risk assessments",
                "Background checks for staff",
                "Confidentiality agreements",
                "Clear data handling procedures",
                "Regular security awareness training"
            ],
            help="Select all organizational measures implemented or planned"
        )
        
        staff_training_details = st.text_area(
            "Staff training program details",
            help="Describe data protection training provided to staff",
            height=100
        )
        
        breach_response_details = st.text_area(
            "Data breach response procedures",
            help="Describe procedures for detecting, reporting, and responding to data breaches",
            height=100
        )
        
        st.markdown("#### Privacy by Design Implementation")
        
        privacy_by_design = st.selectbox(
            "Privacy by Design implementation *",
            options=[
                "Comprehensive - fully integrated into design",
                "Substantial - most principles implemented",
                "Partial - some principles implemented",
                "Minimal - basic considerations only",
                "Not implemented"
            ],
            help="Assess the level of Privacy by Design implementation"
        )
        
        if privacy_by_design != "Not implemented":
            privacy_measures = st.multiselect(
                "Privacy by Design measures",
                options=[
                    "Data minimization built into systems",
                    "Purpose limitation enforced technically",
                    "Privacy-friendly default settings",
                    "User control and transparency features", 
                    "Privacy notices integrated into processes",
                    "Consent management systems",
                    "Data subject rights automation",
                    "Regular privacy reviews"
                ],
                help="Select implemented Privacy by Design measures"
            )
        else:
            privacy_measures = []
        
        st.markdown("#### Data Retention and Deletion")
        
        retention_policy = st.selectbox(
            "Data retention policy status *",
            options=[
                "Comprehensive policy implemented",
                "Basic policy in place",
                "Policy under development",
                "No formal policy"
            ],
            help="Status of data retention policy implementation"
        )
        
        if retention_policy != "No formal policy":
            retention_periods = st.text_area(
                "Retention periods by data category",
                help="Specify retention periods for different categories of personal data",
                height=100
            )
            
            deletion_procedures = st.text_area(
                "Secure deletion procedures",
                help="Describe how data is securely deleted when retention period expires",
                height=100
            )
        else:
            retention_periods = ""
            deletion_procedures = ""
        
        col1, col2 = st.columns(2)
        with col1:
            back = st.form_submit_button("Back")
        with col2:
            next_btn = st.form_submit_button("Continue to Risk Assessment", type="primary")
        
        if back:
            st.session_state.dpia_current_section = 4
            st.rerun()
            
        if next_btn:
            if not technical_measures or not organizational_measures:
                st.error("Please select technical and organizational measures")
                return
            
            st.session_state.dpia_assessment_data['technical_measures'] = {
                'technical_measures': technical_measures,
                'encryption_details': encryption_details,
                'access_control_details': access_control_details,
                'organizational_measures': organizational_measures,
                'staff_training_details': staff_training_details,
                'breach_response_details': breach_response_details,
                'privacy_by_design': privacy_by_design,
                'privacy_measures': privacy_measures,
                'retention_policy': retention_policy,
                'retention_periods': retention_periods,
                'deletion_procedures': deletion_procedures
            }
            
            st.session_state.dpia_current_section = 6
            st.rerun()

def generate_comprehensive_html_report(assessment_data: Dict[str, Any]) -> str:
    """Generate comprehensive HTML report for DPIA assessment."""
    
    # Extract key data
    org_info = assessment_data.get('organization', {})
    processing = assessment_data.get('processing_description', {})
    legal_basis = assessment_data.get('legal_basis', {})
    risk_assessment = assessment_data.get('risk_assessment', {})
    dutch_req = assessment_data.get('dutch_specific', {})
    police_act = assessment_data.get('police_act_compliance', {})
    mitigation = assessment_data.get('mitigation_measures', {})
    
    overall_risk = assessment_data.get('overall_risk_level', 'Unknown')
    compliance_status = assessment_data.get('compliance_status', 'Unknown')
    compliance_issues = assessment_data.get('compliance_issues', [])
    
    created_date = datetime.fromisoformat(assessment_data.get('created_date', datetime.now().isoformat()))
    completed_date = datetime.fromisoformat(assessment_data.get('completed_date', datetime.now().isoformat()))
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DPIA Assessment Report - {org_info.get('name', 'Unknown Organization')}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f8f9fa;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                text-align: center;
                border-radius: 10px;
                margin-bottom: 30px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }}
            .header h1 {{
                margin: 0;
                font-size: 2.5em;
                font-weight: 300;
            }}
            .header .subtitle {{
                margin: 10px 0 0 0;
                opacity: 0.9;
                font-size: 1.2em;
            }}
            .compliance-badge {{
                display: inline-block;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: bold;
                margin: 10px 0;
            }}
            .compliant {{ background-color: #d4edda; color: #155724; }}
            .needs-improvement {{ background-color: #fff3cd; color: #856404; }}
            .non-compliant {{ background-color: #f8d7da; color: #721c24; }}
            .summary-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .summary-card {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                border-left: 4px solid #667eea;
            }}
            .summary-card h3 {{
                margin-top: 0;
                color: #667eea;
            }}
            .section {{
                background: white;
                margin-bottom: 30px;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .section-header {{
                background-color: #667eea;
                color: white;
                padding: 15px 20px;
                font-size: 1.3em;
                font-weight: 600;
            }}
            .section-content {{
                padding: 20px;
            }}
            .risk-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }}
            .risk-item {{
                padding: 10px;
                border-radius: 5px;
                border-left: 4px solid;
            }}
            .risk-critical {{ border-color: #dc3545; background-color: #f8d7da; }}
            .risk-high {{ border-color: #fd7e14; background-color: #fff3cd; }}
            .risk-medium {{ border-color: #ffc107; background-color: #fff3cd; }}
            .risk-low {{ border-color: #28a745; background-color: #d4edda; }}
            .risk-none {{ border-color: #6c757d; background-color: #e9ecef; }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #f8f9fa;
                font-weight: 600;
            }}
            .mitigation-list {{
                list-style-type: none;
                padding: 0;
            }}
            .mitigation-list li {{
                background: #f8f9fa;
                margin: 5px 0;
                padding: 10px;
                border-radius: 5px;
                border-left: 3px solid #667eea;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                color: #6c757d;
                border-top: 1px solid #dee2e6;
                margin-top: 40px;
            }}
            .nl-flag {{
                display: inline-block;
                width: 20px;
                height: 15px;
                background: linear-gradient(to bottom, #FF0000 33%, #FFFFFF 33% 66%, #0000FF 66%);
                margin-right: 5px;
                vertical-align: middle;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1><span class="nl-flag"></span>Data Protection Impact Assessment</h1>
            <div class="subtitle">GDPR • Dutch Police Act • Netherlands Jurisdiction Compliance</div>
            <div class="compliance-badge {compliance_status.lower().replace(' ', '-')}">{compliance_status}</div>
        </div>

        <div class="summary-grid">
            <div class="summary-card">
                <h3>Organization</h3>
                <p><strong>{org_info.get('name', 'Not specified')}</strong></p>
                <p>{org_info.get('type', 'Not specified')}</p>
            </div>
            <div class="summary-card">
                <h3>Assessment Period</h3>
                <p><strong>Created:</strong> {created_date.strftime('%B %d, %Y')}</p>
                <p><strong>Completed:</strong> {completed_date.strftime('%B %d, %Y')}</p>
            </div>
            <div class="summary-card">
                <h3>Risk Level</h3>
                <p><strong>{overall_risk}</strong></p>
                <p>Overall privacy risk assessment</p>
            </div>
            <div class="summary-card">
                <h3>Compliance Issues</h3>
                <p><strong>{len(compliance_issues)}</strong></p>
                <p>Issues requiring attention</p>
            </div>
        </div>

        <div class="section">
            <div class="section-header">Executive Summary</div>
            <div class="section-content">
                <p>This Data Protection Impact Assessment (DPIA) was conducted for <strong>{org_info.get('name', 'the organization')}</strong> 
                to evaluate the privacy risks and compliance requirements for the processing activity: 
                <strong>"{processing.get('name', 'Unnamed Processing Activity')}"</strong>.</p>
                
                <p><strong>Assessment Scope:</strong> {org_info.get('assessment_scope', 'Not specified')}</p>
                
                <p><strong>Key Findings:</strong></p>
                <ul>
                    <li>Overall Risk Level: <strong>{overall_risk}</strong></li>
                    <li>Compliance Status: <strong>{compliance_status}</strong></li>
                    <li>Primary Jurisdiction: <strong>{org_info.get('jurisdiction', 'Not specified')}</strong></li>
                    <li>Data Volume: <strong>{processing.get('data_volume', 'Not specified')}</strong></li>
                </ul>

                {'<p><strong>⚠️ Compliance Issues Identified:</strong></p><ul>' + ''.join([f'<li>{issue}</li>' for issue in compliance_issues]) + '</ul>' if compliance_issues else '<p>✅ No critical compliance issues identified.</p>'}
            </div>
        </div>

        <div class="section">
            <div class="section-header">Processing Description</div>
            <div class="section-content">
                <table>
                    <tr><th>Processing Activity</th><td>{processing.get('name', 'Not specified')}</td></tr>
                    <tr><th>Primary Purpose</th><td>{processing.get('purpose', 'Not specified')}</td></tr>
                    <tr><th>Data Volume</th><td>{processing.get('data_volume', 'Not specified')}</td></tr>
                    <tr><th>Processing Frequency</th><td>{processing.get('processing_frequency', 'Not specified')}</td></tr>
                    <tr><th>Retention Period</th><td>{processing.get('retention_period', 'Not specified')}</td></tr>
                    <tr><th>Automated Decision Making</th><td>{processing.get('automated_decision', 'Not specified')}</td></tr>
                    <tr><th>New Technology</th><td>{processing.get('new_technology', 'Not specified')}</td></tr>
                </table>
                
                <h4>Detailed Description</h4>
                <p>{processing.get('description', 'No detailed description provided.')}</p>
            </div>
        </div>

        <div class="section">
            <div class="section-header">Legal Basis Analysis</div>
            <div class="section-content">
                <h4>GDPR Article 6 Legal Basis</h4>
                <ul>
                    {''.join([f'<li>{basis}</li>' for basis in legal_basis.get('article_6_basis', [])])}
                </ul>
                
                <h4>Justification</h4>
                <p>{legal_basis.get('justification', 'No justification provided.')}</p>
                
                {f"<h4>Special Categories of Data</h4><ul>{''.join([f'<li>{cat}</li>' for cat in legal_basis.get('special_categories', [])])}</ul>" if legal_basis.get('special_categories') else ""}
                
                {f"<h4>Article 9 Legal Basis for Special Categories</h4><ul>{''.join([f'<li>{basis}</li>' for basis in legal_basis.get('article_9_basis', [])])}</ul>" if legal_basis.get('article_9_basis') else ""}
            </div>
        </div>

        <div class="section">
            <div class="section-header">Risk Assessment</div>
            <div class="section-content">
                <h4>Privacy Risks to Data Subjects</h4>
                <div class="risk-grid">
    """
    
    # Add privacy risks
    privacy_risks = risk_assessment.get('privacy_risks', {})
    risk_labels = {
        'unlawful_processing': 'Unlawful Processing',
        'loss_control': 'Loss of Control',
        'discrimination': 'Discrimination/Bias',
        'identity_theft': 'Identity Theft',
        'financial_loss': 'Financial Loss',
        'reputation_damage': 'Reputation Damage',
        'physical_harm': 'Physical Harm',
        'emotional_distress': 'Emotional Distress',
        'violation_rights': 'Rights Violation'
    }
    
    for risk_id, risk_level in privacy_risks.items():
        risk_class = f"risk-{risk_level.lower()}"
        risk_name = risk_labels.get(risk_id, risk_id.replace('_', ' ').title())
        html_content += f'<div class="risk-item {risk_class}"><strong>{risk_name}</strong><br>{risk_level} Risk</div>'
    
    html_content += """
                </div>
                
                <h4>Compliance Risks</h4>
                <div class="risk-grid">
    """
    
    # Add compliance risks
    compliance_risks = risk_assessment.get('compliance_risks', {})
    compliance_labels = {
        'gdpr_violation': 'GDPR Violation',
        'supervisory_action': 'Supervisory Action',
        'data_breach': 'Data Breach',
        'subject_rights': 'Subject Rights',
        'third_country': 'Third Country Transfer',
        'consent_issues': 'Consent Issues',
        'retention_violations': 'Retention Violations',
        'security_failures': 'Security Failures'
    }
    
    for risk_id, risk_level in compliance_risks.items():
        risk_class = f"risk-{risk_level.lower()}"
        risk_name = compliance_labels.get(risk_id, risk_id.replace('_', ' ').title())
        html_content += f'<div class="risk-item {risk_class}"><strong>{risk_name}</strong><br>{risk_level} Risk</div>'
    
    html_content += f"""
                </div>
                
                <h4>Overall Risk Assessment</h4>
                <table>
                    <tr><th>Risk Likelihood</th><td>{risk_assessment.get('overall_likelihood', 'Not assessed')}</td></tr>
                    <tr><th>Risk Impact</th><td>{risk_assessment.get('overall_impact', 'Not assessed')}</td></tr>
                    <tr><th>Calculated Risk Level</th><td><strong>{risk_assessment.get('calculated_risk_level', 'Not calculated')}</strong></td></tr>
                </table>
                
                {f"<h4>Additional Risk Considerations</h4><p>{risk_assessment.get('additional_risks', 'None provided.')}</p>" if risk_assessment.get('additional_risks') else ""}
            </div>
        </div>

        <div class="section">
            <div class="section-header"><span class="nl-flag"></span>Netherlands UAVG Compliance</div>
            <div class="section-content">
                <h4>BSN Processing Assessment</h4>
                <table>
                    <tr><th>BSN Processing</th><td>{dutch_req.get('bsn_processing', 'Not specified')}</td></tr>
                    {'<tr><th>Authorization</th><td>' + dutch_req.get('bsn_authorization', 'Not provided') + '</td></tr>' if dutch_req.get('bsn_authorization') else ''}
                    {'<tr><th>Safeguards</th><td>' + dutch_req.get('bsn_safeguards', 'Not provided') + '</td></tr>' if dutch_req.get('bsn_safeguards') else ''}
                </table>
                
                <h4>Autoriteit Persoonsgegevens (AP) Requirements</h4>
                <table>
                    <tr><th>AP Notification</th><td>{dutch_req.get('ap_notification', 'Not specified')}</td></tr>
                    <tr><th>Breach Procedures</th><td>{dutch_req.get('breach_procedures', 'Not specified')}</td></tr>
                    <tr><th>Minor Processing</th><td>{dutch_req.get('minor_processing', 'Not specified')}</td></tr>
                    <tr><th>Data Location</th><td>{dutch_req.get('data_location', 'Not specified')}</td></tr>
                </table>
                
                <h4>Netherlands-Specific Rights Implementation</h4>
                <ul>
                    {''.join([f'<li>{right}</li>' for right in dutch_req.get('nl_rights_implementation', [])])}
                </ul>
                
                {f"<h4>Third Country Transfer Safeguards</h4><p>{dutch_req.get('transfer_safeguards', 'Not applicable.')}</p>" if dutch_req.get('transfer_safeguards') else ""}
            </div>
        </div>

        <div class="section">
            <div class="section-header">Dutch Police Act Compliance</div>
            <div class="section-content">
                <table>
                    <tr><th>Law Enforcement Context</th><td>{police_act.get('law_enforcement_context', 'Not specified')}</td></tr>
                    <tr><th>Police Act Legal Basis</th><td>{police_act.get('police_act_basis', 'Not specified')}</td></tr>
                    <tr><th>Purpose Limitation</th><td>{police_act.get('purpose_limitation', 'Not specified')}</td></tr>
                    <tr><th>Data Minimization</th><td>{police_act.get('data_minimization', 'Not specified')}</td></tr>
                    <tr><th>Special Powers</th><td>{police_act.get('special_investigative_powers', 'Not specified')}</td></tr>
                </table>
                
                {f"<h4>Proportionality Assessment</h4><p>{police_act.get('proportionality_assessment', 'Not provided.')}</p>" if police_act.get('proportionality_assessment') != 'Not applicable - not law enforcement processing' else ""}
                
                <h4>Data Sharing Arrangements</h4>
                <ul>
                    {''.join([f'<li>{arrangement}</li>' for arrangement in police_act.get('data_sharing_law_enforcement', [])]) if police_act.get('data_sharing_law_enforcement') else '<li>No law enforcement data sharing</li>'}
                </ul>
                
                <h4>Oversight Mechanisms</h4>
                <ul>
                    {''.join([f'<li>{mechanism}</li>' for mechanism in police_act.get('oversight_mechanisms', [])]) if police_act.get('oversight_mechanisms') else '<li>No specific oversight mechanisms specified</li>'}
                </ul>
            </div>
        </div>

        <div class="section">
            <div class="section-header">Mitigation Measures</div>
            <div class="section-content">
                <h4>Technical Safeguards</h4>
                <ul class="mitigation-list">
                    {''.join([f'<li>{measure}</li>' for measure in mitigation.get('technical_measures', [])])}
                </ul>
                
                {f"<p><strong>Technical Implementation Details:</strong> {mitigation.get('technical_details', 'No additional details provided.')}</p>" if mitigation.get('technical_details') else ""}
                
                <h4>Organizational Safeguards</h4>
                <ul class="mitigation-list">
                    {''.join([f'<li>{measure}</li>' for measure in mitigation.get('organizational_measures', [])])}
                </ul>
                
                {f"<p><strong>Organizational Implementation Details:</strong> {mitigation.get('organizational_details', 'No additional details provided.')}</p>" if mitigation.get('organizational_details') else ""}
                
                <h4>High-Risk Mitigation Plan</h4>
                <p>{mitigation.get('high_risk_mitigation', 'No specific plan provided.')}</p>
                
                <h4>Implementation Timeline</h4>
                <table>
                    <tr><th>Immediate Actions (0-30 days)</th><td>{mitigation.get('immediate_actions', 'Not specified')}</td></tr>
                    <tr><th>Short-term Actions (1-6 months)</th><td>{mitigation.get('short_term_actions', 'Not specified')}</td></tr>
                    <tr><th>Ongoing Monitoring</th><td>{mitigation.get('ongoing_monitoring', 'Not specified')}</td></tr>
                </table>
            </div>
        </div>

        <div class="section">
            <div class="section-header">Recommendations & Next Steps</div>
            <div class="section-content">
                <h4>Priority Actions</h4>
                <ol>
    """
    
    # Add recommendations based on assessment
    recommendations = []
    
    if overall_risk in ['Critical', 'High']:
        recommendations.append("Immediately implement high-risk mitigation measures before proceeding with processing")
    
    if 'Non-Compliant' in compliance_status:
        recommendations.append("Address compliance gaps before beginning or continuing data processing activities")
    
    if dutch_req.get('bsn_processing', '').startswith('Yes') and not dutch_req.get('bsn_authorization'):
        recommendations.append("Obtain proper legal authorization for BSN processing under UAVG Article 46")
    
    if police_act.get('law_enforcement_context', '').startswith('Yes') and police_act.get('purpose_limitation') not in ['Fully compliant - clear law enforcement purpose']:
        recommendations.append("Clarify law enforcement purpose and ensure Police Act compliance")
    
    recommendations.extend([
        "Conduct regular DPIA reviews (recommended annually or when processing changes)",
        "Implement ongoing monitoring procedures for privacy risks",
        "Ensure staff training on data protection requirements",
        "Establish clear incident response procedures"
    ])
    
    for i, rec in enumerate(recommendations, 1):
        html_content += f"<li>{rec}</li>"
    
    html_content += f"""
                </ol>
                
                <h4>Review Schedule</h4>
                <p>This DPIA should be reviewed:</p>
                <ul>
                    <li>Annually on {(completed_date + timedelta(days=365)).strftime('%B %d, %Y')}</li>
                    <li>When processing activities significantly change</li>
                    <li>When new risks are identified</li>
                    <li>Following any data breaches or incidents</li>
                    <li>When regulatory requirements change</li>
                </ul>
            </div>
        </div>

        <div class="footer">
            <p><strong>DPIA Report Generated:</strong> {completed_date.strftime('%B %d, %Y at %I:%M %p')}</p>
            <p><strong>Assessment ID:</strong> {assessment_data.get('assessment_id', 'Unknown')}</p>
            <p><strong>Jurisdiction:</strong> {org_info.get('jurisdiction', 'Netherlands')} | <strong>Applicable Law:</strong> GDPR, Dutch UAVG, Police Act</p>
            <p><em>This report represents the privacy impact assessment as of the completion date. 
            Regular reviews and updates are recommended to maintain compliance.</em></p>
        </div>
    </body>
    </html>
    """
    
    return html_content

if __name__ == "__main__":
    run_comprehensive_dpia_assessment()