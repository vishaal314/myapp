"""
Ultra Simple DPIA Form

This is a drastically simplified DPIA form that uses minimal UI elements to avoid crashes,
while still capturing the necessary data to generate reports.
"""

import streamlit as st
import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any

# Import scanner and report functions with clear naming to avoid conflicts
from services.dpia_scanner import DPIAScanner, generate_dpia_report
from services.report_generator import generate_report as generate_pdf_report
from utils.i18n import get_text, _

def run_ultra_simple_dpia():
    """Run an ultra-simplified DPIA form focused on reliability."""
    st.title(_("scan.dpia_assessment"))
    
    # Create a new scanner instance
    scanner = DPIAScanner(language=st.session_state.get('language', 'en'))
    
    # Check if we need to show results or form
    if 'dpia_form_submitted' in st.session_state and st.session_state.dpia_form_submitted:
        # Show results if we have them
        if 'dpia_results' in st.session_state and 'dpia_report_data' in st.session_state:
            try:
                show_dpia_results(
                    st.session_state.dpia_results,
                    st.session_state.dpia_report_data,
                    scanner
                )
                return  # Exit function after showing results
            except Exception as e:
                st.error(f"Error displaying DPIA results: {str(e)}")
                # Clear state to allow trying again
                if 'dpia_form_submitted' in st.session_state:
                    del st.session_state.dpia_form_submitted
                if 'dpia_results' in st.session_state:
                    del st.session_state.dpia_results
                if 'dpia_report_data' in st.session_state:
                    del st.session_state.dpia_report_data
    
    # Process submission if flag is set
    if 'dpia_form_processing' in st.session_state and st.session_state.dpia_form_processing:
        with st.spinner(_("scan.dpia_processing")):
            try:
                # Get answers from session state
                if 'ultra_simple_dpia_answers' not in st.session_state:
                    st.error("No assessment data found. Please complete the form.")
                    del st.session_state.dpia_form_processing
                    return
                
                # Prepare assessment parameters
                assessment_params = {
                    "answers": st.session_state.ultra_simple_dpia_answers,
                    "language": st.session_state.get('language', 'en')
                }
                
                # Perform assessment
                assessment_results = scanner.perform_assessment(**assessment_params)
                
                # Generate report data
                report_data = generate_dpia_report(assessment_results)
                
                # Save results in session state
                st.session_state.dpia_results = assessment_results
                st.session_state.dpia_report_data = report_data
                
                # Set flag to show results and clear processing flag
                st.session_state.dpia_form_submitted = True
                del st.session_state.dpia_form_processing
                
                # Force a rerun to show results cleanly
                st.rerun()
            
            except Exception as e:
                st.error(f"Error processing DPIA assessment: {str(e)}")
                st.exception(e)
                # Clear processing flag so we can try again
                if 'dpia_form_processing' in st.session_state:
                    del st.session_state.dpia_form_processing
                return
    
    # Show instruction banner
    st.info("📝 Due to form complexity, we're using a simplified version that works reliably.")
    
    # Get assessment categories
    assessment_categories = scanner._get_assessment_categories()
    
    # Initialize answer storage if needed
    if 'ultra_simple_dpia_answers' not in st.session_state:
        st.session_state.ultra_simple_dpia_answers = {}
        for category in assessment_categories:
            question_count = len(assessment_categories[category]['questions'])
            st.session_state.ultra_simple_dpia_answers[category] = [0] * question_count
    
    # Show form instructions
    st.markdown("""
    ## DPIA Assessment Instructions
    
    Please answer all questions in each category below. Select values using the dropdown menus:
    - **No**: The statement doesn't apply to your processing activities
    - **Partially**: The statement partially applies to your processing activities
    - **Yes**: The statement fully applies to your processing activities
    
    Click the Submit button at the bottom when you've completed all questions.
    """)
    
    # Create tabs for each category
    tabs = st.tabs([assessment_categories[cat]['name'] for cat in assessment_categories])
    
    # Fill each tab with questions
    for i, category in enumerate(assessment_categories):
        with tabs[i]:
            st.markdown(f"### {assessment_categories[category]['name']}")
            st.markdown(f"*{assessment_categories[category]['description']}*")
            st.markdown("---")
            
            # Create a simple interface for each question
            for q_idx, question in enumerate(assessment_categories[category]['questions']):
                # Current value for this question
                if category in st.session_state.ultra_simple_dpia_answers and \
                   len(st.session_state.ultra_simple_dpia_answers[category]) > q_idx:
                    current_val = st.session_state.ultra_simple_dpia_answers[category][q_idx]
                else:
                    current_val = 0
                
                # Display question
                st.markdown(f"**Q{q_idx+1}:** {question}")
                
                # Simple dropdown selection
                key = f"ultra_simple_{category}_{q_idx}"
                options = ["No", "Partially", "Yes"]
                answer = st.selectbox(
                    "Select answer:", 
                    options,
                    index=current_val,
                    key=key
                )
                
                # Save answer value to session state immediately
                value = options.index(answer)
                if category not in st.session_state.ultra_simple_dpia_answers:
                    st.session_state.ultra_simple_dpia_answers[category] = []
                
                # Ensure the list is long enough
                while len(st.session_state.ultra_simple_dpia_answers[category]) <= q_idx:
                    st.session_state.ultra_simple_dpia_answers[category].append(0)
                
                # Update the value
                st.session_state.ultra_simple_dpia_answers[category][q_idx] = value
                
                # Add separator
                st.markdown("---")
    
    # Submit button
    if st.button("Submit DPIA Assessment", type="primary", use_container_width=True):
        # Set processing flag and force rerun
        st.session_state.dpia_form_processing = True
        st.rerun()

def show_dpia_results(assessment_results, report_data, scanner):
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
            # Clear current assessment data
            if 'ultra_simple_dpia_answers' in st.session_state:
                del st.session_state.ultra_simple_dpia_answers
            if 'dpia_answers' in st.session_state:
                del st.session_state.dpia_answers
            if 'dpia_results' in st.session_state:
                del st.session_state.dpia_results
            if 'dpia_report_data' in st.session_state:
                del st.session_state.dpia_report_data
            # Rerun
            st.rerun()
    
    with col2:
        if st.button("View History", use_container_width=True):
            # Switch to history view
            st.session_state.selected_nav = _('history.title')
            st.rerun()

if __name__ == "__main__":
    run_ultra_simple_dpia()