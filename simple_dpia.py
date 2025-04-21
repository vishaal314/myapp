"""
Simple DPIA Form

This is an extremely simplified DPIA form implementation with minimal code,
designed to just work at the most basic level.
"""

import streamlit as st
import uuid
from datetime import datetime
from typing import Dict, List, Any
import traceback
import json

# Import scanner and report functions with clear naming to avoid conflicts
from services.dpia_scanner import DPIAScanner, generate_dpia_report
from services.report_generator import generate_report as generate_pdf_report
from utils.i18n import get_text, _

# Enable tracing for easier debugging
st.set_option('client.showErrorDetails', True)

def run_simple_dpia():
    """Run a very simple DPIA form with minimal complexity."""
    
    st.title("DPIA Assessment")

    if st.checkbox("Debug: Show Session State", value=False, key="debug_show_session"):
        st.write(dict((k, v) for k, v in st.session_state.items() if not k.startswith('_')))

    if st.checkbox("Debug: Reset Form", value=False, key="debug_reset_form"):
        for key in list(st.session_state.keys()):
            if key.startswith('simple_dpia') or key in ['assessment_results', 'report_data', 'display_results']:
                del st.session_state[key]
        st.success("Form state reset")
        st.rerun()

    try:
        scanner = DPIAScanner(language='en')
        assessment_categories = scanner._get_assessment_categories()
    except Exception as e:
        st.error(f"Error initializing DPIA scanner: {str(e)}")
        st.code(traceback.format_exc())
        return

    if 'simple_dpia_answers' not in st.session_state:
        st.session_state.simple_dpia_answers = {}

    # Ensure answers are correctly initialized or updated
    for category, meta in assessment_categories.items():
        question_count = len(meta.get('questions', []))
        prev_answers = st.session_state.simple_dpia_answers.get(category, [])
        st.session_state.simple_dpia_answers[category] = [
            prev_answers[i] if i < len(prev_answers) and isinstance(prev_answers[i], int) and 0 <= prev_answers[i] <= 2 else 0
            for i in range(question_count)
        ]

    st.info("This is a simplified DPIA assessment form. Please answer all questions and click Submit.")

    if 'display_results' in st.session_state and st.session_state.display_results and 'assessment_results' in st.session_state:
        try:
            display_assessment_results(
                st.session_state.assessment_results,
                st.session_state.report_data,
                scanner
            )

            if st.button("Start New Assessment", type="primary"):
                for key in ['simple_dpia_answers', 'assessment_results', 'report_data', 'display_results']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
            return
        except Exception as e:
            st.error(f"Error displaying results: {str(e)}")
            st.exception(e)
    
    # Show the assessment form
    st.subheader("Assessment Questions")
    
    # Create tabs for each category
    tab_labels = [assessment_categories[cat]['name'] for cat in assessment_categories]
    tabs = st.tabs(tab_labels)
    
    # Create form content in each tab
    for i, category in enumerate(assessment_categories):
        with tabs[i]:
            st.markdown(f"### {assessment_categories[category]['name']}")
            st.markdown(f"*{assessment_categories[category]['description']}*")
            st.markdown("---")
            
            # Show questions for this category
            for q_idx, question_text in enumerate(assessment_categories[category]['questions']):
                st.markdown(f"**{question_text}**")
                
                options = ["No", "Partially", "Yes"]
                stored_value = st.session_state.simple_dpia_answers[category][q_idx]

                # Safe index
                index = stored_value if isinstance(stored_value, int) and 0 <= stored_value < len(options) else 0

                answer = st.radio(
                    "Answer:",
                    options,
                    index=index,
                    key=f"radio_{category}_{q_idx}",
                    horizontal=True,
                    label_visibility="collapsed"
                )

                st.session_state.simple_dpia_answers[category][q_idx] = options.index(answer)
                st.markdown("---")
    
    # Add a submit button
    if st.button("Submit Assessment", type="primary", use_container_width=True):
        # Process the assessment
        with st.spinner("Processing assessment..."):
            try:
                # Get answers from session state - make a deep copy to avoid reference issues
                answers = {}
                for category, values in st.session_state.simple_dpia_answers.items():
                    answers[category] = list(values)
                
                # Show what we're submitting
                st.write("Processing the following answers:")
                st.write(f"**Answer structure:** {json.dumps(answers, indent=2)}")
                
                # First, generate our own result to verify the calculation works
                st.write("Calculating scores...")
                
                # Calculate scores for each category
                total_score = 0
                high_risk_count = 0
                medium_risk_count = 0
                low_risk_count = 0
                total_questions = 0
                category_scores = {}
                
                for category, answer_values in answers.items():
                    category_score = sum(answer_values)
                    max_possible = len(answer_values) * 2
                    percentage = (category_score / max_possible) * 10
                    
                    if percentage >= 7:
                        risk_level = "High"
                        high_risk_count += 1
                    elif percentage >= 4:
                        risk_level = "Medium"
                        medium_risk_count += 1
                    else:
                        risk_level = "Low"
                        low_risk_count += 1
                    
                    category_scores[category] = {
                        "score": category_score,
                        "max_possible": max_possible,
                        "percentage": percentage,
                        "risk_level": risk_level
                    }
                    
                    total_score += category_score
                    total_questions += len(answer_values)
                
                # Calculate overall risk score
                max_total = total_questions * 2
                overall_percentage = (total_score / max_total) * 10 if max_total > 0 else 0
                
                if overall_percentage >= 7:
                    overall_risk = "High"
                elif overall_percentage >= 4:
                    overall_risk = "Medium"
                else:
                    overall_risk = "Low"
                
                st.write(f"Our calculation - Overall Risk: {overall_risk}, Score: {overall_percentage:.1f}/10")
                
                # NOW perform the actual assessment with the scanner
                st.write("Calling official scanner...")
                assessment_results = scanner.perform_assessment(answers=answers)
                
                # Make sure we have essential fields
                scan_id = str(uuid.uuid4())
                timestamp = datetime.now().isoformat()
                
                if 'scan_id' not in assessment_results:
                    assessment_results['scan_id'] = scan_id
                if 'timestamp' not in assessment_results:
                    assessment_results['timestamp'] = timestamp
                
                st.write(f"Scanner result - Overall Risk: {assessment_results['overall_risk_level']}, Score: {assessment_results['overall_percentage']:.1f}/10")
                
                # Generate report data
                st.write("Generating report data...")
                report_data = generate_dpia_report(assessment_results)
                
                # Store results in session state
                st.write("Saving results to session state...")
                st.session_state.assessment_results = assessment_results
                st.session_state.report_data = report_data
                st.session_state.display_results = True
                
                # Show success message and rerun to display results
                st.success("Assessment completed successfully! Click Continue to view results.")
                if st.button("Continue to Results", type="primary"):
                    st.rerun()
                
            except Exception as e:
                st.error(f"Error performing assessment: {str(e)}")
                st.write("Exception details:")
                st.code(traceback.format_exc())

