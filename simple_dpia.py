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
    st.markdown("### Project Information")
    
    col1, col2 = st.columns(2)
    with col1:
        project_name = st.text_input(
            "Project Name",
            value=st.session_state.simple_dpia_answers.get('project_name', ''),
            placeholder="Enter your project name",
            key="project_name_input"
        )
    
    with col2:
        organization = st.text_input(
            "Organization",
            value=st.session_state.simple_dpia_answers.get('organization', ''),
            placeholder="Your organization name",
            key="organization_input"
        )
    
    # Update session state immediately
    if project_name:
        st.session_state.simple_dpia_answers['project_name'] = project_name
    if organization:
        st.session_state.simple_dpia_answers['organization'] = organization
    
    # DPIA Questions
    st.markdown("### DPIA Assessment Questions")
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
    
    answers = {}
    risk_score = 0
    
    for i, q in enumerate(questions, 1):
        st.markdown(f'<div class="question-card">', unsafe_allow_html=True)
        
        st.markdown(f"**Question {i}:** {q['question']}")
        
        answer = st.radio(
            f"Select your answer:",
            options=["No", "Yes"],
            index=0 if st.session_state.simple_dpia_answers.get(q['key']) != 'Yes' else 1,
            key=f"q_{q['key']}",
            help=q['help']
        )
        
        answers[q['key']] = answer
        if answer == "Yes":
            risk_score += 10
        
        # Update session state for this question
        st.session_state.simple_dpia_answers[q['key']] = answer
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Real-time risk indicator
    if risk_score <= 30:
        risk_level = "Low Risk"
        risk_class = "risk-low"
        dpia_required = "DPIA may not be required, but recommended for good practice"
    elif risk_score <= 60:
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
        <p>Score: {risk_score}/100</p>
        <p>{dpia_required}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Digital Signature Section
    st.markdown("### 📝 Digital Signature")
    st.markdown("**Please provide your details to digitally sign this assessment:**")
    st.markdown('<div class="signature-section">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        assessor_name = st.text_input(
            "👤 Full Name *",
            value=st.session_state.simple_dpia_answers.get('assessor_name', ''),
            placeholder="Enter your full name",
            help="This will appear as the digital signature on your DPIA report",
            key="assessor_name_input"
        )
        
        assessor_role = st.text_input(
            "💼 Job Title/Role *",
            value=st.session_state.simple_dpia_answers.get('assessor_role', ''),
            placeholder="e.g., Data Protection Officer, Privacy Manager",
            help="Your professional role or title within the organization",
            key="assessor_role_input"
        )
        
        # Update session state immediately
        if assessor_name:
            st.session_state.simple_dpia_answers['assessor_name'] = assessor_name
        if assessor_role:
            st.session_state.simple_dpia_answers['assessor_role'] = assessor_role
    
    with col2:
        assessment_date = st.date_input(
            "📅 Assessment Date",
            value=datetime.now().date(),
            help="Date of assessment completion",
            key="assessment_date_input"
        )
        
        st.markdown("### ✅ Confirmation")
        confirmation = st.checkbox(
            "I confirm that the above information is accurate and complete to the best of my knowledge, and I digitally sign this DPIA assessment.",
            value=st.session_state.simple_dpia_answers.get('confirmation', False),
            help="Your digital signature confirms the accuracy of this assessment",
            key="confirmation_input"
        )
        
        # Update session state immediately
        st.session_state.simple_dpia_answers['assessment_date'] = assessment_date.isoformat() if assessment_date else None
        st.session_state.simple_dpia_answers['confirmation'] = confirmation
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Submit button - check both current values and session state
    current_project_name = project_name or st.session_state.simple_dpia_answers.get('project_name', '')
    current_organization = organization or st.session_state.simple_dpia_answers.get('organization', '')
    current_assessor_name = assessor_name or st.session_state.simple_dpia_answers.get('assessor_name', '')
    current_assessor_role = assessor_role or st.session_state.simple_dpia_answers.get('assessor_role', '')
    current_confirmation = confirmation or st.session_state.simple_dpia_answers.get('confirmation', False)
    
    can_submit = (
        current_project_name and 
        current_organization and 
        current_assessor_name and 
        current_assessor_role and 
        current_confirmation and
        all(answers.values())
    )
    
    if not can_submit:
        missing_fields = []
        if not current_project_name:
            missing_fields.append("Project Name")
        if not current_organization:
            missing_fields.append("Organization")
        if not current_assessor_name:
            missing_fields.append("Your Full Name")
        if not current_assessor_role:
            missing_fields.append("Your Job Title")
        if not current_confirmation:
            missing_fields.append("Digital Signature Confirmation")
        if not all(answers.values()):
            missing_fields.append("All Assessment Questions")
        
        if missing_fields:
            st.warning(f"Please complete the following fields: {', '.join(missing_fields)}")
        else:
            st.info("All fields completed! You can now generate your DPIA report.")
    
    if st.button("Generate DPIA Report", type="primary", disabled=not can_submit):
        # Save all data using current values
        assessment_data = {
            'assessment_id': str(uuid.uuid4()),
            'project_name': current_project_name,
            'organization': current_organization,
            'assessor_name': current_assessor_name,
            'assessor_role': current_assessor_role,
            'assessment_date': assessment_date.isoformat() if assessment_date else datetime.now().date().isoformat(),
            'confirmation': current_confirmation,
            'answers': answers,
            'risk_score': risk_score,
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
            for key in list(st.session_state.keys()):
                if key.startswith('simple_dpia'):
                    del st.session_state[key]
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