"""
🇳🇱 Netherlands DPIA Assessment Interface

Comprehensive DPIA assessment interface for Netherlands jurisdiction with:
- GDPR compliance
- Dutch UAVG implementation  
- Dutch Police Act compliance
- Database storage and HTML report generation
"""

import streamlit as st
from datetime import datetime
from services.nl_dpia_service import NetherlandsDPIAService
from services.nl_dpia_html_generator import NetherlandsDPIAHTMLGenerator

def run_netherlands_dpia_assessment():
    """Main interface for Netherlands DPIA assessment."""
    
    # Initialize services
    dpia_service = NetherlandsDPIAService()
    html_generator = NetherlandsDPIAHTMLGenerator()
    
    # Header with Dutch flag and professional styling
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
                padding: 30px; border-radius: 10px; text-align: center; color: white; margin-bottom: 30px;">
        <h1>🇳🇱 Netherlands DPIA Assessment</h1>
        <h3>GDPR • Dutch UAVG • Police Act Compliance</h3>
        <p>Comprehensive Data Protection Impact Assessment for Netherlands Jurisdiction</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress tracking
    if 'nl_dpia_step' not in st.session_state:
        st.session_state.nl_dpia_step = 1
    
    if 'nl_dpia_assessment_id' not in st.session_state:
        st.session_state.nl_dpia_assessment_id = None
    
    # Progress bar
    total_steps = 8
    progress = (st.session_state.nl_dpia_step - 1) / total_steps
    st.progress(progress)
    st.markdown(f"**Step {st.session_state.nl_dpia_step} of {total_steps}**")
    
    # Navigation
    if st.session_state.nl_dpia_step == 1:
        step_1_organization_info(dpia_service)
    elif st.session_state.nl_dpia_step == 2:
        step_2_processing_description(dpia_service)
    elif st.session_state.nl_dpia_step == 3:
        step_3_legal_basis(dpia_service)
    elif st.session_state.nl_dpia_step == 4:
        step_4_risk_assessment(dpia_service)
    elif st.session_state.nl_dpia_step == 5:
        step_5_technical_measures(dpia_service)
    elif st.session_state.nl_dpia_step == 6:
        step_6_dutch_compliance(dpia_service)
    elif st.session_state.nl_dpia_step == 7:
        step_7_mitigation_measures(dpia_service)
    elif st.session_state.nl_dpia_step == 8:
        step_8_final_assessment(dpia_service, html_generator)

def step_1_organization_info(dpia_service: NetherlandsDPIAService):
    """Step 1: Organization Information"""
    st.subheader("1. Organization Information")
    st.markdown("Provide details about your organization and its data protection framework.")
    
    with st.form("nl_dpia_step1"):
        col1, col2 = st.columns(2)
        
        with col1:
            org_name = st.text_input(
                "Organization Name *", 
                placeholder="Enter your organization name",
                help="Full legal name of your organization"
            )
            
            dpo_contact = st.text_input(
                "Data Protection Officer Contact", 
                placeholder="DPO email or phone",
                help="Contact information for your DPO (if appointed)"
            )
            
            industry = st.selectbox(
                "Industry Sector *", 
                [
                    "Government/Public Sector",
                    "Healthcare", 
                    "Financial Services",
                    "Education",
                    "Technology/IT",
                    "Law Enforcement",
                    "Municipal Services",
                    "Telecommunications",
                    "Research",
                    "Other"
                ],
                help="Primary industry sector of your organization"
            )
        
        with col2:
            employee_count = st.selectbox(
                "Number of Employees",
                ["1-10", "11-50", "51-200", "201-1000", "1000+"],
                help="Total number of employees in your organization"
            )
            
            jurisdiction = st.selectbox(
                "Primary Jurisdiction",
                ["Netherlands", "European Union", "Other"],
                help="Primary legal jurisdiction for your organization"
            )
            
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                is_controller = st.checkbox(
                    "Data Controller", 
                    value=True,
                    help="Organization determines purposes and means of processing"
                )
            with col2_2:
                is_processor = st.checkbox(
                    "Data Processor",
                    help="Organization processes data on behalf of another controller"
                )
        
        if st.form_submit_button("Continue to Step 2", type="primary", use_container_width=True):
            if not org_name:
                st.error("Organization name is required")
                return
            
            if not industry:
                st.error("Industry sector is required")
                return
            
            # Create new assessment or update existing
            if not st.session_state.nl_dpia_assessment_id:
                assessment_id = dpia_service.create_assessment(
                    user_id=st.session_state.get('username', 'anonymous'),
                    organization_name=org_name
                )
                st.session_state.nl_dpia_assessment_id = assessment_id
            
            # Update organization info
            org_data = {
                'dpo_contact': dpo_contact,
                'industry': industry,
                'employee_count': employee_count,
                'jurisdiction': jurisdiction,
                'is_controller': is_controller,
                'is_processor': is_processor
            }
            
            success = dpia_service.update_organization_info(
                st.session_state.nl_dpia_assessment_id, 
                org_data
            )
            
            if success:
                st.session_state.nl_dpia_step = 2
                st.rerun()
            else:
                st.error("Failed to save organization information")