def display_assessment_results(results, report_data, scanner):
    """Display the results of the DPIA assessment."""
    
    st.title("DPIA Assessment Results")
    
    # Overall risk level
    risk_level = results["overall_risk_level"]
    risk_color = {
        "High": "#ef4444",
        "Medium": "#f97316",
        "Low": "#10b981"
    }.get(risk_level, "#ef4444")
    
    # Show the risk level
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
                    {"Yes" if results["dpia_required"] else "No"}
                </p>
            </div>
            <div style="flex: 1;">
                <h3>Risk Score</h3>
                <p style="font-size: 18px; font-weight: 500;">
                    {results["overall_percentage"]:.1f}/10
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Category scores
    st.subheader("Risk Analysis by Category")
    
    for category, scores in results["category_scores"].items():
        category_name = scanner.assessment_categories[category]["name"]
        percentage = scores["percentage"]
        risk_level = scores["risk_level"]
        risk_color = {
            "High": "#ef4444",
            "Medium": "#f97316",
            "Low": "#10b981"
        }.get(risk_level, "#ef4444")
        
        # Show the category score
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
    
    if results["recommendations"]:
        for i, recommendation in enumerate(results["recommendations"][:5]):  # Show top 5
            severity = recommendation["severity"]
            category = recommendation["category"]
            description = recommendation["description"]
            
            risk_color = {
                "High": "#ef4444",
                "Medium": "#f97316",
                "Low": "#10b981"
            }.get(severity, "#ef4444")
            
            # Show the recommendation
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
    
    # Report download
    st.subheader("Download Full Report")
    st.markdown("The complete report includes detailed findings, all recommendations, and compliance guidance.")
    
    # Generate PDF report
    try:
        report_filename = f"dpia_report_{results['scan_id']}.pdf"
        
        # Show generation message
        with st.spinner("Generating PDF report..."):
            pdf_data = generate_pdf_report(report_data)
        
        st.success("✅ Report generated successfully! Click below to download.")
        
        # Download button
        st.download_button(
            label="📄 Download DPIA Report PDF",
            data=pdf_data,
            file_name=report_filename,
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Error generating report: {str(e)}")

if __name__ == "__main__":
    run_simple_dpia()