"""
GDPR 7-Step DPIA Workflow

This module implements a complete Data Protection Impact Assessment (DPIA) form
following the structured 7-step approach required by GDPR Article 35.
It provides a stable, user-friendly interface for conducting thorough
privacy assessments.
"""

import streamlit as st
import os
import json
import uuid
import time
from datetime import datetime
from typing import Dict, List, Any

# Import scanner and report functions
from services.dpia_scanner import DPIAScanner, generate_dpia_report
from services.report_generator import generate_report as generate_pdf_report
from utils.i18n import get_text, _

# Configure Streamlit to trace all errors
import traceback
st.set_option('client.showErrorDetails', True)

def run_gdpr_7step_dpia():
    """
    Run a comprehensive DPIA form following the GDPR 7-step workflow.
    
    The 7 steps are:
    1. Describe the processing
    2. Consider consultation
    3. Assess necessity and proportionality
    4. Identify and assess risks
    5. Identify measures to mitigate risk
    6. Sign off and record outcomes
    7. Integrate outcomes into plan
    """
    st.title(_("scan.dpia_assessment"))
    
    # Initialize the scanner
    scanner = DPIAScanner(language=st.session_state.get('language', 'en'))
    
    # Initialize session state if needed
    if 'gdpr_dpia_step' not in st.session_state:
        st.session_state.gdpr_dpia_step = 1
    
    if 'gdpr_dpia_answers' not in st.session_state:
        st.session_state.gdpr_dpia_answers = {
            'step1': {},  # Describe the processing
            'step2': {},  # Consider consultation
            'step3': {},  # Assess necessity and proportionality
            'step4': {},  # Identify and assess risks
            'step5': {},  # Identify measures to mitigate risk
            'step6': {},  # Sign off and record outcomes
            'step7': {}   # Integrate outcomes into plan
        }
    
    # Display step navigation
    steps = [
        "1. Describe the processing",
        "2. Consider consultation",
        "3. Assess necessity & proportionality",
        "4. Identify & assess risks",
        "5. Identify measures to mitigate risk",
        "6. Sign off & record outcomes",
        "7. Integrate outcomes into plan"
    ]
    
    # Progress bar for current step
    current_step = st.session_state.gdpr_dpia_step
    st.progress((current_step - 1) / 6)
    
    # Display step indicator
    st.markdown(f"### Step {current_step} of 7: {steps[current_step-1]}")
    st.markdown("---")
    
    # If we've already submitted the form and have results, show them
    if 'gdpr_dpia_form_submitted' in st.session_state and st.session_state.gdpr_dpia_form_submitted:
        try:
            show_dpia_results(
                st.session_state.dpia_results,
                st.session_state.dpia_report_data,
                scanner
            )
            return
        except Exception as e:
            st.error(f"Error displaying DPIA results: {str(e)}")
            if st.button("Restart Assessment", type="primary"):
                reset_assessment()
                st.rerun()
    
    # Handle the current step
    try:
        if current_step == 1:
            handle_step1()
        elif current_step == 2:
            handle_step2()
        elif current_step == 3:
            handle_step3()
        elif current_step == 4:
            handle_step4(scanner)
        elif current_step == 5:
            handle_step5()
        elif current_step == 6:
            handle_step6()
        elif current_step == 7:
            handle_step7(scanner)
        else:
            st.error("Invalid step. Restarting assessment.")
            reset_assessment()
            st.rerun()
    except Exception as e:
        st.error(f"Error processing DPIA step {current_step}: {str(e)}")
        st.exception(e)
        if st.button("Restart Assessment", type="primary"):
            reset_assessment()
            st.rerun()

def handle_step1():
    """
    Step 1: Describe the processing
    
    This step collects information about the data processing activities that will be evaluated.
    """
    # Use unique form key with timestamp to avoid conflicts
    import time
    form_key = f"dpia_step1_form_{int(time.time() * 1000)}"
    with st.form(form_key):
        st.markdown("""
        ### Step 1: Describe the processing
        
        In this step, you'll describe the nature, scope, context, and purposes of the data processing.
        This information helps establish a clear understanding of what this DPIA will evaluate.
        """)
        
        st.markdown("#### Project Information")
        
        # Project details
        project_name = st.text_input("Project Name:", 
            value=st.session_state.gdpr_dpia_answers['step1'].get('project_name', ''))
        
        project_description = st.text_area("Project Description:", 
            value=st.session_state.gdpr_dpia_answers['step1'].get('project_description', ''),
            help="Describe the project or initiative that involves data processing")
        
        st.markdown("#### Processing Details")
        
        processing_purpose = st.text_area("What is the purpose of the data processing?", 
            value=st.session_state.gdpr_dpia_answers['step1'].get('processing_purpose', ''),
            help="Explain why you need to process the personal data")
        
        data_categories = st.multiselect("What categories of personal data will be processed?",
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
            default=st.session_state.gdpr_dpia_answers['step1'].get('data_categories', []))
        
        other_data = st.text_input("If you selected 'Other sensitive data', please specify:",
            value=st.session_state.gdpr_dpia_answers['step1'].get('other_data', ''))
        
        data_subjects = st.multiselect("Who are the data subjects?",
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
            default=st.session_state.gdpr_dpia_answers['step1'].get('data_subjects', []))
        
        other_subjects = st.text_input("If you selected 'Other', please specify:",
            value=st.session_state.gdpr_dpia_answers['step1'].get('other_subjects', ''))
        
        data_flow = st.text_area("Describe the data flow: How is data collected, stored, used, and shared?",
            value=st.session_state.gdpr_dpia_answers['step1'].get('data_flow', ''),
            help="Provide a overview of how data moves through your systems")
        
        # Navigation buttons
        submit = st.form_submit_button("Continue to Step 2", type="primary", use_container_width=True)
    
    if submit:
        # Store answers
        st.session_state.gdpr_dpia_answers['step1'] = {
            'project_name': project_name,
            'project_description': project_description,
            'processing_purpose': processing_purpose,
            'data_categories': data_categories,
            'other_data': other_data,
            'data_subjects': data_subjects,
            'other_subjects': other_subjects,
            'data_flow': data_flow
        }
        
        # Validate answers (at least project name and purpose)
        if not project_name or not processing_purpose:
            st.error("Please provide at least the project name and processing purpose before continuing.")
            return
        
        # Move to next step
        st.session_state.gdpr_dpia_step = 2
        st.rerun()

