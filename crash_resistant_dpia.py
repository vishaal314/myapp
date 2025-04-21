"""
Crash-Resistant DPIA Form

This is a bulletproof version of the DPIA form designed to never crash.
It uses the most minimal, stable UI elements to gather assessment data
while still delivering comprehensive report output.
"""

import streamlit as st
import os
import json
import uuid
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Import scanner and report functions with explicit naming to avoid conflicts
from services.dpia_scanner import DPIAScanner
from services.report_generator import generate_pdf_report

# Initialize scanner
scanner = DPIAScanner(language='en')

def run_crash_resistant_dpia():
    """Run a crash-resistant DPIA form with enhanced report output"""
    
    st.title("DPIA Assessment")
    st.write("Complete this form to conduct a Data Protection Impact Assessment for your project.")
    
    # Add explanatory content
    with st.expander("What is a DPIA and when is it required?", expanded=False):
        st.markdown("""
        ### What is a DPIA?
        A Data Protection Impact Assessment (DPIA) is a process designed to help you identify and minimize data protection risks in your project. It's required under GDPR for processing that is likely to result in a high risk to individuals.

        ### When is a DPIA required?
        You must do a DPIA if your processing is likely to result in a high risk to individuals. This includes:
        - Using new technologies
        - Tracking location or behavior
        - Processing sensitive data on a large scale
        - Systematic monitoring of public areas
        - Using AI for decision-making with significant effects
        
        ### The DPIA Process
        1. Identify the need for a DPIA
        2. Describe the processing
        3. Consider consultation
        4. Assess necessity and proportionality
        5. Identify and assess risks
        6. Identify measures to mitigate risks
        7. Sign off and record outcomes
        """)
    
    # Initialize session state for form answers
    if 'dpia_admin_info' not in st.session_state:
        st.session_state.dpia_admin_info = {
            "project_name": "",
            "contact_person": "",
            "department": "",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "description": "",
            "purpose": ""
        }
    
    # Initialize answers storage
    if 'dpia_answers' not in st.session_state:
        st.session_state.dpia_answers = {}
        assessment_categories = scanner.assessment_categories
        for category in assessment_categories:
            question_count = len(assessment_categories[category]['questions'])
            st.session_state.dpia_answers[category] = [0] * question_count
    
    # Get categories from scanner
    assessment_categories = scanner.assessment_categories
    
    # Flag to track if we're showing results
    showing_results = 'dpia_display_results' in st.session_state and st.session_state.dpia_display_results
    
    if showing_results and 'dpia_results' in st.session_state:
        # Display assessment results
        display_assessment_results(
            st.session_state.dpia_results,
            st.session_state.dpia_report_data,
            scanner
        )
        
        # New assessment button
        if st.button("Start New Assessment", type="primary"):
            # Reset all relevant state
            st.session_state.dpia_display_results = False
            st.session_state.dpia_answers = {}
            for category in assessment_categories:
                question_count = len(assessment_categories[category]['questions'])
                st.session_state.dpia_answers[category] = [0] * question_count
            st.session_state.dpia_admin_info = {
                "project_name": "",
                "contact_person": "",
                "department": "",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "description": "",
                "purpose": ""
            }
            st.rerun()
        
        return
    
    # Create tabs for each section of the form
    tab1, tab2, tab3 = st.tabs(["Project Information", "Assessment Questions", "Review & Submit"])
    
    with tab1:
        st.subheader("Administrative Information")
        st.write("Please provide the details of your project.")
        
        try:
            # Simple text inputs with explicit error handling
            col1, col2 = st.columns(2)
            
            with col1:
                project_name = st.text_input(
                    "Project Name", 
                    value=st.session_state.dpia_admin_info.get("project_name", ""),
                    key="project_name_input"
                )
                st.session_state.dpia_admin_info["project_name"] = project_name
                
                contact_person = st.text_input(
                    "Contact Person",
                    value=st.session_state.dpia_admin_info.get("contact_person", ""),
                    key="contact_person_input"
                )
                st.session_state.dpia_admin_info["contact_person"] = contact_person
            
            with col2:
                department = st.text_input(
                    "Department/Unit",
                    value=st.session_state.dpia_admin_info.get("department", ""),
                    key="department_input"
                )
                st.session_state.dpia_admin_info["department"] = department
                
                try:
                    # Handle date input safely
                    current_date = st.session_state.dpia_admin_info.get("date", datetime.now().strftime("%Y-%m-%d"))
                    if isinstance(current_date, str):
                        try:
                            date_value = datetime.strptime(current_date, "%Y-%m-%d")
                        except:
                            date_value = datetime.now()
                    else:
                        date_value = current_date
                except:
                    date_value = datetime.now()
                
                date = st.date_input(
                    "Assessment Date",
                    value=date_value,
                    key="date_input"
                )
                st.session_state.dpia_admin_info["date"] = date.strftime("%Y-%m-%d")
            
            description = st.text_area(
                "Project Description", 
                value=st.session_state.dpia_admin_info.get("description", ""),
                height=100,
                key="description_input"
            )
            st.session_state.dpia_admin_info["description"] = description
            
            purpose = st.text_area(
                "Purpose of Data Processing",
                value=st.session_state.dpia_admin_info.get("purpose", ""),
                height=100,
                key="purpose_input"
            )
            st.session_state.dpia_admin_info["purpose"] = purpose
        
        except Exception as e:
            st.error(f"Error in project information section: {str(e)}")
            st.write("This error has been logged. Please try again or contact support.")
    
    with tab2:
        st.subheader("DPIA Assessment Questions")
        st.write("Please answer the following questions about your data processing activities.")
        
        st.info("""
        Please rate each of the following statements based on your project:
        - **0 = No** (The statement doesn't apply)
        - **1 = Partially** (The statement somewhat applies)
        - **2 = Yes** (The statement fully applies)
        
        Higher ratings indicate higher privacy risk.
        """)
        
        # Create category tabs
        category_tabs = st.tabs([assessment_categories[cat]["name"] for cat in assessment_categories])
        
        try:
            # Process each category
            for i, category in enumerate(assessment_categories):
                with category_tabs[i]:
                    st.write(f"**{assessment_categories[category]['description']}**")
                    st.markdown("---")
                    
                    # Make sure this category exists in session state
                    if category not in st.session_state.dpia_answers:
                        question_count = len(assessment_categories[category]['questions'])
                        st.session_state.dpia_answers[category] = [0] * question_count
                    
                    # Process each question in this category
                    questions = assessment_categories[category]['questions']
                    for q_idx, question in enumerate(questions):
                        try:
                            # Ensure we have enough elements in the list
                            while len(st.session_state.dpia_answers[category]) <= q_idx:
                                st.session_state.dpia_answers[category].append(0)
                            
                            # Get current value with fallback to 0
                            current_val = st.session_state.dpia_answers[category][q_idx] if q_idx < len(st.session_state.dpia_answers[category]) else 0
                            
                            # Unique key for this question
                            key = f"q_{category}_{q_idx}"
                            
                            st.write(f"**{q_idx+1}. {question}**")
                            
                            # Use radio buttons (most stable form element)
                            value = st.radio(
                                f"Rating for: {question}",
                                options=["No", "Partially", "Yes"],
                                index=current_val,
                                key=key,
                                horizontal=True,
                                label_visibility="collapsed"
                            )
                            
                            # Convert text value to numeric
                            numeric_value = ["No", "Partially", "Yes"].index(value)
                            
                            # Save the answer immediately
                            st.session_state.dpia_answers[category][q_idx] = numeric_value
                            
                            st.markdown("---")
                        except Exception as q_err:
                            st.error(f"Error processing question {q_idx+1}: {str(q_err)}")
                            continue
                
        except Exception as tab_err:
            st.error(f"Error in assessment questions: {str(tab_err)}")
    
    with tab3:
        st.subheader("Review & Submit Assessment")
        st.write("Review your information and submit when ready.")
        
        st.warning("⚠️ Once you submit, the assessment will be processed and you'll receive detailed results.")
        
        # Show submission button
        submit_col1, submit_col2 = st.columns([3, 1])
        
        with submit_col1:
            st.write("Ready to process your DPIA assessment?")
        
        with submit_col2:
            submit_button = st.button("Submit Assessment", type="primary", use_container_width=True)
        
        if submit_button:
            try:
                st.info("Processing your assessment... Please wait.")
                
                # Process the assessment
                with st.spinner("Analyzing data protection risks..."):
                    # Process the DPIA assessment
                    process_dpia_assessment()
            except Exception as submit_err:
                st.error(f"Error submitting assessment: {str(submit_err)}")
                st.code(traceback.format_exc())
                st.warning("Please try again or use a different browser if the issue persists.")

