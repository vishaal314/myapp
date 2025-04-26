"""
Improved DPIA Form

This module provides a clean, stable DPIA form that follows the 7-step DPIA process
while preventing crashes and UI issues. It implements a simplified questionnaire
approach with proper error handling.
"""

import streamlit as st
import os
import json
import uuid
import math
import datetime
from typing import Dict, List, Any, Optional

# Import scanner and report functions
from services.dpia_scanner import DPIAScanner
from services.report_generator import generate_pdf_report
from utils.i18n import get_text, _

def run_improved_dpia():
    """
    Run an improved DPIA form that follows the 7-step structure with crash prevention.
    """
    st.title(_("scan.dpia_assessment"))
    
    # Initialize scanner with proper language support
    scanner = DPIAScanner(language=st.session_state.get('language', 'en'))
    
    # Check if we need to show results instead of the form
    if st.session_state.get('dpia_show_results', False) and 'dpia_results' in st.session_state:
        display_assessment_results(
            st.session_state.dpia_results,
            st.session_state.dpia_report_data,
            scanner
        )
        
        # New assessment button
        if st.button("Start New Assessment", type="primary"):
            clear_session_state()
            st.rerun()
        
        return
    
    # Initialize session state for structured DPIA answers
    if 'dpia_answers' not in st.session_state:
        initialize_session_state()
    
    # Create tabs for the DPIA steps
    tabs = st.tabs([
        "1. Introduction",
        "2. Data Categories",
        "3. Processing Activities", 
        "4. Rights & Freedoms",
        "5. Data Sharing",
        "6. Security Measures",
        "7. Review & Submit"
    ])
    
    # Tab 1: Introduction
    with tabs[0]:
        st.header("Introduction")
        
        with st.expander("What is a DPIA?", expanded=True):
            st.markdown("""
            A Data Protection Impact Assessment (DPIA) is a process required under the General Data Protection Regulation (GDPR) 
            to identify and minimize data protection risks in your project. This assessment will help you determine if your 
            data processing activities pose a high risk to individuals' rights and freedoms.
            
            ### When is a DPIA required?
            - When processing is likely to result in a high risk to individuals
            - For systematic and extensive profiling with significant effects
            - For large-scale processing of special categories of data
            - For systematic monitoring of publicly accessible areas on a large scale
            
            ### This assessment will guide you through:
            1. Identifying the need for a DPIA
            2. Describing the nature, scope, context and purposes of the processing
            3. Identifying and assessing risks to individuals
            4. Identifying measures to reduce risks
            5. Recording the outcome and integrating findings
            """)
        
        # Project Information
        st.subheader("Project Information")
        
        admin_info = st.session_state.dpia_answers.get("admin_info", {})
        
        # Organizational details
        col1, col2 = st.columns(2)
        with col1:
            admin_info["project_name"] = st.text_input(
                "Project Name", 
                value=admin_info.get("project_name", ""),
                key="admin_project_name",
                help="Name of the project or processing activity"
            )
            
            admin_info["organization"] = st.text_input(
                "Organization", 
                value=admin_info.get("organization", ""),
                key="admin_organization",
                help="Your company or organization name"
            )
        
        with col2:
            admin_info["department"] = st.text_input(
                "Department", 
                value=admin_info.get("department", ""),
                key="admin_department",
                help="Department responsible for the processing"
            )
            
            # Current date as default
            try:
                date_value = admin_info.get("date", datetime.datetime.now().date())
                if isinstance(date_value, str):
                    date_value = datetime.datetime.strptime(date_value, "%Y-%m-%d").date()
            except:
                date_value = datetime.datetime.now().date()
                
            admin_info["date"] = st.date_input(
                "Assessment Date", 
                value=date_value,
                key="admin_date"
            )
        
        # Project description
        admin_info["description"] = st.text_area(
            "Project Description", 
            value=admin_info.get("description", ""),
            key="admin_description",
            help="Brief description of the project and its purposes",
            height=100
        )
        
        # Contact details
        admin_info["contact_person"] = st.text_input(
            "Contact Person", 
            value=admin_info.get("contact_person", ""),
            key="admin_contact",
            help="Person responsible for this DPIA"
        )
        
        admin_info["email"] = st.text_input(
            "Contact Email", 
            value=admin_info.get("email", ""),
            key="admin_email",
            help="Email address for DPIA-related communications"
        )
        
        # Update session state
        st.session_state.dpia_answers["admin_info"] = admin_info
    
    # Tab 2: Data Categories
    with tabs[1]:
        st.header("Data Categories")
        st.write("Please answer the following questions about the types of data you are processing.")
        
        # Initialize data_categories if not present
        if "data_categories" not in st.session_state.dpia_answers:
            st.session_state.dpia_answers["data_categories"] = {}
        
        data_categories = st.session_state.dpia_answers["data_categories"]
        
        # Questions with unique keys to avoid conflicts
        questions = [
            {"id": "sensitive_data", "question": "Is sensitive/special category data processed?"},
            {"id": "vulnerable_persons", "question": "Is data of vulnerable persons processed?"},
            {"id": "children_data", "question": "Is children's data processed?"},
            {"id": "large_scale", "question": "Is data processed on a large scale?"},
            {"id": "biometric", "question": "Are biometric or genetic data processed?"}
        ]
        
        for question in questions:
            q_id = question["id"]
            if q_id not in data_categories:
                data_categories[q_id] = 0
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(question["question"])
            with col2:
                options = ["No", "Partially", "Yes"]
                selected = st.selectbox(
                    "Select answer:", 
                    options=options,
                    index=data_categories[q_id],
                    key=f"dc_{q_id}"
                )
                data_categories[q_id] = options.index(selected)
        
        st.session_state.dpia_answers["data_categories"] = data_categories
    
    # Tab 3: Processing Activities
    with tabs[2]:
        st.header("Processing Activities")
        st.write("Please answer the following questions about your data processing activities.")
        
        # Initialize processing_activities if not present
        if "processing_activities" not in st.session_state.dpia_answers:
            st.session_state.dpia_answers["processing_activities"] = {}
        
        processing_activities = st.session_state.dpia_answers["processing_activities"]
        
        # Questions with unique keys
        questions = [
            {"id": "automated_decision", "question": "Is there automated decision-making?"},
            {"id": "monitoring", "question": "Is there systematic and extensive monitoring?"},
            {"id": "innovative_tech", "question": "Are innovative technologies or organizational solutions used?"},
            {"id": "profiling", "question": "Is profiling taking place?"},
            {"id": "combined_data", "question": "Is data combined from multiple sources?"}
        ]
        
        for question in questions:
            q_id = question["id"]
            if q_id not in processing_activities:
                processing_activities[q_id] = 0
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(question["question"])
            with col2:
                options = ["No", "Partially", "Yes"]
                selected = st.selectbox(
                    "Select answer:", 
                    options=options,
                    index=processing_activities[q_id],
                    key=f"pa_{q_id}"
                )
                processing_activities[q_id] = options.index(selected)
        
        st.session_state.dpia_answers["processing_activities"] = processing_activities
    
    # Tab 4: Rights and Freedoms
    with tabs[3]:
        st.header("Rights and Freedoms")
        st.write("Please answer the following questions about the impact on rights and freedoms of data subjects.")
        
        # Initialize rights_freedoms if not present
        if "rights_freedoms" not in st.session_state.dpia_answers:
            st.session_state.dpia_answers["rights_freedoms"] = {}
        
        rights_freedoms = st.session_state.dpia_answers["rights_freedoms"]
        
        # Questions with unique keys
        questions = [
            {"id": "discrimination", "question": "Could processing lead to discrimination?"},
            {"id": "financial_loss", "question": "Could processing lead to financial loss?"},
            {"id": "reputation", "question": "Could processing lead to reputational damage?"},
            {"id": "physical_harm", "question": "Could processing lead to physical harm?"},
            {"id": "rights_restriction", "question": "Are data subjects restricted in exercising their rights?"}
        ]
        
        for question in questions:
            q_id = question["id"]
            if q_id not in rights_freedoms:
                rights_freedoms[q_id] = 0
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(question["question"])
            with col2:
                options = ["No", "Partially", "Yes"]
                selected = st.selectbox(
                    "Select answer:", 
                    options=options,
                    index=rights_freedoms[q_id],
                    key=f"rf_{q_id}"
                )
                rights_freedoms[q_id] = options.index(selected)
        
        st.session_state.dpia_answers["rights_freedoms"] = rights_freedoms
    
    # Tab 5: Data Sharing
    with tabs[4]:
        st.header("Data Sharing & Transfer")
        st.write("Please answer the following questions about sharing and transferring of data.")
        
        # Initialize data_sharing if not present
        if "data_sharing" not in st.session_state.dpia_answers:
            st.session_state.dpia_answers["data_sharing"] = {}
        
        data_sharing = st.session_state.dpia_answers["data_sharing"]
        
        # Questions with unique keys
        questions = [
            {"id": "outside_eu", "question": "Is data transferred outside the EU/EEA?"},
            {"id": "multiple_processors", "question": "Is data shared with multiple processors?"},
            {"id": "third_parties", "question": "Is data shared with third parties?"},
            {"id": "international", "question": "Is there international data exchange?"},
            {"id": "public", "question": "Is data published or made publicly available?"}
        ]
        
        for question in questions:
            q_id = question["id"]
            if q_id not in data_sharing:
                data_sharing[q_id] = 0
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(question["question"])
            with col2:
                options = ["No", "Partially", "Yes"]
                selected = st.selectbox(
                    "Select answer:", 
                    options=options,
                    index=data_sharing[q_id],
                    key=f"ds_{q_id}"
                )
                data_sharing[q_id] = options.index(selected)
        
        st.session_state.dpia_answers["data_sharing"] = data_sharing
    
    # Tab 6: Security Measures
    with tabs[5]:
        st.header("Security Measures")
        st.write("Please answer the following questions about security measures and control mechanisms.")
        
        # Initialize security_measures if not present
        if "security_measures" not in st.session_state.dpia_answers:
            st.session_state.dpia_answers["security_measures"] = {}
        
        security_measures = st.session_state.dpia_answers["security_measures"]
        
        # Questions with unique keys
        questions = [
            {"id": "access_control", "question": "Are adequate access controls implemented?"},
            {"id": "encryption", "question": "Is data encrypted (both at rest and in transit)?"},
            {"id": "breach_notification", "question": "Is there a data breach notification procedure?"},
            {"id": "data_minimization", "question": "Are measures in place to ensure data minimization?"},
            {"id": "security_audits", "question": "Are security audits performed regularly?"}
        ]
        
        for question in questions:
            q_id = question["id"]
            if q_id not in security_measures:
                security_measures[q_id] = 0
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(question["question"])
            with col2:
                options = ["No", "Partially", "Yes"]
                selected = st.selectbox(
                    "Select answer:", 
                    options=options,
                    index=security_measures[q_id],
                    key=f"sm_{q_id}"
                )
                security_measures[q_id] = options.index(selected)
        
        st.session_state.dpia_answers["security_measures"] = security_measures
    
    # Tab 7: Review & Submit
    with tabs[6]:
        st.header("Review & Submit")
        st.write("Please review your answers and submit when ready.")
        
        # Check if we have incomplete data
        admin_info = st.session_state.dpia_answers.get("admin_info", {})
        required_fields = ["project_name", "organization", "description"]
        
        missing_fields = [field for field in required_fields if not admin_info.get(field)]
        
        if missing_fields:
            st.warning(f"Please complete the following required fields in the Introduction tab: {', '.join(missing_fields)}")
        
        # Submit button
        submit_col1, submit_col2 = st.columns([2, 1])
        with submit_col1:
            st.write("When you click Submit, your DPIA assessment will be processed and a report will be generated.")
        
        with submit_col2:
            submit_button = st.button(
                "Submit DPIA Assessment", 
                type="primary", 
                use_container_width=True,
                disabled=bool(missing_fields)
            )
        
        if submit_button:
            with st.spinner("Processing DPIA assessment..."):
                try:
                    # Process the assessment
                    process_dpia_assessment(scanner)
                    st.success("Assessment processed successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error processing assessment: {str(e)}")
                    st.exception(e)

