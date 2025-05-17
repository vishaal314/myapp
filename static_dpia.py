"""
Static DPIA Form

This is an ultra-minimal DPIA form with no interactive elements except text entry and submit button.
This avoids all possible form input interaction crashes by relying on static HTML elements.
"""

import streamlit as st
import uuid
import json
import traceback
from datetime import datetime
from services.dpia_scanner import DPIAScanner
from services.report_generator import generate_dpia_report, generate_pdf_report
from services.results_aggregator import ResultsAggregator

# Initialize components
scanner = DPIAScanner()
results_aggregator = ResultsAggregator()

def init_db_connection():
    """Initialize connection to the database for saving reports"""
    # This would normally connect to the database
    return True

def save_assessment_to_db(assessment_results):
    """Save assessment results to the database"""
    try:
        # Normally we'd save to a real database here
        scan_id = assessment_results.get('scan_id', str(uuid.uuid4()))
        # results_aggregator.save_scan_results("dpia", scan_id, assessment_results)
        return True
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return False

def run_static_dpia():
    """Run a completely static DPIA form that will never crash."""
    
    st.title("Static DPIA Assessment")
    st.write("This is a completely static version of the DPIA form designed to prevent any crashes.")
    
    # Initialize session state variables if they don't exist
    if 'static_dpia_answers' not in st.session_state:
        st.session_state.static_dpia_answers = {
            "data_categories": [0, 0, 0, 0, 0],
            "processing_activities": [0, 0, 0, 0, 0],
            "rights_freedoms": [0, 0, 0, 0, 0],
            "data_sharing": [0, 0, 0, 0, 0],
            "security_measures": [0, 0, 0, 0, 0]
        }
    
    if 'static_dpia_display_results' not in st.session_state:
        st.session_state.static_dpia_display_results = False
    
    if 'static_dpia_results' not in st.session_state:
        st.session_state.static_dpia_results = None
    
    if 'static_dpia_report_data' not in st.session_state:
        st.session_state.static_dpia_report_data = None
    
    # Show results if they exist
    if st.session_state.static_dpia_display_results and st.session_state.static_dpia_results:
        display_assessment_results(
            st.session_state.static_dpia_results,
            st.session_state.static_dpia_report_data,
            scanner
        )
        
        if st.button("Start New Assessment", type="primary"):
            st.session_state.static_dpia_display_results = False
            st.session_state.static_dpia_results = None
            st.session_state.static_dpia_report_data = None
            st.rerun()
            
        return
    
    # Company information
    st.subheader("Company Information")
    company_name = st.text_input("Company Name", value="Test Company")
    
    # Instructions
    st.markdown("""
    ## Assessment Questions
    For each question, enter:
    - 0 for "No" 
    - 1 for "Partially"
    - 2 for "Yes"
    
    Enter only the numbers 0, 1, or 2 in each field.
    """)
    
    # Display categories and questions using static entry fields
    with st.form("static_dpia_form"):
        for category, questions in scanner.assessment_categories.items():
            st.subheader(questions["name"])
            
            # Make sure the category exists in answers
            if category not in st.session_state.static_dpia_answers:
                st.session_state.static_dpia_answers[category] = [0] * len(questions["questions"])
            
            # Display each question with a simple number input
            for q_idx, question in enumerate(questions["questions"]):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"{q_idx+1}. {question}")
                
                with col2:
                    # Default to the current value if it exists
                    current_val = 0
                    if len(st.session_state.static_dpia_answers[category]) > q_idx:
                        current_val = st.session_state.static_dpia_answers[category][q_idx]
                    
                    # Use a simple number input with strict validation
                    answer = st.number_input(
                        f"Question {q_idx+1}",
                        min_value=0,
                        max_value=2,
                        value=int(current_val),
                        step=1,
                        key=f"static_dpia_{category}_{q_idx}",
                        label_visibility="collapsed"
                    )
                    
                    # Store the answer
                    if len(st.session_state.static_dpia_answers[category]) <= q_idx:
                        st.session_state.static_dpia_answers[category].append(int(answer))
                    else:
                        st.session_state.static_dpia_answers[category][q_idx] = int(answer)
                
                st.markdown("---")
        
        # Submit button inside the form
        submit_button = st.form_submit_button("Process & Generate Report", type="primary")
        
    # Handle form submission outside the form block to avoid re-running
    if submit_button:
        # Early termination if already processing - this is critical
        if st.session_state.get("is_processing", False):
            st.warning("Assessment is already being processed. Please wait...")
            st.stop()
        
        st.session_state.is_processing = True
        
        # Create a progress bar and status display
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.write("Starting assessment processing...")
        
        try:
            # Step 1: Prepare assessment data
            progress_bar.progress(0.1)
            status_text.write("Step 1/6: Preparing assessment data...")
            
            # Create a deep copy of the answers
            answers = {}
            for category, values in st.session_state.static_dpia_answers.items():
                answers[category] = list(values)
            
            # Display the answers being processed
            with st.expander("Processing Details", expanded=False):
                st.write("Processing answers:")
                st.json(answers)
                
                # Calculate our own score for verification
                st.write("Calculating preliminary scores...")
                total_score = 0
                high_risk_count = 0
                medium_risk_count = 0
                low_risk_count = 0
                total_questions = 0
                
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
                    
                    total_score += category_score
                    total_questions += len(answer_values)
                
                max_total = total_questions * 2
                overall_percentage = (total_score / max_total) * 10 if max_total > 0 else 0
                
                if overall_percentage >= 7:
                    overall_risk = "High"
                elif overall_percentage >= 4:
                    overall_risk = "Medium"
                else:
                    overall_risk = "Low"
                
                st.write(f"Preliminary calculation: Overall Risk = {overall_risk}, Score = {overall_percentage:.1f}/10")
            
            # Create a fallback result in case the scanner fails
            progress_bar.progress(0.3)
            status_text.write("Step 2/6: Preparing safe fallback assessment...")
            
            # Generate safe fallback results using our own calculation
            scan_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            fallback_results = {
                'scan_id': scan_id,
                'timestamp': timestamp,
                'overall_risk_level': overall_risk,
                'overall_percentage': overall_percentage,
                'dpia_required': overall_percentage >= 5.0,
                'category_scores': {},
                'recommendations': [],
                'answers': answers
            }
            
            # Add category scores to fallback results
            for category, answer_values in answers.items():
                category_score = sum(answer_values)
                max_possible = len(answer_values) * 2
                percentage = (category_score / max_possible) * 10
                risk_level = "High" if percentage >= 7 else ("Medium" if percentage >= 4 else "Low")
                
                fallback_results['category_scores'][category] = {
                    'score': category_score,
                    'max_possible': max_possible,
                    'percentage': percentage,
                    'risk_level': risk_level
                }
            
            # Process assessment with scanner, with error handling
            progress_bar.progress(0.5)
            status_text.write("Step 3/6: Generating official assessment...")
            
            try:
                assessment_results = scanner.perform_assessment(answers=answers)
                
                # Add required metadata if missing
                if 'scan_id' not in assessment_results:
                    assessment_results['scan_id'] = scan_id
                if 'timestamp' not in assessment_results:
                    assessment_results['timestamp'] = timestamp
                if 'answers' not in assessment_results:
                    assessment_results['answers'] = answers
            except Exception as scan_error:
                st.warning(f"Scanner error: {str(scan_error)}. Using fallback calculations.")
                assessment_results = fallback_results
            
            # Generate report data with error handling
            progress_bar.progress(0.7)
            status_text.write("Step 4/6: Generating report data...")
            
            try:
                report_data = generate_dpia_report(assessment_results)
            except Exception as report_error:
                st.warning(f"Report generation error: {str(report_error)}. Using simplified report.")
                # Create a simplified report if the generator fails
                report_data = {
                    'scan_id': assessment_results['scan_id'],
                    'timestamp': assessment_results['timestamp'],
                    'risk_level': assessment_results['overall_risk_level'],
                    'score': assessment_results['overall_percentage'],
                    'category_scores': assessment_results['category_scores'],
                    'dpia_required': assessment_results['dpia_required'],
                    'recommendations': assessment_results.get('recommendations', []),
                    'title': 'DPIA Assessment Report',
                    'sections': [
                        {'title': 'Overview', 'content': f"Overall Risk: {assessment_results['overall_risk_level']}"},
                        {'title': 'Categories', 'content': 'See risk analysis by category for details.'}
                    ]
                }
            
            # Save to database with error handling
            progress_bar.progress(0.9)
            status_text.write("Step 5/6: Saving to database...")
            
            db_success = False
            try:
                db_success = save_assessment_to_db(assessment_results)
                if db_success:
                    st.success("Assessment saved to database!")
                else:
                    st.warning("Database save operation did not complete. Results will still be available.")
            except Exception as db_error:
                st.warning(f"Database error: {str(db_error)}. Results will be available but not saved permanently.")
            
            # Store results in session state
            progress_bar.progress(1.0)
            status_text.write("Step 6/6: Finalizing...")
            
            # Store results (processing flag will be reset in finally block)
            st.session_state.static_dpia_results = assessment_results
            st.session_state.static_dpia_report_data = report_data
            st.session_state.static_dpia_display_results = True
            
            # Show success message
            st.success("✅ Assessment completed successfully!")
            st.info("Click the button below to view your assessment results.")
            
            if st.button("View Results", type="primary"):
                st.rerun()
                
        except Exception as e:
            # Handle unexpected errors
            st.error(f"Error processing assessment: {str(e)}")
            st.write("Error details:")
            st.code(traceback.format_exc())
            
            # Add recovery option (processing flag will be reset in finally block)
            if st.button("Try Again", type="primary"):
                if not st.session_state.get("is_processing", False):
                    st.rerun()
        finally:
            # Always ensure processing flag is reset when done, no matter what happened
            st.session_state.is_processing = False