def handle_step2():
    """
    Step 2: Consider consultation
    
    This step covers consultation with stakeholders, including data subjects and DPO.
    """
    import time
    form_key = f"dpia_step2_form_{int(time.time() * 1000)}"
    with st.form(form_key):
        st.markdown("""
        ### Step 2: Consider consultation
        
        This step covers consultation with stakeholders, including data subjects, 
        data protection officers, and other relevant parties.
        """)
        
        st.markdown("#### Consultation with Data Subjects")
        
        consultation_needed = st.radio(
            "Is consultation with data subjects needed or practical?",
            options=["Yes", "No", "Unsure"],
            index=["Yes", "No", "Unsure"].index(st.session_state.gdpr_dpia_answers['step2'].get('consultation_needed', "Unsure"))
        )
        
        if consultation_needed == "Yes":
            consultation_method = st.text_area(
                "How will you seek the views of data subjects or their representatives?",
                value=st.session_state.gdpr_dpia_answers['step2'].get('consultation_method', ''),
                help="Describe your approach to consultation (e.g., surveys, focus groups)"
            )
        
        st.markdown("#### Data Protection Officer")
        
        dpo_consultation = st.radio(
            "Have you consulted your Data Protection Officer (DPO)?",
            options=["Yes", "No", "Not applicable"],
            index=["Yes", "No", "Not applicable"].index(st.session_state.gdpr_dpia_answers['step2'].get('dpo_consultation', "No"))
        )
        
        if dpo_consultation == "Yes":
            dpo_advice = st.text_area(
                "What advice did your DPO provide?",
                value=st.session_state.gdpr_dpia_answers['step2'].get('dpo_advice', '')
            )
        
        st.markdown("#### Other Stakeholders")
        
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
            back = st.form_submit_button("Back to Step 1", use_container_width=True)
        with col2:
            next_step = st.form_submit_button("Continue to Step 3", type="primary", use_container_width=True)
    
    if back:
        st.session_state.gdpr_dpia_step = 1
        st.rerun()
    
    if next_step:
        # Store answers
        answers = {
            'consultation_needed': consultation_needed,
            'dpo_consultation': dpo_consultation,
            'other_consultations': other_consultations,
            'consultation_outcomes': consultation_outcomes
        }
        
        if consultation_needed == "Yes":
            answers['consultation_method'] = consultation_method
        
        if dpo_consultation == "Yes":
            answers['dpo_advice'] = dpo_advice
        
        st.session_state.gdpr_dpia_answers['step2'] = answers
        
        # Move to next step
        st.session_state.gdpr_dpia_step = 3
        st.rerun()