def process_dpia_assessment(scanner: DPIAScanner):
    """Process the DPIA assessment with error handling"""
    
    # Verify we're not already processing
    if st.session_state.get("is_processing", False):
        st.warning("Assessment already being processed. Please wait...")
        return
    
    try:
        # Set processing flag
        st.session_state.is_processing = True
        
        # Convert the UI answers to the format expected by the scanner
        scanner_answers = {}
        
        # Function to convert UI answers to scanner format
        def convert_category_answers(category, answers):
            result = []
            for q_id, value in answers.items():
                if isinstance(value, int) and 0 <= value <= 2:
                    result.append(value)
            return result
        
        # Map our UI categories to the scanner's categories
        category_mapping = {
            "data_categories": "data_category",
            "processing_activities": "processing_activity",
            "rights_freedoms": "rights_impact",
            "data_sharing": "transfer_sharing",
            "security_measures": "security_measures"
        }
        
        # Process each category
        for ui_category, scanner_category in category_mapping.items():
            if ui_category in st.session_state.dpia_answers:
                scanner_answers[scanner_category] = convert_category_answers(
                    ui_category, 
                    st.session_state.dpia_answers[ui_category]
                )
        
        # Ensure we have all required categories
        for scanner_category in category_mapping.values():
            if scanner_category not in scanner_answers or not scanner_answers[scanner_category]:
                scanner_answers[scanner_category] = [0] * 5  # Default to 5 questions with "No" answers
        
        # Add admin info
        admin_info = st.session_state.dpia_answers.get("admin_info", {})
        
        # Prepare to call perform_assessment with the expected parameters
        # The scanner expects answers as lists of integers
        # We'll also send an empty list for file_findings
        assessment_results = scanner.perform_assessment(
            answers=scanner_answers,
            file_findings=[],  # No file findings since this is just a questionnaire
            data_source_info={
                "type": "questionnaire",
                "name": admin_info.get("project_name", "DPIA Assessment"),
                "description": admin_info.get("description", "")
            }
        )
        
        # Add admin info to results
        assessment_results["admin_info"] = admin_info
        if "scan_id" not in assessment_results:
            assessment_results["scan_id"] = str(uuid.uuid4())
        if "timestamp" not in assessment_results:
            assessment_results["timestamp"] = datetime.datetime.now().isoformat()
        
        # Generate report data
        report_data = {
            "scan_type": "dpia",
            "title": "Data Protection Impact Assessment (DPIA)",
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "project": admin_info.get("project_name", "Unnamed Project"),
            "contact": admin_info.get("contact_person", ""),
            "department": admin_info.get("department", ""),
            "results": assessment_results
        }
        
        # Save results to session state
        st.session_state.dpia_results = assessment_results
        st.session_state.dpia_report_data = report_data
        st.session_state.dpia_show_results = True
        
        # Clear processing flag
        st.session_state.is_processing = False
        
        return assessment_results
    
    except Exception as e:
        # Clear processing flag on error
        st.session_state.is_processing = False
        raise e