def process_dpia_assessment():
    """Process the DPIA assessment with extensive error handling"""
    
    # Early exit if already processing
    if st.session_state.get("is_processing", False):
        st.warning("Assessment is already being processed. Please wait...")
        return
    
    # Set processing flag
    try:
        st.session_state.is_processing = True
        st.info("Starting assessment processing...")
    except:
        # If we can't even set session state, show error and exit
        st.error("Unable to initialize assessment processing. Please refresh the page and try again.")
        return
    
    try:
        # Create a progress bar
        progress_bar = st.progress(0)
        progress_bar.progress(10, "Preparing assessment data...")
        
        # Create a copy of the answers to avoid any reference issues
        answers = {}
        for category, values in st.session_state.dpia_answers.items():
            answers[category] = list(values)
        
        progress_bar.progress(25, "Validating input data...")
        
        # Add admin info
        admin_info = st.session_state.dpia_admin_info.copy()
        
        progress_bar.progress(40, "Running risk analysis...")
        
        # Perform the assessment
        assessment_results = scanner.perform_assessment(answers=answers)
        
        # Add admin info to results
        assessment_results["admin_info"] = admin_info
        
        progress_bar.progress(60, "Generating recommendations...")
        
        # Generate report data
        report_data = {
            "title": "Data Protection Impact Assessment (DPIA)",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "project": admin_info.get("project_name", "Unnamed Project"),
            "contact": admin_info.get("contact_person", ""),
            "department": admin_info.get("department", ""),
            "results": assessment_results
        }
        
        progress_bar.progress(80, "Finalizing results...")
        
        # Save results to session state
        st.session_state.dpia_results = assessment_results
        st.session_state.dpia_report_data = report_data
        st.session_state.dpia_display_results = True
        
        progress_bar.progress(100, "Assessment complete!")
        
        # Rerun to show results
        st.rerun()
    
    except Exception as e:
        st.error(f"Error processing assessment: {str(e)}")
        st.code(traceback.format_exc())
        st.warning("Please try again or contact support if the issue persists.")
    
    finally:
        # Always reset processing flag
        st.session_state.is_processing = False