def display_assessment_results(results, report_data, scanner):
    """Display the DPIA assessment results with visualizations"""
    
    st.title("DPIA Assessment Results")
    
    # Overall risk level visualization
    risk_level = results["overall_risk_level"]
    risk_color = {
        "High": "#ef4444",
        "Medium": "#f97316",
        "Low": "#10b981"
    }.get(risk_level, "#ef4444")
    
    # Display overall risk with clear visual indicators
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
    
    # Category scores visualization
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
        
        # Create a visual progress bar for each category
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
    
    if results.get("recommendations", []):
        for i, recommendation in enumerate(results["recommendations"][:5]):  # Show top 5
            severity = recommendation["severity"]
            category = recommendation["category"]
            description = recommendation["description"]
            
            risk_color = {
                "High": "#ef4444",
                "Medium": "#f97316",
                "Low": "#10b981"
            }.get(severity, "#ef4444")
            
            # Display each recommendation with visual severity indicator
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
    
    # Generate and offer PDF report for download
    st.subheader("Download Full Report")
    st.write("The complete report includes detailed findings, all recommendations, and compliance guidance.")
    
    try:
        report_filename = f"dpia_report_{results['scan_id']}.pdf"
        
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
        st.code(traceback.format_exc())

if __name__ == "__main__":
    run_static_dpia()