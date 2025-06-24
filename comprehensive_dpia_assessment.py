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

def get_step_title(step):
    """Get the title for each GDPR DPIA step."""
    titles = [
        "Describe the processing",
        "Consider consultation", 
        "Assess necessity and proportionality",
        "Identify and assess risks",
        "Identify measures to mitigate risk",
        "Sign off and record outcomes",
        "Integrate outcomes into plan"
    ]
    return titles[step - 1] if step <= len(titles) else "Unknown Step"

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

def handle_step1_processing():
    """Step 1: Describe the processing activities."""
    st.markdown("### Step 1: Describe the processing")
    st.markdown("In this step, you'll describe the nature, scope, context, and purposes of the data processing.")
    
    form_key = f"step1_{int(time.time() * 1000)}"
    with st.form(form_key):
        st.markdown("#### Project Information")
        
        project_name = st.text_input(
            "Project Name:",
            value=st.session_state.gdpr_dpia_answers['step1'].get('project_name', ''),
            help="Name of the project or processing activity"
        )
        
        project_description = st.text_area(
            "Project Description:",
            value=st.session_state.gdpr_dpia_answers['step1'].get('project_description', ''),
            help="Describe the project or initiative that involves data processing"
        )
        
        st.markdown("#### Processing Details")
        
        processing_purpose = st.text_area(
            "What is the purpose of the data processing?",
            value=st.session_state.gdpr_dpia_answers['step1'].get('processing_purpose', ''),
            help="Explain why you need to process the personal data"
        )
        
        data_categories = st.multiselect(
            "What categories of personal data will be processed?",
            options=[
                "Basic identifiers (name, email, etc.)",
                "Contact information", 
                "ID numbers",
                "Financial data",
                "Health data",
                "Biometric data", 
                "Location data",
                "Criminal records",
                "Children's data",
                "Special category data",
                "Other sensitive data"
            ],
            default=st.session_state.gdpr_dpia_answers['step1'].get('data_categories', [])
        )
        
        data_subjects = st.multiselect(
            "Who are the data subjects?",
            options=[
                "Employees",
                "Customers", 
                "Users",
                "Patients",
                "Children",
                "Vulnerable adults",
                "General public",
                "Other"
            ],
            default=st.session_state.gdpr_dpia_answers['step1'].get('data_subjects', [])
        )
        
        data_flow = st.text_area(
            "Describe the data flow: How is data collected, stored, used, and shared?",
            value=st.session_state.gdpr_dpia_answers['step1'].get('data_flow', ''),
            help="Provide an overview of how data moves through your systems"
        )
        
        submitted = st.form_submit_button("Continue to Step 2", type="primary")
        
        if submitted:
            # Store answers
            st.session_state.gdpr_dpia_answers['step1'] = {
                'project_name': project_name,
                'project_description': project_description,
                'processing_purpose': processing_purpose,
                'data_categories': data_categories,
                'data_subjects': data_subjects,
                'data_flow': data_flow
            }
            
            # Validate required fields
            if not project_name or not processing_purpose:
                st.error("Please provide at least the project name and processing purpose before continuing.")
                return
            
            # Move to next step
            st.session_state.gdpr_dpia_step = 2
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
    
    return findings

def generate_recommendations_from_answers():
    """Generate recommendations from user answers."""
    recommendations = []
    
    # Risk-based recommendations
    risk_level = st.session_state.gdpr_dpia_answers['step4'].get('overall_risk_level', 'Medium')
    if risk_level == 'High':
        recommendations.append("Implement additional technical and organizational measures to reduce high-risk processing")
        recommendations.append("Consider consultation with supervisory authority before proceeding")
    
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
        for finding in results['findings']:
            st.write(f"- **{finding.get('category', '')}**: {finding.get('finding', '')}")
    
    # Recommendations  
    if 'recommendations' in results and results['recommendations']:
        st.markdown("### Recommendations")
        for i, rec in enumerate(results['recommendations'], 1):
            st.markdown(f"{i}. {rec}")
    
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
