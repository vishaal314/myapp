"""
Enhanced DPIA Assessment - New UI Implementation

This module provides a modern, enhanced DPIA assessment interface with:
- Improved visual design and user experience
- Progress tracking with visual indicators
- Enhanced form validation and error handling
- Real-time assessment scoring
- Professional report generation
- Database integration for storing assessments
"""

import streamlit as st
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List
import psycopg2
import os

# Import existing services
try:
    from services.dpia_scanner import DPIAScanner
    from services.nl_dpia_html_generator import NLDPIAHTMLGenerator
except ImportError:
    # Fallback if services not available
    class DPIAScanner:
        def perform_assessment(self, data): return {"risk_level": "Medium", "findings": [], "recommendations": []}
    class NLDDPIAHTMLGenerator:
        def generate_html_report(self, data): return "<html><body>Report</body></html>"

def init_db_connection():
    """Initialize database connection for saving assessments"""
    try:
        DATABASE_URL = os.environ.get('DATABASE_URL')
        if DATABASE_URL:
            return psycopg2.connect(DATABASE_URL)
        return None
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        return None

def save_assessment_to_db(assessment_data):
    """Save assessment results to database"""
    try:
        conn = init_db_connection()
        if conn:
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dpia_assessments (
                    id SERIAL PRIMARY KEY,
                    assessment_id VARCHAR(255) UNIQUE,
                    project_name VARCHAR(255),
                    created_date TIMESTAMP,
                    assessment_data JSONB,
                    risk_level VARCHAR(50),
                    compliance_status VARCHAR(100)
                )
            """)
            
            # Insert assessment
            cursor.execute("""
                INSERT INTO dpia_assessments 
                (assessment_id, project_name, created_date, assessment_data, risk_level, compliance_status)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (assessment_id) DO UPDATE SET
                    assessment_data = EXCLUDED.assessment_data,
                    risk_level = EXCLUDED.risk_level,
                    compliance_status = EXCLUDED.compliance_status
            """, (
                assessment_data.get('assessment_id'),
                assessment_data.get('project_name', 'Unknown'),
                datetime.now(),
                assessment_data,
                assessment_data.get('risk_level', 'Medium'),
                assessment_data.get('compliance_status', 'Under Review')
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
    except Exception as e:
        st.error(f"Error saving to database: {str(e)}")
        return False

def run_enhanced_dpia():
    """Main function for the enhanced DPIA assessment"""
    
    # Custom CSS for enhanced styling
    st.markdown("""
    <style>
    .dpia-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .step-indicator {
        display: flex;
        justify-content: space-between;
        margin: 2rem 0;
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 10px;
    }
    
    .step-circle {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
    }
    
    .step-active {
        background-color: #667eea;
    }
    
    .step-completed {
        background-color: #28a745;
    }
    
    .step-inactive {
        background-color: #6c757d;
    }
    
    .risk-card {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid;
    }
    
    .risk-high {
        border-left-color: #dc3545;
        background-color: #f8d7da;
    }
    
    .risk-medium {
        border-left-color: #ffc107;
        background-color: #fff3cd;
    }
    
    .risk-low {
        border-left-color: #28a745;
        background-color: #d4edda;
    }
    
    .assessment-form {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .progress-bar {
        height: 20px;
        background-color: #e9ecef;
        border-radius: 10px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        transition: width 0.3s ease;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'enhanced_dpia_step' not in st.session_state:
        st.session_state.enhanced_dpia_step = 1
        st.session_state.enhanced_dpia_data = {}
        st.session_state.enhanced_dpia_answers = {f'step{i}': {} for i in range(1, 8)}
        st.session_state.enhanced_dpia_score = 0
    
    # Header
    st.markdown("""
    <div class="dpia-header">
        <h1>🛡️ Enhanced DPIA Assessment</h1>
        <p>Comprehensive Data Protection Impact Assessment</p>
        <p><strong>GDPR Compliant • Netherlands Jurisdiction • EU Standards</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress indicator
    progress_percentage = (st.session_state.enhanced_dpia_step - 1) / 7 * 100
    st.markdown(f"""
    <div class="progress-bar">
        <div class="progress-fill" style="width: {progress_percentage}%"></div>
    </div>
    <p style="text-align: center; margin-top: 0.5rem;">
        <strong>Step {st.session_state.enhanced_dpia_step} of 7</strong> • {progress_percentage:.0f}% Complete
    </p>
    """, unsafe_allow_html=True)
    
    # Step indicators
    st.markdown("""
    <div class="step-indicator">
        <div class="step-circle step-active" style="background-color: #667eea;">1</div>
        <div class="step-circle" style="background-color: #6c757d;">2</div>
        <div class="step-circle" style="background-color: #6c757d;">3</div>
        <div class="step-circle" style="background-color: #6c757d;">4</div>
        <div class="step-circle" style="background-color: #6c757d;">5</div>
        <div class="step-circle" style="background-color: #6c757d;">6</div>
        <div class="step-circle" style="background-color: #6c757d;">7</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Step routing
    if st.session_state.enhanced_dpia_step == 1:
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
    elif st.session_state.enhanced_dpia_step == 8:
        display_enhanced_results()
    
    # Sidebar with assessment summary
    with st.sidebar:
        st.markdown("### Assessment Summary")
        st.markdown(f"**Current Step:** {st.session_state.enhanced_dpia_step}/7")
        st.markdown(f"**Progress:** {progress_percentage:.0f}%")
        
        if st.session_state.enhanced_dpia_data.get('project_name'):
            st.markdown(f"**Project:** {st.session_state.enhanced_dpia_data['project_name']}")
        
        if st.session_state.enhanced_dpia_score > 0:
            st.markdown(f"**Current Score:** {st.session_state.enhanced_dpia_score}/100")
        
        st.markdown("---")
        st.markdown("### Quick Actions")
        if st.button("🔄 Restart Assessment", key="restart_enhanced"):
            for key in list(st.session_state.keys()):
                if key.startswith('enhanced_dpia'):
                    del st.session_state[key]
            st.rerun()

def handle_enhanced_step1():
    """Enhanced Step 1: Project Overview"""
    st.markdown("### 📋 Step 1: Project Overview")
    st.markdown("Let's start by understanding your project and its data processing activities.")
    
    with st.container():
        st.markdown('<div class="assessment-form">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input(
                "🏷️ Project Name",
                value=st.session_state.enhanced_dpia_answers['step1'].get('project_name', ''),
                placeholder="Enter your project name",
                help="Provide a clear, descriptive name for your project"
            )
            
            project_type = st.selectbox(
                "📊 Project Type",
                options=[
                    "Web Application",
                    "Mobile Application", 
                    "Data Analytics Platform",
                    "AI/ML System",
                    "Database System",
                    "IoT Solution",
                    "Marketing Campaign",
                    "HR System",
                    "Other"
                ],
                index=0 if not st.session_state.enhanced_dpia_answers['step1'].get('project_type') else 
                      ["Web Application", "Mobile Application", "Data Analytics Platform", "AI/ML System", 
                       "Database System", "IoT Solution", "Marketing Campaign", "HR System", "Other"].index(
                           st.session_state.enhanced_dpia_answers['step1'].get('project_type', "Web Application")
                       )
            )
        
        with col2:
            organization = st.text_input(
                "🏢 Organization",
                value=st.session_state.enhanced_dpia_answers['step1'].get('organization', ''),
                placeholder="Your organization name"
            )
            
            launch_date = st.date_input(
                "📅 Planned Launch Date",
                value=datetime.now().date(),
                help="When do you plan to launch this project?"
            )
        
        project_description = st.text_area(
            "📝 Project Description",
            value=st.session_state.enhanced_dpia_answers['step1'].get('project_description', ''),
            placeholder="Describe your project, its purpose, and main functionality...",
            height=100,
            help="Provide a comprehensive description of your project"
        )
        
        processing_purposes = st.multiselect(
            "🎯 Main Processing Purposes",
            options=[
                "Service Delivery",
                "Customer Support",
                "Marketing & Communication",
                "Analytics & Insights",
                "Security & Fraud Prevention",
                "Legal Compliance",
                "Research & Development",
                "Personnel Management",
                "Financial Management",
                "Other"
            ],
            default=st.session_state.enhanced_dpia_answers['step1'].get('processing_purposes', []),
            help="Select all applicable purposes"
        )
        
        # Real-time validation
        validation_errors = []
        if not project_name:
            validation_errors.append("Project name is required")
        if not project_description:
            validation_errors.append("Project description is required")
        if not processing_purposes:
            validation_errors.append("At least one processing purpose must be selected")
        
        if validation_errors:
            for error in validation_errors:
                st.error(f"⚠️ {error}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Navigation
        col1, col2, col3 = st.columns([1, 1, 1])
        with col3:
            if st.button("Continue to Step 2 →", type="primary", disabled=bool(validation_errors)):
                # Save data
                st.session_state.enhanced_dpia_answers['step1'] = {
                    'project_name': project_name,
                    'project_type': project_type,
                    'organization': organization,
                    'launch_date': launch_date.isoformat(),
                    'project_description': project_description,
                    'processing_purposes': processing_purposes
                }
                st.session_state.enhanced_dpia_data['project_name'] = project_name
                st.session_state.enhanced_dpia_step = 2
                st.rerun()

def handle_enhanced_step2():
    """Enhanced Step 2: Data Categories"""
    st.markdown("### 🗂️ Step 2: Data Categories")
    st.markdown("Identify the types of personal data your project will process.")
    
    with st.container():
        st.markdown('<div class="assessment-form">', unsafe_allow_html=True)
        
        st.markdown("#### Personal Data Categories")
        
        # Data categories with risk indicators
        data_categories = {}
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Basic Personal Data**")
            data_categories['basic_identifiers'] = st.checkbox(
                "📧 Basic Identifiers (name, email, phone)",
                value=st.session_state.enhanced_dpia_answers['step2'].get('basic_identifiers', False)
            )
            data_categories['contact_info'] = st.checkbox(
                "📍 Contact Information",
                value=st.session_state.enhanced_dpia_answers['step2'].get('contact_info', False)
            )
            data_categories['demographic'] = st.checkbox(
                "👥 Demographic Data (age, gender)",
                value=st.session_state.enhanced_dpia_answers['step2'].get('demographic', False)
            )
            data_categories['preferences'] = st.checkbox(
                "⚙️ User Preferences",
                value=st.session_state.enhanced_dpia_answers['step2'].get('preferences', False)
            )
            
            st.markdown("**Technical Data**")
            data_categories['technical'] = st.checkbox(
                "💻 Technical Data (IP, device info)",
                value=st.session_state.enhanced_dpia_answers['step2'].get('technical', False)
            )
            data_categories['usage'] = st.checkbox(
                "📊 Usage Data & Analytics",
                value=st.session_state.enhanced_dpia_answers['step2'].get('usage', False)
            )
        
        with col2:
            st.markdown("**Sensitive Categories** ⚠️")
            data_categories['financial'] = st.checkbox(
                "💳 Financial Data",
                value=st.session_state.enhanced_dpia_answers['step2'].get('financial', False),
                help="Credit cards, bank details, payment info"
            )
            data_categories['health'] = st.checkbox(
                "🏥 Health Data",
                value=st.session_state.enhanced_dpia_answers['step2'].get('health', False),
                help="Medical records, health status"
            )
            data_categories['biometric'] = st.checkbox(
                "👆 Biometric Data",
                value=st.session_state.enhanced_dpia_answers['step2'].get('biometric', False),
                help="Fingerprints, facial recognition"
            )
            data_categories['location'] = st.checkbox(
                "📍 Location Data",
                value=st.session_state.enhanced_dpia_answers['step2'].get('location', False),
                help="GPS coordinates, tracking data"
            )
            data_categories['children'] = st.checkbox(
                "👶 Children's Data (under 16)",
                value=st.session_state.enhanced_dpia_answers['step2'].get('children', False),
                help="Data from minors requires special protection"
            )
            data_categories['criminal'] = st.checkbox(
                "⚖️ Criminal Records",
                value=st.session_state.enhanced_dpia_answers['step2'].get('criminal', False)
            )
        
        # Data subjects
        st.markdown("#### Data Subjects")
        data_subjects = st.multiselect(
            "👥 Who are the data subjects?",
            options=[
                "Customers/Clients",
                "Website Visitors", 
                "Employees",
                "Job Applicants",
                "Business Partners",
                "Suppliers",
                "Children (under 16)",
                "Vulnerable Adults",
                "General Public",
                "Other"
            ],
            default=st.session_state.enhanced_dpia_answers['step2'].get('data_subjects', []),
            help="Select all applicable data subject categories"
        )
        
        # Volume estimation
        st.markdown("#### Processing Volume")
        data_volume = st.select_slider(
            "📈 Estimated number of data subjects",
            options=[
                "< 100",
                "100 - 1,000", 
                "1,000 - 10,000",
                "10,000 - 100,000",
                "100,000 - 1M",
                "> 1M"
            ],
            value=st.session_state.enhanced_dpia_answers['step2'].get('data_volume', "< 100")
        )
        
        # Calculate risk score for this step
        risk_score = calculate_step2_risk_score(data_categories, data_subjects, data_volume)
        
        # Risk indicator
        if risk_score >= 70:
            risk_class = "risk-high"
            risk_text = "High Risk"
            risk_color = "#dc3545"
        elif risk_score >= 40:
            risk_class = "risk-medium" 
            risk_text = "Medium Risk"
            risk_color = "#ffc107"
        else:
            risk_class = "risk-low"
            risk_text = "Low Risk"
            risk_color = "#28a745"
        
        st.markdown(f"""
        <div class="risk-card {risk_class}">
            <strong>Current Risk Level: {risk_text}</strong> (Score: {risk_score}/100)
            <br><small>Based on data categories and volume selected</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Navigation
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("← Back to Step 1"):
                st.session_state.enhanced_dpia_step = 1
                st.rerun()
        with col3:
            can_continue = any(data_categories.values()) and data_subjects
            if st.button("Continue to Step 3 →", type="primary", disabled=not can_continue):
                # Save data
                st.session_state.enhanced_dpia_answers['step2'] = {
                    **data_categories,
                    'data_subjects': data_subjects,
                    'data_volume': data_volume,
                    'risk_score': risk_score
                }
                st.session_state.enhanced_dpia_score += risk_score
                st.session_state.enhanced_dpia_step = 3
                st.rerun()

def calculate_step2_risk_score(data_categories, data_subjects, data_volume):
    """Calculate risk score for Step 2"""
    score = 0
    
    # Basic data adds minimal risk
    basic_categories = ['basic_identifiers', 'contact_info', 'demographic', 'preferences']
    for cat in basic_categories:
        if data_categories.get(cat):
            score += 5
    
    # Technical data adds moderate risk
    if data_categories.get('technical'):
        score += 10
    if data_categories.get('usage'):
        score += 10
    
    # Sensitive data adds high risk
    sensitive_categories = ['financial', 'health', 'biometric', 'location', 'children', 'criminal']
    for cat in sensitive_categories:
        if data_categories.get(cat):
            score += 15
    
    # Volume multiplier
    volume_multipliers = {
        "< 100": 1.0,
        "100 - 1,000": 1.1,
        "1,000 - 10,000": 1.2,
        "10,000 - 100,000": 1.4,
        "100,000 - 1M": 1.6,
        "> 1M": 2.0
    }
    
    score *= volume_multipliers.get(data_volume, 1.0)
    
    # Vulnerable subjects add extra risk
    if 'Children (under 16)' in data_subjects:
        score += 20
    if 'Vulnerable Adults' in data_subjects:
        score += 15
    
    return min(int(score), 100)

def handle_enhanced_step3():
    """Enhanced Step 3: Legal Basis & Compliance"""
    st.markdown("### ⚖️ Step 3: Legal Basis & Compliance")
    st.markdown("Establish the legal foundation for your data processing activities.")
    
    with st.container():
        st.markdown('<div class="assessment-form">', unsafe_allow_html=True)
        
        # Legal basis selection
        st.markdown("#### GDPR Article 6 Legal Basis")
        legal_basis = st.radio(
            "Select the primary legal basis for processing:",
            options=[
                "Consent - Data subject has given clear consent",
                "Contract - Processing necessary for contract performance", 
                "Legal Obligation - Required by law",
                "Vital Interests - Protecting life or health",
                "Public Task - Official authority or public interest",
                "Legitimate Interests - Balanced against data subject rights"
            ],
            index=0 if not st.session_state.enhanced_dpia_answers['step3'].get('legal_basis') else
                  ["Consent - Data subject has given clear consent",
                   "Contract - Processing necessary for contract performance", 
                   "Legal Obligation - Required by law",
                   "Vital Interests - Protecting life or health",
                   "Public Task - Official authority or public interest",
                   "Legitimate Interests - Balanced against data subject rights"].index(
                       st.session_state.enhanced_dpia_answers['step3'].get('legal_basis', "Consent - Data subject has given clear consent")
                   )
        )
        
        # Special category basis if needed
        has_special_categories = any([
            st.session_state.enhanced_dpia_answers['step2'].get('health', False),
            st.session_state.enhanced_dpia_answers['step2'].get('biometric', False),
            st.session_state.enhanced_dpia_answers['step2'].get('criminal', False)
        ])
        
        special_category_basis = None
        if has_special_categories:
            st.markdown("#### GDPR Article 9 - Special Categories")
            st.warning("⚠️ You selected special category data. Additional legal basis required.")
            special_category_basis = st.selectbox(
                "Select Article 9 basis:",
                options=[
                    "Explicit consent",
                    "Employment/social security law",
                    "Vital interests (life or death)",
                    "Public interest in public health",
                    "Archiving/research/statistics",
                    "Other legal basis"
                ]
            )
        
        # Compliance assessments
        st.markdown("#### Compliance Assessments")
        
        col1, col2 = st.columns(2)
        
        with col1:
            necessity_justified = st.radio(
                "Is the processing necessary?",
                options=["Yes, fully justified", "Partially justified", "Not yet assessed"],
                index=0 if not st.session_state.enhanced_dpia_answers['step3'].get('necessity_justified') else
                      ["Yes, fully justified", "Partially justified", "Not yet assessed"].index(
                          st.session_state.enhanced_dpia_answers['step3'].get('necessity_justified', "Not yet assessed")
                      )
            )
            
            proportionality_assessed = st.radio(
                "Is the processing proportionate?",
                options=["Yes, proportionate", "Partially proportionate", "Not yet assessed"],
                index=0 if not st.session_state.enhanced_dpia_answers['step3'].get('proportionality_assessed') else
                      ["Yes, proportionate", "Partially proportionate", "Not yet assessed"].index(
                          st.session_state.enhanced_dpia_answers['step3'].get('proportionality_assessed', "Not yet assessed")
                      )
            )
        
        with col2:
            data_minimization = st.radio(
                "Data minimization applied?",
                options=["Yes, minimal data only", "Partially applied", "Not yet applied"],
                index=0 if not st.session_state.enhanced_dpia_answers['step3'].get('data_minimization') else
                      ["Yes, minimal data only", "Partially applied", "Not yet applied"].index(
                          st.session_state.enhanced_dpia_answers['step3'].get('data_minimization', "Not yet applied")
                      )
            )
            
            purpose_limitation = st.radio(
                "Purpose limitation respected?",
                options=["Yes, single clear purpose", "Multiple related purposes", "Not yet defined"],
                index=0 if not st.session_state.enhanced_dpia_answers['step3'].get('purpose_limitation') else
                      ["Yes, single clear purpose", "Multiple related purposes", "Not yet defined"].index(
                          st.session_state.enhanced_dpia_answers['step3'].get('purpose_limitation', "Not yet defined")
                      )
            )
        
        # Retention period
        retention_period = st.text_input(
            "📅 Data retention period",
            value=st.session_state.enhanced_dpia_answers['step3'].get('retention_period', ''),
            placeholder="e.g., 2 years, Until contract ends, 30 days",
            help="How long will you keep the personal data?"
        )
        
        # International transfers
        international_transfers = st.checkbox(
            "🌍 International data transfers involved",
            value=st.session_state.enhanced_dpia_answers['step3'].get('international_transfers', False)
        )
        
        transfer_mechanism = None
        if international_transfers:
            transfer_mechanism = st.selectbox(
                "Transfer mechanism:",
                options=[
                    "Adequacy decision",
                    "Standard Contractual Clauses (SCCs)",
                    "Binding Corporate Rules (BCRs)",
                    "Derogations",
                    "Other"
                ]
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Navigation
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("← Back to Step 2"):
                st.session_state.enhanced_dpia_step = 2
                st.rerun()
        with col3:
            can_continue = legal_basis and necessity_justified and retention_period
            if st.button("Continue to Step 4 →", type="primary", disabled=not can_continue):
                # Save data
                st.session_state.enhanced_dpia_answers['step3'] = {
                    'legal_basis': legal_basis,
                    'special_category_basis': special_category_basis,
                    'necessity_justified': necessity_justified,
                    'proportionality_assessed': proportionality_assessed,
                    'data_minimization': data_minimization,
                    'purpose_limitation': purpose_limitation,
                    'retention_period': retention_period,
                    'international_transfers': international_transfers,
                    'transfer_mechanism': transfer_mechanism
                }
                st.session_state.enhanced_dpia_step = 4
                st.rerun()

def handle_enhanced_step4():
    """Enhanced Step 4: Risk Assessment"""
    st.markdown("### ⚠️ Step 4: Risk Assessment")
    st.markdown("Identify and evaluate privacy risks to individuals.")
    
    with st.container():
        st.markdown('<div class="assessment-form">', unsafe_allow_html=True)
        
        # Risk identification
        st.markdown("#### Identified Risks")
        
        # Predefined risk categories with checkboxes
        risk_categories = {}
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Data Security Risks**")
            risk_categories['data_breach'] = st.checkbox(
                "🔓 Data breach/unauthorized access",
                value=st.session_state.enhanced_dpia_answers['step4'].get('data_breach', False)
            )
            risk_categories['data_loss'] = st.checkbox(
                "💾 Data loss/corruption",
                value=st.session_state.enhanced_dpia_answers['step4'].get('data_loss', False)
            )
            risk_categories['insider_threat'] = st.checkbox(
                "👤 Insider threats",
                value=st.session_state.enhanced_dpia_answers['step4'].get('insider_threat', False)
            )
            
            st.markdown("**Processing Risks**")
            risk_categories['excessive_processing'] = st.checkbox(
                "📊 Excessive data processing",
                value=st.session_state.enhanced_dpia_answers['step4'].get('excessive_processing', False)
            )
            risk_categories['purpose_creep'] = st.checkbox(
                "🎯 Purpose creep/function creep",
                value=st.session_state.enhanced_dpia_answers['step4'].get('purpose_creep', False)
            )
            risk_categories['automated_decisions'] = st.checkbox(
                "🤖 Automated decision-making",
                value=st.session_state.enhanced_dpia_answers['step4'].get('automated_decisions', False)
            )
        
        with col2:
            st.markdown("**Individual Rights Risks**")
            risk_categories['consent_issues'] = st.checkbox(
                "✋ Consent management issues",
                value=st.session_state.enhanced_dpia_answers['step4'].get('consent_issues', False)
            )
            risk_categories['access_rights'] = st.checkbox(
                "🔍 Difficulty exercising access rights",
                value=st.session_state.enhanced_dpia_answers['step4'].get('access_rights', False)
            )
            risk_categories['transparency'] = st.checkbox(
                "👁️ Lack of transparency",
                value=st.session_state.enhanced_dpia_answers['step4'].get('transparency', False)
            )
            
            st.markdown("**Compliance Risks**")
            risk_categories['regulatory_changes'] = st.checkbox(
                "📋 Regulatory compliance gaps",
                value=st.session_state.enhanced_dpia_answers['step4'].get('regulatory_changes', False)
            )
            risk_categories['cross_border'] = st.checkbox(
                "🌍 Cross-border transfer risks",
                value=st.session_state.enhanced_dpia_answers['step4'].get('cross_border', False)
            )
        
        # Custom risks
        custom_risks = st.text_area(
            "📝 Additional risks identified",
            value=st.session_state.enhanced_dpia_answers['step4'].get('custom_risks', ''),
            placeholder="Describe any other privacy risks specific to your project...",
            height=100
        )
        
        # Risk assessment matrix
        st.markdown("#### Risk Assessment Matrix")
        
        likelihood = st.select_slider(
            "📈 Overall likelihood of risks occurring",
            options=["Very Low", "Low", "Medium", "High", "Very High"],
            value=st.session_state.enhanced_dpia_answers['step4'].get('likelihood', "Medium")
        )
        
        impact = st.select_slider(
            "💥 Potential impact on individuals",
            options=["Very Low", "Low", "Medium", "High", "Very High"],
            value=st.session_state.enhanced_dpia_answers['step4'].get('impact', "Medium")
        )
        
        # Calculate overall risk level
        risk_matrix = {
            "Very Low": 1, "Low": 2, "Medium": 3, "High": 4, "Very High": 5
        }
        
        risk_score = risk_matrix[likelihood] * risk_matrix[impact]
        
        if risk_score >= 20:
            overall_risk = "Very High"
            risk_class = "risk-high"
        elif risk_score >= 12:
            overall_risk = "High"
            risk_class = "risk-high"
        elif risk_score >= 6:
            overall_risk = "Medium"
            risk_class = "risk-medium"
        elif risk_score >= 3:
            overall_risk = "Low"
            risk_class = "risk-low"
        else:
            overall_risk = "Very Low"
            risk_class = "risk-low"
        
        st.markdown(f"""
        <div class="risk-card {risk_class}">
            <strong>Overall Risk Level: {overall_risk}</strong>
            <br>Likelihood: {likelihood} × Impact: {impact} = Score: {risk_score}/25
        </div>
        """, unsafe_allow_html=True)
        
        # Risk tolerance
        risk_tolerance = st.radio(
            "🎯 Organization's risk tolerance for this project",
            options=["Low tolerance", "Medium tolerance", "High tolerance"],
            index=0 if not st.session_state.enhanced_dpia_answers['step4'].get('risk_tolerance') else
                  ["Low tolerance", "Medium tolerance", "High tolerance"].index(
                      st.session_state.enhanced_dpia_answers['step4'].get('risk_tolerance', "Medium tolerance")
                  )
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Navigation
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("← Back to Step 3"):
                st.session_state.enhanced_dpia_step = 3
                st.rerun()
        with col3:
            can_continue = any(risk_categories.values()) or custom_risks
            if st.button("Continue to Step 5 →", type="primary", disabled=not can_continue):
                # Save data
                st.session_state.enhanced_dpia_answers['step4'] = {
                    **risk_categories,
                    'custom_risks': custom_risks,
                    'likelihood': likelihood,
                    'impact': impact,
                    'overall_risk': overall_risk,
                    'risk_score': risk_score,
                    'risk_tolerance': risk_tolerance
                }
                st.session_state.enhanced_dpia_step = 5
                st.rerun()

def handle_enhanced_step5():
    """Enhanced Step 5: Mitigation Measures"""
    st.markdown("### 🛡️ Step 5: Mitigation Measures")
    st.markdown("Implement measures to reduce identified risks.")
    
    with st.container():
        st.markdown('<div class="assessment-form">', unsafe_allow_html=True)
        
        # Get risks from previous step
        identified_risks = st.session_state.enhanced_dpia_answers.get('step4', {})
        
        st.markdown("#### Technical Measures")
        
        technical_measures = {}
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Data Protection**")
            technical_measures['encryption'] = st.checkbox(
                "🔐 Data encryption (in transit and at rest)",
                value=st.session_state.enhanced_dpia_answers['step5'].get('encryption', False)
            )
            technical_measures['pseudonymization'] = st.checkbox(
                "🎭 Pseudonymization/anonymization",
                value=st.session_state.enhanced_dpia_answers['step5'].get('pseudonymization', False)
            )
            technical_measures['access_controls'] = st.checkbox(
                "🔑 Access controls and authentication",
                value=st.session_state.enhanced_dpia_answers['step5'].get('access_controls', False)
            )
            technical_measures['data_minimization_tech'] = st.checkbox(
                "📊 Automated data minimization",
                value=st.session_state.enhanced_dpia_answers['step5'].get('data_minimization_tech', False)
            )
        
        with col2:
            st.markdown("**System Security**")
            technical_measures['security_monitoring'] = st.checkbox(
                "👁️ Security monitoring/logging",
                value=st.session_state.enhanced_dpia_answers['step5'].get('security_monitoring', False)
            )
            technical_measures['backup_recovery'] = st.checkbox(
                "💾 Backup and recovery procedures",
                value=st.session_state.enhanced_dpia_answers['step5'].get('backup_recovery', False)
            )
            technical_measures['vulnerability_management'] = st.checkbox(
                "🔍 Vulnerability management",
                value=st.session_state.enhanced_dpia_answers['step5'].get('vulnerability_management', False)
            )
            technical_measures['secure_deletion'] = st.checkbox(
                "🗑️ Secure deletion procedures",
                value=st.session_state.enhanced_dpia_answers['step5'].get('secure_deletion', False)
            )
        
        st.markdown("#### Organizational Measures")
        
        organizational_measures = {}
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Governance & Training**")
            organizational_measures['privacy_policies'] = st.checkbox(
                "📋 Privacy policies and procedures",
                value=st.session_state.enhanced_dpia_answers['step5'].get('privacy_policies', False)
            )
            organizational_measures['staff_training'] = st.checkbox(
                "🎓 Staff privacy training",
                value=st.session_state.enhanced_dpia_answers['step5'].get('staff_training', False)
            )
            organizational_measures['dpo_appointment'] = st.checkbox(
                "👤 Data Protection Officer (DPO)",
                value=st.session_state.enhanced_dpia_answers['step5'].get('dpo_appointment', False)
            )
            organizational_measures['privacy_by_design'] = st.checkbox(
                "🏗️ Privacy by design processes",
                value=st.session_state.enhanced_dpia_answers['step5'].get('privacy_by_design', False)
            )
        
        with col2:
            st.markdown("**Monitoring & Response**")
            organizational_measures['regular_audits'] = st.checkbox(
                "🔍 Regular privacy audits",
                value=st.session_state.enhanced_dpia_answers['step5'].get('regular_audits', False)
            )
            organizational_measures['incident_response'] = st.checkbox(
                "🚨 Data breach response plan",
                value=st.session_state.enhanced_dpia_answers['step5'].get('incident_response', False)
            )
            organizational_measures['subject_rights'] = st.checkbox(
                "✋ Data subject rights procedures",
                value=st.session_state.enhanced_dpia_answers['step5'].get('subject_rights', False)
            )
            organizational_measures['vendor_management'] = st.checkbox(
                "🤝 Third-party vendor management",
                value=st.session_state.enhanced_dpia_answers['step5'].get('vendor_management', False)
            )
        
        # Additional measures
        additional_measures = st.text_area(
            "📝 Additional mitigation measures",
            value=st.session_state.enhanced_dpia_answers['step5'].get('additional_measures', ''),
            placeholder="Describe any other measures specific to your project...",
            height=100
        )
        
        # Implementation timeline
        st.markdown("#### Implementation Timeline")
        
        implementation_timeline = st.selectbox(
            "📅 When will these measures be implemented?",
            options=[
                "Already implemented",
                "Within 1 month",
                "Within 3 months", 
                "Within 6 months",
                "Within 1 year",
                "Timeline not yet defined"
            ],
            index=0 if not st.session_state.enhanced_dpia_answers['step5'].get('implementation_timeline') else
                  ["Already implemented", "Within 1 month", "Within 3 months", 
                   "Within 6 months", "Within 1 year", "Timeline not yet defined"].index(
                       st.session_state.enhanced_dpia_answers['step5'].get('implementation_timeline', "Timeline not yet defined")
                   )
        )
        
        # Residual risk assessment
        st.markdown("#### Residual Risk Assessment")
        
        residual_risk = st.select_slider(
            "📉 Residual risk level after implementing measures",
            options=["Very Low", "Low", "Medium", "High", "Very High"],
            value=st.session_state.enhanced_dpia_answers['step5'].get('residual_risk', "Medium")
        )
        
        # Calculate mitigation effectiveness
        total_measures = sum([
            sum(technical_measures.values()),
            sum(organizational_measures.values()),
            1 if additional_measures else 0
        ])
        
        if total_measures >= 12:
            effectiveness = "Comprehensive"
            effectiveness_class = "risk-low"
        elif total_measures >= 8:
            effectiveness = "Strong"
            effectiveness_class = "risk-low"
        elif total_measures >= 4:
            effectiveness = "Moderate"
            effectiveness_class = "risk-medium"
        else:
            effectiveness = "Limited"
            effectiveness_class = "risk-high"
        
        st.markdown(f"""
        <div class="risk-card {effectiveness_class}">
            <strong>Mitigation Effectiveness: {effectiveness}</strong>
            <br>Total measures implemented: {total_measures}
            <br>Residual risk: {residual_risk}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Navigation
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("← Back to Step 4"):
                st.session_state.enhanced_dpia_step = 4
                st.rerun()
        with col3:
            can_continue = any(technical_measures.values()) or any(organizational_measures.values())
            if st.button("Continue to Step 6 →", type="primary", disabled=not can_continue):
                # Save data
                st.session_state.enhanced_dpia_answers['step5'] = {
                    **technical_measures,
                    **organizational_measures,
                    'additional_measures': additional_measures,
                    'implementation_timeline': implementation_timeline,
                    'residual_risk': residual_risk,
                    'mitigation_effectiveness': effectiveness,
                    'total_measures': total_measures
                }
                st.session_state.enhanced_dpia_step = 6
                st.rerun()

def handle_enhanced_step6():
    """Enhanced Step 6: Decision & Sign-off"""
    st.markdown("### ✅ Step 6: Decision & Sign-off")
    st.markdown("Make a decision about proceeding with the processing.")
    
    with st.container():
        st.markdown('<div class="assessment-form">', unsafe_allow_html=True)
        
        # Decision matrix
        st.markdown("#### Decision Matrix")
        
        # Summary of assessment
        overall_risk = st.session_state.enhanced_dpia_answers.get('step4', {}).get('overall_risk', 'Medium')
        residual_risk = st.session_state.enhanced_dpia_answers.get('step5', {}).get('residual_risk', 'Medium')
        mitigation_effectiveness = st.session_state.enhanced_dpia_answers.get('step5', {}).get('mitigation_effectiveness', 'Moderate')
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Initial Risk", overall_risk)
        with col2:
            st.metric("Residual Risk", residual_risk)
        with col3:
            st.metric("Mitigation Level", mitigation_effectiveness)
        
        # Decision options
        st.markdown("#### Processing Decision")
        
        processing_decision = st.radio(
            "What is your decision regarding the processing?",
            options=[
                "✅ Proceed - Risks adequately mitigated",
                "⚠️ Proceed with conditions - Additional measures required",
                "🔄 Defer - Further risk assessment needed",
                "❌ Do not proceed - Risks too high"
            ],
            index=0 if not st.session_state.enhanced_dpia_answers['step6'].get('processing_decision') else
                  ["✅ Proceed - Risks adequately mitigated",
                   "⚠️ Proceed with conditions - Additional measures required",
                   "🔄 Defer - Further risk assessment needed",
                   "❌ Do not proceed - Risks too high"].index(
                       st.session_state.enhanced_dpia_answers['step6'].get('processing_decision', "✅ Proceed - Risks adequately mitigated")
                   )
        )
        
        # Conditional requirements
        conditional_requirements = ""
        if "with conditions" in processing_decision:
            conditional_requirements = st.text_area(
                "📋 Specify conditions and additional measures required",
                value=st.session_state.enhanced_dpia_answers['step6'].get('conditional_requirements', ''),
                placeholder="List specific conditions that must be met before processing...",
                height=100
            )
        
        # Decision rationale
        decision_rationale = st.text_area(
            "📝 Decision rationale",
            value=st.session_state.enhanced_dpia_answers['step6'].get('decision_rationale', ''),
            placeholder="Explain the reasoning behind this decision...",
            height=100,
            help="Provide justification for your decision"
        )
        
        # Consultation requirements
        st.markdown("#### Consultation Requirements")
        
        supervisory_consultation = st.radio(
            "Is consultation with supervisory authority required?",
            options=[
                "No - Risk level acceptable",
                "Yes - High residual risk",
                "Yes - Special category processing",
                "Unsure - Need legal advice"
            ],
            index=0 if not st.session_state.enhanced_dpia_answers['step6'].get('supervisory_consultation') else
                  ["No - Risk level acceptable",
                   "Yes - High residual risk",
                   "Yes - Special category processing",
                   "Unsure - Need legal advice"].index(
                       st.session_state.enhanced_dpia_answers['step6'].get('supervisory_consultation', "No - Risk level acceptable")
                   )
        )
        
        # Sign-off information
        st.markdown("#### Sign-off Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            approver_name = st.text_input(
                "👤 Approver name",
                value=st.session_state.enhanced_dpia_answers['step6'].get('approver_name', ''),
                placeholder="Full name of approving authority"
            )
            
            approver_role = st.text_input(
                "💼 Approver role/title",
                value=st.session_state.enhanced_dpia_answers['step6'].get('approver_role', ''),
                placeholder="e.g., Data Protection Officer, Privacy Manager"
            )
        
        with col2:
            approval_date = st.date_input(
                "📅 Approval date",
                value=datetime.now().date(),
                help="Date of DPIA approval"
            )
            
            next_review_date = st.date_input(
                "🔄 Next review date",
                value=datetime.now().date().replace(year=datetime.now().year + 1),
                help="When should this DPIA be reviewed again?"
            )
        
        # Final validation
        validation_errors = []
        if not processing_decision:
            validation_errors.append("Processing decision is required")
        if not decision_rationale:
            validation_errors.append("Decision rationale is required")
        if not approver_name:
            validation_errors.append("Approver name is required")
        if not approver_role:
            validation_errors.append("Approver role is required")
        
        if validation_errors:
            for error in validation_errors:
                st.error(f"⚠️ {error}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Navigation
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("← Back to Step 5"):
                st.session_state.enhanced_dpia_step = 5
                st.rerun()
        with col3:
            if st.button("Continue to Step 7 →", type="primary", disabled=bool(validation_errors)):
                # Save data
                st.session_state.enhanced_dpia_answers['step6'] = {
                    'processing_decision': processing_decision,
                    'conditional_requirements': conditional_requirements,
                    'decision_rationale': decision_rationale,
                    'supervisory_consultation': supervisory_consultation,
                    'approver_name': approver_name,
                    'approver_role': approver_role,
                    'approval_date': approval_date.isoformat(),
                    'next_review_date': next_review_date.isoformat()
                }
                st.session_state.enhanced_dpia_step = 7
                st.rerun()

def handle_enhanced_step7():
    """Enhanced Step 7: Implementation & Monitoring"""
    st.markdown("### 📋 Step 7: Implementation & Monitoring")
    st.markdown("Plan the implementation and ongoing monitoring of your DPIA.")
    
    with st.container():
        st.markdown('<div class="assessment-form">', unsafe_allow_html=True)
        
        # Implementation plan
        st.markdown("#### Implementation Plan")
        
        implementation_plan = st.text_area(
            "📝 Implementation plan for identified measures",
            value=st.session_state.enhanced_dpia_answers['step7'].get('implementation_plan', ''),
            placeholder="Describe how you will implement the mitigation measures...",
            height=150,
            help="Provide a detailed plan for implementing the measures identified in Step 5"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            responsible_person = st.text_input(
                "👤 Responsible person",
                value=st.session_state.enhanced_dpia_answers['step7'].get('responsible_person', ''),
                placeholder="Name of person responsible for implementation"
            )
            
            responsible_role = st.text_input(
                "💼 Role/Department",
                value=st.session_state.enhanced_dpia_answers['step7'].get('responsible_role', ''),
                placeholder="e.g., IT Security Manager, Privacy Team"
            )
        
        with col2:
            implementation_deadline = st.date_input(
                "📅 Implementation deadline",
                value=datetime.now().date().replace(month=datetime.now().month + 3) if datetime.now().month <= 9 else datetime.now().date().replace(year=datetime.now().year + 1, month=datetime.now().month - 9),
                help="Target date for completing implementation"
            )
            
            budget_allocated = st.selectbox(
                "💰 Budget status",
                options=[
                    "Budget approved",
                    "Budget pending approval",
                    "Budget not required",
                    "Budget not yet estimated"
                ],
                index=0 if not st.session_state.enhanced_dpia_answers['step7'].get('budget_allocated') else
                      ["Budget approved", "Budget pending approval", "Budget not required", "Budget not yet estimated"].index(
                          st.session_state.enhanced_dpia_answers['step7'].get('budget_allocated', "Budget not yet estimated")
                      )
            )
        
        # Monitoring plan
        st.markdown("#### Monitoring & Review Plan")
        
        monitoring_procedures = st.text_area(
            "📊 Monitoring procedures",
            value=st.session_state.enhanced_dpia_answers['step7'].get('monitoring_procedures', ''),
            placeholder="Describe how you will monitor the effectiveness of measures...",
            height=100,
            help="How will you track that the mitigation measures are working?"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            review_frequency = st.selectbox(
                "🔄 Review frequency",
                options=[
                    "Quarterly",
                    "Semi-annually",
                    "Annually",
                    "When significant changes occur",
                    "Continuous monitoring"
                ],
                index=0 if not st.session_state.enhanced_dpia_answers['step7'].get('review_frequency') else
                      ["Quarterly", "Semi-annually", "Annually", "When significant changes occur", "Continuous monitoring"].index(
                          st.session_state.enhanced_dpia_answers['step7'].get('review_frequency', "Annually")
                      )
            )
            
            review_triggers = st.multiselect(
                "📋 Review triggers",
                options=[
                    "Regulatory changes",
                    "System updates",
                    "Data breach incidents",
                    "Complaints received",
                    "Audit findings",
                    "Technology changes",
                    "Business process changes"
                ],
                default=st.session_state.enhanced_dpia_answers['step7'].get('review_triggers', [])
            )
        
        with col2:
            kpi_tracking = st.multiselect(
                "📈 Key Performance Indicators",
                options=[
                    "Number of data breaches",
                    "Data subject complaints",
                    "Access request response times",
                    "Training completion rates",
                    "System security scores",
                    "Audit compliance rates",
                    "Incident response times"
                ],
                default=st.session_state.enhanced_dpia_answers['step7'].get('kpi_tracking', [])
            )
            
            reporting_requirements = st.selectbox(
                "📋 Reporting requirements",
                options=[
                    "Internal reporting only",
                    "Board/executive reporting",
                    "Regulatory reporting",
                    "Public reporting",
                    "No formal reporting"
                ],
                index=0 if not st.session_state.enhanced_dpia_answers['step7'].get('reporting_requirements') else
                      ["Internal reporting only", "Board/executive reporting", "Regulatory reporting", "Public reporting", "No formal reporting"].index(
                          st.session_state.enhanced_dpia_answers['step7'].get('reporting_requirements', "Internal reporting only")
                      )
            )
        
        # Documentation requirements
        st.markdown("#### Documentation & Records")
        
        documentation_plan = st.text_area(
            "📄 Documentation and record-keeping plan",
            value=st.session_state.enhanced_dpia_answers['step7'].get('documentation_plan', ''),
            placeholder="How will you maintain records of this DPIA and its implementation?",
            height=100
        )
        
        # Training requirements
        training_requirements = st.text_area(
            "🎓 Staff training requirements",
            value=st.session_state.enhanced_dpia_answers['step7'].get('training_requirements', ''),
            placeholder="What training is needed for staff involved in this processing?",
            height=100
        )
        
        # Final validation
        validation_errors = []
        if not implementation_plan:
            validation_errors.append("Implementation plan is required")
        if not responsible_person:
            validation_errors.append("Responsible person is required")
        if not monitoring_procedures:
            validation_errors.append("Monitoring procedures are required")
        
        if validation_errors:
            for error in validation_errors:
                st.error(f"⚠️ {error}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Navigation
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("← Back to Step 6"):
                st.session_state.enhanced_dpia_step = 6
                st.rerun()
        with col3:
            if st.button("Complete Assessment ✅", type="primary", disabled=bool(validation_errors)):
                # Save data
                st.session_state.enhanced_dpia_answers['step7'] = {
                    'implementation_plan': implementation_plan,
                    'responsible_person': responsible_person,
                    'responsible_role': responsible_role,
                    'implementation_deadline': implementation_deadline.isoformat(),
                    'budget_allocated': budget_allocated,
                    'monitoring_procedures': monitoring_procedures,
                    'review_frequency': review_frequency,
                    'review_triggers': review_triggers,
                    'kpi_tracking': kpi_tracking,
                    'reporting_requirements': reporting_requirements,
                    'documentation_plan': documentation_plan,
                    'training_requirements': training_requirements
                }
                
                # Process the assessment
                process_enhanced_assessment()
                st.session_state.enhanced_dpia_step = 8
                st.rerun()

def process_enhanced_assessment():
    """Process the completed enhanced DPIA assessment"""
    try:
        # Generate assessment ID
        assessment_id = str(uuid.uuid4())
        
        # Calculate final scores
        final_risk_score = calculate_final_risk_score()
        compliance_score = calculate_compliance_score()
        
        # Determine overall status
        if final_risk_score <= 30 and compliance_score >= 80:
            compliance_status = "Compliant"
        elif final_risk_score <= 50 and compliance_score >= 60:
            compliance_status = "Conditionally Compliant"
        else:
            compliance_status = "Non-Compliant"
        
        # Generate findings and recommendations
        findings = generate_enhanced_findings()
        recommendations = generate_enhanced_recommendations()
        
        # Create comprehensive assessment results
        assessment_results = {
            'assessment_id': assessment_id,
            'created_date': datetime.now().isoformat(),
            'project_name': st.session_state.enhanced_dpia_answers['step1'].get('project_name', 'Unknown Project'),
            'organization': st.session_state.enhanced_dpia_answers['step1'].get('organization', 'Unknown Organization'),
            'final_risk_score': final_risk_score,
            'compliance_score': compliance_score,
            'compliance_status': compliance_status,
            'overall_risk_level': st.session_state.enhanced_dpia_answers['step4'].get('overall_risk', 'Medium'),
            'residual_risk_level': st.session_state.enhanced_dpia_answers['step5'].get('residual_risk', 'Medium'),
            'processing_decision': st.session_state.enhanced_dpia_answers['step6'].get('processing_decision', 'Unknown'),
            'findings': findings,
            'recommendations': recommendations,
            'assessment_answers': st.session_state.enhanced_dpia_answers
        }
        
        # Save to database
        save_assessment_to_db(assessment_results)
        
        # Store in session state for display
        st.session_state.enhanced_assessment_results = assessment_results
        
        st.success("✅ DPIA assessment completed successfully!")
        
    except Exception as e:
        st.error(f"Error processing assessment: {str(e)}")

def calculate_final_risk_score():
    """Calculate final risk score based on all steps"""
    score = 0
    
    # Step 2: Data categories risk
    step2_score = st.session_state.enhanced_dpia_answers.get('step2', {}).get('risk_score', 0)
    score += step2_score * 0.3
    
    # Step 4: Risk assessment
    risk_scores = {
        "Very Low": 10, "Low": 25, "Medium": 50, "High": 75, "Very High": 100
    }
    overall_risk = st.session_state.enhanced_dpia_answers.get('step4', {}).get('overall_risk', 'Medium')
    score += risk_scores.get(overall_risk, 50) * 0.4
    
    # Step 5: Mitigation effectiveness (inverse)
    mitigation_score = st.session_state.enhanced_dpia_answers.get('step5', {}).get('total_measures', 0)
    mitigation_effectiveness = min(mitigation_score * 10, 100)
    score += (100 - mitigation_effectiveness) * 0.3
    
    return min(int(score), 100)

def calculate_compliance_score():
    """Calculate compliance score based on GDPR requirements"""
    score = 0
    
    # Legal basis (Step 3)
    if st.session_state.enhanced_dpia_answers.get('step3', {}).get('legal_basis'):
        score += 20
    
    # Necessity and proportionality
    necessity = st.session_state.enhanced_dpia_answers.get('step3', {}).get('necessity_justified', '')
    if 'fully justified' in necessity:
        score += 15
    elif 'partially' in necessity:
        score += 10
    
    # Data minimization
    data_min = st.session_state.enhanced_dpia_answers.get('step3', {}).get('data_minimization', '')
    if 'fully applied' in data_min:
        score += 15
    elif 'partially' in data_min:
        score += 10
    
    # Mitigation measures (Step 5)
    total_measures = st.session_state.enhanced_dpia_answers.get('step5', {}).get('total_measures', 0)
    score += min(total_measures * 3, 30)
    
    # Implementation plan (Step 7)
    if st.session_state.enhanced_dpia_answers.get('step7', {}).get('implementation_plan'):
        score += 10
    
    # Monitoring plan
    if st.session_state.enhanced_dpia_answers.get('step7', {}).get('monitoring_procedures'):
        score += 10
    
    return min(score, 100)

def generate_enhanced_findings():
    """Generate comprehensive findings from assessment"""
    findings = []
    
    # Risk level findings
    overall_risk = st.session_state.enhanced_dpia_answers.get('step4', {}).get('overall_risk', 'Medium')
    findings.append({
        'category': 'Risk Assessment',
        'finding': f'Overall privacy risk level assessed as {overall_risk} based on likelihood and impact analysis',
        'severity': overall_risk.lower(),
        'details': f"Likelihood: {st.session_state.enhanced_dpia_answers.get('step4', {}).get('likelihood', 'Unknown')}, Impact: {st.session_state.enhanced_dpia_answers.get('step4', {}).get('impact', 'Unknown')}"
    })
    
    # Legal basis findings
    legal_basis = st.session_state.enhanced_dpia_answers.get('step3', {}).get('legal_basis', '')
    findings.append({
        'category': 'Legal Compliance',
        'finding': f'Processing based on legal basis: {legal_basis}',
        'severity': 'medium',
        'details': 'Legal basis properly identified and documented'
    })
    
    # Data categories findings
    sensitive_data = []
    step2_data = st.session_state.enhanced_dpia_answers.get('step2', {})
    if step2_data.get('financial'): sensitive_data.append('Financial')
    if step2_data.get('health'): sensitive_data.append('Health')
    if step2_data.get('biometric'): sensitive_data.append('Biometric')
    if step2_data.get('children'): sensitive_data.append('Children')
    
    if sensitive_data:
        findings.append({
            'category': 'Data Categories',
            'finding': f'Special category data identified: {", ".join(sensitive_data)}',
            'severity': 'high',
            'details': 'Special category data requires additional safeguards under GDPR Article 9'
        })
    
    # Mitigation findings
    mitigation_effectiveness = st.session_state.enhanced_dpia_answers.get('step5', {}).get('mitigation_effectiveness', 'Moderate')
    findings.append({
        'category': 'Risk Mitigation',
        'finding': f'Mitigation measures assessed as {mitigation_effectiveness}',
        'severity': 'low' if mitigation_effectiveness in ['Comprehensive', 'Strong'] else 'medium',
        'details': f"Total measures implemented: {st.session_state.enhanced_dpia_answers.get('step5', {}).get('total_measures', 0)}"
    })
    
    return findings

def generate_enhanced_recommendations():
    """Generate actionable recommendations"""
    recommendations = []
    
    # Risk-based recommendations
    overall_risk = st.session_state.enhanced_dpia_answers.get('step4', {}).get('overall_risk', 'Medium')
    if overall_risk in ['High', 'Very High']:
        recommendations.append("Implement additional technical and organizational measures to reduce high-risk processing activities")
        recommendations.append("Consider consultation with supervisory authority before proceeding with processing")
    
    # Sensitive data recommendations
    step2_data = st.session_state.enhanced_dpia_answers.get('step2', {})
    if step2_data.get('children'):
        recommendations.append("Implement enhanced protections for children's data including parental consent mechanisms")
    
    if any([step2_data.get('health'), step2_data.get('biometric'), step2_data.get('financial')]):
        recommendations.append("Implement additional security measures for special category data processing")
    
    # Mitigation recommendations
    mitigation_effectiveness = st.session_state.enhanced_dpia_answers.get('step5', {}).get('mitigation_effectiveness', 'Moderate')
    if mitigation_effectiveness in ['Limited', 'Moderate']:
        recommendations.append("Strengthen technical and organizational measures to improve privacy protection")
    
    # Implementation recommendations
    implementation_timeline = st.session_state.enhanced_dpia_answers.get('step5', {}).get('implementation_timeline', '')
    if 'not yet defined' in implementation_timeline:
        recommendations.append("Define clear implementation timeline for all identified measures")
    
    # Monitoring recommendations
    recommendations.append("Establish regular DPIA review process as specified in implementation plan")
    recommendations.append("Implement continuous monitoring of privacy measures effectiveness")
    recommendations.append("Ensure staff receive regular training on data protection requirements")
    
    return recommendations

def display_enhanced_results():
    """Display enhanced DPIA assessment results"""
    st.markdown("## 🎉 DPIA Assessment Complete!")
    
    results = st.session_state.get('enhanced_assessment_results', {})
    
    if not results:
        st.error("No assessment results found. Please complete the assessment first.")
        return
    
    # Executive summary
    st.markdown("### Executive Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        compliance_score = results.get('compliance_score', 0)
        st.metric(
            "Compliance Score", 
            f"{compliance_score}%",
            delta=f"{compliance_score - 70}%" if compliance_score != 70 else None
        )
    
    with col2:
        risk_score = results.get('final_risk_score', 0)
        st.metric(
            "Risk Score", 
            f"{risk_score}%",
            delta=f"{50 - risk_score}%" if risk_score != 50 else None,
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            "Overall Risk", 
            results.get('overall_risk_level', 'Unknown')
        )
    
    with col4:
        st.metric(
            "Compliance Status", 
            results.get('compliance_status', 'Unknown')
        )
    
    # Status indicator
    compliance_status = results.get('compliance_status', 'Unknown')
    if compliance_status == 'Compliant':
        st.success("✅ Your project meets GDPR compliance requirements!")
    elif compliance_status == 'Conditionally Compliant':
        st.warning("⚠️ Your project requires additional measures for full compliance.")
    else:
        st.error("❌ Your project has significant compliance gaps that must be addressed.")
    
    # Detailed findings
    st.markdown("### Key Findings")
    
    findings = results.get('findings', [])
    for finding in findings:
        severity = finding.get('severity', 'medium')
        if severity == 'high':
            st.error(f"🔴 **{finding.get('category', 'Unknown')}**: {finding.get('finding', 'No details')}")
        elif severity == 'medium':
            st.warning(f"🟡 **{finding.get('category', 'Unknown')}**: {finding.get('finding', 'No details')}")
        else:
            st.info(f"🟢 **{finding.get('category', 'Unknown')}**: {finding.get('finding', 'No details')}")
        
        if finding.get('details'):
            st.markdown(f"   *{finding['details']}*")
    
    # Recommendations
    st.markdown("### Recommendations")
    
    recommendations = results.get('recommendations', [])
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f"{i}. {rec}")
    
    # Action buttons
    st.markdown("### Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Download HTML Report", type="primary"):
            html_report = generate_enhanced_html_report(results)
            st.download_button(
                label="💾 Save HTML Report",
                data=html_report,
                file_name=f"Enhanced_DPIA_Report_{results.get('assessment_id', 'unknown')[:8]}.html",
                mime="text/html"
            )
    
    with col2:
        if st.button("🔄 New Assessment"):
            # Clear session state
            for key in list(st.session_state.keys()):
                if key.startswith('enhanced_dpia') or key.startswith('enhanced_assessment'):
                    del st.session_state[key]
            st.rerun()
    
    with col3:
        if st.button("📊 View History"):
            st.session_state.selected_nav = "History"
            st.rerun()
    
    # Assessment details (collapsible)
    with st.expander("📋 View Complete Assessment Details"):
        st.json(results.get('assessment_answers', {}))

def generate_enhanced_html_report(results):
    """Generate comprehensive HTML report for enhanced DPIA"""
    
    findings_html = ""
    for finding in results.get('findings', []):
        severity_class = f"severity-{finding.get('severity', 'medium')}"
        findings_html += f"""
        <div class="finding-item {severity_class}">
            <h4>{finding.get('category', 'Unknown Category')}</h4>
            <p><strong>{finding.get('finding', 'No finding details')}</strong></p>
            {f"<p><em>{finding.get('details', '')}</em></p>" if finding.get('details') else ""}
        </div>
        """
    
    recommendations_html = ""
    for i, rec in enumerate(results.get('recommendations', []), 1):
        recommendations_html += f"<li>{rec}</li>"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Enhanced DPIA Assessment Report</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                text-align: center;
                border-radius: 10px;
                margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            
            .header h1 {{
                margin: 0;
                font-size: 2.5em;
                font-weight: 300;
            }}
            
            .header p {{
                margin: 10px 0 0 0;
                font-size: 1.2em;
                opacity: 0.9;
            }}
            
            .summary-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            
            .metric-card {{
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
            }}
            
            .metric-value {{
                font-size: 2em;
                font-weight: bold;
                color: #667eea;
                margin-bottom: 5px;
            }}
            
            .metric-label {{
                color: #666;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            .section {{
                background: white;
                padding: 30px;
                margin-bottom: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            
            .section h2 {{
                color: #667eea;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }}
            
            .finding-item {{
                padding: 15px;
                margin-bottom: 15px;
                border-radius: 8px;
                border-left: 4px solid;
            }}
            
            .severity-high {{
                background-color: #fee;
                border-left-color: #dc3545;
            }}
            
            .severity-medium {{
                background-color: #fffbe6;
                border-left-color: #ffc107;
            }}
            
            .severity-low {{
                background-color: #f0f9ff;
                border-left-color: #28a745;
            }}
            
            .status-compliant {{
                background-color: #d4edda;
                color: #155724;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
                text-align: center;
                font-weight: bold;
            }}
            
            .status-conditional {{
                background-color: #fff3cd;
                color: #856404;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
                text-align: center;
                font-weight: bold;
            }}
            
            .status-non-compliant {{
                background-color: #f8d7da;
                color: #721c24;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
                text-align: center;
                font-weight: bold;
            }}
            
            .recommendations ol {{
                counter-reset: recommendation-counter;
            }}
            
            .recommendations li {{
                counter-increment: recommendation-counter;
                margin-bottom: 10px;
                padding-left: 10px;
            }}
            
            .footer {{
                text-align: center;
                color: #666;
                padding: 20px;
                border-top: 1px solid #ddd;
                margin-top: 30px;
            }}
            
            .project-info {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            
            .project-info strong {{
                color: #667eea;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🛡️ Enhanced DPIA Assessment Report</h1>
            <p>Comprehensive Data Protection Impact Assessment</p>
            <p><strong>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</strong></p>
        </div>
        
        <div class="project-info">
            <h3>Project Information</h3>
            <p><strong>Project Name:</strong> {results.get('project_name', 'Unknown')}</p>
            <p><strong>Organization:</strong> {results.get('organization', 'Unknown')}</p>
            <p><strong>Assessment ID:</strong> {results.get('assessment_id', 'Unknown')}</p>
            <p><strong>Processing Decision:</strong> {results.get('processing_decision', 'Unknown')}</p>
        </div>
        
        <div class="summary-grid">
            <div class="metric-card">
                <div class="metric-value">{results.get('compliance_score', 0)}%</div>
                <div class="metric-label">Compliance Score</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{results.get('final_risk_score', 0)}%</div>
                <div class="metric-label">Risk Score</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{results.get('overall_risk_level', 'Unknown')}</div>
                <div class="metric-label">Overall Risk</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{results.get('residual_risk_level', 'Unknown')}</div>
                <div class="metric-label">Residual Risk</div>
            </div>
        </div>
        
        <div class="status-{results.get('compliance_status', 'unknown').lower().replace(' ', '-')}">
            <strong>Compliance Status: {results.get('compliance_status', 'Unknown')}</strong>
        </div>
        
        <div class="section">
            <h2>Key Findings</h2>
            {findings_html if findings_html else '<p>No specific findings to report.</p>'}
        </div>
        
        <div class="section recommendations">
            <h2>Recommendations</h2>
            <ol>
                {recommendations_html if recommendations_html else '<li>No specific recommendations at this time.</li>'}
            </ol>
        </div>
        
        <div class="section">
            <h2>Legal Compliance Summary</h2>
            <p><strong>Jurisdiction:</strong> Netherlands, European Union</p>
            <p><strong>Applicable Regulations:</strong> GDPR, Dutch UAVG, Politiewet (where applicable)</p>
            <p><strong>Assessment Methodology:</strong> 7-step GDPR-compliant DPIA process</p>
            <p><strong>Risk Assessment Framework:</strong> Likelihood × Impact matrix with comprehensive mitigation analysis</p>
        </div>
        
        <div class="footer">
            <p><strong>Report Generated by DataGuardian Pro - Enhanced DPIA Assessment Tool</strong></p>
            <p>This assessment represents a point-in-time evaluation. Regular reviews and updates are recommended to maintain compliance.</p>
            <p><em>For questions about this assessment, please contact your Data Protection Officer or Privacy Team.</em></p>
        </div>
    </body>
    </html>
    """
    
    return html_content

if __name__ == "__main__":
    run_enhanced_dpia()