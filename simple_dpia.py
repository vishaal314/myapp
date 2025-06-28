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
    
    # Project Information
    st.markdown("### 📋 Project Information")
    
    # Use form to ensure proper value capture
    with st.form("project_info_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            project_name = st.text_input(
                "Project Name *",
                value=st.session_state.simple_dpia_answers.get('project_name', ''),
                placeholder="Enter your project name",
                help="Name of the project or processing activity"
            )
        
        with col2:
            organization = st.text_input(
                "Organization *",
                value=st.session_state.simple_dpia_answers.get('organization', ''),
                placeholder="Your organization name",
                help="Name of your organization or company"
            )
        
        # Submit button for project info
        project_submitted = st.form_submit_button("💾 Save Project Information")
        
        if project_submitted:
            st.session_state.simple_dpia_answers['project_name'] = project_name
            st.session_state.simple_dpia_answers['organization'] = organization
            st.success("Project information saved!")
            st.rerun()
    
    # Get saved values for display
    saved_project = st.session_state.simple_dpia_answers.get('project_name', '')
    saved_org = st.session_state.simple_dpia_answers.get('organization', '')
    
    if saved_project and saved_org:
        st.info(f"✅ Project: **{saved_project}** | Organization: **{saved_org}**")
    
    # DPIA Questions
    st.markdown("### 📊 DPIA Assessment Questions")
    st.markdown("Please answer each question with Yes or No:")
    
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
    
    # Use form for questions to ensure proper submission
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
                    key=f"q_{q['key']}",
                    horizontal=True
                )
                
                # Store answer and calculate risk
                answers[q['key']] = answer
                
                if answer == "Yes":
                    risk_score += 10
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("---")
        
        # Submit button for questions
        questions_submitted = st.form_submit_button("💾 Save All Answers")
        
        if questions_submitted:
            # Save all answers to session state
            for q in questions:
                st.session_state.simple_dpia_answers[q['key']] = answers[q['key']]
            st.success("All answers saved!")
            st.rerun()
    
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
    
    # Digital Signature Section
    st.markdown("### 📝 Digital Signature")
    st.markdown("**Please provide your details to digitally sign this assessment:**")
    st.markdown('<div class="signature-section">', unsafe_allow_html=True)
    
    # Use form for digital signature to ensure proper value capture
    with st.form("signature_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            assessor_name = st.text_input(
                "👤 Full Name *",
                value=st.session_state.simple_dpia_answers.get('assessor_name', ''),
                placeholder="Enter your full name",
                help="This will appear as the digital signature on your DPIA report"
            )
            
            assessor_role = st.text_input(
                "💼 Job Title/Role *",
                value=st.session_state.simple_dpia_answers.get('assessor_role', ''),
                placeholder="e.g., Data Protection Officer, Privacy Manager",
                help="Your professional role or title within the organization"
            )
        
        with col2:
            assessment_date = st.date_input(
                "📅 Assessment Date",
                value=datetime.now().date(),
                help="Date of assessment completion"
            )
            
            st.markdown("### ✅ Confirmation")
            confirmation = st.checkbox(
                "I confirm that the above information is accurate and complete to the best of my knowledge, and I digitally sign this DPIA assessment.",
                value=st.session_state.simple_dpia_answers.get('confirmation', False),
                help="Your digital signature confirms the accuracy of this assessment"
            )
        
        # Submit button for signature
        signature_submitted = st.form_submit_button("✍️ Apply Digital Signature")
        
        if signature_submitted:
            st.session_state.simple_dpia_answers['assessor_name'] = assessor_name
            st.session_state.simple_dpia_answers['assessor_role'] = assessor_role
            st.session_state.simple_dpia_answers['assessment_date'] = assessment_date.isoformat() if assessment_date else None
            st.session_state.simple_dpia_answers['confirmation'] = confirmation
            st.success("Digital signature applied!")
            st.rerun()
    
    # Display saved signature info
    saved_name = st.session_state.simple_dpia_answers.get('assessor_name', '')
    saved_role = st.session_state.simple_dpia_answers.get('assessor_role', '')
    saved_confirmation = st.session_state.simple_dpia_answers.get('confirmation', False)
    
    if saved_name and saved_role and saved_confirmation:
        st.info(f"✅ Digitally signed by: **{saved_name}** ({saved_role})")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Debug form validation - show current values
    st.markdown("---")
    
    # Get all saved values from session state for validation
    project_text = st.session_state.simple_dpia_answers.get('project_name', '').strip()
    org_text = st.session_state.simple_dpia_answers.get('organization', '').strip()
    name_text = st.session_state.simple_dpia_answers.get('assessor_name', '').strip()
    role_text = st.session_state.simple_dpia_answers.get('assessor_role', '').strip()
    confirmation_saved = st.session_state.simple_dpia_answers.get('confirmation', False)
    
    # Validation based on saved values
    project_valid = len(project_text) > 0
    org_valid = len(org_text) > 0
    name_valid = len(name_text) > 0
    role_valid = len(role_text) > 0
    answers_valid = len(saved_answers) == len(questions) and all(a in ["Yes", "No"] for a in saved_answers.values())
    
    # Debug information for troubleshooting
    with st.expander("Form Status (Debug)", expanded=False):
        st.write(f"Project Name: '{project_text}' - Valid: {project_valid}")
        st.write(f"Organization: '{org_text}' - Valid: {org_valid}")
        st.write(f"Assessor Name: '{name_text}' - Valid: {name_valid}")
        st.write(f"Assessor Role: '{role_text}' - Valid: {role_valid}")
        st.write(f"Confirmation: {confirmation_saved}")
        st.write(f"Answers: {len(saved_answers)}/{len(questions)} - Valid: {answers_valid}")
        st.write(f"Saved answers: {saved_answers}")
        st.write(f"Session state keys: {list(st.session_state.simple_dpia_answers.keys())}")
    
    # Final validation check
    can_submit = project_valid and org_valid and name_valid and role_valid and confirmation_saved and answers_valid
    
    # Enhanced completion status with visual progress
    st.markdown("### 🎯 Completion Status")
    
    # Progress indicators
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if project_valid and org_valid:
            st.success("✅ Step 1\nProject Info")
        else:
            st.error("❌ Step 1\nProject Info")
    
    with col2:
        if answers_valid:
            st.success("✅ Step 2\nQuestions")
        else:
            st.warning("⏳ Step 2\nQuestions")
    
    with col3:
        if name_valid and role_valid and confirmation_saved:
            st.success("✅ Step 3\nSignature")
        else:
            st.warning("⏳ Step 3\nSignature")
    
    with col4:
        if can_submit:
            st.success("✅ Step 4\nReady!")
        else:
            st.info("⏸️ Step 4\nGenerate")
    
    if can_submit:
        st.success("🎉 All sections completed! Ready to generate your DPIA report.")
    else:
        remaining_steps = []
        if not (project_valid and org_valid):
            remaining_steps.append("1️⃣ Fill out and save Project Information")
        if not answers_valid:
            remaining_steps.append("2️⃣ Answer all questions and save answers")
        if not (name_valid and role_valid and confirmation_saved):
            remaining_steps.append("3️⃣ Complete and apply Digital Signature")
        
        if remaining_steps:
            st.info("📋 Complete these steps:")
            for step in remaining_steps:
                st.markdown(f"- {step}")
    
    if st.button("🔍 Generate DPIA Report", type="primary", disabled=not can_submit):
        # Save all data using saved session values
        assessment_data = {
            'assessment_id': str(uuid.uuid4()),
            'project_name': project_text,
            'organization': org_text,
            'assessor_name': name_text,
            'assessor_role': role_text,
            'assessment_date': st.session_state.simple_dpia_answers.get('assessment_date', datetime.now().date().isoformat()),
            'confirmation': confirmation_saved,
            'answers': saved_answers,
            'risk_score': saved_risk_score,
            'risk_level': risk_level,
            'dpia_required': dpia_required,
            'compliance_status': 'Completed'
        }
        
        st.session_state.simple_dpia_answers = assessment_data
        st.session_state.simple_dpia_completed = True
        
        # Save to database
        save_assessment_to_db(assessment_data)
        
        st.success("Assessment completed! Generating report...")
        st.rerun()

