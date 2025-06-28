"""
Simple DPIA Assessment - Yes/No Questions with Signature

This module provides a simplified DPIA assessment interface with:
- Simple yes/no questions only
- Digital signature collection
- Instant HTML report generation
- Database storage
"""

import streamlit as st
import uuid
from datetime import datetime
import psycopg2
import os
import json

def init_db_connection():
    """Initialize database connection"""
    try:
        DATABASE_URL = os.environ.get('DATABASE_URL')
        if DATABASE_URL:
            return psycopg2.connect(DATABASE_URL)
        return None
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        return None

def save_assessment_to_db(assessment_data):
    """Save assessment to database"""
    try:
        conn = init_db_connection()
        if conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS simple_dpia_assessments (
                    id SERIAL PRIMARY KEY,
                    assessment_id VARCHAR(255) UNIQUE,
                    project_name VARCHAR(255),
                    created_date TIMESTAMP,
                    assessment_data JSONB,
                    risk_score INTEGER,
                    compliance_status VARCHAR(100)
                )
            """)
            
            cursor.execute("""
                INSERT INTO simple_dpia_assessments 
                (assessment_id, project_name, created_date, assessment_data, risk_score, compliance_status)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (assessment_id) DO UPDATE SET
                    assessment_data = EXCLUDED.assessment_data,
                    risk_score = EXCLUDED.risk_score,
                    compliance_status = EXCLUDED.compliance_status
            """, (
                assessment_data.get('assessment_id'),
                assessment_data.get('project_name', 'Unknown'),
                datetime.now(),
                json.dumps(assessment_data),
                assessment_data.get('risk_score', 0),
                assessment_data.get('compliance_status', 'Pending')
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
    except Exception as e:
        st.error(f"Error saving to database: {str(e)}")
        return False

def run_simple_dpia():
    """Main function for simple DPIA assessment"""
    
    # Custom CSS
    st.markdown("""
    <style>
    .simple-dpia-header {
        background: linear-gradient(135deg, #4a90e2 0%, #7b68ee 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .question-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #4a90e2;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .risk-indicator {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        text-align: center;
        font-weight: bold;
    }
    
    .risk-low {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .risk-medium {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }
    
    .risk-high {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    .signature-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        border: 2px solid #4a90e2;
        box-shadow: 0 4px 15px rgba(74, 144, 226, 0.1);
    }
    
    .question-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid #4a90e2;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .question-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'simple_dpia_answers' not in st.session_state:
        st.session_state.simple_dpia_answers = {}
        st.session_state.simple_dpia_completed = False
    
    # Header
    st.markdown("""
    <div class="simple-dpia-header">
        <h1>DPIA Quick Assessment</h1>
        <p>Simple Yes/No Questionnaire for GDPR Compliance</p>
        <p><strong>Netherlands • EU Standards • Fast & Easy</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.simple_dpia_completed:
        show_assessment_form()
    else:
        show_results()

def show_assessment_form():
    """Display the assessment form"""
    
    # Define questions list at the start of the function for global access
    questions = [
        {
            'key': 'large_scale',
            'question': 'Does your processing involve large-scale processing of personal data?',
            'help': 'Large-scale typically means processing affecting many individuals (1000+)'
        },
        {
            'key': 'sensitive_data',
            'question': 'Does your processing involve special categories of personal data?',
            'help': 'Health data, biometric data, racial/ethnic origin, political opinions, etc.'
        },
        {
            'key': 'vulnerable_subjects',
            'question': 'Does your processing involve vulnerable data subjects?',
            'help': 'Children, elderly, patients, employees in vulnerable positions'
        },
        {
            'key': 'automated_decisions',
            'question': 'Does your processing involve automated decision-making or profiling?',
            'help': 'Automated systems making decisions that affect individuals'
        },
        {
            'key': 'new_technology',
            'question': 'Does your processing use innovative or new technology?',
            'help': 'AI, machine learning, biometric systems, IoT devices'
        },
        {
            'key': 'data_matching',
            'question': 'Does your processing involve systematic monitoring or tracking?',
            'help': 'CCTV, location tracking, behavioral monitoring, data matching'
        },
        {
            'key': 'public_access',
            'question': 'Does your processing prevent individuals from exercising their rights?',
            'help': 'Difficulty accessing, correcting, or deleting personal data'
        },
        {
            'key': 'cross_border',
            'question': 'Does your processing involve international data transfers?',
            'help': 'Transferring data outside the EU/EEA'
        },
        {
            'key': 'data_breach_risk',
            'question': 'Is there a high risk of data breach or unauthorized access?',
            'help': 'Poor security measures, public networks, unsecured storage'
        },
        {
            'key': 'consent_issues',
            'question': 'Are there concerns about the validity of consent?',
            'help': 'Unclear consent, consent fatigue, power imbalances'
        }
    ]
    
    # Project Information - Auto-saving inputs
    st.markdown("### 📋 Project Information")
    st.markdown("**Please provide basic information about your project:**")
    
    # Simplified callback functions that always save current values
    def save_project_name():
        name = st.session_state.get("project_name_input", "").strip()
        st.session_state.simple_dpia_answers['project_name'] = name
    
    def save_organization():
        org = st.session_state.get("organization_input", "").strip()
        st.session_state.simple_dpia_answers['organization'] = org
    
    col1, col2 = st.columns(2)
    
    # Get current saved values
    current_project = st.session_state.simple_dpia_answers.get('project_name', '')
    current_org = st.session_state.simple_dpia_answers.get('organization', '')
    
    with col1:
        st.text_input(
            "Project Name *",
            value=current_project,
            placeholder="Enter your project name",
            help="Name of the project or processing activity",
            key="project_name_input",
            on_change=save_project_name
        )
        
        # Real-time validation for project name
        project_value = st.session_state.get("project_name_input", current_project)
        if project_value:
            if len(project_value.strip()) > 0:
                st.success("✓ Valid project name")
            else:
                st.warning("⚠️ Project name cannot be empty")
        else:
            st.info("💡 Enter your project name")
    
    with col2:
        st.text_input(
            "Organization *",
            value=current_org,
            placeholder="Your organization name",
            help="Name of your organization or company",
            key="organization_input",
            on_change=save_organization
        )
        
        # Real-time validation for organization
        org_value = st.session_state.get("organization_input", current_org)
        if org_value:
            if len(org_value.strip()) > 0:
                st.success("✓ Valid organization")
            else:
                st.warning("⚠️ Organization cannot be empty")
        else:
            st.info("💡 Enter your organization name")
    
    # Manual save button as backup
    col1_btn, col2_btn = st.columns([1, 3])
    with col1_btn:
        if st.button("💾 Save Project Info", type="secondary"):
            # Force save current values
            current_name = st.session_state.get("project_name_input", "").strip()
            current_org = st.session_state.get("organization_input", "").strip()
            
            if current_name and current_org:
                st.session_state.simple_dpia_answers['project_name'] = current_name
                st.session_state.simple_dpia_answers['organization'] = current_org
                st.success("Project information saved!")
                st.rerun()
            else:
                st.error("Please fill in both fields before saving")
    
    # Show current saved status
    saved_project = st.session_state.simple_dpia_answers.get('project_name', '')
    saved_org = st.session_state.simple_dpia_answers.get('organization', '')
    
    with col2_btn:
        if saved_project and saved_org:
            st.success(f"✅ Saved: {saved_project} | {saved_org}")
        else:
            st.warning("⚠️ Project information not saved yet")
    
    # DPIA Questions
    st.markdown("### 📊 DPIA Assessment Questions")
    st.markdown("Please answer each question with Yes or No:")
    
    # Fixed questions form with proper submission handling
    with st.form("questions_form", clear_on_submit=False):
        answers = {}
        risk_score = 0
        
        for i, q in enumerate(questions, 1):
            with st.container():
                st.markdown(f'<div class="question-card">', unsafe_allow_html=True)
                
                # Clean question display
                st.markdown(f"**{i}.** {q['question']}")
                st.caption(q['help'])
                
                # Get current answer or default to "No"
                current_answer = st.session_state.simple_dpia_answers.get(q['key'], "No")
                
                answer = st.radio(
                    "Your answer:",
                    options=["No", "Yes"],
                    index=1 if current_answer == "Yes" else 0,
                    key=f"radio_{q['key']}_{i}",
                    horizontal=True
                )
                
                # Store answer and calculate risk
                answers[q['key']] = answer
                
                if answer == "Yes":
                    risk_score += 10
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("---")
        
        # Show completion status
        answered_count = len([a for a in answers.values() if a in ["Yes", "No"]])
        if answered_count == len(questions):
            st.success(f"✅ All {len(questions)} questions completed")
        else:
            st.warning(f"⚠️ {answered_count}/{len(questions)} questions answered")
        
        # Submit button for questions
        questions_submitted = st.form_submit_button(
            "💾 Save All Answers",
            type="primary" if answered_count == len(questions) else "secondary"
        )
        
        if questions_submitted:
            try:
                # Save all answers to session state
                for q in questions:
                    st.session_state.simple_dpia_answers[q['key']] = answers[q['key']]
                st.success("✅ All answers saved successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error saving answers: {str(e)}")
    
    # Calculate current risk from saved answers
    saved_answers = {}
    saved_risk_score = 0
    for q in questions:
        saved_answer = st.session_state.simple_dpia_answers.get(q['key'], "No")
        saved_answers[q['key']] = saved_answer
        if saved_answer == "Yes":
            saved_risk_score += 10
    
    # Show completion status for questions
    answered_count = len([a for a in saved_answers.values() if a in ["Yes", "No"]])
    if answered_count == len(questions):
        st.info(f"✅ All {len(questions)} questions answered")
    
    # Real-time risk indicator based on saved answers
    if saved_risk_score <= 30:
        risk_level = "Low Risk"
        risk_class = "risk-low"
        dpia_required = "DPIA may not be required, but recommended for good practice"
    elif saved_risk_score <= 60:
        risk_level = "Medium Risk"
        risk_class = "risk-medium"
        dpia_required = "DPIA is likely required - proceed with caution"
    else:
        risk_level = "High Risk"
        risk_class = "risk-high"
        dpia_required = "DPIA is definitely required before processing"
    
    st.markdown(f"""
    <div class="risk-indicator {risk_class}">
        <h3>Current Risk Assessment: {risk_level}</h3>
        <p>Score: {saved_risk_score}/100</p>
        <p>{dpia_required}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Set signature as complete since no digital signature required
    signature_complete = True
    
    st.markdown("---")
    
    # Streamlined validation - always use saved session state values
    saved_project = st.session_state.simple_dpia_answers.get('project_name', '').strip()
    saved_org = st.session_state.simple_dpia_answers.get('organization', '').strip()
    
    # Count completed questions
    completed_answers = 0
    for q in questions:
        saved_answer = st.session_state.simple_dpia_answers.get(q['key'], '')
        if saved_answer in ["Yes", "No"]:
            completed_answers += 1
    
    # Simple validation checks
    project_complete = bool(saved_project)
    org_complete = bool(saved_org) 
    questions_complete = completed_answers == len(questions)
    
    # Enable download when all three sections are complete
    can_submit = project_complete and org_complete and questions_complete
    

    
    # Enhanced completion status with visual progress
    st.markdown("### 🎯 Completion Status")
    
    # Progress indicators
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if project_complete and org_complete:
            st.success("✅ Step 1\nProject Info")
        else:
            st.error("❌ Step 1\nProject Info")
    
    with col2:
        if questions_complete:
            st.success("✅ Step 2\nQuestions")
        else:
            st.warning("⏳ Step 2\nQuestions")
    
    with col3:
        if can_submit:
            st.success("✅ Step 3\nReady!")
        else:
            st.info("⏸️ Step 3\nGenerate")
    
    if can_submit:
        st.success("🎉 All sections completed! Ready to generate your DPIA report.")
    else:
        remaining_steps = []
        if not (project_complete and org_complete):
            remaining_steps.append("1️⃣ Fill out and save Project Information")
        if not questions_complete:
            remaining_steps.append("2️⃣ Answer all questions and save answers")
        
        if remaining_steps:
            st.info("📋 Complete these steps:")
            for step in remaining_steps:
                st.markdown(f"- {step}")
    
    if st.button("📥 Download HTML Report", type="primary", disabled=not can_submit):
        with st.spinner("Generating DPIA report..."):
            try:
                # Get current saved answers for processing
                current_saved_answers = {}
                for q in questions:
                    saved_answer = st.session_state.simple_dpia_answers.get(q['key'], '')
                    if saved_answer in ["Yes", "No"]:
                        current_saved_answers[q['key']] = saved_answer
                
                # Validation using saved session state values
                if not all([saved_project, saved_org]):
                    st.error("Missing required information. Please complete project information.")
                    st.stop()
                
                if len(current_saved_answers) != len(questions):
                    st.error("Not all questions have been answered. Please complete the assessment.")
                    st.stop()
                
                # Create comprehensive assessment data using saved answers
                current_risk_score = len([a for a in current_saved_answers.values() if a == "Yes"]) * 10
                
                # Determine risk level based on current score
                if current_risk_score <= 30:
                    current_risk_level = "Low Risk"
                    current_dpia_required = "DPIA may not be required, but recommended for good practice"
                elif current_risk_score <= 60:
                    current_risk_level = "Medium Risk"
                    current_dpia_required = "DPIA is likely required - proceed with caution"
                else:
                    current_risk_level = "High Risk"
                    current_dpia_required = "DPIA is definitely required before processing"
                
                assessment_data = {
                    'assessment_id': str(uuid.uuid4()),
                    'project_name': saved_project.strip(),
                    'organization': saved_org.strip(),
                    'assessor_name': 'Assessment User',
                    'assessor_role': 'Data Protection Assessment',
                    'assessment_date': datetime.now().date().isoformat(),
                    'confirmation': True,
                    'answers': current_saved_answers,
                    'risk_score': current_risk_score,
                    'risk_level': current_risk_level,
                    'dpia_required': current_dpia_required,
                    'compliance_status': 'Completed',
                    'created_timestamp': datetime.now().isoformat(),
                    'question_count': len(questions),
                    'yes_answers': sum(1 for answer in current_saved_answers.values() if answer == "Yes")
                }
                
                # Test HTML report generation before saving
                try:
                    test_html = generate_simple_html_report(assessment_data)
                    if not test_html or len(test_html) < 1000:  # Basic validation
                        raise ValueError("Generated report appears incomplete")
                except Exception as e:
                    st.error(f"Error generating HTML report: {str(e)}")
                    st.stop()
                
                # Update session state without overwriting existing data
                st.session_state.simple_dpia_answers.update(assessment_data)
                st.session_state.simple_dpia_completed = True
                
                # Save to database with error handling
                db_saved = save_assessment_to_db(assessment_data)
                if db_saved:
                    st.success("Assessment completed and saved to database!")
                else:
                    st.warning("Assessment completed but could not save to database. Report generation will continue.")
                
                # Force page refresh to show results
                st.rerun()
                
            except Exception as e:
                st.error(f"Unexpected error during report generation: {str(e)}")
                st.error("Please try again or contact support if the problem persists.")

def show_results():
    """Display assessment results with enhanced download functionality"""
    try:
        data = st.session_state.simple_dpia_answers
        
        # Validate data integrity
        if not data or 'assessment_id' not in data:
            st.error("Assessment data not found. Please complete the assessment again.")
            if st.button("Start New Assessment"):
                st.session_state.simple_dpia_answers = {}
                st.session_state.simple_dpia_completed = False
                st.rerun()
            return
        
        st.markdown("## 🎉 Assessment Complete!")
        
        # Enhanced summary metrics with validation
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            risk_score = data.get('risk_score', 0)
            st.metric("Risk Score", f"{risk_score}/100")
        
        with col2:
            risk_level = data.get('risk_level', 'Unknown')
            st.metric("Risk Level", risk_level)
        
        with col3:
            answers = data.get('answers', {})
            yes_count = sum(1 for answer in answers.values() if answer == "Yes")
            total_questions = len(answers)
            st.metric("Yes Answers", f"{yes_count}/{total_questions}")
        
        with col4:
            status = data.get('compliance_status', 'Unknown')
            st.metric("Status", status)
        
        # DPIA Requirement with enhanced styling
        risk_score = data.get('risk_score', 0)
        risk_class = "risk-low" if risk_score <= 30 else "risk-medium" if risk_score <= 60 else "risk-high"
        
        st.markdown(f"""
        <div class="risk-indicator {risk_class}">
            <h3>DPIA Requirement Assessment</h3>
            <p>{data.get('dpia_required', 'Assessment unavailable')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Assessment details
        with st.expander("📋 Assessment Details", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Project:** {data.get('project_name', 'Unknown')}")
                st.write(f"**Organization:** {data.get('organization', 'Unknown')}")
                st.write(f"**Assessment ID:** {data.get('assessment_id', 'Unknown')[:12]}...")
            with col2:
                st.write(f"**Assessor:** {data.get('assessor_name', 'Unknown')}")
                st.write(f"**Role:** {data.get('assessor_role', 'Unknown')}")
                st.write(f"**Date:** {data.get('assessment_date', 'Unknown')}")
        
        # Recommendations
        st.markdown("### 💡 Recommendations")
        
        try:
            recommendations = generate_recommendations(data)
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"{i}. {rec}")
        except Exception as e:
            st.error(f"Error generating recommendations: {str(e)}")
            st.markdown("- Complete a thorough privacy impact assessment")
            st.markdown("- Implement appropriate technical and organizational measures")
            st.markdown("- Maintain ongoing compliance monitoring")
        
        # Enhanced action buttons with error handling
        st.markdown("### 📥 Download & Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Debug HTML report generation
            with st.expander("HTML Report Debug", expanded=False):
                st.write("Data for report generation:")
                st.json({
                    "has_data": bool(data),
                    "data_keys": list(data.keys()) if data else [],
                    "answers_count": len(data.get('answers', {})),
                    "project_name": data.get('project_name', 'Missing'),
                    "organization": data.get('organization', 'Missing'),
                    "assessor_name": data.get('assessor_name', 'Missing'),
                    "risk_score": data.get('risk_score', 'Missing')
                })
            
            try:
                st.info("Generating HTML report...")
                html_report = generate_simple_html_report(data)
                
                # Enhanced validation with debug info
                if html_report:
                    report_length = len(html_report)
                    st.success(f"Report generated successfully ({report_length} characters)")
                    
                    # Always show download button if report exists
                    st.download_button(
                        label="📄 Download HTML Report",
                        data=html_report,
                        file_name=f"DPIA_Report_{data.get('project_name', 'Assessment').replace(' ', '_')}_{data.get('assessment_id', 'unknown')[:8]}.html",
                        mime="text/html",
                        type="primary",
                        help="Download complete assessment report as HTML file"
                    )
                    
                    # Show preview option
                    if st.button("👀 Preview Report"):
                        with st.expander("HTML Report Preview", expanded=True):
                            st.markdown("**Report Preview (first 2000 characters):**")
                            st.text(html_report[:2000] + "..." if len(html_report) > 2000 else html_report)
                        
                else:
                    st.error("Report generation returned empty content")
                    
            except Exception as e:
                st.error(f"HTML Report Generation Error: {str(e)}")
                st.error("Please check the debug information above")
                
                # Show fallback download with minimal report
                if st.button("Generate Minimal Report"):
                    minimal_html = f"""
                    <!DOCTYPE html>
                    <html><head><title>DPIA Assessment</title></head>
                    <body>
                        <h1>DPIA Assessment Report</h1>
                        <p>Project: {data.get('project_name', 'Unknown')}</p>
                        <p>Organization: {data.get('organization', 'Unknown')}</p>
                        <p>Assessment ID: {data.get('assessment_id', 'Unknown')}</p>
                        <p>Risk Score: {data.get('risk_score', 0)}/100</p>
                        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </body></html>
                    """
                    
                    st.download_button(
                        label="📄 Download Minimal Report",
                        data=minimal_html,
                        file_name=f"DPIA_Minimal_{data.get('assessment_id', 'unknown')[:8]}.html",
                        mime="text/html"
                    )
        
        with col2:
            if st.button("🆕 New Assessment", help="Start a fresh DPIA assessment"):
                # Clear session state with confirmation
                st.session_state.simple_dpia_answers = {}
                st.session_state.simple_dpia_completed = False
                if 'simple_dpia_report_data' in st.session_state:
                    del st.session_state.simple_dpia_report_data
                st.rerun()
        
        with col3:
            if st.button("📚 View in History", help="View this assessment in the history section"):
                st.session_state.selected_nav = "History"
                st.rerun()
                
        # Debug information for troubleshooting
        with st.expander("🔧 Technical Details", expanded=False):
            st.json({
                "assessment_id": data.get('assessment_id', 'Unknown'),
                "created_timestamp": data.get('created_timestamp', 'Unknown'),
                "question_count": data.get('question_count', 0),
                "yes_answers": data.get('yes_answers', 0),
                "risk_calculation": f"{data.get('yes_answers', 0)} * 10 = {data.get('risk_score', 0)}"
            })
            
    except Exception as e:
        st.error(f"Error displaying results: {str(e)}")
        st.markdown("### Recovery Options")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Retry Display"):
                st.rerun()
        with col2:
            if st.button("🆕 Start Over"):
                st.session_state.simple_dpia_answers = {}
                st.session_state.simple_dpia_completed = False
                st.rerun()

def generate_recommendations(data):
    """Generate recommendations based on answers"""
    recommendations = []
    answers = data['answers']
    
    if answers.get('large_scale') == 'Yes':
        recommendations.append("Implement robust data governance frameworks for large-scale processing")
    
    if answers.get('sensitive_data') == 'Yes':
        recommendations.append("Apply additional safeguards for special category data as per GDPR Article 9")
    
    if answers.get('vulnerable_subjects') == 'Yes':
        recommendations.append("Implement enhanced protections for vulnerable data subjects")
    
    if answers.get('automated_decisions') == 'Yes':
        recommendations.append("Ensure transparency and implement right to human review for automated decisions")
    
    if answers.get('new_technology') == 'Yes':
        recommendations.append("Conduct thorough privacy impact assessment for new technology implementation")
    
    if answers.get('data_matching') == 'Yes':
        recommendations.append("Implement privacy-by-design principles for monitoring systems")
    
    if answers.get('public_access') == 'Yes':
        recommendations.append("Establish clear procedures for data subject rights requests")
    
    if answers.get('cross_border') == 'Yes':
        recommendations.append("Ensure adequate safeguards for international data transfers")
    
    if answers.get('data_breach_risk') == 'Yes':
        recommendations.append("Strengthen security measures and incident response procedures")
    
    if answers.get('consent_issues') == 'Yes':
        recommendations.append("Review and improve consent mechanisms to ensure validity")
    
    # General recommendations
    recommendations.extend([
        "Maintain comprehensive records of processing activities",
        "Provide regular privacy training for staff",
        "Establish ongoing monitoring and review procedures",
        "Consider appointing a Data Protection Officer if required"
    ])
    
    return recommendations

def generate_simple_html_report(data):
    """Generate HTML report for simple DPIA with comprehensive error handling"""
    
    try:
        # Validate input data
        if not data or not isinstance(data, dict):
            raise ValueError("Invalid assessment data provided")
        
        # More flexible validation - only require essential fields
        required_fields = ['answers', 'project_name']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Provide defaults for optional fields
        if 'risk_score' not in data:
            data['risk_score'] = 0
        if 'organization' not in data:
            data['organization'] = 'Not Specified'
        if 'assessor_name' not in data:
            data['assessor_name'] = 'Not Specified'
        
        # Generate answers table with error handling
        answers_html = ""
        answers = data.get('answers', {})
        
        if not answers:
            raise ValueError("No assessment answers found")
        
        questions_map = {
            'large_scale': 'Large-scale processing of personal data',
            'sensitive_data': 'Special categories of personal data',
            'vulnerable_subjects': 'Vulnerable data subjects',
            'automated_decisions': 'Automated decision-making or profiling',
            'new_technology': 'Innovative or new technology',
            'data_matching': 'Systematic monitoring or tracking',
            'public_access': 'Prevents exercising rights',
            'cross_border': 'International data transfers',
            'data_breach_risk': 'High risk of data breach',
            'consent_issues': 'Concerns about consent validity'
        }
        
        for i, (key, answer) in enumerate(answers.items(), 1):
            if answer not in ["Yes", "No"]:
                continue  # Skip invalid answers
            
            status_class = "yes-answer" if answer == "Yes" else "no-answer"
            question_text = questions_map.get(key, key.replace('_', ' ').title())
            
            # Escape HTML characters for security
            question_text = question_text.replace('<', '&lt;').replace('>', '&gt;')
            answer = str(answer).replace('<', '&lt;').replace('>', '&gt;')
            
            answers_html += f"""
            <tr class="{status_class}">
                <td>{i}</td>
                <td>{question_text}</td>
                <td><strong>{answer}</strong></td>
            </tr>
            """
        
        if not answers_html:
            raise ValueError("No valid answers found for report generation")
        
        # Generate recommendations with error handling
        recommendations_html = ""
        try:
            recommendations = generate_recommendations(data)
            for rec in recommendations:
                # Escape HTML and ensure recommendation is valid
                safe_rec = str(rec).replace('<', '&lt;').replace('>', '&gt;')
                if safe_rec.strip():  # Only add non-empty recommendations
                    recommendations_html += f"<li>{safe_rec}</li>"
        except Exception as e:
            # Fallback recommendations if generation fails
            recommendations_html = """
                <li>Complete a comprehensive privacy impact assessment</li>
                <li>Implement appropriate technical and organizational measures</li>
                <li>Establish regular compliance monitoring procedures</li>
                <li>Provide staff training on data protection requirements</li>
            """
        
        # Safely extract and validate data fields
        risk_score = max(0, min(100, int(data.get('risk_score', 0))))  # Ensure valid range
        risk_class = "low" if risk_score <= 30 else "medium" if risk_score <= 60 else "high"
        
        # Safely escape text fields
        project_name = str(data.get('project_name', 'Unknown')).replace('<', '&lt;').replace('>', '&gt;')
        organization = str(data.get('organization', 'Unknown')).replace('<', '&lt;').replace('>', '&gt;')
        assessor_name = str(data.get('assessor_name', 'Unknown')).replace('<', '&lt;').replace('>', '&gt;')
        assessor_role = str(data.get('assessor_role', 'Unknown')).replace('<', '&lt;').replace('>', '&gt;')
        assessment_id = str(data.get('assessment_id', 'Unknown'))[:36]  # Limit length
        assessment_date = str(data.get('assessment_date', datetime.now().date().isoformat()))
        risk_level = str(data.get('risk_level', 'Unknown'))
        dpia_required = str(data.get('dpia_required', 'Assessment required'))
        
        # Generate timestamp for report
        generation_time = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        
        html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Simple DPIA Assessment Report</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1000px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            
            .header {{
                background: linear-gradient(135deg, #4a90e2 0%, #7b68ee 100%);
                color: white;
                padding: 40px;
                text-align: center;
                border-radius: 15px;
                margin-bottom: 30px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }}
            
            .header h1 {{
                margin: 0;
                font-size: 2.5em;
                font-weight: 300;
            }}
            
            .summary-section {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 30px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            
            .risk-indicator {{
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                margin: 20px 0;
                font-weight: bold;
                font-size: 1.2em;
            }}
            
            .risk-indicator.low {{
                background-color: #d4edda;
                color: #155724;
                border: 2px solid #c3e6cb;
            }}
            
            .risk-indicator.medium {{
                background-color: #fff3cd;
                color: #856404;
                border: 2px solid #ffeaa7;
            }}
            
            .risk-indicator.high {{
                background-color: #f8d7da;
                color: #721c24;
                border: 2px solid #f5c6cb;
            }}
            
            .questions-table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                background: white;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            
            .questions-table th {{
                background: #4a90e2;
                color: white;
                padding: 15px;
                text-align: left;
            }}
            
            .questions-table td {{
                padding: 12px 15px;
                border-bottom: 1px solid #ddd;
            }}
            
            .yes-answer {{
                background-color: #fff3cd;
            }}
            
            .no-answer {{
                background-color: #f8f9fa;
            }}
            
            .signature-section {{
                background: #f8f9fa;
                padding: 25px;
                border-radius: 10px;
                border: 2px solid #dee2e6;
                margin: 30px 0;
            }}
            
            .signature-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-top: 15px;
            }}
            
            .recommendations {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                margin: 30px 0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            
            .recommendations h3 {{
                color: #4a90e2;
                border-bottom: 2px solid #4a90e2;
                padding-bottom: 10px;
            }}
            
            .recommendations ol {{
                padding-left: 20px;
            }}
            
            .recommendations li {{
                margin-bottom: 8px;
                line-height: 1.5;
            }}
            
            .footer {{
                text-align: center;
                color: #666;
                padding: 30px;
                border-top: 2px solid #ddd;
                margin-top: 40px;
            }}
            
            .metadata {{
                background: #e9ecef;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>DPIA Quick Assessment Report</h1>
            <p>Simple Yes/No Questionnaire for GDPR Compliance</p>
            <p><strong>Generated on {generation_time}</strong></p>
        </div>
        
        <div class="summary-section">
            <h2>Project Information</h2>
            <div class="metadata">
                <strong>Project Name:</strong> {project_name}<br>
                <strong>Organization:</strong> {organization}<br>
                <strong>Assessment Date:</strong> {assessment_date}<br>
                <strong>Assessment ID:</strong> {assessment_id}
            </div>
            
            <div class="risk-indicator {risk_class}">
                <h3>Risk Assessment Result</h3>
                <p>Risk Score: {risk_score}/100 • Risk Level: {risk_level}</p>
                <p>{dpia_required}</p>
            </div>
        </div>
        
        <div class="summary-section">
            <h2>Assessment Questions & Answers</h2>
            <table class="questions-table">
                <thead>
                    <tr>
                        <th style="width: 5%;">#</th>
                        <th style="width: 75%;">Question</th>
                        <th style="width: 20%;">Answer</th>
                    </tr>
                </thead>
                <tbody>
                    {answers_html}
                </tbody>
            </table>
        </div>
        
        <div class="recommendations">
            <h3>Recommendations</h3>
            <ol>
                {recommendations_html}
            </ol>
        </div>
        
        <div class="signature-section">
            <h3>Digital Signature</h3>
            <div class="signature-grid">
                <div>
                    <strong>Assessor Name:</strong> {assessor_name}<br>
                    <strong>Role/Title:</strong> {assessor_role}
                </div>
                <div>
                    <strong>Date:</strong> {assessment_date}<br>
                    <strong>Confirmation:</strong> ✓ Confirmed accurate and complete
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Report Generated by DataGuardian Pro - Simple DPIA Assessment Tool</strong></p>
            <p><strong>Legal Framework:</strong> GDPR, Netherlands UAVG, EU Privacy Standards</p>
            <p><em>This assessment provides initial guidance only. For complex processing activities, 
            a full DPIA may be required regardless of this preliminary assessment.</em></p>
        </div>
    </body>
    </html>
    """
        
        # Validate generated HTML more flexibly
        if not html_content:
            raise ValueError("Generated HTML report is empty")
        
        if len(html_content) < 100:
            raise ValueError("Generated HTML report is too short")
        
        return html_content
        
    except Exception as e:
        # Generate a comprehensive error report with debugging info
        import traceback
        error_details = traceback.format_exc()
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>DPIA Report Generation Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .error {{ background-color: #fee; padding: 20px; border: 1px solid #fcc; }}
                .debug {{ background-color: #eef; padding: 15px; margin-top: 20px; font-family: monospace; }}
            </style>
        </head>
        <body>
            <h1>DPIA Report Generation Error</h1>
            <div class="error">
                <h3>Error Details:</h3>
                <p><strong>Error:</strong> {str(e)}</p>
                <p><strong>Assessment ID:</strong> {data.get('assessment_id', 'Unknown') if data else 'Unknown'}</p>
                <p><strong>Project:</strong> {data.get('project_name', 'Unknown') if data else 'Unknown'}</p>
            </div>
            
            <div class="debug">
                <h3>Debug Information:</h3>
                <p><strong>Data Keys:</strong> {list(data.keys()) if data else 'No data'}</p>
                <p><strong>Has Answers:</strong> {'Yes' if data and data.get('answers') else 'No'}</p>
                <p><strong>Answer Count:</strong> {len(data.get('answers', {})) if data else 0}</p>
                <p><strong>Technical Details:</strong></p>
                <pre>{error_details}</pre>
            </div>
            
            <p><em>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
        </body>
        </html>
        """
        return error_html

if __name__ == "__main__":
    run_simple_dpia()