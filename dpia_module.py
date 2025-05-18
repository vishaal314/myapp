"""
Enhanced DPIA Form Module

This module provides a standalone, stable implementation of the Data Protection
Impact Assessment (DPIA) form that follows the 7-step DPIA process outlined in GDPR
Article 35 requirements.
"""

import streamlit as st
import uuid
import json
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional
import os

# Import scanner and report functions
from services.dpia_scanner import DPIAScanner
from services.report_generator import generate_report as generate_pdf_report
from services.results_aggregator import ResultsAggregator
from utils.i18n import get_text, _

# Initialize database connection
results_aggregator = None

def init_db_connection():
    """Initialize connection to the database for saving reports"""
    global results_aggregator
    if results_aggregator is None:
        try:
            results_aggregator = ResultsAggregator()
            return True
        except Exception as e:
            st.error(f"Error connecting to database: {str(e)}")
            return False
    return True

def save_assessment_to_db(assessment_results):
    """Save assessment results to the database"""
    global results_aggregator
    
    if not init_db_connection():
        return False
    
    try:
        # Create a scan entry structure that matches what the database expects
        scan_entry = {
            "scan_id": assessment_results.get("scan_id", str(uuid.uuid4())),
            "scan_type": "dpia",
            "timestamp": assessment_results.get("timestamp", datetime.now().isoformat()),
            "status": "completed",
            "findings": [],
            "summary": {
                "risk_level": assessment_results.get("overall_risk_level", "Medium"),
                "score": assessment_results.get("overall_percentage", 5.0),
                "dpia_required": assessment_results.get("dpia_required", True),
                "category_scores": assessment_results.get("category_scores", {}),
                "recommendations": assessment_results.get("recommendations", [])
            },
            "metadata": {
                "scan_source": "dpia_online_report",
                "language": "en",
                "answers": assessment_results.get("answers", {})
            },
            "report_data": assessment_results
        }
        
        # Save to database
        success = results_aggregator.save_scan_results(scan_entry)
        return success
    except Exception as e:
        st.error(f"Error saving to database: {str(e)}")
        return False