def display_assessment_results(results, report_data, scanner):
    """Display the DPIA assessment results with the enhanced 7-section report structure"""
    
    st.title("DPIA Assessment Results")
    
    # Display header with report structure info
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; border-left: 4px solid #4caf50;">
        <h3 style="margin-top: 0; color: #3a7144;">DPIA Report</h3>
        <p style="margin: 0;">This report follows the standard DPIA structure and presents the assessment findings in a clear, organized format.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get common variables
    admin_info = results.get('admin_info', {})
    risk_level = results["overall_risk_level"]
    risk_color = {
        "High": "#ef4444",
        "Medium": "#f97316",
        "Low": "#10b981"
    }.get(risk_level, "#ef4444")
    
    # 1. INTRODUCTION SECTION
    st.markdown("""
    <div style="background-color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;
              box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h2 style="margin-top: 0; color: #3f51b5;">1. Introduction</h2>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="margin-left: 20px;">
        <p><strong>Organization/Project:</strong> {admin_info.get('project_name', 'Not specified')}</p>
        <p><strong>Assessment Date:</strong> {admin_info.get('date', 'Not specified')}</p>
        <p><strong>Contact Person:</strong> {admin_info.get('contact_person', 'Not specified')}</p>
        <p><strong>Department/Unit:</strong> {admin_info.get('department', 'Not specified')}</p>
        <p><strong>Purpose:</strong> {admin_info.get('purpose', 'Not specified')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 2. DESCRIPTION OF THE PROCESSING 
    st.markdown("""
    <div style="background-color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;
              box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h2 style="margin-top: 0; color: #3f51b5;">2. Description of the Processing</h2>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="margin-left: 20px;">
        <p><strong>Project Description:</strong> {admin_info.get('description', 'Not specified')}</p>
        <p><strong>Data Processing Purpose:</strong> {admin_info.get('purpose', 'Not specified')}</p>
        
        <h4 style="margin-top: 15px;">Type of data processed:</h4>
        <ul>
            {"<li>Sensitive/special category data</li>" if results.get('category_scores', {}).get('data_category', {}).get('score', 0) > 2 else ""}
            {"<li>Vulnerable persons data</li>" if results.get('category_scores', {}).get('data_category', {}).get('score', 0) > 4 else ""}
            {"<li>Children's data</li>" if results.get('category_scores', {}).get('data_category', {}).get('score', 0) > 6 else ""}
            {"<li>Large scale data processing</li>" if results.get('category_scores', {}).get('data_category', {}).get('score', 0) > 8 else ""}
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 3. NECESSITY & PROPORTIONALITY
    st.markdown("""
    <div style="background-color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;
              box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h2 style="margin-top: 0; color: #3f51b5;">3. Necessity & Proportionality</h2>
        
        <div style="margin-left: 20px;">
            <h4>Data minimization assessment:</h4>
            <p>Based on the assessment, the following aspects require attention:</p>
            <ul>
                {"<li>Data minimization measures appear inadequate</li>" if results.get('category_scores', {}).get('security_measures', {}).get('score', 0) < 4 else ""}
                {"<li>Data subject rights may be restricted</li>" if results.get('category_scores', {}).get('rights_impact', {}).get('score', 0) > 6 else ""}
                {"<li>International data transfers identified</li>" if results.get('category_scores', {}).get('transfer_sharing', {}).get('score', 0) > 5 else ""}
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 4. RISK ASSESSMENT
    st.markdown(f"""
    <div style="background-color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;
              box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h2 style="margin-top: 0; color: #3f51b5;">4. Risk Assessment</h2>
        
        <div style="margin-left: 20px;">
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                <tr style="background-color: #f5f5f5;">
                    <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Risk Type</th>
                    <th style="padding: 10px; text-align: center; border: 1px solid #ddd;">Likelihood</th>
                    <th style="padding: 10px; text-align: center; border: 1px solid #ddd;">Impact</th>
                    <th style="padding: 10px; text-align: center; border: 1px solid #ddd;">Risk Level</th>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;">Overall Privacy Risk</td>
                    <td style="padding: 10px; text-align: center; border: 1px solid #ddd;">
                        {("Low" if results["overall_percentage"] < 4 else "Medium" if results["overall_percentage"] < 7 else "High")}
                    </td>
                    <td style="padding: 10px; text-align: center; border: 1px solid #ddd;">
                        {("Low" if results["overall_percentage"] < 3 else "Medium" if results["overall_percentage"] < 6 else "High")}
                    </td>
                    <td style="padding: 10px; text-align: center; border: 1px solid #ddd; background-color: {risk_color}; color: white; font-weight: bold;">
                        {risk_level}
                    </td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;">DPIA Required</td>
                    <td style="padding: 10px; text-align: center; border: 1px solid #ddd;" colspan="3">
                        <strong>{"Yes" if results["dpia_required"] else "No"}</strong>
                    </td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;">Risk Score</td>
                    <td style="padding: 10px; text-align: center; border: 1px solid #ddd;" colspan="3">
                        <strong>{results["overall_percentage"]:.1f}/10</strong>
                    </td>
                </tr>
            </table>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 5. MITIGATION MEASURES
    st.markdown("""
    <div style="background-color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;
              box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h2 style="margin-top: 0; color: #3f51b5;">5. Mitigation Measures</h2>
    """, unsafe_allow_html=True)
    
    # Default mitigation measures based on risk areas
    mitigation_measures = []
    
    # Add data category mitigations
    if results.get("category_scores", {}).get("data_category", {}).get("risk_level") == "High":
        mitigation_measures.append("Use end-to-end encryption for sensitive data storage and transfer")
        mitigation_measures.append("Implement strong access controls and authentication for sensitive data access")
    
    # Add processing mitigations
    if results.get("category_scores", {}).get("processing_activity", {}).get("risk_level") in ["Medium", "High"]:
        mitigation_measures.append("Document clear purpose limitations and processing boundaries")
        mitigation_measures.append("Implement data minimization practices to only collect necessary data")
    
    # Add rights impact mitigations
    if results.get("category_scores", {}).get("rights_impact", {}).get("risk_level") in ["Medium", "High"]:
        mitigation_measures.append("Implement transparent notification processes to inform data subjects")
        mitigation_measures.append("Provide clear mechanisms for data subject rights requests")
    
    # Add data sharing mitigations
    if results.get("category_scores", {}).get("transfer_sharing", {}).get("risk_level") in ["Medium", "High"]:
        mitigation_measures.append("Establish formal data sharing agreements with all processors/partners")
        mitigation_measures.append("Implement appropriate safeguards for international transfers")
    
    # Add security mitigations
    if results.get("category_scores", {}).get("security_measures", {}).get("risk_level") in ["Medium", "High"]:
        mitigation_measures.append("Enhance security monitoring and breach notification procedures")
        mitigation_measures.append("Conduct regular security audits and penetration testing")
    
    # Display mitigation measures
    if mitigation_measures:
        st.markdown("""
        <div style="margin-left: 20px;">
            <h4>Recommended Mitigation Measures:</h4>
            <ul>
        """, unsafe_allow_html=True)
        
        for measure in mitigation_measures:
            st.markdown(f"<li>{measure}</li>", unsafe_allow_html=True)
        
        st.markdown("""
            </ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="margin-left: 20px;">
            <p>No specific mitigation measures required based on the assessment results.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 6. CONSULTATION
    st.markdown("""
    <div style="background-color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;
              box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h2 style="margin-top: 0; color: #3f51b5;">6. Consultation</h2>
        
        <div style="margin-left: 20px;">
    """, unsafe_allow_html=True)
    
    # Determine consultation requirements based on risk level
    if risk_level == "High":
        st.markdown("""
            <p><strong>DPO Consultation:</strong> Required</p>
            <p><strong>Supervisory Authority Consultation:</strong> Recommended due to high risk level</p>
            <p>According to Article 36 of the GDPR, prior consultation with the supervisory authority is required when data processing would result in a high risk in the absence of mitigating measures.</p>
        """, unsafe_allow_html=True)
    elif risk_level == "Medium":
        st.markdown("""
            <p><strong>DPO Consultation:</strong> Recommended</p>
            <p><strong>Supervisory Authority Consultation:</strong> Not required if mitigation measures are implemented</p>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <p><strong>DPO Consultation:</strong> Optional</p>
            <p><strong>Supervisory Authority Consultation:</strong> Not required</p>
        """, unsafe_allow_html=True)
    
    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 7. FINAL DECISION
    st.markdown(f"""
    <div style="background-color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;
              box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h2 style="margin-top: 0; color: #3f51b5;">7. Final Decision</h2>
        
        <div style="margin-left: 20px;">
            <p><strong>DPIA Status:</strong> Completed</p>
            <p><strong>Overall Decision:</strong> {
                "Processing can proceed with recommended mitigations" if risk_level != "High" else 
                "Processing requires significant mitigation measures and possibly supervisory consultation"
            }</p>
            <p><strong>Date of Completion:</strong> {datetime.now().strftime("%Y-%m-%d")}</p>
            <p><strong>Review Date:</strong> {(datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")} (recommended annual review)</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Category scores visualization in a more structured way
    st.markdown("""
    <div style="background-color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;
              box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h2 style="margin-top: 0; color: #3f51b5;">Detailed Risk Analysis by Category</h2>
    """, unsafe_allow_html=True)
    
    for category, scores in results["category_scores"].items():
        if category in scanner.assessment_categories:
            category_name = scanner.assessment_categories[category]["name"]
            percentage = scores["percentage"]
            risk_level = scores["risk_level"]
            risk_color = {
                "High": "#ef4444",
                "Medium": "#f97316",
                "Low": "#10b981"
            }.get(risk_level, "#ef4444")
            
            st.markdown(f"""
            <div style="margin-bottom: 15px; margin-left: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; 
                          border-left: 5px solid {risk_color}; padding-left: 15px;">
                    <div>
                        <h3 style="margin: 0; color: #333;">{category_name}</h3>
                        <p style="margin: 5px 0 0 0; color: #666;">Risk Level: {risk_level}</p>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 22px; font-weight: 600; color: {risk_color};">
                            {percentage:.1f}/10
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Add PDF report download option
    st.subheader("Download Report")
    
    try:
        if st.button("Generate PDF Report"):
            with st.spinner("Generating PDF report..."):
                try:
                    pdf_content = generate_pdf_report(report_data)
                    
                    # Create download button
                    st.download_button(
                        label="Download DPIA Report PDF",
                        data=pdf_content,
                        file_name=f"dpia_report_{results['scan_id'][:8]}.pdf",
                        mime="application/pdf"
                    )
                except Exception as pdf_err:
                    st.error(f"Error generating PDF: {str(pdf_err)}")
                    st.info("You can still view the assessment results on this page.")
    except Exception as btn_err:
        st.error(f"Error with download button: {str(btn_err)}")

if __name__ == "__main__":
    run_crash_resistant_dpia()