def handle_step3():
    """
    Step 3: Assess necessity and proportionality
    
    This step evaluates whether the processing is necessary and proportionate.
    """
    import time
    form_key = f"dpia_step3_form_{int(time.time() * 1000)}"
    with st.form(form_key):
        st.markdown("""
        ### Step 3: Assess necessity and proportionality
        
        In this step, you'll evaluate whether the data processing is necessary and proportionate
        in relation to the purposes identified in step 1.
        """)
        
        st.markdown("#### Legal Basis")
        
        legal_basis = st.multiselect(
            "What is the legal basis for processing the personal data?",
            options=[
                "Consent of the data subject",
                "Performance of a contract",
                "Compliance with a legal obligation",
                "Protection of vital interests",
                "Performance of a task in the public interest",
                "Legitimate interests pursued by the controller",
                "Special category data - explicit consent",
                "Special category data - other legal basis",
                "Not yet determined"
            ],
            default=st.session_state.gdpr_dpia_answers['step3'].get('legal_basis', [])
        )
        
        if "Special category data - other legal basis" in legal_basis:
            special_category_basis = st.text_area(
                "Please specify the legal basis for processing special category data:",
                value=st.session_state.gdpr_dpia_answers['step3'].get('special_category_basis', '')
            )
        
        st.markdown("#### Necessity and Proportionality Assessment")
        
        data_minimization = st.selectbox(
            "Is the amount of data collected the minimum necessary to achieve the purpose?",
            options=["Yes", "Partially", "No"],
            index=["Yes", "Partially", "No"].index(st.session_state.gdpr_dpia_answers['step3'].get('data_minimization', "Partially"))
        )
        
        purpose_limitation = st.selectbox(
            "Is the data used only for the purposes specified?",
            options=["Yes", "Partially", "No"],
            index=["Yes", "Partially", "No"].index(st.session_state.gdpr_dpia_answers['step3'].get('purpose_limitation', "Partially"))
        )
        
        storage_limitation = st.selectbox(
            "Are there clear retention periods and deletion mechanisms?",
            options=["Yes", "Partially", "No"],
            index=["Yes", "Partially", "No"].index(st.session_state.gdpr_dpia_answers['step3'].get('storage_limitation', "Partially"))
        )
        
        st.markdown("#### Data Subject Rights")
        
        data_subject_rights = st.multiselect(
            "How will you ensure data subjects can exercise their rights?",
            options=[
                "Right to access",
                "Right to rectification",
                "Right to erasure (right to be forgotten)",
                "Right to restrict processing",
                "Right to data portability",
                "Right to object",
                "Rights related to automated decision making and profiling"
            ],
            default=st.session_state.gdpr_dpia_answers['step3'].get('data_subject_rights', [])
        )
        
        rights_procedure = st.text_area(
            "Describe your procedure for handling data subject requests:",
            value=st.session_state.gdpr_dpia_answers['step3'].get('rights_procedure', '')
        )
        
        international_transfers = st.radio(
            "Will personal data be transferred outside the EU/EEA?",
            options=["Yes", "No", "Unsure"],
            index=["Yes", "No", "Unsure"].index(st.session_state.gdpr_dpia_answers['step3'].get('international_transfers', "Unsure"))
        )
        
        if international_transfers == "Yes":
            transfer_safeguards = st.multiselect(
                "What safeguards will be in place for international transfers?",
                options=[
                    "Adequacy decision",
                    "Standard contractual clauses",
                    "Binding corporate rules",
                    "Code of conduct",
                    "Certification mechanism",
                    "Derogations for specific situations",
                    "None of the above"
                ],
                default=st.session_state.gdpr_dpia_answers['step3'].get('transfer_safeguards', [])
            )
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            back = st.form_submit_button("Back to Step 2", use_container_width=True)
        with col2:
            next_step = st.form_submit_button("Continue to Step 4", type="primary", use_container_width=True)
    
    if back:
        st.session_state.gdpr_dpia_step = 2
        st.rerun()
    
    if next_step:
        # Store answers
        answers = {
            'legal_basis': legal_basis,
            'data_minimization': data_minimization,
            'purpose_limitation': purpose_limitation,
            'storage_limitation': storage_limitation,
            'data_subject_rights': data_subject_rights,
            'rights_procedure': rights_procedure,
            'international_transfers': international_transfers
        }
        
        if "Special category data - other legal basis" in legal_basis:
            answers['special_category_basis'] = special_category_basis
        
        if international_transfers == "Yes":
            answers['transfer_safeguards'] = transfer_safeguards
        
        st.session_state.gdpr_dpia_answers['step3'] = answers
        
        # Move to next step
        st.session_state.gdpr_dpia_step = 4
        st.rerun()

def handle_step4(scanner):
    """
    Step 4: Identify and assess risks
    
    This step identifies and assesses the privacy risks to individuals.
    """
    # Get assessment categories from scanner
    assessment_categories = scanner._get_assessment_categories()
    
    # Initialize answers if not already present
    if 'risk_assessment' not in st.session_state.gdpr_dpia_answers['step4']:
        st.session_state.gdpr_dpia_answers['step4']['risk_assessment'] = {}
        for category in assessment_categories:
            question_count = len(assessment_categories[category]['questions'])
            st.session_state.gdpr_dpia_answers['step4']['risk_assessment'][category] = [0] * question_count
    
    import time
    form_key = f"dpia_step4_form_{int(time.time() * 1000)}"
    with st.form(form_key):
        st.markdown("""
        ### Step 4: Identify and assess risks
        
        In this step, you'll identify and assess the risks to individuals' privacy and rights
        that could result from the data processing activities.
        """)
        
        st.markdown("""
        #### Risk Assessment
        
        For each of the following statements, select the appropriate response:
        - **No**: The statement doesn't apply to your processing activities
        - **Partially**: The statement partially applies to your processing activities
        - **Yes**: The statement fully applies to your processing activities
        """)
        
        # Create tabs for each category
        tabs = st.tabs([assessment_categories[cat]['name'] for cat in assessment_categories])
        
        for i, category in enumerate(assessment_categories):
            with tabs[i]:
                st.markdown(f"### {assessment_categories[category]['name']}")
                st.markdown(f"*{assessment_categories[category]['description']}*")
                st.markdown("---")
                
                for q_idx, question in enumerate(assessment_categories[category]['questions']):
                    current_val = st.session_state.gdpr_dpia_answers['step4']['risk_assessment'][category][q_idx]
                    key = f"step4_{category}_{q_idx}"
                    options = ["No", "Partially", "Yes"]
                    selected = st.selectbox(
                        f"{q_idx+1}. {question}",
                        options=options,
                        index=current_val,
                        key=key
                    )
                    st.session_state.gdpr_dpia_answers['step4']['risk_assessment'][category][q_idx] = options.index(selected)
        
        # Additional identified risks
        st.markdown("#### Additional Identified Risks")
        
        additional_risks = st.text_area(
            "List any additional privacy risks you've identified:",
            value=st.session_state.gdpr_dpia_answers['step4'].get('additional_risks', ''),
            help="Describe any risks not covered in the questions above"
        )
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            back = st.form_submit_button("Back to Step 3", use_container_width=True)
        with col2:
            next_step = st.form_submit_button("Continue to Step 5", type="primary", use_container_width=True)
    
    if back:
        st.session_state.gdpr_dpia_step = 3
        st.rerun()
    
    if next_step:
        # Store additional answers
        st.session_state.gdpr_dpia_answers['step4']['additional_risks'] = additional_risks
        
        # Move to next step
        st.session_state.gdpr_dpia_step = 5
        st.rerun()