def step_2_processing_description(dpia_service: NetherlandsDPIAService):
    """Step 2: Data Processing Description"""
    st.subheader("2. Data Processing Description")
    st.markdown("Describe the data processing activities to be assessed.")
    
    with st.form("nl_dpia_step2"):
        purpose = st.text_area(
            "Processing Purpose *",
            placeholder="Describe the main purpose of data processing",
            help="Clear explanation of why you are processing personal data"
        )
        
        description = st.text_area(
            "Detailed Processing Description *",
            placeholder="Provide detailed description of processing activities",
            help="Comprehensive description of how personal data will be processed"
        )
        
        st.markdown("**Data Categories**")
        data_categories = st.multiselect(
            "Select categories of personal data processed:",
            [
                "Basic identification data (name, address, phone)",
                "Email addresses and contact information",
                "Financial and payment data",
                "Health and medical data",
                "Biometric data (fingerprints, facial recognition)",
                "Location and tracking data",
                "Behavioral and usage data",
                "Professional and employment data",
                "Educational records",
                "Criminal conviction and offense data",
                "Political opinions and beliefs",
                "Religious or philosophical beliefs",
                "Trade union membership",
                "Genetic data",
                "BSN (Burgerservicenummer) - Dutch Social Security Number",
                "Other sensitive personal data"
            ],
            help="Select all categories of personal data that will be processed"
        )
        
        st.markdown("**Data Subjects**")
        data_subjects = st.multiselect(
            "Select categories of data subjects:",
            [
                "Customers and clients",
                "Employees and staff",
                "Website visitors",
                "Children (under 16 years)",
                "Vulnerable adults",
                "Public officials",
                "Law enforcement subjects",
                "Healthcare patients",
                "Students",
                "Research participants",
                "Third parties",
                "Other"
            ],
            help="Select all categories of individuals whose data will be processed"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            retention_period = st.text_input(
                "Data Retention Period *",
                placeholder="e.g., 5 years, until account deletion",
                help="How long will the data be stored?"
            )
        
        with col2:
            st.markdown("**Special Processing Activities**")
            automated_decisions = st.checkbox(
                "Automated Decision Making",
                help="Processing that produces legal effects or similarly significant effects"
            )
            profiling = st.checkbox(
                "Profiling Activities",
                help="Automated processing to evaluate personal aspects"
            )
            ai_system = st.checkbox(
                "AI System Usage",
                help="Use of artificial intelligence systems"
            )
        
        col_back, col_next = st.columns(2)
        with col_back:
            if st.form_submit_button("← Back to Step 1", use_container_width=True):
                st.session_state.nl_dpia_step = 1
                st.rerun()
        
        with col_next:
            if st.form_submit_button("Continue to Step 3 →", type="primary", use_container_width=True):
                if not purpose or not description or not retention_period:
                    st.error("Purpose, description, and retention period are required")
                    return
                
                if not data_categories:
                    st.error("Please select at least one data category")
                    return
                
                if not data_subjects:
                    st.error("Please select at least one data subject category")
                    return
                
                processing_data = {
                    'purpose': purpose,
                    'description': description,
                    'data_categories': data_categories,
                    'data_subjects': data_subjects,
                    'retention_period': retention_period,
                    'automated_decisions': automated_decisions,
                    'profiling': profiling,
                    'ai_system_used': ai_system
                }
                
                success = dpia_service.update_processing_description(
                    st.session_state.nl_dpia_assessment_id,
                    processing_data
                )
                
                if success:
                    st.session_state.nl_dpia_step = 3
                    st.rerun()
                else:
                    st.error("Failed to save processing description")

def step_3_legal_basis(dpia_service: NetherlandsDPIAService):
    """Step 3: Legal Basis Analysis"""
    st.subheader("3. Legal Basis Analysis")
    st.markdown("Establish the legal basis for processing under GDPR and Dutch law.")
    
    with st.form("nl_dpia_step3"):
        gdpr_basis = st.selectbox(
            "Primary GDPR Legal Basis *",
            [
                "Consent (Article 6(1)(a))",
                "Contract (Article 6(1)(b))",
                "Legal obligation (Article 6(1)(c))",
                "Vital interests (Article 6(1)(d))",
                "Public task (Article 6(1)(e))",
                "Legitimate interests (Article 6(1)(f))"
            ],
            help="Select the primary legal basis under GDPR Article 6"
        )
        
        # Conditional fields based on legal basis
        legitimate_interest = ""
        consent_mechanism = ""
        
        if "Legitimate interests" in gdpr_basis:
            legitimate_interest = st.text_area(
                "Legitimate Interest Details *",
                placeholder="Describe the legitimate interest and balancing test performed",
                help="Explain the legitimate interest and how you balanced it against data subjects' rights"
            )
        
        if "Consent" in gdpr_basis:
            consent_mechanism = st.text_area(
                "Consent Mechanism *",
                placeholder="Describe how consent is obtained, recorded, and managed",
                help="Explain your consent collection and management process"
            )
        
        st.markdown("**Special Categories and Sensitive Data**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            special_categories = st.checkbox(
                "Special Category Data (Article 9)",
                help="Health, biometric, genetic, political, religious data etc."
            )
            children_data = st.checkbox(
                "Children's Data (under 16)",
                help="Processing data of children requires special consideration"
            )
        
        with col2:
            criminal_data = st.checkbox(
                "Criminal Conviction Data (Article 10)",
                help="Data relating to criminal convictions and offenses"
            )
            cross_border = st.checkbox(
                "Cross-border Data Transfer",
                help="Transfer of data outside the EU/EEA"
            )
        
        with col3:
            adequacy_decision = ""
            if cross_border:
                adequacy_decision = st.selectbox(
                    "Transfer Mechanism",
                    [
                        "Adequacy Decision",
                        "Standard Contractual Clauses (SCCs)",
                        "Binding Corporate Rules (BCRs)",
                        "Certification",
                        "Derogation for specific situations",
                        "Other safeguards"
                    ],
                    help="Legal mechanism for international data transfer"
                )
        
        col_back, col_next = st.columns(2)
        with col_back:
            if st.form_submit_button("← Back to Step 2", use_container_width=True):
                st.session_state.nl_dpia_step = 2
                st.rerun()
        
        with col_next:
            if st.form_submit_button("Continue to Step 4 →", type="primary", use_container_width=True):
                if not gdpr_basis:
                    st.error("GDPR legal basis is required")
                    return
                
                if "Legitimate interests" in gdpr_basis and not legitimate_interest:
                    st.error("Legitimate interest details are required")
                    return
                
                if "Consent" in gdpr_basis and not consent_mechanism:
                    st.error("Consent mechanism details are required")
                    return
                
                legal_data = {
                    'gdpr_basis': gdpr_basis,
                    'legitimate_interest': legitimate_interest,
                    'consent_mechanism': consent_mechanism,
                    'special_categories': special_categories,
                    'criminal_data': criminal_data,
                    'children_data': children_data,
                    'cross_border_transfer': cross_border,
                    'adequacy_decision': adequacy_decision
                }
                
                success = dpia_service.update_legal_basis(
                    st.session_state.nl_dpia_assessment_id,
                    legal_data
                )
                
                if success:
                    st.session_state.nl_dpia_step = 4
                    st.rerun()
                else:
                    st.error("Failed to save legal basis information")

def step_4_risk_assessment(dpia_service: NetherlandsDPIAService):
    """Step 4: Privacy Risk Assessment"""
    st.subheader("4. Privacy Risk Assessment")
    st.markdown("Identify and assess privacy risks to data subjects.")
    
    with st.form("nl_dpia_step4"):
        st.markdown("**Privacy Risks**")
        privacy_risks = st.multiselect(
            "Identify potential privacy risks:",
            [
                "Unauthorized access to personal data",
                "Data breach or data loss",
                "Discrimination or unfair treatment",
                "Surveillance or excessive monitoring",
                "Loss of control over personal data",
                "Identity theft or fraud",
                "Reputation damage",
                "Economic loss to data subjects",
                "Physical harm or safety risks",
                "Psychological distress",
                "Social exclusion or marginalization",
                "Violation of human dignity",
                "Chilling effect on freedom of expression",
                "Restriction of movement or freedom",
                "Other privacy violations"
            ],
            help="Select all potential privacy risks that could affect data subjects"
        )
        
        st.markdown("**Risk Assessment**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            breach_likelihood = st.selectbox(
                "Data Breach Likelihood",
                ["low", "medium", "high"],
                help="Probability of a data breach occurring"
            )
        
        with col2:
            breach_impact = st.selectbox(
                "Data Breach Impact",
                ["low", "medium", "high"],
                help="Potential impact if a breach occurs"
            )
        
        with col3:
            discrimination_risk = st.selectbox(
                "Discrimination Risk",
                ["low", "medium", "high"],
                help="Risk of discriminatory effects on individuals"
            )
        
        surveillance = st.checkbox(
            "Surveillance Concerns",
            help="Processing involves monitoring or surveillance of individuals"
        )
        
        st.markdown("**Vulnerable Groups**")
        vulnerable_groups = st.multiselect(
            "Select vulnerable groups that may be affected:",
            [
                "Children and minors",
                "Elderly persons",
                "Persons with disabilities",
                "Ethnic minorities",
                "Religious minorities",
                "LGBTQ+ individuals",
                "Refugees and asylum seekers",
                "Economically disadvantaged persons",
                "Mentally ill persons",
                "Employees (power imbalance)",
                "Patients (healthcare context)",
                "Students (educational context)",
                "Other vulnerable populations"
            ],
            help="Groups that may be particularly vulnerable to the identified risks"
        )
        
        col_back, col_next = st.columns(2)
        with col_back:
            if st.form_submit_button("← Back to Step 3", use_container_width=True):
                st.session_state.nl_dpia_step = 3
                st.rerun()
        
        with col_next:
            if st.form_submit_button("Continue to Step 5 →", type="primary", use_container_width=True):
                risk_data = {
                    'privacy_risks': privacy_risks,
                    'breach_likelihood': breach_likelihood,
                    'breach_impact': breach_impact,
                    'discrimination_risk': discrimination_risk,
                    'surveillance_concerns': surveillance,
                    'vulnerable_groups': vulnerable_groups,
                    'rights_impact': {}  # Could be expanded for detailed rights analysis
                }
                
                success = dpia_service.update_risk_assessment(
                    st.session_state.nl_dpia_assessment_id,
                    risk_data
                )
                
                if success:
                    st.session_state.nl_dpia_step = 5
                    st.rerun()
                else:
                    st.error("Failed to save risk assessment")

def step_5_technical_measures(dpia_service: NetherlandsDPIAService):
    """Step 5: Technical and Organizational Measures"""
    st.subheader("5. Technical & Organizational Measures")
    st.markdown("Describe security measures implemented to protect personal data.")
    
    with st.form("nl_dpia_step5"):
        st.markdown("**Technical Security Measures**")
        col1, col2 = st.columns(2)
        
        with col1:
            encryption_rest = st.checkbox(
                "Encryption at Rest",
                help="Data is encrypted when stored"
            )
            
            audit_logging = st.checkbox(
                "Audit Logging",
                help="Comprehensive logging of data access and processing"
            )
            
            data_minimization = st.checkbox(
                "Data Minimization",
                help="Only necessary data is collected and processed"
            )
            
            anonymization = st.checkbox(
                "Anonymization",
                help="Data is anonymized where possible"
            )
        
        with col2:
            encryption_transit = st.checkbox(
                "Encryption in Transit",
                help="Data is encrypted during transmission"
            )
            
            pseudonymization = st.checkbox(
                "Pseudonymization",
                help="Direct identifiers are replaced with pseudonyms"
            )
            
            staff_training = st.checkbox(
                "Staff Training Program",
                help="Regular training on data protection for staff"
            )
        
        st.markdown("**Access Controls**")
        access_controls = st.multiselect(
            "Select implemented access controls:",
            [
                "Role-based access control (RBAC)",
                "Multi-factor authentication (MFA)",
                "Regular access reviews",
                "Privileged access management",
                "Need-to-know basis access",
                "Time-limited access",
                "IP address restrictions",
                "Device-based restrictions",
                "Automated access provisioning/deprovisioning"
            ],
            help="Access control mechanisms in place"
        )
        
        st.markdown("**Organizational Measures**")
        backup_procedures = st.text_area(
            "Backup and Recovery Procedures",
            placeholder="Describe backup and disaster recovery procedures",
            help="How do you ensure data availability and recovery?"
        )
        
        incident_response = st.text_area(
            "Incident Response Plan",
            placeholder="Describe incident response and breach notification procedures",
            help="How do you handle data breaches and security incidents?"
        )
        
        col_back, col_next = st.columns(2)
        with col_back:
            if st.form_submit_button("← Back to Step 4", use_container_width=True):
                st.session_state.nl_dpia_step = 4
                st.rerun()
        
        with col_next:
            if st.form_submit_button("Continue to Step 6 →", type="primary", use_container_width=True):
                tech_data = {
                    'encryption_at_rest': encryption_rest,
                    'encryption_in_transit': encryption_transit,
                    'access_controls': access_controls,
                    'audit_logging': audit_logging,
                    'data_minimization': data_minimization,
                    'pseudonymization': pseudonymization,
                    'anonymization': anonymization,
                    'backup_procedures': backup_procedures,
                    'incident_response': incident_response,
                    'staff_training': staff_training
                }
                
                success = dpia_service.update_technical_measures(
                    st.session_state.nl_dpia_assessment_id,
                    tech_data
                )
                
                if success:
                    st.session_state.nl_dpia_step = 6
                    st.rerun()
                else:
                    st.error("Failed to save technical measures")

def step_6_dutch_compliance(dpia_service: NetherlandsDPIAService):
    """Step 6: Dutch-Specific Compliance"""
    st.subheader("6. Netherlands-Specific Compliance")
    st.markdown("Address Dutch UAVG and local regulatory requirements.")
    
    with st.form("nl_dpia_step6"):
        st.markdown("**Dutch UAVG (GDPR Implementation)**")
        col1, col2 = st.columns(2)
        
        with col1:
            uavg_compliant = st.checkbox(
                "UAVG Compliant Design",
                help="Processing designed for compliance with Dutch UAVG"
            )
            
            dpa_notification = st.checkbox(
                "Dutch DPA Notification",
                help="Notification to Dutch Data Protection Authority if required"
            )
            
            bsn_processing = st.checkbox(
                "BSN Processing",
                help="Processing of Dutch Social Security Numbers (BSN)"
            )
        
        with col2:
            municipal = st.checkbox(
                "Municipal Data Processing",
                help="Processing by or for municipal authorities"
            )
            
            healthcare_bsn = st.checkbox(
                "Healthcare BSN Processing",
                help="BSN processing in healthcare context"
            )
        
        st.markdown("**Dutch Police Act Compliance**")
        police_act = st.checkbox(
            "Police Act (Politiewet) Applicable",
            help="Processing falls under Dutch Police Act scope"
        )
        
        police_purpose = ""
        if police_act:
            police_purpose = st.text_area(
                "Police Processing Purpose *",
                placeholder="Describe the law enforcement purpose for data processing",
                help="Specific law enforcement purpose under the Police Act"
            )
        
        st.markdown("**Dutch Sector Codes**")
        sector_codes = st.multiselect(
            "Applicable Dutch sector codes and regulations:",
            [
                "Healthcare sector (WGBO, WMO)",
                "Financial services (Wft, Wwft)",
                "Education sector (WPO, WVO, WHW)",
                "Government sector (Wob, Woo)",
                "Telecommunications (Tw)",
                "Municipal services (Wabo, Wmo)",
                "Research sector (WMO, GDPR research provisions)",
                "Employment sector (WW, WWB)",
                "Insurance sector (Wvv)",
                "Other sector-specific regulations"
            ],
            help="Select applicable Dutch sector-specific data protection rules"
        )
        
        col_back, col_next = st.columns(2)
        with col_back:
            if st.form_submit_button("← Back to Step 5", use_container_width=True):
                st.session_state.nl_dpia_step = 5
                st.rerun()
        
        with col_next:
            if st.form_submit_button("Continue to Step 7 →", type="primary", use_container_width=True):
                if police_act and not police_purpose:
                    st.error("Police processing purpose is required when Police Act applies")
                    return
                
                dutch_data = {
                    'uavg_compliant': uavg_compliant,
                    'dutch_dpa_notification': dpa_notification,
                    'police_act_applicable': police_act,
                    'police_processing_purpose': police_purpose,
                    'bsn_processing': bsn_processing,
                    'dutch_sector_codes': sector_codes,
                    'municipal_processing': municipal,
                    'healthcare_bsn': healthcare_bsn
                }
                
                success = dpia_service.update_dutch_compliance(
                    st.session_state.nl_dpia_assessment_id,
                    dutch_data
                )
                
                if success:
                    st.session_state.nl_dpia_step = 7
                    st.rerun()
                else:
                    st.error("Failed to save Dutch compliance information")

def step_7_mitigation_measures(dpia_service: NetherlandsDPIAService):
    """Step 7: Mitigation Measures"""
    st.subheader("7. Mitigation Measures")
    st.markdown("Define measures to address identified risks and ensure compliance.")
    
    with st.form("nl_dpia_step7"):
        measures = st.text_area(
            "Proposed Mitigation Measures",
            placeholder="List specific measures to address identified risks (one per line)",
            help="Concrete steps to reduce privacy risks and ensure compliance",
            height=150
        )
        
        col1, col2 = st.columns(2)
        with col1:
            timeline = st.text_input(
                "Implementation Timeline",
                placeholder="e.g., 6 months, Q2 2024",
                help="When will these measures be implemented?"
            )
            
            responsible = st.text_input(
                "Responsible Parties",
                placeholder="e.g., IT Team, DPO, Management (comma-separated)",
                help="Who is responsible for implementing these measures?"
            )
        
        with col2:
            review_schedule = st.text_input(
                "Review Schedule",
                placeholder="e.g., Annual, Every 6 months",
                help="How often will you review these measures?"
            )
            
            monitoring = st.text_area(
                "Monitoring Procedures",
                placeholder="How will you monitor the effectiveness of these measures?",
                help="Ongoing monitoring and evaluation procedures"
            )
        
        col_back, col_next = st.columns(2)
        with col_back:
            if st.form_submit_button("← Back to Step 6", use_container_width=True):
                st.session_state.nl_dpia_step = 6
                st.rerun()
        
        with col_next:
            if st.form_submit_button("Complete Assessment →", type="primary", use_container_width=True):
                mitigation_data = {
                    'measures': measures.split('\n') if measures else [],
                    'implementation_timeline': timeline,
                    'responsible_parties': responsible.split(',') if responsible else [],
                    'monitoring_procedures': monitoring,
                    'review_schedule': review_schedule
                }
                
                success = dpia_service.update_mitigation_measures(
                    st.session_state.nl_dpia_assessment_id,
                    mitigation_data
                )
                
                if success:
                    st.session_state.nl_dpia_step = 8
                    st.rerun()
                else:
                    st.error("Failed to save mitigation measures")

def step_8_final_assessment(dpia_service: NetherlandsDPIAService, html_generator: NetherlandsDPIAHTMLGenerator):
    """Step 8: Final Assessment and Report Generation"""
    st.subheader("8. Final Assessment & Report Generation")
    st.markdown("Generate compliance scores and download your comprehensive DPIA report.")
    
    # Calculate compliance scores
    if st.button("Generate Final Assessment", type="primary", use_container_width=True):
        with st.spinner("Calculating compliance scores..."):
            scores = dpia_service.calculate_compliance_scores(st.session_state.nl_dpia_assessment_id)
            
            if scores:
                st.session_state.nl_dpia_scores = scores
                st.success("Assessment completed successfully!")
                st.rerun()
    
    # Display results if available
    if hasattr(st.session_state, 'nl_dpia_scores') and st.session_state.nl_dpia_scores:
        scores = st.session_state.nl_dpia_scores
        
        # Key metrics
        st.markdown("### Assessment Results")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            risk_level = scores.get('overall_risk_level', 'medium')
            risk_color = {'low': 'green', 'medium': 'orange', 'high': 'red'}.get(risk_level, 'gray')
            st.metric("Overall Risk", risk_level.upper())
        
        with col2:
            can_proceed = scores.get('can_proceed', False)
            st.metric("Can Proceed", "YES" if can_proceed else "NO")
        
        with col3:
            gdpr_score = scores.get('gdpr_score', 0)
            st.metric("GDPR Score", f"{gdpr_score}%", delta=f"{gdpr_score-80}%" if gdpr_score >= 80 else None)
        
        with col4:
            uavg_score = scores.get('uavg_score', 0)
            st.metric("UAVG Score", f"{uavg_score}%", delta=f"{uavg_score-80}%" if uavg_score >= 80 else None)
        
        # Recommendations
        recommendations = scores.get('recommendations', [])
        if recommendations:
            st.markdown("### Key Recommendations")
            for i, rec in enumerate(recommendations[:5], 1):
                priority_color = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
                priority = rec.get('priority', 'medium')
                st.write(f"{priority_color.get(priority, '🔵')} **{rec.get('category')}**: {rec.get('recommendation')}")
        
        # Generate HTML report
        st.markdown("### Download Report")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Generate HTML Report", type="secondary", use_container_width=True):
                with st.spinner("Generating HTML report..."):
                    try:
                        # Get complete assessment data
                        assessment_data = dpia_service.get_assessment(st.session_state.nl_dpia_assessment_id)
                        
                        if assessment_data:
                            # Generate HTML report
                            report_path = html_generator.generate_html_report(assessment_data)
                            report_url = html_generator.get_report_url(report_path)
                            
                            # Update database with report info
                            import psycopg2
                            with psycopg2.connect(dpia_service.db_url) as conn:
                                with conn.cursor() as cur:
                                    cur.execute("""
                                        UPDATE nl_dpia_assessments 
                                        SET html_report_generated = TRUE,
                                            html_report_path = %s,
                                            html_report_url = %s,
                                            report_generated_at = CURRENT_TIMESTAMP
                                        WHERE assessment_id = %s
                                    """, (report_path, report_url, st.session_state.nl_dpia_assessment_id))
                                    conn.commit()
                            
                            st.success("HTML report generated successfully!")
                            st.session_state.nl_dpia_report_url = report_url
                            st.session_state.nl_dpia_report_path = report_path
                            
                        else:
                            st.error("Failed to retrieve assessment data")
                            
                    except Exception as e:
                        st.error(f"Failed to generate report: {str(e)}")
        
        with col2:
            # Download button for HTML report
            if hasattr(st.session_state, 'nl_dpia_report_path') and st.session_state.nl_dpia_report_path:
                try:
                    with open(st.session_state.nl_dpia_report_path, 'r', encoding='utf-8') as file:
                        html_content = file.read()
                    
                    st.download_button(
                        label="Download HTML Report",
                        data=html_content,
                        file_name=f"NL_DPIA_Report_{st.session_state.nl_dpia_assessment_id}.html",
                        mime="text/html",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Failed to prepare download: {str(e)}")
        
        # Report URL for sharing
        if hasattr(st.session_state, 'nl_dpia_report_url') and st.session_state.nl_dpia_report_url:
            st.markdown("### Report Access URL")
            st.code(f"https://your-domain.com{st.session_state.nl_dpia_report_url}", language="text")
            st.info("Share this URL to provide access to the HTML report")
        
        # New assessment button
        st.markdown("---")
        if st.button("Start New Assessment", use_container_width=True):
            # Clear session state
            keys_to_clear = [k for k in st.session_state.keys() if k.startswith('nl_dpia')]
            for key in keys_to_clear:
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    run_netherlands_dpia_assessment()