def show_results():
    """Display assessment results"""
    data = st.session_state.simple_dpia_answers
    
    st.markdown("## Assessment Complete!")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Risk Score", f"{data['risk_score']}/100")
    
    with col2:
        st.metric("Risk Level", data['risk_level'])
    
    with col3:
        yes_count = sum(1 for answer in data['answers'].values() if answer == "Yes")
        st.metric("Yes Answers", f"{yes_count}/10")
    
    with col4:
        st.metric("Status", "Complete")
    
    # DPIA Requirement
    risk_class = "risk-low" if data['risk_score'] <= 30 else "risk-medium" if data['risk_score'] <= 60 else "risk-high"
    
    st.markdown(f"""
    <div class="risk-indicator {risk_class}">
        <h3>DPIA Requirement Assessment</h3>
        <p>{data['dpia_required']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Recommendations
    st.markdown("### Recommendations")
    
    recommendations = generate_recommendations(data)
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f"{i}. {rec}")
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        html_report = generate_simple_html_report(data)
        st.download_button(
            label="Download HTML Report",
            data=html_report,
            file_name=f"Simple_DPIA_Report_{data['assessment_id'][:8]}.html",
            mime="text/html",
            type="primary"
        )
    
    with col2:
        if st.button("New Assessment"):
            # Clear only the simple DPIA related session state
            st.session_state.simple_dpia_answers = {}
            st.session_state.simple_dpia_completed = False
            if 'simple_dpia_report_data' in st.session_state:
                del st.session_state.simple_dpia_report_data
            st.rerun()
    
    with col3:
        if st.button("View in History"):
            st.session_state.selected_nav = "History"
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
    """Generate HTML report for simple DPIA"""
    
    answers_html = ""
    for i, (key, answer) in enumerate(data['answers'].items(), 1):
        status_class = "yes-answer" if answer == "Yes" else "no-answer"
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
        
        question_text = questions_map.get(key, key.replace('_', ' ').title())
        answers_html += f"""
        <tr class="{status_class}">
            <td>{i}</td>
            <td>{question_text}</td>
            <td><strong>{answer}</strong></td>
        </tr>
        """
    
    recommendations_html = ""
    for i, rec in enumerate(generate_recommendations(data), 1):
        recommendations_html += f"<li>{rec}</li>"
    
    risk_class = "low" if data['risk_score'] <= 30 else "medium" if data['risk_score'] <= 60 else "high"
    
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
            <p><strong>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</strong></p>
        </div>
        
        <div class="summary-section">
            <h2>Project Information</h2>
            <div class="metadata">
                <strong>Project Name:</strong> {data.get('project_name', 'Unknown')}<br>
                <strong>Organization:</strong> {data.get('organization', 'Unknown')}<br>
                <strong>Assessment Date:</strong> {data.get('assessment_date', 'Unknown')}<br>
                <strong>Assessment ID:</strong> {data.get('assessment_id', 'Unknown')}
            </div>
            
            <div class="risk-indicator {risk_class}">
                <h3>Risk Assessment Result</h3>
                <p>Risk Score: {data['risk_score']}/100 • Risk Level: {data['risk_level']}</p>
                <p>{data['dpia_required']}</p>
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
                    <strong>Assessor Name:</strong> {data.get('assessor_name', 'Unknown')}<br>
                    <strong>Role/Title:</strong> {data.get('assessor_role', 'Unknown')}
                </div>
                <div>
                    <strong>Date:</strong> {data.get('assessment_date', 'Unknown')}<br>
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
    
    return html_content

if __name__ == "__main__":
    run_simple_dpia()