def handle_step5():
    """
    Step 5: Identify measures to mitigate risk
    
    This step identifies measures to reduce the risks identified in step 4.
    """
    import time
    form_key = f"dpia_step5_form_{int(time.time() * 1000)}"
    with st.form(form_key):
        st.markdown("""
        ### Step 5: Identify measures to mitigate risk
        
        In this step, you'll identify measures to reduce the privacy risks identified in step 4.
        These measures should help ensure compliance with data protection principles.
        """)
        
        st.markdown("#### Technical Measures")
        
        technical_measures = st.multiselect(
            "What technical measures will be implemented to mitigate risks?",
            options=[
                "Encryption (at rest)",
                "Encryption (in transit)",
                "Pseudonymization",
                "Anonymization",
                "Access controls",
                "Audit logs",
                "Intrusion detection/prevention systems",
                "Data loss prevention",
                "Backup and recovery processes",
                "Regular security testing",
                "Secure development lifecycle",
                "Other technical measures"
            ],
            default=st.session_state.gdpr_dpia_answers['step5'].get('technical_measures', [])
        )
        
        if "Other technical measures" in technical_measures:
            other_technical = st.text_area(
                "Please specify other technical measures:",
                value=st.session_state.gdpr_dpia_answers['step5'].get('other_technical', '')
            )
        
        st.markdown("#### Organizational Measures")
        
        organizational_measures = st.multiselect(
            "What organizational measures will be implemented to mitigate risks?",
            options=[
                "Data protection policies",
                "Staff training",
                "Confidentiality agreements",
                "Processor contracts with appropriate clauses",
                "Regular compliance audits",
                "Data protection by design and default processes",
                "Incident response procedures",
                "Data minimization practices",
                "Clear retention schedules",
                "Data subject rights procedures",
                "Other organizational measures"
            ],
            default=st.session_state.gdpr_dpia_answers['step5'].get('organizational_measures', [])
        )
        
        if "Other organizational measures" in organizational_measures:
            other_organizational = st.text_area(
                "Please specify other organizational measures:",
                value=st.session_state.gdpr_dpia_answers['step5'].get('other_organizational', '')
            )
        
        st.markdown("#### Specific Risk Mitigations")
        
        specific_mitigations = st.text_area(
            "Describe specific mitigations for high-risk areas identified in Step 4:",
            value=st.session_state.gdpr_dpia_answers['step5'].get('specific_mitigations', '')
        )
        
        residual_risk = st.radio(
            "What is the level of residual risk after implementing these measures?",
            options=["Low", "Medium", "High"],
            index=["Low", "Medium", "High"].index(st.session_state.gdpr_dpia_answers['step5'].get('residual_risk', "Medium"))
        )
        
        residual_risk_acceptable = st.radio(
            "Is the residual risk acceptable in relation to the benefits of the processing?",
            options=["Yes", "No", "Requires further assessment"],
            index=["Yes", "No", "Requires further assessment"].index(st.session_state.gdpr_dpia_answers['step5'].get('residual_risk_acceptable', "Requires further assessment"))
        )
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            back = st.form_submit_button("Back to Step 4", use_container_width=True)
        with col2:
            next_step = st.form_submit_button("Continue to Step 6", type="primary", use_container_width=True)
    
    if back:
        st.session_state.gdpr_dpia_step = 4
        st.rerun()
    
    if next_step:
        # Store answers
        answers = {
            'technical_measures': technical_measures,
            'organizational_measures': organizational_measures,
            'specific_mitigations': specific_mitigations,
            'residual_risk': residual_risk,
            'residual_risk_acceptable': residual_risk_acceptable
        }
        
        if "Other technical measures" in technical_measures:
            answers['other_technical'] = other_technical
        
        if "Other organizational measures" in organizational_measures:
            answers['other_organizational'] = other_organizational
        
        st.session_state.gdpr_dpia_answers['step5'] = answers
        
        # Move to next step
        st.session_state.gdpr_dpia_step = 6
        st.rerun()

