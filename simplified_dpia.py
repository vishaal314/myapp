"""
Simplified DPIA (Data Protection Impact Assessment) Form

This module provides a standalone, simplified version of the DPIA form
that avoids the complex UI elements that cause form crashes.
"""

import streamlit as st
import os
import uuid
import tempfile
import json
from datetime import datetime
from typing import Dict, List, Any

from services.dpia_scanner import DPIAScanner, generate_dpia_report
from services.report_generator import generate_report
from utils.i18n import get_text, _

def run_simplified_dpia():
    """
    Run a simplified version of the DPIA assessment form.
    This function is designed to be more stable than the complex form.
    """
    st.title(_("scan.dpia_assessment"))
    
    # Initialize state for DPIA assessment if not already done
    if 'dpia_answers' not in st.session_state:
        # Initialize with default values (0 = No)
        scanner = DPIAScanner(language=st.session_state.get('language', 'en'))
        assessment_categories = scanner.assessment_categories
        
        # Create nested dictionary structure for all categories and questions
        st.session_state.dpia_answers = {}
        for category, info in assessment_categories.items():
            question_count = len(info['questions'])
            st.session_state.dpia_answers[category] = [0] * question_count
    
    # Display instructions
    st.info("This is a simplified version of the DPIA assessment form designed for better stability.")
    
    # Display a banner with instructions
    st.markdown("""
    <div style="background-color: #f8fafc; padding: 15px; border-radius: 8px; margin-bottom: 20px; 
              border-left: 4px solid #0ea5e9;">
        <h3 style="color: #0369a1; margin-top: 0;">DPIA Assessment Instructions</h3>
        <p>This form assesses if a formal Data Protection Impact Assessment is required under Article 35 of GDPR.</p>
        <p>Complete <strong>all questions</strong> in each category, then click <strong>Submit</strong> to generate your report.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create a dictionary to store answers for final submission
    answers = {}
    
    # Load the scanner to get assessment categories
    scanner = DPIAScanner(language=st.session_state.get('language', 'en'))
    assessment_categories = scanner.assessment_categories
    
    # Create expanders for each category
    for category, info in assessment_categories.items():
        with st.expander(f"{info['name']} - {info['description']}", expanded=True):
            # Create a list to store answers for this category
            category_answers = []
            
            # Show all questions in a simple table format
            for i, question in enumerate(info['questions']):
                # Get current value from session state
                current_value = st.session_state.dpia_answers[category][i]
                
                # Show question
                st.markdown(f"**Q{i+1}:** {question}")
                
                # Use a simple selectbox for answer selection
                options = ["No", "Partially", "Yes"]
                answer = st.selectbox(
                    "Your answer:",
                    options,
                    index=current_value,
                    key=f"simple_{category}_{i}"
                )
                
                # Convert answer to numerical value
                answer_value = {"No": 0, "Partially": 1, "Yes": 2}[answer]
                
                # Update session state
                st.session_state.dpia_answers[category][i] = answer_value
                
                # Add to category answers
                category_answers.append(answer_value)
                
                # Add a small separator between questions
                st.markdown("---")
            
            # Store answers for this category
            answers[category] = category_answers
    
    # Display completion status
    total_questions = sum(len(info['questions']) for info in assessment_categories.values())
    answered_questions = total_questions  # In simplified form, all questions have default values
    
    # Show progress bar
    st.subheader("Assessment Progress")
    st.progress(1.0)  # All questions have values (default or selected)
    st.success(f"All {total_questions} questions have been answered.")
    
    # Submit button
    submit_button = st.button(
        "Generate DPIA Assessment Report",
        key="simplified_dpia_submit",
        type="primary",
        use_container_width=True
    )
    
    # Process the assessment when button is clicked
    if submit_button:
        try:
            # Show processing status
            with st.spinner("Processing DPIA assessment..."):
                # Create assessment parameters
                assessment_params = {
                    "answers": answers,
                    "language": st.session_state.get('language', 'en')
                }
                
                # Perform assessment
                assessment_results = scanner.perform_assessment(**assessment_params)
                
                # Generate report data
                report_data = generate_dpia_report(assessment_results)
                
                # Save results in session state
                st.session_state.dpia_results = assessment_results
                st.session_state.dpia_report_data = report_data
            
            # Clear the form and show results
            st.empty()
            
            # Display results
            st.title(_("scan.dpia_results"))
            
            # Show overall risk level
            risk_level = assessment_results["overall_risk_level"]
            risk_color = {
                "High": _("scan.dpia_risk_color.high"),
                "Medium": _("scan.dpia_risk_color.medium"),
                "Low": _("scan.dpia_risk_color.low")
            }.get(risk_level, "#ef4444")
            
            st.markdown(f"""
            <div style="background-color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;
                       box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h2 style="margin-top: 0;">{_("scan.dpia_overall_risk")}</h2>
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <div style="width: 20px; height: 20px; border-radius: 50%; 
                             background-color: {risk_color}; margin-right: 10px;"></div>
                    <span style="font-size: 24px; font-weight: 600;">{risk_level}</span>
                </div>
                <div style="display: flex; align-items: center; margin-top: 10px;">
                    <div style="flex: 1;">
                        <h3>{_("scan.dpia_required")}</h3>
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
            
            # Display risk summary by category
            st.subheader("Risk Analysis by Category")
            
            for category, scores in assessment_results["category_scores"].items():
                category_name = scanner.assessment_categories[category]["name"]
                percentage = scores["percentage"]
                risk_level = scores["risk_level"]
                risk_color = {
                    "High": _("scan.dpia_risk_color.high"),
                    "Medium": _("scan.dpia_risk_color.medium"),
                    "Low": _("scan.dpia_risk_color.low")
                }.get(risk_level, "#ef4444")
                
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
            
            # Create download button for PDF report
            st.subheader("Download Report")
            
            report_filename = f"dpia_report_{assessment_results['scan_id']}.pdf"
            
            # Generate the report when the button is clicked
            pdf_data = generate_report(report_data)
            
            if st.download_button(
                label="📄 " + _("scan.dpia_download_report"),
                data=pdf_data,
                file_name=report_filename,
                mime="application/pdf",
                use_container_width=True,
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
            
            # Action buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(_("scan.dpia_new_assessment"), use_container_width=True):
                    # Clear current assessment data
                    if 'dpia_answers' in st.session_state:
                        del st.session_state.dpia_answers
                    if 'dpia_results' in st.session_state:
                        del st.session_state.dpia_results
                    if 'dpia_report_data' in st.session_state:
                        del st.session_state.dpia_report_data
                    # Rerun the app to show the form again
                    st.rerun()
            
            with col2:
                if st.button(_("scan.dpia_view_history"), use_container_width=True):
                    # Switch to history view
                    st.session_state.selected_nav = _('history.title')
                    st.rerun()
                    
        except Exception as e:
            st.error(f"An error occurred during DPIA assessment: {str(e)}")
            st.exception(e)

if __name__ == "__main__":
    # For testing purposes
    run_simplified_dpia()