def run_enhanced_dpia():
    """Run the enhanced DPIA form with crash prevention"""
    
    st.title("Data Protection Impact Assessment (DPIA)")
    st.markdown("""
    <div style="background-color: #e0f7fa; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #00bcd4;">
        <h3 style="color: #00838f; margin-top: 0; margin-bottom: 10px;">What is a DPIA?</h3>
        <p style="margin: 0;">A Data Protection Impact Assessment (DPIA) is a process required under the GDPR to identify and 
        minimize data protection risks in your project. This step-by-step assessment will help you evaluate the privacy impacts 
        of your data processing activities.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we're in results display mode
    if 'dpia_display_results' in st.session_state and st.session_state.dpia_display_results:
        display_assessment_results(
            st.session_state.dpia_results, 
            st.session_state.dpia_report_data
        )
        
        if st.button("Start New Assessment", type="primary"):
            for key in st.session_state.keys():
                if key.startswith('dpia_'):
                    del st.session_state[key]
            st.rerun()
        return
    
    # Initialize scanner
    try:
        scanner = DPIAScanner(language='en')
        assessment_categories = scanner._get_assessment_categories()
    except Exception as e:
        st.error(f"Error initializing scanner: {str(e)}")
        st.warning("Using simplified assessment categories instead.")
        assessment_categories = get_default_categories()
    
    # Initialize answers in session state
    if 'dpia_answers' not in st.session_state:
        st.session_state.dpia_answers = {}
        
    # Ensure all answer categories are properly initialized
    for category, meta in assessment_categories.items():
        question_count = len(meta.get('questions', []))
        prev_answers = st.session_state.dpia_answers.get(category, [])
        st.session_state.dpia_answers[category] = [
            prev_answers[i] if i < len(prev_answers) and isinstance(prev_answers[i], int) and 0 <= prev_answers[i] <= 2 else 0
            for i in range(question_count)
        ]
    
    # Project Information
    with st.expander("Project Information", expanded=True):
        st.subheader("Project Details")
        
        # Initialize admin info
        if 'dpia_admin_info' not in st.session_state:
            st.session_state.dpia_admin_info = {}
        
        admin_info = st.session_state.dpia_admin_info
        
        # Project details in two columns
        col1, col2 = st.columns(2)
        with col1:
            admin_info["project_name"] = st.text_input(
                "Project Name", 
                value=admin_info.get("project_name", ""),
                key="dpia_project_name",
                help="Name of the project or processing activity"
            )
            
            admin_info["organization"] = st.text_input(
                "Organization", 
                value=admin_info.get("organization", ""),
                key="dpia_organization",
                help="Your company or organization name"
            )
        
        with col2:
            admin_info["department"] = st.text_input(
                "Department", 
                value=admin_info.get("department", ""),
                key="dpia_department",
                help="Department responsible for the processing"
            )
            
            # Current date as default
            try:
                date_value = admin_info.get("date", datetime.now().date())
                if isinstance(date_value, str):
                    date_value = datetime.datetime.strptime(date_value, "%Y-%m-%d").date()
            except:
                date_value = datetime.now().date()
                
            admin_info["date"] = st.date_input(
                "Assessment Date", 
                value=date_value,
                key="dpia_date"
            )
        
        # Project description
        admin_info["description"] = st.text_area(
            "Project Description", 
            value=admin_info.get("description", ""),
            key="dpia_description",
            help="Brief description of the project and its purposes",
            height=100
        )
        
        # Contact details
        admin_info["contact_person"] = st.text_input(
            "Contact Person", 
            value=admin_info.get("contact_person", ""),
            key="dpia_contact",
            help="Person responsible for this DPIA"
        )
        
        admin_info["email"] = st.text_input(
            "Contact Email", 
            value=admin_info.get("email", ""),
            key="dpia_email",
            help="Email address for DPIA-related communications"
        )
        
        # Update session state
        st.session_state.dpia_admin_info = admin_info
    
    # Assessment form instructions
    st.subheader("Assessment Questions")
    st.info("Answer all questions below and submit to generate your DPIA report.")
    
    # Create tabs for each category
    category_tabs = st.tabs([assessment_categories[cat]['name'] for cat in assessment_categories])
    
    # Create form content in each tab
    for i, category in enumerate(assessment_categories):
        with category_tabs[i]:
            st.markdown(f"### {assessment_categories[category]['name']}")
            st.markdown(f"*{assessment_categories[category]['description']}*")
            st.markdown("---")
            
            # Show questions for this category
            for q_idx, question_text in enumerate(assessment_categories[category]['questions']):
                st.markdown(f"**{question_text}**")
                
                options = ["No", "Partially", "Yes"]
                stored_value = st.session_state.dpia_answers[category][q_idx]
                
                # Safe index
                index = stored_value if isinstance(stored_value, int) and 0 <= stored_value < len(options) else 0
                
                # Use radio buttons for better UX
                answer = st.radio(
                    "Answer:",
                    options,
                    index=index,
                    key=f"dpia_radio_{category}_{q_idx}",
                    horizontal=True,
                    label_visibility="collapsed"
                )
                
                st.session_state.dpia_answers[category][q_idx] = options.index(answer)
                st.markdown("---")
    
    # Submission area with clear instructions
    st.subheader("Submit Assessment")
    st.markdown("Click the button below to process your assessment and generate a report.")
    
    # Prevent double-clicking issues by tracking submission state
    if 'dpia_is_processing' not in st.session_state:
        st.session_state.dpia_is_processing = False
    
    # Validate if project name is provided
    admin_info = st.session_state.dpia_admin_info
    required_fields = ["project_name", "organization"]
    missing_fields = [field for field in required_fields if not admin_info.get(field)]
    
    if missing_fields:
        st.warning(f"Please complete the following required fields: {', '.join(missing_fields)}")
    
    # Add a submit button with disabled state during processing
    submit_button = st.button(
        "Process & Generate Report", 
        type="primary", 
        use_container_width=True,
        disabled=st.session_state.dpia_is_processing or bool(missing_fields)
    )
    
    if submit_button:
        st.session_state.dpia_is_processing = True
        
        # Create a progress bar and status display
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.write("Starting assessment processing...")
        
        try:
            # Step 1: Prepare assessment data
            progress_bar.progress(0.2)
            status_text.write("Step 1/4: Preparing assessment data...")
            
            # Create a deep copy of the answers
            answers = {}
            for category, values in st.session_state.dpia_answers.items():
                answers[category] = list(values)
            
            # Process assessment with scanner
            progress_bar.progress(0.4)
            status_text.write("Step 2/4: Generating assessment...")
            
            try:
                assessment_results = scanner.perform_assessment(answers=answers)
                
                # Add required metadata
                scan_id = str(uuid.uuid4())
                timestamp = datetime.now().isoformat()
                
                if 'scan_id' not in assessment_results:
                    assessment_results['scan_id'] = scan_id
                if 'timestamp' not in assessment_results:
                    assessment_results['timestamp'] = timestamp
                if 'answers' not in assessment_results:
                    assessment_results['answers'] = answers
                
                # Add admin info
                assessment_results['admin_info'] = st.session_state.dpia_admin_info
            except Exception as scan_error:
                st.warning(f"Scanner error: {str(scan_error)}. Using simplified assessment.")
                assessment_results = generate_simplified_assessment(answers)
                assessment_results['admin_info'] = st.session_state.dpia_admin_info
            
            # Generate report data
            progress_bar.progress(0.6)
            status_text.write("Step 3/4: Generating report data...")
            
            report_data = generate_report_data(assessment_results)
            
            # Save to database
            progress_bar.progress(0.8)
            status_text.write("Step 4/4: Saving to database...")
            
            try:
                db_success = save_assessment_to_db(assessment_results)
                if db_success:
                    st.success("Assessment saved to database!")
                else:
                    st.info("Results will be available for this session only.")
            except Exception as db_error:
                st.info("Database connection not available. Results will be available for this session only.")
            
            # Store results in session state
            progress_bar.progress(1.0)
            status_text.write("Assessment completed successfully!")
            
            # Reset processing flag first to avoid state issues
            st.session_state.dpia_is_processing = False
            
            # Then store results
            st.session_state.dpia_results = assessment_results
            st.session_state.dpia_report_data = report_data
            st.session_state.dpia_display_results = True
            
            # Show success message and button
            st.success("✅ Assessment completed successfully!")
            
            if st.button("View Results", type="primary"):
                st.rerun()
                
        except Exception as e:
            # Handle unexpected errors
            st.error(f"Error processing assessment: {str(e)}")
            
            # Reset processing flag so user can try again
            st.session_state.dpia_is_processing = False
            
            # Add recovery option
            if st.button("Try Again", type="primary"):
                st.rerun()

def display_assessment_results(results, report_data):
    """Display DPIA assessment results with visualizations"""
    
    st.title("DPIA Assessment Results")
    
    # Get admin info
    admin_info = results.get('admin_info', {})
    
    # Display project information
    st.markdown(f"""
    ### Project: {admin_info.get('project_name', 'DPIA Assessment')}
    **Organization:** {admin_info.get('organization', 'Not specified')}  
    **Department:** {admin_info.get('department', 'Not specified')}  
    **Assessment Date:** {admin_info.get('date', 'Not specified')}  
    **Contact:** {admin_info.get('contact_person', 'Not specified')}
    """)
    
    # Display Project Description if available
    if admin_info.get('description'):
        with st.expander("Project Description", expanded=False):
            st.write(admin_info.get('description'))
    
    # Display overall risk level with colored badge
    risk_level = results.get('overall_risk_level', 'Medium')
    risk_color = {
        'High': 'red',
        'Medium': 'orange',
        'Low': 'green'
    }.get(risk_level, 'blue')
    
    st.markdown(f"""
    <div style="margin-bottom: 20px;">
        <span style="background-color: {risk_color}; color: white; padding: 6px 12px; border-radius: 16px; font-weight: bold;">
            {risk_level} Risk
        </span>
        <span style="margin-left: 15px; font-size: 1.2em;">
            Overall Score: {results.get('overall_percentage', 5.0):.1f}/10
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # DPIA Required status
    dpia_required = results.get('dpia_required', True)
    st.markdown(f"""
    <div style="margin-bottom: 20px; padding: 15px; border-radius: 8px; background-color: {'#ffebee' if dpia_required else '#e8f5e9'}; border-left: 4px solid {'#f44336' if dpia_required else '#4caf50'};">
        <h3 style="margin-top: 0; color: {'#d32f2f' if dpia_required else '#2e7d32'};">
            {'DPIA is Required' if dpia_required else 'DPIA is Not Required'}
        </h3>
        <p>
            {'Based on your answers, a formal Data Protection Impact Assessment (DPIA) is required for this project under GDPR Article 35.' if dpia_required else 'Based on your answers, this project does not appear to require a formal DPIA under GDPR Article 35, but best practice suggests maintaining privacy documentation.'}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display risk scores by category in a table
    st.subheader("Risk Assessment by Category")
    
    category_scores = results.get('category_scores', {})
    
    if category_scores:
        # Prepare data for table
        categories = []
        risk_levels = []
        scores = []
        
        for category, score_data in category_scores.items():
            # Use a nicer display name for the category
            display_name = category.replace('_', ' ').title()
            categories.append(display_name)
            
            # Get risk level and score
            risk_level = score_data.get('risk_level', 'Medium')
            risk_levels.append(risk_level)
            
            # Calculate percentage score out of 10
            score = score_data.get('percentage', 5.0)
            scores.append(f"{score:.1f}/10")
        
        # Create a DataFrame for the table
        import pandas as pd
        risk_df = pd.DataFrame({
            'Category': categories,
            'Risk Level': risk_levels,
            'Score': scores
        })
        
        # Apply styling to risk levels
        def highlight_risk(val):
            if val == 'High':
                return 'background-color: #ffebee; color: #c62828; font-weight: bold'
            elif val == 'Medium':
                return 'background-color: #fff8e1; color: #ff8f00; font-weight: bold'
            elif val == 'Low':
                return 'background-color: #e8f5e9; color: #2e7d32; font-weight: bold'
            return ''
        
        # Display styled table
        st.table(risk_df.style.applymap(highlight_risk, subset=['Risk Level']))
    else:
        st.info("No category risk scores available")
    
    # Display key recommendations
    st.subheader("Key Recommendations")
    
    recommendations = results.get('recommendations', [])
    if recommendations:
        for rec in recommendations:
            st.markdown(f"- {rec}")
    else:
        st.info("No specific recommendations available")
    
    # Report download section
    st.subheader("Download Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # PDF report generation
        if st.button("Generate PDF Report", use_container_width=True):
            with st.spinner("Generating PDF report..."):
                try:
                    # Generate PDF report
                    pdf_data = generate_pdf_report(results)
                    
                    if pdf_data:
                        st.success("PDF report generated successfully!")
                        st.download_button(
                            label="Download PDF Report",
                            data=pdf_data,
                            file_name=f"dpia_report_{results.get('scan_id', 'report')}.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.error("Failed to generate PDF report.")
                except Exception as e:
                    st.error(f"Error generating PDF report: {str(e)}")
    
    with col2:
        # JSON Export
        if st.button("Export JSON Data", use_container_width=True):
            try:
                # Prepare export data
                export_data = {
                    "assessment_id": results.get('scan_id', str(uuid.uuid4())),
                    "timestamp": results.get('timestamp', datetime.now().isoformat()),
                    "project_name": admin_info.get('project_name', 'DPIA Assessment'),
                    "organization": admin_info.get('organization', ''),
                    "overall_risk": {
                        "level": results.get('overall_risk_level', 'Medium'),
                        "score": results.get('overall_percentage', 5.0),
                        "dpia_required": results.get('dpia_required', True)
                    },
                    "category_scores": results.get('category_scores', {}),
                    "recommendations": results.get('recommendations', [])
                }
                
                # Convert to JSON string
                json_data = json.dumps(export_data, indent=2)
                
                st.success("JSON data ready for download")
                st.download_button(
                    label="Download JSON Data",
                    data=json_data,
                    file_name=f"dpia_data_{results.get('scan_id', 'data')}.json",
                    mime="application/json"
                )
            except Exception as e:
                st.error(f"Error preparing JSON data: {str(e)}")

def generate_simplified_assessment(answers):
    """Generate a simplified assessment result when the scanner fails"""
    scan_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    # Calculate scores for each category
    category_scores = {}
    total_score = 0
    total_questions = 0
    
    for category, answer_values in answers.items():
        category_score = sum(answer_values)
        max_possible = len(answer_values) * 2
        percentage = (category_score / max_possible) * 10 if max_possible > 0 else 0
        
        risk_level = "High" if percentage >= 7 else ("Medium" if percentage >= 4 else "Low")
        
        category_scores[category] = {
            'score': category_score,
            'max_possible': max_possible,
            'percentage': percentage,
            'risk_level': risk_level
        }
        
        total_score += category_score
        total_questions += len(answer_values)
    
    # Calculate overall score
    max_total = total_questions * 2
    overall_percentage = (total_score / max_total) * 10 if max_total > 0 else 0
    
    # Determine overall risk level
    if overall_percentage >= 7:
        overall_risk = "High"
    elif overall_percentage >= 4:
        overall_risk = "Medium"
    else:
        overall_risk = "Low"
    
    # Generate simplified recommendations
    recommendations = []
    
    # Add general recommendations based on risk level
    if overall_risk == "High":
        recommendations.append("Conduct a full DPIA with external DPO consultation.")
        recommendations.append("Implement comprehensive data protection measures before proceeding.")
        recommendations.append("Consider redesigning high-risk aspects of the project.")
    elif overall_risk == "Medium":
        recommendations.append("Document all processing activities in detail.")
        recommendations.append("Implement additional safeguards for sensitive data.")
        recommendations.append("Consider consulting with privacy experts.")
    else:
        recommendations.append("Maintain documentation of this assessment for compliance.")
        recommendations.append("Regularly review data handling practices.")
    
    # Add category-specific recommendations
    for category, score_data in category_scores.items():
        if score_data['risk_level'] == "High":
            category_name = category.replace('_', ' ').title()
            recommendations.append(f"Address high risk issues in the {category_name} category.")
    
    # Determine if DPIA is required
    dpia_required = overall_percentage >= 5.0
    
    # Build result structure
    return {
        'scan_id': scan_id,
        'timestamp': timestamp,
        'overall_risk_level': overall_risk,
        'overall_percentage': overall_percentage,
        'dpia_required': dpia_required,
        'category_scores': category_scores,
        'recommendations': recommendations,
        'answers': answers
    }

def generate_report_data(assessment_results):
    """Generate report data structure from assessment results"""
    
    admin_info = assessment_results.get('admin_info', {})
    
    # Create a basic report structure
    report_data = {
        'scan_id': assessment_results.get('scan_id', ''),
        'timestamp': assessment_results.get('timestamp', ''),
        'title': 'Data Protection Impact Assessment (DPIA) Report',
        'subtitle': f"Project: {admin_info.get('project_name', 'Not specified')}",
        'organization': admin_info.get('organization', 'Not specified'),
        'department': admin_info.get('department', ''),
        'contact_person': admin_info.get('contact_person', ''),
        'assessment_date': admin_info.get('date', ''),
        'risk_level': assessment_results.get('overall_risk_level', 'Medium'),
        'score': assessment_results.get('overall_percentage', 5.0),
        'dpia_required': assessment_results.get('dpia_required', True),
        'sections': []
    }
    
    # Add Executive Summary section
    report_data['sections'].append({
        'title': 'Executive Summary',
        'content': f"""
        This Data Protection Impact Assessment (DPIA) has been conducted for {admin_info.get('project_name', 'the specified project')}. 
        The assessment evaluated various aspects of data processing to identify and mitigate privacy risks.
        
        Overall Risk Level: {assessment_results.get('overall_risk_level', 'Medium')}
        Overall Score: {assessment_results.get('overall_percentage', 5.0):.1f}/10
        
        {'Based on this assessment, a formal DPIA is required under GDPR Article 35.' 
        if assessment_results.get('dpia_required', True) else 
        'Based on this assessment, a formal DPIA is not required under GDPR Article 35, but privacy documentation should be maintained.'}
        """
    })
    
    # Add Project Description section
    if admin_info.get('description'):
        report_data['sections'].append({
            'title': 'Project Description',
            'content': admin_info.get('description', '')
        })
    
    # Add Risk Assessment section
    category_content = "The assessment evaluated the following categories:\n\n"
    
    for category, score_data in assessment_results.get('category_scores', {}).items():
        category_name = category.replace('_', ' ').title()
        risk_level = score_data.get('risk_level', 'Medium')
        score = score_data.get('percentage', 5.0)
        
        category_content += f"- {category_name}: {risk_level} Risk (Score: {score:.1f}/10)\n"
    
    report_data['sections'].append({
        'title': 'Risk Assessment',
        'content': category_content
    })
    
    # Add Recommendations section
    recommendations = assessment_results.get('recommendations', [])
    if recommendations:
        rec_content = "Based on the assessment, the following recommendations are provided:\n\n"
        for rec in recommendations:
            rec_content += f"- {rec}\n"
        
        report_data['sections'].append({
            'title': 'Recommendations',
            'content': rec_content
        })
    
    # Add Conclusion section
    report_data['sections'].append({
        'title': 'Conclusion',
        'content': f"""
        {'This project requires a full Data Protection Impact Assessment under GDPR Article 35. The identified risks should be addressed before proceeding with implementation.' 
        if assessment_results.get('dpia_required', True) else 
        'While a formal DPIA is not required for this project under GDPR Article 35, the organization should maintain appropriate documentation and implement the recommendations to ensure ongoing compliance with data protection principles.'}
        
        This assessment was conducted on {admin_info.get('date', '[date]')} by {admin_info.get('contact_person', '[assessor]')}.
        """
    })
    
    return report_data

def get_default_categories():
    """Return default assessment categories if scanner fails to load them"""
    return {
        "data_category": {
            "name": "Data Categories",
            "description": "Assessment of the types of data being processed",
            "questions": [
                "Is sensitive/special category data processed?",
                "Is data of vulnerable persons processed?",
                "Is children's data processed?",
                "Is data processed on a large scale?",
                "Are biometric or genetic data processed?"
            ]
        },
        "processing_activity": {
            "name": "Processing Activities",
            "description": "Assessment of data processing operations",
            "questions": [
                "Is there automated decision-making?",
                "Is there systematic and extensive monitoring?",
                "Are innovative technologies or organizational solutions used?",
                "Is profiling taking place?",
                "Is data combined from multiple sources?"
            ]
        },
        "rights_impact": {
            "name": "Rights and Freedoms",
            "description": "Assessment of the impact on data subjects' rights",
            "questions": [
                "Could processing lead to discrimination?",
                "Could processing lead to financial loss?",
                "Could processing lead to reputational damage?",
                "Could processing lead to physical harm?",
                "Are data subjects restricted in exercising their rights?"
            ]
        },
        "transfer_sharing": {
            "name": "Data Sharing & Transfer",
            "description": "Assessment of data sharing and transfer practices",
            "questions": [
                "Is data transferred outside the EU/EEA?",
                "Is data shared with multiple processors?",
                "Is data shared with third parties?",
                "Is there international data exchange?",
                "Is data published or made publicly available?"
            ]
        },
        "security_measures": {
            "name": "Security Measures",
            "description": "Assessment of security and control mechanisms",
            "questions": [
                "Are adequate access controls implemented?",
                "Is data encrypted (both at rest and in transit)?",
                "Is there a data breach notification procedure?",
                "Are measures in place to ensure data minimization?",
                "Are security audits performed regularly?"
            ]
        }
    }