def handle_step6():
    """
    Step 6: Sign off and record outcomes
    
    This step involves formally accepting the outcomes of the DPIA and documenting sign-off.
    """
    import time
    form_key = f"dpia_step6_form_{int(time.time() * 1000)}"
    with st.form(form_key):
        st.markdown("""
        ### Step 6: Sign off and record outcomes
        
        In this step, you'll sign off on the DPIA findings and decisions, 
        and record the outcomes for documentation purposes.
        """)
        
        st.markdown("#### Decision")
        
        proceed_decision = st.radio(
            "What is your decision about proceeding with the processing?",
            options=[
                "Proceed - Risks have been eliminated",
                "Proceed - Risks have been reduced to an acceptable level",
                "Proceed - Benefits outweigh risks",
                "Proceed - Only with prior consultation with supervisory authority",
                "Do not proceed - Risks remain unacceptably high"
            ],
            index=["Proceed - Risks have been eliminated", 
                   "Proceed - Risks have been reduced to an acceptable level", 
                   "Proceed - Benefits outweigh risks",
                   "Proceed - Only with prior consultation with supervisory authority",
                   "Do not proceed - Risks remain unacceptably high"].index(
                       st.session_state.gdpr_dpia_answers['step6'].get('proceed_decision', "Proceed - Risks have been reduced to an acceptable level")
                   )
        )
        
        prior_consultation = st.radio(
            "Is prior consultation with the supervisory authority needed?",
            options=["Yes", "No"],
            index=["Yes", "No"].index(st.session_state.gdpr_dpia_answers['step6'].get('prior_consultation', "No"))
        )
        
        st.markdown("#### Sign Off")
        
        dpo_approved = st.radio(
            "DPO/Privacy Officer Approval:",
            options=["Approved", "Approved with conditions", "Not approved", "Not applicable"],
            index=["Approved", "Approved with conditions", "Not approved", "Not applicable"].index(
                st.session_state.gdpr_dpia_answers['step6'].get('dpo_approved', "Not applicable")
            )
        )
        
        if dpo_approved == "Approved with conditions":
            dpo_conditions = st.text_area(
                "DPO approval conditions:",
                value=st.session_state.gdpr_dpia_answers['step6'].get('dpo_conditions', '')
            )
        
        approver_name = st.text_input(
            "Name of approver:",
            value=st.session_state.gdpr_dpia_answers['step6'].get('approver_name', '')
        )
        
        approver_role = st.text_input(
            "Role/position of approver:",
            value=st.session_state.gdpr_dpia_answers['step6'].get('approver_role', '')
        )
        
        approval_date = st.date_input(
            "Date of approval:",
            value=datetime.now().date()
        )
        
        summary_comments = st.text_area(
            "Summary comments:",
            value=st.session_state.gdpr_dpia_answers['step6'].get('summary_comments', '')
        )
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            back = st.form_submit_button("Back to Step 5", use_container_width=True)
        with col2:
            next_step = st.form_submit_button("Continue to Step 7", type="primary", use_container_width=True)
    
    if back:
        st.session_state.gdpr_dpia_step = 5
        st.rerun()
    
    if next_step:
        # Store answers
        answers = {
            'proceed_decision': proceed_decision,
            'prior_consultation': prior_consultation,
            'dpo_approved': dpo_approved,
            'approver_name': approver_name,
            'approver_role': approver_role,
            'approval_date': str(approval_date),
            'summary_comments': summary_comments
        }
        
        if dpo_approved == "Approved with conditions":
            answers['dpo_conditions'] = dpo_conditions
        
        st.session_state.gdpr_dpia_answers['step6'] = answers
        
        # Move to next step
        st.session_state.gdpr_dpia_step = 7
        st.rerun()

def handle_step7(scanner):
    """
    Step 7: Integrate outcomes into plan
    
    This final step involves planning how to implement the identified measures and complete the DPIA.
    """
    import time
    form_key = f"dpia_step7_form_{int(time.time() * 1000)}"
    with st.form(form_key):
        st.markdown("""
        ### Step 7: Integrate outcomes into plan
        
        In this final step, you'll plan how to implement the measures identified in the DPIA,
        assign responsibilities, and set up review processes.
        """)
        
        st.markdown("#### Implementation Plan")
        
        action_plan = st.text_area(
            "Action plan for implementing identified measures:",
            value=st.session_state.gdpr_dpia_answers['step7'].get('action_plan', ''),
            help="Outline the specific actions that will be taken to implement the mitigation measures"
        )
        
        st.markdown("#### Responsibilities")
        
        responsible_person = st.text_input(
            "Who is responsible for implementing the action plan?",
            value=st.session_state.gdpr_dpia_answers['step7'].get('responsible_person', '')
        )
        
        responsible_role = st.text_input(
            "Role/position of responsible person:",
            value=st.session_state.gdpr_dpia_answers['step7'].get('responsible_role', '')
        )
        
        st.markdown("#### Timeline")
        
        implementation_timeline = st.text_area(
            "Timeline for implementation:",
            value=st.session_state.gdpr_dpia_answers['step7'].get('implementation_timeline', ''),
            help="Provide target dates for implementing measures"
        )
        
        st.markdown("#### Review Process")
        
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
        
        if review_schedule == "Other":
            other_schedule = st.text_input(
                "Please specify review schedule:",
                value=st.session_state.gdpr_dpia_answers['step7'].get('other_schedule', '')
            )
        
        monitoring_process = st.text_area(
            "How will you monitor the effectiveness of measures?",
            value=st.session_state.gdpr_dpia_answers['step7'].get('monitoring_process', '')
        )
        
        additional_comments = st.text_area(
            "Additional comments or considerations:",
            value=st.session_state.gdpr_dpia_answers['step7'].get('additional_comments', '')
        )
        
        # Navigation and submission
        col1, col2, col3 = st.columns([1,1,2])
        with col1:
            back = st.form_submit_button("Back to Step 6", use_container_width=True)
        with col2:
            review = st.form_submit_button("Review All Steps", use_container_width=True)
        with col3:
            submit = st.form_submit_button("Submit DPIA Assessment", type="primary", use_container_width=True)
    
    if back:
        st.session_state.gdpr_dpia_step = 6
        st.rerun()
    
    if review:
        # Store current answers first
        answers = {
            'action_plan': action_plan,
            'responsible_person': responsible_person,
            'responsible_role': responsible_role,
            'implementation_timeline': implementation_timeline,
            'review_schedule': review_schedule,
            'monitoring_process': monitoring_process,
            'additional_comments': additional_comments
        }
        
        if review_schedule == "Other":
            answers['other_schedule'] = other_schedule
        
        st.session_state.gdpr_dpia_answers['step7'] = answers
        
        # Show review page
        show_review_page(scanner)
    
    if submit:
        # Store answers
        answers = {
            'action_plan': action_plan,
            'responsible_person': responsible_person,
            'responsible_role': responsible_role,
            'implementation_timeline': implementation_timeline,
            'review_schedule': review_schedule,
            'monitoring_process': monitoring_process,
            'additional_comments': additional_comments
        }
        
        if review_schedule == "Other":
            answers['other_schedule'] = other_schedule
        
        st.session_state.gdpr_dpia_answers['step7'] = answers
        
        # Process DPIA assessment
        process_dpia_assessment(scanner)

