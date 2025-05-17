"""
Enhanced Ultra Simple DPIA Form

This is a completely reliable DPIA form implementation that fixes the selectbox duplicate ID issues.
It uses unique key generation to avoid any Streamlit errors.
"""

import streamlit as st
import os
import json
import uuid
import time
from datetime import datetime
from typing import Dict, List, Any

# Import scanner and report functions with clear naming to avoid conflicts
from services.dpia_scanner import DPIAScanner, generate_dpia_report
from services.report_generator import generate_report as generate_pdf_report
from utils.i18n import get_text, _

# Configure Streamlit to trace all errors
import traceback
st.set_option('client.showErrorDetails', True)

def generate_unique_key(base, category, index):
    """Generate a guaranteed unique key for Streamlit widgets"""
    return f"{base}__{category}__{index}__{int(time.time() * 1000) % 10000}"

def run_fixed_ultra_simple_dpia():
    """Run an enhanced ultra-simplified DPIA form that fixes selectbox ID issues."""
    st.title(_("scan.dpia_assessment"))
    
    # Initialize scanner with language from session state
    scanner = DPIAScanner(language=st.session_state.get('language', 'en'))
    assessment_categories = scanner._get_assessment_categories()
    
    # Initialize answers in session state if not present
    if 'fixed_dpia_answers' not in st.session_state:
        st.session_state.fixed_dpia_answers = {}
        for category in assessment_categories:
            question_count = len(assessment_categories[category]['questions'])
            st.session_state.fixed_dpia_answers[category] = [0] * question_count
            
    st.info("📝 This is an enhanced reliable DPIA form with improved stability.")
    
    answers = {}
    
    with st.form("fixed_ultra_simple_dpia_form"):
        st.markdown("""
        ## DPIA Assessment Instructions
        
        Please answer all questions in each category below. Select values using the dropdown menus:
        - **No**: The statement doesn't apply to your processing activities
        - **Partially**: The statement partially applies to your processing activities
        - **Yes**: The statement fully applies to your processing activities
        
        Click the Submit button at the bottom when you've completed all questions.
        """)
        
        # Create tabs for each category
        tab_labels = [assessment_categories[cat]['name'] for cat in assessment_categories]
        tabs = st.tabs(tab_labels)
        
        # Fill each tab with questions
        for i, category in enumerate(assessment_categories):
            with tabs[i]:
                st.markdown(f"### {assessment_categories[category]['name']}")
                st.markdown(f"*{assessment_categories[category]['description']}*")
                st.markdown("---")
                
                category_answers = []
                for q_idx, question in enumerate(assessment_categories[category]['questions']):
                    # Get the current value from session state with fallback to default
                    current_val = st.session_state.fixed_dpia_answers[category][q_idx]
                    
                    # Important: Generate a unique key for this selectbox
                    unique_key = generate_unique_key("fixed_dpia", category, q_idx)
                    
                    # Display the question
                    st.markdown(f"**{question}**")
                    
                    # Create the selectbox with unique key
                    options = ["No", "Partially", "Yes"]
                    selected = st.selectbox(
                        "Select answer:", 
                        options,
                        index=current_val,
                        key=unique_key
                    )
                    
                    # Store the selected value
                    value = options.index(selected)
                    st.session_state.fixed_dpia_answers[category][q_idx] = value
                    category_answers.append(value)
                    st.markdown("---")
                
                # Store the answers for this category
                answers[category] = category_answers
        
        # Submit button
        submit = st.form_submit_button("Submit DPIA Assessment", type="primary", use_container_width=True)

    # Handle form submission
    if submit:
        # Validate that all questions are answered
        incomplete = any(len(v) == 0 for v in answers.values())
        if incomplete:
            st.error("❌ Please complete all questions in each category before submitting.")
            return
        
        # Set the form submitted flag
        st.session_state.fixed_dpia_form_submitted = True
        
        # Store answers in session state
        for category in assessment_categories:
            if category in answers:
                st.session_state.fixed_dpia_answers[category] = answers[category]
        
        # Rerun the app to process the submission
        st.rerun()

    # Process form submission
    if 'fixed_dpia_form_submitted' in st.session_state and st.session_state.fixed_dpia_form_submitted:
        # Add debug message if needed
        # st.write("Processing form submission...")
        # st.write(f"Answers: {st.session_state.fixed_dpia_answers}")
        
        # Clear the submission flag to prevent endless processing
        del st.session_state.fixed_dpia_form_submitted
        
        try:
            with st.spinner(_("scan.dpia_processing")):
                # Get a direct reference to the answers to avoid any chance of them changing
                answers_copy = {}
                for category, values in st.session_state.fixed_dpia_answers.items():
                    answers_copy[category] = list(values)  # Make explicit copy
                
                assessment_params = {
                    "answers": answers_copy,
                    "language": st.session_state.get('language', 'en')
                }
                
                # Perform assessment
                assessment_results = scanner.perform_assessment(**assessment_params)
                
                # Add a unique ID if missing
                if "scan_id" not in assessment_results:
                    assessment_results["scan_id"] = str(uuid.uuid4())
                
                # Add timestamp if missing
                if "timestamp" not in assessment_results:
                    assessment_results["timestamp"] = datetime.utcnow().isoformat()
                
                # Generate report data
                report_data = generate_dpia_report(assessment_results)
                
                # Save results in session state
                st.session_state.dpia_results = assessment_results
                st.session_state.dpia_report_data = report_data
                st.session_state.dpia_form_submitted = True
            
            # Display results directly without rerunning
            st.success("✅ Assessment completed! Showing results...")
            display_dpia_results(
                st.session_state.dpia_results,
                st.session_state.dpia_report_data,
                scanner
            )
        
        except Exception as e:
            st.error(f"Error processing DPIA assessment: {str(e)}")
            st.exception(e)
            st.write("Exception details:")
            st.code(traceback.format_exc())

    # Display results if already processed
    elif 'dpia_form_submitted' in st.session_state and st.session_state.dpia_form_submitted:
        try:
            display_dpia_results(
                st.session_state.dpia_results,
                st.session_state.dpia_report_data,
                scanner
            )
        except Exception as e:
            st.error(f"Error displaying DPIA results: {str(e)}")
            if st.button("Retry Assessment", type="primary"):
                for key in ['dpia_form_submitted', 'dpia_results', 'dpia_report_data']:
                    st.session_state.pop(key, None)
                st.rerun()