def display_assessment_results(assessment_results, report_data, scanner):
    """Display the results of the DPIA assessment."""
    st.title(_("scan.dpia_results"))
    
    # Overall risk summary
    risk_level = assessment_results["overall_risk_level"]
    risk_color = {
        "High": "#ef4444",
        "Medium": "#f97316",
        "Low": "#10b981"
    }.get(risk_level, "#ef4444")
    
    # Display result card
    st.markdown(f"""
    <div style="background-color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;
               box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h2 style="margin-top: 0;">Overall Risk Level</h2>
        <div style="display: flex; align-items: center; margin-bottom: 15px;">
            <div style="width: 20px; height: 20px; border-radius: 50%; 
                     background-color: {risk_color}; margin-right: 10px;"></div>
            <span style="font-size: 24px; font-weight: 600;">{risk_level}</span>
        </div>
        <div style="display: flex; align-items: center; margin-top: 10px;">
            <div style="flex: 1;">
                <h3>DPIA Required</h3>
                <p style="font-size: 18px; font-weight: 500;">
                    {"Yes" if assessment_results["dpia_required"] else "No"}
                </p>
            </div>
            <div style="flex: 1;">
                <h3>Risk Score</h3>
                <p style="font-size: 18px; font-weight: 500;">
                    {assessment_results["risk_percentage"]:.1f}/100
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Category breakdown
    st.subheader("Risk Analysis by Category")
    
    for category, scores in assessment_results["category_scores"].items():
        # Get the category name, handling both formats of category keys
        if category in scanner.assessment_categories:
            category_name = scanner.assessment_categories[category]["name"]
        else:
            # Fallback for categories not found directly
            # Map back from internal categories to display names
            category_mapping = {
                "data_category": "Data Categories",
                "processing_activity": "Processing Activities",
                "rights_impact": "Rights and Freedoms",
                "transfer_sharing": "Data Sharing & Transfer",
                "security_measures": "Security Measures"
            }
            category_name = category_mapping.get(category, category.replace("_", " ").title())
        
        # Extract score values safely
        percentage = scores.get("percentage", 0) * 10  # Convert from 0-10 to 0-100 scale
        risk_level = scores.get("risk_level", "Low")
        risk_color = {
            "High": "#ef4444",
            "Medium": "#f97316",
            "Low": "#10b981"
        }.get(risk_level, "#ef4444")
        
        # Display category risk bar
        st.markdown(f"""
        <div style="margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                <span style="font-weight: 500;">{category_name}</span>
                <span style="color: {risk_color}; font-weight: 500;">{risk_level}</span>
            </div>
            <div style="height: 8px; background-color: #f3f4f6; border-radius: 4px; overflow: hidden;">
                <div style="width: {percentage}%; height: 100%; background-color: {risk_color};"></div>
            </div>
            <div style="display: flex; justify-content: flex-end; margin-top: 2px;">
                <span style="font-size: 12px; color: #6b7280;">{percentage:.1f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Recommendations
    st.subheader("Key Findings & Recommendations")
    
    if assessment_results.get("recommendations", []):
        for i, recommendation in enumerate(assessment_results["recommendations"][:5]):  # Top 5
            severity = recommendation["severity"]
            category = recommendation["category"]
            description = recommendation["description"]
            
            risk_color = {
                "High": "#ef4444",
                "Medium": "#f97316",
                "Low": "#10b981"
            }.get(severity, "#ef4444")
            
            st.markdown(f"""
            <div style="background-color: white; padding: 15px; border-radius: 8px; margin-bottom: 10px;
                       box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-left: 4px solid {risk_color};">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span style="font-weight: 500; color: #4b5563;">{category}</span>
                    <span style="color: {risk_color}; font-weight: 500;">{severity}</span>
                </div>
                <p style="margin: 0;">{description}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No specific recommendations were generated.")
    
    # Report download section
    st.markdown("""
    <div style="margin-top: 40px; margin-bottom: 20px;">
        <h2>Download Full Report</h2>
        <p style="color: #4b5563;">The complete report includes detailed findings, all recommendations, and compliance guidance.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Generate PDF report
    try:
        report_filename = f"dpia_report_{assessment_results['scan_id']}.pdf"
        
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
    
    # Important notice
    st.info("⚠️ Important: This report will not be saved automatically. Please download it now for your records.")
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("New Assessment", use_container_width=True):
            clear_session_state()
            st.rerun()
    
    with col2:
        if st.button("View History", use_container_width=True):
            # Switch to history view
            st.session_state.selected_nav = _('history.title')
            st.rerun()

def initialize_session_state():
    """Initialize the session state for the DPIA form"""
    st.session_state.dpia_answers = {
        "admin_info": {
            "project_name": "",
            "organization": "",
            "department": "",
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "description": "",
            "contact_person": "",
            "email": ""
        },
        "data_categories": {},
        "processing_activities": {},
        "rights_freedoms": {},
        "data_sharing": {},
        "security_measures": {}
    }
    st.session_state.dpia_show_results = False

def clear_session_state():
    """Clear the DPIA form session state"""
    if 'dpia_answers' in st.session_state:
        del st.session_state.dpia_answers
    if 'dpia_results' in st.session_state:
        del st.session_state.dpia_results
    if 'dpia_report_data' in st.session_state:
        del st.session_state.dpia_report_data
    if 'dpia_show_results' in st.session_state:
        del st.session_state.dpia_show_results
    if 'is_processing' in st.session_state:
        del st.session_state.is_processing

def highlight_risk_level(val):
    """Apply color styling to risk levels"""
    color_map = {
        "High": "#ef4444",
        "Medium": "#f97316",
        "Low": "#10b981"
    }
    color = color_map.get(val, "#4b5563")
    return f'color: {color}; font-weight: bold;'

if __name__ == "__main__":
    run_improved_dpia()