def show_review_page(scanner):
    """Show a review of all DPIA steps before final submission."""
    st.title("DPIA Assessment Review")
    st.markdown("Please review your answers before final submission.")
    
    # Create expandable sections for each step
    with st.expander("Step 1: Describe the processing", expanded=True):
        step1 = st.session_state.gdpr_dpia_answers['step1']
        st.markdown(f"**Project Name:** {step1.get('project_name', 'Not provided')}")
        st.markdown(f"**Project Description:** {step1.get('project_description', 'Not provided')}")
        st.markdown(f"**Processing Purpose:** {step1.get('processing_purpose', 'Not provided')}")
        st.markdown(f"**Data Categories:** {', '.join(step1.get('data_categories', ['None']))}")
        st.markdown(f"**Data Subjects:** {', '.join(step1.get('data_subjects', ['None']))}")
        st.markdown(f"**Data Flow:** {step1.get('data_flow', 'Not provided')}")
    
    with st.expander("Step 2: Consider consultation"):
        step2 = st.session_state.gdpr_dpia_answers['step2']
        st.markdown(f"**Consultation with Data Subjects:** {step2.get('consultation_needed', 'Not provided')}")
        st.markdown(f"**DPO Consultation:** {step2.get('dpo_consultation', 'Not provided')}")
        st.markdown(f"**Other Consultations:** {', '.join(step2.get('other_consultations', ['None']))}")
        st.markdown(f"**Consultation Outcomes:** {step2.get('consultation_outcomes', 'Not provided')}")
    
    with st.expander("Step 3: Assess necessity and proportionality"):
        step3 = st.session_state.gdpr_dpia_answers['step3']
        st.markdown(f"**Legal Basis:** {', '.join(step3.get('legal_basis', ['Not provided']))}")
        st.markdown(f"**Data Minimization:** {step3.get('data_minimization', 'Not provided')}")
        st.markdown(f"**Purpose Limitation:** {step3.get('purpose_limitation', 'Not provided')}")
        st.markdown(f"**Storage Limitation:** {step3.get('storage_limitation', 'Not provided')}")
        st.markdown(f"**Data Subject Rights:** {', '.join(step3.get('data_subject_rights', ['Not provided']))}")
        st.markdown(f"**International Transfers:** {step3.get('international_transfers', 'Not provided')}")
    
    with st.expander("Step 4: Identify and assess risks"):
        step4 = st.session_state.gdpr_dpia_answers['step4']
        st.markdown("**Risk Assessment Responses**: [Detailed risk assessment in each category]")
        st.markdown(f"**Additional Risks:** {step4.get('additional_risks', 'None')}")
    
    with st.expander("Step 5: Identify measures to mitigate risk"):
        step5 = st.session_state.gdpr_dpia_answers['step5']
        st.markdown(f"**Technical Measures:** {', '.join(step5.get('technical_measures', ['None']))}")
        st.markdown(f"**Organizational Measures:** {', '.join(step5.get('organizational_measures', ['None']))}")
        st.markdown(f"**Specific Mitigations:** {step5.get('specific_mitigations', 'Not provided')}")
        st.markdown(f"**Residual Risk:** {step5.get('residual_risk', 'Not provided')}")
        st.markdown(f"**Residual Risk Acceptable:** {step5.get('residual_risk_acceptable', 'Not provided')}")
    
    with st.expander("Step 6: Sign off and record outcomes"):
        step6 = st.session_state.gdpr_dpia_answers['step6']
        st.markdown(f"**Decision:** {step6.get('proceed_decision', 'Not provided')}")
        st.markdown(f"**Prior Consultation:** {step6.get('prior_consultation', 'Not provided')}")
        st.markdown(f"**DPO Approval:** {step6.get('dpo_approved', 'Not provided')}")
        st.markdown(f"**Approver:** {step6.get('approver_name', 'Not provided')}, {step6.get('approver_role', 'Not provided')}")
        st.markdown(f"**Approval Date:** {step6.get('approval_date', 'Not provided')}")
        st.markdown(f"**Summary Comments:** {step6.get('summary_comments', 'Not provided')}")
    
    with st.expander("Step 7: Integrate outcomes into plan"):
        step7 = st.session_state.gdpr_dpia_answers['step7']
        st.markdown(f"**Action Plan:** {step7.get('action_plan', 'Not provided')}")
        st.markdown(f"**Responsible Person:** {step7.get('responsible_person', 'Not provided')}, {step7.get('responsible_role', 'Not provided')}")
        st.markdown(f"**Implementation Timeline:** {step7.get('implementation_timeline', 'Not provided')}")
        st.markdown(f"**Review Schedule:** {step7.get('review_schedule', 'Not provided')}")
        st.markdown(f"**Monitoring Process:** {step7.get('monitoring_process', 'Not provided')}")
    
    # Add navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Continue Editing", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("Submit DPIA Assessment", type="primary", use_container_width=True):
            process_dpia_assessment(scanner)