def display_dpia_results(assessment_results, report_data, scanner):
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
                    {assessment_results["overall_percentage"]:.1f}/10
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Category breakdown
    st.subheader("Risk Analysis by Category")
    
    for category, scores in assessment_results["category_scores"].items():
        category_name = scanner.assessment_categories[category]["name"]
        percentage = scores["percentage"]
        risk_level = scores["risk_level"]
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
                <div style="width: {percentage*10}%; height: 100%; background-color: {risk_color};"></div>
            </div>
            <div style="display: flex; justify-content: flex-end; margin-top: 2px;">
                <span style="font-size: 12px; color: #6b7280;">{percentage:.1f}/10</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Recommendations
    st.subheader("Key Findings & Recommendations")
    
    if assessment_results["recommendations"]:
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
        
        # Download button with unique key
        unique_download_key = f"dpia_download_report_button_{int(time.time() * 1000)}"
        if st.download_button(
            label="📄 Download DPIA Report PDF",
            data=pdf_data,
            file_name=report_filename,
            mime="application/pdf",
            use_container_width=True,
            type="primary",
            key=unique_download_key
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
    
    # Action buttons with unique keys
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("New Assessment", use_container_width=True, key=f"new_assessment_btn_{int(time.time() * 1000)}"):
            # Clear current assessment data
            if 'fixed_dpia_answers' in st.session_state:
                del st.session_state.fixed_dpia_answers
            if 'dpia_answers' in st.session_state:
                del st.session_state.dpia_answers
            if 'dpia_results' in st.session_state:
                del st.session_state.dpia_results
            if 'dpia_report_data' in st.session_state:
                del st.session_state.dpia_report_data
            if 'dpia_form_submitted' in st.session_state:
                del st.session_state.dpia_form_submitted
            # Rerun
            st.rerun()
    
    with col2:
        if st.button("View History", use_container_width=True, key=f"view_history_btn_{int(time.time() * 1000)}"):
            # Switch to history view
            st.session_state.selected_nav = _('history.title')
            st.rerun()

if __name__ == "__main__":
    run_fixed_ultra_simple_dpia()