def process_dpia_assessment(scanner):
    """Process the completed DPIA assessment and generate results."""
    try:
        with st.spinner(_("scan.dpia_processing")):
            st.write("Processing DPIA assessment...")
            
            # Extract risk assessment answers from step 4
            risk_answers = {}
            for category, values in st.session_state.gdpr_dpia_answers['step4']['risk_assessment'].items():
                risk_answers[category] = values
            
            # Perform assessment based on risk answers
            assessment_params = {
                "answers": risk_answers,
                "language": st.session_state.get('language', 'en')
            }
            
            assessment_results = scanner.perform_assessment(**assessment_params)
            
            # Enrich the results with additional data from other steps
            assessment_results['project_name'] = st.session_state.gdpr_dpia_answers['step1'].get('project_name', '')
            assessment_results['project_description'] = st.session_state.gdpr_dpia_answers['step1'].get('project_description', '')
            assessment_results['dpia_steps'] = st.session_state.gdpr_dpia_answers
            
            # Add unique ID if not present
            if "scan_id" not in assessment_results:
                assessment_results["scan_id"] = str(uuid.uuid4())
            
            # Add timestamp if not present
            if "timestamp" not in assessment_results:
                assessment_results["timestamp"] = datetime.utcnow().isoformat()
            
            # Generate report data
            report_data = generate_dpia_report(assessment_results)
            
            # Save results in session state
            st.session_state.dpia_results = assessment_results
            st.session_state.dpia_report_data = report_data
            st.session_state.gdpr_dpia_form_submitted = True
            
            # Try to save to database
            try:
                save_assessment_to_db(assessment_results)
            except Exception as db_error:
                st.warning(f"Could not save to database, but assessment is complete. Error: {str(db_error)}")
        
        # Display results without rerunning
        st.success("Assessment completed successfully!")
        show_dpia_results(
            st.session_state.dpia_results,
            st.session_state.dpia_report_data,
            scanner
        )
    
    except Exception as e:
        st.error(f"Error processing DPIA assessment: {str(e)}")
        st.exception(e)
        st.error("Please try again or contact support if the issue persists.")

def save_assessment_to_db(assessment_results):
    """Save assessment results to the database."""
    try:
        import psycopg2
        from psycopg2.extras import Json
        import os
        
        # Get database connection string from environment variable
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            st.warning("No database connection string found. Results will not be saved to database.")
            return
        
        # Connect to database
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Check if dpia_assessments table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'dpia_assessments'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        # Create table if it doesn't exist
        if not table_exists:
            cursor.execute("""
                CREATE TABLE dpia_assessments (
                    id SERIAL PRIMARY KEY,
                    scan_id TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    project_name TEXT,
                    overall_risk_level TEXT,
                    overall_percentage FLOAT,
                    dpia_required BOOLEAN,
                    data JSON
                );
            """)
            conn.commit()
        
        # Insert assessment results
        cursor.execute("""
            INSERT INTO dpia_assessments (
                scan_id, timestamp, project_name, overall_risk_level, 
                overall_percentage, dpia_required, data
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            assessment_results['scan_id'],
            assessment_results['timestamp'],
            assessment_results.get('project_name', ''),
            assessment_results['overall_risk_level'],
            assessment_results['overall_percentage'],
            assessment_results['dpia_required'],
            Json(assessment_results)
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        st.success("Assessment results saved to database.")
    except Exception as e:
        st.warning(f"Could not save to database: {str(e)}")
        raise

def show_dpia_results(assessment_results, report_data, scanner):
    """Display the results of the DPIA assessment with a professional report."""
    st.title(_("scan.dpia_results"))
    
    # Extract project information for the report header
    project_name = assessment_results.get('project_name', 'DPIA Assessment')
    
    # Create a modern report header
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #4f46e5, #2563eb); 
                color: white; padding: 20px; border-radius: 10px; margin-bottom: 30px;">
        <h1 style="margin: 0; font-size: 24px;">{project_name}</h1>
        <p style="margin: 5px 0 0 0; opacity: 0.9;">Data Protection Impact Assessment</p>
        <p style="margin: 5px 0 0 0; font-size: 12px; opacity: 0.7;">
            Assessment ID: {assessment_results['scan_id'][:8]} | 
            Date: {datetime.fromisoformat(assessment_results['timestamp']).strftime('%d %b %Y')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Overall risk summary
    risk_level = assessment_results["overall_risk_level"]
    risk_color = {
        "High": "#ef4444",
        "Medium": "#f97316",
        "Low": "#10b981"
    }.get(risk_level, "#ef4444")
    
    # Display result card with modern design
    st.markdown(f"""
    <div style="background-color: white; padding: 25px; border-radius: 10px; margin-bottom: 30px;
               box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <h2 style="margin-top: 0; color: #1f2937;">Overall Risk Assessment</h2>
        <div style="display: flex; align-items: center; margin-bottom: 20px;">
            <div style="width: 24px; height: 24px; border-radius: 50%; 
                     background-color: {risk_color}; margin-right: 12px;"></div>
            <span style="font-size: 28px; font-weight: 600; color: #1f2937;">{risk_level} Risk</span>
        </div>
        <div style="display: flex; align-items: center; margin-top: 15px;">
            <div style="flex: 1;">
                <h3 style="color: #4b5563; margin: 0 0 5px 0;">DPIA Required</h3>
                <p style="font-size: 20px; font-weight: 500; color: #1f2937; margin: 0;">
                    {"Yes" if assessment_results["dpia_required"] else "No"}
                </p>
            </div>
            <div style="flex: 1;">
                <h3 style="color: #4b5563; margin: 0 0 5px 0;">Risk Score</h3>
                <p style="font-size: 20px; font-weight: 500; color: #1f2937; margin: 0;">
                    {assessment_results["overall_percentage"]:.1f}/10
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Category breakdown with modern visualization
    st.markdown("""
    <h2 style="color: #1f2937; margin-top: 40px; margin-bottom: 20px; font-size: 22px;">
        Risk Analysis by Category
    </h2>
    """, unsafe_allow_html=True)
    
    for category, scores in assessment_results["category_scores"].items():
        category_name = scanner.assessment_categories[category]["name"]
        percentage = scores["percentage"]
        risk_level = scores["risk_level"]
        risk_color = {
            "High": "#ef4444",
            "Medium": "#f97316",
            "Low": "#10b981"
        }.get(risk_level, "#ef4444")
        
        # Display category risk bar with modern style
        st.markdown(f"""
        <div style="margin-bottom: 20px; background-color: white; padding: 15px; 
                   border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.03);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="font-weight: 500; color: #1f2937;">{category_name}</span>
                <span style="color: {risk_color}; font-weight: 500; 
                      background-color: {risk_color}15; padding: 3px 10px; border-radius: 6px;">
                    {risk_level}
                </span>
            </div>
            <div style="height: 10px; background-color: #f3f4f6; border-radius: 5px; overflow: hidden;">
                <div style="width: {percentage*10}%; height: 100%; background-color: {risk_color};"></div>
            </div>
            <div style="display: flex; justify-content: flex-end; margin-top: 5px;">
                <span style="font-size: 14px; color: #6b7280;">{percentage:.1f}/10</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Key findings and recommendations
    st.markdown("""
    <h2 style="color: #1f2937; margin-top: 40px; margin-bottom: 20px; font-size: 22px;">
        Key Findings & Recommendations
    </h2>
    """, unsafe_allow_html=True)
    
    if assessment_results["recommendations"]:
        for i, recommendation in enumerate(assessment_results["recommendations"][:7]):  # Top 7
            severity = recommendation["severity"]
            category = recommendation["category"]
            description = recommendation["description"]
            
            risk_color = {
                "High": "#ef4444",
                "Medium": "#f97316",
                "Low": "#10b981"
            }.get(severity, "#ef4444")
            
            # Display recommendation with modern card design
            st.markdown(f"""
            <div style="background-color: white; padding: 20px; border-radius: 8px; margin-bottom: 15px;
                       box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 4px solid {risk_color};">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-weight: 500; color: #4b5563;">{category}</span>
                    <span style="color: {risk_color}; font-weight: 500; 
                          background-color: {risk_color}15; padding: 2px 10px; border-radius: 6px;">
                        {severity}
                    </span>
                </div>
                <p style="margin: 0; color: #1f2937;">{description}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No specific recommendations were generated.")
    
    # Report download section with modern design
    st.markdown("""
    <div style="margin-top: 50px; margin-bottom: 30px; background-color: #f9fafb; 
              padding: 25px; border-radius: 10px;">
        <h2 style="margin-top: 0; color: #1f2937; font-size: 22px;">Download Full Report</h2>
        <p style="color: #4b5563;">
            The complete report includes detailed findings, all recommendations, and compliance guidance.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Generate PDF report
    try:
        report_filename = f"dpia_report_{assessment_results['scan_id'][:8]}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        # Show generation message
        with st.spinner("Generating PDF report..."):
            pdf_data = generate_pdf_report(report_data)
        
        st.success("✅ Report generated successfully! Click below to download.")
        
        # Download button
        if st.download_button(
            label="📄 Download DPIA Report PDF",
            data=pdf_data,
            file_name=report_filename,
            mime="application/pdf",
            use_container_width=True,
            type="primary",
            key="dpia_download_report_button"
        ):
            st.success("Report downloaded successfully!")
            
            # Add to history automatically
            if 'history' not in st.session_state:
                st.session_state.history = {}
            
            history_id = assessment_results['scan_id']
            if history_id not in st.session_state.history:
                st.session_state.history[history_id] = {
                    'type': 'DPIA',
                    'data': assessment_results,
                    'timestamp': assessment_results['timestamp']
                }
    except Exception as e:
        st.error(f"Error generating report: {str(e)}")
        st.warning("Try again or contact support if the issue persists.")
    
    # Important notice with modern styling
    st.markdown("""
    <div style="background-color: #e0f2fe; color: #0369a1; padding: 15px; 
              border-radius: 8px; margin-top: 20px; margin-bottom: 30px;">
        <p style="margin: 0; display: flex; align-items: center;">
            <span style="font-size: 18px; margin-right: 10px;">⚠️</span>
            <span>
                This report will not be saved automatically. Please download it now for your records.
            </span>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("New Assessment", use_container_width=True):
            reset_assessment()
            st.rerun()
    
    with col2:
        if st.button("View History", use_container_width=True):
            # Switch to history view
            st.session_state.selected_nav = _('history.title')
            st.rerun()

def reset_assessment():
    """Reset the assessment state to start a new one."""
    if 'gdpr_dpia_step' in st.session_state:
        del st.session_state.gdpr_dpia_step
    if 'gdpr_dpia_answers' in st.session_state:
        del st.session_state.gdpr_dpia_answers
    if 'gdpr_dpia_form_submitted' in st.session_state:
        del st.session_state.gdpr_dpia_form_submitted
    if 'dpia_results' in st.session_state:
        del st.session_state.dpia_results
    if 'dpia_report_data' in st.session_state:
        del st.session_state.dpia_report_data

if __name__ == "__main__":
    run_gdpr_7step_dpia()